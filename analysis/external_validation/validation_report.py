"""Benchmark compatibility matrix and validation roadmap generation."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple

from analysis.external_validation.constants import (
    DEFAULT_REPORT_DIR,
    EXTERNAL_DATASETS,
    ExternalDataset,
)

ROADMAP_PHASES: Tuple[str, ...] = (
    "Phase 0 (current): document inventory, ontology mappings, and compatibility constraints "
    "without running external evaluation.",
    "Phase 1 (post-pilot): project adjudicated SPDB fallacy labels onto nearest external "
    "classes for FallacyES-Political and FallacyES; report label-wise coverage and gaps.",
    "Phase 2 (post-pilot): train or fine-tune SPDB fallacy models on external Spanish data "
    "and evaluate on held-out SPDB dev units (transfer-in) and vice versa (transfer-out).",
    "Phase 3 (scale-up): add cross-lingual checks using English resources (Argotario, LOGIC, "
    "SemEval-2020 propaganda) via multilingual encoders; report macro-F1 with harmonised "
    "projection tables only.",
    "Phase 4 (release): pre-register any schema-repair or label-projection rules before "
    "official external-validation numbers are reported.",
)


def render_compatibility_markdown(datasets: Iterable[ExternalDataset] | None = None) -> str:
    rows = list(datasets or EXTERNAL_DATASETS)
    lines = [
        "# Benchmark Compatibility Matrix",
        "",
        "Compatibility of SPDB with external fallacy and persuasion datasets.",
        "",
        "**Status:** planning assessment only. No models have been trained or evaluated.",
        "",
        "| Dataset | Direct comparison | Transfer learning | External validation | Cross-lingual | Notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for dataset in rows:
        scores = dataset.compatibility
        lines.append(
            f"| {dataset.name} | {scores.direct_comparison} | {scores.transfer_learning} | "
            f"{scores.external_validation} | {scores.cross_lingual} | {scores.notes} |"
        )
    lines.extend(
        [
            "",
            "## Evaluation questions",
            "",
            "| Question | Interpretation |",
            "| --- | --- |",
            "| Can SPDB be compared directly? | Requires harmonised units and label projection; "
            " feasible for FallacyES-Political at MEDIUM, most English sets at LOW. |",
            "| Can transfer learning be tested? | YES for Spanish FallacyES resources (HIGH); "
            "English sets at MEDIUM with multilingual models. |",
            "| Can external validation be performed? | Planned after SPDB adjudicated gold exists; "
            "FallacyES-Political is the primary candidate (HIGH). |",
            "| Can cross-lingual validation be performed? | MEDIUM--HIGH using English fallacy "
            "corpora and projection tables; not a substitute for Spanish human gold. |",
            "",
            "## Recommended validation roadmap",
            "",
        ]
    )
    for index, phase in enumerate(ROADMAP_PHASES, start=1):
        lines.append(f"{index}. {phase}")
    lines.extend(["", "## Ranking summary (planning)", ""])
    lines.extend(_ranking_summary_lines(rows))
    lines.append("")
    return "\n".join(lines) + "\n"


def _ranking_summary_lines(datasets: List[ExternalDataset]) -> List[str]:
    by_external = sorted(
        datasets,
        key=lambda d: _score_rank(d.compatibility.external_validation),
        reverse=True,
    )
    spanish_political = [
        d for d in datasets if "Spanish" in d.language and "political" in d.domain.lower()
    ]
    cross_lingual = sorted(
        datasets,
        key=lambda d: _score_rank(d.compatibility.cross_lingual),
        reverse=True,
    )
    lines = [
        f"- **Strongest overall external-validation candidate:** `{by_external[0].dataset_id}` "
        f"({by_external[0].name}).",
    ]
    if spanish_political:
        lines.append(
            f"- **Strongest Spanish political-discourse candidate:** "
            f"`{spanish_political[0].dataset_id}` ({spanish_political[0].name})."
        )
    lines.append(
        f"- **Strongest cross-lingual planning candidate:** "
        f"`{cross_lingual[0].dataset_id}` ({cross_lingual[0].name})."
    )
    lines.append(
        "- **Important constraint:** external validation supports construct positioning; "
        "it does not replace SPDB human pilot adjudication."
    )
    return lines


def _score_rank(level: str) -> int:
    return {"LOW": 1, "MEDIUM": 2, "HIGH": 3}.get(level, 0)


def write_compatibility_report(output_path: Path | None = None) -> Path:
    path = output_path or DEFAULT_REPORT_DIR / "benchmark_compatibility.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_compatibility_markdown(), encoding="utf-8")
    return path


def write_validation_roadmap(output_path: Path | None = None) -> Path:
    path = output_path or DEFAULT_REPORT_DIR / "validation_roadmap.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    body = ["# External Validation Roadmap", "", *ROADMAP_PHASES, ""]
    path.write_text("\n".join(f"- {item}" if not item.startswith("Phase") else f"## {item}" for item in body), encoding="utf-8")
    return path
