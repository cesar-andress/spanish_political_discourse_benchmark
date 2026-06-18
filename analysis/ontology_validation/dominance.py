"""Single-dominant-function audit for PF ontology validation."""

from __future__ import annotations

import math
import statistics
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from analysis.ontology_validation.constants import OPTIONAL_QC_COLUMNS
from analysis.ontology_validation.io import OntologyValidationDataset, pf_unit_ratings
from analysis.pilot.io import AnnotationStatus


@dataclass(frozen=True)
class DominanceAuditResult:
    status: AnnotationStatus
    unanimous_rate: float
    majority_rate: float
    full_split_rate: float
    entropy_mean: float
    entropy_values: List[float]
    borderline_rate: float
    second_choice_rate: float
    unit_details: List[Dict[str, Any]]


def _vote_entropy(ratings: List[str]) -> float:
    counts = Counter(ratings)
    total = sum(counts.values())
    if total == 0:
        return float("nan")
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log(p)
    return entropy


def _borderline_rate(dataset: OntologyValidationDataset) -> float:
    if not dataset.qc_fields:
        return float("nan")
    flagged = 0
    for unit_id in dataset.unit_ids:
        for qc in dataset.qc_fields:
            value = (qc.get(unit_id, {}).get("borderline") or "").strip().lower()
            if value in {"true", "1", "yes"}:
                flagged += 1
                break
    return flagged / dataset.n_units if dataset.n_units else float("nan")


def _second_choice_rate(dataset: OntologyValidationDataset) -> float:
    if not dataset.qc_fields:
        return float("nan")
    filled = 0
    for unit_id in dataset.unit_ids:
        for qc in dataset.qc_fields:
            value = (qc.get(unit_id, {}).get("second_choice") or "").strip()
            if value:
                filled += 1
                break
    return filled / dataset.n_units if dataset.n_units else float("nan")


def run_dominance_audit(dataset: OntologyValidationDataset) -> DominanceAuditResult:
    if dataset.status is AnnotationStatus.PENDING:
        return DominanceAuditResult(
            status=dataset.status,
            unanimous_rate=float("nan"),
            majority_rate=float("nan"),
            full_split_rate=float("nan"),
            entropy_mean=float("nan"),
            entropy_values=[],
            borderline_rate=float("nan"),
            second_choice_rate=float("nan"),
            unit_details=[],
        )

    unit_ratings = pf_unit_ratings(dataset)
    unanimous = majority = full_split = 0
    entropies: List[float] = []
    details: List[Dict[str, Any]] = []

    for unit_id, ratings in zip(
        [uid for uid in dataset.unit_ids if all(
            dataset.pilot.labels[i][uid]["pragmatic_function"].strip() for i in range(dataset.n_annotators)
        )],
        unit_ratings,
    ):
        counts = Counter(ratings)
        top_count = counts.most_common(1)[0][1]
        unique = len(counts)
        if unique == 1:
            unanimous += 1
        if top_count >= 2:
            majority += 1
        if unique == dataset.n_annotators and dataset.n_annotators >= 3:
            full_split += 1
        entropy = _vote_entropy(ratings)
        entropies.append(entropy)
        second_choices = [
            dataset.qc_fields[i].get(unit_id, {}).get("second_choice", "")
            for i in range(len(dataset.qc_fields))
        ]
        borderline_flags = [
            dataset.qc_fields[i].get(unit_id, {}).get("borderline", "")
            for i in range(len(dataset.qc_fields))
        ]
        details.append(
            {
                "unit_id": unit_id,
                "votes": "|".join(ratings),
                "entropy": entropy,
                "borderline": "|".join(borderline_flags),
                "second_choice": "|".join(second_choices),
            }
        )

    n = len(unit_ratings)
    return DominanceAuditResult(
        status=dataset.status,
        unanimous_rate=unanimous / n if n else float("nan"),
        majority_rate=majority / n if n else float("nan"),
        full_split_rate=full_split / n if n else float("nan"),
        entropy_mean=statistics.mean(entropies) if entropies else float("nan"),
        entropy_values=entropies,
        borderline_rate=_borderline_rate(dataset),
        second_choice_rate=_second_choice_rate(dataset),
        unit_details=details,
    )


def write_dominance_audit(result: DominanceAuditResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Single-dominant-function audit",
        "",
        f"**Status:** `{result.status.value}`",
        "",
        "## Aggregate rates",
        "",
        "| Metric | Value | Pilot threshold |",
        "|--------|------:|-----------------|",
        f"| Unanimous rate | {_fmt(result.unanimous_rate)} | — |",
        f"| Majority rate | {_fmt(result.majority_rate)} | — |",
        f"| Full-split rate (3 distinct labels) | {_fmt(result.full_split_rate)} | ≤ 0.20 |",
        f"| Mean vote entropy | {_fmt(result.entropy_mean)} | — |",
        f"| Borderline rate | {_fmt(result.borderline_rate)} | ≤ 0.25 |",
        f"| Second-choice usage rate | {_fmt(result.second_choice_rate)} | — |",
        "",
        "## Entropy distribution",
        "",
    ]
    if result.entropy_values:
        buckets = Counter(round(value, 2) for value in result.entropy_values)
        lines.extend(["| Entropy (rounded) | Units |", "|------------------|------:|"])
        for entropy, count in sorted(buckets.items()):
            lines.append(f"| {entropy:.2f} | {count} |")
    else:
        lines.append("_Awaiting annotations._")

    if result.unit_details:
        lines.extend(
            [
                "",
                "## Unit-level audit (first 20 rows)",
                "",
                "| unit_id | votes | entropy | borderline | second_choice |",
                "|---------|-------|--------:|------------|---------------|",
            ]
        )
        for row in result.unit_details[:20]:
            lines.append(
                f"| `{row['unit_id']}` | `{row['votes']}` | {row['entropy']:.3f} | "
                f"`{row['borderline']}` | `{row['second_choice']}` |"
            )
    lines.append("")
    (output_dir / "single_dominance_report.md").write_text("\n".join(lines), encoding="utf-8")


def _fmt(value: float) -> str:
    return "n/a" if value != value else f"{value:.4f}"
