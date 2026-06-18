"""Tests for FallacyES-Political ingest, mapping, and reporting."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.external_validation.fallacyes_constants import FIXTURE_RAW_CSV
from analysis.external_validation.fallacyes_mapping import project_original_label
from analysis.external_validation.fallacyes_political_report import write_fallacyes_political_report
from scripts.external_validation.ingest_fallacyes_political import ingest_fallacyes_political
from scripts.external_validation.map_fallacyes_to_spdb import map_fallacyes_to_spdb


def test_project_ad_hominem_exact() -> None:
    result = project_original_label("Ad Hominem")
    assert result.mapping_type == "exact"
    assert result.spdb_fallacy_labels == ("FAL_ADHOM",)


def test_project_appeal_to_authority_unmapped() -> None:
    result = project_original_label("Appeal to Authority")
    assert result.mapping_type == "none"
    assert result.spdb_fallacy_labels == ()


def test_ingest_fixture_csv(tmp_path: Path) -> None:
    output = tmp_path / "ingested.jsonl"
    count = ingest_fallacyes_political(
        csv_path=FIXTURE_RAW_CSV,
        output_path=output,
        download=False,
    )
    assert count == 3
    rows = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows[0]["source_dataset"] == "fallacyes_political"
    assert rows[0]["original_label"] == "Ad Hominem"


def test_map_fixture_produces_spdb_fields(tmp_path: Path) -> None:
    ingested = tmp_path / "ingested.jsonl"
    mapped = tmp_path / "mapped.jsonl"
    ingest_fallacyes_political(csv_path=FIXTURE_RAW_CSV, output_path=ingested, download=False)
    count = map_fallacyes_to_spdb(input_path=ingested, output_path=mapped)
    assert count == 3
    rows = [json.loads(line) for line in mapped.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert rows[0]["spdb_fallacy_labels"] == ["FAL_ADHOM"]
    assert rows[1]["spdb_fallacy_labels"] == ["FAL_DILEMMA"]
    assert rows[2]["mapping_type"] == "none"


def test_report_writes_compatibility_framing(tmp_path: Path) -> None:
    ingested = tmp_path / "ingested.jsonl"
    mapped = tmp_path / "mapped.jsonl"
    predictions = tmp_path / "pred.jsonl"
    report = tmp_path / "report.md"
    ingest_fallacyes_political(csv_path=FIXTURE_RAW_CSV, output_path=ingested, download=False)
    map_fallacyes_to_spdb(input_path=ingested, output_path=mapped)
    predictions.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "row_id": "fep_1993-05-24_0001",
                        "model_name": "mock",
                        "text": "ejemplo",
                        "fallacy_labels": ["FAL_ADHOM"],
                        "fallacy_none_explicit": False,
                        "confidence": 0.8,
                        "explanation": "Ataque personal.",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "row_id": "fep_1993-05-24_0002",
                        "model_name": "mock",
                        "text": "ejemplo2",
                        "fallacy_labels": ["FAL_DILEMMA"],
                        "fallacy_none_explicit": False,
                        "confidence": 0.7,
                        "explanation": "Dilema falso.",
                    },
                    ensure_ascii=False,
                ),
                json.dumps(
                    {
                        "row_id": "fep_2008-03-03_0003",
                        "model_name": "mock",
                        "text": "ejemplo3",
                        "fallacy_labels": [],
                        "fallacy_none_explicit": True,
                        "confidence": 0.6,
                        "explanation": "Sin proyección SPDB.",
                    },
                    ensure_ascii=False,
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    write_fallacyes_political_report(
        ingested_path=ingested,
        mapped_path=mapped,
        predictions_path=predictions,
        model_name="mock",
        report_path=report,
    )
    text = report.read_text(encoding="utf-8")
    assert "preliminary cross-dataset fallacy projection" in text
    assert "full SPDB validation" in text
