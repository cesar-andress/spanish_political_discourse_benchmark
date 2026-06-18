#!/usr/bin/env python3
"""Audit pragmatic-function labels for predictability from trivial corpus signals."""

from __future__ import annotations

import argparse
import csv
import json
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Mapping, Sequence, Tuple

DEFAULT_INPUT = Path("annotation/pilot_001/pilot_100_units_annotator_a.csv")
DEFAULT_JSONL = Path("data/processed/parlamint_100_units.jsonl")
DEFAULT_MD = Path("reports/artifact_audit.md")
DEFAULT_FIGURES = Path("figures/artifact_audit")

LABEL_COLUMN = "pragmatic_function"
HIGH_ACCURACY_THRESHOLD = 0.55
SKEW_THRESHOLD = 0.40


@dataclass(frozen=True)
class AuditRecord:
    unit_id: str
    text: str
    label: str
    char_length: int
    token_count: int
    speaker_role: str
    speaker_party: str
    source_type: str


@dataclass(frozen=True)
class BaselineResult:
    name: str
    accuracy: float
    macro_f1: float
    flagged: bool
    note: str


def _token_count(text: str) -> int:
    return len(text.split())


def load_jsonl_index(path: Path) -> Dict[str, Dict[str, Any]]:
    index: Dict[str, Dict[str, Any]] = {}
    if not path.exists():
        return index
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            unit = json.loads(line)
            unit_id = unit.get("unit_id")
            if unit_id:
                index[str(unit_id)] = unit
    return index


def _speaker_role_from_unit(unit: Mapping[str, Any]) -> str:
    meta = unit.get("metadata") or {}
    role = meta.get("speaker_role") or unit.get("speaker_role")
    if role:
        return str(role)
    source_type = str(meta.get("source_type") or unit.get("source_type") or "unknown")
    if source_type == "parliamentary":
        return "legislator"
    if source_type == "manifesto":
        return "party_org"
    return "unknown"


def load_audit_records(
    csv_path: Path,
    *,
    jsonl_path: Path | None = None,
) -> List[AuditRecord]:
    jsonl_index = load_jsonl_index(jsonl_path) if jsonl_path else {}
    records: List[AuditRecord] = []

    with csv_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError(f"Missing header row in {csv_path}")
        if LABEL_COLUMN not in reader.fieldnames:
            raise ValueError(f"{csv_path} is missing required column '{LABEL_COLUMN}'")

        for row_index, row in enumerate(reader, start=2):
            label = (row.get(LABEL_COLUMN) or "").strip()
            if not label:
                continue
            unit_id = (row.get("unit_id") or "").strip()
            text = row.get("text") or ""
            unit = jsonl_index.get(unit_id, {})
            meta = unit.get("metadata") or {}

            speaker_party = (row.get("speaker_party") or meta.get("speaker_party") or "unknown").strip()
            speaker_role = (row.get("speaker_role") or _speaker_role_from_unit(unit)).strip()
            source_type = (row.get("source_type") or meta.get("source_type") or "unknown").strip()
            char_length = int(unit.get("character_count") or len(text))
            token_count = int(unit.get("token_count") or _token_count(text))

            records.append(
                AuditRecord(
                    unit_id=unit_id or f"row-{row_index}",
                    text=text,
                    label=label,
                    char_length=char_length,
                    token_count=token_count,
                    speaker_role=speaker_role or "unknown",
                    speaker_party=speaker_party or "unknown",
                    source_type=source_type or "unknown",
                )
            )

    if not records:
        raise ValueError(
            f"No labeled rows found in {csv_path}. "
            f"Ensure '{LABEL_COLUMN}' is filled for audited units."
        )
    return records


def label_distribution(records: Sequence[AuditRecord]) -> Counter[str]:
    return Counter(record.label for record in records)


def average_by_label(
    records: Sequence[AuditRecord],
    metric: Callable[[AuditRecord], int],
) -> Dict[str, float]:
    buckets: Dict[str, List[int]] = defaultdict(list)
    for record in records:
        buckets[record.label].append(metric(record))
    return {label: statistics.mean(values) for label, values in sorted(buckets.items())}


