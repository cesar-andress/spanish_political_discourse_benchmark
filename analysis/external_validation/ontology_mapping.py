"""SPDB fallacy ontology mappings to external dataset label schemes."""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from analysis.external_validation.constants import (
    DEFAULT_REPORT_DIR,
    EXTERNAL_DATASETS,
    SPDB_FAL_LABELS,
    ExternalDataset,
    LabelMapping,
    MatchKind,
)

# Primary mapping table: dataset_id -> list[LabelMapping]
ONTOLOGY_MAPPINGS: Dict[str, Sequence[LabelMapping]] = {
    "fallacyes_political": (
        LabelMapping("FAL_ADHOM", "Ad Hominem", "exact", "Direct label correspondence."),
        LabelMapping("FAL_ADHOM", "Poisoning the Well", "partial", "Both attack speaker credibility; SPDB requires personal disqualification salience."),
        LabelMapping("FAL_ADHOM", "Guilt by Association", "approximate", "Associative attack; may map to ad hominem or attack PF layer depending on span."),
        LabelMapping("FAL_STRAW", "Strawman", "exact", "Direct label correspondence."),
        LabelMapping("FAL_DILEMMA", "False Dilemma", "exact", "Direct label correspondence."),
        LabelMapping("FAL_SLOPE", "Slippery Slope", "exact", "Direct label correspondence."),
        LabelMapping("FAL_EMOTION", "Appeal to Emotion", "exact", "Direct label correspondence."),
        LabelMapping("FAL_EMOTION", "Appeal to Fear", "partial", "Fear is a subtype; SPDB FAL_EMOTION covers fear/outrage/pity warrants."),
        LabelMapping("FAL_EMOTION", "Flag Waving", "partial", "Patriotic emotional appeal; often co-occurs with PF_APPEAL."),
        LabelMapping("FAL_GENERAL", "Hasty Generalization", "exact", "Direct label correspondence."),
        LabelMapping("FAL_GENERAL", "False Cause", "approximate", "Causal overgeneralization; SPDB may code as generalization when leap is explicit."),
        LabelMapping("FAL_GENERAL", "False Analogy", "approximate", "Weak analogy can function as hasty generalization across domains."),
        LabelMapping("FAL_WHATABOUT", "Ad Populum", "approximate", "Populist bandwagon differs; no direct FallacyES-Political whataboutism class."),
        LabelMapping("FAL_WHATABOUT", "Complex Question", "none", "Loaded question structure; not SPDB whataboutism."),
        LabelMapping("FAL_NONE", "Wishful Thinking", "none", "External positive fallacy; SPDB none is explicit absence of fallacy inventory."),
        LabelMapping("FAL_NONE", "(no fallacy in FallacyES controls)", "partial", "Both support explicit non-fallacy baselines but with different export semantics."),
    ),
    "fallacyes": (
        LabelMapping("FAL_ADHOM", "ad hominem", "exact", "LOGIC-derived taxonomy in prototypical section."),
        LabelMapping("FAL_STRAW", "straw man", "exact", "Direct correspondence."),
        LabelMapping("FAL_DILEMMA", "false dilemma", "exact", "Direct correspondence."),
        LabelMapping("FAL_SLOPE", "slippery slope", "exact", "Direct correspondence."),
        LabelMapping("FAL_EMOTION", "appeal to emotion", "exact", "Direct correspondence."),
        LabelMapping("FAL_GENERAL", "hasty generalization", "exact", "Direct correspondence."),
        LabelMapping("FAL_WHATABOUT", "tu quoque", "partial", "Tu quoque overlaps deflection/whataboutism; SPDB requires merit non-engagement."),
        LabelMapping("FAL_WHATABOUT", "appeal to worse problems", "approximate", "Deflection via comparative harm; partial overlap."),
        LabelMapping("FAL_NONE", "non-fallacy controls", "partial", "FallacyES includes non-fallacious controls; export semantics differ from FAL_NONE."),
    ),
    "semeval2020_propaganda": (
        LabelMapping("FAL_ADHOM", "Name Calling or Labeling", "approximate", "Insult framing; not always ad hominem rejection of claim merits."),
        LabelMapping("FAL_STRAW", "Loaded Language", "none", "Persuasive wording without misrepresentation requirement."),
        LabelMapping("FAL_DILEMMA", "Black-and-white Fallacy / Dictatorship", "partial", "Forced binary framing; SPDB requires exclusion of reasonable alternatives."),
        LabelMapping("FAL_SLOPE", "Causal Oversimplification", "approximate", "Oversimplified causal chain; not always extreme-outcome slope."),
        LabelMapping("FAL_EMOTION", "Appeal to fear-prejudice", "partial", "Fear-based persuasion overlap."),
        LabelMapping("FAL_EMOTION", "Flag-waving", "partial", "Nationalist emotional appeal."),
        LabelMapping("FAL_GENERAL", "Causal Oversimplification", "approximate", "May encode hasty causal claims."),
        LabelMapping("FAL_WHATABOUT", "Whataboutism", "exact", "Direct technique match (propaganda frame)."),
        LabelMapping("FAL_NONE", "non-propaganda spans", "partial", "Absence label differs from explicit SPDB FAL_NONE coding."),
    ),
    "argotario": (
        LabelMapping("FAL_ADHOM", "ad hominem", "exact", "Direct correspondence."),
        LabelMapping("FAL_STRAW", "straw man", "exact", "Direct correspondence."),
        LabelMapping("FAL_DILEMMA", "false dilemma", "exact", "Direct correspondence."),
        LabelMapping("FAL_SLOPE", "slippery slope", "exact", "Direct correspondence."),
        LabelMapping("FAL_EMOTION", "appeal to emotion", "exact", "Direct correspondence."),
        LabelMapping("FAL_EMOTION", "appeal to fear", "partial", "Fear subtype under SPDB FAL_EMOTION."),
        LabelMapping("FAL_GENERAL", "hasty generalization", "exact", "Direct correspondence."),
        LabelMapping("FAL_WHATABOUT", "whataboutism", "exact", "Direct correspondence."),
        LabelMapping("FAL_WHATABOUT", "tu quoque", "partial", "Closely related deflection pattern."),
        LabelMapping("FAL_NONE", "no fallacy", "partial", "Argotario fallacy vs. non-fallacy distinction; schema differs."),
    ),
    "logic": (
        LabelMapping("FAL_ADHOM", "ad hominem", "exact", "Direct correspondence."),
        LabelMapping("FAL_STRAW", "straw man", "exact", "Direct correspondence."),
        LabelMapping("FAL_DILEMMA", "false dilemma", "exact", "Direct correspondence."),
        LabelMapping("FAL_SLOPE", "slippery slope", "exact", "Direct correspondence."),
        LabelMapping("FAL_EMOTION", "appeal to emotion", "exact", "Direct correspondence."),
        LabelMapping("FAL_GENERAL", "hasty generalization", "exact", "Direct correspondence."),
        LabelMapping("FAL_WHATABOUT", "tu quoque", "partial", "Partial overlap with SPDB whataboutism."),
        LabelMapping("FAL_NONE", "non-fallacy / intentional", "none", "LOGIC 'intentional' is not SPDB none."),
    ),
    "dipromats": (
        LabelMapping("FAL_ADHOM", "propaganda techniques (various)", "none", "Task labels are propaganda/narrative frames."),
        LabelMapping("FAL_WHATABOUT", "propaganda techniques (various)", "approximate", "Possible overlap at technique level only."),
        LabelMapping("FAL_NONE", "non-propaganda", "none", "No shared explicit none code."),
    ),
    "multifallacy_llm_benchmark": (
        LabelMapping("FAL_ADHOM", "corpus-specific ad hominem", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_STRAW", "corpus-specific straw man", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_DILEMMA", "corpus-specific false dilemma", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_SLOPE", "corpus-specific slippery slope", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_EMOTION", "corpus-specific appeal to emotion", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_GENERAL", "corpus-specific hasty generalization", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_WHATABOUT", "corpus-specific whataboutism/tu quoque", "partial", "Requires per-corpus projection table."),
        LabelMapping("FAL_NONE", "corpus-specific non-fallacy", "partial", "Harmonisation needed across sources."),
    ),
    "parliamentary_fallacy_en": (
        LabelMapping("FAL_ADHOM", "Ad Hominem", "exact", "Shared construct in debate fallacy sets."),
        LabelMapping("FAL_STRAW", "Straw Man", "partial", "Label naming varies by release."),
        LabelMapping("FAL_DILEMMA", "False Dilemma", "partial", "Institutional debate annotations."),
        LabelMapping("FAL_SLOPE", "Slippery Slope", "partial", "Institutional debate annotations."),
        LabelMapping("FAL_EMOTION", "Appeal to Emotion", "exact", "Multimodal debate datasets include this class."),
        LabelMapping("FAL_GENERAL", "Hasty Generalization", "partial", "Coverage varies by corpus."),
        LabelMapping("FAL_WHATABOUT", "Whataboutism", "approximate", "May appear under deflection labels."),
        LabelMapping("FAL_NONE", "non-fallacy", "partial", "Export semantics differ."),
    ),
}


