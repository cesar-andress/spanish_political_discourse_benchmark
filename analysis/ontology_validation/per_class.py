"""Per-class reliability analysis for PF ontology validation."""

from __future__ import annotations

import csv
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from analysis.ontology_validation.io import OntologyValidationDataset, pf_label_matrix, pf_unit_ratings
from analysis.ontology_validation.metrics import (
    one_vs_rest_alpha,
    one_vs_rest_kappa,
    positive_specific_agreement,
)
from analysis.pilot.io import AnnotationStatus


@dataclass(frozen=True)
class PerClassReliabilityResult:
    status: AnnotationStatus
    rows: List[Dict[str, Any]]


def run_per_class_reliability(dataset: OntologyValidationDataset) -> PerClassReliabilityResult:
    inventory = dataset.pf_inventory
    if dataset.status is AnnotationStatus.PENDING:
        rows = [
            {
                "label": label,
                "support": 0,
                "one_vs_rest_kappa": float("nan"),
                "one_vs_rest_alpha": float("nan"),
                "positive_specific_agreement": float("nan"),
            }
            for label in inventory
        ]
        return PerClassReliabilityResult(status=dataset.status, rows=rows)

    matrix = pf_label_matrix(dataset)
    unit_ratings = pf_unit_ratings(dataset)
    pooled = Counter(label for ratings in unit_ratings for label in ratings)
    rows: List[Dict[str, Any]] = []
    for label in inventory:
        rows.append(
            {
                "label": label,
                "support": pooled.get(label, 0),
                "one_vs_rest_kappa": one_vs_rest_kappa(matrix, label),
                "one_vs_rest_alpha": one_vs_rest_alpha(matrix, label),
                "positive_specific_agreement": positive_specific_agreement(unit_ratings, label),
            }
        )
    return PerClassReliabilityResult(status=dataset.status, rows=rows)


def write_per_class_reliability(result: PerClassReliabilityResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "label",
        "support",
        "one_vs_rest_kappa",
        "one_vs_rest_alpha",
        "positive_specific_agreement",
    ]
    with (output_dir / "per_class_reliability.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(result.rows)

    lines = [
        "# Per-class reliability — pragmatic function ontology",
        "",
        f"**Status:** `{result.status.value}`",
        "",
        "| PF label | Support | One-vs-rest κ | One-vs-rest α | PSA |",
        "|----------|--------:|--------------:|--------------:|----:|",
    ]
    for row in result.rows:
        lines.append(
            f"| `{row['label']}` | {row['support']} | "
            f"{_fmt(row['one_vs_rest_kappa'])} | {_fmt(row['one_vs_rest_alpha'])} | "
            f"{_fmt(row['positive_specific_agreement'])} |"
        )
    lines.append("")
    (output_dir / "per_class_reliability.md").write_text("\n".join(lines), encoding="utf-8")


def _fmt(value: float) -> str:
    return "n/a" if value != value else f"{value:.4f}"
