"""Orchestration for SPDB external fallacy LLM batch runs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Sequence

from analysis.external_validation.fallacy_io import ExternalTextRow, load_external_dataset, write_predictions_jsonl
from analysis.external_validation.fallacy_prompts import render_fallacy_prompt
from analysis.external_validation.fallacy_validator import validate_predictions_file
from analysis.llm_annotation.backend import AnnotationBackend, CommandBackend
from analysis.llm_annotation.parser import parse_model_response


@dataclass(frozen=True)
class FallacyBatchResult:
    model_name: str
    output_path: Path
    records: List[dict]
    validation: object


def _normalize_prediction(
    parsed: dict,
    *,
    row: ExternalTextRow,
    model_name: str,
) -> dict:
    fallacies = parsed.get("fallacy_labels", [])
    if isinstance(fallacies, str):
        fallacies = [part.strip() for part in fallacies.split("|") if part.strip()]
    if not isinstance(fallacies, list):
        fallacies = []

    cleaned = [str(label).strip() for label in fallacies if str(label).strip()]
    none_explicit = parsed.get("fallacy_none_explicit")
    if none_explicit is None:
        none_explicit = not cleaned

    record = {
        "row_id": row.row_id,
        "model_name": str(parsed.get("model_name") or model_name).strip(),
        "text": row.text,
        "fallacy_labels": cleaned[:3],
        "fallacy_none_explicit": bool(none_explicit),
        "confidence": float(parsed.get("confidence", 0.0)),
        "explanation": str(parsed.get("explanation", "")),
    }
    return record


def run_fallacy_batch(
    *,
    input_path: Path,
    text_column: str,
    prompt_path: Path,
    model_name: str,
    backend: AnnotationBackend,
    output_path: Path,
    id_column: str = "id",
    limit: int | None = None,
    progress_every: int = 50,
) -> FallacyBatchResult:
    rows = load_external_dataset(input_path, text_column=text_column, id_column=id_column)
    if limit is not None:
        rows = rows[:limit]
    records: List[dict] = []
    total = len(rows)

    for index, row in enumerate(rows, start=1):
        prompt = render_fallacy_prompt(
            prompt_path,
            text=row.text,
            row_id=row.row_id,
            model_name=model_name,
        )
        try:
            raw = backend.generate(prompt)
        except Exception as exc:  # noqa: BLE001 - batch runner records backend failures per row
            records.append(
                {
                    "row_id": row.row_id,
                    "model_name": model_name,
                    "text": row.text,
                    "_parse_error": f"backend error: {exc}",
                }
            )
            if progress_every and index % progress_every == 0:
                print(f"Progress: {index}/{total} rows", flush=True)
            continue

        parsed, parse_error = parse_model_response(raw, unit_id=row.row_id, model_name=model_name)
        if parse_error:
            records.append(
                {
                    "row_id": row.row_id,
                    "model_name": model_name,
                    "text": row.text,
                    "_parse_error": parse_error,
                    "_raw_response": raw[:500],
                }
            )
        else:
            record = _normalize_prediction(parsed, row=row, model_name=model_name)
            records.append(record)

        if progress_every and index % progress_every == 0:
            print(f"Progress: {index}/{total} rows", flush=True)

    write_predictions_jsonl(output_path, records)
    validation = validate_predictions_file(
        output_path,
        input_path,
        text_column=text_column,
        id_column=id_column,
    )
    return FallacyBatchResult(
        model_name=model_name,
        output_path=output_path,
        records=records,
        validation=validation,
    )


def run_fallacy_batch_command(
    *,
    input_path: Path,
    text_column: str,
    prompt_path: Path,
    model_name: str,
    backend_command: str,
    output_path: Path,
    id_column: str = "id",
    timeout_seconds: int = 180,
    limit: int | None = None,
    progress_every: int = 50,
) -> FallacyBatchResult:
    backend = CommandBackend(backend_command, timeout_seconds=timeout_seconds)
    return run_fallacy_batch(
        input_path=input_path,
        text_column=text_column,
        prompt_path=prompt_path,
        model_name=model_name,
        backend=backend,
        output_path=output_path,
        id_column=id_column,
        limit=limit,
        progress_every=progress_every,
    )


def deterministic_mock_prediction(row: ExternalTextRow, index: int, model_name: str) -> dict:
    fal_cycle = [
        [],
        ["FAL_ADHOM"],
        ["FAL_STRAW"],
        ["FAL_WHATABOUT", "FAL_EMOTION"],
    ]
    labels = fal_cycle[index % len(fal_cycle)]
    return {
        "row_id": row.row_id,
        "model_name": model_name,
        "text": row.text,
        "fallacy_labels": labels,
        "fallacy_none_explicit": not labels,
        "confidence": 0.65 + (index % 3) * 0.1,
        "explanation": "Respuesta simulada para prueba del pipeline SPDB.",
    }


def run_fallacy_dry_run(
    *,
    input_path: Path,
    text_column: str,
    prompt_path: Path,
    model_name: str,
    output_path: Path,
    id_column: str = "id",
) -> FallacyBatchResult:
    rows = load_external_dataset(input_path, text_column=text_column, id_column=id_column)
    records = [
        deterministic_mock_prediction(row, index, model_name)
        for index, row in enumerate(rows)
    ]
    write_predictions_jsonl(output_path, records)
    validation = validate_predictions_file(
        output_path,
        input_path,
        text_column=text_column,
        id_column=id_column,
    )
    return FallacyBatchResult(
        model_name=model_name,
        output_path=output_path,
        records=records,
        validation=validation,
    )
