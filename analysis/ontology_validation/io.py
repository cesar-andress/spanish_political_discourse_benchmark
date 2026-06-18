"""Load ontology validation datasets with optional QC fields."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence

from analysis.ontology_validation.constants import OPTIONAL_QC_COLUMNS, PF_COLUMN, PF_INVENTORY
from analysis.pilot.io import AnnotationStatus, PilotDataset, load_pilot_dataset


@dataclass(frozen=True)
class OntologyValidationDataset:
    pilot: PilotDataset
    pf_inventory: List[str]
    qc_fields: tuple[Dict[str, Dict[str, str]], ...]

    @property
    def status(self) -> AnnotationStatus:
        return self.pilot.status

    @property
    def n_units(self) -> int:
        return self.pilot.n_units

    @property
    def n_annotators(self) -> int:
        return self.pilot.n_annotators

    @property
    def unit_ids(self) -> List[str]:
        return self.pilot.unit_ids

    @property
    def annotator_names(self) -> tuple[str, ...]:
        return self.pilot.annotator_names


def _load_inventory(path: Path) -> List[str]:
    labels: List[str] = []
    if not path.exists():
        return labels
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            label_id = (row.get("label_id") or "").strip()
            if label_id:
                labels.append(label_id)
    return labels


def _load_qc_fields(path: Path, unit_ids: Sequence[str]) -> Dict[str, Dict[str, str]]:
    qc: Dict[str, Dict[str, str]] = {unit_id: {} for unit_id in unit_ids}
    if not path.exists():
        return qc
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return qc
        available = [column for column in OPTIONAL_QC_COLUMNS if column in reader.fieldnames]
        for row in reader:
            unit_id = (row.get("unit_id") or "").strip()
            if unit_id not in qc:
                continue
            qc[unit_id] = {column: (row.get(column) or "").strip() for column in available}
    return qc


def load_ontology_dataset(
    *,
    annotator_paths: Sequence[Path],
    template_path: Path | None = None,
) -> OntologyValidationDataset:
    pilot = load_pilot_dataset(annotator_paths=annotator_paths, template_path=template_path)
    pf_inventory = _load_inventory(PF_INVENTORY)
    qc_fields: List[Dict[str, Dict[str, str]]] = []
    if pilot.annotator_paths:
        for path in pilot.annotator_paths:
            qc_fields.append(_load_qc_fields(path, pilot.unit_ids))
    else:
        template = template_path or Path()
        qc_fields.append(_load_qc_fields(template, pilot.unit_ids))
    return OntologyValidationDataset(
        pilot=pilot,
        pf_inventory=pf_inventory,
        qc_fields=tuple(qc_fields),
    )


def pf_unit_ratings(dataset: OntologyValidationDataset) -> List[List[str]]:
    if dataset.status is AnnotationStatus.PENDING:
        return []
    return [
        [dataset.pilot.labels[index][unit_id][PF_COLUMN] for index in range(dataset.n_annotators)]
        for unit_id in dataset.unit_ids
        if all(
            dataset.pilot.labels[index][unit_id][PF_COLUMN].strip()
            for index in range(dataset.n_annotators)
        )
    ]


def pf_label_matrix(dataset: OntologyValidationDataset) -> List[List[str]]:
    if dataset.status is AnnotationStatus.PENDING:
        return []
    return [
        [dataset.pilot.labels[index][unit_id][PF_COLUMN] for unit_id in dataset.unit_ids]
        for index in range(dataset.n_annotators)
    ]