def nested_distribution(
    records: Sequence[AuditRecord],
    field: Callable[[AuditRecord], str],
) -> Dict[str, Counter[str]]:
    table: Dict[str, Counter[str]] = defaultdict(Counter)
    for record in records:
        table[record.label][field(record)] += 1
    return dict(table)


def _sorted_labels(records: Sequence[AuditRecord]) -> List[str]:
    return sorted({record.label for record in records})


def _accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    if not y_true:
        return 0.0
    return sum(a == b for a, b in zip(y_true, y_pred)) / len(y_true)


def _macro_f1(y_true: Sequence[str], y_pred: Sequence[str], labels: Sequence[str]) -> float:
    scores: List[float] = []
    for label in labels:
        tp = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred == label)
        fp = sum(1 for truth, pred in zip(y_true, y_pred) if truth != label and pred == label)
        fn = sum(1 for truth, pred in zip(y_true, y_pred) if truth == label and pred != label)
        if tp == 0 and fp == 0 and fn == 0:
            continue
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        if precision + recall == 0:
            scores.append(0.0)
        else:
            scores.append(2 * precision * recall / (precision + recall))
    return statistics.mean(scores) if scores else 0.0


def stratified_folds(labels: Sequence[str], k: int, seed: int) -> List[List[int]]:
    by_label: Dict[str, List[int]] = defaultdict(list)
    for index, label in enumerate(labels):
        by_label[label].append(index)
    rng = random.Random(seed)
    folds: List[List[int]] = [[] for _ in range(k)]
    for indices in by_label.values():
        shuffled = indices[:]
        rng.shuffle(shuffled)
        for fold_index, sample_index in enumerate(shuffled):
            folds[fold_index % k].append(sample_index)
    return folds


def cross_validate(
    records: Sequence[AuditRecord],
    predictor: Callable[[Sequence[AuditRecord], Sequence[AuditRecord]], List[str]],
    *,
    seed: int = 42,
) -> Tuple[List[str], List[str]]:
    labels = [record.label for record in records]
    k = min(5, min(Counter(labels).values()))
    if k < 2:
        k = len(records)
    folds = stratified_folds(labels, k, seed)
    y_true: List[str] = []
    y_pred: List[str] = []

    for fold in folds:
        test_indices = set(fold)
        train = [records[i] for i in range(len(records)) if i not in test_indices]
        test = [records[i] for i in fold]
        predictions = predictor(train, test)
        y_true.extend(record.label for record in test)
        y_pred.extend(predictions)
    return y_true, y_pred


def _majority_label(train: Sequence[AuditRecord]) -> str:
    return Counter(record.label for record in train).most_common(1)[0][0]


def predict_majority(train: Sequence[AuditRecord], test: Sequence[AuditRecord]) -> List[str]:
    majority = _majority_label(train)
    return [majority for _ in test]


def predict_length_only(train: Sequence[AuditRecord], test: Sequence[AuditRecord]) -> List[str]:
    means: Dict[str, float] = {}
    for label in _sorted_labels(train):
        lengths = [record.token_count for record in train if record.label == label]
        means[label] = statistics.mean(lengths) if lengths else 0.0

    def nearest(length: int) -> str:
        return min(means, key=lambda label: abs(means[label] - length))

    return [nearest(record.token_count) for record in test]


def _mode_by_key(
    train: Sequence[AuditRecord],
    key: Callable[[AuditRecord], str],
) -> Tuple[Dict[str, str], str]:
    counts: Dict[str, Counter[str]] = defaultdict(Counter)
    for record in train:
        counts[key(record)][record.label] += 1
    mapping = {value: counter.most_common(1)[0][0] for value, counter in counts.items()}
    global_label = _majority_label(train)
    return mapping, global_label


def _predict_from_mapping(
    train: Sequence[AuditRecord],
    test: Sequence[AuditRecord],
    key: Callable[[AuditRecord], str],
) -> List[str]:
    mapping, fallback = _mode_by_key(train, key)
    return [mapping.get(key(record), fallback) for record in test]


