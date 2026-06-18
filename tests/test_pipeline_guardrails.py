from __future__ import annotations

import subprocess
from pathlib import Path

BENCHMARK_ROOT = Path(__file__).resolve().parents[1]


def test_make_pipeline_requires_ingest_input():
    result = subprocess.run(
        ["make", "pipeline"],
        cwd=BENCHMARK_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode != 0
    assert "INGEST_INPUT is required" in result.stderr + result.stdout


def test_make_pipeline_fixture_succeeds():
    result = subprocess.run(
        ["make", "pipeline-fixture"],
        cwd=BENCHMARK_ROOT,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stdout + result.stderr
