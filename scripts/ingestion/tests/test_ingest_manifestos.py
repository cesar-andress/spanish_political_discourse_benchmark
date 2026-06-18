from __future__ import annotations

from pathlib import Path

from scripts.ingestion.base import IngestConfig
from scripts.ingestion.ingest_manifestos import ManifestoIngestor
from scripts.ingestion.common import read_jsonl, validate_discourse_unit
from scripts.ingestion.tests.conftest import FIXTURES


def test_manifesto_ingestor_writes_jsonl(tmp_path: Path):
    config = IngestConfig(
        input_path=FIXTURES / "sample_manifesto.jsonl",
        intermediate_path=tmp_path / "intermediate.jsonl",
        processed_path=tmp_path / "processed.jsonl",
    )
    intermediate_count, processed_count = ManifestoIngestor(config).run()
    assert intermediate_count == 1
    assert processed_count == 1

    unit = next(read_jsonl(config.processed_path))
    assert unit["source_type"] == "manifesto"
    assert unit["speaker_role"] == "party_org"
    assert not validate_discourse_unit(unit)
