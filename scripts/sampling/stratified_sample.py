#!/usr/bin/env python3
"""Stratified discourse-unit sampling with speaker round-robin caps."""

from __future__ import annotations

import hashlib
import random
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, DefaultDict, Dict, List, Sequence, Tuple

StratumKey = Tuple[str, str]


@dataclass
class StratifiedSampleResult:
    units: List[Dict[str, Any]]
    requested_n: int
    seed: int
    max_per_speaker: int
    stratum_quotas: Dict[StratumKey, int]
    stratum_selected: Dict[StratumKey, int]
    party_selected: Counter[str] = field(default_factory=Counter)
    year_selected: Counter[str] = field(default_factory=Counter)
    speaker_selected: Counter[str] = field(default_factory=Counter)
    pool_total: int = 0
    shortfall_reason: str | None = None


def _year(date_str: str) -> str:
    if date_str and len(date_str) >= 4:
        return date_str[:4]
    return "unknown"


def _unit_stratum(unit: Dict[str, Any]) -> StratumKey:
    meta = unit.get("metadata") or {}
    party = str(meta.get("speaker_party") or "unknown")
    year = _year(str(meta.get("date") or ""))
    return party, year


def _speaker_name(unit: Dict[str, Any]) -> str:
    meta = unit.get("metadata") or {}
    return str(meta.get("speaker_name") or "unknown")


def _deterministic_shuffle(items: List[Any], *, seed: int, label: str) -> None:
    digest = hashlib.sha256(f"{seed}:{label}".encode()).hexdigest()
    local_seed = int(digest[:16], 16)
    rng = random.Random(local_seed)
    rng.shuffle(items)


def allocate_quotas(stratum_sizes: Dict[StratumKey, int], n: int) -> Dict[StratumKey, int]:
    if n <= 0:
        return {key: 0 for key in stratum_sizes}
    total = sum(stratum_sizes.values())
    if total == 0:
        return {key: 0 for key in stratum_sizes}

    keys = sorted(stratum_sizes)
    quotas: Dict[StratumKey, int] = {}
    remainders: List[Tuple[float, StratumKey]] = []
    allocated = 0
    for key in keys:
        exact = n * stratum_sizes[key] / total
        base = int(exact)
        quotas[key] = base
        allocated += base
        remainders.append((exact - base, key))

    for _, key in sorted(remainders, key=lambda item: (-item[0], item[1])):
        if allocated >= n:
            break
        quotas[key] += 1
        allocated += 1
    return quotas


def _build_pools(
    units: Sequence[Dict[str, Any]], *, seed: int
) -> Tuple[DefaultDict[StratumKey, DefaultDict[str, List[Dict[str, Any]]]], Counter]:
    pools: DefaultDict[StratumKey, DefaultDict[str, List[Dict[str, Any]]]] = defaultdict(
        lambda: defaultdict(list)
    )
    stratum_sizes: Counter[StratumKey] = Counter()
    for unit in units:
        key = _unit_stratum(unit)
        speaker = _speaker_name(unit)
        pools[key][speaker].append(unit)
        stratum_sizes[key] += 1

    for key in sorted(pools):
        for speaker in sorted(pools[key]):
            _deterministic_shuffle(pools[key][speaker], seed=seed, label=f"{key}:{speaker}")
    return pools, stratum_sizes


def _pick_one_round_robin(
    pools: DefaultDict[str, List[Dict[str, Any]]],
    *,
    speaker_counts: Counter[str],
    speaker_indices: Dict[str, int],
    max_per_speaker: int,
    selected_ids: set[str],
    stratum_round: int,
) -> Dict[str, Any] | None:
    speakers = sorted(pools)
    if not speakers:
        return None

    start = stratum_round % len(speakers)
    for offset in range(len(speakers)):
        speaker = speakers[(start + offset) % len(speakers)]
        if speaker_counts[speaker] >= max_per_speaker:
            continue
        pool = pools[speaker]
        idx = speaker_indices[speaker]
        while idx < len(pool):
            unit = pool[idx]
            idx += 1
            unit_id = str(unit.get("unit_id") or id(unit))
            if unit_id in selected_ids:
                continue
            speaker_indices[speaker] = idx
            return unit
        speaker_indices[speaker] = idx
    return None


def _speaker_capacity(units: Sequence[Dict[str, Any]], max_per_speaker: int) -> int:
    by_speaker: Counter[str] = Counter()
    for unit in units:
        by_speaker[_speaker_name(unit)] += 1
    return sum(min(max_per_speaker, count) for count in by_speaker.values())


