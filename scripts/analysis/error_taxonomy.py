#!/usr/bin/env python3
"""CLI for automatic SPDB error taxonomy generation."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from analysis.error_taxonomy.constants import (
    DEFAULT_ADJUDICATED,
    DEFAULT_ANNOTATORS,
    DEFAULT_LLM_DIR,
    DEFAULT_OUTPUT,
)
from analysis.error_taxonomy.pipeline import run_error_taxonomy, run_error_taxonomy_fixtures


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate publication-ready PF error taxonomy from human disagreements and model errors.",
    )
    parser.add_argument("--fixtures", action="store_true", help="Use tests/fixtures/error_taxonomy/")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--annotator",
        action="append",
        type=Path,
        default=[],
        help="Human annotator CSV (repeatable; default: pilot annotators)",
    )
    parser.add_argument("--adjudicated", type=Path, default=DEFAULT_ADJUDICATED)
    parser.add_argument("--llm-dir", type=Path, default=DEFAULT_LLM_DIR)
    parser.add_argument(
        "--gold-strategy",
        choices=["majority_vote", "unanimous_only", "adjudicated_file"],
        default="majority_vote",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if args.fixtures:
        result = run_error_taxonomy_fixtures(output_path=args.output)
    else:
        annotators = tuple(args.annotator) if args.annotator else DEFAULT_ANNOTATORS
        result = run_error_taxonomy(
            annotator_paths=annotators,
            adjudicated_path=args.adjudicated,
            llm_dir=args.llm_dir,
            output_path=args.output,
            gold_strategy=args.gold_strategy,
        )

    if result.pending:
        print(f"Error taxonomy pending. See {result.output_path}")
        return 0

    assert result.taxonomy is not None
    top = max(result.taxonomy.clusters, key=lambda item: item.human_count + item.model_count)
    print(f"Wrote {result.output_path}")
    print(
        f"Top cluster: {top.cluster.title} "
        f"(human={top.human_count}, model={top.model_count})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
