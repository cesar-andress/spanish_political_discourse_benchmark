#!/usr/bin/env python3
"""Sample discourse units from a processed JSONL file."""

from __future__ import annotations

import argparse
import logging
import random
import sys
from pathlib import Path
from typing import Optional, Sequence

from scripts.ingestion.common import read_jsonl, setup_logging, write_jsonl

logger = logging.getLogger("spdb.sampling")


def sample_units(
    input_path: Path,
    output_path: Path,
    *,
    n: int,
    seed: int,
) -> int:
    units = list(read_jsonl(input_path))
    if not units:
        raise ValueError(f"No units found in {input_path}")

    sample_size = min(n, len(units))
    if sample_size < n:
        logger.warning(
            "Requested n=%d but input contains only %d unit(s); writing all available units",
            n,
            len(units),
        )

    rng = random.Random(seed)
    selected = rng.sample(units, sample_size)
    return write_jsonl(output_path, selected)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample N discourse units from JSONL.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--n", type=int, required=True)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(args.log_level)

    if not args.input.exists():
        logger.error("Input not found: %s", args.input)
        return 1

    try:
        written = sample_units(args.input, args.output, n=args.n, seed=args.seed)
    except ValueError as exc:
        logger.error("%s", exc)
        return 1

    logger.info("Wrote %d sampled unit(s) to %s", written, args.output)
    return 0


if __name__ == "__main__":
    sys.exit(main())
