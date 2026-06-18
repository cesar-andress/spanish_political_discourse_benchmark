"""Shared constants for pilot analytics."""

from __future__ import annotations

from pathlib import Path

ANNOTATION_COLUMNS = (
    "pragmatic_function",
    "fallacy_labels",
    "semantic_vacuity",
    "conceptual_anachronism",
)

PRIMARY_ONTOLOGY_COLUMN = "pragmatic_function"

DEFAULT_TEMPLATE = Path("annotation/pilot_001/pilot_100_units.csv")
DEFAULT_OUTPUT_DIR = Path("reports/pilot")
DEFAULT_REPORT = Path("reports/pilot_annotation_report.md")
DEFAULT_TEMPLATE_FILE = Path("reports/templates/pilot_annotation_report.md.tpl")
DEFAULT_FIGURES_DIR = Path("figures/pilot")

ONTOLOGY_INVENTORIES = {
    "pragmatic_function": Path("labels/pragmatic_functions.tsv"),
    "fallacy_labels": Path("labels/fallacies.tsv"),
    "semantic_vacuity": Path("labels/semantic_vacuity.tsv"),
    "conceptual_anachronism": Path("labels/conceptual_anachronism.tsv"),
}

SINGLE_LABEL_COLUMNS = (
    "pragmatic_function",
    "semantic_vacuity",
    "conceptual_anachronism",
)
