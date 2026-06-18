---
language:
  - es
license: cc-by-4.0
task_categories:
  - text-classification
  - multi-label-classification
tags:
  - political-discourse
  - pragmatics
  - argumentation
  - fallacies
  - spanish
  - computational-social-science
pretty_name: Spanish Political Discourse Benchmark (SPDB)
size_categories:
  - 5K<n<10K
dataset_info:
  features:
    - name: instance_id
      dtype: string
    - name: text
      dtype: string
    - name: source_type
      dtype: string
    - name: pragmatic_function
      dtype: string
    - name: fallacy_labels
      sequence: string
  splits:
    - name: train
      num_bytes: 0
      num_examples: 5600
    - name: dev
      num_bytes: 0
      num_examples: 1200
    - name: test
      num_bytes: 0
      num_examples: 1200
  download_size: 0
  dataset_size: 0
configs:
  - config_name: default
    data_files:
      - split: train
        path: spdb_v1_train.jsonl
      - split: validation
        path: spdb_v1_dev.jsonl
      - split: test
        path: spdb_v1_test.jsonl
---

# Dataset Card for Spanish Political Discourse Benchmark (SPDB)

> **Release status:** `v0.1.0-dev` — schemas, tooling, and documentation are public; **annotated v1 splits are not yet released**. Counts below describe the **v1 target specification**. Development samples (e.g. ParlaMint-derived units) are for pipeline QA only and are not the benchmark release.

## Dataset Summary

The **Spanish Political Discourse Benchmark (SPDB)** is a stratified corpus of Spanish political discourse designed for computational social science and NLP. Each instance is a **discourse unit**: a contiguous text span annotated for:

- **Pragmatic function** (single label, primary supervision)
- **Political fallacies** (multi-label, max three labels, or explicit none)
- **Experimental labels** (optional subset): semantic vacuity and conceptual anachronism

SPDB combines three registers: **parliamentary speech** (~60% of annotated units), **party manifestos** (~12%), and **elite social media** (~28%, identifiers-only public path where platform terms restrict text redistribution).

Canonical specification: [`docs/dataset_documentation/v1_build_specification.md`](../docs/dataset_documentation/v1_build_specification.md).

| Component | v1 target | Minimum viable |
|-----------|-----------|----------------|
| Annotated units (core labels) | 8,000 | 5,000 |
| Double-annotated QC subset | 20% (1,600) | 20% (1,000) |
| Experimental-label subset (SV/CA) | 2,000 | 1,000 |
| Distinct source documents | ≥400 | ≥250 |
| Temporal coverage | 2015–2025 | 2018–2024 |

Geographic scope: **Spain** (state and autonomous-community sources where text redistribution is permitted).

## Languages

| Language | Script | Coverage |
|----------|--------|----------|
| Spanish (`es`) | Latin | Primary |

Code-switched segments with **&lt;70% Spanish** are excluded in v1 unless explicitly tagged `mixed` (planned). Label IDs and operational definitions are documented in English; **unit text is Spanish**.

## Source Data

### Source types and target mix

| `source_type` | Target share | v1 units @ 8k | Acquisition notes |
|---------------|-------------:|--------------:|-------------------|
| `parliamentary` | 60% (55–65%) | 4,800 | Congreso de Diputados, Senado, regional parliaments where licensed; ParlaMint-ES used for pipeline development ([`docs/sources/parlamint.md`](../docs/sources/parlamint.md)) |
| `manifesto` | 12% (10–15%) | 960 | Manifesto Project (MARPOR) and cleared programmatic text |
| `social_media` | 28% (20–30%) | 2,240 | Elite accounts; **IDs-only** public release where ToS require it |

### Inclusion criteria (instance level)

- Political speech by elected officials, party organs, or candidates in official capacity
- Units with at least one claim, evaluative statement, or procedural move with a political referent

### Exclusion criteria

- Pure procedural boilerplate without political content (e.g. roll-call only), when identified in QC
- Near-verbatim duplicates (MinHash dedupe, threshold 0.85; keep earliest)
- Segments **&lt;20** or **&gt;2,000** characters after normalization
- Sources without documented redistribution rights for **text** (social media: IDs-only path)

### Segmentation

