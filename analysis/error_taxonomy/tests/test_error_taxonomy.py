"""Tests for automatic error taxonomy generation."""

from __future__ import annotations

from pathlib import Path

from analysis.error_taxonomy.clusters import analyze_taxonomy
from analysis.error_taxonomy.constants import ERROR_CLUSTERS, FIXTURE_ANNOTATORS, FIXTURE_LLM
from analysis.error_taxonomy.io import build_inventory, collect_human_disagreements
from analysis.error_taxonomy.pipeline import run_error_taxonomy_fixtures
from analysis.error_taxonomy.report import render_error_taxonomy
from analysis.human_vs_llm.io import load_human_annotations


def test_cluster_definitions_cover_requested_pairs():
    titles = {cluster.title for cluster in ERROR_CLUSTERS}
    assert "ATTACK vs DEFENSE" in titles
    assert "ADVOCACY vs PROPOSAL" in titles
    assert "APPEAL vs ADVOCACY" in titles
    assert "DEFLECT vs DEFENSE" in titles


def test_fixture_human_disagreements_hit_all_clusters():
    human = load_human_annotations(FIXTURE_ANNOTATORS)
    transitions, n_units, _ = collect_human_disagreements(human)
    assert n_units >= 4
    cluster_ids = {
        cluster.cluster_id
        for cluster in ERROR_CLUSTERS
        if any(cluster.matches_pair(item.source, item.target) for item in transitions)
    }
    assert cluster_ids == {cluster.cluster_id for cluster in ERROR_CLUSTERS}


def test_fixture_inventory_and_model_errors():
    inventory = build_inventory(
        annotator_paths=FIXTURE_ANNOTATORS,
        adjudicated_path=FIXTURE_ANNOTATORS[0].parent / "adjudicated.csv",
        llm_paths=[FIXTURE_LLM],
        gold_strategy="adjudicated_file",
    )
    assert inventory is not None
    assert inventory.n_model_errors >= 4
    taxonomy = analyze_taxonomy(inventory)
    assert taxonomy.total_human_clustered > 0
    assert taxonomy.total_model_clustered > 0


def test_pipeline_writes_publication_tables(tmp_path: Path):
    result = run_error_taxonomy_fixtures(output_path=tmp_path / "error_taxonomy.md")
    assert result.pending is False
    text = result.output_path.read_text(encoding="utf-8")
    assert "## Table 1." in text
    assert "## Table 2." in text
    assert "ATTACK vs DEFENSE" in text
    assert "ADVOCACY vs PROPOSAL" in text
    assert (tmp_path / "error_taxonomy").exists() or result.export_dir.exists()


def test_render_includes_directional_table():
    inventory = build_inventory(
        annotator_paths=FIXTURE_ANNOTATORS,
        adjudicated_path=FIXTURE_ANNOTATORS[0].parent / "adjudicated.csv",
        llm_paths=[FIXTURE_LLM],
        gold_strategy="adjudicated_file",
    )
    assert inventory is not None
    report = render_error_taxonomy(analyze_taxonomy(inventory))
    assert "Reference → Alternate" in report
    assert "PF_ATTACK" in report
