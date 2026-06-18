"""Load human and LLM annotations for comparison."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.human_vs_llm.constants import PF_COLUMN
from analysis.llm_annotation.validator import load_annotation_jsonl


@dataclass(frozen=True)
class HumanAnnotationSet:
    annotator_paths: tuple[Path, ...]
    annotator_names: tuple[str, ...]
    unit_ids: List[str]
    labels: tuple[Dict[str, str], ...]


@dataclass(frozen=True)
class LLMAnnotationSet:
    model_name: str
    path: Path
    records_by_id: Dict[str, dict]


def _read_csv(path: Path) -> List[Dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")
        return [dict(row) for row in reader]


def human_files_available(paths: Sequence[Path]) -> tuple[bool, List[str]]:
    missing = [str(path) for path in paths if not path.exists()]
    return len(missing) == 0, missing


def load_human_annotations(paths: Sequence[Path]) -> HumanAnnotationSet:
    available, missing = human_files_available(paths)
    if not available:
        raise FileNotFoundError(f"Missing human annotation files: {', '.join(missing)}")

    indices = []
    names = []
    for path in paths:
        rows = _read_csv(path)
        by_id = {(row.get("unit_id") or "").strip(): row for row in rows if (row.get("unit_id") or "").strip()}
        indices.append(by_id)
        names.append(path.stem)

    common = set(indices[0])
    for index in indices[1:]:
        common &= set(index)
    unit_ids = sorted(common)
    if not unit_ids:
        raise ValueError("No overlapping unit_id values across human annotator files.")

    labels = tuple(
        {
            unit_id: (indices[i][unit_id].get(PF_COLUMN) or "").strip()
            for unit_id in unit_ids
        }
        for i in range(len(indices))
    )
    return HumanAnnotationSet(
        annotator_paths=tuple(paths),
        annotator_names=tuple(names),
        unit_ids=unit_ids,
        labels=labels,
    )


def load_adjudicated_labels(path: Path) -> Dict[str, str]:
    if not path.exists():
        return {}
    labels: Dict[str, str] = {}
    for row in _read_csv(path):
        unit_id = (row.get("unit_id") or "").strip()
        label = (row.get(PF_COLUMN) or "").strip()
        if unit_id and label:
            labels[unit_id] = label
    return labels


def discover_llm_jsonl_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*_pilot_100.jsonl"))


def load_llm_annotations(path: Path) -> LLMAnnotationSet:
    records = load_annotation_jsonl(path)
    model_name = path.stem.replace("_pilot_100", "")
    by_id: Dict[str, dict] = {}
    for record in records:
        unit_id = str(record.get("unit_id", "")).strip()
        if unit_id:
            by_id[unit_id] = record
    return LLMAnnotationSet(model_name=model_name, path=path, records_by_id=by_id)


def llm_label(record: dict) -> str | None:
    if record.get("_parse_error"):
        return None
    label = (record.get(PF_COLUMN) or "").strip()
    return label or None
