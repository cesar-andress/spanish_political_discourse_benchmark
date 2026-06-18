"""Tests for pragmatic-function artifact audit."""

from __future__ import annotations

from pathlib import Path

from scripts.analysis.artifact_audit import (
    evaluate_baselines,
    load_audit_records,
    run,
)

FIXTURE = Path("tests/fixtures/annotation/artifact_audit_sample.csv")


def test_load_audit_records_from_fixture():
    records = load_audit_records(FIXTURE)
    assert len(records) == 30
    assert {record.label for record in records} == {
        "PF_ADVOCACY",
        "PF_ATTACK",
        "PF_DEFENSE",
        "PF_PROPOSAL",
        "PF_APPEAL",
        "PF_INFO",
        "PF_PROCEDURAL",
        "PF_DEFLECT",
    }


def test_party_only_baseline_is_flagged_on_fixture():
    records = load_audit_records(FIXTURE)
    baselines = evaluate_baselines(records, seed=42)
    party = next(result for result in baselines if result.name == "Party-only")
    assert party.flagged
    assert party.accuracy >= 0.55


def test_run_writes_report_and_figures(tmp_path: Path):
    output_md = tmp_path / "artifact_audit.md"
    figures_dir = tmp_path / "figures"
    summary = run(
        FIXTURE,
        markdown_path=output_md,
        figures_dir=figures_dir,
        no_figures=False,
    )
    assert summary["n_units"] == 30
    assert output_md.exists()
    text = output_md.read_text(encoding="utf-8")
    assert "## Label distribution" in text
    assert "## Trivial baseline performance" in text
    assert any(item["flagged"] for item in summary["baselines"])
    assert len(list(figures_dir.glob("*.png"))) == 5


def test_evaluate_baselines_returns_four_models():
    records = load_audit_records(FIXTURE)
    baselines = evaluate_baselines(records, seed=42)
    assert len(baselines) == 4
    assert {result.name for result in baselines} == {
        "Majority-class",
        "Length-only",
        "Speaker-role-only",
        "Party-only",
    }
