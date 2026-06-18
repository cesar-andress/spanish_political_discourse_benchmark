#!/usr/bin/env python3
"""Ingest parliamentary discourse into SPDB discourse_unit JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Sequence

from scripts.ingestion.base import BaseIngestor, IngestConfig
from scripts.ingestion.common import (
    default_intermediate_path,
    default_processed_path,
    make_instance_id,
    normalize_text,
    utc_now_iso,
)

INTERMEDIATE_REQUIRED = (
    "doc_id",
    "speaker",
    "party",
    "date",
    "chamber",
    "text_raw",
    "url",
    "license_ref",
)


def validate_intermediate_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in INTERMEDIATE_REQUIRED:
        if field not in record or record[field] in (None, ""):
            errors.append(f"{field}: required in parliamentary intermediate record")
    return errors


def segment_intervention(text_raw: str, max_chars: int = 1600) -> List[tuple[str, int, int]]:
    """
    Split an intervention into discourse segments.

    Stub segmentation: paragraph breaks, then hard cap by character length.
    """
    paragraphs = [part.strip() for part in text_raw.split("\n\n") if part.strip()]
    if not paragraphs:
        paragraphs = [text_raw.strip()] if text_raw.strip() else [""]

    segments: List[tuple[str, int, int]] = []
    cursor = 0
    for paragraph in paragraphs:
        normalized = normalize_text(paragraph)
        if not normalized:
            continue
        if len(normalized) <= max_chars:
            start = cursor
            end = cursor + len(normalized)
            segments.append((normalized, start, end))
            cursor = end + 1
            continue
        start = 0
        while start < len(normalized):
            chunk = normalized[start : start + max_chars]
            abs_start = cursor + start
            abs_end = abs_start + len(chunk)
            segments.append((chunk, abs_start, abs_end))
            start += max_chars
        cursor += len(normalized) + 1
    return segments or [("", 0, 0)]


class ParliamentIngestor(BaseIngestor):
    source_name = "parliamentary"
    source_type = "parliamentary"
    source_corpus = "congreso_es"

    def __init__(self, config: IngestConfig, jurisdiction: str = "es_state", **kwargs: Any) -> None:
        super().__init__(config, **kwargs)
        self.jurisdiction = jurisdiction

    @classmethod
    def add_source_cli_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--jurisdiction",
            default="es_state",
            help="Jurisdiction slug for provenance (e.g. es_state, senado_es).",
        )
        parser.add_argument(
            "--source-corpus",
            default="congreso_es",
            help="Value for discourse_unit.source_corpus.",
        )

    @classmethod
    def from_args(cls, config: IngestConfig, args: argparse.Namespace) -> "ParliamentIngestor":
        ingestor = cls(config, jurisdiction=args.jurisdiction)
        ingestor.source_corpus = args.source_corpus
        return ingestor

    def parse_raw(self, input_path: Path) -> Iterator[Dict[str, Any]]:
        """
        Parse local raw parliamentary input.

        Supported stub formats:
        - JSONL with one intervention per line
        - Single JSON array file
        """
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
            if isinstance(payload, list):
                records = iter(payload)
            elif isinstance(payload, dict) and "records" in payload:
                records = iter(payload["records"])
            else:
                raise ValueError("JSON input must be an array or {\"records\": [...]}")
        else:
            raise NotImplementedError(
                f"Parser for {suffix!r} not implemented; supply JSONL/JSON stub input."
            )

        for index, record in enumerate(records):
            errors = validate_intermediate_record(record)
            if errors:
                raise ValueError(f"intermediate record {index}: " + "; ".join(errors))
            yield record

    def to_discourse_units(self, intermediate_records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        created_at = utc_now_iso()
        for doc in intermediate_records:
            text_raw = doc["text_raw"]
            segments = segment_intervention(text_raw)
            speaker_id = doc.get("speaker_id") or f"speaker-{doc['speaker']}"
            for segment_index, (text, char_start, char_end) in enumerate(segments):
                yield {
                    "instance_id": make_instance_id(doc["doc_id"], segment_index, self.config.split),
                    "text": text,
                    "text_redistributable": True,
                    "source_type": self.source_type,
                    "source_corpus": self.source_corpus,
                    "document_id": doc["doc_id"],
                    "segment_index": segment_index,
                    "char_start": char_start,
                    "char_end": char_end,
                    "language": doc.get("language", "es"),
                    "date": doc["date"],
                    "speaker_id": speaker_id,
                    "speaker_role": doc.get("speaker_role", "legislator"),
                    "party_family": doc.get("party_family") or doc["party"],
                    "chamber_or_level": doc["chamber"],
                    "election_cycle": doc.get("election_cycle", "n/a"),
                    "platform": "n/a",
                    "license_ref": doc["license_ref"],
                    "split": self.config.split,
                    "annotated": False,
                    "annotation_version": "none",
                    "token_count_beto": 0,
                    "character_count": len(text),
                    "created_at": created_at,
                    "pipeline_version": self.config.pipeline_version,
                    "rehydration_url": doc.get("url", ""),
                }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SPDB v1 ingestion — parliamentary")
    from scripts.ingestion.base import add_common_cli_args

    add_common_cli_args(parser)
    ParliamentIngestor.add_source_cli_args(parser)
    args = parser.parse_args(argv)

    from scripts.ingestion.common import setup_logging

    setup_logging(args.log_level)
    config = IngestConfig(
        input_path=args.input,
        intermediate_path=args.intermediate_out
        or default_intermediate_path("parliamentary", "documents.jsonl"),
        processed_path=args.processed_out
        or default_processed_path("parliamentary"),
        pipeline_version=args.pipeline_version,
        split=args.split,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
    )
    ingestor = ParliamentIngestor.from_args(config, args)
    ingestor.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
