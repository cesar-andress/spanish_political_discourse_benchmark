#!/usr/bin/env python3
"""Ingest local parliamentary sources into intermediate JSONL documents."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence

from scripts.ingestion.common import (
    default_parliament_documents_path,
    normalize_text,
    read_jsonl,
    setup_logging,
    validate_parliament_document,
    write_jsonl,
)

CANONICAL_FIELDS = (
    "document_id",
    "source_type",
    "source_name",
    "date",
    "speaker_name",
    "speaker_party",
    "language",
    "text",
)

FIELD_ALIASES: Dict[str, Sequence[str]] = {
    "document_id": ("document_id", "doc_id", "id"),
    "source_type": ("source_type",),
    "source_name": ("source_name", "source_corpus", "chamber", "corpus"),
    "date": ("date", "session_date", "timestamp"),
    "speaker_name": ("speaker_name", "speaker", "author"),
    "speaker_party": ("speaker_party", "party", "party_family"),
    "language": ("language", "lang"),
    "text": ("text", "text_raw", "content", "body"),
}


@dataclass
class TextDefaults:
    document_id: Optional[str] = None
    source_name: str = "parliamentary"
    date: str = "1970-01-01"
    speaker_name: str = "unknown"
    speaker_party: str = "unknown"
    language: str = "es"


def _first_value(record: Mapping[str, Any], field: str) -> Any:
    for alias in FIELD_ALIASES[field]:
        value = record.get(alias)
        if value not in (None, ""):
            return value
    return None


def normalize_parliament_record(
    record: Mapping[str, Any],
    *,
    defaults: Optional[TextDefaults] = None,
    fallback_document_id: Optional[str] = None,
) -> Dict[str, Any]:
    """Map vendor-specific keys to the canonical intermediate schema."""
    defaults = defaults or TextDefaults()
    document_id = _first_value(record, "document_id") or defaults.document_id or fallback_document_id
    text_value = _first_value(record, "text")
    if text_value is None and "text" not in record:
        text_value = record.get("text_raw", "")

    normalized = {
        "document_id": str(document_id) if document_id is not None else None,
        "source_type": str(_first_value(record, "source_type") or "parliamentary"),
        "source_name": str(_first_value(record, "source_name") or defaults.source_name),
        "date": str(_first_value(record, "date") or defaults.date),
        "speaker_name": str(_first_value(record, "speaker_name") or defaults.speaker_name),
        "speaker_party": str(_first_value(record, "speaker_party") or defaults.speaker_party),
        "language": str(_first_value(record, "language") or defaults.language),
        "text": normalize_text(str(text_value or "")),
    }

    if "T" in normalized["date"]:
        normalized["date"] = normalized["date"][:10]

    return normalized


def _load_sidecar_metadata(path: Path) -> Dict[str, Any]:
    sidecar = path.with_suffix(".json")
    if not sidecar.exists():
        return {}
    payload = json.loads(sidecar.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{sidecar}: sidecar metadata must be a JSON object")
    return payload


def _parse_json_records(path: Path) -> Iterator[Dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        yield from read_jsonl(path)
        return

    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        yield from payload
    elif isinstance(payload, dict) and "records" in payload:
        records = payload["records"]
        if not isinstance(records, list):
            raise ValueError('JSON input {"records": ...} must contain an array')
        yield from records
    elif isinstance(payload, dict):
        yield payload
    else:
        raise ValueError("JSON input must be an object, array, or {\"records\": [...]}")


def _parse_csv_records(path: Path) -> Iterator[Dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"{path}: CSV file has no header row")
        for row in reader:
            yield dict(row)


def _parse_txt_record(path: Path, defaults: TextDefaults) -> Dict[str, Any]:
    sidecar = _load_sidecar_metadata(path)
    text = path.read_text(encoding="utf-8")
    merged_defaults = TextDefaults(
        document_id=defaults.document_id or path.stem,
        source_name=defaults.source_name,
        date=defaults.date,
        speaker_name=defaults.speaker_name,
        speaker_party=defaults.speaker_party,
        language=defaults.language,
    )
    payload = {"text": text, **sidecar}
    return normalize_parliament_record(
        payload,
        defaults=merged_defaults,
        fallback_document_id=path.stem,
    )


def parse_input(path: Path, defaults: TextDefaults) -> Iterator[Dict[str, Any]]:
    """
    Parse local parliamentary input without network access.

    Supported formats:
    - ``.jsonl`` / ``.json`` structured records
    - ``.csv`` with a header row
    - ``.txt`` plain text (optional ``.json`` sidecar with metadata)
    - directory of ``.txt`` files
    """
    if path.is_dir():
        txt_files = sorted(path.glob("*.txt"))
        if not txt_files:
            raise ValueError(f"No .txt files found in directory: {path}")
        for txt_path in txt_files:
            yield _parse_txt_record(txt_path, defaults)
        return

    suffix = path.suffix.lower()
    if suffix in {".jsonl", ".json"}:
        records = _parse_json_records(path)
    elif suffix == ".csv":
        records = _parse_csv_records(path)
    elif suffix == ".txt":
        yield _parse_txt_record(path, defaults)
        return
    else:
        raise ValueError(
            f"Unsupported input format {suffix!r}; use .jsonl, .json, .csv, or .txt"
        )

    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"record {index}: expected JSON object")
        yield normalize_parliament_record(
            record,
            defaults=defaults,
            fallback_document_id=f"{path.stem}-{index:04d}",
        )


def ingest_parliament(
    input_path: Path,
    output_path: Path,
    *,
    defaults: Optional[TextDefaults] = None,
    dry_run: bool = False,
) -> tuple[int, List[str]]:
    defaults = defaults or TextDefaults()
    documents = list(parse_input(input_path, defaults))
    errors: List[str] = []
    for index, document in enumerate(documents):
        field_errors = validate_parliament_document(document)
        for message in field_errors:
            errors.append(f"document {index}: {message}")

    if errors:
        return len(documents), errors

    if dry_run:
        return len(documents), []

    written = write_jsonl(output_path, documents)
    return written, []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SPDB parliamentary ingestion — local files to intermediate JSONL.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Local .jsonl, .json, .csv, .txt file, or directory of .txt files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Intermediate JSONL path (default: data/intermediate/parliament_documents.jsonl).",
    )
    parser.add_argument(
        "--source-name",
        default="parliamentary",
        help="Default source_name when not present in input records.",
    )
    parser.add_argument(
        "--date",
        default="1970-01-01",
        help="Default ISO date for plain-text inputs without metadata.",
    )
    parser.add_argument(
        "--speaker-name",
        default="unknown",
        help="Default speaker_name for plain-text inputs without metadata.",
    )
    parser.add_argument(
        "--speaker-party",
        default="unknown",
        help="Default speaker_party for plain-text inputs without metadata.",
    )
    parser.add_argument(
        "--language",
        default="es",
        help="Default language code (ISO 639-1).",
    )
    parser.add_argument(
        "--document-id",
        default=None,
        help="Override document_id for a single plain-text input file.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Parse and validate without writing output JSONL.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logger = setup_logging(args.log_level)

    if not args.input.exists():
        logger.error("Input not found: %s", args.input)
        return 1

    defaults = TextDefaults(
        document_id=args.document_id,
        source_name=args.source_name,
        date=args.date,
        speaker_name=args.speaker_name,
        speaker_party=args.speaker_party,
        language=args.language,
    )
    output_path = args.output or default_parliament_documents_path()

    try:
        count, errors = ingest_parliament(
            args.input,
            output_path,
            defaults=defaults,
            dry_run=args.dry_run,
        )
    except (ValueError, json.JSONDecodeError, OSError) as exc:
        logger.error("%s", exc)
        return 1

    if errors:
        for message in errors[:10]:
            logger.error(message)
        logger.error("Validation failed with %d error(s)", len(errors))
        return 1

    if args.dry_run:
        logger.info("Dry run: validated %d document(s); no output written", count)
    else:
        logger.info("Wrote %d document(s) to %s", count, output_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
