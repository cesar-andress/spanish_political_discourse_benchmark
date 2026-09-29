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
  - parliament
  - manifesto
  - social-media
pretty_name: Spanish Political Discourse Benchmark (SPDB)
size_categories:
  - 5K<n<10K
dataset_info:
  features:
    - name: unit_id
      dtype: string
    - name: text
      dtype: string
    - name: source_type
      dtype: string
    - name: pragmatic_function
      dtype: string
    - name: fallacy_labels
      sequence: string
    - name: speaker_name
      dtype: string
    - name: speaker_party
      dtype: string
    - name: date
      dtype: string
  splits:
    - name: train
      num_bytes: 0
      num_examples: 5600
    - name: validation
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
# Dataset Card for SPDB v1.0.0 — Spanish Political Discourse Annotation Resource

> **Release status:** `v0.1.0-alpha (alpha)` — First public alpha: schemas, annotation guidelines, pipeline documentation, and an unannotated 100-unit ParlaMint pilot sample. Not a benchmark gold release.

## Motivation

SPDB is a reproducible annotation resource for pragmatic-function coding in Spanish parliamentary discourse. Version 1.0.0 provides schemas, guidelines, ParlaMint-derived sampling, and a completed two-annotator Wave-1 reliability pilot (N=100; observed agreement 0.350; Cohen kappa ~0.235; Krippendorff alpha ~0.223; Fleiss kappa ~0.219; 65 disagreements). Revised codebook-v1.1.0 remains unvalidated. This release is not an adjudicated gold benchmark.

SPDB addresses a gap in Spanish NLP: most political text resources focus on **topic, sentiment, or stance**, but under-specify the **pragmatic function** of a discourse unit (attack, defense, advocacy, procedural ritual, etc.) and its relation to **argumentation phenomena** such as fallacies. The benchmark supports:

- Computational pragmatics and discourse analysis in institutional Spanish
- Inter-annotator agreement studies on a reduced, operational ontology
- Cross-register evaluation (parliament, manifestos, elite social media)
- Baseline and LLM comparisons under fixed label inventories

SPDB is developed at **Universidad Internacional de La Rioja (UNIR)** as an open, versioned resource with Zenodo archiving and HuggingFace-compatible exports.

## Dataset composition

Each instance is a **discourse unit**: a contiguous Spanish text span with metadata and (in v1) gold labels.

| Layer | Cardinality | Label space |
|-------|-------------|-------------|
| Pragmatic function (primary) | Single-label | `PF_ADVOCACY`, `PF_ATTACK`, `PF_DEFENSE`, `PF_PROPOSAL`, `PF_APPEAL`, `PF_INFO`, `PF_DEFLECT`, `PF_PROCEDURAL` |
| Political fallacies | Multi-label (≤3) or explicit none | `FAL_ADHOM`, `FAL_STRAW`, `FAL_DILEMMA`, `FAL_SLOPE`, `FAL_EMOTION`, `FAL_GENERAL`, `FAL_WHATABOUT`; `FAL_NONE` when no fallacy applies |
| Semantic vacuity (experimental) | Single-label | `SV_0`, `SV_1`, `SV_UNCLEAR` |
| Conceptual anachronism (experimental) | Single-label | `CA_0`, `CA_1`, `CA_UNCLEAR` |

### Target scale (v1 specification)

| Component | v1 target | MVP floor |
|-----------|----------:|----------:|
| Annotated units (core labels) | 8,000 | 5,000 |
| Double-annotated QC subset | 20% (1,600) | 20% (1,000) |
| Experimental-label subset | 2,000 | 1,000 |
| Distinct source documents | ≥400 | ≥250 |
| Temporal coverage | 2015–2025 | 2018–2024 |

### Register mix (by annotated unit count @ 8k)

