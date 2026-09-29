"""Generate a Gebru et al. (2021) Datasheet for Datasets for SPDB."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Sequence

from scripts.release.dataset_card_constants import (
    CONTACT_EMAILS,
    DEV_UNITS,
    DOI_URL,
    GITHUB_REPO,
    LABELS_FAL,
    LABELS_PF,
    SOURCE_MIX,
    TEST_UNITS,
    TRAIN_UNITS,
    V1_MVP_UNITS,
    V1_TARGET_UNITS,
)
from scripts.release.metadata_loader import (
    CitationMetadata,
    count_jsonl_lines,
    load_citation_metadata,
    load_label_ids,
    populated,
    release_status,
    todo,
)

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = ROOT / "docs/datasheet_for_datasets.md"
PARLAMINT_POOL = ROOT / "data/processed/parlamint_units.jsonl"
PARLAMINT_SAMPLE = ROOT / "data/processed/parlamint_100_units.jsonl"
GEBRU_REFERENCE = "Gebru, T., Morgado, J., Cascella, C., Li, Y., Rao, J., & Denton, E. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723"


@dataclass
class DatasheetBuilder:
    lines: List[str] = field(default_factory=list)
    pending: List[str] = field(default_factory=list)

    def q(self, question: str, answer: str, *, track_todo: bool = True) -> None:
        self.lines.extend([f"### {question}", "", answer, ""])
        if track_todo and answer.strip().startswith("**TODO:**"):
            self.pending.append(question)

    def section(self, title: str) -> None:
        self.lines.extend([f"## {title}", ""])


def _author_table(citation: CitationMetadata) -> str:
    if not citation.authors:
        return todo("Add authors to CITATION.cff")
    rows = [
        "| Name | Affiliation | ORCID |",
        "|------|-------------|-------|",
    ]
    for author in citation.authors:
        name = f"{author.given_names} {author.family_names}"
        orcid = f"[{author.orcid}]({author.orcid})" if author.orcid else todo("ORCID missing")
        rows.append(f"| {name} | {author.affiliation or todo('affiliation missing')} | {orcid} |")
    return "\n".join(rows)


def _label_summary(pf_labels: Sequence[str], fal_labels: Sequence[str]) -> str:
    fal_core = [label for label in fal_labels if label != "FAL_NONE"]
    pf = ", ".join(f"`{label}`" for label in pf_labels)
    fal = ", ".join(f"`{label}`" for label in fal_core)
    return (
        f"- **Pragmatic function (single-label):** {pf}\n"
        f"- **Political fallacies (multi-label, ≤3):** {fal}; `FAL_NONE` when none apply\n"
        f"- **Experimental (subset):** `SV_*`, `CA_*`"
    )


def _development_counts() -> str:
    pool = count_jsonl_lines(PARLAMINT_POOL)
    sample = count_jsonl_lines(PARLAMINT_SAMPLE)
    parts = []
    if pool is not None:
        parts.append(f"{pool:,} unlabeled parliamentary units in `data/processed/parlamint_units.jsonl` (development pool)")
    if sample is not None:
        parts.append(f"{sample:,} unlabeled units in `data/processed/parlamint_100_units.jsonl` (pilot sample)")
    if not parts:
        return todo("No processed JSONL counts available in the local workspace")
    return "- " + "\n- ".join(parts)


def render_datasheet(
    *,
    citation: CitationMetadata,
    pf_labels: Sequence[str],
    fal_labels: Sequence[str],
) -> tuple[str, List[str]]:
    release_name, release_note, published = release_status()
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    builder = DatasheetBuilder()

    builder.lines.extend(
        [
            f"# Datasheet for Datasets: {citation.title}",
            "",
            f"**Version:** `{citation.version}`  ",
            f"**Release status:** `{release_name}`  ",
            f"**Generated:** {generated} (UTC)  ",
            f"**Template:** [{GEBRU_REFERENCE}](https://doi.org/10.1145/3458723)",
            "",
            "> Auto-generated from repository metadata (`CITATION.cff`, label inventories, release manifest, build specification). "
            "Sections marked **TODO** require manual completion before v1.0.0.",
            "",
        ]
    )

    builder.section("1. Motivation")
    builder.q(
        "For what purpose was the dataset created?",
        populated(
            citation.abstract,
            hint="Add abstract to CITATION.cff",
        )
        + "\n\nThe benchmark additionally targets cross-register evaluation (parliament, manifestos, elite social media) "
        "and reproducible baselines for rule-based, classical ML, transformer, and LLM systems.",
    )
    builder.q(
        "Who created the dataset and on behalf of which entity?",
        _author_table(citation),
        track_todo=False,
    )
    builder.q(
        "Who funded the creation of the dataset?",
        todo("Add grant identifiers and funding bodies before v1.0.0 release"),
    )
    builder.q(
        "Any other comments?",
        release_note or todo("Add release notes to releases/v0.1.0-alpha/MANIFEST.json"),
    )

    builder.section("2. Composition")
    builder.q(
        "What do the instances that comprise the dataset represent?",
        "Each instance is a **discourse unit**: a contiguous Spanish text span that an informed reader "
        "would treat as carrying one dominant pragmatic function toward a political target (actor, policy, institution, or electorate).",
    )
    builder.q(
        "How many instances are there in total (in each distribution)?",
        f"**Planned annotated release (v1 target):** {V1_TARGET_UNITS:,} core units "
        f"({TRAIN_UNITS:,} train / {DEV_UNITS:,} dev / {TEST_UNITS:,} test). "
        f"MVP floor: {V1_MVP_UNITS:,}.\n\n"
        f"**Current public release:** annotated splits are **not yet distributed**. Development snapshot:\n\n"
        f"{_development_counts()}",
        track_todo=not (PARLAMINT_POOL.exists() or PARLAMINT_SAMPLE.exists()),
    )
    builder.q(
        "Does the dataset contain all possible instances or is it a sample (not necessarily random) "
        "from a larger set?",
        "SPDB is a **stratified sample** from larger parliamentary, manifesto, and social-media corpora. "
        "Sampling targets balance across `source_type`, `party_family`, and temporal bins after deduplication "
        "(MinHash ≥0.85). See `docs/dataset_documentation/v1_build_specification.md`.",
    )
    builder.q(
        "What data does each instance consist of?",
        "Raw or normalized text (where redistribution permitted), stable `unit_id`, `document_id`, "
        "character offsets, token counts, metadata (`source_type`, speaker fields, date, party), "
        "and gold labels when annotated. Schema: `schemas/discourse_unit.schema.json`.",
    )
    builder.q(
        "Is there a label or target associated with each instance?",
        _label_summary(pf_labels, fal_labels),
    )
    builder.q(
        "Is any information missing from individual instances?",
        "Yes, by design in some slices:\n\n"
        "- Social-media public exports may omit `text` (IDs + rehydration metadata only).\n"
        "- Experimental labels (`SV_*`, `CA_*`) apply to a subset only.\n"
        "- Upstream `license_ref` may be `to_be_verified` during development (ParlaMint-ES).",
    )
    builder.q(
        "Are relationships between individual instances made explicit?",
        "Yes. Instances link to `document_id`, source document metadata, and (for social media) account-level IDs. "
        "Recommended splits enforce document-level and account-level grouping.",
    )
    builder.q(
        "Are there recommended data splits (e.g., training, development/validation, testing)?",
        f"Yes — planned v1 split: train 70% ({TRAIN_UNITS:,}), dev 15% ({DEV_UNITS:,}), "
        f"test 15% ({TEST_UNITS:,}) with stratification constraints. "
        "Test IDs will be locked in `test_manifest.sha256`.",
    )
    builder.q(
        "Are there any errors, sources of noise, or redundancies in the data?",
        "Potential sources include: segmentation boundary errors, OCR/PDF extraction noise in manifestos, "
        "deleted or edited social posts, near-duplicate speeches, and procedural boilerplate. "
        "Near-verbatim duplicates are deduplicated; segmentation QC targets <10% error before annotation wave 2.",
    )
    builder.q(
        "Is the dataset self-contained, or does it link to or otherwise rely on external resources?",
        "Partially self-contained. Annotations and metadata are bundled; **upstream raw files are not**. "
        "Social text may require local rehydration under platform terms.",
    )
    builder.q(
        "Does the dataset contain data that might be considered confidential?",
        "No private citizen communications are targeted. Content is **public political speech**; "
        "social slice may ship IDs-only where redistribution is restricted.",
    )
    builder.q(
        "Does the dataset contain data that, if viewed directly, might be offensive, insulting, "
        "threatening, or might otherwise cause anxiety?",
        "Yes. Political attacks and inflammatory rhetoric may appear, especially in `PF_ATTACK` units and "
        "populist mobilization text. Users should handle content appropriately; annotator welfare guidelines exist.",
    )

    builder.section("3. Collection Process")
    builder.q(
        "How was the data associated with each instance acquired?",
        "Through documented ingestion pipelines:\n\n"
        "- `scripts/ingestion/ingest_parlamint.py` / parliamentary sources\n"
        "- `scripts/ingestion/ingest_manifestos.py` (MARPOR and programmatic text)\n"
        "- `scripts/ingestion/ingest_social_ids.py` (elite social post IDs)\n\n"
        "See `docs/dataset_documentation/v1_build_specification.md` §1–§2.",
    )
    builder.q(
        "What mechanisms or procedures were used to collect the data?",
        "Batch ingestion from licensed corpora and APIs/feeds where permitted; segmentation via "
        "`scripts/segmentation/segment_discourse_units.py`; validation via `scripts/validation/validate_dataset.py`.",
    )
    builder.q(
        "If the dataset is a sample from a larger set, what was the sampling strategy?",
        "Stratified sampling over register × party family × temporal bin after deduplication. "
        "Register target mix @ 8k: "
        + ", ".join(f"{label} {share}" for _, label, share, _ in SOURCE_MIX)
        + ".",
    )
    builder.q(
        "Who was involved in the data collection process and how were they compensated?",
        todo("Document data engineering roles and compensation for collection phase"),
    )
    builder.q(
        "Over what timeframe was the data collected?",
        "Planned coverage: **2015–2025** (MVP floor 2018–2024). Development parliamentary pool draws on ParlaMint-ES sessions documented in `docs/sources/parlamint.md`.",
    )
    builder.q(
        "Were any ethical review processes conducted?",
        todo("Document IRB/ethics review status before annotation wave 2 (see docs/ethics.md)"),
    )
    builder.q(
        "Does the dataset relate to people?",
        "Yes. Instances reference **public figures** (elected officials, party organs, candidates). "
        "Speaker names and handles may appear where source licenses permit.",
    )

    builder.section("4. Preprocessing / Cleaning / Labeling")
    builder.q(
        "Was any preprocessing/cleaning/labeling of the data done?",
        "Yes.\n\n"
        "- Unicode NFC normalization\n"
        "- URL → `<URL>`, @mention → `<USER>` masking\n"
        "- Paragraph/sentence-aware segmentation; 400 BETO token cap; 20–2,000 character bounds\n"
        "- Expert annotation for pragmatic function and fallacies under versioned guidelines",
    )
    builder.q(
        'Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?',
        "Yes. `text_raw` and `text_norm` fields are specified; intermediate JSONL is retained in the pipeline. "
        "Raw upstream corpora are stored outside Git (`data/raw/`).",
    )
    builder.q(
        "Is the software used to preprocess/clean/label the data available?",
        f"Yes — open-source tooling in this repository (`scripts/`) and documentation in `docs/pipeline.md`. "
        f"GitHub: [{GITHUB_REPO}]({GITHUB_REPO})",
    )
    builder.q(
        "How was the data labeled (e.g., tool used, number of human labelers)?",
        "Label Studio exports (`annotation/labelstudio/`) with guidelines in `annotation/codebook/SPDB_Codebook_v1.md`. "
        "Target: trained annotators under PI/adjudicator supervision; 20% double-coded QC subset.",
    )
    builder.q(
        "What labeling protocol was used?",
        "Versioned annotation protocol (`annotation/pilot_001/pilot_protocol.md`, `protocol/annotation/`) with "
        "adjudication for pragmatic-function disagreement, fallacy borderline review, and locked test labels after Week 10.",
    )
    builder.q(
        "What is the annotator demographic (e.g., age, gender) and background?",
        todo("Collect and document annotator demographic summary at release while preserving pseudonymization"),
    )

    builder.section("5. Uses")
    builder.q(
        "Has the dataset been used for any tasks already?",
        "Development-only uses: pipeline QA, ontology validation frameworks, LLM annotation pilots, and internal "
        "reliability simulations. **No published benchmark results on locked test data yet.**",
    )
    builder.q(
        "Is there a repository that links to any or all papers or systems that use the dataset?",
        todo("Create publications/systems index when first external papers cite SPDB"),
    )
    builder.q(
        "What (other) tasks could the dataset be used for?",
        "Pragmatic function classification, fallacy detection, inter-annotator agreement research, "
        "cross-register domain adaptation, computational social science on elite discourse, and IberLEF-style shared tasks.",
    )
    builder.q(
        "Are there tasks for which the dataset should not be used?",
        "Yes. Do **not** use SPDB for individual targeting, voter manipulation, surveillance of private citizens, "
        "or automated harassment. See `docs/ethics.md`.",
    )

    builder.section("6. Distribution")
    builder.q(
        "Will the dataset be distributed to third parties outside of the entity on behalf of which "
        "the dataset was created?",
        "Yes — public release planned via Zenodo and GitHub.",
    )
    builder.q(
        "How will the dataset be distributed?",
        f"Zenodo archive ([{DOI_URL}]({DOI_URL})) plus GitHub repository. "
        "Planned files: `spdb_v1_train/dev/test.jsonl` and companion CSV exports.",
    )
    builder.q(
        "When will the dataset be distributed?",
        "Alpha tooling release (`spdb-v0.1.0`) is available. **Annotated v1.0.0 splits:** "
        + ("available" if published else todo("Target v1.0.0 release date not finalized")),
    )
    builder.q(
        "Will the dataset be distributed under a copyright or other intellectual property (IP) license, "
        "and/or under applicable terms of use (ToU)?",
        populated(
            f"Project annotations and guidelines: **{citation.license_id}** (see CITATION.cff). "
            "Upstream source text remains under per-record `license_ref` terms.",
            hint="Add license to CITATION.cff",
        ),
    )
    builder.q(
        "Have any third parties imposed IP-based or other restrictions on the data associated with the instances?",
        "Yes. ParlaMint-ES, MARPOR/manifesto sources, and social-platform ToS may restrict text redistribution. "
        "Social slice may be IDs-only in public files.",
    )
    builder.q(
        "Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?",
        todo("Confirm export-control review for international redistribution if applicable"),
    )

    builder.section("7. Maintenance")
    builder.q(
        "Who will be supporting/hosting/maintaining the dataset?",
        "Author team at Universidad Internacional de La Rioja (UNIR); long-term hosting on Zenodo with GitHub for code/docs.",
    )
    builder.q(
        "How can the owner/curator/manager of the dataset be contacted (e.g., email address)?",
        " · ".join(f"[{email}](mailto:{email})" for email in CONTACT_EMAILS),
    )
    builder.q(
        "Is there an erratum?",
        todo("Publish erratum page when first post-release corrections are issued"),
    )
    builder.q(
        "Will the dataset be updated (e.g., to correct labeling errors, add new instances, delete instances)?",
        "Yes. Versioned releases with changelog; concept DOI on Zenodo for major versions.",
    )
    builder.q(
        "If the dataset relates to people, are there applicable limits on the retention of the data "
        "contained in the dataset?",
        todo("Document retention policy for pseudonymized annotator logs and rehydrated social text"),
    )
    builder.q(
        "Will older versions of the dataset continue to be supported/hosted/maintained?",
        "Yes. Prior Zenodo versions remain accessible; breaking schema changes increment major version.",
    )
    builder.q(
        "If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?",
        f"Contributions via GitHub pull requests ([`CONTRIBUTING.md`](CONTRIBUTING.md)) and documented issue templates. "
        f"Annotation changes require codebook and schema updates.",
    )

    builder.lines.extend(
        [
            "## Pending sections summary",
            "",
        ]
    )
    if builder.pending:
        builder.lines.append("The following Gebru et al. questions still require manual input:")
        builder.lines.append("")
        for item in builder.pending:
            builder.lines.append(f"- {item}")
    else:
        builder.lines.append("_All sections populated from repository metadata._")

    builder.lines.extend(
        [
            "",
            "## Document provenance",
            "",
            f"- Generator: `scripts/release/generate_datasheet.py`",
            f"- Citation metadata: `CITATION.cff`",
            f"- Related: [`dataset_card.md`](../dataset_card.md), [`docs/ethics.md`](ethics.md)",
            "",
        ]
    )
    return "\n".join(builder.lines), builder.pending


def generate_datasheet(*, output_path: Path = DEFAULT_OUTPUT) -> tuple[Path, List[str]]:
    citation = load_citation_metadata()
    pf_labels = load_label_ids(LABELS_PF)
    fal_labels = load_label_ids(LABELS_FAL)
    content, pending = render_datasheet(citation=citation, pf_labels=pf_labels, fal_labels=fal_labels)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path, pending


def main() -> int:
    path, pending = generate_datasheet()
    print(f"Wrote {path}")
    if pending:
        print(f"Pending sections: {len(pending)}")
        for item in pending:
            print(f"  - {item}")
    else:
        print("All sections populated from metadata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
