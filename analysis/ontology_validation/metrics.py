"""Reliability metrics for ontology validation."""

from __future__ import annotations

import math
import random
from collections import Counter
from dataclasses import dataclass
from typing import Callable, Dict, List, Sequence, Tuple

from scripts.analysis.agreement_metrics import cohen_kappa, krippendorff_alpha_nominal

from analysis.pilot.metrics import fleiss_kappa, multi_rater_krippendorff_alpha


@dataclass(frozen=True)
class BootstrapCI:
    point: float
    lower: float
    upper: float
    iterations: int


def gwet_ac1(unit_ratings: Sequence[Sequence[str]]) -> float:
    if not unit_ratings:
        return float("nan")
    categories = sorted({label for ratings in unit_ratings for label in ratings})
    k = len(categories)
    if k <= 1:
        return 1.0

    n_items = len(unit_ratings)
    m = len(unit_ratings[0])
    if any(len(ratings) != m for ratings in unit_ratings):
        raise ValueError("Gwet AC1 requires the same number of ratings per unit.")

    pa_values: List[float] = []
    totals: Counter[str] = Counter()
    for ratings in unit_ratings:
        counts = Counter(ratings)
        totals.update(ratings)
        pa_values.append((sum(count * count for count in counts.values()) - m) / (m * (m - 1)))
    pa = sum(pa_values) / n_items

    total_assignments = n_items * m
    proportions = {label: totals[label] / total_assignments for label in categories}
    pe = sum(proportions[label] * (1.0 - proportions[label]) for label in categories) / (k - 1)
    if math.isclose(1.0 - pe, 0.0):
        return float("nan")
    return (pa - pe) / (1.0 - pe)


def mean_pairwise_cohen_kappa(matrix: Sequence[Sequence[str]]) -> float:
    if len(matrix) < 2:
        return float("nan")
    scores = []
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            scores.append(cohen_kappa(matrix[i], matrix[j]).kappa)
    return sum(scores) / len(scores) if scores else float("nan")


def pairwise_cohen_details(
    matrix: Sequence[Sequence[str]],
    annotator_names: Sequence[str],
) -> List[Dict[str, float | str]]:
    rows: List[Dict[str, float | str]] = []
    for i in range(len(matrix)):
        for j in range(i + 1, len(matrix)):
            result = cohen_kappa(matrix[i], matrix[j])
            rows.append(
                {
                    "annotator_a": annotator_names[i],
                    "annotator_b": annotator_names[j],
                    "cohen_kappa": result.kappa,
                    "observed_agreement": result.observed_agreement,
                }
            )
    return rows


def bootstrap_ci(
    unit_ratings: Sequence[Sequence[str]],
    metric_fn: Callable[[Sequence[Sequence[str]]], float],
    *,
    iterations: int = 2000,
    seed: int = 42,
) -> BootstrapCI:
    point = metric_fn(unit_ratings)
    if not unit_ratings or point != point:
        return BootstrapCI(point=point, lower=float("nan"), upper=float("nan"), iterations=0)

    rng = random.Random(seed)
    n = len(unit_ratings)
    samples: List[float] = []
    for _ in range(iterations):
        draw = [unit_ratings[rng.randrange(n)] for _ in range(n)]
        value = metric_fn(draw)
        if value == value:
            samples.append(value)
    samples.sort()
    lower = samples[int(0.025 * len(samples))] if samples else float("nan")
    upper = samples[int(0.975 * len(samples)) - 1] if samples else float("nan")
    return BootstrapCI(point=point, lower=lower, upper=upper, iterations=len(samples))


def one_vs_rest_kappa(matrix: Sequence[Sequence[str]], label: str) -> float:
    binary = [["1" if value == label else "0" for value in row] for row in matrix]
    return mean_pairwise_cohen_kappa(binary)


def one_vs_rest_alpha(matrix: Sequence[Sequence[str]], label: str) -> float:
    binary = [["1" if value == label else "0" for value in row] for row in matrix]
    return multi_rater_krippendorff_alpha(binary, column=label).alpha


def positive_specific_agreement(unit_ratings: Sequence[Sequence[str]], label: str) -> float:
    scores: List[float] = []
    for ratings in unit_ratings:
        positives = [rating == label for rating in ratings]
        if not any(positives):
            continue
        agree_pairs = 0
        total_pairs = 0
        m = len(ratings)
        for i in range(m):
            for j in range(i + 1, m):
                if ratings[i] == label or ratings[j] == label:
                    total_pairs += 1
                    if ratings[i] == label and ratings[j] == label:
                        agree_pairs += 1
        if total_pairs:
            scores.append(agree_pairs / total_pairs)
    return sum(scores) / len(scores) if scores else float("nan")


def _resample(unit_ratings: Sequence[Sequence[str]], matrix: Sequence[Sequence[str]], indices: Sequence[int]):
    resampled_units = [unit_ratings[i] for i in indices]
    resampled_matrix = [[row[i] for i in indices] for row in matrix]
    return resampled_units, resampled_matrix


def _bootstrap_metrics(
    unit_ratings: Sequence[Sequence[str]],
    matrix: Sequence[Sequence[str]],
    *,
    iterations: int,
    seed: int,
) -> Dict[str, BootstrapCI]:
    n = len(unit_ratings)
    if n == 0:
        nan = float("nan")
        empty = BootstrapCI(point=nan, lower=nan, upper=nan, iterations=0)
        return {
            "krippendorff_alpha": empty,
            "fleiss_kappa": empty,
            "mean_pairwise_cohen_kappa": empty,
            "gwet_ac1": empty,
        }

    rng = random.Random(seed)
    metric_defs = {
        "krippendorff_alpha": lambda u, m: multi_rater_krippendorff_alpha(m, column="pragmatic_function").alpha,
        "fleiss_kappa": lambda u, m: fleiss_kappa(u).kappa,
        "mean_pairwise_cohen_kappa": lambda u, m: mean_pairwise_cohen_kappa(m),
        "gwet_ac1": lambda u, m: gwet_ac1(u),
    }
    results: Dict[str, BootstrapCI] = {}
    for name, metric_fn in metric_defs.items():
        point = metric_fn(unit_ratings, matrix)
        samples: List[float] = []
        for offset in range(iterations):
            local_rng = random.Random(seed + offset + 1)
            indices = [local_rng.randrange(n) for _ in range(n)]
            u, m = _resample(unit_ratings, matrix, indices)
            value = metric_fn(u, m)
            if value == value:
                samples.append(value)
        samples.sort()
        lower = samples[int(0.025 * len(samples))] if samples else float("nan")
        upper = samples[int(0.975 * len(samples)) - 1] if samples else float("nan")
        results[name] = BootstrapCI(point=point, lower=lower, upper=upper, iterations=len(samples))
    return results


def overall_metrics(
    unit_ratings: Sequence[Sequence[str]],
    matrix: Sequence[Sequence[str]],
    annotator_names: Sequence[str],
    *,
    bootstrap_iterations: int,
    seed: int,
) -> Dict[str, object]:
    boot = _bootstrap_metrics(
        unit_ratings,
        matrix,
        iterations=bootstrap_iterations,
        seed=seed,
    )
    return {
        "krippendorff_alpha": boot["krippendorff_alpha"].__dict__,
        "fleiss_kappa": boot["fleiss_kappa"].__dict__,
        "mean_pairwise_cohen_kappa": boot["mean_pairwise_cohen_kappa"].__dict__,
        "gwet_ac1": boot["gwet_ac1"].__dict__,
        "pairwise_cohen_kappa": pairwise_cohen_details(matrix, annotator_names),
    }
