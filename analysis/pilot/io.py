"""Load pilot annotation CSVs for two or more annotators."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.pilot.constants import ANNOTATION_COLUMNS
from scripts.analysis.pilot_annotation_io import fallacy_set_label, parse_fallacy_set


class AnnotationStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    COMPLETE = "complete"


@dataclass(frozen=True)
class PilotDataset:
    template_path: Path | None
    annotator_paths: tuple[Path, ...]
    annotator_names: tuple[str, ...]
    unit_ids: List[str]
    labels: tuple[Dict[str, Dict[str, str]], ...]
    metadata: Dict[str, Dict[str, str]]
    status: AnnotationStatus
    filled_counts: Dict[str, int]

    @property
    def n_annotators(self) -> int:
        return len(self.annotator_paths)

    @property
    def n_units(self) -> int:
        return len(self.unit_ids)


def _read_csv(path: Path) -> tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header row in {path}")
        rows = [dict(row) for row in reader]
        return list(reader.fieldnames), rows


def _normalize_label(column: str, value: str) -> str:
    value = (value or "").strip()
    if column == "fallacy_labels":
        return fallacy_set_label(value)
    return value


def _is_filled(column: str, value: str) -> bool:
    value = (value or "").strip()
    if not value:
        return False
    if column == "fallacy_labels" and value.upper() == "FAL_NONE":
        return True
    return True


def _rows_to_index(rows: Sequence[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    return {(row.get("unit_id") or "").strip(): row for row in rows if (row.get("unit_id") or "").strip()}


def _annotation_status(
    unit_ids: Sequence[str],
    labels: Sequence[Dict[str, Dict[str, str]]],
) -> tuple[AnnotationStatus, Dict[str, int]]:
    filled_counts = {column: 0 for column in ANNOTATION_COLUMNS}
    total_slots = len(unit_ids) * len(labels)
    filled_slots = 0

    for unit_id in unit_ids:
        for annotator_labels in labels:
            for column in ANNOTATION_COLUMNS:
                value = annotator_labels.get(unit_id, {}).get(column, "")
                if _is_filled(column, value):
                    filled_counts[column] += 1
                    filled_slots += 1

    if filled_slots == 0:
        return AnnotationStatus.PENDING, filled_counts
    if filled_slots == total_slots * len(ANNOTATION_COLUMNS):
        return AnnotationStatus.COMPLETE, filled_counts
    return AnnotationStatus.PARTIAL, filled_counts


def load_pilot_dataset(
    *,
    annotator_paths: Sequence[Path],
    template_path: Path | None = None,
) -> PilotDataset:
    resolved_annotators = tuple(path for path in annotator_paths if path.exists())
    template_rows: List[Dict[str, str]] = []
    template_fields: List[str] = []

    if template_path and template_path.exists():
        template_fields, template_rows = _read_csv(template_path)
    elif resolved_annotators:
        _, template_rows = _read_csv(resolved_annotators[0])
        template_fields = list(ANNOTATION_COLUMNS)
    else:
        raise ValueError("Provide at least one annotator CSV or an existing template CSV.")

    for column in ("unit_id", "text"):
        if template_rows and column not in template_rows[0]:
            raise ValueError(f"Template/annotator CSV missing required column '{column}'")

    unit_ids = [(row.get("unit_id") or "").strip() for row in template_rows]
    unit_ids = [unit_id for unit_id in unit_ids if unit_id]
    if not unit_ids:
        raise ValueError("No unit_id rows found in template or annotator CSV.")

    metadata = {
        (row.get("unit_id") or "").strip(): {
            key: row.get(key, "")
            for key in ("text", "speaker_name", "speaker_party", "date")
        }
        for row in template_rows
        if (row.get("unit_id") or "").strip()
    }

    labels_by_annotator: List[Dict[str, Dict[str, str]]] = []
    names: List[str] = []

    if resolved_annotators:
        indices = [_rows_to_index(_read_csv(path)[1]) for path in resolved_annotators]
        common_ids = set(unit_ids)
        for index in indices:
            common_ids &= set(index)
        if common_ids != set(unit_ids):
            missing = sorted(set(unit_ids) - common_ids)
            raise ValueError(
                "Annotator CSV files must share the same unit_id set as the template. "
                f"Missing in annotators: {', '.join(missing[:5])}"
            )

        for path, index in zip(resolved_annotators, indices):
            names.append(path.stem)
            annotator_labels: Dict[str, Dict[str, str]] = {}
            for unit_id in unit_ids:
                row = index[unit_id]
                annotator_labels[unit_id] = {
                    column: _normalize_label(column, row.get(column, ""))
                    for column in ANNOTATION_COLUMNS
                }
            labels_by_annotator.append(annotator_labels)
    else:
        names = ["pending"]

    if not labels_by_annotator:
        empty = {
            unit_id: {column: "" for column in ANNOTATION_COLUMNS}
            for unit_id in unit_ids
        }
        labels_by_annotator = [empty]

    status, filled_counts = _annotation_status(unit_ids, labels_by_annotator)
    return PilotDataset(
        template_path=template_path,
        annotator_paths=resolved_annotators,
        annotator_names=tuple(names),
        unit_ids=unit_ids,
        labels=tuple(labels_by_annotator),
        metadata=metadata,
        status=status,
        filled_counts=filled_counts,
    )


def column_values(dataset: PilotDataset, column: str, annotator_index: int) -> List[str]:
    return [dataset.labels[annotator_index][unit_id][column] for unit_id in dataset.unit_ids]


def normalized_column_matrix(dataset: PilotDataset, column: str) -> List[List[str]]:
    return [column_values(dataset, column, index) for index in range(dataset.n_annotators)]


def usable_units_for_column(dataset: PilotDataset, column: str) -> List[str]:
    usable: List[str] = []
    for unit_id in dataset.unit_ids:
        values = [
            dataset.labels[index][unit_id][column]
            for index in range(dataset.n_annotators)
        ]
        filled = [value for value in values if _is_filled(column, value)]
        if len(filled) >= 2:
            usable.append(unit_id)
    return usable
