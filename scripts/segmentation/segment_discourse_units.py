#!/usr/bin/env python3
"""CLI: segment long political texts into SPDB discourse_unit JSONL."""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Optional, Sequence

from scripts.ingestion.common import read_jsonl, validate_discourse_unit, write_jsonl
from scripts.segmentation.common import default_segmented_path, setup_logging
from scripts.segmentation.segmenter import SegmentConfig, segment_document, segment_documents

logger = logging.getLogger("spdb.segmentation.cli")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="SPDB v1 discourse segmentation — paragraph- and sentence-aware Spanish splitter.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input JSONL of document records (local only; must include document_id/doc_id and text_raw/text).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output discourse_unit JSONL (default: data/processed/segmented/discourse_units.jsonl).",
    )
    parser.add_argument(
        "--max-tokens-beto",
        type=int,
        default=400,
        help="Maximum BETO tokens per unit before sentence-level splitting.",
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
        help="Split label embedded in unit_id / instance_id.",
    )
    parser.add_argument(
        "--pipeline-version",
        default="0.1.0",
        help="Pipeline version stored in provenance fields.",
    )
    parser.add_argument(
        "--use-beto-model",
        action="store_true",
        help="Use Hugging Face BETO tokenizer when available (offline tests use estimate fallback).",
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
        help="Segment a single document_id/doc_id from the input file.",
    )
    return parser


def run_segmentation(args: argparse.Namespace) -> tuple[int, int]:
    config = SegmentConfig(
        max_tokens_beto=args.max_tokens_beto,
        min_chars=args.min_chars,
        max_chars=args.max_chars,
        split=args.split,
        pipeline_version=args.pipeline_version,
        use_beto_model=args.use_beto_model,
    )

    documents = list(read_jsonl(args.input))
    if args.document_id:
        documents = [
            doc
            for doc in documents
            if doc.get("document_id") == args.document_id or doc.get("doc_id") == args.document_id
        ]
        if not documents:
            raise ValueError(f"document id not found in input: {args.document_id}")

    units = list(segment_documents(documents, config))
    validation_errors: list[str] = []
    for index, unit in enumerate(units):
        field_errors = validate_discourse_unit(unit)
        for message in field_errors:
            validation_errors.append(f"unit {index}: {message}")

    if validation_errors:
        for message in validation_errors[:10]:
            logger.error(message)
        raise ValueError(f"Validation failed with {len(validation_errors)} error(s)")

    if args.dry_run:
        logger.info("Dry run: validated %d unit(s); no output written", len(units))
        return len(documents), len(units)

    output_path = args.output or default_segmented_path()
    written = write_jsonl(output_path, units)
    logger.info("Wrote %d discourse unit(s) to %s", written, output_path)
    return len(documents), written


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.log_level)

    if not args.input.exists():
        logger.error("Input not found: %s", args.input)
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
