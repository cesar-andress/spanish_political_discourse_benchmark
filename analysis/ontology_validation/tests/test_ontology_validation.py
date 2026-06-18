"""Tests for SPDB ontology validation framework."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.ontology_validation.constants import FIXTURE_ANNOTATORS, FIXTURE_TEMPLATE
from analysis.ontology_validation.dashboard import OntologyDecision
from analysis.ontology_validation.io import load_ontology_dataset
from analysis.ontology_validation.metrics import gwet_ac1
from analysis.ontology_validation.pipeline import run_ontology_validation
from analysis.pilot.io import AnnotationStatus

OUTPUT = Path("tests/output/ontology_validation")


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "ontology_validation"


def test_pre_annotation_mode(output_dir: Path):
    bundle = run_ontology_validation(
        annotator_paths=[],
        template_path=FIXTURE_TEMPLATE,
        output_dir=output_dir,
        figures_dir=output_dir / "figures",
        bootstrap_iterations=200,
        seed=42,
    )
    dataset = load_ontology_dataset(annotator_paths=[], template_path=FIXTURE_TEMPLATE)
    assert dataset.status is AnnotationStatus.PENDING
    assert (output_dir / "overall_reliability.json").exists()
    decision = (output_dir / "ontology_decision.md").read_text(encoding="utf-8")
    assert "PENDING" in decision
    assert (output_dir / "publication_tables.md").exists()


def test_fixture_pipeline_produces_all_outputs(output_dir: Path):
    bundle = run_ontology_validation(
        annotator_paths=list(FIXTURE_ANNOTATORS),
        template_path=FIXTURE_TEMPLATE,
        output_dir=output_dir,
        figures_dir=output_dir / "figures",
        bootstrap_iterations=300,
        seed=42,
    )
    expected = [
        "overall_reliability.json",
        "overall_reliability.md",
        "per_class_reliability.csv",
        "per_class_reliability.md",
        "confusion_matrix.csv",
        "confusion_report.md",
        "single_dominance_report.md",
        "ontology_decision.md",
        "publication_tables.md",
    ]
    for name in expected:
        assert (output_dir / name).exists(), name

    payload = json.loads((output_dir / "overall_reliability.json").read_text(encoding="utf-8"))
    alpha = payload["metrics"]["krippendorff_alpha"]["point"]
    assert alpha == alpha
    assert alpha > 0.0
    assert payload["metrics"]["gwet_ac1"]["iterations"] > 0


def test_gwet_ac1_perfect_agreement():
    units = [["PF_ATTACK", "PF_ATTACK", "PF_ATTACK"] for _ in range(10)]
    assert gwet_ac1(units) == pytest.approx(1.0, abs=1e-9)


def test_dashboard_decision_on_fixtures(output_dir: Path):
    run_ontology_validation(
        annotator_paths=list(FIXTURE_ANNOTATORS),
        template_path=FIXTURE_TEMPLATE,
        output_dir=output_dir,
        figures_dir=output_dir / "figures",
        bootstrap_iterations=200,
        seed=42,
    )
    text = (output_dir / "ontology_decision.md").read_text(encoding="utf-8")
    assert any(label in text for label in (OntologyDecision.PASS.value, OntologyDecision.PASS_WITH_WARNINGS.value))
