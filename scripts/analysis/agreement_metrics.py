"""Agreement metric helpers for pilot annotation analysis."""

from __future__ import annotations

import json
import math
from collections import Counter
from dataclasses import dataclass
from typing import Dict, Iterable, List, Sequence, Set, Tuple


@dataclass(frozen=True)
class CohenKappaResult:
    column: str
    n: int
    observed_agreement: float
    expected_agreement: float
    kappa: float
    per_label: Dict[str, Dict[str, float | int]]


@dataclass(frozen=True)
class KrippendorffAlphaResult:
    column: str
    n_units: int
    n_values: int
    alpha: float
    per_label: Dict[str, Dict[str, float | int]]


@dataclass(frozen=True)
class ConfusionMatrixResult:
    column: str
    labels: List[str]
    matrix: Dict[str, Dict[str, int]]
    total: int


def _categories(values_a: Sequence[str], values_b: Sequence[str]) -> List[str]:
    return sorted(set(values_a) | set(values_b))


def observed_agreement(values_a: Sequence[str], values_b: Sequence[str]) -> float:
    if not values_a:
        return float("nan")
    matches = sum(1 for left, right in zip(values_a, values_b) if left == right)
    return matches / len(values_a)


def cohen_kappa(values_a: Sequence[str], values_b: Sequence[str]) -> CohenKappaResult:
    if len(values_a) != len(values_b):
        raise ValueError("Label sequences must have equal length")
    n = len(values_a)
    if n == 0:
        return CohenKappaResult(
            column="",
            n=0,
            observed_agreement=float("nan"),
            expected_agreement=float("nan"),
            kappa=float("nan"),
            per_label={},
        )

    categories = _categories(values_a, values_b)
    counts = Counter(zip(values_a, values_b))
    po = sum(counts[(label, label)] for label in categories) / n

    marginal_a = Counter(values_a)
    marginal_b = Counter(values_b)
    pe = sum(marginal_a[label] * marginal_b[label] for label in categories) / (n * n)

    if math.isclose(pe, 1.0):
        kappa = 1.0 if math.isclose(po, 1.0) else float("nan")
    else:
        kappa = (po - pe) / (1.0 - pe)

    per_label: Dict[str, Dict[str, float | int]] = {}
    for label in categories:
        both = counts[(label, label)]
        either = marginal_a[label] + marginal_b[label] - both
        union = either + both
        per_label[label] = {
            "support_a": marginal_a[label],
            "support_b": marginal_b[label],
            "agree_both": both,
            "agree_rate": both / union if union else float("nan"),
        }

    return CohenKappaResult(
        column="",
        n=n,
        observed_agreement=po,
        expected_agreement=pe,
        kappa=kappa,
        per_label=per_label,
    )


def binary_cohen_kappa(presence_a: Sequence[bool], presence_b: Sequence[bool]) -> float:
    labels_a = ["1" if value else "0" for value in presence_a]
    labels_b = ["1" if value else "0" for value in presence_b]
    return cohen_kappa(labels_a, labels_b).kappa


def krippendorff_alpha_nominal(values_a: Sequence[str], values_b: Sequence[str]) -> KrippendorffAlphaResult:
    if len(values_a) != len(values_b):
        raise ValueError("Label sequences must have equal length")

    categories = _categories(values_a, values_b)
    n_units = len(values_a)
    n_values = n_units * 2
    if n_units == 0:
        return KrippendorffAlphaResult(
            column="",
            n_units=0,
            n_values=0,
            alpha=float("nan"),
            per_label={},
        )

    coincidence = Counter()
    category_counts = Counter()
    for left, right in zip(values_a, values_b):
        for value in (left, right):
            category_counts[value] += 1
        if left == right:
            coincidence[(left, left)] += 2
        else:
            coincidence[(left, right)] += 1
            coincidence[(right, left)] += 1

    agreement = sum(coincidence[(cat, cat)] for cat in categories) / n_values
    do = 1.0 - agreement
    de = 1.0 - sum(
        category_counts[cat] * (category_counts[cat] - 1) for cat in categories
    ) / (n_values * (n_values - 1))

    if math.isclose(de, 0.0):
        alpha = 1.0 if math.isclose(do, 0.0) else float("nan")
    else:
        alpha = 1.0 - (do / de)

    per_label: Dict[str, Dict[str, float | int]] = {}
    for label in categories:
        in_a = sum(1 for value in values_a if value == label)
        in_b = sum(1 for value in values_b if value == label)
        both = sum(1 for left, right in zip(values_a, values_b) if left == label and right == label)
        union = in_a + in_b - both
        per_label[label] = {
            "support_a": in_a,
            "support_b": in_b,
            "agree_both": both,
            "agree_rate": both / union if union else float("nan"),
        }

    return KrippendorffAlphaResult(
        column="",
        n_units=n_units,
        n_values=n_values,
        alpha=alpha,
        per_label=per_label,
    )


def confusion_matrix(values_a: Sequence[str], values_b: Sequence[str]) -> ConfusionMatrixResult:
    labels = _categories(values_a, values_b)
    matrix: Dict[str, Dict[str, int]] = {row: {col: 0 for col in labels} for row in labels}
    for left, right in zip(values_a, values_b):
        matrix[left][right] += 1
    return ConfusionMatrixResult(column="", labels=labels, matrix=matrix, total=len(values_a))


def fallacy_label_universe(values_a: Sequence[str], values_b: Sequence[str]) -> List[str]:
    universe: Set[str] = set()
    for value in list(values_a) + list(values_b):
        if value and value.upper() != "FAL_NONE":
            for part in value.split("|"):
                part = part.strip()
                if part:
                    universe.add(part)
    return sorted(universe)


def exact_set_agreement(values_a: Sequence[str], values_b: Sequence[str]) -> float:
    if not values_a:
        return float("nan")
    matches = sum(1 for left, right in zip(values_a, values_b) if left == right)
    return matches / len(values_a)


def json_safe(value: object) -> object:
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return None
    if isinstance(value, dict):
        return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_safe(item) for item in value]
    return value
