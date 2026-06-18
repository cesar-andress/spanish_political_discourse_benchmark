"""Report for FallacyES-Political preliminary cross-dataset fallacy projection."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Sequence, Set

from analysis.external_validation.fallacyes_constants import (
    FALLACYES_REPORT,
    INGESTED_JSONL,
    MAPPED_JSONL,
    MISTRAL_PREDICTIONS,
    ZENODO_RECORD_URL,
)
from analysis.external_validation.fallacy_validator import (
    load_predictions_jsonl,
    validate_predictions_file,
)


@dataclass
class ComparisonMetrics:
    comparable_rows: int = 0
    overlap_matches: int = 0
    primary_matches: int = 0


def _load_jsonl(path: Path) -> List[dict]:
    records: List[dict] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def _confidence_average(records: Sequence[dict]) -> float:
    values = [
        float(record["confidence"])
        for record in records
        if not record.get("_parse_error") and isinstance(record.get("confidence"), (int, float))
    ]
    return sum(values) / len(values) if values else 0.0


def _none_rate(records: Sequence[dict]) -> float:
    valid = [record for record in records if not record.get("_parse_error")]
    if not valid:
        return 0.0
    return sum(1 for record in valid if record.get("fallacy_none_explicit")) / len(valid)


def _compare_predictions(mapped_rows: Sequence[dict], predictions: Sequence[dict]) -> ComparisonMetrics:
    mapped_by_id = {row["id"]: row for row in mapped_rows}
    metrics = ComparisonMetrics()
    for prediction in predictions:
        if prediction.get("_parse_error"):
            continue
        mapped = mapped_by_id.get(prediction.get("row_id"))
        if not mapped:
            continue
        if mapped.get("mapping_type") not in {"exact", "partial"}:
            continue
        gold: Set[str] = set(mapped.get("spdb_fallacy_labels") or [])
        if not gold:
            continue
        predicted: Set[str] = set(prediction.get("fallacy_labels") or [])
        metrics.comparable_rows += 1
        if predicted & gold:
            metrics.overlap_matches += 1
        primary = next(iter(gold))
        if primary in predicted:
            metrics.primary_matches += 1
    return metrics


def write_fallacyes_political_report(
    *,
    ingested_path: Path,
    mapped_path: Path,
    predictions_path: Path,
    model_name: str,
    report_path: Path = FALLACYES_REPORT,
) -> Path:
    ingested_rows = _load_jsonl(ingested_path)
    mapped_rows = _load_jsonl(mapped_path)
    predictions = load_predictions_jsonl(predictions_path)
    validation = validate_predictions_file(predictions_path, ingested_path, text_column="text", id_column="id")

    mapping_counts = Counter(row.get("mapping_type", "none") for row in mapped_rows)
    mapped_with_spdb = sum(1 for row in mapped_rows if row.get("spdb_fallacy_labels"))
    mapping_coverage = mapped_with_spdb / len(mapped_rows) if mapped_rows else 0.0

    fal_counts: Counter[str] = Counter()
    for record in predictions:
        if record.get("_parse_error"):
            continue
        for label in record.get("fallacy_labels", []) or []:
            fal_counts[str(label)] += 1

    comparison = _compare_predictions(mapped_rows, predictions)
    overlap_rate = (
        comparison.overlap_matches / comparison.comparable_rows if comparison.comparable_rows else 0.0
    )
    primary_rate = (
        comparison.primary_matches / comparison.comparable_rows if comparison.comparable_rows else 0.0
    )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# FallacyES-Political — preliminary cross-dataset fallacy projection",
        "",
        "**Framing:** external compatibility analysis / preliminary cross-dataset fallacy projection. "
        "This is **not** full SPDB validation, **not** human validation, and **does not** modify the SPDB ontology.",
        "",
        f"**Model:** `{model_name}`  ",
        f"**Source dataset:** [FallacyES-Political]({ZENODO_RECORD_URL})  ",
        f"**Ingested records:** {len(ingested_rows)}  ",
        f"**Mapped records:** {len(mapped_rows)}  ",
        f"**LLM predictions:** {validation.total_records}  ",
        "",
        "## Dataset ingestion",
        "",
        f"- Official source: {ZENODO_RECORD_URL}",
        f"- Normalized JSONL: `{ingested_path}`",
        f"- Records ingested: {len(ingested_rows)}",
        "",
        "## SPDB label projection (FallacyES-Political → SPDB)",
        "",
        f"- Mapping coverage (rows with ≥1 projected SPDB label): **{mapping_coverage:.1%}** ({mapped_with_spdb}/{len(mapped_rows)})",
        "",
        "| Mapping type | Count | Share |",
        "|--------------|------:|------:|",
    ]
    for mapping_type in ("exact", "partial", "approximate", "none"):
        count = mapping_counts.get(mapping_type, 0)
        share = 100.0 * count / len(mapped_rows) if mapped_rows else 0.0
        lines.append(f"| {mapping_type} | {count} | {share:.1f}% |")
    lines.extend(
        [
            "",
            "## LLM batch quality (SPDB JSON schema)",
            "",
            "| Metric | Value |",
            "|--------|------:|",
            f"| Valid outputs | {validation.valid_outputs} |",
            f"| Parse failure rate | {validation.parse_failure_rate:.3f} |",
            f"| Invalid label rate | {validation.invalid_label_rate:.3f} |",
            f"| FAL_NONE rate (`fallacy_none_explicit=true`) | {_none_rate(predictions):.3f} |",
            f"| Average confidence | {_confidence_average(predictions):.3f} |",
            "",
            "## SPDB fallacy label distribution (LLM predictions)",
            "",
            "| Label | Count | Share |",
            "|-------|------:|------:|",
        ]
    )
    total_labels = sum(fal_counts.values()) or 1
    for label, count in fal_counts.most_common():
        lines.append(f"| `{label}` | {count} | {100.0 * count / total_labels:.1f}% |")
    if not fal_counts:
        lines.append("| _none predicted_ | 0 | 0.0% |")

    lines.extend(
        [
            "",
            "## Comparison against projected labels (exact + partial mappings only)",
            "",
            f"- Comparable rows: {comparison.comparable_rows}",
            f"- Any-label overlap rate: **{overlap_rate:.1%}**",
            f"- Primary projected-label match rate: **{primary_rate:.1%}**",
            "",
            "Comparison is indicative only: FallacyES-Political spans, label granularity, and debate genre "
            "differ from SPDB discourse units. Multi-label and approximate mappings are excluded from strict comparison.",
            "",
            "## Limitations",
            "",
            "- FallacyES-Political annotates debate excerpts with 16+ fallacy types; SPDB uses seven political fallacy codes plus explicit none.",
            "- Not all external labels project onto SPDB (`none` and unmapped classes remain).",
            "- Zero-shot LLM projection is not calibrated against SPDB gold and must not be read as benchmark accuracy.",
            "- Debate transcripts ≠ parliamentary plenary units; register and interaction context differ.",
            "- No human adjudication was performed for this compatibility run.",
            "",
        ]
    )
    if validation.errors:
        lines.extend(["## Validation notes", ""])
        for error in validation.errors[:20]:
            lines.append(f"- {error}")
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")

    distribution_path = report_path.parent / "fallacyes_political_label_distribution.csv"
    with distribution_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["label", "count", "share"])
        for label, count in fal_counts.most_common():
            writer.writerow([label, count, f"{100.0 * count / total_labels:.4f}"])

    return report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate FallacyES-Political external compatibility report.")
    parser.add_argument("--ingested", type=Path, default=INGESTED_JSONL)
    parser.add_argument("--mapped", type=Path, default=MAPPED_JSONL)
    parser.add_argument("--predictions", type=Path, default=MISTRAL_PREDICTIONS)
    parser.add_argument("--model-name", default="mistral")
    parser.add_argument("--report", type=Path, default=FALLACYES_REPORT)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    path = write_fallacyes_political_report(
        ingested_path=args.ingested,
        mapped_path=args.mapped,
        predictions_path=args.predictions,
        model_name=args.model_name,
        report_path=args.report,
    )
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
