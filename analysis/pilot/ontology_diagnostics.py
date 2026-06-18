"""Ontology diagnostics for pilot annotation labels."""

from __future__ import annotations

import csv
import json
import math
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from analysis.pilot.confusion_analysis import _aggregate_pairwise_confusion, _dominant_confusion_pairs
from analysis.pilot.constants import ONTOLOGY_INVENTORIES, PRIMARY_ONTOLOGY_COLUMN
from analysis.pilot.io import AnnotationStatus, PilotDataset, normalized_column_matrix
from scripts.analysis.agreement_metrics import json_safe


@dataclass(frozen=True)
class OntologyDiagnosticsResult:
    status: AnnotationStatus
    by_column: Dict[str, Dict[str, Any]]
    markdown_tables: Dict[str, List[str]]


def _load_inventory(path: Path) -> List[str]:
    if not path.exists():
        return []
    labels: List[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            label_id = (row.get("label_id") or "").strip()
            if label_id:
                labels.append(label_id)
    return labels


def _entropy(counts: Counter[str], *, inventory: List[str]) -> float:
    total = sum(counts.values())
    if total == 0:
        if not inventory:
            return float("nan")
        return math.log(len(inventory))
    entropy = 0.0
    for label in inventory or sorted(counts):
        p = counts.get(label, 0) / total
        if p > 0:
            entropy -= p * math.log(p)
    return entropy


def _imbalance_metrics(counts: Counter[str], inventory: List[str]) -> Dict[str, float | int | str]:
    total = sum(counts.values())
    if total == 0:
        return {
            "total": 0,
            "max_share": 0.0,
            "min_share": 0.0,
            "imbalance_ratio": float("nan"),
            "assessment": "pending",
        }
    shares = [counts.get(label, 0) / total for label in inventory or sorted(counts)]
    max_share = max(shares)
    positive = [share for share in shares if share > 0]
    min_share = min(positive) if positive else 0.0
    ratio = max_share / min_share if min_share else float("inf")
    assessment = "balanced"
    if max_share >= 0.50:
        assessment = "highly_imbalanced"
    elif max_share >= 0.35:
        assessment = "moderately_imbalanced"
    return {
        "total": total,
        "max_share": max_share,
        "min_share": min_share,
        "imbalance_ratio": ratio,
        "assessment": assessment,
    }


def _pooled_counts(dataset: PilotDataset, column: str) -> Counter[str]:
    counts: Counter[str] = Counter()
    for index in range(dataset.n_annotators):
        for unit_id in dataset.unit_ids:
            value = dataset.labels[index][unit_id][column].strip()
            if value:
                counts[value] += 1
    return counts


def run_ontology_diagnostics(dataset: PilotDataset) -> OntologyDiagnosticsResult:
    by_column: Dict[str, Dict[str, Any]] = {}
    markdown_tables: Dict[str, List[str]] = {}

    summary_lines = [
        "| Dimension | Observed assignments | Entropy | Max class share | Imbalance |",
        "|-----------|---------------------:|--------:|----------------:|-----------|",
    ]

    for column, inventory_path in ONTOLOGY_INVENTORIES.items():
        inventory = _load_inventory(inventory_path)
        counts = _pooled_counts(dataset, column) if dataset.status is not AnnotationStatus.PENDING else Counter()
        entropy = _entropy(counts, inventory=inventory)
        imbalance = _imbalance_metrics(counts, inventory)
        support = {label: counts.get(label, 0) for label in inventory or sorted(counts)}

        dominant_pairs: List[Dict[str, str | int]] = []
        if (
            column == PRIMARY_ONTOLOGY_COLUMN
            and dataset.n_annotators >= 2
            and dataset.status is not AnnotationStatus.PENDING
        ):
            matrix = normalized_column_matrix(dataset, column)
            aggregate = _aggregate_pairwise_confusion(matrix)
            dominant_pairs = [
                {"from": left, "to": right, "count": count}
                for left, right, count in _dominant_confusion_pairs(aggregate)
            ]

        by_column[column] = {
            "inventory": inventory,
            "support": support,
            "entropy": entropy,
            "imbalance": imbalance,
            "dominant_confusion_pairs": dominant_pairs,
        }

        summary_lines.append(
            f"| `{column}` | {int(imbalance['total'])} | {entropy:.4f} | "
            f"{float(imbalance['max_share']):.3f} | {imbalance['assessment']} |"
        )

        support_lines = [
            "",
            f"### Class support — `{column}`",
            "",
            "| Label | Observed count | Inventory |",
            "|-------|---------------:|:---------:|",
        ]
        for label in inventory or sorted(counts):
            support_lines.append(f"| `{label}` | {support.get(label, 0)} | yes |")
        for label in sorted(counts):
            if label not in inventory:
                support_lines.append(f"| `{label}` | {counts[label]} | no |")
        markdown_tables[f"support_{column}"] = support_lines

        if dominant_pairs:
            pair_lines = [
                "",
                f"### Dominant confusion pairs — `{column}`",
                "",
                "| From | To | Count |",
                "|------|----|------:|",
            ]
            for pair in dominant_pairs:
                pair_lines.append(
                    f"| `{pair['from']}` | `{pair['to']}` | {pair['count']} |"
                )
            markdown_tables[f"pairs_{column}"] = pair_lines

    if dataset.status is AnnotationStatus.PENDING:
        summary_lines.extend(
            [
                "",
                "_Ontology diagnostics are in pre-annotation mode: inventories are loaded, "
                "but observed support counts are zero until labels are submitted._",
            ]
        )

    markdown_tables["summary"] = summary_lines
    return OntologyDiagnosticsResult(
        status=dataset.status,
        by_column=by_column,
        markdown_tables=markdown_tables,
    )


def write_ontology_outputs(result: OntologyDiagnosticsResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "ontology_diagnostics.json").write_text(
        json.dumps(json_safe({"status": result.status.value, "dimensions": result.by_column}), indent=2)
        + "\n",
        encoding="utf-8",
    )
    lines = ["# Ontology diagnostics", "", *result.markdown_tables.get("summary", [])]
    for column in ONTOLOGY_INVENTORIES:
        lines.extend(result.markdown_tables.get(f"support_{column}", []))
        lines.extend(result.markdown_tables.get(f"pairs_{column}", []))
    (output_dir / "ontology_diagnostics.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
