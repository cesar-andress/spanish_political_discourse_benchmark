"""Paths and source metadata for FallacyES-Political external validation."""

from __future__ import annotations

from pathlib import Path

ZENODO_RECORD_URL = "https://zenodo.org/records/14836328"
ZENODO_CSV_URL = "https://zenodo.org/api/records/14836328/files/fallacyES-political.csv/content"
ZENODO_CSV_FILENAME = "fallacyES-political.csv"

SOURCE_DATASET = "fallacyes_political"

FALLACYES_DIR = Path("data/external/fallacyes_political")
RAW_DIR = FALLACYES_DIR / "raw"
RAW_CSV = RAW_DIR / ZENODO_CSV_FILENAME
INGESTED_JSONL = FALLACYES_DIR / "fallacyes_political.jsonl"
MAPPED_JSONL = FALLACYES_DIR / "fallacyes_political_spdb_mapped.jsonl"

MISTRAL_PREDICTIONS = Path("data/experiments/external_validation/mistral_fallacyes_political.jsonl")
FALLACYES_REPORT = Path("reports/external_validation/fallacyes_political_llm_report.md")

FIXTURE_RAW_CSV = Path("tests/fixtures/external_validation/fallacyes_political_sample.csv")
FIXTURE_INGESTED = Path("tests/fixtures/external_validation/fallacyes_political_sample.jsonl")
FIXTURE_MAPPED = Path("tests/fixtures/external_validation/fallacyes_political_sample_mapped.jsonl")
