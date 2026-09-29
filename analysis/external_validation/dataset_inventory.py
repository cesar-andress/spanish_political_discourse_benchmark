"""Render open-dataset inventory markdown from structured metadata."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from analysis.external_validation.constants import DEFAULT_REPORT_DIR, EXTERNAL_DATASETS, ExternalDataset


def render_inventory_markdown(datasets: Iterable[ExternalDataset] | None = None) -> str:
    rows = list(datasets or EXTERNAL_DATASETS)
    lines = [
        "# Open Fallacy Dataset Inventory",
        "",
        "Structured inventory of public fallacy and related persuasion datasets relevant to",
        "SPDB external validation planning.",
        "",
        "**Status:** planning document only. No external evaluation has been run.",
        "",
        f"**Datasets catalogued:** {len(rows)}",
        "",
    ]
    for index, dataset in enumerate(rows, start=1):
        lines.extend(
            [
                f"## {index}. {dataset.name}",
                "",
                f"- **ID:** `{dataset.dataset_id}`",
                f"- **Citation:** {dataset.citation}",
                f"- **URL:** {dataset.url}",
                f"- **Language:** {dataset.language}",
                f"- **Domain:** {dataset.domain}",
                f"- **Annotation scheme:** {dataset.annotation_scheme}",
                f"- **Examples:** {dataset.num_examples}",
                f"- **License:** {dataset.license_info}",
                f"- **Availability:** {dataset.availability}",
                f"- **Mapping potential to SPDB FAL labels:** {dataset.mapping_potential}",
                f"- **External label inventory ({len(dataset.external_labels)}):** "
                + ", ".join(f"`{label}`" for label in dataset.external_labels[:8])
                + (" ..." if len(dataset.external_labels) > 8 else ""),
                "",
            ]
        )
    lines.extend(
        [
            "## Notes",
            "",
            "- SPDB human gold labels are not yet available; this inventory supports future",
            "  external validation once adjudicated pilot annotations exist.",
            "- Parliamentary plenary spans (SPDB) differ from debate excerpts (FallacyES-Political)",
            "  in segmentation and context packaging.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_inventory_report(output_path: Path | None = None) -> Path:
    path = output_path or DEFAULT_REPORT_DIR / "open_datasets_inventory.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_inventory_markdown(), encoding="utf-8")
    return path
