"""Tests for pilot annotation agreement analysis."""

from __future__ import annotations

import json
from pathlib import Path

from scripts.analysis.compute_cohen_kappa import run as run_kappa
from scripts.analysis.compute_confusion_matrix import run as run_confusion
from scripts.analysis.compute_krippendorff_alpha import run as run_alpha
from scripts.analysis.generate_disagreement_report import run as run_disagreement

FIXTURES = Path("tests/fixtures/annotation")
ANNOTATOR_A = FIXTURES / "pilot_annotator_a.csv"
ANNOTATOR_B = FIXTURES / "pilot_annotator_b.csv"


def test_cohen_kappa_perfect_and_mixed(tmp_path: Path):
    output_dir = tmp_path / "results"
    results = run_kappa(ANNOTATOR_A, ANNOTATOR_B, output_dir)

    assert abs(results["pragmatic_function"].kappa - 0.75) < 1e-9
    assert (output_dir / "cohen_kappa.json").exists()
    assert (output_dir / "cohen_kappa.md").exists()
    payload = json.loads((output_dir / "cohen_kappa.json").read_text(encoding="utf-8"))
    assert payload["n_units"] == 5
    assert "PF_ATTACK" in payload["dimensions"]["pragmatic_function"]["per_label"]


def test_krippendorff_alpha_outputs(tmp_path: Path):
    output_dir = tmp_path / "results"
    results = run_alpha(ANNOTATOR_A, ANNOTATOR_B, output_dir)
    assert results["pragmatic_function"].alpha > 0.5
    assert (output_dir / "krippendorff_alpha.md").exists()


def test_confusion_matrix_outputs(tmp_path: Path):
    output_dir = tmp_path / "results"
    results = run_confusion(ANNOTATOR_A, ANNOTATOR_B, output_dir)
    matrix = results["pragmatic_function"].matrix
    assert matrix["PF_ATTACK"]["PF_ATTACK"] == 1
    assert matrix["PF_ADVOCACY"]["PF_ATTACK"] == 1
    assert (output_dir / "confusion_matrix_pragmatic_function.csv").exists()
    assert (output_dir / "confusion_matrices.md").exists()


def test_disagreement_report_counts(tmp_path: Path):
    output_dir = tmp_path / "results"
    rows = run_disagreement(ANNOTATOR_A, ANNOTATOR_B, output_dir)
    assert len(rows) == 3
    types = {row["disagreement_type"] for row in rows}
    assert "pragmatic_function" in types
    assert "conceptual_anachronism" in types
    assert (output_dir / "disagreement_report.csv").exists()
    assert (output_dir / "disagreement_report.md").exists()
