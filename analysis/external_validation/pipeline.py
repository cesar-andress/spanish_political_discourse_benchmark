"""Orchestrate external validation planning report generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from analysis.external_validation.constants import DEFAULT_REPORT_DIR
from analysis.external_validation.dataset_inventory import write_inventory_report
from analysis.external_validation.ontology_mapping import (
    validate_mapping_coverage,
    write_mapping_report,
)
from analysis.external_validation.validation_report import write_compatibility_report


@dataclass(frozen=True)
class ExternalValidationResult:
    report_dir: Path
    inventory_path: Path
    mapping_path: Path
    compatibility_path: Path
    missing_mappings: dict[str, list[str]]


def run_external_validation(report_dir: Path | None = None) -> ExternalValidationResult:
    target = report_dir or DEFAULT_REPORT_DIR
    inventory = write_inventory_report(target / "open_datasets_inventory.md")
    mapping = write_mapping_report(target / "fallacy_mapping.md")
    compatibility = write_compatibility_report(target / "benchmark_compatibility.md")
    missing = validate_mapping_coverage()
    return ExternalValidationResult(
        report_dir=target,
        inventory_path=inventory,
        mapping_path=mapping,
        compatibility_path=compatibility,
        missing_mappings=missing,
    )