def predict_speaker_role_only(
    train: Sequence[AuditRecord], test: Sequence[AuditRecord]
) -> List[str]:
    return _predict_from_mapping(train, test, lambda record: record.speaker_role)


def predict_party_only(train: Sequence[AuditRecord], test: Sequence[AuditRecord]) -> List[str]:
    return _predict_from_mapping(train, test, lambda record: record.speaker_party)


def evaluate_baselines(records: Sequence[AuditRecord], *, seed: int = 42) -> List[BaselineResult]:
    labels = _sorted_labels(records)
    random_guess = 1.0 / len(labels)
    majority_acc = max(label_distribution(records).values()) / len(records)
    predictors = [
        ("Majority-class", predict_majority),
        ("Length-only", predict_length_only),
        ("Speaker-role-only", predict_speaker_role_only),
        ("Party-only", predict_party_only),
    ]
    results: List[BaselineResult] = []
    for name, predictor in predictors:
        y_true, y_pred = cross_validate(records, predictor, seed=seed)
        accuracy = _accuracy(y_true, y_pred)
        macro_f1 = _macro_f1(y_true, y_pred, labels)
        flagged = accuracy >= HIGH_ACCURACY_THRESHOLD or (
            name != "Majority-class" and accuracy >= majority_acc + 0.10
        )
        note = ""
        if name == "Majority-class" and majority_acc >= SKEW_THRESHOLD:
            flagged = True
            note = "Label skew makes the majority class a strong trivial predictor."
        elif flagged:
            note = "Trivial signal may encode label information; review for annotation artifacts."
        if name == "Majority-class" and not note:
            note = f"Random-guess baseline ≈ {random_guess:.3f}."
        results.append(
            BaselineResult(
                name=name,
                accuracy=accuracy,
                macro_f1=macro_f1,
                flagged=flagged,
                note=note,
            )
        )
    return results


def distribution_table(
    distribution: Counter[str],
    total: int,
    *,
    label_header: str = "Label",
) -> List[str]:
    lines = [
        f"| {label_header} | Count | Share |",
        "|--------|------:|------:|",
    ]
    for label, count in distribution.most_common():
        share = 100.0 * count / total
        lines.append(f"| `{label}` | {count} | {share:.1f}% |")
    return lines


def cross_tab_table(
    nested: Mapping[str, Counter[str]],
    *,
    column_header: str,
) -> List[str]:
    columns = sorted({key for counter in nested.values() for key in counter})
    lines = [
        "| Label | " + " | ".join(f"`{column}`" for column in columns) + " |",
        "|-------|" + "|".join("------:" for _ in columns) + "|",
    ]
    for label in sorted(nested):
        counter = nested[label]
        row_total = sum(counter.values())
        cells = []
        for column in columns:
            count = counter.get(column, 0)
            share = 100.0 * count / row_total if row_total else 0.0
            cells.append(f"{count} ({share:.0f}%)")
        lines.append(f"| `{label}` | " + " | ".join(cells) + " |")
    return lines


