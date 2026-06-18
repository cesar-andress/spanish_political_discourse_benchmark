from __future__ import annotations

from scripts.ingestion.common import (
    load_schema,
    read_jsonl,
    validate_discourse_unit,
    write_jsonl,
)


def test_load_schema_has_required_fields():
    schema = load_schema()
    assert "instance_id" in schema["required"]
    assert schema["properties"]["source_type"]["enum"] == [
        "parliamentary",
        "manifesto",
        "social_media",
    ]


def test_validate_discourse_unit_rejects_missing_required():
    errors = validate_discourse_unit({"instance_id": "spdb-v1-unassigned-deadbeef"})
    assert any("text: required" in err for err in errors)


def test_validate_discourse_unit_requires_platform_post_id_for_social():
    unit = {
        "instance_id": "spdb-v1-unassigned-abc",
        "text": "",
        "text_redistributable": False,
        "source_type": "social_media",
        "source_corpus": "elite_x_ids",
        "document_id": "x:1",
        "segment_index": 0,
        "char_start": 0,
        "char_end": 0,
        "language": "es",
        "date": "2024-01-01",
        "speaker_id": "user",
        "speaker_role": "legislator",
        "party_family": "PSOE",
        "chamber_or_level": "n/a",
        "election_cycle": "n/a",
        "platform": "x",
        "license_ref": "ids-only",
        "split": "unassigned",
        "annotated": False,
        "annotation_version": "none",
        "token_count_beto": 0,
        "character_count": 0,
        "created_at": "2024-01-01T00:00:00Z",
        "pipeline_version": "0.1.0",
    }
    errors = validate_discourse_unit(unit)
    assert any("platform_post_id" in err for err in errors)


def test_jsonl_roundtrip(tmp_path):
    records = [{"a": 1}, {"b": "dos"}]
    path = tmp_path / "sample.jsonl"
    assert write_jsonl(path, records) == 2
    assert list(read_jsonl(path)) == records
