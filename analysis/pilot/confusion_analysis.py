"""Confusion and disagreement analysis for pilot annotations."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from analysis.pilot.constants import ANNOTATION_COLUMNS, SINGLE_LABEL_COLUMNS
from analysis.pilot.io import AnnotationStatus, PilotDataset, normalized_column_matrix, usable_units_for_column
from scripts.analysis.agreement_metrics import ConfusionMatrixResult, confusion_matrix, json_safe


@dataclass(frozen=True)
class ConfusionAnalysisResult:
    status: AnnotationStatus
    by_column: Dict[str, Dict[str, Any]]
    disagreement_units: List[Dict[str, str]]
    markdown_tables: Dict[str, List[str]]
    figure_paths: List[Path]


def _aggregate_pairwise_confusion(
    matrix: List[List[str]],
) -> ConfusionMatrixResult:
    aggregate: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    labels: set[str] = set()
    total = 0
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            result = confusion_matrix(matrix[i], matrix[j])
            labels.update(result.labels)
            for row_label in result.labels:
                for col_label in result.labels:
                    aggregate[row_label][col_label] += result.matrix[row_label][col_label]
                    total += result.matrix[row_label][col_label]
    ordered = sorted(labels)
    matrix_dict = {
        row: {col: int(aggregate[row][col]) for col in ordered}
        for row in ordered
    }
    return ConfusionMatrixResult(column="", labels=ordered, matrix=matrix_dict, total=total)


def _dominant_confusion_pairs(result: ConfusionMatrixResult, *, top_n: int = 10) -> List[Tuple[str, str, int]]:
    pairs: List[Tuple[str, str, int]] = []
    for row in result.labels:
        for col in result.labels:
            if row != col and result.matrix[row][col]:
                pairs.append((row, col, result.matrix[row][col]))
    pairs.sort(key=lambda item: item[2], reverse=True)
    return pairs[:top_n]


def _collect_disagreement_units(dataset: PilotDataset) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    if dataset.n_annotators < 2:
        return rows

    for unit_id in dataset.unit_ids:
        changed: List[str] = []
        row: Dict[str, str] = {
            "unit_id": unit_id,
            "speaker_name": dataset.metadata.get(unit_id, {}).get("speaker_name", ""),
            "speaker_party": dataset.metadata.get(unit_id, {}).get("speaker_party", ""),
        }
        disagreement_count = 0
        for column in ANNOTATION_COLUMNS:
            values = [dataset.labels[index][unit_id][column] for index in range(dataset.n_annotators)]
            if len(set(values)) > 1:
                changed.append(column)
                disagreement_count += 1
            row[f"{column}_values"] = "|".join(values)
        if changed:
            row["changed_columns"] = "|".join(changed)
            row["disagreement_count"] = str(disagreement_count)
            rows.append(row)

    rows.sort(key=lambda item: int(item["disagreement_count"]), reverse=True)
    return rows


def _write_heatmap(path: Path, result: ConfusionMatrixResult, *, title: str) -> None:
    import matplotlib.pyplot as plt
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.array([[result.matrix[row][col] for col in result.labels] for row in result.labels])
    fig, ax = plt.subplots(figsize=(8, 6))
    image = ax.imshow(data, cmap="Blues")
    ax.set_xticks(range(len(result.labels)), result.labels, rotation=35, ha="right")
    ax.set_yticks(range(len(result.labels)), result.labels)
    ax.set_xlabel("Predicted / annotator B")
    ax.set_ylabel("Reference / annotator A")
    ax.set_title(title)
    for i in range(len(result.labels)):
        for j in range(len(result.labels)):
            ax.text(j, i, str(data[i, j]), ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def run_confusion_analysis(
    dataset: PilotDataset,
    *,
    figures_dir: Path,
) -> ConfusionAnalysisResult:
    by_column: Dict[str, Dict[str, Any]] = {}
    markdown_tables: Dict[str, List[str]] = {}
    figure_paths: List[Path] = []

    if dataset.status is AnnotationStatus.PENDING:
        return ConfusionAnalysisResult(
            status=dataset.status,
            by_column={},
            disagreement_units=[],
            markdown_tables={
                "summary": ["_Confusion analysis pending: no filled annotation labels were found._"]
            },
            figure_paths=[],
        )

    disagreement_units = _collect_disagreement_units(dataset)
    summary_lines = [
        "| Dimension | Pairwise comparisons | Dominant off-diagonal pair | Count |",
        "|-----------|---------------------:|----------------------------|------:|",
    ]

    for column in (*SINGLE_LABEL_COLUMNS, "fallacy_labels"):
        unit_ids = usable_units_for_column(dataset, column)
        if len(unit_ids) < 2 or dataset.n_annotators < 2:
            continue
        matrix = [
            [row[dataset.unit_ids.index(unit_id)] for unit_id in unit_ids]
            for row in normalized_column_matrix(dataset, column)
        ]
        aggregate = _aggregate_pairwise_confusion(matrix)
        dominant = _dominant_confusion_pairs(aggregate)
        concentration = Counter()
        for unit_id in unit_ids:
            values = [dataset.labels[index][unit_id][column] for index in range(dataset.n_annotators)]
            if len(set(values)) > 1:
                concentration["|".join(sorted(set(values)))] += 1

        by_column[column] = {
            "matrix": aggregate.matrix,
            "labels": aggregate.labels,
            "total": aggregate.total,
            "dominant_pairs": dominant,
            "disagreement_patterns": concentration.most_common(10),
        }

        top_pair = dominant[0] if dominant else ("—", "—", 0)
        summary_lines.append(
            f"| `{column}` | {aggregate.total} | `{top_pair[0]}` → `{top_pair[1]}` | {top_pair[2]} |"
        )

        table_lines = [
            "",
            f"### Confusion matrix — `{column}`",
            "",
            "| A \\ B | " + " | ".join(f"`{label}`" for label in aggregate.labels) + " |",
            "|-------|" + "|".join(["---:"] * len(aggregate.labels)) + "|",
        ]
        for row_label in aggregate.labels:
            cells = " | ".join(str(aggregate.matrix[row_label][col_label]) for col_label in aggregate.labels)
            table_lines.append(f"| `{row_label}` | {cells} |")
        markdown_tables[f"matrix_{column}"] = table_lines

        figure_path = figures_dir / f"confusion_{column}.png"
        _write_heatmap(figure_path, aggregate, title=f"Aggregated confusion — {column}")
        figure_paths.append(figure_path)

    concentration_lines = [
        "",
        "## Disagreement concentration",
        "",
        f"**Units with any disagreement:** {len(disagreement_units)} / {dataset.n_units}",
        "",
    ]
    if disagreement_units:
        concentration_lines.extend(
            [
                "| unit_id | speaker_party | changed_columns | disagreement_count |",
                "|---------|---------------|-----------------|-------------------:|",
            ]
        )
        for row in disagreement_units[:15]:
            concentration_lines.append(
                f"| `{row['unit_id']}` | {row.get('speaker_party', '')} | "
                f"`{row.get('changed_columns', '')}` | {row.get('disagreement_count', '0')} |"
            )
    else:
        concentration_lines.append("_No disagreements observed._")

    markdown_tables["summary"] = summary_lines
    markdown_tables["concentration"] = concentration_lines

    return ConfusionAnalysisResult(
        status=dataset.status,
        by_column=by_column,
        disagreement_units=disagreement_units,
        markdown_tables=markdown_tables,
        figure_paths=figure_paths,
    )


def write_confusion_outputs(result: ConfusionAnalysisResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": result.status.value,
        "matrices": json_safe(result.by_column),
        "disagreement_units": result.disagreement_units,
        "figures": [str(path) for path in result.figure_paths],
    }
    (output_dir / "confusion_analysis.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = ["# Confusion analysis", "", *result.markdown_tables.get("summary", [])]
    for column in ANNOTATION_COLUMNS:
        lines.extend(result.markdown_tables.get(f"matrix_{column}", []))
    lines.extend(result.markdown_tables.get("concentration", []))
    (output_dir / "confusion_analysis.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