def write_markdown(
    path: Path,
    records: Sequence[AuditRecord],
    baselines: Sequence[BaselineResult],
    *,
    input_path: Path,
    jsonl_path: Path | None,
    figures: Sequence[Path],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    total = len(records)
    distribution = label_distribution(records)
    char_means = average_by_label(records, lambda record: record.char_length)
    token_means = average_by_label(records, lambda record: record.token_count)
    role_nested = nested_distribution(records, lambda record: record.speaker_role)
    party_nested = nested_distribution(records, lambda record: record.speaker_party)
    source_nested = nested_distribution(records, lambda record: record.source_type)
    flagged = [result for result in baselines if result.flagged]

    lines = [
        "# SPDB artifact audit — pragmatic function labels",
        "",
        f"**Input:** `{input_path}`  ",
        f"**Metadata merge:** `{jsonl_path}`" if jsonl_path else "**Metadata merge:** none  ",
        f"**Generated:** {generated}  ",
        f"**Units audited:** {total}",
        "",
        "## Purpose",
        "",
        "Estimate how predictable `pragmatic_function` labels are from trivial corpus signals "
        "(length, party, speaker role, source type). High trivial baseline performance suggests "
        "potential annotation artifacts or confounds to control in modeling.",
        "",
    ]

    if flagged:
        lines.extend(
            [
                "## ⚠ Artifact warnings",
                "",
                "The following trivial predictors reached suspicious performance or reflect strong label skew:",
                "",
            ]
        )
        for result in flagged:
            lines.append(
                f"- **{result.name}** — accuracy {result.accuracy:.3f}, macro-F1 {result.macro_f1:.3f}. "
                f"{result.note}"
            )
        lines.append("")

    lines.extend(["## Label distribution", ""])
    lines.extend(distribution_table(distribution, total))
    lines.extend(
        [
            "",
            "## Average text length by label",
            "",
            "| Label | Mean characters |",
            "|-------|----------------:|",
        ]
    )
    for label, value in sorted(char_means.items()):
        lines.append(f"| `{label}` | {value:.1f} |")

    lines.extend(
        [
            "",
            "## Average token count by label",
            "",
            "| Label | Mean tokens |",
            "|-------|------------:|",
        ]
    )
    for label, value in sorted(token_means.items()):
        lines.append(f"| `{label}` | {value:.1f} |")

    lines.extend(["", "## Speaker-role distribution by label", ""])
    lines.extend(cross_tab_table(role_nested, column_header="speaker_role"))
    lines.extend(["", "## Party distribution by label", ""])
    lines.extend(cross_tab_table(party_nested, column_header="party"))
    lines.extend(["", "## Source-type distribution by label", ""])
    lines.extend(cross_tab_table(source_nested, column_header="source_type"))

    lines.extend(
        [
            "",
            "## Trivial baseline performance (stratified cross-validation)",
            "",
            "| Baseline | Accuracy | Macro-F1 | Flagged | Notes |",
            "|----------|----------:|---------:|:-------:|-------|",
        ]
    )
    for result in baselines:
        flag = "yes" if result.flagged else "no"
        lines.append(
            f"| {result.name} | {result.accuracy:.3f} | {result.macro_f1:.3f} | {flag} | {result.note} |"
        )

    lines.extend(["", "## Figures", ""])
    if figures:
        lines.extend(["| Figure | Description |", "|--------|-------------|"])
        descriptions = {
            "label_distribution.png": "Pragmatic-function label counts",
            "avg_length_by_label.png": "Mean character length by label",
            "avg_tokens_by_label.png": "Mean token count by label",
            "party_by_label.png": "Party share within each label",
            "baseline_accuracy.png": "Trivial baseline cross-validated accuracy",
        }
        for figure in figures:
            desc = descriptions.get(figure.name, figure.stem.replace("_", " "))
            lines.append(f"| `{figure.as_posix()}` | {desc} |")
    else:
        lines.append("_Figures not generated._")

    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_figures(output_dir: Path, records: Sequence[AuditRecord], baselines: Sequence[BaselineResult]) -> List[Path]:
    import matplotlib.pyplot as plt

    output_dir.mkdir(parents=True, exist_ok=True)
    written: List[Path] = []
    distribution = label_distribution(records)
    char_means = average_by_label(records, lambda record: record.char_length)
    token_means = average_by_label(records, lambda record: record.token_count)
    party_nested = nested_distribution(records, lambda record: record.speaker_party)

    def save_bar(path: Path, labels: Sequence[str], values: Sequence[float], title: str, ylabel: str) -> None:
        fig, ax = plt.subplots(figsize=(9, 5))
        ax.bar(list(labels), list(values), color="#4C72B0")
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        fig.savefig(path, dpi=150)
        plt.close(fig)
        written.append(path)

    save_bar(
        output_dir / "label_distribution.png",
        [label for label, _ in distribution.most_common()],
        [count for _, count in distribution.most_common()],
        "Pragmatic-function label distribution",
        "Units",
    )
    save_bar(
        output_dir / "avg_length_by_label.png",
        sorted(char_means),
        [char_means[label] for label in sorted(char_means)],
        "Mean character length by pragmatic function",
        "Characters",
    )
    save_bar(
        output_dir / "avg_tokens_by_label.png",
        sorted(token_means),
        [token_means[label] for label in sorted(token_means)],
        "Mean token count by pragmatic function",
        "Tokens",
    )

    parties = sorted({party for counter in party_nested.values() for party in counter})
    labels = sorted(party_nested)
    fig, ax = plt.subplots(figsize=(10, 6))
    bottom = [0.0] * len(labels)
    for party in parties:
        shares = []
        for label in labels:
            counter = party_nested[label]
            total = sum(counter.values())
            shares.append(100.0 * counter.get(party, 0) / total if total else 0.0)
        ax.bar(labels, shares, bottom=bottom, label=party)
        bottom = [base + share for base, share in zip(bottom, shares)]
    ax.set_title("Party composition within pragmatic-function labels")
    ax.set_ylabel("Share within label (%)")
    ax.tick_params(axis="x", rotation=35)
    ax.legend(loc="upper right", fontsize=8)
    fig.tight_layout()
    party_path = output_dir / "party_by_label.png"
    fig.savefig(party_path, dpi=150)
    plt.close(fig)
    written.append(party_path)

    fig, ax = plt.subplots(figsize=(8, 5))
    names = [result.name for result in baselines]
    values = [result.accuracy for result in baselines]
    colors = ["#C44E52" if result.flagged else "#55A868" for result in baselines]
    ax.bar(names, values, color=colors)
    ax.axhline(HIGH_ACCURACY_THRESHOLD, color="#999999", linestyle="--", linewidth=1, label="flag threshold")
    ax.set_ylim(0.0, 1.0)
    ax.set_title("Trivial baseline accuracy (cross-validation)")
    ax.set_ylabel("Accuracy")
    ax.tick_params(axis="x", rotation=20)
    ax.legend()
    fig.tight_layout()
    baseline_path = output_dir / "baseline_accuracy.png"
    fig.savefig(baseline_path, dpi=150)
    plt.close(fig)
    written.append(baseline_path)

    return written


def run(
    input_path: Path,
    *,
    jsonl_path: Path | None = None,
    markdown_path: Path = DEFAULT_MD,
    figures_dir: Path = DEFAULT_FIGURES,
    no_figures: bool = False,
    seed: int = 42,
) -> Dict[str, Any]:
    records = load_audit_records(input_path, jsonl_path=jsonl_path)
    baselines = evaluate_baselines(records, seed=seed)
    figures: List[Path] = []
    if not no_figures:
        figures = write_figures(figures_dir, records, baselines)
    write_markdown(
        markdown_path,
        records,
        baselines,
        input_path=input_path,
        jsonl_path=jsonl_path,
        figures=figures,
    )
    return {
        "n_units": len(records),
        "label_distribution": dict(label_distribution(records)),
        "baselines": [
            {
                "name": result.name,
                "accuracy": result.accuracy,
                "macro_f1": result.macro_f1,
                "flagged": result.flagged,
                "note": result.note,
            }
            for result in baselines
        ],
        "markdown": markdown_path,
        "figures": figures,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Audit pragmatic-function labels for trivial predictability.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT, help="Annotated CSV with pragmatic_function")
    parser.add_argument(
        "--jsonl",
        type=Path,
        default=None,
        help="Optional pipeline JSONL to enrich metadata by unit_id",
    )
    parser.add_argument("--markdown", type=Path, default=DEFAULT_MD)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES)
    parser.add_argument("--no-figures", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    summary = run(
        args.input,
        jsonl_path=args.jsonl,
        markdown_path=args.markdown,
        figures_dir=args.figures_dir,
        no_figures=args.no_figures,
        seed=args.seed,
    )
    print(f"Audited {summary['n_units']} labeled units")
    print(f"Wrote {summary['markdown']}")
    if summary["figures"]:
        print(f"Wrote {len(summary['figures'])} figures under {args.figures_dir}/")
    flagged = [item["name"] for item in summary["baselines"] if item["flagged"]]
    if flagged:
        print(f"Flagged baselines: {', '.join(flagged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
