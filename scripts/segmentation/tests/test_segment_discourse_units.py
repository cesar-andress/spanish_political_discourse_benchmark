from __future__ import annotations

from pathlib import Path

from scripts.segmentation.segment_discourse_units import main
from scripts.ingestion.common import read_jsonl, validate_pipeline_discourse_unit
from scripts.segmentation.tests.conftest import FIXTURES


def test_cli_dry_run():
    assert (
        main(
            [
                "--input",
                str(FIXTURES / "sample_long_document.jsonl"),
                "--dry-run",
                "--max-tokens",
                "80",
                "--log-level",
                "ERROR",
            ]
        )
        == 0
    )


def test_cli_writes_pipeline_jsonl(tmp_path: Path):
    output = tmp_path / "discourse_units.jsonl"
    assert (
        main(
            [
                "--input",
                str(FIXTURES / "sample_long_document.jsonl"),
                "--output",
                str(output),
                "--max-tokens",
                "80",
                "--log-level",
                "ERROR",
            ]
        )
        == 0
    )
    units = list(read_jsonl(output))
    assert units
    assert all("unit_id" in unit for unit in units)
    assert all("metadata" in unit for unit in units)
    assert all(not validate_pipeline_discourse_unit(unit) for unit in units)
