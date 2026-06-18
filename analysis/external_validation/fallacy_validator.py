"""Validate SPDB external fallacy LLM predictions."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Set

from analysis.external_validation.fallacy_constants import REQUIRED_OUTPUT_FIELDS, SPDB_FAL_LABELS
from analysis.external_validation.fallacy_io import ExternalTextRow, load_external_dataset


@dataclass
class FallacyValidationSummary:
    total_records: int = 0
    expected_rows: int = 0
    valid_outputs: int = 0
    parse_failures: int = 0
    invalid_label_records: int = 0
    duplicate_row_ids: int = 0
    missing_row_ids: List[str] = field(default_factory=list)
    extra_row_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def parse_failure_rate(self) -> float:
        return self.parse_failures / self.total_records if self.total_records else 0.0

    @property
    def invalid_label_rate(self) -> float:
        return self.invalid_label_records / self.total_records if self.total_records else 0.0

    @property
    def ok(self) -> bool:
        return (
            not self.errors
            and self.total_records == self.expected_rows
            and not self.missing_row_ids
            and not self.extra_row_ids
            and self.duplicate_row_ids == 0
        )


def load_predictions_jsonl(path: Path) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON ({exc})") from exc
            if not isinstance(payload, dict):
                raise ValueError(f"{path}:{line_no}: each line must be a JSON object")
            records.append(payload)
    return records


def validate_fallacy_prediction(record: Mapping[str, Any]) -> List[str]:
    errors: List[str] = []

    if record.get("_parse_error"):
        errors.append(f"parse failure: {record.get('_parse_error')}")
        return errors

    for field_name in REQUIRED_OUTPUT_FIELDS:
        if field_name not in record:
            errors.append(f"missing required field {field_name!r}")

    fallacies = record.get("fallacy_labels")
    if not isinstance(fallacies, list):
        errors.append("fallacy_labels must be an array")
        return errors

    if len(fallacies) > 3:
        errors.append("fallacy_labels: max 3 labels allowed")

    if "FAL_NONE" in fallacies:
        errors.append("fallacy_labels must not contain FAL_NONE")

    invalid_labels = [label for label in fallacies if label not in SPDB_FAL_LABELS]
    if invalid_labels:
        errors.append(f"fallacy_labels: invalid label(s) {invalid_labels!r}")

    if len(set(fallacies)) != len(fallacies):
        errors.append("fallacy_labels: duplicate labels are not allowed")

    none_explicit = record.get("fallacy_none_explicit")
    if not isinstance(none_explicit, bool):
        errors.append("fallacy_none_explicit must be a boolean")
    elif fallacies and none_explicit:
        errors.append("fallacy_none_explicit must be false when fallacy_labels is non-empty")
    elif not fallacies and not none_explicit:
        errors.append("fallacy_none_explicit must be true when fallacy_labels is empty")

    confidence = record.get("confidence")
    if not isinstance(confidence, (int, float)):
        errors.append("confidence must be a number")
    elif confidence < 0 or confidence > 1:
        errors.append("confidence must be in [0, 1]")

    explanation = record.get("explanation")
    if not isinstance(explanation, str):
        errors.append("explanation must be a string")

    return errors


def validate_predictions_file(
    predictions_path: Path,
    input_path: Path,
    *,
    text_column: str = "text",
    id_column: str = "id",
) -> FallacyValidationSummary:
    expected_rows = load_external_dataset(input_path, text_column=text_column, id_column=id_column)
    expected_ids = {row.row_id for row in expected_rows}
    summary = FallacyValidationSummary(expected_rows=len(expected_ids))

    try:
        records = load_predictions_jsonl(predictions_path)
    except ValueError as exc:
        summary.errors.append(str(exc))
        return summary

    summary.total_records = len(records)
    seen: Set[str] = set()

    for index, record in enumerate(records, start=1):
        row_id = str(record.get("row_id", "")).strip()
        if not row_id:
            summary.errors.append(f"line {index}: missing row_id")
            continue

        if row_id in seen:
            summary.duplicate_row_ids += 1
            summary.errors.append(f"line {index}: duplicate row_id {row_id!r}")
        seen.add(row_id)

        errors = validate_fallacy_prediction(record)
        if record.get("_parse_error"):
            summary.parse_failures += 1
        elif errors:
            if any("invalid label" in err for err in errors):
                summary.invalid_label_records += 1
            summary.errors.extend(f"line {index} ({row_id}): {err}" for err in errors)
        else:
            summary.valid_outputs += 1

    summary.missing_row_ids = sorted(expected_ids - seen)
    summary.extra_row_ids = sorted(seen - expected_ids)
    if summary.missing_row_ids:
        summary.errors.append(f"missing {len(summary.missing_row_ids)} expected row_id values")
    if summary.extra_row_ids:
        summary.errors.append(f"found {len(summary.extra_row_ids)} unexpected row_id values")
    if summary.total_records != summary.expected_rows:
        summary.errors.append(
            f"expected {summary.expected_rows} records, found {summary.total_records}"
        )
    return summary
