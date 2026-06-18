"""Tests for Human-vs-LLM comparison framework."""

from __future__ import annotations

from pathlib import Path

import pytest

from analysis.human_vs_llm.ambiguity import analyze_ambiguity
from analysis.human_vs_llm.constants import (
    FIXTURE_ADJUDICATED,
    FIXTURE_ANNOTATORS,
    FIXTURE_LLM,
)
from analysis.human_vs_llm.gold import build_gold, build_majority_vote_gold, build_unanimous_gold
from analysis.human_vs_llm.io import load_human_annotations, load_llm_annotations
from analysis.human_vs_llm.pipeline import run_pipeline


@pytest.fixture()
def output_dir(tmp_path: Path) -> Path:
    return tmp_path / "human_vs_llm"


def test_pending_mode_when_human_files_missing(output_dir: Path):
    missing_dir = output_dir / "missing_inputs"
    result = run_pipeline(
        annotator_paths=(
            missing_dir / "annotator_a.csv",
            missing_dir / "annotator_b.csv",
            missing_dir / "annotator_c.csv",
        ),
        output_dir=output_dir / "pending",
    )
    assert result.pending is True
    readme = output_dir / "pending" / "README_PENDING.md"
    assert readme.exists()
    assert "annotator_a.csv" in readme.read_text(encoding="utf-8")


def test_majority_vote_full_split_is_ambiguous(output_dir: Path):
    human = load_human_annotations(FIXTURE_ANNOTATORS)
    gold = build_majority_vote_gold(human)
    split = [unit for unit in gold.units if unit.exclusion_reason == "full_split"]
    assert split
    assert split[0].unit_id == "u003"
    assert split[0].gold_label is None
    assert split[0].ambiguous is True


def test_unanimous_only_excludes_disagreements(output_dir: Path):
    human = load_human_annotations(FIXTURE_ANNOTATORS)
    gold = build_unanimous_gold(human)
    evaluable = gold.evaluable_units
    eval_ids = {unit.unit_id for unit in evaluable}
    assert "u001" in eval_ids
    assert "u002" in eval_ids
    assert "u003" not in eval_ids
    assert "u007" not in eval_ids


def test_fixture_pipeline_generates_reports(output_dir: Path):
    result = run_pipeline(
        annotator_paths=FIXTURE_ANNOTATORS,
        adjudicated_path=FIXTURE_ADJUDICATED,
        llm_paths=[FIXTURE_LLM],
        output_dir=output_dir,
    )
    assert result.pending is False
    assert result.gold is not None
    assert len(result.system_results) == 1

    mock = result.system_results[0]
    assert mock.system_name == "mock_llm"
    assert mock.scores.n_evaluated > 0
    assert mock.scores.invalid_rate > 0

    assert (output_dir / "human_vs_llm_report.md").exists()
    assert (output_dir / "system_scores.csv").exists()
    assert (output_dir / "per_class_scores.csv").exists()
    assert (output_dir / "human_vs_llm_table.tex").exists()
    assert (output_dir / "confusion_matrices" / "mock_llm_confusion.json").exists()


def test_ambiguity_cases_detected(output_dir: Path):
    human = load_human_annotations(FIXTURE_ANNOTATORS)
    gold = build_gold(human, "majority_vote", adjudicated_path=FIXTURE_ADJUDICATED)
    llm = load_llm_annotations(FIXTURE_LLM)
    report = analyze_ambiguity(human, gold, llm)

    assert "u003" in report.full_split_units
    assert any(item["unit_id"] == "u002" for item in report.unanimous_human_llm_fail)
    assert any(item["unit_id"] == "u008" for item in report.llm_agrees_one_human_not_gold)
    assert any(item["unit_id"] == "u003" for item in report.human_disagree_llm_picks_side)


def test_adjudicated_strategy(output_dir: Path):
    human = load_human_annotations(FIXTURE_ANNOTATORS)
    gold = build_gold(human, "adjudicated_file", adjudicated_path=FIXTURE_ADJUDICATED)
    u003 = next(unit for unit in gold.evaluable_units if unit.unit_id == "u003")
    assert u003.gold_label == "PF_ATTACK"
