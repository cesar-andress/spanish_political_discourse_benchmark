"""Build multilabel evaluation pairs and export external validation metrics."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set

from analysis.external_validation.fallacy_constants import (
    DEFAULT_REPORT_DIR,
    SPDB_FAL_LABELS,
)
from analysis.external_validation.fallacy_validator import load_predictions_jsonl
from analysis.external_validation.multilabel_metrics import (
    MultilabelMetrics,
    compute_multilabel_metrics,
    normalize_spdb_label_set,
)

DEFAULT_METRICS_JSON = DEFAULT_REPORT_DIR / "metrics.json"
DEFAULT_METRICS_MD = DEFAULT_REPORT_DIR / "metrics.md"


@dataclass(frozen=True)
class EvaluationPair:
    row_id: str
    y_true: Set[str]
    y_pred: Set[str]
    mapping_type: str | None = None


def _load_jsonl(path: Path) -> List[dict]:
    records: List[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_evaluation_pairs(
    mapped_rows: Sequence[dict],
    predictions: Sequence[dict],
    *,
    mapping_types: Sequence[str] | None = None,
    require_gold_labels: bool = True,
    prediction_id_field: str = "row_id",
    mapped_id_field: str = "id",
    gold_field: str = "spdb_fallacy_labels",
    pred_field: str = "fallacy_labels",
) -> List[EvaluationPair]:
    mapped_by_id = {row[mapped_id_field]: row for row in mapped_rows}
    allowed_types = set(mapping_types) if mapping_types else None
    pairs: List[EvaluationPair] = []

    for prediction in predictions:
        if prediction.get("_parse_error"):
            continue
        row_id = str(prediction.get(prediction_id_field, "")).strip()
        mapped = mapped_by_id.get(row_id)
        if mapped is None:
            continue
        mapping_type = str(mapped.get("mapping_type", "none"))
        if allowed_types is not None and mapping_type not in allowed_types:
            continue
        gold = normalize_spdb_label_set(mapped.get(gold_field) or [])
        if require_gold_labels and not gold:
            continue
        pred = normalize_spdb_label_set(prediction.get(pred_field) or [])
        pairs.append(
            EvaluationPair(
                row_id=row_id,
                y_true=set(gold),
                y_pred=set(pred),
                mapping_type=mapping_type,
            )
        )
    return pairs


def evaluate_mapped_dataset(
    *,
    mapped_path: Path,
    predictions_path: Path,
    dataset_name: str,
    model_name: str,
    mapping_types: Sequence[str] | None = None,
    require_gold_labels: bool = True,
) -> Dict[str, object]:
    mapped_rows = _load_jsonl(mapped_path)
    predictions = load_predictions_jsonl(predictions_path)
    pairs = build_evaluation_pairs(
        mapped_rows,
        predictions,
        mapping_types=mapping_types,
        require_gold_labels=require_gold_labels,
    )
    y_true = [pair.y_true for pair in pairs]
    y_pred = [pair.y_pred for pair in pairs]
    metrics = compute_multilabel_metrics(y_true, y_pred, labels=SPDB_FAL_LABELS)

    mapping_filter = list(mapping_types) if mapping_types else None
    return {
        "dataset": dataset_name,
        "model": model_name,
        "mapped_path": str(mapped_path),
        "predictions_path": str(predictions_path),
        "mapping_types_filter": mapping_filter,
        "require_gold_labels": require_gold_labels,
        "label_set": list(SPDB_FAL_LABELS),
        "metrics": metrics.to_dict(),
    }


def write_metrics_reports(
    payload: Dict[str, object],
    *,
    json_path: Path = DEFAULT_METRICS_JSON,
    markdown_path: Path = DEFAULT_METRICS_MD,
) -> tuple[Path, Path]:
    json_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    metrics = payload["metrics"]
    lines = [
        "# External validation — multilabel metrics",
        "",
        "**Framing:** preliminary cross-dataset fallacy projection (not full SPDB validation).",
        "",
        f"**Dataset:** `{payload.get('dataset')}`  ",
        f"**Model:** `{payload.get('model')}`  ",
        f"**Evaluated samples:** {metrics['n_samples']}  ",
        f"**Label inventory:** {metrics['n_labels']} SPDB fallacy codes",
        "",
    ]
    if payload.get("mapping_types_filter"):
        lines.append(f"**Mapping-type filter:** {', '.join(payload['mapping_types_filter'])}  ")
        lines.append("")

    lines.extend(
        [
            "## Multilabel metrics",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Micro Precision | {metrics['micro_precision']:.4f} |",
            f"| Micro Recall | {metrics['micro_recall']:.4f} |",
            f"| Micro F1 | {metrics['micro_f1']:.4f} |",
            f"| Macro Precision | {metrics['macro_precision']:.4f} |",
            f"| Macro Recall | {metrics['macro_recall']:.4f} |",
            f"| Macro F1 | {metrics['macro_f1']:.4f} |",
            f"| Exact Match Ratio | {metrics['exact_match_ratio']:.4f} |",
            f"| Hamming Loss | {metrics['hamming_loss']:.4f} |",
            f"| Jaccard Similarity | {metrics['jaccard_similarity']:.4f} |",
            "",
            "## Per-label F1",
            "",
            "| Label | Precision | Recall | F1 | Support |",
            "|-------|----------:|-------:|---:|--------:|",
        ]
    )
    for label in SPDB_FAL_LABELS:
        stats = metrics["per_label"].get(label, {})
        lines.append(
            f"| `{label}` | {stats.get('precision', 0.0):.4f} | "
            f"{stats.get('recall', 0.0):.4f} | {stats.get('f1', 0.0):.4f} | "
            f"{stats.get('support', 0)} |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Predictions are filtered to valid SPDB `FAL_*` labels before scoring.",
            "- Gold labels come from ontology projection in the mapped external dataset.",
            "- Metrics support multi-label predictions (0–3 labels per unit).",
            "",
        ]
    )
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path


def evaluate_and_write(
    *,
    mapped_path: Path,
    predictions_path: Path,
    dataset_name: str,
    model_name: str,
    mapping_types: Sequence[str] | None = None,
    require_gold_labels: bool = True,
    json_path: Path = DEFAULT_METRICS_JSON,
    markdown_path: Path = DEFAULT_METRICS_MD,
) -> Dict[str, object]:
    payload = evaluate_mapped_dataset(
        mapped_path=mapped_path,
        predictions_path=predictions_path,
        dataset_name=dataset_name,
        model_name=model_name,
        mapping_types=mapping_types,
        require_gold_labels=require_gold_labels,
    )
    write_metrics_reports(payload, json_path=json_path, markdown_path=markdown_path)
    return payload


def main(argv: Iterable[str] | None = None) -> int:
    import argparse

    from analysis.external_validation.fallacyes_constants import (
        MAPPED_JSONL,
        MISTRAL_PREDICTIONS,
        SOURCE_DATASET,
    )

    parser = argparse.ArgumentParser(description="Evaluate multilabel metrics for mapped external datasets.")
    parser.add_argument("--mapped", type=Path, default=MAPPED_JSONL)
    parser.add_argument("--predictions", type=Path, default=MISTRAL_PREDICTIONS)
    parser.add_argument("--dataset-name", default=SOURCE_DATASET)
    parser.add_argument("--model-name", default="mistral")
    parser.add_argument(
        "--mapping-types",
        default="",
        help="Comma-separated mapping types to include (default: all rows with gold labels).",
    )
    parser.add_argument("--include-empty-gold", action="store_true")
    parser.add_argument("--json-output", type=Path, default=DEFAULT_METRICS_JSON)
    parser.add_argument("--markdown-output", type=Path, default=DEFAULT_METRICS_MD)
    args = parser.parse_args(list(argv) if argv is not None else None)

    mapping_types = [part.strip() for part in args.mapping_types.split(",") if part.strip()] or None
    payload = evaluate_and_write(
        mapped_path=args.mapped,
        predictions_path=args.predictions,
        dataset_name=args.dataset_name,
        model_name=args.model_name,
        mapping_types=mapping_types,
        require_gold_labels=not args.include_empty_gold,
        json_path=args.json_output,
        markdown_path=args.markdown_output,
    )
    print(f"Wrote {args.json_output}")
    print(f"Wrote {args.markdown_output}")
    print(f"Samples: {payload['metrics']['n_samples']}")
    print(f"Micro F1: {payload['metrics']['micro_f1']:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
