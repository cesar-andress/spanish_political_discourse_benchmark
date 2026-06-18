"""Project FallacyES-Political labels onto the SPDB fallacy inventory."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

MatchKind = str  # exact | partial | approximate | none

MATCH_RANK: Dict[MatchKind, int] = {
    "exact": 4,
    "partial": 3,
    "approximate": 2,
    "none": 1,
}

MATCH_CONFIDENCE: Dict[MatchKind, float] = {
    "exact": 1.0,
    "partial": 0.75,
    "approximate": 0.5,
    "none": 0.0,
}

# Rows mirror reports/external_validation/fallacy_mapping.md (FallacyES-Political).
FALLACYES_POLITICAL_MAPPINGS: Tuple[Tuple[str, str, MatchKind, str], ...] = (
    ("FAL_ADHOM", "Ad Hominem", "exact", "Direct label correspondence."),
    ("FAL_ADHOM", "Poisoning the Well", "partial", "Both attack speaker credibility."),
    ("FAL_ADHOM", "Guilt by Association", "approximate", "Associative attack; salience-dependent."),
    ("FAL_STRAW", "Strawman", "exact", "Direct label correspondence."),
    ("FAL_DILEMMA", "False Dilemma", "exact", "Direct label correspondence."),
    ("FAL_SLOPE", "Slippery Slope", "exact", "Direct label correspondence."),
    ("FAL_EMOTION", "Appeal to Emotion", "exact", "Direct label correspondence."),
    ("FAL_EMOTION", "Appeal to Fear", "partial", "Fear subtype under SPDB FAL_EMOTION."),
    ("FAL_EMOTION", "Flag Waving", "partial", "Patriotic emotional appeal."),
    ("FAL_GENERAL", "Hasty Generalization", "exact", "Direct label correspondence."),
    ("FAL_GENERAL", "False Cause", "approximate", "Causal overgeneralization overlap."),
    ("FAL_GENERAL", "False Analogy", "approximate", "Weak analogy overlap."),
    ("FAL_WHATABOUT", "Ad Populum", "approximate", "Populist bandwagon; partial overlap."),
    ("FAL_WHATABOUT", "Complex Question", "none", "Loaded question; not SPDB whataboutism."),
    ("FAL_NONE", "Wishful Thinking", "none", "External positive fallacy; no SPDB projection."),
)


@dataclass(frozen=True)
class ProjectedLabel:
    spdb_label: str
    mapping_type: MatchKind
    mapping_confidence: float
    mapping_notes: str


@dataclass(frozen=True)
class ProjectionResult:
    spdb_fallacy_labels: Tuple[str, ...]
    mapping_type: MatchKind
    mapping_confidence: float
    mapping_notes: str


def _build_external_lookup() -> Dict[str, ProjectedLabel]:
    lookup: Dict[str, ProjectedLabel] = {}
    for spdb_label, external_label, match_type, notes in FALLACYES_POLITICAL_MAPPINGS:
        rank = MATCH_RANK[match_type]
        projected = ProjectedLabel(
            spdb_label=spdb_label if match_type != "none" else "",
            mapping_type=match_type,
            mapping_confidence=MATCH_CONFIDENCE[match_type],
            mapping_notes=notes,
        )
        existing = lookup.get(external_label)
        if existing is None or rank > MATCH_RANK[existing.mapping_type]:
            lookup[external_label] = projected
    return lookup


EXTERNAL_LABEL_LOOKUP = _build_external_lookup()


def split_external_labels(original_label: str) -> List[str]:
    parts = [part.strip() for part in (original_label or "").split(",") if part.strip()]
    return parts or [""]


def project_original_label(original_label: str) -> ProjectionResult:
    components = split_external_labels(original_label)
    projected: List[ProjectedLabel] = []
    unmapped: List[str] = []

    for component in components:
        match = EXTERNAL_LABEL_LOOKUP.get(component)
        if match is None:
            unmapped.append(component)
            continue
        if match.mapping_type == "none" or not match.spdb_label:
            unmapped.append(component)
            continue
        projected.append(match)

    spdb_labels: List[str] = []
    for item in projected:
        if item.spdb_label and item.spdb_label not in spdb_labels:
            spdb_labels.append(item.spdb_label)
        if len(spdb_labels) >= 3:
            break

    if not projected:
        notes = "No SPDB projection for: " + ", ".join(unmapped or components)
        return ProjectionResult((), "none", 0.0, notes)

    best = max(projected, key=lambda item: MATCH_RANK[item.mapping_type])
    confidences = [item.mapping_confidence for item in projected]
    notes_parts = [f"{item.spdb_label} ({item.mapping_type})" for item in projected]
    if unmapped:
        notes_parts.append("unmapped: " + ", ".join(unmapped))
    return ProjectionResult(
        tuple(spdb_labels),
        best.mapping_type,
        sum(confidences) / len(confidences),
        "; ".join(notes_parts),
    )


def summarize_mapping_types(rows: Iterable[Mapping[str, str]]) -> Dict[str, int]:
    counts = {"exact": 0, "partial": 0, "approximate": 0, "none": 0}
    for row in rows:
        mapping_type = str(row.get("mapping_type", "none"))
        counts[mapping_type] = counts.get(mapping_type, 0) + 1
    return counts
