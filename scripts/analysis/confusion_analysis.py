"""Thin wrappers exposing pilot confusion analysis from scripts.analysis."""

from analysis.pilot.confusion_analysis import ConfusionAnalysisResult, run_confusion_analysis, write_confusion_outputs

__all__ = ["ConfusionAnalysisResult", "run_confusion_analysis", "write_confusion_outputs"]
