"""Ontology validation thresholds and paths."""

from __future__ import annotations

from pathlib import Path

PF_COLUMN = "pragmatic_function"
PF_INVENTORY = Path("labels/pragmatic_functions.tsv")
OPTIONAL_QC_COLUMNS = ("borderline", "second_choice")

DEFAULT_TEMPLATE = Path("annotation/pilot_001/pilot_100_units.csv")
DEFAULT_OUTPUT_DIR = Path("reports/ontology_validation")
DEFAULT_FIGURES_DIR = Path("figures/ontology_validation")

BOOTSTRAP_ITERATIONS = 2000
RANDOM_SEED = 42

THRESHOLD_ALPHA_MIN = 0.55
THRESHOLD_FULL_SPLIT_MAX = 0.20
THRESHOLD_BORDERLINE_MAX = 0.25
THRESHOLD_CONFUSION_PAIR_MAX = 0.35

WARN_ALPHA_MIN = 0.65
WARN_BORDERLINE_MAX = 0.15

FIXTURE_DIR = Path("tests/fixtures/ontology_validation")
FIXTURE_TEMPLATE = FIXTURE_DIR / "pilot_template.csv"
FIXTURE_ANNOTATORS = (
    FIXTURE_DIR / "annotator_a.csv",
    FIXTURE_DIR / "annotator_b.csv",
    FIXTURE_DIR / "annotator_c.csv",
)
