"""Constants for Human-vs-LLM comparison."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

GoldStrategy = Literal["majority_vote", "unanimous_only", "adjudicated_file"]

PF_COLUMN = "pragmatic_function"

DEFAULT_ANNOTATORS = (
    Path("annotation/pilot_001/pilot_100_units_annotator_a.csv"),
    Path("annotation/pilot_001/pilot_100_units_annotator_b.csv"),
    Path("annotation/pilot_001/pilot_100_units_annotator_c.csv"),
)
DEFAULT_ADJUDICATED = Path("annotation/pilot_001/pilot_100_units_adjudicated.csv")
DEFAULT_LLM_DIR = Path("data/experiments/llm_annotations")
DEFAULT_OUTPUT_DIR = Path("reports/human_vs_llm")

FIXTURE_DIR = Path("tests/fixtures/human_vs_llm")
FIXTURE_ANNOTATORS = (
    FIXTURE_DIR / "annotator_a.csv",
    FIXTURE_DIR / "annotator_b.csv",
    FIXTURE_DIR / "annotator_c.csv",
)
FIXTURE_LLM = FIXTURE_DIR / "mock_llm_pilot_100.jsonl"
FIXTURE_ADJUDICATED = FIXTURE_DIR / "adjudicated.csv"
FIXTURE_TEMPLATE = FIXTURE_DIR / "pilot_template.csv"
