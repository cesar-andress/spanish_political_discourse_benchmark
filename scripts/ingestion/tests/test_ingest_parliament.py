from __future__ import annotations

from pathlib import Path

from scripts.ingestion.base import IngestConfig
from scripts.ingestion.ingest_parliament import ParliamentIngestor
from scripts.ingestion.common import read_jsonl, validate_discourse_unit
from scripts.ingestion.tests.conftest import FIXTURES


def test_parliament_ingestor_writes_jsonl(tmp_path: Path):
    config = IngestConfig(
        input_path=FIXTURES / "sample_parliamentary.jsonl",
        intermediate_path=tmp_path / "intermediate.jsonl",
        processed_path=tmp_path / "processed.jsonl",
        pipeline_version="0.1.0-test",
    )
    intermediate_count, processed_count = ParliamentIngestor(config).run()
    assert intermediate_count == 1
    assert processed_count == 2

    units = list(read_jsonl(config.processed_path))
    assert all(unit["source_type"] == "parliamentary" for unit in units)
    assert all(unit["text_redistributable"] is True for unit in units)
    assert all(not validate_discourse_unit(unit) for unit in units)


def test_parliament_dry_run():
    config = IngestConfig(
        input_path=FIXTURES / "sample_parliamentary.jsonl",
        intermediate_path=Path("/tmp/unused-intermediate.jsonl"),
        processed_path=Path("/tmp/unused-processed.jsonl"),
        dry_run=True,
    )
    intermediate_count, processed_count = ParliamentIngestor(config).run()
    assert intermediate_count == 1
    assert processed_count == 2
