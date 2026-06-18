"""Pipeline orchestration for Human-vs-LLM comparison."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.human_vs_llm.ambiguity import AmbiguityReport, analyze_ambiguity
from analysis.human_vs_llm.ceiling import HumanCeiling, compute_human_ceiling
from analysis.human_vs_llm.constants import (
    DEFAULT_ADJUDICATED,
    DEFAULT_ANNOTATORS,
    DEFAULT_LLM_DIR,
    DEFAULT_OUTPUT_DIR,
    GoldStrategy,
)
from analysis.human_vs_llm.gold import GoldSet, build_gold
from analysis.human_vs_llm.io import (
    HumanAnnotationSet,
    LLMAnnotationSet,
    discover_llm_jsonl_files,
    human_files_available,
    load_human_annotations,
    load_llm_annotations,
    llm_label,
)
from analysis.human_vs_llm.metrics import classification_scores
from analysis.human_vs_llm.report import (
    SystemResult,
    human_ceiling_gap,
    write_confusion_matrices,
    write_latex_table,
    write_markdown_report,
    write_pending_readme,
    write_per_class_scores_csv,
    write_system_scores_csv,
)


@dataclass(frozen=True)
class PipelineResult:
    pending: bool
    output_dir: Path
    gold: GoldSet | None
    system_results: List[SystemResult]
    ceiling: HumanCeiling | None
    ambiguity_reports: Dict[str, AmbiguityReport]


def _compare_llm_to_gold(llm: LLMAnnotationSet, gold: GoldSet) -> SystemResult:
    eval_units = gold.evaluable_units
    y_true = [unit.gold_label for unit in eval_units if unit.gold_label]
    unit_ids = [unit.unit_id for unit in eval_units if unit.gold_label]

    y_pred: List[str | None] = []
    invalid_flags: List[bool] = []
    for unit_id in unit_ids:
        record = llm.records_by_id.get(unit_id, {})
        y_pred.append(llm_label(record))
        invalid_flags.append(bool(record.get("_parse_error")))

    scores = classification_scores(y_true, y_pred, invalid_flags=invalid_flags)
    return SystemResult(
        system_name=llm.model_name,
        scores=scores,
        ceiling_gap=float("nan"),
    )


def run_pipeline(
    *,
    annotator_paths: Sequence[Path] = DEFAULT_ANNOTATORS,
    adjudicated_path: Path = DEFAULT_ADJUDICATED,
    llm_dir: Path = DEFAULT_LLM_DIR,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    gold_strategy: GoldStrategy = "majority_vote",
    llm_paths: Sequence[Path] | None = None,
) -> PipelineResult:
    available, missing = human_files_available(annotator_paths)
    if not available:
        write_pending_readme(output_dir, missing)
        return PipelineResult(
            pending=True,
            output_dir=output_dir,
            gold=None,
            system_results=[],
            ceiling=None,
            ambiguity_reports={},
        )

    human = load_human_annotations(annotator_paths)
    gold = build_gold(human, gold_strategy, adjudicated_path=adjudicated_path)

    adjudicated_gold = None
    if adjudicated_path.exists() and gold_strategy != "adjudicated_file":
        adjudicated_gold = build_gold(human, "adjudicated_file", adjudicated_path=adjudicated_path)

    ceiling = compute_human_ceiling(human, gold, adjudicated_gold=adjudicated_gold)

    resolved_llm_paths = list(llm_paths) if llm_paths else discover_llm_jsonl_files(llm_dir)
    llm_sets = [load_llm_annotations(path) for path in resolved_llm_paths]

    system_results: List[SystemResult] = []
    ambiguity_reports: Dict[str, AmbiguityReport] = {}
    for llm in llm_sets:
        result = _compare_llm_to_gold(llm, gold)
        gap = human_ceiling_gap(result.scores.macro_f1, ceiling)
        system_results.append(
            SystemResult(
                system_name=result.system_name,
                scores=result.scores,
                ceiling_gap=gap,
            )
        )
        ambiguity_reports[llm.model_name] = analyze_ambiguity(human, gold, llm)

    output_dir.mkdir(parents=True, exist_ok=True)
    write_system_scores_csv(system_results, output_dir / "system_scores.csv")
    write_per_class_scores_csv(system_results, output_dir / "per_class_scores.csv")
    write_confusion_matrices(system_results, output_dir / "confusion_matrices")
    write_markdown_report(
        output_path=output_dir / "human_vs_llm_report.md",
        gold=gold,
        results=system_results,
        ceiling=ceiling,
        ambiguity_reports=ambiguity_reports,
        llm_paths=resolved_llm_paths,
    )
    write_latex_table(system_results, output_dir / "human_vs_llm_table.tex")

    return PipelineResult(
        pending=False,
        output_dir=output_dir,
        gold=gold,
        system_results=system_results,
        ceiling=ceiling,
        ambiguity_reports=ambiguity_reports,
    )