def _interleaved_stratum_order(quotas: Dict[StratumKey, int]) -> List[StratumKey]:
    parties = sorted({key[0] for key in quotas})
    keys_by_party: Dict[str, List[StratumKey]] = {
        party_name: sorted(key for key in quotas if key[0] == party_name)
        for party_name in parties
    }
    order: List[StratumKey] = []
    pos = 0
    while True:
        added = False
        for party in parties:
            keys = keys_by_party[party]
            if pos < len(keys):
                order.append(keys[pos])
                added = True
        if not added:
            break
        pos += 1
    return order


def stratified_sample_units(
    units: Sequence[Dict[str, Any]],
    *,
    n: int,
    seed: int,
    max_per_speaker: int = 5,
) -> StratifiedSampleResult:
    if not units:
        raise ValueError("Cannot sample from an empty unit pool")

    pools, stratum_sizes = _build_pools(units, seed=seed)
    quotas = allocate_quotas(dict(stratum_sizes), n)
    remaining = dict(quotas)
    speaker_counts: Counter[str] = Counter()
    selected_ids: set[str] = set()
    selected: List[Dict[str, Any]] = []
    stratum_selected: Dict[StratumKey, int] = {key: 0 for key in quotas}
    speaker_indices: Dict[StratumKey, Dict[str, int]] = {
        key: {speaker: 0 for speaker in sorted(pools[key])} for key in sorted(pools)
    }
    stratum_round: Dict[StratumKey, int] = {key: 0 for key in quotas}

    stratum_cycle = _interleaved_stratum_order(quotas)
    cycle_idx = 0
    while len(selected) < n and any(remaining.get(key, 0) > 0 for key in remaining):
        progress = False
        for _ in range(len(stratum_cycle)):
            if len(selected) >= n:
                break
            key = stratum_cycle[cycle_idx % len(stratum_cycle)]
            cycle_idx += 1
            if remaining.get(key, 0) <= 0:
                continue
            unit = _pick_one_round_robin(
                pools[key],
                speaker_counts=speaker_counts,
                speaker_indices=speaker_indices[key],
                max_per_speaker=max_per_speaker,
                selected_ids=selected_ids,
                stratum_round=stratum_round[key],
            )
            if unit is None:
                continue
            unit_id = str(unit.get("unit_id") or id(unit))
            selected.append(unit)
            selected_ids.add(unit_id)
            speaker = _speaker_name(unit)
            speaker_counts[speaker] += 1
            remaining[key] -= 1
            stratum_selected[key] += 1
            stratum_round[key] += 1
            progress = True
        if not progress:
            break

    if len(selected) < n:
        remaining_units: List[Dict[str, Any]] = []
        for unit in units:
            unit_id = str(unit.get("unit_id") or id(unit))
            if unit_id in selected_ids:
                continue
            speaker = _speaker_name(unit)
            if speaker_counts[speaker] >= max_per_speaker:
                continue
            remaining_units.append(unit)
        _deterministic_shuffle(remaining_units, seed=seed, label="global-backfill")
        for unit in remaining_units:
            if len(selected) >= n:
                break
            speaker = _speaker_name(unit)
            if speaker_counts[speaker] >= max_per_speaker:
                continue
            unit_id = str(unit.get("unit_id") or id(unit))
            if unit_id in selected_ids:
                continue
            selected.append(unit)
            selected_ids.add(unit_id)
            speaker_counts[speaker] += 1
            key = _unit_stratum(unit)
            stratum_selected[key] = stratum_selected.get(key, 0) + 1

    shortfall_reason: str | None = None
    if len(selected) < n:
        capacity = _speaker_capacity(units, max_per_speaker)
        shortfall_reason = (
            f"Requested n={n} but only {len(selected)} unit(s) could be selected "
            f"under max_per_speaker={max_per_speaker} (theoretical ceiling={capacity})."
        )

    party_selected: Counter[str] = Counter()
    year_selected: Counter[str] = Counter()
    for unit in selected:
        party, year = _unit_stratum(unit)
        party_selected[party] += 1
        year_selected[year] += 1

    return StratifiedSampleResult(
        units=selected,
        requested_n=n,
        seed=seed,
        max_per_speaker=max_per_speaker,
        stratum_quotas=quotas,
        stratum_selected=stratum_selected,
        party_selected=party_selected,
        year_selected=year_selected,
        speaker_selected=speaker_counts,
        pool_total=len(units),
        shortfall_reason=shortfall_reason,
    )
