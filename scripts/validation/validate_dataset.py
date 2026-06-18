#!/usr/bin/env python3
"""Validate SPDB pipeline discourse unit JSONL."""

from __future__ import annotations

import argparse
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Sequence

from scripts.ingestion.common import (
    default_pipeline_discourse_units_path,
    read_jsonl,
    setup_logging,
    validate_pipeline_discourse_unit,
)

logger = logging.getLogger("spdb.validation.dataset")

REQUIRED_TOP_LEVEL = (
    "unit_id",
    "document_id",
    "language",
    "text",
    "character_count",
    "token_count",
    "metadata",
)

REQUIRED_METADATA = (
    "source_type",
    "source_name",
    "date",
    "speaker_name",
    "speaker_party",
    "segment_index",
    "char_start",
    "char_end",
)

FIXTURE_ID_MARKERS = ("fixture", "synthetic", "example", "test")


def fixture_like_identifier(value: str) -> bool:
    """Return True when an identifier looks like test/fixture data."""
    lowered = value.lower()
    return any(marker in lowered for marker in FIXTURE_ID_MARKERS)


@dataclass
class DatasetValidationReport:
    records_checked: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def validate_dataset_file(path: Path) -> DatasetValidationReport:
    report = DatasetValidationReport()
    seen_unit_ids: set[str] = set()

    for index, record in enumerate(read_jsonl(path)):
        report.records_checked += 1
        label = f"record {index}"

        for field_name in REQUIRED_TOP_LEVEL:
            if field_name not in record:
                report.errors.append(f"{label}.{field_name}: required field missing")

        text = record.get("text")
        if text is None or not str(text).strip():
            report.errors.append(f"{label}.text: empty text")

        unit_id = record.get("unit_id")
        if isinstance(unit_id, str):
            if unit_id in seen_unit_ids:
                report.errors.append(f"{label}.unit_id: duplicate unit_id {unit_id!r}")
            seen_unit_ids.add(unit_id)
            if fixture_like_identifier(unit_id):
                report.warnings.append(
                    f"{label}.unit_id: fixture-like identifier {unit_id!r}"
                )

        document_id = record.get("document_id")
        if isinstance(document_id, str) and fixture_like_identifier(document_id):
            report.warnings.append(
                f"{label}.document_id: fixture-like identifier {document_id!r}"
            )

        metadata = record.get("metadata")
        if metadata is None:
            report.errors.append(f"{label}.metadata: required object missing")
        elif not isinstance(metadata, dict):
            report.errors.append(f"{label}.metadata: must be a JSON object")
        else:
            for field_name in REQUIRED_METADATA:
                if field_name not in metadata or metadata[field_name] in (None, ""):
                    report.errors.append(f"{label}.metadata.{field_name}: required field missing")
            if metadata.get("source_type") not in (None, "parliamentary"):
                report.errors.append(
                    f"{label}.metadata.source_type: expected 'parliamentary', got {metadata.get('source_type')!r}"
                )

        for message in validate_pipeline_discourse_unit(record):
            report.errors.append(f"{label}: {message}")

    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate SPDB pipeline discourse_units.jsonl.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="JSONL file to validate (default: data/processed/discourse_units.jsonl).",
    )
    parser.add_argument(
        "--allow-fixtures",
        action="store_true",
        help="Allow fixture-like document_id/unit_id markers (for test pipeline runs).",
    )
    parser.add_argument(
        "--allow-real-data",
        action="store_true",
        help="Allow real-corpus identifier patterns during validation (skips fixture warnings).",
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
    setup_logging(args.log_level)

    input_path = args.input or default_pipeline_discourse_units_path()
    if not input_path.exists():
        logger.error("Input not found: %s", input_path)
        return 1

    report = validate_dataset_file(input_path)
    if report.errors:
        for message in report.errors[:20]:
            logger.error(message)
        logger.error(
            "Validation failed: %d record(s) checked, %d error(s)",
            report.records_checked,
            len(report.errors),
        )
        return 1

    if report.warnings:
        for message in report.warnings:
            logger.warning(message)
        if not (args.allow_fixtures or args.allow_real_data):
            logger.error(
                "Validation failed: %d fixture-like identifier warning(s); "
                "pass --allow-fixtures for test data or --allow-real-data for real corpora",
                len(report.warnings),
            )
            return 1

    logger.info(
        "Validation passed: %d record(s) checked, 0 error(s)",
        report.records_checked,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
