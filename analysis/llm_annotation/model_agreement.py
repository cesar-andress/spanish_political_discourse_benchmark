"""Multi-model agreement analysis for SPDB LLM annotations."""

from __future__ import annotations

import csv
import math
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from analysis.llm_annotation.constants import DEFAULT_OUTPUT_DIR, DEFAULT_REPORT_DIR
from analysis.llm_annotation.validator import load_annotation_jsonl
from analysis.pilot.metrics import multi_rater_krippendorff_alpha
from scripts.analysis.agreement_metrics import cohen_kappa, confusion_matrix


PF_COLUMN = "pragmatic_function"
FALLACY_COLUMN = "fallacy_labels"

DISCLAIMER = (
    "This is not human validation. It measures model convergence and disagreement only."
)


@dataclass(frozen=True)
class ModelAnnotationMatrix:
    model_names: List[str]
    unit_ids: List[str]
    pf_labels: List[List[str]]
    fallacy_labels: List[List[str]]
    parse_failure_rates: Dict[str, float]


@dataclass(frozen=True)
class ModelAgreementSummary:
    matrix: ModelAnnotationMatrix
    pf_distribution: Dict[str, Dict[str, int]]
    fallacy_distribution: Dict[str, Dict[str, int]]
    pairwise_observed_agreement: List[Dict[str, object]]
    pairwise_cohen_kappa: List[Dict[str, object]]
    krippendorff_alpha_pf: float
    krippendorff_alpha_fallacy: float
    unanimous_rate_pf: float
    majority_rate_pf: float
    full_disagreement_rate_pf: float
    mean_entropy_pf: float
    unit_entropy_pf: List[Dict[str, object]]
    top_disagreement_pairs_pf: List[Tuple[str, str, int, float]]
    max_disagreement_units_pf: List[Dict[str, object]]


def discover_model_jsonl_files(directory: Path) -> List[Path]:
    if not directory.exists():
        return []
    return sorted(directory.glob("*_pilot_100.jsonl"))


def _fallacy_signature(record: dict) -> str:
    labels = record.get(FALLACY_COLUMN, [])
    if isinstance(labels, str):
        labels = [part.strip() for part in labels.split("|") if part.strip()]
    if not isinstance(labels, list):
        return ""
    cleaned = sorted({str(label).strip() for label in labels if str(label).strip()})
    return "|".join(cleaned)


def _pf_label(record: dict) -> str | None:
    if record.get("_parse_error"):
        return None
    label = str(record.get(PF_COLUMN, "")).strip()
    return label or None


def load_model_matrices(paths: Sequence[Path]) -> ModelAnnotationMatrix:
    if not paths:
        raise ValueError("At least one model JSONL path is required.")

    loaded: List[tuple[str, Dict[str, dict]]] = []
    for path in paths:
        model_name = path.stem.replace("_pilot_100", "")
        records = load_annotation_jsonl(path)
        by_id = {str(record.get("unit_id", "")).strip(): record for record in records if record.get("unit_id")}
        loaded.append((model_name, by_id))

    common_ids = set(loaded[0][1])
    for _, by_id in loaded[1:]:
        common_ids &= set(by_id)
    unit_ids = sorted(common_ids)
    if not unit_ids:
        raise ValueError("No overlapping unit_id values across model JSONL files.")

    pf_matrix: List[List[str]] = []
    fallacy_matrix: List[List[str]] = []
    parse_rates: Dict[str, float] = {}

    for model_name, by_id in loaded:
        pf_row: List[str] = []
        fallacy_row: List[str] = []
        failures = 0
        for unit_id in unit_ids:
            record = by_id[unit_id]
            pf = _pf_label(record)
            if pf is None:
                failures += 1
                pf_row.append("")
            else:
                pf_row.append(pf)
            fallacy_row.append(_fallacy_signature(record))
        pf_matrix.append(pf_row)
        fallacy_matrix.append(fallacy_row)
        parse_rates[model_name] = failures / len(unit_ids) if unit_ids else 0.0

    return ModelAnnotationMatrix(
        model_names=[name for name, _ in loaded],
        unit_ids=unit_ids,
        pf_labels=pf_matrix,
        fallacy_labels=fallacy_matrix,
        parse_failure_rates=parse_rates,
    )


