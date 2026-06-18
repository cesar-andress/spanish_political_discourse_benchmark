#!/usr/bin/env python3
"""Compute Krippendorff's alpha for two pilot annotation CSV exports."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from scripts.analysis.agreement_metrics import (
    KrippendorffAlphaResult,
    binary_cohen_kappa,
    fallacy_label_universe,
    json_safe,
    krippendorff_alpha_nominal,
)
from scripts.analysis.pilot_annotation_io import (
    ANNOTATION_COLUMNS,
    add_pilot_input_args,
    ensure_output_dir,
    load_aligned_annotations,
    normalized_column_values,
    parse_fallacy_set,
    write_markdown,
)


def _format_float(value: float) -> str:
    if value != value:
        return "n/a"
    return f"{value:.4f}"


def _compute_for_column(aligned, column: str) -> KrippendorffAlphaResult:
    values_a, values_b = normalized_column_values(aligned, column)
    result = krippendorff_alpha_nominal(values_a, values_b)
    per_label = dict(result.per_label)

    if column == "fallacy_labels":
        universe = fallacy_label_universe(values_a, values_b)
        for label in universe:
            presence_a = [label in parse_fallacy_set(value) for value in values_a]
            presence_b = [label in parse_fallacy_set(value) for value in values_b]
            both = sum(1 for left, right in zip(presence_a, presence_b) if left and right)
            either = sum(1 for left, right in zip(presence_a, presence_b) if left or right)
            per_label[label] = {
                "support_a": sum(presence_a),
                "support_b": sum(presence_b),
                "agree_both": both,
                "agree_rate": both / either if either else float("nan"),
                "binary_kappa": binary_cohen_kappa(presence_a, presence_b),
            }

    return KrippendorffAlphaResult(
        column=column,
        n_units=result.n_units,
        n_values=result.n_values,
        alpha=result.alpha,
        per_label=per_label,
    )


def render_markdown(results: Dict[str, KrippendorffAlphaResult], *, aligned) -> List[str]:
    lines = [
        "# Krippendorff's alpha — pilot 001",
        "",
        f"**Annotator A:** `{aligned.annotator_a_path}`  ",
        f"**Annotator B:** `{aligned.annotator_b_path}`  ",
        f"**Units:** {len(aligned.unit_ids)}  ",
        "",
        "Nominal α with two coders (no missing values).",
        "",
        "## Overall alpha",
        "",
        "| Dimension | Units | Codings | Krippendorff's α |",
        "|-----------|------:|--------:|-----------------:|",
    ]
    for column in ANNOTATION_COLUMNS:
        result = results[column]
        lines.append(
            f"| `{column}` | {result.n_units} | {result.n_values} | **{_format_float(result.alpha)}** |"
        )

    for column in ANNOTATION_COLUMNS:
        result = results[column]
        lines.extend(
            [
                "",
                f"## Per-label agreement — `{column}`",
                "",
                "| Label | Support A | Support B | Agree both | Agree rate |",
                "|-------|----------:|----------:|-----------:|-----------:|",
            ]
        )
        for label, stats in sorted(result.per_label.items()):
            lines.append(
                f"| `{label}` | {int(stats['support_a'])} | {int(stats['support_b'])} | "
                f"{int(stats['agree_both'])} | {_format_float(float(stats['agree_rate']))} |"
            )
    return lines


def run(annotator_a: Path, annotator_b: Path, output_dir: Path) -> Dict[str, KrippendorffAlphaResult]:
    aligned = load_aligned_annotations(annotator_a, annotator_b)
    ensure_output_dir(output_dir)
    results = {column: _compute_for_column(aligned, column) for column in ANNOTATION_COLUMNS}

    payload = {
        "annotator_a": str(annotator_a),
        "annotator_b": str(annotator_b),
        "n_units": len(aligned.unit_ids),
        "dimensions": {
            column: {
                "alpha": result.alpha,
                "n_units": result.n_units,
                "n_values": result.n_values,
                "per_label": result.per_label,
            }
            for column, result in results.items()
        },
    }
    (output_dir / "krippendorff_alpha.json").write_text(
        json.dumps(json_safe(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(output_dir / "krippendorff_alpha.md", render_markdown(results, aligned=aligned))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute Krippendorff's alpha for pilot annotations.")
    add_pilot_input_args(parser)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if not args.annotator_a.exists():
        print(f"Annotator A file not found: {args.annotator_a}", file=sys.stderr)
        return 1
    if not args.annotator_b.exists():
        print(f"Annotator B file not found: {args.annotator_b}", file=sys.stderr)
        return 1
    try:
        run(args.annotator_a, args.annotator_b, args.output_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote Krippendorff's alpha report to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
