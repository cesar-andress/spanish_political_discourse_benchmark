#!/usr/bin/env python3
"""Generate disagreement report for two pilot annotation CSV exports."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path
from typing import Dict, List, Sequence

from scripts.analysis.pilot_annotation_io import (
    ANNOTATION_COLUMNS,
    add_pilot_input_args,
    ensure_output_dir,
    load_aligned_annotations,
    normalized_column_values,
    write_markdown,
)


def _disagreement_type(changed_columns: List[str]) -> str:
    if len(changed_columns) > 1:
        return "multi"
    return changed_columns[0]


def collect_disagreements(aligned) -> List[Dict[str, str]]:
    fallacy_a, fallacy_b = normalized_column_values(aligned, "fallacy_labels")
    rows: List[Dict[str, str]] = []
    for index, unit_id in enumerate(aligned.unit_ids):
        changed: List[str] = []
        row: Dict[str, str] = {
            "unit_id": unit_id,
            "speaker_name": aligned.metadata[unit_id].get("speaker_name", ""),
            "speaker_party": aligned.metadata[unit_id].get("speaker_party", ""),
            "date": aligned.metadata[unit_id].get("date", ""),
        }
        for column in ANNOTATION_COLUMNS:
            value_a = aligned.labels_a[unit_id][column]
            value_b = aligned.labels_b[unit_id][column]
            row[f"{column}_a"] = value_a
            row[f"{column}_b"] = value_b
            if column == "fallacy_labels":
                if fallacy_a[index] != fallacy_b[index]:
                    changed.append(column)
            elif value_a != value_b:
                changed.append(column)
        if changed:
            row["disagreement_type"] = _disagreement_type(changed)
            row["changed_columns"] = "|".join(changed)
            rows.append(row)
    return rows


def render_markdown(rows: List[Dict[str, str]], *, aligned) -> List[str]:
    total = len(aligned.unit_ids)
    lines = [
        "# Disagreement report — pilot 001",
        "",
        f"**Annotator A:** `{aligned.annotator_a_path}`  ",
        f"**Annotator B:** `{aligned.annotator_b_path}`  ",
        f"**Units compared:** {total}  ",
        f"**Units with any disagreement:** {len(rows)} ({100.0 * len(rows) / total:.1f}%)  ",
        "",
    ]

    by_type: Dict[str, int] = {}
    for row in rows:
        by_type[row["disagreement_type"]] = by_type.get(row["disagreement_type"], 0) + 1
    lines.extend(["## Disagreement counts by type", "", "| Type | Units |", "|------|------:|"])
    for disagreement_type, count in sorted(by_type.items()):
        lines.append(f"| `{disagreement_type}` | {count} |")

    lines.extend(["", "## Unit-level disagreements", ""])
    if not rows:
        lines.append("_No disagreements found._")
        return lines

    for row in rows:
        lines.append(f"### `{row['unit_id']}` ({row['disagreement_type']})")
        lines.append("")
        lines.append(
            f"- **Speaker:** {row['speaker_name']} ({row['speaker_party']}, {row['date']})"
        )
        lines.append(f"- **Changed columns:** `{row['changed_columns']}`")
        for column in ANNOTATION_COLUMNS:
            if column in row["changed_columns"].split("|"):
                lines.append(
                    f"- **`{column}`:** A=`{row[f'{column}_a']}` · B=`{row[f'{column}_b']}`"
                )
        lines.append("")
    return lines


def run(annotator_a: Path, annotator_b: Path, output_dir: Path) -> List[Dict[str, str]]:
    aligned = load_aligned_annotations(annotator_a, annotator_b)
    ensure_output_dir(output_dir)
    rows = collect_disagreements(aligned)

    csv_path = output_dir / "disagreement_report.csv"
    fieldnames = [
        "unit_id",
        "speaker_name",
        "speaker_party",
        "date",
        "disagreement_type",
        "changed_columns",
        *[f"{column}_a" for column in ANNOTATION_COLUMNS],
        *[f"{column}_b" for column in ANNOTATION_COLUMNS],
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    summary = {
        "annotator_a": str(annotator_a),
        "annotator_b": str(annotator_b),
        "n_units": len(aligned.unit_ids),
        "n_disagreements": len(rows),
        "disagreement_rate": len(rows) / len(aligned.unit_ids) if aligned.unit_ids else 0.0,
        "by_type": {},
    }
    for row in rows:
        summary["by_type"][row["disagreement_type"]] = (
            summary["by_type"].get(row["disagreement_type"], 0) + 1
        )
    (output_dir / "disagreement_report.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    write_markdown(output_dir / "disagreement_report.md", render_markdown(rows, aligned=aligned))
    return rows


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate pilot annotation disagreement report.")
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
        rows = run(args.annotator_a, args.annotator_b, args.output_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"Wrote disagreement report ({len(rows)} unit(s)) to {args.output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
