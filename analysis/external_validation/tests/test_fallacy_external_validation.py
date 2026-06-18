"""Tests for SPDB external fallacy LLM batch pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.external_validation.fallacy_batch import run_fallacy_batch, run_fallacy_dry_run
from analysis.external_validation.fallacy_constants import (
    FALLACY_SPDB_CLAIM_EVIDENCE,
    FALLACY_SPDB_CONSENSUS,
    FALLACY_SPDB_ZERO_SHOT,
    FIXTURE_DATASET,
    SPDB_FAL_LABELS,
)
from analysis.external_validation.fallacy_io import load_external_dataset, write_predictions_jsonl
from analysis.external_validation.fallacy_prediction_report import write_fallacy_prediction_report
from analysis.external_validation.fallacy_prompts import render_fallacy_prompt
from analysis.external_validation.fallacy_validator import (
    validate_fallacy_prediction,
    validate_predictions_file,
)
from analysis.llm_annotation.backend import MockResponseBackend


def test_prompt_templates_exist_and_render_spanish_text() -> None:
    rows = load_external_dataset(FIXTURE_DATASET, text_column="text")
    for template in (FALLACY_SPDB_ZERO_SHOT, FALLACY_SPDB_CLAIM_EVIDENCE, FALLACY_SPDB_CONSENSUS):
        prompt = render_fallacy_prompt(
            template,
            text=rows[0].text,
            row_id=rows[0].row_id,
            model_name="test-model",
        )
        assert rows[0].text in prompt
        assert "FAL_ADHOM" in prompt
        assert "fallacy_none_explicit" in prompt


def test_validate_accepts_valid_none_prediction() -> None:
    record = {
        "row_id": "ext_003",
        "fallacy_labels": [],
        "fallacy_none_explicit": True,
        "confidence": 0.9,
        "explanation": "Afirmación informativa sin falacia retórica detectable.",
    }
    assert validate_fallacy_prediction(record) == []


def test_validate_rejects_invalid_label_and_none_logic() -> None:
    bad_label = {
        "row_id": "ext_001",
        "fallacy_labels": ["ad hominem"],
        "fallacy_none_explicit": False,
        "confidence": 0.5,
        "explanation": "x",
    }
    assert any("invalid label" in err for err in validate_fallacy_prediction(bad_label))

    bad_none = {
        "row_id": "ext_001",
        "fallacy_labels": ["FAL_ADHOM"],
        "fallacy_none_explicit": True,
        "confidence": 0.5,
        "explanation": "x",
    }
    assert any("fallacy_none_explicit" in err for err in validate_fallacy_prediction(bad_none))


def test_validate_rejects_too_many_labels() -> None:
    record = {
        "row_id": "ext_001",
        "fallacy_labels": list(SPDB_FAL_LABELS),
        "fallacy_none_explicit": False,
        "confidence": 0.4,
        "explanation": "x",
    }
    assert any("max 3" in err for err in validate_fallacy_prediction(record))


def test_dry_run_produces_one_output_per_fixture_row(tmp_path: Path) -> None:
    output = tmp_path / "dry.jsonl"
    result = run_fallacy_dry_run(
        input_path=FIXTURE_DATASET,
        text_column="text",
        prompt_path=FALLACY_SPDB_ZERO_SHOT,
        model_name="dry-run-mock",
        output_path=output,
    )
    assert output.exists()
    assert result.validation.ok
    assert result.validation.total_records == len(
        load_external_dataset(FIXTURE_DATASET, text_column="text")
    )


def test_mock_backend_batch_run(tmp_path: Path) -> None:
    rows = load_external_dataset(FIXTURE_DATASET, text_column="text")
    responses = {}
    for index, row in enumerate(rows):
        labels = [SPDB_FAL_LABELS[index % len(SPDB_FAL_LABELS)]] if index % 2 else []
        responses[row.row_id] = json.dumps(
            {
                "fallacy_labels": labels,
                "fallacy_none_explicit": not labels,
                "confidence": 0.8,
                "explanation": "Respuesta simulada en español.",
            },
            ensure_ascii=False,
        )

    output = tmp_path / "mock_backend.jsonl"
    backend = MockResponseBackend(responses_by_unit_id=responses)
    result = run_fallacy_batch(
        input_path=FIXTURE_DATASET,
        text_column="text",
        prompt_path=FALLACY_SPDB_ZERO_SHOT,
        model_name="mock-local",
        backend=backend,
        output_path=output,
    )
    assert result.validation.ok
    assert all("explanation" in record for record in result.records)


def test_report_writes_markdown_and_csv(tmp_path: Path) -> None:
    predictions = tmp_path / "pred.jsonl"
    records = [
        {
            "row_id": "ext_001",
            "model_name": "mock",
            "text": "Ejemplo",
            "fallacy_labels": ["FAL_ADHOM"],
            "fallacy_none_explicit": False,
            "confidence": 0.85,
            "explanation": "Ataque personal.",
        },
        {
            "row_id": "ext_002",
            "model_name": "mock",
            "text": "Ejemplo 2",
            "fallacy_labels": [],
            "fallacy_none_explicit": True,
            "confidence": 0.7,
            "explanation": "Sin falacia.",
        },
    ]
    write_predictions_jsonl(predictions, records)

    input_subset = tmp_path / "input.jsonl"
    write_predictions_jsonl(
        input_subset,
        [{"id": "ext_001", "text": "Ejemplo"}, {"id": "ext_002", "text": "Ejemplo 2"}],
    )

    report = tmp_path / "report.md"
    distribution = tmp_path / "distribution.csv"
    parse_errors = tmp_path / "parse_errors.csv"
    write_fallacy_prediction_report(
        predictions_path=predictions,
        input_path=input_subset,
        model_name="mock",
        report_path=report,
        label_distribution_path=distribution,
        parse_errors_path=parse_errors,
    )
    assert report.exists()
    assert "FAL_ADHOM" in report.read_text(encoding="utf-8")
    assert distribution.exists()
    assert parse_errors.exists()


def test_validate_detects_duplicate_and_missing_ids(tmp_path: Path) -> None:
    predictions = tmp_path / "dup.jsonl"
    write_predictions_jsonl(
        predictions,
        [
            {
                "row_id": "ext_001",
                "fallacy_labels": [],
                "fallacy_none_explicit": True,
                "confidence": 0.5,
                "explanation": "ok",
            },
            {
                "row_id": "ext_001",
                "fallacy_labels": ["FAL_ADHOM"],
                "fallacy_none_explicit": False,
                "confidence": 0.5,
                "explanation": "dup",
            },
        ],
    )
    summary = validate_predictions_file(predictions, FIXTURE_DATASET, text_column="text")
    assert summary.duplicate_row_ids == 1
    assert summary.missing_row_ids
