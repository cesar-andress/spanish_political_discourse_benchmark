#!/usr/bin/env python3
"""Compute confusion matrices for pilot annotation CSV exports."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from scripts.analysis.agreement_metrics import ConfusionMatrixResult, confusion_matrix, json_safe
from scripts.analysis.pilot_annotation_io import (
    ANNOTATION_COLUMNS,
    add_pilot_input_args,
    ensure_output_dir,
    load_aligned_annotations,
    normalized_column_values,
    write_markdown,
)

SINGLE_LABEL_COLUMNS = ("pragmatic_function", "semantic_vacuity", "conceptual_anachronism")


def _write_csv(path: Path, result: ConfusionMatrixResult) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["annotator_a", *result.labels])
        for row_label in result.labels:
            writer.writerow([row_label, *[result.matrix[row_label][col_label] for col_label in result.labels]])


def render_markdown(results: Dict[str, ConfusionMatrixResult], *, aligned) -> List[str]:
    lines = [
        "# Confusion matrices — pilot 001",
        "",
        f"**Annotator A:** `{aligned.annotator_a_path}`  ",
        f"**Annotator B:** `{aligned.annotator_b_path}`  ",
        f"**Units:** {len(aligned.unit_ids)}  ",
        "",
        "Rows = annotator A; columns = annotator B.",
        "",
    ]
    for column, result in results.items():
        lines.extend(
            [
                f"## `{column}`",
                "",
                "| A \\ B | " + " | ".join(f"`{label}`" for label in result.labels) + " |",
                "|-------|" + "|".join(["---:"] * len(result.labels)) + "|",
            ]
        )
        for row_label in result.labels:
            cells = " | ".join(str(result.matrix[row_label][col_label]) for col_label in result.labels)
            lines.append(f"| `{row_label}` | {cells} |")
        diagonal = sum(result.matrix[label][label] for label in result.labels)
        lines.append("")
        lines.append(
            f"Diagonal agreement: **{diagonal}** / {result.total} "
            f"({100.0 * diagonal / result.total:.1f}%)"
        )
        lines.append("")
    return lines


def run(annotator_a: Path, annotator_b: Path, output_dir: Path) -> Dict[str, ConfusionMatrixResult]:
    aligned = load_aligned_annotations(annotator_a, annotator_b)
    ensure_output_dir(output_dir)
    results: Dict[str, ConfusionMatrixResult] = {}

    for column in (*SINGLE_LABEL_COLUMNS, "fallacy_labels"):
        values_a, values_b = normalized_column_values(aligned, column)
        result = confusion_matrix(values_a, values_b)
        results[column] = ConfusionMatrixResult(
            column=column,
            labels=result.labels,
            matrix=result.matrix,
            total=result.total,
        )
        _write_csv(output_dir / f"confusion_matrix_{column}.csv", results[column])

    payload = {
        "annotator_a": str(annotator_a),
        "annotator_b": str(annotator_b),
        "n_units": len(aligned.unit_ids),
        "matrices": {
            column: {
                "labels": result.labels,
                "matrix": result.matrix,
                "total": result.total,
            }
            for column, result in results.items()
        },
    }
    (output_dir / "confusion_matrices.json").write_text(
        json.dumps(json_safe(payload), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(output_dir / "confusion_matrices.md", render_markdown(results, aligned=aligned))
    return results


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Compute confusion matrices for pilot annotations.")
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
    print(f"Wrote confusion matrices to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
