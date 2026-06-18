"""Disagreement structure analysis for PF ontology validation."""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Tuple

from analysis.ontology_validation.io import OntologyValidationDataset, pf_label_matrix
from analysis.pilot.io import AnnotationStatus
from scripts.analysis.agreement_metrics import ConfusionMatrixResult, confusion_matrix


@dataclass(frozen=True)
class DisagreementStructureResult:
    status: AnnotationStatus
    matrix: ConfusionMatrixResult
    top_pairs: List[Tuple[str, str, int, float]]
    symmetry: Dict[str, float | int]
    concentration: List[Dict[str, str | int]]


def _aggregate_confusion(matrix: List[List[str]]) -> ConfusionMatrixResult:
    aggregate: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    labels: set[str] = set()
    total = 0
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            result = confusion_matrix(matrix[i], matrix[j])
            labels.update(result.labels)
            for row in result.labels:
                for col in result.labels:
                    aggregate[row][col] += result.matrix[row][col]
                    total += result.matrix[row][col]
    ordered = sorted(labels)
    return ConfusionMatrixResult(
        column="pragmatic_function",
        labels=ordered,
        matrix={row: {col: int(aggregate[row][col]) for col in ordered} for row in ordered},
        total=total,
    )


def _top_confusion_pairs(result: ConfusionMatrixResult) -> List[Tuple[str, str, int, float]]:
    off_total = sum(
        result.matrix[row][col]
        for row in result.labels
        for col in result.labels
        if row != col
    )
    pairs: List[Tuple[str, str, int, float]] = []
    for row in result.labels:
        for col in result.labels:
            if row == col:
                continue
            count = result.matrix[row][col]
            if count:
                mass = count / off_total if off_total else 0.0
                pairs.append((row, col, count, mass))
    pairs.sort(key=lambda item: item[2], reverse=True)
    return pairs


def _symmetry_analysis(result: ConfusionMatrixResult) -> Dict[str, float | int]:
    symmetric = 0
    asymmetric = 0
    for row in result.labels:
        for col in result.labels:
            if row >= col:
                continue
            left = result.matrix[row][col]
            right = result.matrix[col][row]
            symmetric += min(left, right)
            asymmetric += abs(left - right)
    total = symmetric + asymmetric
    return {
        "symmetric_mass": symmetric,
        "asymmetric_mass": asymmetric,
        "symmetry_ratio": symmetric / total if total else float("nan"),
    }


def _disagreement_concentration(dataset: OntologyValidationDataset) -> List[Dict[str, str | int]]:
    rows: List[Dict[str, str | int]] = []
    for unit_id in dataset.unit_ids:
        values = [dataset.pilot.labels[index][unit_id]["pragmatic_function"] for index in range(dataset.n_annotators)]
        if len(set(values)) > 1:
            rows.append(
                {
                    "unit_id": unit_id,
                    "labels": "|".join(values),
                    "unique_labels": len(set(values)),
                    "speaker_party": dataset.pilot.metadata.get(unit_id, {}).get("speaker_party", ""),
                }
            )
    rows.sort(key=lambda item: int(item["unique_labels"]), reverse=True)
    return rows


def run_disagreement_structure(dataset: OntologyValidationDataset) -> DisagreementStructureResult:
    inventory = dataset.pf_inventory
    if dataset.status is AnnotationStatus.PENDING:
        empty = ConfusionMatrixResult(
            column="pragmatic_function",
            labels=inventory,
            matrix={row: {col: 0 for col in inventory} for row in inventory},
            total=0,
        )
        return DisagreementStructureResult(
            status=dataset.status,
            matrix=empty,
            top_pairs=[],
            symmetry={"symmetric_mass": 0, "asymmetric_mass": 0, "symmetry_ratio": float("nan")},
            concentration=[],
        )

    matrix = pf_label_matrix(dataset)
    aggregate = _aggregate_confusion(matrix)
    return DisagreementStructureResult(
        status=dataset.status,
        matrix=aggregate,
        top_pairs=_top_confusion_pairs(aggregate),
        symmetry=_symmetry_analysis(aggregate),
        concentration=_disagreement_concentration(dataset),
    )


def write_disagreement_structure(result: DisagreementStructureResult, output_dir: Path, *, figures_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    labels = result.matrix.labels
    with (output_dir / "confusion_matrix.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["annotator_a", *labels])
        for row_label in labels:
            writer.writerow([row_label, *[result.matrix.matrix[row_label][col] for col in labels]])

    lines = [
        "# Disagreement structure — pragmatic function ontology",
        "",
        f"**Status:** `{result.status.value}`",
        "",
        "## Aggregated 8×8 confusion matrix",
        "",
        "Rows and columns index annotator label pairs (A→B) aggregated across all annotator pairs.",
        "",
        "| A \\ B | " + " | ".join(f"`{label}`" for label in labels) + " |",
        "|-------|" + "|".join(["---:"] * len(labels)) + "|",
    ]
    for row_label in labels:
        cells = " | ".join(str(result.matrix.matrix[row_label][col]) for col in labels)
        lines.append(f"| `{row_label}` | {cells} |")

    lines.extend(
        [
            "",
            "## Top confusion pairs",
            "",
            "| From | To | Count | Disagreement mass |",
            "|------|----|------:|------------------:|",
        ]
    )
    for row, col, count, mass in result.top_pairs[:10]:
        lines.append(f"| `{row}` | `{col}` | {count} | {mass:.3f} |")

    lines.extend(
        [
            "",
            "## Symmetry analysis",
            "",
            f"- Symmetric mass: {result.symmetry['symmetric_mass']}",
            f"- Asymmetric mass: {result.symmetry['asymmetric_mass']}",
            f"- Symmetry ratio: {result.symmetry['symmetry_ratio']}",
            "",
            "## Disagreement concentration",
            "",
        ]
    )
    if result.concentration:
        lines.extend(
            [
                "| unit_id | labels | unique_labels | party |",
                "|---------|--------|--------------:|-------|",
            ]
        )
        for row in result.concentration[:20]:
            lines.append(
                f"| `{row['unit_id']}` | `{row['labels']}` | {row['unique_labels']} | {row.get('speaker_party', '')} |"
            )
    else:
        lines.append("_No disagreements observed._")

    if result.status is not AnnotationStatus.PENDING and result.matrix.labels:
        figure_path = _write_heatmap(figures_dir / "confusion_heatmap.png", result.matrix)
        lines.extend(["", f"![Confusion heatmap]({figure_path.as_posix()})", ""])

    lines.append("")
    (output_dir / "confusion_report.md").write_text("\n".join(lines), encoding="utf-8")


def _write_heatmap(path: Path, result: ConfusionMatrixResult) -> Path:
    import matplotlib.pyplot as plt
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    data = np.array([[result.matrix[row][col] for col in result.labels] for row in result.labels])
    fig, ax = plt.subplots(figsize=(9, 7))
    image = ax.imshow(data, cmap="Blues")
    ax.set_xticks(range(len(result.labels)), result.labels, rotation=35, ha="right")
    ax.set_yticks(range(len(result.labels)), result.labels)
    ax.set_title("Aggregated PF confusion matrix")
    for i in range(len(result.labels)):
        for j in range(len(result.labels)):
            ax.text(j, i, str(data[i, j]), ha="center", va="center", color="black", fontsize=8)
    fig.colorbar(image, ax=ax, fraction=0.046, pad=0.04)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
