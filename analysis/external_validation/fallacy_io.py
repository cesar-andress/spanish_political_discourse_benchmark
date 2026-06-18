"""Load external text datasets for fallacy batch runs."""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence


@dataclass(frozen=True)
class ExternalTextRow:
    row_id: str
    text: str


def _resolve_row_id(payload: dict, *, index: int, id_column: str) -> str:
    for key in (id_column, "id", "row_id", "unit_id", "example_id"):
        value = payload.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return f"row_{index:04d}"


def load_external_dataset(
    path: Path,
    *,
    text_column: str,
    id_column: str = "id",
) -> List[ExternalTextRow]:
    if not path.exists():
        raise FileNotFoundError(f"Input dataset not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".jsonl":
        return _load_jsonl(path, text_column=text_column, id_column=id_column)
    if suffix == ".csv":
        return _load_csv(path, text_column=text_column, id_column=id_column)
    raise ValueError(f"Unsupported input format: {path.suffix} (expected .jsonl or .csv)")


def _load_jsonl(path: Path, *, text_column: str, id_column: str) -> List[ExternalTextRow]:
    rows: List[ExternalTextRow] = []
    with path.open(encoding="utf-8") as handle:
        for index, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{index}: each JSONL line must be an object")
            text = str(payload.get(text_column, "")).strip()
            if not text:
                raise ValueError(f"{path}:{index}: missing or empty {text_column!r}")
            row_id = _resolve_row_id(payload, index=index, id_column=id_column)
            rows.append(ExternalTextRow(row_id=row_id, text=text))
    if not rows:
        raise ValueError(f"{path}: no rows loaded")
    return rows


def _load_csv(path: Path, *, text_column: str, id_column: str) -> List[ExternalTextRow]:
    rows: List[ExternalTextRow] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames or text_column not in reader.fieldnames:
            raise ValueError(f"{path}: missing required column {text_column!r}")
        for index, payload in enumerate(reader, start=1):
            text = str(payload.get(text_column, "")).strip()
            if not text:
                raise ValueError(f"{path}:{index}: missing or empty {text_column!r}")
            row_id = _resolve_row_id(payload, index=index, id_column=id_column)
            rows.append(ExternalTextRow(row_id=row_id, text=text))
    if not rows:
        raise ValueError(f"{path}: no rows loaded")
    return rows


def dataset_name_from_path(path: Path) -> str:
    stem = path.stem
    parent = path.parent.name
    if parent and parent not in {".", "data", "external", "fixtures"}:
        return f"{parent}/{stem}"
    return stem


def write_predictions_jsonl(path: Path, records: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
