"""Thin wrappers exposing pilot ontology diagnostics from scripts.analysis."""

from analysis.pilot.ontology_diagnostics import (
    OntologyDiagnosticsResult,
    run_ontology_diagnostics,
    write_ontology_outputs,
)

__all__ = ["OntologyDiagnosticsResult", "run_ontology_diagnostics", "write_ontology_outputs"]
