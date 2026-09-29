"""Metadata and constants for HuggingFace dataset card generation."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CITATION_CFF = ROOT / "CITATION.cff"
MANIFEST = ROOT / "releases/v0.1.0-alpha/MANIFEST.json"
LABELS_PF = ROOT / "labels/pragmatic_functions.tsv"
LABELS_FAL = ROOT / "labels/fallacies.tsv"

DEFAULT_OUTPUT = ROOT / "dataset_card.md"
LEGACY_OUTPUT = ROOT / "dataset_documentation/dataset_card.md"

GITHUB_REPO = "https://github.com/cesar-andress/spanish_political_discourse_benchmark"
DOI = "10.5281/zenodo.20745403"
DOI_URL = f"https://doi.org/{DOI}"
HISTORICAL_ALPHA_VERSION_DOI = "10.5281/zenodo.20745404"

V1_TARGET_UNITS = 8000
V1_MVP_UNITS = 5000
TRAIN_UNITS = 5600
DEV_UNITS = 1200
TEST_UNITS = 1200

SOURCE_MIX = (
    ("parliamentary", "Parliament", "60%", 4800),
    ("manifesto", "Party manifestos", "12%", 960),
    ("social_media", "Elite social media", "28%", 2240),
)

CONTACT_EMAILS = (
    "josejaime.baena@unir.net",
    "daniel.pinto@unir.net",
)
