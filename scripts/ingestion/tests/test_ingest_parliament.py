from __future__ import annotations

from pathlib import Path

from scripts.ingestion.ingest_parliament import ingest_parliament, main
from scripts.ingestion.common import read_jsonl, validate_parliament_document
from scripts.ingestion.tests.conftest import FIXTURES


def test_ingest_parliament_writes_intermediate_jsonl(tmp_path: Path):
    output = tmp_path / "parliament_documents.jsonl"
    count, errors = ingest_parliament(
        FIXTURES / "sample_parliamentary.jsonl",
        output,
    )
    assert errors == []
    assert count == 1

    documents = list(read_jsonl(output))
    assert documents[0]["document_id"] == "congreso-2023-001"
    assert documents[0]["speaker_name"] == "Ana Example"
    assert documents[0]["source_type"] == "parliamentary"
    assert all(not validate_parliament_document(document) for document in documents)


def test_ingest_parliament_dry_run():
    count, errors = ingest_parliament(
        FIXTURES / "sample_parliament_documents.jsonl",
        Path("/tmp/unused.jsonl"),
        dry_run=True,
    )
    assert errors == []
    assert count == 1


def test_ingest_parliament_cli(tmp_path: Path):
    output = tmp_path / "parliament_documents.jsonl"
    assert (
        main(
            [
                "--input",
                str(FIXTURES / "sample_parliament_documents.jsonl"),
                "--output",
                str(output),
                "--log-level",
                "ERROR",
            ]
        )
        == 0
    )
    assert output.exists()
