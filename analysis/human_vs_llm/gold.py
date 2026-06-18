"""Gold label construction for Human-vs-LLM comparison."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.human_vs_llm.constants import GoldStrategy
from analysis.human_vs_llm.io import HumanAnnotationSet, load_adjudicated_labels


@dataclass(frozen=True)
class GoldUnit:
    unit_id: str
    gold_label: str | None
    ambiguous: bool
    human_labels: tuple[str, ...]
    excluded: bool
    exclusion_reason: str


@dataclass(frozen=True)
class GoldSet:
    strategy: GoldStrategy
    units: List[GoldUnit]

    @property
    def evaluable_units(self) -> List[GoldUnit]:
        return [unit for unit in self.units if unit.gold_label and not unit.excluded]

    def gold_by_id(self) -> Dict[str, str]:
        return {unit.unit_id: unit.gold_label for unit in self.evaluable_units if unit.gold_label}


def _human_labels_for_unit(human: HumanAnnotationSet, unit_id: str) -> tuple[str, ...]:
    return tuple(human.labels[i][unit_id] for i in range(len(human.labels)))


def build_majority_vote_gold(human: HumanAnnotationSet) -> GoldSet:
    units: List[GoldUnit] = []
    for unit_id in human.unit_ids:
        labels = _human_labels_for_unit(human, unit_id)
        filled = [label for label in labels if label]
        if len(filled) < len(labels):
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=None,
                    ambiguous=True,
                    human_labels=labels,
                    excluded=True,
                    exclusion_reason="incomplete_human_labels",
                )
            )
            continue
        counts = Counter(labels)
        top_label, top_count = counts.most_common(1)[0]
        if len(counts) == len(labels) and top_count == 1:
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=None,
                    ambiguous=True,
                    human_labels=labels,
                    excluded=False,
                    exclusion_reason="full_split",
                )
            )
            continue
        if top_count >= 2:
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=top_label,
                    ambiguous=False,
                    human_labels=labels,
                    excluded=False,
                    exclusion_reason="",
                )
            )
        else:
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=None,
                    ambiguous=True,
                    human_labels=labels,
                    excluded=False,
                    exclusion_reason="no_majority",
                )
            )
    return GoldSet(strategy="majority_vote", units=units)


def build_unanimous_gold(human: HumanAnnotationSet) -> GoldSet:
    units: List[GoldUnit] = []
    for unit_id in human.unit_ids:
        labels = _human_labels_for_unit(human, unit_id)
        filled = [label for label in labels if label]
        if len(filled) < len(labels) or len(set(labels)) != 1:
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=None,
                    ambiguous=len(set(filled)) > 1 if filled else True,
                    human_labels=labels,
                    excluded=True,
                    exclusion_reason="not_unanimous",
                )
            )
            continue
        units.append(
            GoldUnit(
                unit_id=unit_id,
                gold_label=labels[0],
                ambiguous=False,
                human_labels=labels,
                excluded=False,
                exclusion_reason="",
            )
        )
    return GoldSet(strategy="unanimous_only", units=units)


def build_adjudicated_gold(human: HumanAnnotationSet, adjudicated_path: Path) -> GoldSet:
    adjudicated = load_adjudicated_labels(adjudicated_path)
    if not adjudicated:
        raise FileNotFoundError(f"Adjudicated file not found or empty: {adjudicated_path}")
    units: List[GoldUnit] = []
    for unit_id in human.unit_ids:
        labels = _human_labels_for_unit(human, unit_id)
        gold = adjudicated.get(unit_id)
        if not gold:
            units.append(
                GoldUnit(
                    unit_id=unit_id,
                    gold_label=None,
                    ambiguous=True,
                    human_labels=labels,
                    excluded=True,
                    exclusion_reason="missing_adjudication",
                )
            )
            continue
        units.append(
            GoldUnit(
                unit_id=unit_id,
                gold_label=gold,
                ambiguous=False,
                human_labels=labels,
                excluded=False,
                exclusion_reason="",
            )
        )
    return GoldSet(strategy="adjudicated_file", units=units)


def build_gold(
    human: HumanAnnotationSet,
    strategy: GoldStrategy,
    *,
    adjudicated_path: Path,
) -> GoldSet:
    if strategy == "majority_vote":
        return build_majority_vote_gold(human)
    if strategy == "unanimous_only":
        return build_unanimous_gold(human)
    if strategy == "adjudicated_file":
        return build_adjudicated_gold(human, adjudicated_path)
    raise ValueError(f"Unknown gold strategy: {strategy}")
