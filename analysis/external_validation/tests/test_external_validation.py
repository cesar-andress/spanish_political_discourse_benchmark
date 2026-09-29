"""Tests for external validation planning framework."""

from __future__ import annotations

from pathlib import Path

from analysis.external_validation.constants import EXTERNAL_DATASETS, SPDB_FAL_LABELS
from analysis.external_validation.dataset_inventory import render_inventory_markdown
from analysis.external_validation.ontology_mapping import (
    ONTOLOGY_MAPPINGS,
    render_mapping_markdown,
    validate_mapping_coverage,
)
from analysis.external_validation.pipeline import run_external_validation
from analysis.external_validation.validation_report import render_compatibility_markdown


def test_inventory_lists_required_datasets() -> None:
    text = render_inventory_markdown()
    for name in (
        "FallacyES-Political",
        "FallacyES",
        "SemEval-2020 Task 11",
        "Argotario",
    ):
        assert name in text


def test_mapping_covers_spdb_labels_for_primary_datasets() -> None:
    missing = validate_mapping_coverage(("fallacyes_political", "fallacyes", "semeval2020_propaganda"))
    assert missing == {}


def test_mapping_markdown_contains_match_types() -> None:
    text = render_mapping_markdown()
    for kind in ("exact", "partial", "approximate", "none"):
        assert kind in text


def test_compatibility_matrix_has_scores() -> None:
    text = render_compatibility_markdown()
    assert "HIGH" in text and "LOW" in text
    assert "FallacyES-Political" in text


def test_pipeline_writes_reports(tmp_path: Path) -> None:
    result = run_external_validation(tmp_path)
    assert result.inventory_path.exists()
    assert result.mapping_path.exists()
    assert result.compatibility_path.exists()
    assert len(EXTERNAL_DATASETS) >= 6
    assert "FAL_WHATABOUT" in SPDB_FAL_LABELS
    assert "fallacyes_political" in ONTOLOGY_MAPPINGS
