"""Overall reliability analysis for pragmatic-function ontology validation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

from analysis.ontology_validation.constants import BOOTSTRAP_ITERATIONS, RANDOM_SEED
from analysis.ontology_validation.io import OntologyValidationDataset, pf_label_matrix, pf_unit_ratings
from analysis.ontology_validation.metrics import overall_metrics
from analysis.pilot.io import AnnotationStatus
from scripts.analysis.agreement_metrics import json_safe


@dataclass(frozen=True)
class OverallReliabilityResult:
    status: AnnotationStatus
    metrics: Dict[str, Any]


def _format_ci(metric: Dict[str, Any]) -> str:
    point = metric.get("point", float("nan"))
    lower = metric.get("lower", float("nan"))
    upper = metric.get("upper", float("nan"))
    if point != point:
        return "n/a"
    if lower != lower or upper != upper:
        return f"{point:.4f}"
    return f"{point:.4f} [{lower:.4f}, {upper:.4f}]"


def run_overall_reliability(
    dataset: OntologyValidationDataset,
    *,
    bootstrap_iterations: int = BOOTSTRAP_ITERATIONS,
    seed: int = RANDOM_SEED,
) -> OverallReliabilityResult:
    if dataset.status is AnnotationStatus.PENDING:
        return OverallReliabilityResult(status=dataset.status, metrics={})

    unit_ratings = pf_unit_ratings(dataset)
    matrix = pf_label_matrix(dataset)
    metrics = overall_metrics(
        unit_ratings,
        matrix,
        dataset.annotator_names,
        bootstrap_iterations=bootstrap_iterations,
        seed=seed,
    )
    return OverallReliabilityResult(status=dataset.status, metrics=metrics)


def write_overall_reliability(result: OverallReliabilityResult, output_dir: Path, dataset: OntologyValidationDataset) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "status": result.status.value,
        "n_units": dataset.n_units,
        "n_annotators": dataset.n_annotators,
        "annotators": list(dataset.annotator_names),
        "metrics": json_safe(result.metrics),
    }
    (output_dir / "overall_reliability.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Overall reliability — pragmatic function ontology",
        "",
        f"**Status:** `{result.status.value}`  ",
        f"**Units:** {dataset.n_units}  ",
        f"**Annotators:** {dataset.n_annotators}",
        "",
    ]
    if result.status is AnnotationStatus.PENDING:
        lines.append("_Awaiting annotations — metrics will populate once annotator CSV files are filled._")
    else:
        lines.extend(
            [
                "## Summary metrics (95% bootstrap CI)",
                "",
                "| Metric | Estimate [95% CI] |",
                "|--------|-------------------:|",
                f"| Krippendorff α (nominal) | {_format_ci(result.metrics['krippendorff_alpha'])} |",
                f"| Fleiss κ | {_format_ci(result.metrics['fleiss_kappa'])} |",
                f"| Mean pairwise Cohen κ | {_format_ci(result.metrics['mean_pairwise_cohen_kappa'])} |",
                f"| Gwet AC1 | {_format_ci(result.metrics['gwet_ac1'])} |",
                "",
                "## Pairwise Cohen κ",
                "",
                "| Annotator A | Annotator B | κ | Observed agreement |",
                "|-------------|-------------|--:|-------------------:|",
            ]
        )
        for row in result.metrics.get("pairwise_cohen_kappa", []):
            lines.append(
                f"| `{row['annotator_a']}` | `{row['annotator_b']}` | "
                f"{row['cohen_kappa']:.4f} | {row['observed_agreement']:.4f} |"
            )
    lines.append("")
    (output_dir / "overall_reliability.md").write_text("\n".join(lines), encoding="utf-8")
