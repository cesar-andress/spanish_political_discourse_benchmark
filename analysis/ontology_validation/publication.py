"""Publication-ready tables for ontology validation outputs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from analysis.ontology_validation.dashboard import OntologyDashboardResult
from analysis.ontology_validation.disagreement import DisagreementStructureResult
from analysis.ontology_validation.dominance import DominanceAuditResult
from analysis.ontology_validation.io import OntologyValidationDataset
from analysis.ontology_validation.per_class import PerClassReliabilityResult
from analysis.ontology_validation.reliability import OverallReliabilityResult


def _fmt(value: float) -> str:
    return "—" if value != value else f"{value:.3f}"


def generate_publication_tables(
    dataset: OntologyValidationDataset,
    reliability: OverallReliabilityResult,
    per_class: PerClassReliabilityResult,
    disagreement: DisagreementStructureResult,
    dominance: DominanceAuditResult,
    dashboard: OntologyDashboardResult,
) -> str:
    alpha = reliability.metrics.get("krippendorff_alpha", {})
    fleiss = reliability.metrics.get("fleiss_kappa", {})
    ac1 = reliability.metrics.get("gwet_ac1", {})

    lines: List[str] = [
        "# Publication tables — SPDB pragmatic-function ontology validation",
        "",
        "Draft tables formatted for *Language Resources and Evaluation* (LREC) and *Scientific Data* submissions.",
        "",
        "## Table 1. Pilot corpus and annotation design (Scientific Data style)",
        "",
        "**Table 1.** SPDB pilot ontology-validation corpus.",
        "",
        "| Attribute | Value |",
        "|-----------|-------|",
        f"| Discourse units | {dataset.n_units} |",
        f"| Annotators | {dataset.n_annotators} |",
        f"| Primary ontology | 8-class pragmatic function (`PF_*`) |",
        f"| Annotation status | `{dataset.status.value}` |",
        f"| Ontology decision | {dashboard.decision.value} |",
        "",
        "## Table 2. Overall inter-annotator reliability (LREC style)",
        "",
        "**Table 2.** Overall reliability for pragmatic-function labels (nominal metrics with 95% bootstrap CI, 2,000 resamples).",
        "",
        "| Metric | Estimate | 95% CI |",
        "|--------|---------:|--------|",
        f"| Krippendorff α | {_fmt(alpha.get('point', float('nan')))} | "
        f"[{_fmt(alpha.get('lower', float('nan')))}, {_fmt(alpha.get('upper', float('nan')))}] |",
        f"| Fleiss κ | {_fmt(fleiss.get('point', float('nan')))} | "
        f"[{_fmt(fleiss.get('lower', float('nan')))}, {_fmt(fleiss.get('upper', float('nan')))}] |",
        f"| Gwet AC1 | {_fmt(ac1.get('point', float('nan')))} | "
        f"[{_fmt(ac1.get('lower', float('nan')))}, {_fmt(ac1.get('upper', float('nan')))}] |",
        "",
        "## Table 3. Per-class reliability and support",
        "",
        "**Table 3.** One-vs-rest reliability by pragmatic-function label.",
        "",
        "| Label | Support | κ (1 vs rest) | α (1 vs rest) | PSA |",
        "|-------|--------:|--------------:|--------------:|----:|",
    ]
    for row in per_class.rows:
        lines.append(
            f"| `{row['label']}` | {row['support']} | {_fmt(row['one_vs_rest_kappa'])} | "
            f"{_fmt(row['one_vs_rest_alpha'])} | {_fmt(row['positive_specific_agreement'])} |"
        )

    lines.extend(
        [
            "",
            "## Table 4. Dominant-function audit and disagreement structure",
            "",
            "**Table 4.** Single-dominant-function audit metrics and leading confusion pairs.",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Unanimous rate | {_fmt(dominance.unanimous_rate)} |",
            f"| Majority rate | {_fmt(dominance.majority_rate)} |",
            f"| Full-split rate | {_fmt(dominance.full_split_rate)} |",
            f"| Borderline rate | {_fmt(dominance.borderline_rate)} |",
            f"| Mean vote entropy | {_fmt(dominance.entropy_mean)} |",
            "",
            "| Top confusion pair | Count | Mass |",
            "|--------------------|------:|-----:|",
        ]
    )
    if disagreement.top_pairs:
        row, col, count, mass = disagreement.top_pairs[0]
        lines.append(f"| `{row}` → `{col}` | {count} | {mass:.3f} |")
    else:
        lines.append("| — | 0 | — |")

    lines.append("")
    return "\n".join(lines)


def write_publication_tables(content: str, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "publication_tables.md"
    path.write_text(content, encoding="utf-8")
    return path
