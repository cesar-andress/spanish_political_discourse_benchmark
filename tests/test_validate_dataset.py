from __future__ import annotations

from pathlib import Path

from scripts.validation.validate_dataset import (
    fixture_like_identifier,
    main,
    validate_dataset_file,
)
from scripts.segmentation.segment_discourse_units import main as segment_main
from tests.conftest import PIPELINE_FIXTURES


def test_validate_dataset_passes_for_segmented_output(tmp_path: Path):
    output = tmp_path / "discourse_units.jsonl"
    assert (
        segment_main(
            [
                "--input",
                str(PIPELINE_FIXTURES / "sample_long_document.jsonl"),
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
    assert not report.warnings


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
            str(PIPELINE_FIXTURES / "sample_parliament_documents.jsonl"),
            "--output",
            str(output),
            "--log-level",
            "ERROR",
        ]
    )
    assert main(["--input", str(output), "--log-level", "ERROR"]) == 0


def test_fixture_like_identifier_markers():
    assert fixture_like_identifier("congreso-fixture-001")
    assert fixture_like_identifier("synthetic-doc-01")
    assert fixture_like_identifier("example-intervention")
    assert fixture_like_identifier("spdb-v1-unassigned-testhash")
    assert not fixture_like_identifier("congreso-2023-001")


def test_validate_dataset_warns_on_fixture_identifiers(tmp_path: Path):
    path = tmp_path / "fixture_units.jsonl"
    path.write_text(
        '{"unit_id":"spdb-v1-unassigned-abc","document_id":"fixture-doc-001",'
        '"language":"es","text":"Texto de prueba suficientemente largo.",'
        '"character_count":38,"token_count":8,"metadata":{"source_type":"parliamentary",'
        '"source_name":"congreso","date":"2023-07-12","speaker_name":"Ana",'
        '"speaker_party":"PSOE","segment_index":0,"char_start":0,"char_end":38}}\n',
        encoding="utf-8",
    )
    report = validate_dataset_file(path)
    assert report.ok
    assert report.warnings
    assert main(["--input", str(path), "--log-level", "ERROR"]) == 1
    assert main(["--input", str(path), "--allow-fixtures", "--log-level", "ERROR"]) == 0
