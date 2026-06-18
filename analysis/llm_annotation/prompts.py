"""Prompt construction for LLM annotation."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from analysis.llm_annotation.constants import (
    FALLACY_ZERO_SHOT,
    FEW_SHOT_EXAMPLES,
    PF_FEW_SHOT,
    PF_ZERO_SHOT,
)
from analysis.llm_annotation.io import PilotUnit
from analysis.llm_annotation.labels import format_fal_inventory, format_pf_inventory

PromptMode = Literal["zero_shot", "few_shot"]


def _read_template(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render(template: str, values: dict[str, str]) -> str:
    text = template
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def build_prompt(
    unit: PilotUnit,
    *,
    model_name: str,
    mode: PromptMode = "zero_shot",
) -> str:
    pf_template_path = PF_FEW_SHOT if mode == "few_shot" else PF_ZERO_SHOT
    pf_template = _read_template(pf_template_path)
    fallacy_template = _read_template(FALLACY_ZERO_SHOT)

    shared = {
        "UNIT_ID": unit.unit_id,
        "TEXT": unit.text,
        "SPEAKER_NAME": unit.speaker_name,
        "SPEAKER_PARTY": unit.speaker_party,
        "DATE": unit.date,
        "MODEL_NAME": model_name,
        "PF_LABELS": format_pf_inventory(),
        "FAL_LABELS": format_fal_inventory(),
        "FEW_SHOT_EXAMPLES": FEW_SHOT_EXAMPLES if mode == "few_shot" else "",
    }

    pf_section = _render(pf_template, shared)
    fallacy_section = _render(fallacy_template, shared)
    return pf_section.strip() + "\n\n" + fallacy_section.strip() + "\n"
