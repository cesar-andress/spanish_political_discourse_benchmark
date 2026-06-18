"""Human ceiling metrics for Human-vs-LLM comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Sequence

from analysis.human_vs_llm.gold import GoldSet
from analysis.human_vs_llm.io import HumanAnnotationSet
from analysis.human_vs_llm.metrics import classification_scores, mean_pairwise_kappa


@dataclass(frozen=True)
class HumanCeiling:
    pairwise_kappa: float
    annotator_vs_majority: Dict[str, float]
    annotator_vs_adjudicated: Dict[str, float] | None
    majority_macro_f1: float


def _annotator_vs_reference(
    annotator_labels: Sequence[str],
    reference_labels: Sequence[str],
) -> float:
    scores = classification_scores(reference_labels, annotator_labels)
    return scores.macro_f1


def compute_human_ceiling(
    human: HumanAnnotationSet,
    gold: GoldSet,
    *,
    adjudicated_gold: GoldSet | None = None,
) -> HumanCeiling:
    label_matrix = [
        [human.labels[i][unit_id] for unit_id in human.unit_ids]
        for i in range(len(human.labels))
    ]
    pairwise = mean_pairwise_kappa(label_matrix)

    eval_units = gold.evaluable_units
    unit_ids = [unit.unit_id for unit in eval_units]
    gold_labels = [unit.gold_label for unit in eval_units if unit.gold_label]

    vs_majority: Dict[str, float] = {}
    for i, name in enumerate(human.annotator_names):
        pred = [human.labels[i][unit_id] for unit_id in unit_ids]
        vs_majority[name] = _annotator_vs_reference(pred, gold_labels)

    vs_adjudicated: Dict[str, float] | None = None
    if adjudicated_gold is not None:
        adj_units = adjudicated_gold.evaluable_units
        adj_ids = [unit.unit_id for unit in adj_units]
        adj_labels = [unit.gold_label for unit in adj_units if unit.gold_label]
        vs_adjudicated = {}
        for i, name in enumerate(human.annotator_names):
            pred = [human.labels[i][unit_id] for unit_id in adj_ids]
            vs_adjudicated[name] = _annotator_vs_reference(pred, adj_labels)

    majority_scores = classification_scores(gold_labels, gold_labels)
    return HumanCeiling(
        pairwise_kappa=pairwise,
        annotator_vs_majority=vs_majority,
        annotator_vs_adjudicated=vs_adjudicated,
        majority_macro_f1=majority_scores.macro_f1,
    )


def human_ceiling_gap(system_macro_f1: float, ceiling: HumanCeiling) -> float:
    if ceiling.majority_macro_f1 != ceiling.majority_macro_f1:
        return float("nan")
    return ceiling.majority_macro_f1 - system_macro_f1
