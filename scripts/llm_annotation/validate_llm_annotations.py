#!/usr/bin/env python3
"""Validate SPDB LLM annotation JSONL outputs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Iterable

from analysis.llm_annotation.constants import DEFAULT_PILOT_INPUT
from analysis.llm_annotation.validator import validate_annotations_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate LLM annotation JSONL against pilot units.")
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--pilot-input", type=Path, default=DEFAULT_PILOT_INPUT)
    parser.add_argument("--model-name", default="")
    parser.add_argument("--json-report", type=Path, default=None)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if not args.annotations.exists():
        print(f"Annotations file not found: {args.annotations}", file=sys.stderr)
        return 1
    if not args.pilot_input.exists():
        print(f"Pilot input not found: {args.pilot_input}", file=sys.stderr)
        return 1

    summary = validate_annotations_file(
        args.annotations,
        args.pilot_input,
        model_name=args.model_name or None,
    )
    payload = {
        "ok": summary.ok,
        "total_records": summary.total_records,
        "expected_units": summary.expected_units,
        "parse_failure_rate": summary.parse_failure_rate,
        "invalid_label_rate": summary.invalid_label_rate,
        "duplicate_unit_ids": summary.duplicate_unit_ids,
        "missing_unit_ids": summary.missing_unit_ids,
        "extra_unit_ids": summary.extra_unit_ids,
        "errors": summary.errors,
    }
    if args.json_report:
        args.json_report.parent.mkdir(parents=True, exist_ok=True)
        args.json_report.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"Records: {summary.total_records}/{summary.expected_units}")
    print(f"Parse failure rate: {summary.parse_failure_rate:.3f}")
    print(f"Invalid label rate: {summary.invalid_label_rate:.3f}")
    if summary.errors:
        print("Errors:")
        for error in summary.errors[:20]:
            print(f"  - {error}")
    return 0 if summary.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
