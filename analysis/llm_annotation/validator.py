"""Validate and normalize LLM annotation records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Set

from analysis.llm_annotation.constants import SCHEMA_PATH
from analysis.llm_annotation.io import PilotUnit, load_pilot_units
from analysis.llm_annotation.labels import load_fal_labels, load_pf_labels
from scripts.ingestion.common import load_schema, validate_against_schema


@dataclass
class ValidationSummary:
    total_records: int = 0
    expected_units: int = 0
    parse_failures: int = 0
    schema_errors: int = 0
    invalid_pf_labels: int = 0
    invalid_fal_labels: int = 0
    duplicate_unit_ids: int = 0
    missing_unit_ids: List[str] = field(default_factory=list)
    extra_unit_ids: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)

    @property
    def parse_failure_rate(self) -> float:
        return self.parse_failures / self.total_records if self.total_records else 0.0

    @property
    def invalid_label_rate(self) -> float:
        invalid = self.invalid_pf_labels + self.invalid_fal_labels + self.schema_errors
        return invalid / self.total_records if self.total_records else 0.0

    @property
    def ok(self) -> bool:
        return (
            not self.errors
            and self.total_records == self.expected_units
            and not self.missing_unit_ids
            and not self.extra_unit_ids
            and self.duplicate_unit_ids == 0
        )


def normalize_fallacy_labels(labels: Sequence[str]) -> List[str]:
    cleaned = [label.strip() for label in labels if label and label.strip()]
    if not cleaned:
        return ["FAL_NONE"]
    if "FAL_NONE" in cleaned:
        return ["FAL_NONE"] if len(cleaned) == 1 else cleaned
    return cleaned[:3]


def normalize_record(record: Mapping[str, Any], *, model_name: str) -> Dict[str, Any]:
    fallacies = record.get("fallacy_labels", [])
    if isinstance(fallacies, str):
        fallacies = [part.strip() for part in fallacies.split("|") if part.strip()]
    if not isinstance(fallacies, list):
        fallacies = []
    normalized = {
        "unit_id": str(record.get("unit_id", "")).strip(),
        "model_name": str(record.get("model_name") or model_name).strip(),
        "pragmatic_function": str(record.get("pragmatic_function", "")).strip(),
        "fallacy_labels": normalize_fallacy_labels([str(item) for item in fallacies]),
    }
    if "confidence" in record and record["confidence"] is not None:
        normalized["confidence"] = float(record["confidence"])
    if record.get("rationale"):
        normalized["rationale"] = str(record["rationale"])
    return normalized


def validate_record(record: Mapping[str, Any], schema: Mapping[str, Any]) -> List[str]:
    errors = validate_against_schema(record, schema, record_label="record")
    pf_labels = set(load_pf_labels())
    fal_labels = set(load_fal_labels())

    pf = record.get("pragmatic_function")
    if pf not in pf_labels:
        errors.append(f"record.pragmatic_function: invalid label {pf!r}")

    fallacies = record.get("fallacy_labels", [])
    if not isinstance(fallacies, list):
        errors.append("record.fallacy_labels: must be an array")
        return errors

    if len(fallacies) > 3:
        errors.append("record.fallacy_labels: max 3 labels allowed")

    if "FAL_NONE" in fallacies and len(fallacies) > 1:
        errors.append("record.fallacy_labels: FAL_NONE cannot co-occur with other labels")

    for label in fallacies:
        if label not in fal_labels:
            errors.append(f"record.fallacy_labels: invalid label {label!r}")

    if "confidence" in record and record["confidence"] is not None:
        confidence = record["confidence"]
        if not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1:
            errors.append("record.confidence: must be a number between 0 and 1")

    return errors


def load_annotation_jsonl(path: Path) -> List[Dict[str, Any]]:
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


def validate_annotations_file(
    annotations_path: Path,
    pilot_path: Path,
    *,
    model_name: str | None = None,
) -> ValidationSummary:
    schema = load_schema(SCHEMA_PATH)
    expected_units = load_pilot_units(pilot_path)
    expected_ids = {unit.unit_id for unit in expected_units}
    summary = ValidationSummary(expected_units=len(expected_ids))

    try:
        records = load_annotation_jsonl(annotations_path)
    except ValueError as exc:
        summary.errors.append(str(exc))
        return summary

    summary.total_records = len(records)
    seen: Set[str] = set()

    for index, raw in enumerate(records, start=1):
        if raw.get("_parse_error"):
            summary.parse_failures += 1
            summary.errors.append(f"line {index}: parse failure ({raw.get('_parse_error')})")
            continue

        record = normalize_record(raw, model_name=model_name or str(raw.get("model_name", "")))
        unit_id = record["unit_id"]
        if unit_id in seen:
            summary.duplicate_unit_ids += 1
            summary.errors.append(f"line {index}: duplicate unit_id {unit_id}")
        seen.add(unit_id)

        errors = validate_record(record, schema)
        if errors:
            summary.schema_errors += 1
            summary.errors.extend(f"line {index}: {err}" for err in errors)
            if any("pragmatic_function" in err for err in errors):
                summary.invalid_pf_labels += 1
            if any("fallacy_labels" in err for err in errors):
                summary.invalid_fal_labels += 1

    summary.missing_unit_ids = sorted(expected_ids - seen)
    summary.extra_unit_ids = sorted(seen - expected_ids)
    if summary.missing_unit_ids:
        summary.errors.append(f"missing {len(summary.missing_unit_ids)} expected unit_id values")
    if summary.extra_unit_ids:
        summary.errors.append(f"found {len(summary.extra_unit_ids)} unexpected unit_id values")
    if summary.total_records != summary.expected_units:
        summary.errors.append(
            f"expected {summary.expected_units} records, found {summary.total_records}"
        )
    return summary
