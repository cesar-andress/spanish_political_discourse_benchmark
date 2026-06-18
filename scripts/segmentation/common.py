"""Shared helpers for SPDB segmentation scripts."""

from __future__ import annotations

import logging
from pathlib import Path

from scripts.ingestion.common import (
    default_pipeline_discourse_units_path,
    make_unit_id,
    read_jsonl,
    utc_now_iso,
    validate_pipeline_discourse_unit,
    write_jsonl,
)

__all__ = [
    "default_pipeline_discourse_units_path",
    "default_segmented_path",
    "make_unit_id",
    "read_jsonl",
    "setup_logging",
    "utc_now_iso",
    "validate_pipeline_discourse_unit",
    "write_jsonl",
]


def setup_logging(level: str = "INFO") -> logging.Logger:
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    return logging.getLogger("spdb.segmentation")


def default_segmented_path(filename: str = "discourse_units.jsonl") -> Path:
    return default_pipeline_discourse_units_path()
