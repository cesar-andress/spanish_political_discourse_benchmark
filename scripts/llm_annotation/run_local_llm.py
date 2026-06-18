#!/usr/bin/env python3
"""Run local command-based LLM annotation for the SPDB pilot."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from analysis.llm_annotation.constants import (
    DEFAULT_ANNOTATION_REPORT,
    DEFAULT_DRY_RUN_REPORT,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PILOT_INPUT,
)
from analysis.llm_annotation.pipeline import run_dry_run, run_local_annotation


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SPDB local LLM annotation pipeline.")
    parser.add_argument("--pilot-input", type=Path, default=DEFAULT_PILOT_INPUT)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_ANNOTATION_REPORT)
    parser.add_argument("--dry-run-report", type=Path, default=DEFAULT_DRY_RUN_REPORT)
    parser.add_argument("--model-name", default="local-model")
    parser.add_argument("--backend-command", default="")
    parser.add_argument("--prompt-mode", choices=("zero_shot", "few_shot"), default="zero_shot")
    parser.add_argument("--dry-run", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)

    if args.dry_run:
        result = run_dry_run(
            pilot_path=args.pilot_input,
            report_path=args.dry_run_report,
            model_name=args.model_name,
            mode=args.prompt_mode,
        )
        print(f"Dry run complete: {len(result.records)} mock annotations validated")
        print(f"Wrote {args.dry_run_report}")
        return 0 if result.validation.ok else 1

    if not args.backend_command:
        print("--backend-command is required for real runs (or use --dry-run).", file=sys.stderr)
        return 1

    result = run_local_annotation(
        pilot_path=args.pilot_input,
        model_name=args.model_name,
        backend_command=args.backend_command,
        output_dir=args.output_dir,
        report_path=args.report,
        mode=args.prompt_mode,
    )
    print(f"Wrote annotations to {result.output_path}")
    print(f"Wrote report to {args.report}")
    return 0 if result.validation.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
