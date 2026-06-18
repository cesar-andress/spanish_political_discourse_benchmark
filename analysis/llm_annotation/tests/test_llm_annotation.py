"""Tests for SPDB LLM annotation pipeline."""

from __future__ import annotations

import json
from pathlib import Path

from analysis.llm_annotation.backend import CommandBackend, MockResponseBackend
from analysis.llm_annotation.constants import FIXTURE_MOCK_RESPONSES, FIXTURE_PILOT_MINI
from analysis.llm_annotation.io import load_pilot_units
from analysis.llm_annotation.parser import parse_model_response
from analysis.llm_annotation.pipeline import run_dry_run
from analysis.llm_annotation.prompts import build_prompt
from analysis.llm_annotation.validator import normalize_record
from scripts.llm_annotation.validate_llm_annotations import main as validate_main


def test_build_prompt_contains_inventories():
    units = load_pilot_units(FIXTURE_PILOT_MINI)
    prompt = build_prompt(units[0], model_name="test-model", mode="zero_shot")
    assert "PF_ADVOCACY" in prompt
    assert "FAL_NONE" in prompt
    assert units[0].unit_id in prompt
    assert "exactly one" in prompt.lower()


def test_parse_json_from_fenced_response():
    raw = (
        'Here is the answer:\n```json\n'
        '{"unit_id":"u001","model_name":"m","pragmatic_function":"PF_INFO","fallacy_labels":["FAL_NONE"]}\n'
        "```"
    )
    data, err = parse_model_response(raw, unit_id="u001", model_name="m")
    assert err is None
    assert data["pragmatic_function"] == "PF_INFO"


def test_normalize_fallacy_none_default():
    record = normalize_record(
        {"unit_id": "u001", "pragmatic_function": "PF_INFO", "fallacy_labels": []},
        model_name="m",
    )
    assert record["fallacy_labels"] == ["FAL_NONE"]


def test_dry_run_generates_report(tmp_path: Path):
    report = tmp_path / "dry_run_report.md"
    result = run_dry_run(
        pilot_path=FIXTURE_PILOT_MINI,
        report_path=report,
        model_name="mock-model",
    )
    assert report.exists()
    assert result.validation.ok
    assert result.validation.total_records == 3


def test_validate_cli_on_mock_jsonl(tmp_path: Path):
    units = load_pilot_units(FIXTURE_PILOT_MINI)
    path = tmp_path / "mock.jsonl"
    with path.open("w", encoding="utf-8") as handle:
        for unit in units:
            payload = {
                "unit_id": unit.unit_id,
                "model_name": "mock",
                "pragmatic_function": "PF_INFO",
                "fallacy_labels": ["FAL_NONE"],
            }
            handle.write(json.dumps(payload) + "\n")
    assert validate_main(["--annotations", str(path), "--pilot-input", str(FIXTURE_PILOT_MINI)]) == 0


def test_mock_backend_with_fixture_responses():
    mapping = {
        json.loads(line)["unit_id"]: line
        for line in FIXTURE_MOCK_RESPONSES.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }
    backend = MockResponseBackend(mapping)
    units = load_pilot_units(FIXTURE_PILOT_MINI)
    prompt = build_prompt(units[0], model_name="mock", mode="zero_shot")
    response = backend.generate(prompt)
    data, err = parse_model_response(response, unit_id=units[0].unit_id, model_name="mock")
    assert err is None
    assert data["pragmatic_function"].startswith("PF_")


def test_command_backend_with_mock_script(tmp_path: Path):
    script = tmp_path / "mock_backend.py"
    script.write_text(
        "import json, sys\n"
        "prompt = sys.stdin.read()\n"
        "unit_id = 'spdb-v1-test'\n"
        "for line in prompt.splitlines():\n"
        "    if line.startswith('unit_id:'):\n"
        "        unit_id = line.split(':',1)[1].strip()\n"
        "print(json.dumps({'unit_id': unit_id, 'model_name': 'mock', "
        "'pragmatic_function': 'PF_INFO', 'fallacy_labels': ['FAL_NONE']}))\n",
        encoding="utf-8",
    )
    backend = CommandBackend(f"python3.11 {script}")
    out = backend.generate("unit_id: spdb-v1-test\n")
    data, err = parse_model_response(out, unit_id="spdb-v1-test", model_name="mock")
    assert err is None
    assert data["pragmatic_function"] == "PF_INFO"
