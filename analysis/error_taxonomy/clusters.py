"""Cluster human disagreements and model errors into publication taxonomy."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Set

from analysis.error_taxonomy.constants import ERROR_CLUSTERS, ErrorCluster
from analysis.error_taxonomy.io import ErrorInventory, LabelTransition


@dataclass(frozen=True)
class ClusterStats:
    cluster: ErrorCluster
    human_count: int
    model_count: int
    human_units: int
    model_units: int
    directional: Dict[tuple[str, str], int]
    human_directional: Dict[tuple[str, str], int]
    model_directional: Dict[tuple[str, str], int]
    exemplars: List[LabelTransition]


@dataclass(frozen=True)
class TaxonomyResult:
    clusters: List[ClusterStats]
    total_human_clustered: int
    total_model_clustered: int
    total_human_transitions: int
    total_model_transitions: int
    unclustered_human: int
    unclustered_model: int
    model_recapitulation_rate: float
    inventory: ErrorInventory


def _directional_counts(
    transitions: Sequence[LabelTransition],
    cluster: ErrorCluster,
) -> Dict[tuple[str, str], int]:
    counts: Counter[tuple[str, str]] = Counter()
    for item in transitions:
        key = cluster.canonical_key(item.source, item.target)
        if key is None:
            continue
        counts[key] += 1
    return dict(counts)


def _unique_units(transitions: Sequence[LabelTransition], cluster: ErrorCluster) -> Set[str]:
    units: Set[str] = set()
    for item in transitions:
        if cluster.matches_pair(item.source, item.target):
            units.add(item.unit_id)
    return units


def _exemplars(
    human: Sequence[LabelTransition],
    model: Sequence[LabelTransition],
    cluster: ErrorCluster,
    *,
    limit: int = 5,
) -> List[LabelTransition]:
    seen: Set[str] = set()
    rows: List[LabelTransition] = []
    for item in list(human) + list(model):
        if item.unit_id in seen:
            continue
        if not cluster.matches_pair(item.source, item.target):
            continue
        seen.add(item.unit_id)
        rows.append(item)
        if len(rows) >= limit:
            break
    return rows


def analyze_taxonomy(inventory: ErrorInventory) -> TaxonomyResult:
    human = inventory.human_transitions
    model = inventory.model_transitions

    total_human_clustered = sum(
        1 for item in human if _cluster_for(item.source, item.target) is not None
    )
    total_model_clustered = sum(
        1 for item in model if _cluster_for(item.source, item.target) is not None
    )

    clusters: List[ClusterStats] = []
    for cluster in ERROR_CLUSTERS:
        human_dir = _directional_counts(human, cluster)
        model_dir = _directional_counts(model, cluster)
        combined_dir: Dict[tuple[str, str], int] = defaultdict(int)
        for key, value in human_dir.items():
            combined_dir[key] += value
        for key, value in model_dir.items():
            combined_dir[key] += value

        human_count = sum(human_dir.values())
        model_count = sum(model_dir.values())
        clusters.append(
            ClusterStats(
                cluster=cluster,
                human_count=human_count,
                model_count=model_count,
                human_units=len(_unique_units(human, cluster)),
                model_units=len(_unique_units(model, cluster)),
                directional=dict(combined_dir),
                human_directional=human_dir,
                model_directional=model_dir,
                exemplars=_exemplars(human, model, cluster),
            )
        )

    model_cluster_units = {
        item.unit_id
        for item in model
        if _cluster_for(item.source, item.target) is not None
    }
    human_cluster_units = {
        item.unit_id
        for item in human
        if _cluster_for(item.source, item.target) is not None
    }
    overlap = model_cluster_units & human_cluster_units
    recapitulation = (
        len(overlap) / len(model_cluster_units) if model_cluster_units else float("nan")
    )

    return TaxonomyResult(
        clusters=clusters,
        total_human_clustered=total_human_clustered,
        total_model_clustered=total_model_clustered,
        total_human_transitions=len(human),
        total_model_transitions=len(model),
        unclustered_human=len(human) - total_human_clustered,
        unclustered_model=len(model) - total_model_clustered,
        model_recapitulation_rate=recapitulation,
        inventory=inventory,
    )


def _cluster_for(left: str, right: str) -> ErrorCluster | None:
    for cluster in ERROR_CLUSTERS:
        if cluster.matches_pair(left, right):
            return cluster
    return None
