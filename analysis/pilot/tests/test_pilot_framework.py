"""Tests for the SPDB pilot analytics framework."""

from __future__ import annotations

from pathlib import Path

from analysis.pilot.io import AnnotationStatus, load_pilot_dataset
from scripts.analysis.pilot_analytics import run_pilot_analytics

FIXTURES = Path("tests/fixtures/annotation")
ANNOTATOR_A = FIXTURES / "pilot_annotator_a.csv"
ANNOTATOR_B = FIXTURES / "pilot_annotator_b.csv"
ANNOTATOR_C = FIXTURES / "pilot_annotator_c.csv"
TEMPLATE = FIXTURES / "pilot_template.csv"


def test_pre_annotation_mode_with_template_only():
    dataset = load_pilot_dataset(annotator_paths=[], template_path=TEMPLATE)
    assert dataset.status is AnnotationStatus.PENDING
    assert dataset.n_units == 5
    assert dataset.filled_counts["pragmatic_function"] == 0


def test_three_annotator_dataset_loads():
    dataset = load_pilot_dataset(
        annotator_paths=[ANNOTATOR_A, ANNOTATOR_B, ANNOTATOR_C],
        template_path=TEMPLATE,
    )
    assert dataset.n_annotators == 3
    assert dataset.status is AnnotationStatus.COMPLETE


def test_full_pipeline_with_three_annotators(tmp_path: Path):
    output_dir = tmp_path / "pilot"
    report_path = tmp_path / "pilot_annotation_report.md"
    bundle = run_pilot_analytics(
        annotator_paths=[ANNOTATOR_A, ANNOTATOR_B, ANNOTATOR_C],
        template_path=TEMPLATE,
        output_dir=output_dir,
        report_path=report_path,
        figures_dir=tmp_path / "figures",
        seed=42,
    )
    assert bundle.dataset.status is AnnotationStatus.COMPLETE
    assert report_path.exists()
    text = report_path.read_text(encoding="utf-8")
    assert "## 1. Agreement analysis" in text
    assert (output_dir / "agreement_analysis.json").exists()
    assert (output_dir / "confusion_analysis.json").exists()
    assert (output_dir / "ontology_diagnostics.json").exists()
    assert "pragmatic_function" in (output_dir / "agreement_analysis.json").read_text(encoding="utf-8")


def test_pre_annotation_pipeline_generates_report(tmp_path: Path):
    report_path = tmp_path / "pilot_annotation_report.md"
    bundle = run_pilot_analytics(
        annotator_paths=[],
        template_path=TEMPLATE,
        output_dir=tmp_path / "pilot",
        report_path=report_path,
        figures_dir=tmp_path / "figures",
        no_figures=True,
        seed=42,
    )
    assert bundle.dataset.status is AnnotationStatus.PENDING
    assert "Pre-annotation mode" in report_path.read_text(encoding="utf-8")
