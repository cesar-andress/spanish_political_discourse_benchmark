"""Tests for Gebru et al. datasheet generation."""

from __future__ import annotations

from pathlib import Path

from scripts.release.generate_datasheet import generate_datasheet, render_datasheet
from scripts.release.metadata_loader import load_citation_metadata


def test_render_includes_gebru_sections():
    citation = load_citation_metadata()
    content, pending = render_datasheet(
        citation=citation,
        pf_labels=["PF_ATTACK"],
        fal_labels=["FAL_NONE", "FAL_ADHOM"],
    )
    assert "Gebru" in content
    assert "## 1. Motivation" in content
    assert "## 2. Composition" in content
    assert "## 3. Collection Process" in content
    assert "## 4. Preprocessing / Cleaning / Labeling" in content
    assert "## 5. Uses" in content
    assert "## 6. Distribution" in content
    assert "## 7. Maintenance" in content
    assert "## Pending sections summary" in content
    assert "Who funded the creation of the dataset?" in content
    assert len(pending) >= 1


def test_generate_writes_output(tmp_path: Path):
    output = tmp_path / "datasheet_for_datasets.md"
    path, pending = generate_datasheet(output_path=output)
    assert path.exists()
    text = path.read_text(encoding="utf-8")
    assert "10.5281/zenodo.20745403" in text
    assert "PF_ADVOCACY" in text or "PF_ATTACK" in text
    assert "**TODO:**" in text
    assert pending
