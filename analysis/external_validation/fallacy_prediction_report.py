"""Markdown and CSV reports for external fallacy LLM batch runs."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from analysis.external_validation.fallacy_io import dataset_name_from_path, load_external_dataset
from analysis.external_validation.fallacy_validator import (
    FallacyValidationSummary,
    load_predictions_jsonl,
    validate_predictions_file,
)


@dataclass(frozen=True)
class FallacyReportPaths:
    markdown: Path
    label_distribution: Path
    parse_errors: Path


def _confidence_average(records: Sequence[dict]) -> float:
    values = [
        float(record["confidence"])
        for record in records
        if not record.get("_parse_error") and isinstance(record.get("confidence"), (int, float))
    ]
    return sum(values) / len(values) if values else 0.0


def _none_rate(records: Sequence[dict]) -> float:
    valid = [record for record in records if not record.get("_parse_error")]
    if not valid:
        return 0.0
    none_count = sum(1 for record in valid if record.get("fallacy_none_explicit"))
    return none_count / len(valid)


def write_fallacy_prediction_report(
    *,
    predictions_path: Path,
    input_path: Path,
    model_name: str,
    text_column: str = "text",
    id_column: str = "id",
    report_path: Path,
    label_distribution_path: Path,
    parse_errors_path: Path,
) -> FallacyReportPaths:
    validation = validate_predictions_file(
        predictions_path,
        input_path,
        text_column=text_column,
        id_column=id_column,
    )
    records = load_predictions_jsonl(predictions_path)
    dataset_name = dataset_name_from_path(input_path)
    expected_rows = len(load_external_dataset(input_path, text_column=text_column, id_column=id_column))

    fal_counts: Counter[str] = Counter()
    for record in records:
        if record.get("_parse_error"):
            continue
        for label in record.get("fallacy_labels", []) or []:
            fal_counts[str(label)] += 1

    report_path.parent.mkdir(parents=True, exist_ok=True)
    label_distribution_path.parent.mkdir(parents=True, exist_ok=True)
    parse_errors_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# SPDB external fallacy LLM batch report",
        "",
        f"**Model:** `{model_name}`  ",
        f"**Dataset:** `{dataset_name}`  ",
        f"**Input rows:** {expected_rows}  ",
        f"**Output records:** {validation.total_records}  ",
        f"**Validation status:** {'OK' if validation.ok else 'ISSUES DETECTED'}",
        "",
        "## Quality metrics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Valid outputs | {validation.valid_outputs} |",
        f"| Parse failure rate | {validation.parse_failure_rate:.3f} |",
        f"| Invalid label rate | {validation.invalid_label_rate:.3f} |",
        f"| FAL_NONE rate (explicit none) | {_none_rate(records):.3f} |",
        f"| Average confidence | {_confidence_average(records):.3f} |",
        f"| Duplicate row_id | {validation.duplicate_row_ids} |",
        f"| Missing row_id | {len(validation.missing_row_ids)} |",
        "",
        "## FAL label distribution",
        "",
        "| Label | Count | Share |",
        "|-------|------:|------:|",
    ]
    total_labels = sum(fal_counts.values()) or 1
    for label, count in fal_counts.most_common():
        lines.append(f"| `{label}` | {count} | {100.0 * count / total_labels:.1f}% |")
    if not fal_counts:
        lines.append("| _none_ | 0 | 0.0% |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "This report summarizes JSON outputs from the SPDB external fallacy batch pipeline. "
            "It does **not** constitute external validation against gold labels.",
            "",
        ]
    )
    if validation.errors:
        lines.extend(["## Validation errors", ""])
        for error in validation.errors[:30]:
            lines.append(f"- {error}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    with label_distribution_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["label", "count", "share"])
        for label, count in fal_counts.most_common():
            writer.writerow([label, count, f"{100.0 * count / total_labels:.4f}"])

    with parse_errors_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["row_id", "error", "raw_response_prefix"])
        for record in records:
            if not record.get("_parse_error"):
                continue
            writer.writerow(
                [
                    record.get("row_id", ""),
                    record.get("_parse_error", ""),
                    record.get("_raw_response", ""),
                ]
            )

    return FallacyReportPaths(
        markdown=report_path,
        label_distribution=label_distribution_path,
        parse_errors=parse_errors_path,
    )


def main(argv: Sequence[str] | None = None) -> int:
    import argparse

    from analysis.external_validation.fallacy_constants import (
        DEFAULT_FALLACY_REPORT,
        DEFAULT_LABEL_DISTRIBUTION,
        DEFAULT_PARSE_ERRORS,
    )

    parser = argparse.ArgumentParser(description="Generate SPDB external fallacy LLM batch report.")
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--model-name", required=True)
    parser.add_argument("--text-column", default="text")
    parser.add_argument("--id-column", default="id")
    parser.add_argument("--report", type=Path, default=DEFAULT_FALLACY_REPORT)
    parser.add_argument("--label-distribution", type=Path, default=DEFAULT_LABEL_DISTRIBUTION)
    parser.add_argument("--parse-errors", type=Path, default=DEFAULT_PARSE_ERRORS)
    args = parser.parse_args(list(argv) if argv is not None else None)

    paths = write_fallacy_prediction_report(
        predictions_path=args.predictions,
        input_path=args.input,
        model_name=args.model_name,
        text_column=args.text_column,
        id_column=args.id_column,
        report_path=args.report,
        label_distribution_path=args.label_distribution,
        parse_errors_path=args.parse_errors,
    )
    print(f"Wrote {paths.markdown}")
    print(f"Wrote {paths.label_distribution}")
    print(f"Wrote {paths.parse_errors}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
