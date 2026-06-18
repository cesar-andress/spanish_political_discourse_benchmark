"""Constants for SPDB external fallacy LLM batch pipeline."""

from __future__ import annotations

from pathlib import Path

PROMPTS_DIR = Path("prompts")
FALLACY_SPDB_ZERO_SHOT = PROMPTS_DIR / "fallacy_spdb_zero_shot.txt"
FALLACY_SPDB_CLAIM_EVIDENCE = PROMPTS_DIR / "fallacy_spdb_claim_evidence.txt"
FALLACY_SPDB_CONSENSUS = PROMPTS_DIR / "fallacy_spdb_consensus.txt"

FAL_INVENTORY = Path("labels/fallacies.tsv")

SPDB_FAL_LABELS: tuple[str, ...] = (
    "FAL_ADHOM",
    "FAL_STRAW",
    "FAL_DILEMMA",
    "FAL_SLOPE",
    "FAL_EMOTION",
    "FAL_GENERAL",
    "FAL_WHATABOUT",
)

DEFAULT_REPORT_DIR = Path("reports/external_validation")
DEFAULT_OUTPUT_DIR = Path("data/experiments/external_validation")
DEFAULT_FALLACY_REPORT = DEFAULT_REPORT_DIR / "fallacy_llm_report.md"
DEFAULT_LABEL_DISTRIBUTION = DEFAULT_REPORT_DIR / "fallacy_label_distribution.csv"
DEFAULT_PARSE_ERRORS = DEFAULT_REPORT_DIR / "fallacy_parse_errors.csv"

FIXTURE_DATASET = Path("tests/fixtures/external_validation/fallacy_sample.jsonl")
FIXTURE_MOCK_BACKEND = Path("tests/fixtures/external_validation/mock_fallacy_backend.py")
FIXTURE_OUTPUT = DEFAULT_OUTPUT_DIR / "mock_fallacy_fixture.jsonl"

REQUIRED_OUTPUT_FIELDS = (
    "fallacy_labels",
    "fallacy_none_explicit",
    "confidence",
    "explanation",
)
