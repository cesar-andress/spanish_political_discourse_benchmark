"""Prompt rendering for SPDB external fallacy batch runs."""

from __future__ import annotations

from pathlib import Path

from analysis.external_validation.fallacy_constants import SPDB_FAL_LABELS


def format_fal_inventory() -> str:
    lines = []
    for label in SPDB_FAL_LABELS:
        lines.append(f"- `{label}`")
    lines.append("- `FAL_NONE` — no fallacy (express via empty `fallacy_labels` + `fallacy_none_explicit=true`)")
    return "\n".join(lines)


def render_fallacy_prompt(
    template_path: Path,
    *,
    text: str,
    row_id: str,
    model_name: str,
) -> str:
    template = template_path.read_text(encoding="utf-8")
    values = {
        "TEXT": text,
        "ROW_ID": row_id,
        "MODEL_NAME": model_name,
        "FAL_LABELS": format_fal_inventory(),
    }
    rendered = template
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    return rendered.strip() + "\n"
