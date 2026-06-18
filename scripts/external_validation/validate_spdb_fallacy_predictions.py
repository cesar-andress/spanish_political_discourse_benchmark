#!/usr/bin/env python3
"""Validate SPDB external fallacy LLM prediction JSONL outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from analysis.external_validation.fallacy_constants import FIXTURE_DATASET
from analysis.external_validation.fallacy_validator import validate_predictions_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate SPDB external fallacy prediction JSONL against input rows.",
    )
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--input", type=Path, default=FIXTURE_DATASET)
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--json-report", type=Path, default=None)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if not args.predictions.exists():
        print(f"Predictions file not found: {args.predictions}", file=sys.stderr)
        return 1
    if not args.input.exists():
        print(f"Input dataset not found: {args.input}", file=sys.stderr)
        return 1

    summary = validate_predictions_file(
        args.predictions,
        args.input,
        text_column=args.text_column,
        id_column=args.id_column,
    )
    payload = {
        "ok": summary.ok,
        "total_records": summary.total_records,
        "expected_rows": summary.expected_rows,
        "valid_outputs": summary.valid_outputs,
        "parse_failure_rate": summary.parse_failure_rate,
        "invalid_label_rate": summary.invalid_label_rate,
        "duplicate_row_ids": summary.duplicate_row_ids,
        "missing_row_ids": summary.missing_row_ids,
        "extra_row_ids": summary.extra_row_ids,
        "errors": summary.errors,
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Records: {summary.total_records}/{summary.expected_rows}")
    print(f"Valid outputs: {summary.valid_outputs}")
    print(f"Parse failure rate: {summary.parse_failure_rate:.3f}")
    print(f"Invalid label rate: {summary.invalid_label_rate:.3f}")
    if summary.errors:
        print("Errors:")
        for error in summary.errors[:20]:
            print(f"  - {error}")
    return 0 if summary.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
