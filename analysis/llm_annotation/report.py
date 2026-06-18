"""Markdown reports for LLM annotation pipeline."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import List, Sequence

from analysis.llm_annotation.io import PilotUnit
from analysis.llm_annotation.prompts import PromptMode
from analysis.llm_annotation.validator import ValidationSummary


def _distribution_table(counter: Counter[str], title: str) -> List[str]:
    lines = [f"### {title}", "", "| Label | Count | Share |", "|-------|------:|------:|"]
    total = sum(counter.values()) or 1
    for label, count in counter.most_common():
        lines.append(f"| `{label}` | {count} | {100.0 * count / total:.1f}% |")
    lines.append("")
    return lines


def write_dry_run_report(
    path: Path,
    *,
    units: Sequence[PilotUnit],
    sample_prompt: str,
    validation: ValidationSummary,
    model_name: str,
    mode: PromptMode,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SPDB LLM annotation — dry run report",
        "",
        f"**Model placeholder:** `{model_name}`  ",
        f"**Prompt mode:** `{mode}`  ",
        f"**Pilot units loaded:** {len(units)}  ",
        f"**Validation status:** {'OK' if validation.ok else 'ISSUES DETECTED'}",
        "",
        "## Summary",
        "",
        "Dry-run mode builds prompts for the 100-unit pilot, applies deterministic mock "
        "responses, and validates JSON output against `schemas/llm_annotation_output.schema.json`. "
        "No external or paid API is called.",
        "",
        "| Check | Result |",
        "|-------|--------|",
        f"| Expected units | {validation.expected_units} |",
        f"| Mock records validated | {validation.total_records} |",
        f"| Parse failure rate | {validation.parse_failure_rate:.3f} |",
        f"| Invalid label rate | {validation.invalid_label_rate:.3f} |",
        f"| Missing unit_id | {len(validation.missing_unit_ids)} |",
        f"| Duplicate unit_id | {validation.duplicate_unit_ids} |",
        "",
        "## Sample prompt (first unit)",
        "",
        "```text",
        sample_prompt[:4000],
        "```",
        "",
        "## Next step — local model run",
        "",
        "```bash",
        "make llm-annotation-local MODEL_NAME=llama-local BACKEND_COMMAND=\"ollama run llama3\"",
        "```",
        "",
    ]
    if validation.errors:
        lines.extend(["## Validation notes", ""])
        for error in validation.errors[:20]:
            lines.append(f"- {error}")
        lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def write_annotation_report(
    path: Path,
    *,
    model_name: str,
    validation: ValidationSummary,
    records: Sequence[dict],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pf_counts: Counter[str] = Counter()
    fal_counts: Counter[str] = Counter()
    for record in records:
        if record.get("_parse_error"):
            continue
        pf = record.get("pragmatic_function")
        if pf:
            pf_counts[str(pf)] += 1
        for label in record.get("fallacy_labels", []) or []:
            fal_counts[str(label)] += 1

    lines = [
        "# SPDB LLM annotation report",
        "",
        f"**Model:** `{model_name}`  ",
        f"**Units processed:** {validation.total_records}  ",
        f"**Validation status:** {'OK' if validation.ok else 'ISSUES DETECTED'}",
        "",
        "## Quality metrics",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| Parse failure rate | {validation.parse_failure_rate:.3f} |",
        f"| Invalid label rate | {validation.invalid_label_rate:.3f} |",
        f"| Missing unit_id | {len(validation.missing_unit_ids)} |",
        f"| Duplicate unit_id | {validation.duplicate_unit_ids} |",
        "",
    ]
    lines.extend(_distribution_table(pf_counts, "Pragmatic-function label distribution"))
    lines.extend(_distribution_table(fal_counts, "Fallacy label distribution"))

    if validation.errors:
        lines.extend(["## Validation errors", ""])
        for error in validation.errors[:30]:
            lines.append(f"- {error}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
