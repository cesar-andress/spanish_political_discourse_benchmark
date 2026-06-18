#!/usr/bin/env python3
"""Run SPDB-aligned fallacy LLM batch annotation on external datasets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from analysis.external_validation.fallacy_batch import run_fallacy_batch_command, run_fallacy_dry_run
from analysis.external_validation.fallacy_constants import (
    DEFAULT_OUTPUT_DIR,
    FALLACY_SPDB_ZERO_SHOT,
    FIXTURE_DATASET,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run SPDB external fallacy LLM batch annotation.",
    )
    parser.add_argument("--input", type=Path, default=FIXTURE_DATASET)
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--prompt", type=Path, default=FALLACY_SPDB_ZERO_SHOT)
    parser.add_argument("--model-name", default="mock-local")
    parser.add_argument("--backend-command", default="")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR / "fallacy_batch.jsonl")
    parser.add_argument("--dry-run", action="store_true", help="Use deterministic mock outputs (no backend).")
    parser.add_argument("--timeout-seconds", type=int, default=180)
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N input rows.")
    parser.add_argument("--progress-every", type=int, default=50)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if args.dry_run:
        result = run_fallacy_dry_run(
            input_path=args.input,
            text_column=args.text_column,
            prompt_path=args.prompt,
            model_name=args.model_name,
            output_path=args.output,
            id_column=args.id_column,
        )
    else:
        if not args.backend_command:
            print("--backend-command is required for real runs (or use --dry-run).", file=sys.stderr)
            return 1
        result = run_fallacy_batch_command(
            input_path=args.input,
            text_column=args.text_column,
            prompt_path=args.prompt,
            model_name=args.model_name,
            backend_command=args.backend_command,
            output_path=args.output,
            id_column=args.id_column,
            timeout_seconds=args.timeout_seconds,
            limit=args.limit,
            progress_every=args.progress_every,
        )

    validation = result.validation
    print(f"Wrote predictions to {result.output_path}")
    print(f"Records: {validation.total_records}/{validation.expected_rows}")
    print(f"Valid outputs: {validation.valid_outputs}")
    print(f"Parse failure rate: {validation.parse_failure_rate:.3f}")
    return 0 if validation.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
