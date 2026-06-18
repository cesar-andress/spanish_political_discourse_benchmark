from __future__ import annotations

from pathlib import Path

from scripts.ingestion.base import IngestConfig
from scripts.ingestion.ingest_social_ids import SocialIdsIngestor
from scripts.ingestion.common import read_jsonl, validate_discourse_unit
from scripts.ingestion.tests.conftest import FIXTURES


def test_social_ids_ingestor_writes_jsonl(tmp_path: Path):
    config = IngestConfig(
        input_path=FIXTURES / "sample_social_ids.jsonl",
        intermediate_path=tmp_path / "intermediate.jsonl",
        processed_path=tmp_path / "processed.jsonl",
    )
    intermediate_count, processed_count = SocialIdsIngestor(config).run()
    assert intermediate_count == 1
    assert processed_count == 1

    unit = next(read_jsonl(config.processed_path))
    assert unit["source_type"] == "social_media"
    assert unit["text"] == ""
    assert unit["text_redistributable"] is False
    assert unit["platform_post_id"] == "1234567890"
    assert not validate_discourse_unit(unit)
