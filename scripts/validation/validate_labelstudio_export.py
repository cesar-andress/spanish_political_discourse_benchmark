#!/usr/bin/env python3
"""Validate Label Studio JSON exports against SPDB v1 annotation rules."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

logger = logging.getLogger("spdb.validation.labelstudio")

REQUIRED_DATA_FIELDS = (
    "instance_id",
    "document_id",
    "text",
    "task_type",
    "experimental_subset",
    "adjudication_context",
)

VALID_TASK_TYPES = {"primary", "adjudication"}

PRAGMATIC_FUNCTIONS = {
    "PF_ADVOCACY",
    "PF_ATTACK",
    "PF_DEFENSE",
    "PF_PROPOSAL",
    "PF_APPEAL",
    "PF_INFO",
    "PF_DEFLECT",
    "PF_PROCEDURAL",
}

FALLACY_LABELS = {
    "FAL_ADHOM",
    "FAL_STRAW",
    "FAL_DILEMMA",
    "FAL_SLOPE",
    "FAL_EMOTION",
    "FAL_GENERAL",
    "FAL_WHATABOUT",
}

SEMANTIC_VACUITY = {"SV_0", "SV_1", "SV_UNCLEAR"}
CONCEPTUAL_ANACHRONISM = {"CA_0", "CA_1", "CA_UNCLEAR"}

MAX_FALLACY_LABELS = 3


@dataclass
class TaskValidationResult:
    task_index: int
    instance_id: str
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class ValidationReport:
    input_path: Path
    total_tasks: int = 0
    passed_tasks: int = 0
    failed_tasks: int = 0
    results: List[TaskValidationResult] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.failed_tasks == 0

    def to_text(self) -> str:
        lines = [
            f"Label Studio export validation: {self.input_path}",
            f"Tasks: {self.total_tasks} total, {self.passed_tasks} passed, {self.failed_tasks} failed",
            "",
        ]
        for result in self.results:
            status = "PASS" if result.passed else "FAIL"
            lines.append(f"[{status}] task {result.task_index} instance_id={result.instance_id}")
            for message in result.errors:
                lines.append(f"  ERROR: {message}")
            for message in result.warnings:
                lines.append(f"  WARN:  {message}")
            if result.passed and not result.warnings:
                lines.append("  (no issues)")
            lines.append("")
        lines.append("OVERALL: PASS" if self.ok else "OVERALL: FAIL")
        return "\n".join(lines)


def load_labelstudio_export(path: Path) -> List[Dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, list):
        raise ValueError("Label Studio export must be a JSON array of tasks")
    for index, task in enumerate(payload):
        if not isinstance(task, dict):
            raise ValueError(f"task {index}: expected JSON object")
    return payload


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    return str(value).strip().lower() in {"true", "1", "yes"}


def _extract_choices(annotation_result: Sequence[Mapping[str, Any]], from_name: str) -> List[str]:
    values: List[str] = []
    for item in annotation_result:
        if item.get("from_name") != from_name:
            continue
        value = item.get("value") or {}
        choices = value.get("choices") or []
        if isinstance(choices, str):
            choices = [choices]
        values.extend(str(choice) for choice in choices)
    return values


def _latest_annotation(task: Mapping[str, Any]) -> List[Dict[str, Any]]:
    annotations = task.get("annotations") or []
    if not annotations:
        return []
    completed = [ann for ann in annotations if not ann.get("was_cancelled")]
    if not completed:
        return []
    return list(completed[-1].get("result") or [])


def validate_task(task: Mapping[str, Any], task_index: int) -> TaskValidationResult:
    data = task.get("data") or {}
    instance_id = str(data.get("instance_id") or f"<missing-{task_index}>")
    errors: List[str] = []
    warnings: List[str] = []

    for field_name in REQUIRED_DATA_FIELDS:
        if field_name not in data:
            errors.append(f"data.{field_name}: required field missing")

    task_type = str(data.get("task_type", "")).strip()
    if task_type and task_type not in VALID_TASK_TYPES:
        errors.append(f"data.task_type: invalid value {task_type!r}")

    experimental = _as_bool(data.get("experimental_subset"))

    result = _latest_annotation(task)
    if not result:
        errors.append("annotations: no completed annotation found")
        return TaskValidationResult(task_index, instance_id, False, errors, warnings)

    pragmatic = _extract_choices(result, "pragmatic_function")
    if len(pragmatic) != 1:
        errors.append(f"pragmatic_function: expected exactly 1 label, got {len(pragmatic)} ({pragmatic})")
    elif pragmatic[0] not in PRAGMATIC_FUNCTIONS:
        errors.append(f"pragmatic_function: unknown label {pragmatic[0]!r}")

    fallacy_labels = _extract_choices(result, "fallacy_labels")
    fallacy_none = _extract_choices(result, "fallacy_none_explicit")

    invalid_fallacies = [label for label in fallacy_labels if label not in FALLACY_LABELS]
    if invalid_fallacies:
        errors.append(f"fallacy_labels: unknown labels {invalid_fallacies}")

    has_explicit_none = any(_as_bool(value) for value in fallacy_none)
    if has_explicit_none and fallacy_labels:
        errors.append("fallacy: fallacy_none_explicit cannot be combined with fallacy_labels")
    if not has_explicit_none and not fallacy_labels:
        errors.append("fallacy: require fallacy_labels or fallacy_none_explicit=true")
    if len(fallacy_labels) > MAX_FALLACY_LABELS:
        errors.append(f"fallacy_labels: max {MAX_FALLACY_LABELS} labels allowed, got {len(fallacy_labels)}")

    semantic = _extract_choices(result, "semantic_vacuity")
    conceptual = _extract_choices(result, "conceptual_anachronism")

    if experimental:
        if len(semantic) != 1:
            errors.append(f"semantic_vacuity: required when experimental_subset=true, got {len(semantic)}")
        elif semantic[0] not in SEMANTIC_VACUITY:
            errors.append(f"semantic_vacuity: unknown label {semantic[0]!r}")
        if len(conceptual) != 1:
            errors.append(
                f"conceptual_anachronism: required when experimental_subset=true, got {len(conceptual)}"
            )
        elif conceptual[0] not in CONCEPTUAL_ANACHRONISM:
            errors.append(f"conceptual_anachronism: unknown label {conceptual[0]!r}")
    else:
        if semantic:
            errors.append("semantic_vacuity: must not be present when experimental_subset=false")
        if conceptual:
            errors.append("conceptual_anachronism: must not be present when experimental_subset=false")

    if task_type == "adjudication" and not str(data.get("adjudication_context", "")).strip():
        warnings.append("adjudication_context: empty for adjudication task")

    passed = len(errors) == 0
    return TaskValidationResult(task_index, instance_id, passed, errors, warnings)


def validate_export(tasks: Iterable[Mapping[str, Any]], input_path: Path) -> ValidationReport:
    report = ValidationReport(input_path=input_path)
    for index, task in enumerate(tasks):
        result = validate_task(task, index)
        report.results.append(result)
        report.total_tasks += 1
        if result.passed:
            report.passed_tasks += 1
        else:
            report.failed_tasks += 1
    return report


def setup_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate a Label Studio JSON export against SPDB v1 annotation rules.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Path to Label Studio JSON export file.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write the validation report as plain text.",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    setup_logging(args.log_level)

    if not args.input.exists():
        logger.error("Input not found: %s", args.input)
        return 1

    try:
        tasks = load_labelstudio_export(args.input)
        report = validate_export(tasks, args.input)
    except (ValueError, json.JSONDecodeError) as exc:
        logger.error("%s", exc)
        return 1

    text = report.to_text()
    print(text)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
        logger.info("Report written to %s", args.output)

    return 0 if report.ok else 2


if __name__ == "__main__":
    sys.exit(main())
