# Datasheet for Datasets: SPDB v1.0.0 — Spanish Political Discourse Annotation Resource

**Version:** `1.0.0`  
**Release status:** `v0.1.0-alpha (alpha)`  
**Generated:** 2026-09-29 (UTC)  
**Template:** [Gebru, T., Morgado, J., Cascella, C., Li, Y., Rao, J., & Denton, E. (2021). Datasheets for datasets. *Communications of the ACM*, 64(12), 86–92. https://doi.org/10.1145/3458723](https://doi.org/10.1145/3458723)

> Auto-generated from repository metadata (`CITATION.cff`, label inventories, release manifest, build specification). Sections marked **TODO** require manual completion before v1.0.0.

## 1. Motivation

### For what purpose was the dataset created?

SPDB is a reproducible annotation resource for pragmatic-function coding in Spanish parliamentary discourse. Version 1.0.0 provides schemas, guidelines, ParlaMint-derived sampling, and a completed two-annotator Wave-1 reliability pilot (N=100; observed agreement 0.350; Cohen kappa ~0.235; Krippendorff alpha ~0.223; Fleiss kappa ~0.219; 65 disagreements). Revised codebook-v1.1.0 remains unvalidated. This release is not an adjudicated gold benchmark.

The benchmark additionally targets cross-register evaluation (parliament, manifestos, elite social media) and reproducible baselines for rule-based, classical ML, transformer, and LLM systems.

### Who created the dataset and on behalf of which entity?

| Name | Affiliation | ORCID |
|------|-------------|-------|
| José Jaime Baena Rojas | Universidad Internacional de La Rioja (UNIR), Spain | [https://orcid.org/0000-0002-0915-4087](https://orcid.org/0000-0002-0915-4087) |
| Daniel Pinto Pajares | Universidad Internacional de La Rioja (UNIR), Spain | [https://orcid.org/0000-0001-9397-811X](https://orcid.org/0000-0001-9397-811X) |
| César Andrés | Universidad Internacional de La Rioja (UNIR), Spain | [https://orcid.org/0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404) |
| César Andrés | **TODO:** affiliation missing | **TODO:** ORCID missing |

### Who funded the creation of the dataset?

**TODO:** Add grant identifiers and funding bodies before v1.0.0 release

### Any other comments?

First public alpha: schemas, annotation guidelines, pipeline documentation, and an unannotated 100-unit ParlaMint pilot sample. Not a benchmark gold release.

## 2. Composition

### What do the instances that comprise the dataset represent?

Each instance is a **discourse unit**: a contiguous Spanish text span that an informed reader would treat as carrying one dominant pragmatic function toward a political target (actor, policy, institution, or electorate).

### How many instances are there in total (in each distribution)?

**Planned annotated release (v1 target):** 8,000 core units (5,600 train / 1,200 dev / 1,200 test). MVP floor: 5,000.

**Current public release:** annotated splits are **not yet distributed**. Development snapshot:

- 878 unlabeled parliamentary units in `data/processed/parlamint_units.jsonl` (development pool)
- 100 unlabeled units in `data/processed/parlamint_100_units.jsonl` (pilot sample)

### Does the dataset contain all possible instances or is it a sample (not necessarily random) from a larger set?

SPDB is a **stratified sample** from larger parliamentary, manifesto, and social-media corpora. Sampling targets balance across `source_type`, `party_family`, and temporal bins after deduplication (MinHash ≥0.85). See `docs/dataset_documentation/v1_build_specification.md`.

### What data does each instance consist of?

Raw or normalized text (where redistribution permitted), stable `unit_id`, `document_id`, character offsets, token counts, metadata (`source_type`, speaker fields, date, party), and gold labels when annotated. Schema: `schemas/discourse_unit.schema.json`.

### Is there a label or target associated with each instance?

- **Pragmatic function (single-label):** `PF_ADVOCACY`, `PF_ATTACK`, `PF_DEFENSE`, `PF_PROPOSAL`, `PF_APPEAL`, `PF_INFO`, `PF_DEFLECT`, `PF_PROCEDURAL`
- **Political fallacies (multi-label, ≤3):** `FAL_ADHOM`, `FAL_STRAW`, `FAL_DILEMMA`, `FAL_SLOPE`, `FAL_EMOTION`, `FAL_GENERAL`, `FAL_WHATABOUT`; `FAL_NONE` when none apply
- **Experimental (subset):** `SV_*`, `CA_*`

### Is any information missing from individual instances?

Yes, by design in some slices:

- Social-media public exports may omit `text` (IDs + rehydration metadata only).
- Experimental labels (`SV_*`, `CA_*`) apply to a subset only.
- Upstream `license_ref` may be `to_be_verified` during development (ParlaMint-ES).

### Are relationships between individual instances made explicit?

Yes. Instances link to `document_id`, source document metadata, and (for social media) account-level IDs. Recommended splits enforce document-level and account-level grouping.

### Are there recommended data splits (e.g., training, development/validation, testing)?

Yes — planned v1 split: train 70% (5,600), dev 15% (1,200), test 15% (1,200) with stratification constraints. Test IDs will be locked in `test_manifest.sha256`.

### Are there any errors, sources of noise, or redundancies in the data?

Potential sources include: segmentation boundary errors, OCR/PDF extraction noise in manifestos, deleted or edited social posts, near-duplicate speeches, and procedural boilerplate. Near-verbatim duplicates are deduplicated; segmentation QC targets <10% error before annotation wave 2.

### Is the dataset self-contained, or does it link to or otherwise rely on external resources?

Partially self-contained. Annotations and metadata are bundled; **upstream raw files are not**. Social text may require local rehydration under platform terms.

### Does the dataset contain data that might be considered confidential?

No private citizen communications are targeted. Content is **public political speech**; social slice may ship IDs-only where redistribution is restricted.

### Does the dataset contain data that, if viewed directly, might be offensive, insulting, threatening, or might otherwise cause anxiety?

Yes. Political attacks and inflammatory rhetoric may appear, especially in `PF_ATTACK` units and populist mobilization text. Users should handle content appropriately; annotator welfare guidelines exist.

## 3. Collection Process

### How was the data associated with each instance acquired?

Through documented ingestion pipelines:

- `scripts/ingestion/ingest_parlamint.py` / parliamentary sources
- `scripts/ingestion/ingest_manifestos.py` (MARPOR and programmatic text)
- `scripts/ingestion/ingest_social_ids.py` (elite social post IDs)

See `docs/dataset_documentation/v1_build_specification.md` §1–§2.

### What mechanisms or procedures were used to collect the data?

Batch ingestion from licensed corpora and APIs/feeds where permitted; segmentation via `scripts/segmentation/segment_discourse_units.py`; validation via `scripts/validation/validate_dataset.py`.

### If the dataset is a sample from a larger set, what was the sampling strategy?

Stratified sampling over register × party family × temporal bin after deduplication. Register target mix @ 8k: Parliament 60%, Party manifestos 12%, Elite social media 28%.

### Who was involved in the data collection process and how were they compensated?

**TODO:** Document data engineering roles and compensation for collection phase

### Over what timeframe was the data collected?

Planned coverage: **2015–2025** (MVP floor 2018–2024). Development parliamentary pool draws on ParlaMint-ES sessions documented in `docs/sources/parlamint.md`.

### Were any ethical review processes conducted?

**TODO:** Document IRB/ethics review status before annotation wave 2 (see docs/ethics.md)

### Does the dataset relate to people?

Yes. Instances reference **public figures** (elected officials, party organs, candidates). Speaker names and handles may appear where source licenses permit.

## 4. Preprocessing / Cleaning / Labeling

### Was any preprocessing/cleaning/labeling of the data done?

Yes.

- Unicode NFC normalization
- URL → `<URL>`, @mention → `<USER>` masking
- Paragraph/sentence-aware segmentation; 400 BETO token cap; 20–2,000 character bounds
- Expert annotation for pragmatic function and fallacies under versioned guidelines

### Was the "raw" data saved in addition to the preprocessed/cleaned/labeled data?

Yes. `text_raw` and `text_norm` fields are specified; intermediate JSONL is retained in the pipeline. Raw upstream corpora are stored outside Git (`data/raw/`).

### Is the software used to preprocess/clean/label the data available?

Yes — open-source tooling in this repository (`scripts/`) and documentation in `docs/pipeline.md`. GitHub: [https://github.com/cesar-andress/spanish_political_discourse_benchmark](https://github.com/cesar-andress/spanish_political_discourse_benchmark)

### How was the data labeled (e.g., tool used, number of human labelers)?

Label Studio exports (`annotation/labelstudio/`) with guidelines in `annotation/codebook/SPDB_Codebook_v1.md`. Target: trained annotators under PI/adjudicator supervision; 20% double-coded QC subset.

### What labeling protocol was used?

Versioned annotation protocol (`annotation/pilot_001/pilot_protocol.md`, `protocol/annotation/`) with adjudication for pragmatic-function disagreement, fallacy borderline review, and locked test labels after Week 10.

### What is the annotator demographic (e.g., age, gender) and background?

**TODO:** Collect and document annotator demographic summary at release while preserving pseudonymization

## 5. Uses

### Has the dataset been used for any tasks already?

Development-only uses: pipeline QA, ontology validation frameworks, LLM annotation pilots, and internal reliability simulations. **No published benchmark results on locked test data yet.**

### Is there a repository that links to any or all papers or systems that use the dataset?

**TODO:** Create publications/systems index when first external papers cite SPDB

### What (other) tasks could the dataset be used for?

Pragmatic function classification, fallacy detection, inter-annotator agreement research, cross-register domain adaptation, computational social science on elite discourse, and IberLEF-style shared tasks.

### Are there tasks for which the dataset should not be used?

Yes. Do **not** use SPDB for individual targeting, voter manipulation, surveillance of private citizens, or automated harassment. See `docs/ethics.md`.

## 6. Distribution

### Will the dataset be distributed to third parties outside of the entity on behalf of which the dataset was created?

Yes — public release planned via Zenodo and GitHub.

### How will the dataset be distributed?

Zenodo archive ([https://doi.org/10.5281/zenodo.23039355](https://doi.org/10.5281/zenodo.23039355)) plus GitHub repository. Planned files: `spdb_v1_train/dev/test.jsonl` and companion CSV exports.

### When will the dataset be distributed?

Alpha tooling release (`spdb-v0.1.0`) is available. **Annotated v1.0.0 splits:** **TODO:** Target v1.0.0 release date not finalized

### Will the dataset be distributed under a copyright or other intellectual property (IP) license, and/or under applicable terms of use (ToU)?

Project annotations and guidelines: **CC-BY-4.0** (see CITATION.cff). Upstream source text remains under per-record `license_ref` terms.

### Have any third parties imposed IP-based or other restrictions on the data associated with the instances?

Yes. ParlaMint-ES, MARPOR/manifesto sources, and social-platform ToS may restrict text redistribution. Social slice may be IDs-only in public files.

### Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?

**TODO:** Confirm export-control review for international redistribution if applicable

## 7. Maintenance

### Who will be supporting/hosting/maintaining the dataset?

Author team at Universidad Internacional de La Rioja (UNIR); long-term hosting on Zenodo with GitHub for code/docs.

### How can the owner/curator/manager of the dataset be contacted (e.g., email address)?

[josejaime.baena@unir.net](mailto:josejaime.baena@unir.net) · [daniel.pinto@unir.net](mailto:daniel.pinto@unir.net)

### Is there an erratum?

**TODO:** Publish erratum page when first post-release corrections are issued

### Will the dataset be updated (e.g., to correct labeling errors, add new instances, delete instances)?

Yes. Versioned releases with changelog; concept DOI on Zenodo for major versions.

### If the dataset relates to people, are there applicable limits on the retention of the data contained in the dataset?

**TODO:** Document retention policy for pseudonymized annotator logs and rehydrated social text

### Will older versions of the dataset continue to be supported/hosted/maintained?

Yes. Prior Zenodo versions remain accessible; breaking schema changes increment major version.

### If others want to extend/augment/build on/contribute to the dataset, is there a mechanism for them to do so?

Contributions via GitHub pull requests ([`CONTRIBUTING.md`](CONTRIBUTING.md)) and documented issue templates. Annotation changes require codebook and schema updates.

## Pending sections summary

The following Gebru et al. questions still require manual input:

- Who funded the creation of the dataset?
- Who was involved in the data collection process and how were they compensated?
- Were any ethical review processes conducted?
- What is the annotator demographic (e.g., age, gender) and background?
- Is there a repository that links to any or all papers or systems that use the dataset?
- Do any export controls or other regulatory restrictions apply to the dataset or to individual instances?
- Is there an erratum?
- If the dataset relates to people, are there applicable limits on the retention of the data contained in the dataset?

## Document provenance

- Generator: `scripts/release/generate_datasheet.py`
- Citation metadata: `CITATION.cff`
- Related: [`dataset_card.md`](../dataset_card.md), [`docs/ethics.md`](ethics.md)
