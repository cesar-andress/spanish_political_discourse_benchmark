from __future__ import annotations

from pathlib import Path

from scripts.validation.validate_labelstudio_export import (
    load_labelstudio_export,
    validate_export,
    validate_task,
)
from tests.conftest import FIXTURES


def test_import_fixture_has_three_synthetic_tasks():
    tasks = load_labelstudio_export(FIXTURES / "labelstudio_import_sample.json")
    assert len(tasks) == 3
    assert all("Texto sintético" in task["data"]["text"] for task in tasks)
    assert tasks[0]["data"]["task_type"] == "primary"
    assert tasks[1]["data"]["experimental_subset"] == "true"
    assert tasks[2]["data"]["task_type"] == "adjudication"


def test_valid_export_sample_passes():
    path = FIXTURES / "labelstudio_export_sample.json"
    report = validate_export(load_labelstudio_export(path), path)
    assert report.ok
    assert report.total_tasks == 3
    assert report.failed_tasks == 0


def test_invalid_export_sample_fails():
    path = FIXTURES / "labelstudio_export_invalid.json"
    report = validate_export(load_labelstudio_export(path), path)
    assert not report.ok
    assert report.failed_tasks == 1
    result = report.results[0]
    assert any("pragmatic_function" in err for err in result.errors)
    assert any("semantic_vacuity" in err for err in result.errors)


def test_fallacy_none_and_labels_mutually_exclusive():
    task = {
        "data": {
            "instance_id": "x",
            "document_id": "d",
            "text": "Texto sintético.",
            "task_type": "primary",
            "experimental_subset": "false",
            "adjudication_context": "",
        },
        "annotations": [
            {
                "result": [
                    {"from_name": "pragmatic_function", "to_name": "text", "value": {"choices": ["PF_INFO"]}},
                    {"from_name": "fallacy_none_explicit", "to_name": "text", "value": {"choices": ["true"]}},
                    {"from_name": "fallacy_labels", "to_name": "text", "value": {"choices": ["FAL_ADHOM"]}},
                ]
            }
        ],
    }
    result = validate_task(task, 0)
    assert not result.passed
    assert any("fallacy_none_explicit cannot be combined" in err for err in result.errors)
