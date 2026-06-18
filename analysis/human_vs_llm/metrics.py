"""Classification metrics for Human-vs-LLM comparison."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Dict, List, Sequence, Tuple

from scripts.analysis.agreement_metrics import cohen_kappa, confusion_matrix


@dataclass(frozen=True)
class ClassificationScores:
    accuracy: float
    macro_f1: float
    weighted_f1: float
    per_class: Dict[str, Dict[str, float]]
    confusion: Dict[str, Dict[str, int]]
    labels: List[str]
    n_evaluated: int
    n_abstained: int
    abstention_rate: float
    invalid_rate: float


def _sorted_labels(*label_groups: Sequence[str]) -> List[str]:
    labels = set()
    for group in label_groups:
        labels.update(label for label in group if label)
    return sorted(labels)


def _precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    if precision + recall == 0:
        return precision, recall, 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def classification_scores(
    y_true: Sequence[str],
    y_pred: Sequence[str | None],
    *,
    invalid_flags: Sequence[bool] | None = None,
) -> ClassificationScores:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have equal length")

    evaluated_true: List[str] = []
    evaluated_pred: List[str] = []
    abstained = 0
    invalid = 0
    flags = invalid_flags or [False] * len(y_pred)

    for truth, pred, bad in zip(y_true, y_pred, flags):
        if pred is None or bad:
            if bad:
                invalid += 1
            else:
                abstained += 1
            continue
        evaluated_true.append(truth)
        evaluated_pred.append(pred)

    n = len(y_true)
    labels = _sorted_labels(evaluated_true, evaluated_pred)
    if not evaluated_true:
        return ClassificationScores(
            accuracy=float("nan"),
            macro_f1=float("nan"),
            weighted_f1=float("nan"),
            per_class={},
            confusion={},
            labels=labels,
            n_evaluated=0,
            n_abstained=abstained,
            abstention_rate=abstained / n if n else 0.0,
            invalid_rate=invalid / n if n else 0.0,
        )

    matrix = confusion_matrix(evaluated_true, evaluated_pred)
    accuracy = sum(
        matrix.matrix[label][label] for label in matrix.labels
    ) / len(evaluated_true)

    supports = Counter(evaluated_true)
    per_class: Dict[str, Dict[str, float]] = {}
    f1_scores: List[float] = []
    weighted_f1_sum = 0.0
    total_support = sum(supports.values())

    for label in labels:
        tp = matrix.matrix.get(label, {}).get(label, 0)
        fp = sum(matrix.matrix.get(row, {}).get(label, 0) for row in matrix.labels if row != label)
        fn = sum(matrix.matrix.get(label, {}).get(col, 0) for col in matrix.labels if col != label)
        precision, recall, f1 = _precision_recall_f1(tp, fp, fn)
        per_class[label] = {
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": float(supports.get(label, 0)),
        }
        f1_scores.append(f1)
        weighted_f1_sum += f1 * supports.get(label, 0)

    return ClassificationScores(
        accuracy=accuracy,
        macro_f1=sum(f1_scores) / len(f1_scores) if f1_scores else float("nan"),
        weighted_f1=weighted_f1_sum / total_support if total_support else float("nan"),
        per_class=per_class,
        confusion=matrix.matrix,
        labels=matrix.labels,
        n_evaluated=len(evaluated_true),
        n_abstained=abstained,
        abstention_rate=abstained / n if n else 0.0,
        invalid_rate=invalid / n if n else 0.0,
    )


def mean_pairwise_kappa(label_matrix: Sequence[Sequence[str]]) -> float:
    if len(label_matrix) < 2:
        return float("nan")
    scores = []
    for i in range(len(label_matrix)):
        for j in range(i + 1, len(label_matrix)):
            scores.append(cohen_kappa(label_matrix[i], label_matrix[j]).kappa)
    return sum(scores) / len(scores) if scores else float("nan")
