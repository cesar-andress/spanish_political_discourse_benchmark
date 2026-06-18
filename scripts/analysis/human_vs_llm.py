#!/usr/bin/env python3
"""CLI entry point for Human-vs-LLM comparison."""

from __future__ import annotations

import argparse
from pathlib import Path

from analysis.human_vs_llm.constants import (
    DEFAULT_ADJUDICATED,
    DEFAULT_ANNOTATORS,
    DEFAULT_LLM_DIR,
    DEFAULT_OUTPUT_DIR,
    FIXTURE_ADJUDICATED,
    FIXTURE_ANNOTATORS,
    FIXTURE_LLM,
    GoldStrategy,
)
from analysis.human_vs_llm.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare human gold annotations against LLM outputs for SPDB pilot units.",
    )
    parser.add_argument(
        "--fixtures",
        action="store_true",
        help="Use synthetic fixtures under tests/fixtures/human_vs_llm/",
    )
    parser.add_argument(
        "--annotator",
        action="append",
        type=Path,
        default=[],
        help="Human annotator CSV (repeat for each annotator)",
    )
    parser.add_argument(
        "--adjudicated",
        type=Path,
        default=DEFAULT_ADJUDICATED,
        help="Optional adjudicated gold CSV",
    )
    parser.add_argument(
        "--llm",
        action="append",
        type=Path,
        default=[],
        help="LLM annotation JSONL (repeat for each model)",
    )
    parser.add_argument(
        "--llm-dir",
        type=Path,
        default=DEFAULT_LLM_DIR,
        help="Directory with {MODEL}_pilot_100.jsonl files",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory for comparison reports",
    )
    parser.add_argument(
        "--gold-strategy",
        choices=("majority_vote", "unanimous_only", "adjudicated_file"),
        default="majority_vote",
        help="Strategy for constructing gold labels from human annotations",
    )
    return parser


def resolve_paths(args: argparse.Namespace) -> tuple[tuple[Path, ...], Path, list[Path] | None]:
    if args.fixtures:
        annotators = FIXTURE_ANNOTATORS
        adjudicated = FIXTURE_ADJUDICATED
        llm_paths = [FIXTURE_LLM]
        return annotators, adjudicated, llm_paths

    annotators = tuple(args.annotator) if args.annotator else DEFAULT_ANNOTATORS
    llm_paths = list(args.llm) if args.llm else None
    return annotators, args.adjudicated, llm_paths


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    annotators, adjudicated, llm_paths = resolve_paths(args)

    result = run_pipeline(
        annotator_paths=annotators,
        adjudicated_path=adjudicated,
        llm_dir=args.llm_dir,
        output_dir=args.output_dir,
        gold_strategy=args.gold_strategy,  # type: ignore[arg-type]
        llm_paths=llm_paths,
    )
    if result.pending:
        print(f"Human annotations pending. See {result.output_dir / 'README_PENDING.md'}")
        return 0

    print(f"Human-vs-LLM report written to {result.output_dir}")
    for system in result.system_results:
        print(
            f"- {system.system_name}: accuracy={system.scores.accuracy:.4f}, "
            f"macro_f1={system.scores.macro_f1:.4f}, gap={system.ceiling_gap:.4f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