| `source_type` | Register | Target share | Units @ 8k |
|---------------|----------|-------------:|-----------:|
| `parliamentary` | Parliament | 60% | 4,800 |
| `manifesto` | Party manifestos | 12% | 960 |
| `social_media` | Elite social media | 28% | 2,240 |

**Geographic scope:** Spain (state and autonomous-community sources where text redistribution is permitted).  
**Language:** Spanish (`es`); code-switched segments with <70% Spanish are excluded unless tagged `mixed`.

### Current repository snapshot

The public `1.0.0` alpha release ships **schemas, guidelines, pipelines, and an unannotated 100-unit parliamentary pilot sample**. Full annotated splits are planned for v1.0.0.

## Collection process

### Sources

1. **Parliament (`parliamentary`)** — Congreso de Diputados, Senado, and regional parliaments where licensed; ParlaMint-ES supports pipeline development (`docs/sources/parlamint.md`).
2. **Manifestos (`manifesto`)** — Manifesto Project (MARPOR) and programmatic text cleared for redistribution.
3. **Social media (`social_media`)** — Elite accounts (elected officials, party organs, candidates); **IDs-only** public path where platform terms restrict text redistribution.

### Ingestion and segmentation

- Raw documents are ingested via `scripts/ingestion/` into intermediate JSONL, then segmented with `scripts/segmentation/`.
- **Unit definition:** smallest span carrying one dominant pragmatic function toward a political target.
- **Token cap:** 400 tokens (BETO tokenizer: `dccuchile/bert-base-spanish-wwm-cased`).
- **Normalization:** Unicode NFC; URLs masked as `<URL>`, @mentions as `<USER>`; hashtags preserved.
- **Deduplication:** near-verbatim duplicates removed (MinHash, threshold 0.85; keep earliest).
- **Exclusions:** segments <20 or >2,000 characters; pure roll-call boilerplate; sources without text redistribution rights.

### Provenance

Each unit stores `document_id`, `unit_id`, `metadata.source_type`, speaker fields where available, and `provenance.license_status` / `license_ref` per upstream corpus. Raw upstream files are **not** bundled in Git.

## Annotation process

1. **Guidelines** — Versioned codebook (`annotation/codebook/SPDB_Codebook_v1.md`) and Label Studio configuration (`annotation/labelstudio/`).
2. **Primary annotation** — Trained annotators assign pragmatic function and fallacy labels under PI supervision.
3. **Quality control** — 20% double-coded subset; Cohen's κ / Krippendorff's α reported on development data.
4. **Adjudication** — Senior adjudicator resolves pragmatic-function disagreements and borderline fallacy cases; logs store IDs and label deltas only.
5. **Gold export** — Adjudicated labels written to JSONL/CSV with stable `unit_id` keys matching the schema (`schemas/discourse_unit.schema.json`).

**Independence rule:** pragmatic function and fallacy labels are coded independently (e.g. evidence-based attack without ad hominem).

## Splits

Planned v1 split policy (@ 8,000 annotated units):

| Split | Share | Units | Purpose |
|-------|------:|------:|---------|
| `train` | 70% | 5,600 | Model training |
| `validation` | 15% | 1,200 | Hyperparameter tuning, IA monitoring |
| `test` | 15% | 1,200 | **Locked** final evaluation |

**Grouping constraints:**

- Document-level: all segments from the same `document_id` stay in one split.
- Stratification: match `source_type`, `party_family`, and temporal bin within ±2% per split.
- Social media: account-level grouping to prevent leakage.
- Test labels locked before baseline tuning; test IDs committed as `test_manifest.sha256`.

**Files (planned):** `spdb_v1_train.jsonl`, `spdb_v1_dev.jsonl`, `spdb_v1_test.jsonl` (+ flat CSV companions for IberLEF-style consumption).

## Licensing

| Component | License | Notes |
|-----------|---------|-------|
| SPDB annotations & guidelines | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) | Project-authored labels and documentation |
| Repository code | See [`LICENSE`](LICENSE) | Under review (Apache 2.0 / MIT target) |
| Upstream source text | Per-record `license_ref` | ParlaMint-ES, MARPOR, etc. |
| Social-media text (public set) | Not redistributed where ToS require | Post IDs + rehydration instructions |

