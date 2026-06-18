#!/usr/bin/env python3
"""Ingest elite social media post IDs into SPDB discourse_unit JSONL (IDs-only path)."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from scripts.ingestion.base import BaseIngestor, IngestConfig
from scripts.ingestion.common import (
    default_intermediate_path,
    default_processed_path,
    make_instance_id,
    utc_now_iso,
)

INTERMEDIATE_REQUIRED = (
    "platform",
    "post_id",
    "author_handle",
    "author_party",
    "timestamp",
    "url",
    "rehydration_method",
)


def validate_intermediate_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in INTERMEDIATE_REQUIRED:
        if field not in record or record[field] in (None, ""):
            errors.append(f"{field}: required in social ID intermediate record")
    return errors


def timestamp_to_date(timestamp: str) -> str:
    """Extract ISO date from an ISO datetime or date string."""
    return timestamp[:10]


class SocialIdsIngestor(BaseIngestor):
    source_name = "social"
    source_type = "social_media"
    source_corpus = "elite_x_ids"

    def __init__(self, config: IngestConfig, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, logger)
        self.platform_override: Optional[str] = None

    @classmethod
    def add_source_cli_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--source-corpus",
            default="elite_x_ids",
            help="Value for discourse_unit.source_corpus.",
        )
        parser.add_argument(
            "--platform",
            default=None,
            help="Override platform for all records (otherwise taken from input).",
        )

    @classmethod
    def from_args(cls, config: IngestConfig, args: argparse.Namespace) -> "SocialIdsIngestor":
        ingestor = cls(config)
        ingestor.source_corpus = args.source_corpus
        ingestor.platform_override = args.platform
        return ingestor

    def parse_raw(self, input_path: Path) -> Iterator[Dict[str, Any]]:
        if input_path.is_dir():
            raise NotImplementedError(
                "Directory ingestion is not implemented yet; provide a JSONL or JSON file."
            )

        suffix = input_path.suffix.lower()
        if suffix == ".jsonl":
            from scripts.ingestion.common import read_jsonl

            records = read_jsonl(input_path)
        elif suffix == ".json":
            payload = json.loads(input_path.read_text(encoding="utf-8"))
            records = iter(payload if isinstance(payload, list) else payload["records"])
        elif suffix == ".csv":
            raise NotImplementedError(
                "CSV parser not implemented yet; convert to JSONL stub for architecture tests."
            )
        else:
            raise NotImplementedError(
                f"Parser for {suffix!r} not implemented; supply JSONL/JSON stub input."
            )

        for index, record in enumerate(records):
            if self.platform_override:
                record = {**record, "platform": self.platform_override}
            errors = validate_intermediate_record(record)
            if errors:
                raise ValueError(f"intermediate record {index}: " + "; ".join(errors))
            yield record

    def to_discourse_units(self, intermediate_records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        """
        Map post IDs to discourse units.

        Public release path: empty text, text_redistributable=false.
        Local annotation rebuild happens outside this script.
        """
        created_at = utc_now_iso()
        for index, post in enumerate(intermediate_records):
            document_id = f"{post['platform']}:{post['post_id']}"
            speaker_id = post.get("author_id") or post["author_handle"]
            yield {
                "instance_id": make_instance_id(document_id, 0, self.config.split),
                "text": "",
                "text_redistributable": False,
                "source_type": self.source_type,
                "source_corpus": self.source_corpus,
                "document_id": document_id,
                "segment_index": 0,
                "char_start": 0,
                "char_end": 0,
                "language": post.get("language", "es"),
                "date": timestamp_to_date(post["timestamp"]),
                "speaker_id": speaker_id,
                "speaker_role": post.get("speaker_role", "legislator"),
                "party_family": post.get("party_family") or post["author_party"],
                "chamber_or_level": post.get("chamber_or_level", "n/a"),
                "election_cycle": post.get("election_cycle", "n/a"),
                "platform": post["platform"],
                "platform_post_id": post["post_id"],
                "rehydration_url": post["url"],
                "license_ref": post.get("license_ref", "ids-only"),
                "split": self.config.split,
                "annotated": False,
                "annotation_version": "none",
                "token_count_beto": 0,
                "character_count": 0,
                "created_at": created_at,
                "pipeline_version": self.config.pipeline_version,
            }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SPDB v1 ingestion — social IDs")
    from scripts.ingestion.base import add_common_cli_args

    add_common_cli_args(parser)
    SocialIdsIngestor.add_source_cli_args(parser)
    args = parser.parse_args(argv)

    from scripts.ingestion.common import setup_logging

    setup_logging(args.log_level)
    config = IngestConfig(
        input_path=args.input,
        intermediate_path=args.intermediate_out
        or default_intermediate_path("social", "post_ids.jsonl"),
        processed_path=args.processed_out or default_processed_path("social"),
        pipeline_version=args.pipeline_version,
        split=args.split,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
    )
    SocialIdsIngestor.from_args(config, args).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