def mappings_for_dataset(dataset_id: str) -> List[LabelMapping]:
    return list(ONTOLOGY_MAPPINGS.get(dataset_id, ()))


def spdb_labels_covered(dataset_id: str) -> List[str]:
    return sorted({mapping.spdb_label for mapping in mappings_for_dataset(dataset_id)})


def render_mapping_markdown(
    datasets: Iterable[ExternalDataset] | None = None,
) -> str:
    dataset_rows = list(datasets or EXTERNAL_DATASETS)
    lines = [
        "# SPDB Fallacy Ontology Mapping",
        "",
        "Mapping between SPDB v1 political-fallacy labels and external dataset schemes.",
        "",
        "**SPDB labels:** "
        + ", ".join(f"`{label}`" for label in SPDB_FAL_LABELS),
        "",
        "**Status:** planning document only. No labels have been projected or evaluated.",
        "",
    ]
    for dataset in dataset_rows:
        mappings = mappings_for_dataset(dataset.dataset_id)
        lines.extend([f"## {dataset.name} (`{dataset.dataset_id}`)", ""])
        if not mappings:
            lines.extend(["No mapping rows defined.", ""])
            continue
        lines.extend(
            [
                "| SPDB label | External label | Match | Rationale |",
                "| --- | --- | --- | --- |",
            ]
        )
        for row in mappings:
            lines.append(
                f"| `{row.spdb_label}` | {row.external_label} | **{row.match}** | {row.rationale} |"
            )
        covered = spdb_labels_covered(dataset.dataset_id)
        lines.extend(
            [
                "",
                f"**SPDB labels with at least one mapping row:** {len(covered)}/{len(SPDB_FAL_LABELS)}.",
                "",
            ]
        )
    lines.extend(
        [
            "## Match legend",
            "",
            "- **exact:** definitions and annotation intent align closely.",
            "- **partial:** substantial overlap with SPDB boundary conditions.",
            "- **approximate:** related construct; projection requires adjudication rules.",
            "- **none:** no meaningful mapping without ontology revision.",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def write_mapping_report(output_path: Path | None = None) -> Path:
    path = output_path or DEFAULT_REPORT_DIR / "fallacy_mapping.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_mapping_markdown(), encoding="utf-8")
    return path


def validate_mapping_coverage(required_datasets: Sequence[str] | None = None) -> Dict[str, List[str]]:
    """Return SPDB labels missing from each required dataset mapping."""
    required = required_datasets or ("fallacyes_political", "fallacyes", "semeval2020_propaganda")
    missing: Dict[str, List[str]] = {}
    for dataset_id in required:
        covered = set(spdb_labels_covered(dataset_id))
        absent = [label for label in SPDB_FAL_LABELS if label not in covered]
        if absent:
            missing[dataset_id] = absent
    return missing