Users must comply with upstream corpus terms in addition to SPDB's CC BY 4.0 annotation layer.

## Known limitations

- **Partial release:** Annotated train/dev/test splits are **not yet published**; current release is documentation, tooling, and pilot samples.
- **Register coverage:** Development data is predominantly parliamentary; manifesto and social slices require additional ingestion and license clearance.
- **Segmentation heuristics:** Paragraph/sentence splits may mis-boundary units; >10% segmentation error on QC triggers pipeline revision.
- **Social text access:** Public release may contain metadata/IDs only; researchers must rehydrate text under platform terms locally.
- **Experimental labels:** Semantic vacuity and conceptual anachronism are optional and excluded from the official v1 leaderboard ranking.
- **Ontology scope:** Eight pragmatic functions and seven fallacy types are operational reductions, not exhaustive rhetorical taxonomies.
- **Cross-lingual use:** Labels are tuned to Spanish institutional genres; transfer requires re-validation.

## Ethical considerations

SPDB covers **public political communication** by elected officials, party organs, and candidates — not private citizens.

- **Platform compliance:** Social-media text follows IDs-only release where redistribution is restricted.
- **Annotator welfare:** Guidelines include breaks and escalation for inflammatory content; annotator IDs are pseudonymized.
- **Misuse:** The dataset is intended for research on discourse structure and modelling — not for targeting individuals, voter manipulation, or surveillance.
- **Re-identification:** Users must not attempt to re-identify speakers beyond what public sources already expose.
- **Human subjects:** Formal IRB/ethics review depends on deployment jurisdiction; documented before annotation wave 2.

See `docs/ethics.md` for the living ethics policy.

## Citation

**DOI:** [10.5281/zenodo.23039355](https://doi.org/10.5281/zenodo.23039355)

**APA**

> J. Baena Rojas, D. Pinto Pajares, & C. Andrés (2026). *SPDB v1.0.0 — Spanish Political Discourse Annotation Resource* (Version 1.0.0) [Computer software]. Zenodo. https://doi.org/10.5281/zenodo.23039355

**BibTeX**

```bibtex
@misc{spdb_2026,
  author       = {José Jaime Baena Rojas and Daniel Pinto Pajares and César Andrés},
  title        = {SPDB v1.0.0 — Spanish Political Discourse Annotation Resource},
  year         = {2026},
  version      = {1.0.0},
  doi          = {10.5281/zenodo.23039355},
  publisher    = {Zenodo},
  url          = {https://doi.org/10.5281/zenodo.23039355}
}
```

Machine-readable metadata: [`CITATION.cff`](CITATION.cff)

When using upstream corpora (ParlaMint, MARPOR, etc.), cite the original sources in addition to SPDB.

## Additional links

| Resource | Location |
|----------|----------|
| GitHub repository | [https://github.com/cesar-andress/spanish_political_discourse_benchmark](https://github.com/cesar-andress/spanish_political_discourse_benchmark) |
| Zenodo record | [https://doi.org/10.5281/zenodo.23039355](https://doi.org/10.5281/zenodo.23039355) |
| JSON Schema | [`schemas/discourse_unit.schema.json`](schemas/discourse_unit.schema.json) |
| v1 build specification | [`docs/dataset_documentation/v1_build_specification.md`](docs/dataset_documentation/v1_build_specification.md) |
| Datasheet | [`docs/datasheet_for_datasets.md`](docs/datasheet_for_datasets.md) |
| Changelog | [`docs/changelog.md`](docs/changelog.md) |

**Contact:** [josejaime.baena@unir.net](mailto:josejaime.baena@unir.net) · [daniel.pinto@unir.net](mailto:daniel.pinto@unir.net)
