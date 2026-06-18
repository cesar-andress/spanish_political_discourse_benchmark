#!/usr/bin/env python3
"""Ingest party manifestos into SPDB discourse_unit JSONL."""

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
    normalize_text,
    utc_now_iso,
)

INTERMEDIATE_REQUIRED = (
    "doc_id",
    "party",
    "date",
    "section_title",
    "text_raw",
    "license_ref",
)


def validate_intermediate_record(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in INTERMEDIATE_REQUIRED:
        if field not in record or record[field] in (None, ""):
            errors.append(f"{field}: required in manifesto intermediate record")
    return errors


def segment_paragraph(text_raw: str, max_chars: int = 1600) -> List[tuple[str, int, int]]:
    """One paragraph per unit when short enough; otherwise sentence-boundary stub."""
    normalized = normalize_text(text_raw)
    if not normalized:
        return [("", 0, 0)]
    if len(normalized) <= max_chars:
        return [(normalized, 0, len(normalized))]

    segments: List[tuple[str, int, int]] = []
    start = 0
    while start < len(normalized):
        chunk = normalized[start : start + max_chars]
        segments.append((chunk, start, start + len(chunk)))
        start += max_chars
    return segments


class ManifestoIngestor(BaseIngestor):
    source_name = "manifestos"
    source_type = "manifesto"
    source_corpus = "marpor_es"

    def __init__(self, config: IngestConfig, logger: Optional[logging.Logger] = None) -> None:
        super().__init__(config, logger)
        self.ocr = False

    @classmethod
    def add_source_cli_args(cls, parser: argparse.ArgumentParser) -> None:
        parser.add_argument(
            "--source-corpus",
            default="marpor_es",
            help="Value for discourse_unit.source_corpus (e.g. marpor_es, party_pdf_es).",
        )
        parser.add_argument(
            "--ocr",
            action="store_true",
            help="Flag manifesto text extracted via OCR (stored in intermediate metadata).",
        )

    @classmethod
    def from_args(cls, config: IngestConfig, args: argparse.Namespace) -> "ManifestoIngestor":
        ingestor = cls(config)
        ingestor.source_corpus = args.source_corpus
        ingestor.ocr = args.ocr
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
        else:
            raise NotImplementedError(
                f"Parser for {suffix!r} not implemented; supply JSONL/JSON stub input."
            )

        for index, record in enumerate(records):
            if self.ocr:
                record = {**record, "ocr": True}
            errors = validate_intermediate_record(record)
            if errors:
                raise ValueError(f"intermediate record {index}: " + "; ".join(errors))
            yield record

    def to_discourse_units(self, intermediate_records: Iterator[Dict[str, Any]]) -> Iterator[Dict[str, Any]]:
        created_at = utc_now_iso()
        for doc in intermediate_records:
            segments = segment_paragraph(doc["text_raw"])
            speaker_id = doc.get("speaker_id") or f"party-{doc['party']}"
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
                    "speaker_role": doc.get("speaker_role", "party_org"),
                    "party_family": doc.get("party_family") or doc["party"],
                    "chamber_or_level": doc.get("chamber_or_level", "n/a"),
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
                }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="SPDB v1 ingestion — manifestos")
    from scripts.ingestion.base import add_common_cli_args

    add_common_cli_args(parser)
    ManifestoIngestor.add_source_cli_args(parser)
    args = parser.parse_args(argv)

    from scripts.ingestion.common import setup_logging

    setup_logging(args.log_level)
    config = IngestConfig(
        input_path=args.input,
        intermediate_path=args.intermediate_out
        or default_intermediate_path("manifestos", "documents.jsonl"),
        processed_path=args.processed_out or default_processed_path("manifestos"),
        pipeline_version=args.pipeline_version,
        split=args.split,
        dry_run=args.dry_run,
        validate_only=args.validate_only,
    )
    ManifestoIngestor.from_args(config, args).run()
    return 0


if __name__ == "__main__":
    sys.exit(main())
