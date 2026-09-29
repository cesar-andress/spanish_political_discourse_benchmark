"""Multilabel evaluation metrics for external SPDB fallacy projection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Sequence, Set, Tuple

from analysis.external_validation.fallacy_constants import SPDB_FAL_LABELS


def _precision_recall_f1(tp: int, fp: int, fn: int) -> Tuple[float, float, float]:
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    if precision + recall == 0:
        return precision, recall, 0.0
    f1 = 2 * precision * recall / (precision + recall)
    return precision, recall, f1


def normalize_spdb_label_set(raw: Iterable[str], *, valid_labels: Sequence[str] = SPDB_FAL_LABELS) -> FrozenSet[str]:
    allowed = set(valid_labels)
    return frozenset(label.strip() for label in raw if label and label.strip() in allowed)


@dataclass(frozen=True)
class PerLabelMetrics:
    precision: float
    recall: float
    f1: float
    support: int


@dataclass(frozen=True)
class MultilabelMetrics:
    n_samples: int
    n_labels: int
    micro_precision: float
    micro_recall: float
    micro_f1: float
    macro_precision: float
    macro_recall: float
    macro_f1: float
    exact_match_ratio: float
    hamming_loss: float
    jaccard_similarity: float
    per_label: Dict[str, PerLabelMetrics] = field(default_factory=dict)

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["per_label"] = {
            label: asdict(stats) for label, stats in self.per_label.items()
        }
        return payload


def compute_multilabel_metrics(
    y_true: Sequence[Set[str] | FrozenSet[str]],
    y_pred: Sequence[Set[str] | FrozenSet[str]],
    labels: Sequence[str] | None = None,
) -> MultilabelMetrics:
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must have the same length")
    if not y_true:
        return MultilabelMetrics(
            n_samples=0,
            n_labels=len(labels or SPDB_FAL_LABELS),
            micro_precision=float("nan"),
            micro_recall=float("nan"),
            micro_f1=float("nan"),
            macro_precision=float("nan"),
            macro_recall=float("nan"),
            macro_f1=float("nan"),
            exact_match_ratio=float("nan"),
            hamming_loss=float("nan"),
            jaccard_similarity=float("nan"),
        )

    label_list = list(labels or SPDB_FAL_LABELS)
    n_samples = len(y_true)
    n_labels = len(label_list)

    per_label: Dict[str, PerLabelMetrics] = {}
    macro_precisions: List[float] = []
    macro_recalls: List[float] = []
    macro_f1s: List[float] = []
    tp_total = fp_total = fn_total = 0

    for label in label_list:
        tp = fp = fn = 0
        for truth, pred in zip(y_true, y_pred):
            truth_has = label in truth
            pred_has = label in pred
            if truth_has and pred_has:
                tp += 1
            elif pred_has:
                fp += 1
            elif truth_has:
                fn += 1
        precision, recall, f1 = _precision_recall_f1(tp, fp, fn)
        support = sum(1 for truth in y_true if label in truth)
        per_label[label] = PerLabelMetrics(
            precision=precision,
            recall=recall,
            f1=f1,
            support=support,
        )
        macro_precisions.append(precision)
        macro_recalls.append(recall)
        macro_f1s.append(f1)
        tp_total += tp
        fp_total += fp
        fn_total += fn

    micro_precision, micro_recall, micro_f1 = _precision_recall_f1(tp_total, fp_total, fn_total)
    macro_precision = sum(macro_precisions) / len(macro_precisions)
    macro_recall = sum(macro_recalls) / len(macro_recalls)
    macro_f1 = sum(macro_f1s) / len(macro_f1s)

    exact_matches = sum(1 for truth, pred in zip(y_true, y_pred) if truth == pred)
    exact_match_ratio = exact_matches / n_samples

    hamming_errors = 0
    jaccard_scores: List[float] = []
    for truth, pred in zip(y_true, y_pred):
        for label in label_list:
            if (label in truth) != (label in pred):
                hamming_errors += 1
        union = truth | pred
        if not union:
            jaccard_scores.append(1.0)
        else:
            jaccard_scores.append(len(truth & pred) / len(union))

    hamming_loss = hamming_errors / (n_samples * n_labels)
    jaccard_similarity = sum(jaccard_scores) / n_samples

    return MultilabelMetrics(
        n_samples=n_samples,
        n_labels=n_labels,
        micro_precision=micro_precision,
        micro_recall=micro_recall,
        micro_f1=micro_f1,
        macro_precision=macro_precision,
        macro_recall=macro_recall,
        macro_f1=macro_f1,
        exact_match_ratio=exact_match_ratio,
        hamming_loss=hamming_loss,
        jaccard_similarity=jaccard_similarity,
        per_label=per_label,
    )
