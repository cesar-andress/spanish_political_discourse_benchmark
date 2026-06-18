"""Thin wrappers exposing pilot report generation from scripts.analysis."""

from analysis.pilot.report_generator import PilotReportBundle, generate_pilot_report

__all__ = ["PilotReportBundle", "generate_pilot_report"]
