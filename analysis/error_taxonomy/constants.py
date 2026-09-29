"""Paths and cluster definitions for SPDB error taxonomy generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "reports/error_taxonomy.md"
DEFAULT_EXPORT_DIR = ROOT / "reports/error_taxonomy"

DEFAULT_ANNOTATORS = (
    ROOT / "annotation/pilot_001/pilot_100_units_annotator_a.csv",
    ROOT / "annotation/pilot_001/pilot_100_units_annotator_b.csv",
    ROOT / "annotation/pilot_001/pilot_100_units_annotator_c.csv",
)
DEFAULT_ADJUDICATED = ROOT / "annotation/pilot_001/pilot_100_units_adjudicated.csv"
DEFAULT_LLM_DIR = ROOT / "data/experiments/llm_annotations"

FIXTURE_DIR = ROOT / "tests/fixtures/error_taxonomy"
FIXTURE_ANNOTATORS = (
    FIXTURE_DIR / "annotator_a.csv",
    FIXTURE_DIR / "annotator_b.csv",
    FIXTURE_DIR / "annotator_c.csv",
)
FIXTURE_ADJUDICATED = FIXTURE_DIR / "adjudicated.csv"
FIXTURE_LLM = FIXTURE_DIR / "mock_model_pilot.jsonl"

PF_COLUMN = "pragmatic_function"


@dataclass(frozen=True)
class ErrorCluster:
    cluster_id: str
    title: str
    label_a: str
    label_b: str
    description: str

    def matches_pair(self, left: str, right: str) -> bool:
        return {left, right} == {self.label_a, self.label_b}

    def canonical_key(self, left: str, right: str) -> tuple[str, str] | None:
        if not self.matches_pair(left, right):
            return None
        return (left, right)


ERROR_CLUSTERS: tuple[ErrorCluster, ...] = (
    ErrorCluster(
        cluster_id="attack_defense",
        title="ATTACK vs DEFENSE",
        label_a="PF_ATTACK",
        label_b="PF_DEFENSE",
        description="Oppositional stance boundary between criticizing a target and rebutting criticism.",
    ),
    ErrorCluster(
        cluster_id="advocacy_proposal",
        title="ADVOCACY vs PROPOSAL",
        label_a="PF_ADVOCACY",
        label_b="PF_PROPOSAL",
        description="Policy endorsement vs concrete legislative or programmatic commitment.",
    ),
    ErrorCluster(
        cluster_id="appeal_advocacy",
        title="APPEAL vs ADVOCACY",
        label_a="PF_APPEAL",
        label_b="PF_ADVOCACY",
        description="Electoral or mobilizational call vs programmatic support for a policy line.",
    ),
    ErrorCluster(
        cluster_id="deflect_defense",
        title="DEFLECT vs DEFENSE",
        label_a="PF_DEFLECT",
        label_b="PF_DEFENSE",
        description="Topic shift away from the question vs direct rebuttal of an accusation.",
    ),
)

CLUSTER_BY_ID = {cluster.cluster_id: cluster for cluster in ERROR_CLUSTERS}
