#!/usr/bin/env python3
"""CLI: segment parliament documents into pipeline discourse units."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

from scripts.ingestion.common import (
    default_parliament_documents_path,
    default_pipeline_discourse_units_path,
    read_jsonl,
    validate_pipeline_discourse_unit,
    write_jsonl,
)
from scripts.segmentation.common import setup_logging
from scripts.segmentation.segmenter import SegmentConfig, segment_documents_pipeline

logger = logging.getLogger("spdb.segmentation.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SPDB discourse segmentation — parliament documents to discourse units.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Input JSONL (default: data/intermediate/parliament_documents.jsonl).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSONL (default: data/processed/discourse_units.jsonl).",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=400,
        help="Maximum tokens per unit before sentence-level splitting.",
    )
    parser.add_argument(
        "--min-chars",
        type=int,
        default=20,
        help="Minimum character length for a unit (shorter spans are dropped).",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=2000,
        help="Maximum character length for a unit.",
    )
    parser.add_argument(
        "--split",
        default="unassigned",
        choices=["train", "dev", "test", "unassigned"],
        help="Split label embedded in unit_id.",
    )
    parser.add_argument(
        "--use-beto-model",
        action="store_true",
        help="Use Hugging Face BETO tokenizer when available (offline runs use estimate fallback).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Segment and validate without writing output JSONL.",
    )
    parser.add_argument(
        "--document-id",
        default=None,
        help="Segment a single document_id from the input file.",
    )
    return parser


def run_segmentation(args: argparse.Namespace) -> tuple[int, int]:
    input_path = args.input or default_parliament_documents_path()
    config = SegmentConfig(
        max_tokens_beto=args.max_tokens,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        split=args.split,
        use_beto_model=args.use_beto_model,
    )

    documents = list(read_jsonl(input_path))
    if args.document_id:
        documents = [
            doc for doc in documents if doc.get("document_id") == args.document_id
        ]
        if not documents:
            raise ValueError(f"document id not found in input: {args.document_id}")

    units = list(segment_documents_pipeline(documents, config))
    validation_errors: list[str] = []
    for index, unit in enumerate(units):
        field_errors = validate_pipeline_discourse_unit(unit)
        for message in field_errors:
            validation_errors.append(f"unit {index}: {message}")

    if validation_errors:
        for message in validation_errors[:10]:
            logger.error(message)
        raise ValueError(f"Validation failed with {len(validation_errors)} error(s)")

    if args.dry_run:
        logger.info("Dry run: validated %d unit(s); no output written", len(units))
        return len(documents), len(units)

    output_path = args.output or default_pipeline_discourse_units_path()
    written = write_jsonl(output_path, units)
    logger.info("Wrote %d discourse unit(s) to %s", written, output_path)
    return len(documents), written


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.log_level)

    input_path = args.input or default_parliament_documents_path()
    if not input_path.exists():
        logger.error("Input not found: %s", input_path)
        return 1

    try:
        documents, units = run_segmentation(args)
    except (ValueError, NotImplementedError) as exc:
        logger.error("%s", exc)
        return 1

    logger.info("Segmented %d document(s) into %d unit(s)", documents, units)
    return 0


if __name__ == "__main__":
    sys.exit(main())
