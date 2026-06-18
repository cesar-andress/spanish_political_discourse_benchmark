"""Ontology pass/fail dashboard for pilot-review thresholds."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List

from analysis.ontology_validation.constants import (
    THRESHOLD_ALPHA_MIN,
    THRESHOLD_BORDERLINE_MAX,
    THRESHOLD_CONFUSION_PAIR_MAX,
    THRESHOLD_FULL_SPLIT_MAX,
    WARN_ALPHA_MIN,
    WARN_BORDERLINE_MAX,
)
from analysis.ontology_validation.disagreement import DisagreementStructureResult
from analysis.ontology_validation.dominance import DominanceAuditResult
from analysis.ontology_validation.reliability import OverallReliabilityResult
from analysis.pilot.io import AnnotationStatus


class OntologyDecision(str, Enum):
    PENDING = "PENDING — AWAITING ANNOTATIONS"
    PASS = "PASS"
    PASS_WITH_WARNINGS = "PASS WITH WARNINGS"
    FAIL = "FAIL"


@dataclass(frozen=True)
class OntologyDashboardResult:
    decision: OntologyDecision
    failures: List[str]
    warnings: List[str]
    metrics_snapshot: Dict[str, Any]


def evaluate_dashboard(
    *,
    dataset_status: AnnotationStatus,
    reliability: OverallReliabilityResult,
    disagreement: DisagreementStructureResult,
    dominance: DominanceAuditResult,
) -> OntologyDashboardResult:
    if dataset_status is AnnotationStatus.PENDING:
        return OntologyDashboardResult(
            decision=OntologyDecision.PENDING,
            failures=[],
            warnings=["Human annotations not yet available; thresholds not evaluated."],
            metrics_snapshot={},
        )

    failures: List[str] = []
    warnings: List[str] = []

    alpha = reliability.metrics.get("krippendorff_alpha", {}).get("point", float("nan"))
    if alpha == alpha and alpha < THRESHOLD_ALPHA_MIN:
        failures.append(f"Krippendorff α = {alpha:.3f} < {THRESHOLD_ALPHA_MIN}")
    elif alpha == alpha and alpha < WARN_ALPHA_MIN:
        warnings.append(f"Krippendorff α = {alpha:.3f} below recommended {WARN_ALPHA_MIN}")

    if dominance.full_split_rate == dominance.full_split_rate and dominance.full_split_rate > THRESHOLD_FULL_SPLIT_MAX:
        failures.append(
            f"Full-split rate = {dominance.full_split_rate:.3f} > {THRESHOLD_FULL_SPLIT_MAX}"
        )

    if dominance.borderline_rate == dominance.borderline_rate and dominance.borderline_rate > THRESHOLD_BORDERLINE_MAX:
        failures.append(
            f"Borderline rate = {dominance.borderline_rate:.3f} > {THRESHOLD_BORDERLINE_MAX}"
        )
    elif (
        dominance.borderline_rate == dominance.borderline_rate
        and dominance.borderline_rate > WARN_BORDERLINE_MAX
    ):
        warnings.append(
            f"Borderline rate = {dominance.borderline_rate:.3f} above guideline target {WARN_BORDERLINE_MAX}"
        )

    top_mass = disagreement.top_pairs[0][3] if disagreement.top_pairs else 0.0
    if top_mass > THRESHOLD_CONFUSION_PAIR_MAX:
        pair = disagreement.top_pairs[0]
        failures.append(
            f"Dominant confusion pair `{pair[0]}`→`{pair[1]}` carries {top_mass:.3f} disagreement mass "
            f"(> {THRESHOLD_CONFUSION_PAIR_MAX})"
        )

    if failures:
        decision = OntologyDecision.FAIL
    elif warnings:
        decision = OntologyDecision.PASS_WITH_WARNINGS
    else:
        decision = OntologyDecision.PASS

    snapshot = {
        "krippendorff_alpha": alpha,
        "full_split_rate": dominance.full_split_rate,
        "borderline_rate": dominance.borderline_rate,
        "top_confusion_mass": top_mass,
    }
    return OntologyDashboardResult(
        decision=decision,
        failures=failures,
        warnings=warnings,
        metrics_snapshot=snapshot,
    )


def write_dashboard(result: OntologyDashboardResult, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Ontology pass/fail dashboard",
        "",
        f"## Decision: **{result.decision.value}**",
        "",
        "### Thresholds",
        "",
        "| Rule | Threshold |",
        "|------|-----------|",
        f"| Krippendorff α | ≥ {THRESHOLD_ALPHA_MIN} |",
        f"| Full-split rate | ≤ {THRESHOLD_FULL_SPLIT_MAX} |",
        f"| Borderline rate | ≤ {THRESHOLD_BORDERLINE_MAX} |",
        f"| Single confusion-pair mass | ≤ {THRESHOLD_CONFUSION_PAIR_MAX} |",
        "",
    ]
    if result.metrics_snapshot:
        lines.extend(
            [
                "### Observed metrics",
                "",
                "| Metric | Value |",
                "|--------|------:|",
            ]
        )
        for key, value in result.metrics_snapshot.items():
            display = "n/a" if isinstance(value, float) and value != value else (
                f"{value:.4f}" if isinstance(value, float) else str(value)
            )
            lines.append(f"| `{key}` | {display} |")
        lines.append("")

    if result.failures:
        lines.extend(["### Failures", ""])
        for item in result.failures:
            lines.append(f"- {item}")
        lines.append("")

    if result.warnings:
        lines.extend(["### Warnings", ""])
        for item in result.warnings:
            lines.append(f"- {item}")
        lines.append("")

    (output_dir / "ontology_decision.md").write_text("\n".join(lines), encoding="utf-8")
