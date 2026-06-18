from __future__ import annotations

from pathlib import Path

from scripts.validation.validate_dataset import main, validate_dataset_file
from scripts.segmentation.segment_discourse_units import main as segment_main
from scripts.ingestion.tests.conftest import FIXTURES as INGEST_FIXTURES
from scripts.segmentation.tests.conftest import FIXTURES as SEGMENT_FIXTURES


def test_validate_dataset_passes_for_segmented_output(tmp_path: Path):
    output = tmp_path / "discourse_units.jsonl"
    assert (
        segment_main(
            [
                "--input",
                str(SEGMENT_FIXTURES / "sample_long_document.jsonl"),
                "--output",
                str(output),
                "--max-tokens",
                "80",
                "--log-level",
                "ERROR",
            ]
        )
        == 0
    )
    report = validate_dataset_file(output)
    assert report.ok
    assert report.records_checked > 0


def test_validate_dataset_detects_duplicate_unit_id(tmp_path: Path):
    path = tmp_path / "bad.jsonl"
    duplicate = (
        '{"unit_id":"spdb-v1-unassigned-deadbeef0001","document_id":"doc-1",'
        '"language":"es","text":"Texto de prueba suficientemente largo.",'
        '"character_count":38,"token_count":8,"metadata":{"source_type":"parliamentary",'
        '"source_name":"congreso","date":"2023-07-12","speaker_name":"Ana",'
        '"speaker_party":"PSOE","segment_index":0,"char_start":0,"char_end":38}}\n'
    )
    path.write_text(duplicate + duplicate, encoding="utf-8")
    report = validate_dataset_file(path)
    assert not report.ok
    assert any("duplicate unit_id" in error for error in report.errors)


def test_validate_dataset_cli(tmp_path: Path):
    output = tmp_path / "discourse_units.jsonl"
    segment_main(
        [
            "--input",
            str(INGEST_FIXTURES / "sample_parliament_documents.jsonl"),
            "--output",
            str(output),
            "--log-level",
            "ERROR",
        ]
    )
    assert main(["--input", str(output), "--log-level", "ERROR"]) == 0
