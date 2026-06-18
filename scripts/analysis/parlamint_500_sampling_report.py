#!/usr/bin/env python3
"""Sample 500 ParlaMint units (stratified) and write a sampling report."""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

from scripts.analysis.parlamint_corpus_statistics import load_units
from scripts.ingestion.common import setup_logging, write_jsonl
from scripts.sampling.stratified_sample import StratifiedSampleResult, stratified_sample_units

DEFAULT_INPUT = Path("data/processed/parlamint_units.jsonl")
DEFAULT_OUTPUT = Path("data/processed/parlamint_500_units.jsonl")
DEFAULT_REPORT = Path("reports/parlamint_500_sampling_report.md")
DEFAULT_N = 500
DEFAULT_SEED = 42
DEFAULT_MAX_PER_SPEAKER = 5


def _pct(count: int, total: int) -> str:
    if total <= 0:
        return "0.0"
    return f"{100.0 * count / total:.1f}"


def _counter_table(counter: Counter[str], total: int, *, limit: int | None = None) -> list[str]:
    lines = ["| Label | Units | Share |", "|-------|------:|------:|"]
    items = counter.most_common(limit)
    for label, count in items:
        lines.append(f"| {label} | {count} | {_pct(count, total)}% |")
    return lines


def render_report(result: StratifiedSampleResult, *, input_path: Path, output_path: Path) -> str:
    selected = result.units
    n = len(selected)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    max_speaker = max(result.speaker_selected.values()) if result.speaker_selected else 0
    speakers_at_cap = sum(
        1 for count in result.speaker_selected.values() if count >= result.max_per_speaker
    )
    pool_units = load_units(input_path)
    pool_parties: Counter[str] = Counter()
    pool_years: Counter[str] = Counter()
    pool_counter: Counter[tuple[str, str]] = Counter()
    for unit in pool_units:
        meta = unit.get("metadata") or {}
        party = str(meta.get("speaker_party") or "unknown")
        year = str(meta.get("date") or "")[:4] or "unknown"
        pool_parties[party] += 1
        pool_years[year] += 1
        pool_counter[(party, year)] += 1
    speaker_ceiling = sum(
        min(result.max_per_speaker, count)
        for count in Counter(
            str((u.get("metadata") or {}).get("speaker_name") or "unknown") for u in pool_units
        ).values()
    )

    lines = [
        "# ParlaMint 500-unit benchmark candidate sample",
        "",
        f"**Input pool:** `{input_path}` ({result.pool_total} units)  ",
        f"**Output sample:** `{output_path}` ({n} units)  ",
        f"**Generated:** {generated}  ",
        f"**Seed:** `{result.seed}` (deterministic)  ",
        "",
        "## Sampling constraints",
        "",
        "| Constraint | Setting |",
        "|------------|---------|",
        f"| Target size (`n`) | {result.requested_n} |",
        f"| Stratification | `speaker_party` × session year |",
        f"| Quota allocation | Proportional (largest remainder) |",
        f"| Speaker selection | Round-robin within stratum |",
        f"| Max units per speaker | {result.max_per_speaker} (global, before reuse) |",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Selected units | {n} |",
        f"| Unique parties | {len(result.party_selected)} |",
        f"| Unique speakers | {len(result.speaker_selected)} |",
        f"| Session years | {', '.join(sorted(result.year_selected))} |",
        f"| Max units from one speaker | {max_speaker} |",
        f"| Speakers at cap ({result.max_per_speaker}) | {speakers_at_cap} |",
        f"| Speaker-cap ceiling (current pool) | {speaker_ceiling} |",
        "",
    ]

    if result.shortfall_reason:
        lines.extend(
            [
                "> **Shortfall:** "
                + result.shortfall_reason
                + " With the current six-session ParlaMint pool (878 units, 99 speakers),"
                + f" at most **{speaker_ceiling}** units can be selected before any speaker contributes"
                + f" a sixth unit. Ingest additional sessions to approach the n={result.requested_n} target.",
                "",
            ]
        )

    lines.extend(
        [
            "## Pool vs sample (year)",
            "",
            "| Year | Pool units | Pool share | Sample units | Sample share |",
            "|------|----------:|-----------:|-------------:|-------------:|",
        ]
    )
    for year in sorted(set(pool_years) | set(result.year_selected)):
        pool_count = pool_years.get(year, 0)
        sample_count = result.year_selected.get(year, 0)
        lines.append(
            f"| {year} | {pool_count} | {_pct(pool_count, len(pool_units))}% | "
            f"{sample_count} | {_pct(sample_count, n)}% |"
        )

    lines.extend(["", "## Party × year quotas", "", "| Party | Year | Pool | Quota | Selected |", "|-------|------|-----:|------:|---------:|"])
    stratum_keys = sorted(set(result.stratum_quotas) | set(result.stratum_selected))
    for party, year in stratum_keys:
        pool = pool_counter.get((party, year), 0)
        quota = result.stratum_quotas.get((party, year), 0)
        selected_count = result.stratum_selected.get((party, year), 0)
        lines.append(f"| {party} | {year} | {pool} | {quota} | {selected_count} |")

    lines.extend(["", "## Marginal distribution by party", ""])
    lines.extend(_counter_table(result.party_selected, n))
    lines.extend(["", "## Marginal distribution by year", ""])
    lines.extend(_counter_table(result.year_selected, n))
    lines.extend(["", "## Top 25 speakers in sample", ""])
    lines.extend(_counter_table(result.speaker_selected, n, limit=25))
    lines.extend(
        [
            "",
            "## Reproduction",
            "",
            "```bash",
            "make segment-parlamint   # if pool missing",
            "make parlamint-500",
            "```",
            "",
        ]
    )
    return "\n".join(lines)


def run(
    *,
    input_path: Path,
    output_path: Path,
    report_path: Path,
    n: int,
    seed: int,
    max_per_speaker: int,
) -> StratifiedSampleResult:
    units = load_units(input_path)
    result = stratified_sample_units(
        units,
        n=n,
        seed=seed,
        max_per_speaker=max_per_speaker,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(output_path, result.units)
    report_path.write_text(
        render_report(result, input_path=input_path, output_path=output_path),
        encoding="utf-8",
    )
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Sample stratified ParlaMint benchmark candidate.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--n", type=int, default=DEFAULT_N)
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--max-per-speaker", type=int, default=DEFAULT_MAX_PER_SPEAKER)
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    setup_logging(args.log_level)

    if not args.input.exists():
        print(f"Input not found: {args.input}", file=sys.stderr)
        return 1

    result = run(
        input_path=args.input,
        output_path=args.output,
        report_path=args.report,
        n=args.n,
        seed=args.seed,
        max_per_speaker=args.max_per_speaker,
    )
    print(f"Wrote {len(result.units)} unit(s) to {args.output}")
    print(f"Wrote report to {args.report}")
    if result.shortfall_reason:
        print(result.shortfall_reason, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
