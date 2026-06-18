"""SPDB v1 ingestion layer — shared utilities."""

from scripts.ingestion.base import BaseIngestor, IngestConfig
from scripts.ingestion.common import (
    benchmark_root,
    default_intermediate_path,
    default_processed_path,
    default_raw_path,
    load_schema,
    read_jsonl,
    setup_logging,
    validate_discourse_unit,
    write_jsonl,
)

__all__ = [
    "BaseIngestor",
    "IngestConfig",
    "benchmark_root",
    "default_intermediate_path",
    "default_processed_path",
    "default_raw_path",
    "load_schema",
    "read_jsonl",
    "setup_logging",
    "validate_discourse_unit",
    "write_jsonl",
]
