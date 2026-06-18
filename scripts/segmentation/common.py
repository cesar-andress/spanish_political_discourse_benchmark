"""Shared helpers for SPDB segmentation scripts."""

from __future__ import annotations

import logging
from pathlib import Path

from scripts.ingestion.common import (
    benchmark_root,
    make_instance_id,
    read_jsonl,
    utc_now_iso,
    validate_discourse_unit,
    write_jsonl,
)

DEFAULT_SEGMENTED_PATH = Path("data/processed/segmented/discourse_units.jsonl")


def setup_logging(level: str = "INFO") -> logging.Logger:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger("spdb.segmentation")


def default_segmented_path(filename: str = "discourse_units.jsonl") -> Path:
    return benchmark_root() / "data" / "processed" / "segmented" / filename


def make_unit_id(document_id: str, segment_index: int, split: str = "unassigned") -> str:
    """
    Stable discourse-unit identifier.

    Stored as ``instance_id`` in JSONL output (SPDB schema field name).
    """
    return make_instance_id(document_id, segment_index, split)