def _vote_entropy(labels: Sequence[str]) -> float:
    filled = [label for label in labels if label]
    if not filled:
        return float("nan")
    counts = Counter(filled)
    total = sum(counts.values())
    entropy = 0.0
    for count in counts.values():
        p = count / total
        entropy -= p * math.log(p)
    return entropy


def _aggregate_confusion(label_matrix: Sequence[Sequence[str]]) -> Dict[str, Dict[str, int]]:
    aggregate: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    labels: set[str] = set()
    for i in range(len(label_matrix)):
        for j in range(i + 1, len(label_matrix)):
            result = confusion_matrix(label_matrix[i], label_matrix[j])
            labels.update(result.labels)
            for row in result.labels:
                for col in result.labels:
                    aggregate[row][col] += result.matrix[row][col]
    ordered = sorted(labels)
    return {row: {col: int(aggregate[row][col]) for col in ordered} for row in ordered}


def _top_disagreement_pairs(matrix: Dict[str, Dict[str, int]]) -> List[Tuple[str, str, int, float]]:
    labels = sorted(matrix)
    off_total = sum(matrix[row][col] for row in labels for col in labels if row != col)
    pairs: List[Tuple[str, str, int, float]] = []
    for row in labels:
        for col in labels:
            if row == col:
                continue
            count = matrix[row][col]
            if count:
                mass = count / off_total if off_total else 0.0
                pairs.append((row, col, count, mass))
    pairs.sort(key=lambda item: item[2], reverse=True)
    return pairs


def _label_distribution(matrix: ModelAnnotationMatrix, row_index: int, field: str) -> Dict[str, int]:
    rows = matrix.pf_labels if field == PF_COLUMN else matrix.fallacy_labels
    counts = Counter(label for label in rows[row_index] if label)
    return dict(sorted(counts.items()))


def _consensus_rates(label_rows: Sequence[Sequence[str]], n_models: int) -> tuple[float, float, float]:
    unanimous = majority = full_disagreement = 0
    n_units = len(label_rows[0]) if label_rows else 0
    for unit_index in range(n_units):
        labels = [row[unit_index] for row in label_rows if row[unit_index]]
        if not labels:
            continue
        counts = Counter(labels)
        unique = len(counts)
        top = counts.most_common(1)[0][1]
        if unique == 1:
            unanimous += 1
        if top >= math.ceil(n_models / 2):
            majority += 1
        if unique == n_models and n_models >= 2:
            full_disagreement += 1
    denominator = n_units if n_units else 1
    return unanimous / denominator, majority / denominator, full_disagreement / denominator


def compute_model_agreement(matrix: ModelAnnotationMatrix) -> ModelAgreementSummary:
    pf_rows_for_pairs = [
        [label or "MISSING" for label in row]
        for row in matrix.pf_labels
    ]

    pf_distribution = {
        model: _label_distribution(matrix, index, PF_COLUMN)
        for index, model in enumerate(matrix.model_names)
    }
    fallacy_distribution = {
        model: _label_distribution(matrix, index, FALLACY_COLUMN)
        for index, model in enumerate(matrix.model_names)
    }

    pairwise_agreement: List[Dict[str, object]] = []
    pairwise_kappa: List[Dict[str, object]] = []
    for i in range(len(matrix.model_names)):
        for j in range(i + 1, len(matrix.model_names)):
            left = matrix.model_names[i]
            right = matrix.model_names[j]
            comparable = [
                (a, b)
                for a, b in zip(matrix.pf_labels[i], matrix.pf_labels[j], strict=True)
                if a and b
            ]
            if not comparable:
                observed = float("nan")
                kappa = float("nan")
            else:
                values_a, values_b = zip(*comparable)
                result = cohen_kappa(values_a, values_b)
                observed = result.observed_agreement
                kappa = result.kappa
            pairwise_agreement.append(
                {
                    "model_a": left,
                    "model_b": right,
                    "field": PF_COLUMN,
                    "observed_agreement": observed,
                    "n_units": len(comparable),
                }
            )
            pairwise_kappa.append(
                {
                    "model_a": left,
                    "model_b": right,
                    "field": PF_COLUMN,
                    "cohen_kappa": kappa,
                    "n_units": len(comparable),
                }
            )

    alpha_pf = multi_rater_krippendorff_alpha(pf_rows_for_pairs, column=PF_COLUMN).alpha
    alpha_fallacy = multi_rater_krippendorff_alpha(matrix.fallacy_labels, column=FALLACY_COLUMN).alpha
    unanimous, majority, full_disagreement = _consensus_rates(
        matrix.pf_labels,
        len(matrix.model_names),
    )

    unit_entropy: List[Dict[str, object]] = []
    for unit_index, unit_id in enumerate(matrix.unit_ids):
        labels = [row[unit_index] for row in matrix.pf_labels if row[unit_index]]
        unit_entropy.append(
            {
                "unit_id": unit_id,
                "entropy": _vote_entropy(labels),
                "labels": "|".join(labels),
                "unique_labels": len(set(labels)),
            }
        )
    entropies = [row["entropy"] for row in unit_entropy if row["entropy"] == row["entropy"]]
    mean_entropy = statistics.mean(entropies) if entropies else float("nan")

    confusion = _aggregate_confusion(pf_rows_for_pairs)
    top_pairs = _top_disagreement_pairs(confusion)
    max_unique = max((row["unique_labels"] for row in unit_entropy), default=0)
    max_disagreement_units = [
        row for row in unit_entropy if row["unique_labels"] == max_unique and max_unique > 1
    ]
    max_disagreement_units.sort(key=lambda item: item["entropy"], reverse=True)

    return ModelAgreementSummary(
        matrix=matrix,
        pf_distribution=pf_distribution,
        fallacy_distribution=fallacy_distribution,
        pairwise_observed_agreement=pairwise_agreement,
        pairwise_cohen_kappa=pairwise_kappa,
        krippendorff_alpha_pf=alpha_pf,
        krippendorff_alpha_fallacy=alpha_fallacy,
        unanimous_rate_pf=unanimous,
        majority_rate_pf=majority,
        full_disagreement_rate_pf=full_disagreement,
        mean_entropy_pf=mean_entropy,
        unit_entropy_pf=unit_entropy,
        top_disagreement_pairs_pf=top_pairs,
        max_disagreement_units_pf=max_disagreement_units,
    )


