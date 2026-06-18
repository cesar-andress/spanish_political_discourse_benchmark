"""Orchestration for SPDB LLM annotation runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from analysis.llm_annotation.backend import AnnotationBackend, CommandBackend
from analysis.llm_annotation.constants import (
    DEFAULT_ANNOTATION_REPORT,
    DEFAULT_DRY_RUN_REPORT,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_PILOT_INPUT,
    DEFAULT_REPORT_DIR,
    SCHEMA_PATH,
)
from analysis.llm_annotation.io import PilotUnit, load_pilot_units
from analysis.llm_annotation.labels import load_fal_labels, load_pf_labels
from analysis.llm_annotation.parser import parse_model_response
from analysis.llm_annotation.prompts import PromptMode, build_prompt
from analysis.llm_annotation.report import write_annotation_report, write_dry_run_report
from analysis.llm_annotation.validator import (
    ValidationSummary,
    normalize_record,
    validate_annotations_file,
    validate_record,
)
from scripts.ingestion.common import load_schema


@dataclass(frozen=True)
class AnnotationRunResult:
    model_name: str
    output_path: Path | None
    records: List[dict]
    validation: ValidationSummary
    dry_run: bool


def _deterministic_mock_record(unit: PilotUnit, index: int, model_name: str) -> dict:
    pf_labels = list(load_pf_labels())
    fal_labels = [label for label in load_fal_labels() if label != "FAL_NONE"]
    pf = pf_labels[index % len(pf_labels)]
    fallacies = ["FAL_NONE"] if index % 4 else [fal_labels[index % len(fal_labels)]]
    return {
        "unit_id": unit.unit_id,
        "model_name": model_name,
        "pragmatic_function": pf,
        "fallacy_labels": fallacies,
        "confidence": 0.75,
    }


def _annotate_units(
    units: Sequence[PilotUnit],
    backend: AnnotationBackend,
    *,
    model_name: str,
    mode: PromptMode,
) -> List[dict]:
    schema = load_schema(SCHEMA_PATH)
    records: List[dict] = []
    for index, unit in enumerate(units):
        prompt = build_prompt(unit, model_name=model_name, mode=mode)
        raw = backend.generate(prompt)
        parsed, parse_error = parse_model_response(raw, unit_id=unit.unit_id, model_name=model_name)
        if parse_error:
            records.append(
                {
                    "unit_id": unit.unit_id,
                    "model_name": model_name,
                    "_parse_error": parse_error,
                    "_raw_response": raw[:500],
                }
            )
            continue
        record = normalize_record(parsed, model_name=model_name)
        record["unit_id"] = unit.unit_id
        validation_errors = validate_record(record, schema)
        if validation_errors:
            record["_validation_errors"] = validation_errors
        records.append(record)
    return records


def _write_jsonl(path: Path, records: Sequence[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def run_dry_run(
    *,
    pilot_path: Path = DEFAULT_PILOT_INPUT,
    report_path: Path = DEFAULT_DRY_RUN_REPORT,
    model_name: str = "dry-run-mock",
    mode: PromptMode = "zero_shot",
) -> AnnotationRunResult:
    units = load_pilot_units(pilot_path)
    annotated = [_deterministic_mock_record(unit, index, model_name) for index, unit in enumerate(units)]

    temp_path = DEFAULT_REPORT_DIR / "_dry_run_annotations.jsonl"
    _write_jsonl(temp_path, annotated)
    validation = validate_annotations_file(temp_path, pilot_path, model_name=model_name)

    sample_prompt = build_prompt(units[0], model_name=model_name, mode=mode)
    write_dry_run_report(
        report_path,
        units=units,
        sample_prompt=sample_prompt,
        validation=validation,
        model_name=model_name,
        mode=mode,
    )
    temp_path.unlink(missing_ok=True)

    return AnnotationRunResult(
        model_name=model_name,
        output_path=None,
        records=annotated,
        validation=validation,
        dry_run=True,
    )


def run_local_annotation(
    *,
    pilot_path: Path = DEFAULT_PILOT_INPUT,
    model_name: str,
    backend_command: str,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    report_path: Path = DEFAULT_ANNOTATION_REPORT,
    mode: PromptMode = "zero_shot",
) -> AnnotationRunResult:
    units = load_pilot_units(pilot_path)
    backend = CommandBackend(backend_command)
    records = _annotate_units(units, backend, model_name=model_name, mode=mode)

    output_path = output_dir / f"{model_name}_pilot_100.jsonl"
    _write_jsonl(output_path, records)
    validation = validate_annotations_file(output_path, pilot_path, model_name=model_name)
    write_annotation_report(report_path, model_name=model_name, validation=validation, records=records)
    return AnnotationRunResult(
        model_name=model_name,
        output_path=output_path,
        records=records,
        validation=validation,
        dry_run=False,
    )
