#!/usr/bin/env python3
"""Compare multiple local LLM annotation JSONL files."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from analysis.llm_annotation.constants import DEFAULT_OUTPUT_DIR, DEFAULT_REPORT_DIR
from analysis.llm_annotation.model_agreement import run_model_comparison


FIXTURE_ANNOTATIONS = Path("tests/fixtures/llm_annotation/model_compare")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compare SPDB LLM model annotations.")
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Use synthetic model JSONL fixtures for comparison.",
    )
    parser.add_argument(
        "--annotations-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory containing {model}_pilot_100.jsonl files",
    )
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument(
        "--jsonl",
        action="append",
        type=Path,
        default=[],
        help="Explicit model JSONL path (repeatable)",
    )
    return parser


def resolve_jsonl_paths(args: argparse.Namespace) -> list[Path]:
    if args.jsonl:
        return list(args.jsonl)
    if args.fixtures:
        return sorted(FIXTURE_ANNOTATIONS.glob("*_pilot_100.jsonl"))
    return []


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    jsonl_paths = resolve_jsonl_paths(args)
    outputs = run_model_comparison(
        jsonl_paths=jsonl_paths or None,
        annotations_dir=args.annotations_dir,
        report_dir=args.report_dir,
    )
    print(f"Wrote comparison report to {outputs.report_path}")
    print(f"Models compared: {', '.join(outputs.summary.matrix.model_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