def write_model_scores_csv(summary: ModelAgreementSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["model", "field", "label", "count", "parse_failure_rate"],
        )
        writer.writeheader()
        for model in summary.matrix.model_names:
            rate = summary.matrix.parse_failure_rates.get(model, 0.0)
            for label, count in summary.pf_distribution.get(model, {}).items():
                writer.writerow(
                    {
                        "model": model,
                        "field": PF_COLUMN,
                        "label": label,
                        "count": count,
                        "parse_failure_rate": f"{rate:.4f}",
                    }
                )
            for label, count in summary.fallacy_distribution.get(model, {}).items():
                writer.writerow(
                    {
                        "model": model,
                        "field": FALLACY_COLUMN,
                        "label": label,
                        "count": count,
                        "parse_failure_rate": f"{rate:.4f}",
                    }
                )


def write_pairwise_agreement_csv(summary: ModelAgreementSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["model_a", "model_b", "field", "observed_agreement", "cohen_kappa", "n_units"],
        )
        writer.writeheader()
        kappa_by_pair = {
            (row["model_a"], row["model_b"]): row["cohen_kappa"]
            for row in summary.pairwise_cohen_kappa
        }
        for row in summary.pairwise_observed_agreement:
            writer.writerow(
                {
                    "model_a": row["model_a"],
                    "model_b": row["model_b"],
                    "field": row["field"],
                    "observed_agreement": _fmt(row["observed_agreement"]),
                    "cohen_kappa": _fmt(kappa_by_pair.get((row["model_a"], row["model_b"]), float("nan"))),
                    "n_units": row["n_units"],
                }
            )


def write_disagreement_units_csv(summary: ModelAgreementSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["unit_id", "entropy", "unique_labels", "model_labels"],
        )
        writer.writeheader()
        for row in summary.max_disagreement_units_pf:
            writer.writerow(
                {
                    "unit_id": row["unit_id"],
                    "entropy": _fmt(row["entropy"]),
                    "unique_labels": row["unique_labels"],
                    "model_labels": row["labels"],
                }
            )