- **Unit:** one dominant pragmatic function per span (see §2.1 of v1 build spec)
- **Token cap:** 400 tokens (BETO: `dccuchile/bert-base-spanish-wwm-cased`)
- **Non-overlapping** units; adjacent units do not share sentences
- Tooling: [`scripts/segmentation/`](../scripts/segmentation/)

Raw files are **not** bundled in Git; provenance fields include `license_ref`, `document_id`, and pipeline version stamps.

## Annotation Process

### Label ontologies

Machine-readable definitions: [`labels/`](../labels/).

| Task | Cardinality | Label IDs |
|------|-------------|-----------|
| Pragmatic function | Single-label | `PF_ADVOCACY`, `PF_ATTACK`, `PF_DEFENSE`, `PF_PROPOSAL`, `PF_APPEAL`, `PF_INFO`, `PF_DEFLECT`, `PF_PROCEDURAL` |
| Political fallacies | Multi-label (≤3) or none | `FAL_ADHOM`, `FAL_STRAW`, `FAL_DILEMMA`, `FAL_SLOPE`, `FAL_EMOTION`, `FAL_GENERAL`, `FAL_WHATABOUT`; `FAL_NONE` → empty list + `fallacy_none_explicit=true` |
| Semantic vacuity (experimental) | Single-label | `SV_0`, `SV_1`, `SV_UNCLEAR` |
| Conceptual anachronism (experimental) | Single-label | `CA_0`, `CA_1`, `CA_UNCLEAR` |

Worked examples: [`annotation/guidelines/pragmatic_function_examples.md`](../annotation/guidelines/pragmatic_function_examples.md).

### Workflow

1. **Primary annotation** via Label Studio ([`annotation/labelstudio/`](../annotation/labelstudio/)); guidelines versioned independently of model checkpoints.
2. **Double coding** on 20% QC subset; Cohen's κ / Krippendorff's α reported on dev (pilot thresholds in [`annotation/pilot_001/pilot_metrics.md`](../annotation/pilot_001/pilot_metrics.md)).
3. **Adjudication** for pragmatic-function disagreement and borderline fallacy cases (target turnaround 72 h).
4. **Gold labels** on adjudicated units; adjudication log stores IDs and label deltas only (`adjudication_log.jsonl`).

### Quality rules (summary)

- Pragmatic function and fallacy labels are **independent** (e.g. evidence-based `PF_ATTACK` without `FAL_ADHOM`).
- Fallacies labelled only if present **in the span**; ±1 adjacent unit from same `document_id` allowed for context.
- `borderline=true` on pragmatic function expected ≤5% of submissions.
- Test split labels **locked** after Week 10; no guideline iteration using test labels.

### Annotators

Trained annotators under PI supervision; annotator IDs pseudonymized in exports. See [`docs/ethics.md`](../docs/ethics.md).

## Biases

SPDB reflects **public elite political communication in Spain** and inherits biases from:

- **Source selection:** Over-representation of plenary and programmatic text relative to informal citizen discourse; social-media slice limited to elite accounts.
- **Party and institution coverage:** Stratification targets major `party_family` buckets but regional and minor parties may remain under-represented.
- **Temporal bins:** Planned bins (`2015–2017`, `2018–2020`, `2021–2023`, `2024–2025`) may not evenly cover all political events.
- **Annotation perspective:** Labels encode operational definitions in a reduced ontology; they are not neutral philosophical adjudications of fallacies.
- **Chair / procedural speech:** Parliamentary corpora include Presidencia and ritual units (`PF_PROCEDURAL`); models may overfit procedural formulae if not stratified.
- **Gender and identity:** Speaker metadata depends on source registries; historical records may under-document non-binary identities.

Users should not treat SPDB as a census of all Spanish political talk or as a tool for targeting individuals.

## Limitations

- **Not yet released:** Public `train` / `dev` / `test` JSONL and Zenodo DOI are **planned** for v1.0.0; current repository provides schemas and pipelines only.
- **Partial automation:** Segmentation uses heuristics (paragraph/sentence splits); error rate &gt;10% on QC sample triggers pipeline revision (kill criterion in build spec).
- **Social-media text:** Public release may contain **post IDs and metadata only**; researchers must rehydrate text under platform terms locally.
- **Experimental labels:** Semantic vacuity and conceptual anachronism are **not required** for leaderboard v1.
- **Cross-lingual use:** Labels are tuned to Spanish institutional genres; direct transfer to other languages requires re-validation.
- **LLM baselines:** Parsing failures &gt;5% on dev may exclude LLM systems from the official leaderboard (exploratory only).

