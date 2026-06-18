#!/usr/bin/env python3
"""Generate ParlaMint corpus statistics report, CSV, and figures."""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence

DEFAULT_INPUT = Path("data/processed/parlamint_units.jsonl")
DEFAULT_MD = Path("reports/parlamint_corpus_statistics.md")
DEFAULT_CSV = Path("reports/parlamint_corpus_statistics.csv")
DEFAULT_FIGURES = Path("figures/parlamint")


def load_units(path: Path) -> List[Dict[str, Any]]:
    units: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                units.append(json.loads(line))
    return units


def _year(date_str: str) -> str:
    return date_str[:4] if date_str and len(date_str) >= 4 else "unknown"


def compute_stats(units: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    parties = Counter()
    speakers = Counter()
    years = Counter()
    char_lengths: List[int] = []
    token_lengths: List[int] = []

    for unit in units:
        meta = unit.get("metadata") or {}
        parties[meta.get("speaker_party") or "unknown"] += 1
        speakers[meta.get("speaker_name") or "unknown"] += 1
        years[_year(str(meta.get("date") or ""))] += 1
        char_lengths.append(int(unit.get("character_count") or len(unit.get("text", ""))))
        token_lengths.append(int(unit.get("token_count") or 0))

    char_mean = statistics.mean(char_lengths) if char_lengths else 0.0
    char_median = statistics.median(char_lengths) if char_lengths else 0.0
    token_mean = statistics.mean(token_lengths) if token_lengths else 0.0
    token_median = statistics.median(token_lengths) if token_lengths else 0.0

    return {
        "total_units": len(units),
        "unique_parties": len(parties),
        "unique_speakers": len(speakers),
        "unique_years": len(years),
        "years_list": sorted(y for y in years if y != "unknown"),
        "char_mean": char_mean,
        "char_median": char_median,
        "token_mean": token_mean,
        "token_median": token_median,
        "char_lengths": char_lengths,
        "token_lengths": token_lengths,
        "parties": parties,
        "speakers": speakers,
        "years": years,
        "top_parties": parties.most_common(25),
        "top_speakers": speakers.most_common(25),
    }


def write_csv(path: Path, stats: Dict[str, Any], input_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows: List[Dict[str, str]] = []

    def add(section: str, metric: str, value: Any, extra: str = "") -> None:
        rows.append(
            {
                "section": section,
                "metric": metric,
                "value": str(value),
                "rank": "",
                "extra": extra,
            }
        )

    add("summary", "source_file", input_path)
    add("summary", "generated_at_utc", datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
    add("summary", "total_units", stats["total_units"])
    add("summary", "unique_parties", stats["unique_parties"])
    add("summary", "unique_speakers", stats["unique_speakers"])
    add("summary", "unique_years", stats["unique_years"])
    add("summary", "years", ", ".join(stats["years_list"]))
    add("summary", "mean_character_count", f"{stats['char_mean']:.2f}")
    add("summary", "median_character_count", f"{stats['char_median']:.2f}")
    add("summary", "mean_token_count", f"{stats['token_mean']:.2f}")
    add("summary", "median_token_count", f"{stats['token_median']:.2f}")

    for rank, (label, count) in enumerate(stats["top_parties"], start=1):
        rows.append(
            {
                "section": "top_parties",
                "metric": label,
                "value": str(count),
                "rank": str(rank),
                "extra": f"{100.0 * count / stats['total_units']:.2f}%",
            }
        )
    for rank, (label, count) in enumerate(stats["top_speakers"], start=1):
        rows.append(
            {
                "section": "top_speakers",
                "metric": label,
                "value": str(count),
                "rank": str(rank),
                "extra": f"{100.0 * count / stats['total_units']:.2f}%",
            }
        )

    for bucket, count in _token_histogram(stats["token_lengths"]).items():
        rows.append(
            {
                "section": "token_distribution",
                "metric": bucket,
                "value": str(count),
                "rank": "",
                "extra": f"{100.0 * count / stats['total_units']:.2f}%",
            }
        )

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["section", "metric", "value", "rank", "extra"],
        )
        writer.writeheader()
        writer.writerows(rows)


def _token_histogram(tokens: Sequence[int]) -> Dict[str, int]:
    bins = [(0, 50), (51, 100), (101, 200), (201, 400), (401, 800), (801, 10_000)]
    labels = ["1-50", "51-100", "101-200", "201-400", "401-800", "801+"]
    counts = {label: 0 for label in labels}
    for value in tokens:
        placed = False
        for (lo, hi), label in zip(bins, labels):
            if lo <= value <= hi:
                counts[label] += 1
                placed = True
                break
        if not placed:
            counts["801+"] += 1
    return counts


def write_markdown(path: Path, stats: Dict[str, Any], input_path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    token_hist = _token_histogram(stats["token_lengths"])
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    lines = [
        "# ParlaMint corpus statistics (SPDB processed units)",
        "",
        f"**Source:** `{input_path}`  ",
        f"**Generated:** {generated}  ",
        "**Provenance:** ParlaMint-ES (see `docs/sources/parlamint.md`)",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Total discourse units | {stats['total_units']:,} |",
        f"| Unique parties (`speaker_party`) | {stats['unique_parties']:,} |",
        f"| Unique speakers (`speaker_name`) | {stats['unique_speakers']:,} |",
        f"| Session years | {', '.join(stats['years_list'])} |",
        f"| Mean character count | {stats['char_mean']:.1f} |",
        f"| Median character count | {stats['char_median']:.1f} |",
        f"| Mean token count (BETO estimate) | {stats['token_mean']:.1f} |",
        f"| Median token count (BETO estimate) | {stats['token_median']:.1f} |",
        "",
        "## Token distribution",
        "",
        "| Token range | Units | Share |",
        "|-------------|------:|------:|",
    ]
    for label, count in token_hist.items():
        share = 100.0 * count / stats["total_units"]
        lines.append(f"| {label} | {count:,} | {share:.1f}% |")

    lines.extend(
        [
            "",
            "## Figures",
            "",
            "| Figure | Description |",
            "|--------|-------------|",
            "| `figures/parlamint/token_distribution.png` | Histogram of token counts |",
            "| `figures/parlamint/units_by_year.png` | Units per session year |",
            "| `figures/parlamint/top_parties.png` | Top 25 parties by unit count |",
            "| `figures/parlamint/top_speakers.png` | Top 25 speakers by unit count |",
            "",
            "## Top 25 parties",
            "",
            "| Rank | Party | Units | Share |",
            "|-----:|-------|------:|------:|",
        ]
    )
    for rank, (party, count) in enumerate(stats["top_parties"], start=1):
        share = 100.0 * count / stats["total_units"]
        lines.append(f"| {rank} | {party} | {count:,} | {share:.1f}% |")

    lines.extend(
        [
            "",
            "## Top 25 speakers",
            "",
            "| Rank | Speaker | Units | Share |",
            "|-----:|---------|------:|------:|",
        ]
    )
    for rank, (speaker, count) in enumerate(stats["top_speakers"], start=1):
        share = 100.0 * count / stats["total_units"]
        lines.append(f"| {rank} | {speaker} | {count:,} | {share:.1f}% |")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(output_dir: Path, stats: Dict[str, Any]) -> List[Path]:
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []

    # Token distribution
    fig, ax = plt.subplots(figsize=(8, 5))
    token_hist = _token_histogram(stats["token_lengths"])
    labels = list(token_hist.keys())
    values = [token_hist[k] for k in labels]
    ax.bar(labels, values, color="#4C72B0")
    ax.set_title("ParlaMint units — token count distribution")
    ax.set_xlabel("Tokens (BETO estimate)")
    ax.set_ylabel("Units")
    ax.tick_params(axis="x", rotation=30)
    fig.tight_layout()
    token_path = output_dir / "token_distribution.png"
    fig.savefig(token_path, dpi=150)
    plt.close(fig)
    written.append(token_path)

    # Units by year
    fig, ax = plt.subplots(figsize=(7, 4))
    year_items = sorted(
        ((y, c) for y, c in stats["years"].items() if y != "unknown"),
        key=lambda item: item[0],
    )
    ax.bar([y for y, _ in year_items], [c for _, c in year_items], color="#55A868")
    ax.set_title("ParlaMint units — by session year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Units")
    fig.tight_layout()
    year_path = output_dir / "units_by_year.png"
    fig.savefig(year_path, dpi=150)
    plt.close(fig)
    written.append(year_path)

    def _horizontal_bar(path: Path, title: str, items: Sequence[tuple[str, int]], color: str) -> None:
        fig, ax = plt.subplots(figsize=(10, 10))
        labels = [label for label, _ in reversed(items)]
        values = [count for _, count in reversed(items)]
        ax.barh(labels, values, color=color)
        ax.set_title(title)
        ax.set_xlabel("Units")
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)

    _horizontal_bar(
        output_dir / "top_parties.png",
        "Top 25 parties by unit count",
        stats["top_parties"],
        "#C44E52",
    )
    _horizontal_bar(
        output_dir / "top_speakers.png",
        "Top 25 speakers by unit count",
        stats["top_speakers"],
        "#8172B3",
    )

    return written


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ParlaMint corpus statistics report.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--no-figures", action="store_true")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    units = load_units(args.input)
    stats = compute_stats(units)
    write_markdown(args.markdown, stats, args.input)
    write_csv(args.csv, stats, args.input)
    if not args.no_figures:
        write_figures(args.figures_dir, stats)

    print(f"Wrote {args.markdown}")
    print(f"Wrote {args.csv}")
    if not args.no_figures:
        print(f"Wrote figures under {args.figures_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