def write_comparison_report(summary: ModelAgreementSummary, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    matrix = summary.matrix
    lines = [
        "# Ollama multi-model comparison",
        "",
        f"> **Note:** {DISCLAIMER}",
        "",
        f"Models compared: {len(matrix.model_names)}",
        f"Units compared: {len(matrix.unit_ids)}",
        "",
        "## Pragmatic function consensus",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Unanimous agreement rate | {_fmt(summary.unanimous_rate_pf)} |",
        f"| Majority agreement rate | {_fmt(summary.majority_rate_pf)} |",
        f"| Full disagreement rate | {_fmt(summary.full_disagreement_rate_pf)} |",
        f"| Mean vote entropy | {_fmt(summary.mean_entropy_pf)} |",
        f"| Krippendorff α | {_fmt(summary.krippendorff_alpha_pf)} |",
        "",
        "## Fallacy-label convergence",
        "",
        f"| Krippendorff α (fallacy signature) | {_fmt(summary.krippendorff_alpha_fallacy)} |",
        "",
        "## Per-model pragmatic-function distribution",
        "",
    ]
    for model, distribution in summary.pf_distribution.items():
        lines.append(f"### `{model}`")
        lines.append("")
        lines.append("| Label | Count |")
        lines.append("|-------|------:|")
        for label, count in sorted(distribution.items()):
            lines.append(f"| `{label}` | {count} |")
        lines.append("")

    lines.extend(
        [
            "## Pairwise pragmatic-function agreement",
            "",
            "| Model A | Model B | Observed agreement | Cohen κ | Units |",
            "|---------|---------|-------------------:|--------:|------:|",
        ]
    )
    kappa_by_pair = {
        (row["model_a"], row["model_b"]): row["cohen_kappa"]
        for row in summary.pairwise_cohen_kappa
    }
    for row in summary.pairwise_observed_agreement:
        pair = (row["model_a"], row["model_b"])
        lines.append(
            f"| `{row['model_a']}` | `{row['model_b']}` | "
            f"{_fmt(row['observed_agreement'])} | {_fmt(kappa_by_pair.get(pair, float('nan')))} | {row['n_units']} |"
        )

    lines.extend(["", "## Top pragmatic-function disagreement pairs", ""])
    if summary.top_disagreement_pairs_pf:
        lines.extend(["| From | To | Count | Mass |", "|------|----|------:|-----:|"])
        for row, col, count, mass in summary.top_disagreement_pairs_pf[:10]:
            lines.append(f"| `{row}` | `{col}` | {count} | {mass:.3f} |")
    else:
        lines.append("_No off-diagonal disagreements observed._")

    lines.extend(["", "## Units with maximum pragmatic-function disagreement", ""])
    if summary.max_disagreement_units_pf:
        lines.extend(["| unit_id | entropy | labels |", "|---------|--------:|--------|"])
        for row in summary.max_disagreement_units_pf[:20]:
            lines.append(
                f"| `{row['unit_id']}` | {_fmt(row['entropy'])} | `{row['labels']}` |"
            )
    else:
        lines.append("_All compared units had unanimous model labels._")

    lines.extend(["", "## Parse-failure rates", ""])
    for model, rate in summary.matrix.parse_failure_rates.items():
        lines.append(f"- `{model}`: {rate:.3f}")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: float) -> str:
    if isinstance(value, float) and value != value:
        return "n/a"
    return f"{value:.4f}"


@dataclass
class ModelComparisonOutputs:
    summary: ModelAgreementSummary
    report_path: Path
    scores_path: Path
    pairwise_path: Path
    disagreement_path: Path


def run_model_comparison(
    *,
    jsonl_paths: Sequence[Path] | None = None,
    annotations_dir: Path = DEFAULT_OUTPUT_DIR,
    report_dir: Path = DEFAULT_REPORT_DIR,
) -> ModelComparisonOutputs:
    paths = list(jsonl_paths) if jsonl_paths else discover_model_jsonl_files(annotations_dir)
    if len(paths) < 2:
        raise ValueError("At least two model JSONL files are required for comparison.")

    matrix = load_model_matrices(paths)
    summary = compute_model_agreement(matrix)

    report_path = report_dir / "ollama_model_comparison.md"
    scores_path = report_dir / "ollama_model_scores.csv"
    pairwise_path = report_dir / "ollama_pairwise_agreement.csv"
    disagreement_path = report_dir / "ollama_disagreement_units.csv"

    write_comparison_report(summary, report_path)
    write_model_scores_csv(summary, scores_path)
    write_pairwise_agreement_csv(summary, pairwise_path)
    write_disagreement_units_csv(summary, disagreement_path)

    return ModelComparisonOutputs(
        summary=summary,
        report_path=report_path,
        scores_path=scores_path,
        pairwise_path=pairwise_path,
        disagreement_path=disagreement_path,
    )