## Licensing

| Component | Planned license | Status |
|-----------|-----------------|--------|
| SPDB annotations (project work) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Planned at v1.0.0 |
| Repository code | Apache 2.0 or MIT | **TBD** — see [`LICENSE`](../LICENSE) |
| Source text | Per-record `license_ref` | Documented per upstream corpus |
| Social-media text (public set) | Not redistributed | IDs + rehydration instructions |

Upstream examples used in development:

- **ParlaMint-ES:** licence **to be verified** before any redistribution of derived text ([`docs/sources/parlamint.md`](../docs/sources/parlamint.md)).
- **MARPOR / manifestos:** Manifesto Project terms apply per document.

Full matrix: [`docs/dataset_documentation/licensing_and_ethics.md`](../docs/dataset_documentation/licensing_and_ethics.md).

## Citation

SPDB is under active development. Use the provisional citation below until v1.0.0 and a Zenodo DOI are published.

```bibtex
@misc{spdb2026,
  title        = {Spanish Political Discourse Benchmark (SPDB)},
  author       = {Baena Rojas, Jose Jaime and Pinto Pajares, Daniel and Andr{\'e}s, C{\'e}sar},
  year         = {2026},
  note         = {Under development; v0.1.0-dev. Dataset not yet released.},
  publisher    = {Universidad Internacional de La Rioja (UNIR)},
  howpublished = {GitHub/Zenodo repository},
  url          = {https://github.com/PLACEHOLDER/spanish_political_discourse_benchmark}
}
```

Machine-readable: [`CITATION.cff`](../CITATION.cff).

When using upstream corpora (e.g. ParlaMint, MARPOR), cite the original sources in addition to SPDB.

## Leaderboard

### Status

The official v1 leaderboard is **planned** for release with locked test labels. File: `results/metrics/baseline_leaderboard_v1.csv` (versioned in Git when populated).

Hidden-test evaluation on the **locked test split** (15%, ~1,200 units) with document- and account-level grouping to prevent leakage.

### Tasks and metrics (v1)

| Task | Primary metric | Secondary metrics |
|------|----------------|-------------------|
| Pragmatic function (`PF_*`) | **Macro-F1** | Accuracy, per-class F1 |
| Political fallacies (`FAL_*`) | **Macro-F1** (label-wise) | Micro-F1, sample-wise F1 |
| Combined (official ranking) | **Macro average** of PF macro-F1 and fallacy macro-F1 | — |

Experimental SV/CA labels are reported separately and **do not** affect the official v1 ranking.

### Baseline tiers (planned)

1. Majority / prior  
2. Rule-based (`code/src/discourse_classifier/`)  
3. Classical ML (TF-IDF + linear models)  
4. Transformer (BETO primary; optional RoBERTa-BNE)  
5. Open LLM (pinned checkpoint, fixed prompts; excluded if parse failure &gt;5% on dev)

Proprietary API models may appear as **non-reproducible** comparison rows only.

### Submission rules (planned)

- Predictions must cover the same label inventory as [`labels/`](../labels/).
- Submit dev-tuned models evaluated **once** on locked test; report seeds and config JSON.
- IberLEF-compatible export (`label_pf` column, `label_inventory.tsv`) documented for future shared tasks — optional in v1, required before hosting a shared task (build spec §12.5).

### Current results

| Model | PF macro-F1 | Fallacy macro-F1 | Combined | Status |
|-------|------------:|-----------------:|---------:|--------|
| — | — | — | — | **Not yet available** |

---

## Additional links

| Resource | Path |
|----------|------|
| JSON Schema | [`schemas/discourse_unit.schema.json`](../schemas/discourse_unit.schema.json) |
| Datasheet | [`docs/dataset_documentation/datasheet.md`](../docs/dataset_documentation/datasheet.md) |
| Reproducibility | [`docs/reproducibility.md`](../docs/reproducibility.md) |
| Changelog | [`docs/changelog.md`](../docs/changelog.md) |

**Contact:** [josejaime.baena@unir.net](mailto:josejaime.baena@unir.net) · [daniel.pinto@unir.net](mailto:daniel.pinto@unir.net)
