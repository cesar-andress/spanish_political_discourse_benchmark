"""Label inventory helpers for LLM prompts and validation."""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import List

from analysis.llm_annotation.constants import FAL_INVENTORY, PF_INVENTORY


@lru_cache(maxsize=1)
def load_pf_labels(path: Path = PF_INVENTORY) -> tuple[str, ...]:
    return tuple(_load_inventory(path))


@lru_cache(maxsize=1)
def load_fal_labels(path: Path = FAL_INVENTORY) -> tuple[str, ...]:
    return tuple(_load_inventory(path))


def _load_inventory(path: Path) -> List[str]:
    labels: List[str] = []
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        for row in reader:
            label_id = (row.get("label_id") or "").strip()
            if label_id:
                labels.append(label_id)
    return labels


def format_pf_inventory() -> str:
    return "\n".join(f"- `{label}`" for label in load_pf_labels())


def format_fal_inventory() -> str:
    lines = []
    for label in load_fal_labels():
        note = " (use alone when no fallacy is present)" if label == "FAL_NONE" else ""
        lines.append(f"- `{label}`{note}")
    return "\n".join(lines)
