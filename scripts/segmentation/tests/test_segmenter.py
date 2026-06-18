from __future__ import annotations

from scripts.ingestion.common import read_jsonl, validate_discourse_unit, validate_pipeline_discourse_unit
from scripts.segmentation.common import make_unit_id
from scripts.segmentation.segmenter import SegmentConfig, segment_document, segment_document_pipeline
from scripts.segmentation.tests.conftest import FIXTURES


def test_make_unit_id_is_stable():
    first = make_unit_id("doc-1", 0, "unassigned")
    second = make_unit_id("doc-1", 0, "unassigned")
    third = make_unit_id("doc-1", 1, "unassigned")
    assert first == second
    assert first.startswith("spdb-v1-unassigned-")
    assert first != third


def test_segment_long_document_produces_multiple_units():
    doc = next(read_jsonl(FIXTURES / "sample_long_document.jsonl"))
    units = segment_document_pipeline(doc, SegmentConfig(max_tokens_beto=80))
    assert len(units) >= 3
    assert all(unit["document_id"] == doc["document_id"] for unit in units)
    assert all(unit["language"] == "es" for unit in units)
    assert all(unit["metadata"]["speaker_party"] == "PSOE" for unit in units)
    assert all(unit["character_count"] == len(unit["text"]) for unit in units)
    assert all(unit["token_count"] > 0 for unit in units)
    assert all(not validate_pipeline_discourse_unit(unit) for unit in units)


def test_segment_indices_are_sequential():
    doc = next(read_jsonl(FIXTURES / "sample_long_document.jsonl"))
    units = segment_document_pipeline(doc, SegmentConfig(max_tokens_beto=80))
    assert [unit["metadata"]["segment_index"] for unit in units] == list(range(len(units)))


def test_short_spans_are_filtered():
    doc = {
        "doc_id": "filter-test",
        "date": "2023-01-01",
        "party": "PSOE",
        "chamber": "congreso",
        "license_ref": "CC-BY-4.0",
        "source_type": "parliamentary",
        "source_corpus": "congreso_es",
        "text_raw": (
            "Corto.\n\n"
            "Este párrafo sí supera el mínimo de longitud exigido para ser una unidad válida."
        ),
    }
    units = segment_document(doc, SegmentConfig(min_chars=20, max_tokens_beto=400))
    assert units
    assert all(len(unit["text"]) >= 20 for unit in units)
    assert all("Corto." not in unit["text"] for unit in units)
    assert all(not validate_discourse_unit(unit) for unit in units)
