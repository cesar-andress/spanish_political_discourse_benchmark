"""Report generation for Human-vs-LLM comparison."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.human_vs_llm.ambiguity import AmbiguityReport
from analysis.human_vs_llm.ceiling import HumanCeiling, human_ceiling_gap
from analysis.human_vs_llm.constants import DEFAULT_ANNOTATORS, DEFAULT_ADJUDICATED, GoldStrategy
from analysis.human_vs_llm.gold import GoldSet
from analysis.human_vs_llm.metrics import ClassificationScores


@dataclass(frozen=True)
class SystemResult:
    system_name: str
    scores: ClassificationScores
    ceiling_gap: float


def write_pending_readme(output_dir: Path, missing_files: Sequence[str]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / "README_PENDING.md"
    lines = [
        "# Human-vs-LLM analysis pending",
        "",
        "Human annotation files are not yet available. Run this analysis again once the following files exist:",
        "",
    ]
    for item in missing_files:
        lines.append(f"- `{item}`")
    lines.extend(
        [
            "",
            "Optional adjudicated gold:",
            "",
            f"- `{DEFAULT_ADJUDICATED}`",
            "",
            "Expected LLM outputs (one per model):",
            "",
            "- `data/experiments/llm_annotations/{MODEL_NAME}_pilot_100.jsonl`",
            "",
            "When ready:",
            "",
            "```bash",
            "make human-vs-llm",
            "```",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def write_system_scores_csv(results: Sequence[SystemResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "system",
                "accuracy",
                "macro_f1",
                "weighted_f1",
                "human_ceiling_gap",
                "n_evaluated",
                "abstention_rate",
                "invalid_rate",
            ],
        )
        writer.writeheader()
        for result in results:
            writer.writerow(
                {
                    "system": result.system_name,
                    "accuracy": f"{result.scores.accuracy:.4f}",
                    "macro_f1": f"{result.scores.macro_f1:.4f}",
                    "weighted_f1": f"{result.scores.weighted_f1:.4f}",
                    "human_ceiling_gap": f"{result.ceiling_gap:.4f}",
                    "n_evaluated": result.scores.n_evaluated,
                    "abstention_rate": f"{result.scores.abstention_rate:.4f}",
                    "invalid_rate": f"{result.scores.invalid_rate:.4f}",
                }
            )


def write_per_class_scores_csv(
    results: Sequence[SystemResult],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["system", "label", "precision", "recall", "f1", "support"],
        )
        writer.writeheader()
        for result in results:
            for label, metrics in sorted(result.scores.per_class.items()):
                writer.writerow(
                    {
                        "system": result.system_name,
                        "label": label,
                        "precision": f"{metrics['precision']:.4f}",
                        "recall": f"{metrics['recall']:.4f}",
                        "f1": f"{metrics['f1']:.4f}",
                        "support": int(metrics["support"]),
                    }
                )


def write_confusion_matrices(results: Sequence[SystemResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    for result in results:
        path = output_dir / f"{result.system_name}_confusion.json"
        payload = {
            "system": result.system_name,
            "labels": result.scores.labels,
            "matrix": result.scores.confusion,
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_markdown_report(
    *,
    output_path: Path,
    gold: GoldSet,
    results: Sequence[SystemResult],
    ceiling: HumanCeiling,
    ambiguity_reports: Dict[str, AmbiguityReport],
    llm_paths: Sequence[Path],
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Human-vs-LLM comparison report",
        "",
        f"Gold strategy: `{gold.strategy}`",
        f"Evaluable units: {len(gold.evaluable_units)} / {len(gold.units)}",
        "",
        "## System scores",
        "",
        "| System | Accuracy | Macro-F1 | Weighted-F1 | Human ceiling gap |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for result in results:
        lines.append(
            f"| {result.system_name} | {result.scores.accuracy:.4f} | "
            f"{result.scores.macro_f1:.4f} | {result.scores.weighted_f1:.4f} | "
            f"{result.ceiling_gap:.4f} |"
        )

    lines.extend(
        [
            "",
            "## Human ceiling",
            "",
            f"- Pairwise Cohen's kappa (mean): {ceiling.pairwise_kappa:.4f}",
            f"- Majority-vote macro-F1 ceiling: {ceiling.majority_macro_f1:.4f}",
            "",
            "### Annotator vs majority gold",
            "",
        ]
    )
    for name, score in ceiling.annotator_vs_majority.items():
        lines.append(f"- `{name}`: macro-F1 = {score:.4f}")

    if ceiling.annotator_vs_adjudicated:
        lines.extend(["", "### Annotator vs adjudicated gold", ""])
        for name, score in ceiling.annotator_vs_adjudicated.items():
            lines.append(f"- `{name}`: macro-F1 = {score:.4f}")

    lines.extend(["", "## Ambiguity analysis", ""])
    for system, report in ambiguity_reports.items():
        lines.extend(
            [
                f"### {system}",
                "",
                f"- Full-split human disagreement: {len(report.full_split_units)}",
                f"- LLM agrees with one human but not gold: {len(report.llm_agrees_one_human_not_gold)}",
                f"- Unanimous human / LLM error: {len(report.unanimous_human_llm_fail)}",
                f"- Human disagree, LLM picks a side: {len(report.human_disagree_llm_picks_side)}",
                "",
            ]
        )

    lines.extend(["## LLM inputs", ""])
    for path in llm_paths:
        lines.append(f"- `{path}`")

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_latex_table(results: Sequence[SystemResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "% Auto-generated Human-vs-LLM comparison table",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Human-vs-LLM pragmatic function classification on the pilot set. "
        "Human ceiling gap is majority-vote macro-F1 minus system macro-F1.}",
        "\\label{tab:human-vs-llm}",
        "\\begin{tabular}{lrrr}",
        "\\toprule",
        "System & Accuracy & Macro-F1 & Human ceiling gap \\\\",
        "\\midrule",
    ]
    for result in results:
        name = result.system_name.replace("_", "\\_")
        lines.append(
            f"{name} & {result.scores.accuracy:.3f} & "
            f"{result.scores.macro_f1:.3f} & {result.ceiling_gap:.3f} \\\\"
        )
    lines.extend(["\\bottomrule", "\\end{tabular}", "\\end{table}", ""])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
