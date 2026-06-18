"""Agreement analysis for multi-annotator pilot studies."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from analysis.pilot.constants import ANNOTATION_COLUMNS, SINGLE_LABEL_COLUMNS
from analysis.pilot.io import AnnotationStatus, PilotDataset, normalized_column_matrix, usable_units_for_column
from analysis.pilot.metrics import (
    PairwiseAgreement,
    fleiss_kappa,
    multi_rater_krippendorff_alpha,
    pairwise_cohen_matrix,
    per_class_agreement,
)
from scripts.analysis.agreement_metrics import cohen_kappa, json_safe


@dataclass(frozen=True)
class AgreementAnalysisResult:
    status: AnnotationStatus
    by_column: Dict[str, Dict[str, Any]]
    pairwise: List[PairwiseAgreement]
    markdown_tables: Dict[str, List[str]]


def _format_float(value: float) -> str:
    if value != value:
        return "n/a"
    return f"{value:.4f}"


def _subset_matrix(
    dataset: PilotDataset,
    column: str,
    unit_ids: List[str],
) -> List[List[str]]:
    matrix = normalized_column_matrix(dataset, column)
    indices = [dataset.unit_ids.index(unit_id) for unit_id in unit_ids]
    return [[row[index] for index in indices] for row in matrix]


def run_agreement_analysis(dataset: PilotDataset) -> AgreementAnalysisResult:
    by_column: Dict[str, Dict[str, Any]] = {}
    pairwise: List[PairwiseAgreement] = []
    markdown_tables: Dict[str, List[str]] = {}

    if dataset.status is AnnotationStatus.PENDING:
        return AgreementAnalysisResult(
            status=dataset.status,
            by_column={},
            pairwise=[],
            markdown_tables={
                "summary": [
                    "_Agreement metrics pending: no filled annotation labels were found._",
                ]
            },
        )

    summary_lines = [
        "| Dimension | Units | Fleiss κ | Krippendorff α | Mean pairwise κ |",
        "|-----------|------:|---------:|---------------:|----------------:|",
    ]

    for column in ANNOTATION_COLUMNS:
        unit_ids = usable_units_for_column(dataset, column)
        if len(unit_ids) < 2 or dataset.n_annotators < 2:
            by_column[column] = {"status": "insufficient_data", "units": len(unit_ids)}
            continue

        matrix = _subset_matrix(dataset, column, unit_ids)
        unit_ratings = [
            [matrix[rater_index][unit_index] for rater_index in range(dataset.n_annotators)]
            for unit_index in range(len(unit_ids))
        ]

        fleiss = fleiss_kappa(unit_ratings)
        alpha = multi_rater_krippendorff_alpha(matrix, column=column)
        pair_matrix, _ = pairwise_cohen_matrix(matrix, dataset.annotator_names, column=column)
        pair_entries: List[PairwiseAgreement] = []
        for i in range(dataset.n_annotators):
            for j in range(i + 1, dataset.n_annotators):
                result = cohen_kappa(matrix[i], matrix[j])
                entry = PairwiseAgreement(
                    annotator_a=dataset.annotator_names[i],
                    annotator_b=dataset.annotator_names[j],
                    column=column,
                    kappa=result.kappa,
                    observed_agreement=result.observed_agreement,
                )
                pair_entries.append(entry)
                pairwise.append(entry)

        mean_pairwise = (
            sum(entry.kappa for entry in pair_entries if entry.kappa == entry.kappa) / len(pair_entries)
            if pair_entries
            else float("nan")
        )
        per_class = per_class_agreement(matrix)

        by_column[column] = {
            "units": len(unit_ids),
            "fleiss_kappa": fleiss.kappa,
            "krippendorff_alpha": alpha.alpha,
            "mean_pairwise_kappa": mean_pairwise,
            "pairwise_matrix": pair_matrix,
            "per_class_agreement": per_class,
            "fleiss_per_label": fleiss.per_label,
        }

        summary_lines.append(
            f"| `{column}` | {len(unit_ids)} | {_format_float(fleiss.kappa)} | "
            f"{_format_float(alpha.alpha)} | {_format_float(mean_pairwise)} |"
        )

        per_class_lines = [
            "",
            f"### Per-class agreement — `{column}`",
            "",
            "| Label | Units with label | Unanimous units | Unanimous rate |",
            "|-------|-----------------:|----------------:|---------------:|",
        ]
        for label, stats in sorted(per_class.items()):
            per_class_lines.append(
                f"| `{label}` | {int(stats['units_with_label'])} | {int(stats['units_unanimous'])} | "
                f"{_format_float(float(stats['unanimous_rate']))} |"
            )
        markdown_tables[f"per_class_{column}"] = per_class_lines

    markdown_tables["summary"] = summary_lines
    return AgreementAnalysisResult(
        status=dataset.status,
        by_column=by_column,
        pairwise=pairwise,
        markdown_tables=markdown_tables,
    )


def write_agreement_outputs(result: AgreementAnalysisResult, output_dir: Path, dataset: PilotDataset) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": result.status.value,
        "annotators": list(dataset.annotator_names),
        "n_units": dataset.n_units,
        "dimensions": json_safe(result.by_column),
        "pairwise": [
            {
                "annotator_a": item.annotator_a,
                "annotator_b": item.annotator_b,
                "column": item.column,
                "kappa": item.kappa,
                "observed_agreement": item.observed_agreement,
            }
            for item in result.pairwise
        ],
    }
    (output_dir / "agreement_analysis.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Agreement analysis",
        "",
        f"**Status:** `{result.status.value}`  ",
        f"**Annotators:** {', '.join(f'`{name}`' for name in dataset.annotator_names)}  ",
        f"**Units:** {dataset.n_units}",
        "",
        "## Summary",
        "",
        *result.markdown_tables.get("summary", []),
    ]
    for column in ANNOTATION_COLUMNS:
        lines.extend(result.markdown_tables.get(f"per_class_{column}", []))

    (output_dir / "agreement_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    pair_path = output_dir / "pairwise_kappa_matrix.csv"
    with pair_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["column", "annotator_a", "annotator_b", "cohen_kappa", "observed_agreement"])
        for item in result.pairwise:
            writer.writerow(
                [item.column, item.annotator_a, item.annotator_b, item.kappa, item.observed_agreement]
            )
