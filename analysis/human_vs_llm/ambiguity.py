"""Ambiguity analysis for Human-vs-LLM comparison."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from analysis.human_vs_llm.gold import GoldSet
from analysis.human_vs_llm.io import HumanAnnotationSet, LLMAnnotationSet, llm_label


@dataclass(frozen=True)
class AmbiguityReport:
    full_split_units: List[str]
    llm_agrees_one_human_not_gold: List[Dict[str, object]]
    unanimous_human_llm_fail: List[Dict[str, object]]
    human_disagree_llm_picks_side: List[Dict[str, object]]


def analyze_ambiguity(
    human: HumanAnnotationSet,
    gold: GoldSet,
    llm: LLMAnnotationSet,
) -> AmbiguityReport:
    full_split = [
        unit.unit_id
        for unit in gold.units
        if unit.exclusion_reason == "full_split"
    ]

    llm_one_human: List[Dict[str, object]] = []
    unanimous_fail: List[Dict[str, object]] = []
    disagree_pick: List[Dict[str, object]] = []

    gold_by_id = {unit.unit_id: unit for unit in gold.units}

    for unit_id in human.unit_ids:
        gold_unit = gold_by_id.get(unit_id)
        if gold_unit is None:
            continue
        human_labels = list(gold_unit.human_labels)
        record = llm.records_by_id.get(unit_id, {})
        pred = llm_label(record)
        gold_label = gold_unit.gold_label

        unique_human = set(label for label in human_labels if label)

        if len(unique_human) == 1 and gold_label and pred and pred != gold_label:
            unanimous_fail.append(
                {
                    "unit_id": unit_id,
                    "human_label": next(iter(unique_human)),
                    "llm_label": pred,
                }
            )

        if len(unique_human) > 1 and pred and pred in unique_human:
            if gold_label and pred != gold_label:
                llm_one_human.append(
                    {
                        "unit_id": unit_id,
                        "human_labels": human_labels,
                        "gold_label": gold_label,
                        "llm_label": pred,
                    }
                )
            if gold_label is None or gold_unit.ambiguous:
                disagree_pick.append(
                    {
                        "unit_id": unit_id,
                        "human_labels": human_labels,
                        "llm_label": pred,
                    }
                )

    return AmbiguityReport(
        full_split_units=full_split,
        llm_agrees_one_human_not_gold=llm_one_human,
        unanimous_human_llm_fail=unanimous_fail,
        human_disagree_llm_picks_side=disagree_pick,
    )
