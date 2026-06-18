#!/usr/bin/env python3
"""Ingest local ParlaMint TEI/XML into SPDB intermediate JSONL."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from xml.etree import ElementTree as ET

from scripts.ingestion.common import normalize_text, setup_logging, write_jsonl
from scripts.ingestion.parlamint_tei import (
    ParseStats,
    iter_parlamint_files,
    load_org_registry,
    load_person_registry,
    parse_plain_text_export,
    parse_tei_session,
)

DEFAULT_OUTPUT = Path("data/intermediate/parlamint_documents.jsonl")
UNKNOWN = "unknown"

REQUIRED_FIELDS = (
    "document_id",
    "source_type",
    "source_name",
    "date",
    "speaker_name",
    "speaker_party",
    "language",
    "text",
    "provenance",
)


@dataclass
class IngestStats:
    files_read: int = 0
    speeches_extracted: int = 0
    skipped_empty: int = 0
    missing_speaker: int = 0
    missing_date: int = 0
    missing_party: int = 0


def validate_parlamint_document(record: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    for field in REQUIRED_FIELDS:
        if field not in record or record[field] in (None, ""):
            errors.append(f"{field}: required")
    provenance = record.get("provenance")
    if not isinstance(provenance, dict):
        errors.append("provenance: must be an object")
    else:
        for key in ("source_file", "license_status"):
            if not provenance.get(key):
                errors.append(f"provenance.{key}: required")
    if record.get("source_type") != "parliamentary":
        errors.append("source_type: must be parliamentary")
    if record.get("source_name") != "ParlaMint":
        errors.append("source_name: must be ParlaMint")
    if record.get("language") != "es":
        errors.append("language: must be es")
    return errors


def _track_missing(record: Dict[str, Any], stats: IngestStats) -> None:
    if record.get("speaker_name") == UNKNOWN:
        stats.missing_speaker += 1
    if record.get("date") == UNKNOWN:
        stats.missing_date += 1
    if record.get("speaker_party") == UNKNOWN:
        stats.missing_party += 1


def _find_registry(input_path: Path, filename: str) -> Optional[Path]:
    direct = input_path / filename if input_path.is_dir() else input_path.parent / filename
    if direct.exists():
        return direct
    root = input_path if input_path.is_dir() else input_path.parent
    for candidate in root.rglob(filename):
        return candidate
    return None


def ingest_parlamint(
    input_path: Path,
    output_path: Path,
    *,
    limit_documents: Optional[int] = None,
    dry_run: bool = False,
) -> Tuple[int, List[str], IngestStats]:
    input_root = input_path if input_path.is_dir() else input_path.parent
    parse_stats = ParseStats()
    ingest_stats = IngestStats()

    person_path = _find_registry(input_path, "ParlaMint-ES-listPerson.xml")
    org_path = _find_registry(input_path, "ParlaMint-ES-listOrg.xml")
    person_registry = load_person_registry(person_path) if person_path else {}
    org_registry = load_org_registry(org_path) if org_path else {}

    documents: List[Dict[str, Any]] = []
    errors: List[str] = []

    for file_path in iter_parlamint_files(input_path):
        ingest_stats.files_read += 1
        if file_path.suffix.lower() == ".txt":
            iterator = parse_plain_text_export(
                file_path,
                input_root=input_root,
                stats=parse_stats,
            )
        else:
            iterator = parse_tei_session(
                file_path,
                person_registry=person_registry,
                org_registry=org_registry,
                input_root=input_root,
                stats=parse_stats,
            )
        for record in iterator:
            record["text"] = normalize_text(record["text"])
            field_errors = validate_parlamint_document(record)
            if field_errors:
                errors.append(f"{file_path.name}: " + "; ".join(field_errors))
                continue
            _track_missing(record, ingest_stats)
            documents.append(record)
            ingest_stats.speeches_extracted += 1
            if limit_documents is not None and len(documents) >= limit_documents:
                break
        if limit_documents is not None and len(documents) >= limit_documents:
            break

    ingest_stats.skipped_empty = parse_stats.skipped_empty

    if errors:
        return len(documents), errors, ingest_stats
    if dry_run:
        return len(documents), [], ingest_stats
    written = write_jsonl(output_path, documents)
    return written, [], ingest_stats


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SPDB ParlaMint ingestion — local TEI/XML only (no downloads).",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Directory or file with local ParlaMint TEI/XML or .txt exports.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="Intermediate JSONL output path.",
    )
    parser.add_argument(
        "--limit-documents",
        type=int,
        default=None,
        help="Maximum number of utterance documents to emit.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing output.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    logger = setup_logging(args.log_level)

    if not args.input.exists():
        logger.error("Input not found: %s", args.input)
        return 1

    try:
        count, errors, stats = ingest_parlamint(
            args.input,
            args.output,
            limit_documents=args.limit_documents,
            dry_run=args.dry_run,
        )
    except (OSError, json.JSONDecodeError, ET.ParseError) as exc:
        logger.error("%s", exc)
        return 1

    if errors:
        for message in errors[:10]:
            logger.error(message)
        return 1

    logger.info("files_read=%d", stats.files_read)
    logger.info("speeches_extracted=%d", stats.speeches_extracted)
    logger.info("skipped_empty=%d", stats.skipped_empty)
    logger.info("missing_speaker=%d", stats.missing_speaker)
    logger.info("missing_date=%d", stats.missing_date)
    logger.info("missing_party=%d", stats.missing_party)

    if args.dry_run:
        logger.info("Dry run: validated %d document(s)", count)
    else:
        logger.info("Wrote %d ParlaMint document(s) to %s", count, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
