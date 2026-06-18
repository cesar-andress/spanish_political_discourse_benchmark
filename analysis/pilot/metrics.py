"""Extended agreement metrics for multi-annotator pilot studies."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from scripts.analysis.agreement_metrics import (
    CohenKappaResult,
    KrippendorffAlphaResult,
    cohen_kappa,
    json_safe,
    krippendorff_alpha_nominal,
)


@dataclass(frozen=True)
class FleissKappaResult:
    column: str
    n_units: int
    n_raters: int
    kappa: float
    per_label: Dict[str, Dict[str, float | int]]


@dataclass(frozen=True)
class PairwiseAgreement:
    annotator_a: str
    annotator_b: str
    column: str
    kappa: float
    observed_agreement: float


def fleiss_kappa(unit_ratings: Sequence[Sequence[str]]) -> FleissKappaResult:
    filtered = [tuple(ratings) for ratings in unit_ratings if len(ratings) >= 2]
    if not filtered:
        return FleissKappaResult(column="", n_units=0, n_raters=0, kappa=float("nan"), per_label={})

    categories = sorted({label for ratings in filtered for label in ratings})
    n_units = len(filtered)
    n_raters = len(filtered[0])
    if any(len(ratings) != n_raters for ratings in filtered):
        raise ValueError("Fleiss kappa requires the same number of ratings per unit.")

    category_totals = Counter()
    p_values: List[float] = []
    per_label_counts = {label: [] for label in categories}

    for ratings in filtered:
        counts = Counter(ratings)
        for label in categories:
            category_totals[label] += counts.get(label, 0)
            per_label_counts[label].append(counts.get(label, 0))
        n_i = len(ratings)
        sum_squares = sum(count * (count - 1) for count in counts.values())
        p_values.append(sum_squares / (n_i * (n_i - 1)))

    p_bar = sum(p_values) / n_units
    total_assignments = n_units * n_raters
    proportions = {label: category_totals[label] / total_assignments for label in categories}
    p_e = sum(value * value for value in proportions.values())

    if math.isclose(p_e, 1.0):
        kappa = 1.0 if math.isclose(p_bar, 1.0) else float("nan")
    else:
        kappa = (p_bar - p_e) / (1.0 - p_e)

    per_label: Dict[str, Dict[str, float | int]] = {}
    for label in categories:
        per_label[label] = {
            "total_assignments": category_totals[label],
            "mean_count_per_unit": sum(per_label_counts[label]) / n_units,
            "category_proportion": proportions[label],
        }

    return FleissKappaResult(
        column="",
        n_units=n_units,
        n_raters=n_raters,
        kappa=kappa,
        per_label=per_label,
    )


def pairwise_cohen_matrix(
    matrix: Sequence[Sequence[str]],
    annotator_names: Sequence[str],
    *,
    column: str,
) -> Tuple[List[List[float | None]], List[CohenKappaResult]]:
    n = len(matrix)
    scores: List[List[float | None]] = [[None for _ in range(n)] for _ in range(n)]
    details: List[CohenKappaResult] = []

    for i in range(n):
        scores[i][i] = 1.0
        for j in range(i + 1, n):
            result = cohen_kappa(matrix[i], matrix[j])
            result = CohenKappaResult(
                column=column,
                n=result.n,
                observed_agreement=result.observed_agreement,
                expected_agreement=result.expected_agreement,
                kappa=result.kappa,
                per_label=result.per_label,
            )
            scores[i][j] = result.kappa
            scores[j][i] = result.kappa
            details.append(result)
    return scores, details


def multi_rater_krippendorff_alpha(
    matrix: Sequence[Sequence[str]],
    *,
    column: str,
) -> KrippendorffAlphaResult:
    if len(matrix) < 2:
        return KrippendorffAlphaResult(
            column=column,
            n_units=0,
            n_values=0,
            alpha=float("nan"),
            per_label={},
        )

    if len(matrix) == 2:
        result = krippendorff_alpha_nominal(matrix[0], matrix[1])
        return KrippendorffAlphaResult(
            column=column,
            n_units=result.n_units,
            n_values=result.n_values,
            alpha=result.alpha,
            per_label=result.per_label,
        )

    alphas = []
    per_label_acc: Dict[str, Dict[str, float | int]] = {}
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            result = krippendorff_alpha_nominal(matrix[i], matrix[j])
            alphas.append(result.alpha)
            for label, stats in result.per_label.items():
                bucket = per_label_acc.setdefault(
                    label,
                    {"support_total": 0, "agree_both_total": 0, "pairs": 0},
                )
                bucket["support_total"] = int(bucket["support_total"]) + int(stats["support_a"]) + int(stats["support_b"])
                bucket["agree_both_total"] = int(bucket["agree_both_total"]) + int(stats["agree_both"])
                bucket["pairs"] = int(bucket["pairs"]) + 1

    per_label = {
        label: {
            "agree_both_total": stats["agree_both_total"],
            "pairs": stats["pairs"],
            "agree_rate": (
                int(stats["agree_both_total"]) / int(stats["pairs"])
                if int(stats["pairs"])
                else float("nan")
            ),
        }
        for label, stats in per_label_acc.items()
    }
    alpha = sum(alphas) / len(alphas) if alphas else float("nan")
    return KrippendorffAlphaResult(
        column=column,
        n_units=len(matrix[0]),
        n_values=len(matrix[0]) * len(matrix),
        alpha=alpha,
        per_label=per_label,
    )


def per_class_agreement(values: Sequence[Sequence[str]]) -> Dict[str, Dict[str, float | int]]:
    categories = sorted({label for row in values for label in row})
    per_label: Dict[str, Dict[str, float | int]] = {}
    n_units = len(values[0]) if values else 0

    for label in categories:
        exact = 0
        present = 0
        for unit_index in range(n_units):
            unit_values = [row[unit_index] for row in values]
            if any(value == label for value in unit_values):
                present += 1
                if len(set(unit_values)) == 1:
                    exact += 1
        per_label[label] = {
            "units_with_label": present,
            "units_unanimous": exact,
            "unanimous_rate": exact / present if present else float("nan"),
        }
    return per_label
