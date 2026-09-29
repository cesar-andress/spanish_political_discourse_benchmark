"""Tests for external multilabel evaluation metrics."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.external_validation.external_metrics_report import (
    build_evaluation_pairs,
    evaluate_and_write,
)
from analysis.external_validation.multilabel_metrics import compute_multilabel_metrics


def test_perfect_multilabel_prediction() -> None:
    y_true = [{"FAL_ADHOM"}, {"FAL_STRAW", "FAL_EMOTION"}]
    y_pred = [{"FAL_ADHOM"}, {"FAL_STRAW", "FAL_EMOTION"}]
    metrics = compute_multilabel_metrics(y_true, y_pred, labels=["FAL_ADHOM", "FAL_STRAW", "FAL_EMOTION"])
    assert metrics.exact_match_ratio == 1.0
    assert metrics.micro_f1 == 1.0
    assert metrics.macro_f1 == 1.0
    assert metrics.hamming_loss == 0.0
    assert metrics.jaccard_similarity == 1.0


def test_partial_overlap_multilabel() -> None:
    y_true = [{"FAL_ADHOM", "FAL_STRAW"}]
    y_pred = [{"FAL_ADHOM"}]
    metrics = compute_multilabel_metrics(y_true, y_pred, labels=["FAL_ADHOM", "FAL_STRAW"])
    assert metrics.exact_match_ratio == 0.0
    assert metrics.jaccard_similarity == 0.5
    assert metrics.hamming_loss == 0.5
    assert metrics.micro_recall == 0.5
    assert metrics.micro_precision == 1.0


def test_empty_sets_jaccard_and_exact_match() -> None:
    y_true = [set()]
    y_pred = [set()]
    metrics = compute_multilabel_metrics(y_true, y_pred, labels=["FAL_ADHOM"])
    assert metrics.exact_match_ratio == 1.0
    assert metrics.jaccard_similarity == 1.0
    assert metrics.hamming_loss == 0.0


def test_build_pairs_filters_invalid_prediction_labels() -> None:
    mapped = [
        {"id": "r1", "spdb_fallacy_labels": ["FAL_ADHOM"], "mapping_type": "exact"},
    ]
    predictions = [
        {
            "row_id": "r1",
            "fallacy_labels": ["FAL_ADHOM", "FAL_INVENTED"],
            "fallacy_none_explicit": False,
            "confidence": 0.8,
            "explanation": "x",
        }
    ]
    pairs = build_evaluation_pairs(mapped, predictions)
    assert len(pairs) == 1
    assert pairs[0].y_pred == {"FAL_ADHOM"}


def test_evaluate_mapped_dataset_and_write_reports(tmp_path: Path) -> None:
    mapped = tmp_path / "mapped.jsonl"
    predictions = tmp_path / "pred.jsonl"
    mapped.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "id": "r1",
                        "text": "a",
                        "original_label": "Ad Hominem",
                        "spdb_fallacy_labels": ["FAL_ADHOM"],
                        "mapping_type": "exact",
                        "mapping_confidence": 1.0,
                        "mapping_notes": "",
                    }
                ),
                json.dumps(
                    {
                        "id": "r2",
                        "text": "b",
                        "original_label": "Strawman",
                        "spdb_fallacy_labels": ["FAL_STRAW"],
                        "mapping_type": "exact",
                        "mapping_confidence": 1.0,
                        "mapping_notes": "",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    predictions.write_text(
        "\n".join(
            [
                json.dumps(
                    {
                        "row_id": "r1",
                        "fallacy_labels": ["FAL_ADHOM"],
                        "fallacy_none_explicit": False,
                        "confidence": 0.9,
                        "explanation": "ok",
                    }
                ),
                json.dumps(
                    {
                        "row_id": "r2",
                        "fallacy_labels": ["FAL_ADHOM"],
                        "fallacy_none_explicit": False,
                        "confidence": 0.5,
                        "explanation": "miss",
                    }
                ),
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    json_out = tmp_path / "metrics.json"
    md_out = tmp_path / "metrics.md"
    payload = evaluate_and_write(
        mapped_path=mapped,
        predictions_path=predictions,
        dataset_name="fixture",
        model_name="mock",
        json_path=json_out,
        markdown_path=md_out,
    )
    assert payload["metrics"]["n_samples"] == 2
    assert payload["metrics"]["exact_match_ratio"] == 0.5
    assert json_out.exists()
    assert "Micro F1" in md_out.read_text(encoding="utf-8")


def test_mapping_type_filter() -> None:
    mapped = [
        {"id": "r1", "spdb_fallacy_labels": ["FAL_ADHOM"], "mapping_type": "exact"},
        {"id": "r2", "spdb_fallacy_labels": ["FAL_GENERAL"], "mapping_type": "approximate"},
    ]
    predictions = [
        {"row_id": "r1", "fallacy_labels": ["FAL_ADHOM"]},
        {"row_id": "r2", "fallacy_labels": ["FAL_GENERAL"]},
    ]
    pairs = build_evaluation_pairs(mapped, predictions, mapping_types=("exact",))
    assert len(pairs) == 1
    assert pairs[0].row_id == "r1"
