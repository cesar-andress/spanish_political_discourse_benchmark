"""Tests for multi-model Ollama comparison workflow."""

from __future__ import annotations

from pathlib import Path

from analysis.llm_annotation.model_agreement import (
    DISCLAIMER,
    compute_model_agreement,
    load_model_matrices,
    run_model_comparison,
)
from analysis.llm_annotation.registry import (
    load_ollama_registry,
    model_is_installed,
    resolve_model_availability,
)
from scripts.llm_annotation.compare_ollama_models import main as compare_main
from scripts.llm_annotation.run_ollama_batch import run_ollama_batch

FIXTURE_COMPARE_DIR = Path("tests/fixtures/llm_annotation/model_compare")
FIXTURE_REGISTRY = Path("tests/fixtures/llm_annotation/mock_ollama_models.yaml")
FIXTURE_PILOT_MINI = Path("tests/fixtures/llm_annotation/pilot_mini.csv")


def test_load_ollama_registry():
    specs = load_ollama_registry(FIXTURE_REGISTRY)
    assert len(specs) == 2
    assert specs[0].name == "mock_alpha"
    assert "mock_backend.py" in specs[0].command


def test_model_is_installed_matches_tagged_names():
    installed = {"llama3.1:latest", "mistral:7b"}
    assert model_is_installed("llama3.1", installed)
    assert model_is_installed("mistral", installed)
    assert not model_is_installed("gemma2", installed)


def test_resolve_model_availability_without_ollama(monkeypatch):
    monkeypatch.setattr("analysis.llm_annotation.registry.ollama_cli_available", lambda: False)
    specs = load_ollama_registry(FIXTURE_REGISTRY)
    ready, notes = resolve_model_availability(specs)
    assert ready == []
    assert notes


def test_model_agreement_metrics_on_fixtures():
    paths = sorted(FIXTURE_COMPARE_DIR.glob("*_pilot_100.jsonl"))
    matrix = load_model_matrices(paths)
    summary = compute_model_agreement(matrix)

    assert len(summary.matrix.model_names) == 3
    assert summary.unanimous_rate_pf > 0
    assert summary.full_disagreement_rate_pf > 0
    assert summary.top_disagreement_pairs_pf
    assert any(row["unit_id"] == "u003" for row in summary.max_disagreement_units_pf)
    assert len(summary.pairwise_cohen_kappa) == 3


def test_run_model_comparison_writes_reports(tmp_path: Path):
    outputs = run_model_comparison(
        jsonl_paths=sorted(FIXTURE_COMPARE_DIR.glob("*_pilot_100.jsonl")),
        report_dir=tmp_path,
    )
    report = outputs.report_path.read_text(encoding="utf-8")
    assert DISCLAIMER in report
    assert outputs.scores_path.exists()
    assert outputs.pairwise_path.exists()
    assert outputs.disagreement_path.exists()


def test_compare_cli_with_fixtures(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("PYTHONPATH", ".")
    assert (
        compare_main(
            [
                "--fixtures",
                "--report-dir",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (tmp_path / "ollama_model_comparison.md").exists()


def test_run_ollama_batch_with_mock_registry(tmp_path: Path):
    result = run_ollama_batch(
        registry_path=FIXTURE_REGISTRY,
        pilot_path=FIXTURE_PILOT_MINI,
        output_dir=tmp_path / "annotations",
        failures_report=tmp_path / "failures.md",
        skip_availability_check=True,
        skip_probe=True,
    )
    assert len(result.successes) == 2
    assert (tmp_path / "annotations" / "mock_alpha_pilot_100.jsonl").exists()
    assert (tmp_path / "annotations" / "mock_beta_pilot_100.jsonl").exists()
    assert (tmp_path / "failures.md").exists()
