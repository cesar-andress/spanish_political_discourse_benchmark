"""Load and align pilot annotation CSV exports from two annotators."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set, Tuple

DEFAULT_ANNOTATOR_A = Path("annotation/pilot_001/pilot_100_units_annotator_a.csv")
DEFAULT_ANNOTATOR_B = Path("annotation/pilot_001/pilot_100_units_annotator_b.csv")
DEFAULT_RESULTS_DIR = Path("annotation/pilot_001/results")

ANNOTATION_COLUMNS = (
    "pragmatic_function",
    "fallacy_labels",
    "semantic_vacuity",
    "conceptual_anachronism",
)

REQUIRED_COLUMNS = ("unit_id", *ANNOTATION_COLUMNS)


@dataclass(frozen=True)
class AlignedPilotAnnotations:
    annotator_a_path: Path
    annotator_b_path: Path
    unit_ids: List[str]
    labels_a: Dict[str, Dict[str, str]]
    labels_b: Dict[str, Dict[str, str]]
    metadata: Dict[str, Dict[str, str]]


def _read_pilot_csv(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header row in {path}")
        missing = [column for column in REQUIRED_COLUMNS if column not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path} is missing required columns: {', '.join(missing)}")
        rows = [dict(row) for row in reader]
    return list(reader.fieldnames), rows


def _validate_filled(rows: Sequence[Dict[str, str]], path: Path) -> None:
    for index, row in enumerate(rows, start=2):
        for column in ANNOTATION_COLUMNS:
            if not (row.get(column) or "").strip():
                raise ValueError(
                    f"{path} row {index} (unit_id={row.get('unit_id', '?')}) "
                    f"has empty '{column}'"
                )


def load_aligned_annotations(
    annotator_a_path: Path,
    annotator_b_path: Path,
    *,
    require_filled: bool = True,
) -> AlignedPilotAnnotations:
    _, rows_a = _read_pilot_csv(annotator_a_path)
    _, rows_b = _read_pilot_csv(annotator_b_path)

    if require_filled:
        _validate_filled(rows_a, annotator_a_path)
        _validate_filled(rows_b, annotator_b_path)

    by_id_a = {row["unit_id"]: row for row in rows_a}
    by_id_b = {row["unit_id"]: row for row in rows_b}
    ids_a = set(by_id_a)
    ids_b = set(by_id_b)
    if ids_a != ids_b:
        only_a = sorted(ids_a - ids_b)
        only_b = sorted(ids_b - ids_a)
        details: List[str] = []
        if only_a:
            details.append(f"only in A ({len(only_a)}): {', '.join(only_a[:5])}")
        if only_b:
            details.append(f"only in B ({len(only_b)}): {', '.join(only_b[:5])}")
        raise ValueError(
            "Annotator CSV files must contain the same unit_id set. "
            + "; ".join(details)
        )

    unit_ids = sorted(ids_a)
    labels_a = {
        unit_id: {column: by_id_a[unit_id].get(column, "").strip() for column in ANNOTATION_COLUMNS}
        for unit_id in unit_ids
    }
    labels_b = {
        unit_id: {column: by_id_b[unit_id].get(column, "").strip() for column in ANNOTATION_COLUMNS}
        for unit_id in unit_ids
    }
    metadata = {
        unit_id: {
            key: by_id_a[unit_id].get(key, "")
            for key in ("text", "speaker_name", "speaker_party", "date")
        }
        for unit_id in unit_ids
    }
    return AlignedPilotAnnotations(
        annotator_a_path=annotator_a_path,
        annotator_b_path=annotator_b_path,
        unit_ids=unit_ids,
        labels_a=labels_a,
        labels_b=labels_b,
        metadata=metadata,
    )


def column_values(
    aligned: AlignedPilotAnnotations,
    column: str,
    *,
    side: str = "both",
) -> Tuple[List[str], List[str]] | List[str]:
    values_a = [aligned.labels_a[unit_id][column] for unit_id in aligned.unit_ids]
    values_b = [aligned.labels_b[unit_id][column] for unit_id in aligned.unit_ids]
    if side == "a":
        return values_a
    if side == "b":
        return values_b
    return values_a, values_b


def parse_fallacy_set(value: str) -> Set[str]:
    raw = (value or "").strip()
    if not raw or raw.upper() == "FAL_NONE":
        return set()
    return {part.strip() for part in raw.split("|") if part.strip()}


def fallacy_set_label(value: str) -> str:
    labels = sorted(parse_fallacy_set(value))
    return "|".join(labels) if labels else "FAL_NONE"


def ensure_output_dir(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir


def write_markdown(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def add_pilot_input_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--annotator-a",
        type=Path,
        default=DEFAULT_ANNOTATOR_A,
        help="Pilot CSV from annotator A",
    )
    parser.add_argument(
        "--annotator-b",
        type=Path,
        default=DEFAULT_ANNOTATOR_B,
        help="Pilot CSV from annotator B",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_RESULTS_DIR,
        help="Directory for agreement analysis outputs",
    )


def normalized_column_values(
    aligned: AlignedPilotAnnotations,
    column: str,
) -> Tuple[List[str], List[str]]:
    values_a, values_b = column_values(aligned, column)
    if column == "fallacy_labels":
        return (
            [fallacy_set_label(value) for value in values_a],
            [fallacy_set_label(value) for value in values_b],
        )
    return values_a, values_b
