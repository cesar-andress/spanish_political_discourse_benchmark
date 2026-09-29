"""Tests for dataset card generation."""

from __future__ import annotations

from pathlib import Path

from scripts.release.generate_dataset_card import (
    generate_dataset_card,
    render_dataset_card,
)
from scripts.release.metadata_loader import load_citation_metadata


def test_load_citation_metadata_has_doi_and_authors():
    meta = load_citation_metadata()
    assert meta.doi == "10.5281/zenodo.23039355"
    assert "Baena Rojas" in meta.authors_bibtex
    assert "Andrés" in meta.authors_bibtex
    assert "Spanish Political Discourse" in meta.title
    assert meta.version == "1.0.0"


def test_render_includes_required_hf_sections():
    meta = load_citation_metadata()
    card = render_dataset_card(
        citation=meta,
        pf_labels=["PF_ATTACK", "PF_INFO"],
        fal_labels=["FAL_NONE", "FAL_ADHOM"],
    )
    assert card.startswith("---")
    assert "license: cc-by-4.0" in card
    assert "## Motivation" in card
    assert "## Dataset composition" in card
    assert "## Collection process" in card
    assert "## Annotation process" in card
    assert "## Splits" in card
    assert "## Licensing" in card
    assert "## Known limitations" in card
    assert "## Ethical considerations" in card
    assert "## Citation" in card
    assert "task_categories:" in card


def test_generate_writes_root_and_legacy_paths(tmp_path: Path):
    output = tmp_path / "dataset_card.md"
    legacy = tmp_path / "legacy/dataset_card.md"
    path = generate_dataset_card(output_path=output, legacy_output_path=legacy)
    assert path.exists()
    assert legacy.exists()
    text = path.read_text(encoding="utf-8")
    assert "PF_ADVOCACY" in text
    assert "10.5281/zenodo.23039355" in text
