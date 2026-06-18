"""Constants for LLM annotation pipeline."""

from __future__ import annotations

from pathlib import Path

DEFAULT_PILOT_INPUT = Path("annotation/pilot_001/pilot_100_units.csv")
DEFAULT_OUTPUT_DIR = Path("data/experiments/llm_annotations")
DEFAULT_REPORT_DIR = Path("reports/llm_annotation")
DEFAULT_DRY_RUN_REPORT = DEFAULT_REPORT_DIR / "dry_run_report.md"
DEFAULT_ANNOTATION_REPORT = DEFAULT_REPORT_DIR / "llm_annotation_report.md"

PROMPTS_DIR = Path("prompts")
PF_ZERO_SHOT = PROMPTS_DIR / "pragmatic_function_zero_shot.txt"
PF_FEW_SHOT = PROMPTS_DIR / "pragmatic_function_few_shot.txt"
FALLACY_ZERO_SHOT = PROMPTS_DIR / "fallacy_zero_shot.txt"

SCHEMA_PATH = Path("schemas/llm_annotation_output.schema.json")
PF_INVENTORY = Path("labels/pragmatic_functions.tsv")
FAL_INVENTORY = Path("labels/fallacies.tsv")

FEW_SHOT_EXAMPLES = """\
Example 1 — PF_ADVOCACY
text: «En Ciudadanos abogamos por definir la figura del consumidor vulnerable…»
label: PF_ADVOCACY

Example 2 — PF_ATTACK
text: «Ustedes ni siquiera han estado sentados en la mesa… no han conseguido nada.»
label: PF_ATTACK

Example 3 — PF_PROCEDURAL
text: «Muchas gracias, señora presidenta. Tiene la palabra el portavoz.»
label: PF_PROCEDURAL
"""

FIXTURE_PILOT_MINI = Path("tests/fixtures/llm_annotation/pilot_mini.csv")
FIXTURE_MOCK_RESPONSES = Path("tests/fixtures/llm_annotation/mock_responses.jsonl")
