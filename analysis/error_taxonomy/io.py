"""Collect human disagreements and model prediction errors."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set

from analysis.error_taxonomy.constants import ERROR_CLUSTERS, ErrorCluster, PF_COLUMN
from analysis.human_vs_llm.gold import GoldSet, build_gold
from analysis.human_vs_llm.io import (
    HumanAnnotationSet,
    LLMAnnotationSet,
    _read_csv,
    human_files_available,
    load_human_annotations,
    load_llm_annotations,
    llm_label,
)


@dataclass(frozen=True)
class LabelTransition:
    unit_id: str
    source: str
    target: str
    text: str = ""
    speaker_party: str = ""
    source_type: str = "human_disagreement"
    model_name: str = ""


@dataclass
class ErrorInventory:
    human_transitions: List[LabelTransition] = field(default_factory=list)
    model_transitions: List[LabelTransition] = field(default_factory=list)
    unit_text: Dict[str, str] = field(default_factory=dict)
    unit_party: Dict[str, str] = field(default_factory=dict)
    n_human_disagreement_units: int = 0
    n_model_errors: int = 0
    n_units_human: int = 0
    n_units_model: int = 0
    gold_strategy: str = "majority_vote"
    model_names: List[str] = field(default_factory=list)


def _metadata_from_rows(rows_by_id: Dict[str, Dict[str, str]], unit_id: str) -> tuple[str, str]:
    row = rows_by_id.get(unit_id, {})
    return (row.get("text") or "").strip(), (row.get("speaker_party") or "").strip()


def _cluster_for_pair(left: str, right: str) -> ErrorCluster | None:
    if left == right:
        return None
    for cluster in ERROR_CLUSTERS:
        if cluster.matches_pair(left, right):
            return cluster
    return None


def collect_human_disagreements(human: HumanAnnotationSet) -> tuple[List[LabelTransition], int, Set[str]]:
    transitions: List[LabelTransition] = []
    disagreement_units: Set[str] = set()
    metadata_rows: Dict[str, Dict[str, str]] = {}
    for path in human.annotator_paths:
        for row in _read_csv(path):
            unit_id = (row.get("unit_id") or "").strip()
            if unit_id:
                metadata_rows[unit_id] = row

    for unit_id in human.unit_ids:
        labels = [human.labels[i][unit_id] for i in range(len(human.labels))]
        unique = {label for label in labels if label}
        if len(unique) <= 1:
            continue
        disagreement_units.add(unit_id)
        text, party = _metadata_from_rows(metadata_rows, unit_id)

        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                left, right = labels[i], labels[j]
                if left == right or not left or not right:
                    continue
                if _cluster_for_pair(left, right) is None:
                    continue
                transitions.append(
                    LabelTransition(
                        unit_id=unit_id,
                        source=left,
                        target=right,
                        text=text,
                        speaker_party=party,
                        source_type="human_disagreement",
                    )
                )
                transitions.append(
                    LabelTransition(
                        unit_id=unit_id,
                        source=right,
                        target=left,
                        text=text,
                        speaker_party=party,
                        source_type="human_disagreement",
                    )
                )
    return transitions, len(disagreement_units), disagreement_units


def collect_model_errors(
    gold: GoldSet,
    llm_files: Sequence[Path],
    *,
    unit_text: Dict[str, str],
    unit_party: Dict[str, str],
) -> tuple[List[LabelTransition], int, List[str]]:
    transitions: List[LabelTransition] = []
    model_names: List[str] = []
    error_count = 0

    gold_by_id = {unit.unit_id: unit for unit in gold.units if unit.gold_label}

    for path in llm_files:
        llm: LLMAnnotationSet = load_llm_annotations(path)
        model_names.append(llm.model_name)
        for unit_id, gold_unit in gold_by_id.items():
            if gold_unit.excluded:
                continue
            gold_label = gold_unit.gold_label
            if not gold_label:
                continue
            record = llm.records_by_id.get(unit_id, {})
            pred = llm_label(record)
            if pred is None or pred == gold_label:
                continue
            error_count += 1
            if _cluster_for_pair(gold_label, pred) is None:
                continue
            transitions.append(
                LabelTransition(
                    unit_id=unit_id,
                    source=gold_label,
                    target=pred,
                    text=unit_text.get(unit_id, ""),
                    speaker_party=unit_party.get(unit_id, ""),
                    source_type="model_error",
                    model_name=llm.model_name,
                )
            )
    return transitions, error_count, model_names


def build_inventory(
    *,
    annotator_paths: Sequence[Path],
    adjudicated_path: Path | None,
    llm_paths: Sequence[Path],
    gold_strategy: str = "majority_vote",
) -> ErrorInventory | None:
    available, missing = human_files_available(annotator_paths)
    if not available:
        return None

    human = load_human_annotations(annotator_paths)
    if gold_strategy == "adjudicated_file":
        if not adjudicated_path or not adjudicated_path.exists():
            return None
        gold = build_gold(human, "adjudicated_file", adjudicated_path=adjudicated_path)
    else:
        gold = build_gold(
            human,
            gold_strategy,  # type: ignore[arg-type]
            adjudicated_path=adjudicated_path or Path("_missing_adjudicated.csv"),
        )

    unit_text: Dict[str, str] = {}
    unit_party: Dict[str, str] = {}
    for path in annotator_paths:
        for row in _read_csv(path):
            unit_id = (row.get("unit_id") or "").strip()
            if unit_id and unit_id not in unit_text:
                unit_text[unit_id] = (row.get("text") or "").strip()
                unit_party[unit_id] = (row.get("speaker_party") or "").strip()

    human_transitions, n_disagreement_units, _ = collect_human_disagreements(human)
    model_transitions, n_model_errors, model_names = collect_model_errors(
        gold,
        llm_paths,
        unit_text=unit_text,
        unit_party=unit_party,
    )

    inventory = ErrorInventory(
        human_transitions=human_transitions,
        model_transitions=model_transitions,
        unit_text=unit_text,
        unit_party=unit_party,
        n_human_disagreement_units=n_disagreement_units,
        n_model_errors=n_model_errors,
        n_units_human=len(human.unit_ids),
        n_units_model=len([unit for unit in gold.units if unit.gold_label and not unit.excluded]),
        gold_strategy=gold_strategy,
        model_names=model_names,
    )
    return inventory


def aggregate_confusion(transitions: Iterable[LabelTransition]) -> Dict[str, Dict[str, int]]:
    matrix: Dict[str, Dict[str, int]] = {}
    for item in transitions:
        matrix.setdefault(item.source, {})
        matrix[item.source][item.target] = matrix[item.source].get(item.target, 0) + 1
    return matrix
