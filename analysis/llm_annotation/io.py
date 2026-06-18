"""Load pilot discourse units for LLM annotation."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class PilotUnit:
    unit_id: str
    text: str
    speaker_name: str
    speaker_party: str
    date: str


def load_pilot_units(path: Path) -> List[PilotUnit]:
    units: List[PilotUnit] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header in {path}")
        for row in reader:
            unit_id = (row.get("unit_id") or "").strip()
            text = (row.get("text") or "").strip()
            if not unit_id or not text:
                continue
            units.append(
                PilotUnit(
                    unit_id=unit_id,
                    text=text,
                    speaker_name=(row.get("speaker_name") or "").strip(),
                    speaker_party=(row.get("speaker_party") or "").strip(),
                    date=(row.get("date") or "").strip(),
                )
            )
    if not units:
        raise ValueError(f"No units loaded from {path}")
    return units


def pilot_unit_ids(units: Sequence[PilotUnit]) -> List[str]:
    return [unit.unit_id for unit in units]


def units_by_id(units: Sequence[PilotUnit]) -> Dict[str, PilotUnit]:
    return {unit.unit_id: unit for unit in units}
