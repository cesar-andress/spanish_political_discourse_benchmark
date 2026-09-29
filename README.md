# SPDB — Spanish Political Discourse Annotation Resource

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20745403.svg)](https://doi.org/10.5281/zenodo.20745403)
[![Version](https://img.shields.io/badge/version-v1.0.1-blue)](docs/release_notes_v1.0.1.md)
[![License](https://img.shields.io/badge/license-CC%20BY%204.0-green)](LICENSE)

**Current release:** [`v1.0.1`](docs/release_notes_v1.0.1.md) — provenance and metadata correction over immutable [`v1.0.0`](docs/release_notes_v1.0.0.md). Primary Wave-1 labels and agreement metrics are unchanged.

## What SPDB is

SPDB is a **reproducible annotation resource** for **pragmatic function** in Spanish political and parliamentary discourse. It provides schemas, label inventories, annotation guidelines, sampling/reproduction code, and a completed two-coder diagnostic reliability pilot on ParlaMint-ES units.

## What the current release contains

- Annotation infrastructure (schemas, PF label inventory, guidelines)
- ParlaMint-derived development pool metadata and reproducible sampling (pool **N = 878**)
- Wave-1 pragmatic-function pilot: **N = 100**, two independent annotators, simple random sample without replacement, **seed = 42**
- Agreement and disagreement analysis artefacts needed to reproduce the reported pilot evidence
- Historical instrument **codebook-v1.0.0** (Wave-1 instrument) and revised **codebook-v1.1.0**
- Corrected provenance documentation for exploratory post-hoc disagreement-cause labels (v1.0.1)

## What the pilot found

Under the Wave-1 instrument, observed agreement was **0.350**; Cohen κ ≈ **0.235**; Krippendorff α ≈ **0.223**; Fleiss κ ≈ **0.219**; **65** disagreements. The initial pragmatic-function instrument did not meet the project screening threshold of α ≥ 0.67.

The primary reliable evidence is the frozen dual-coder labels, agreement coefficients, confusion matrix, and coder marginals (including argumentative-subset sensitivity analyses reported in the companion paper).

An exploratory post-hoc disagreement review was produced with AI-assisted workflow support to help identify candidate sources of ambiguity. These cause labels were **not** independently human-audited and should be treated as diagnostic rather than as validated qualitative annotations. See [`annotation/pilot_001/results/README.md`](annotation/pilot_001/results/README.md).

## What codebook-v1.1.0 means

**codebook-v1.1.0** is a documented revision addressing observed Wave-1 ambiguities. It is included for transparency. It has **not** been independently revalidated; this release does **not** claim that v1.1 improved reliability.

## What this release does not contain

- No adjudicated human gold labels
- No validated production multi-register labelled corpus
- No native human fallacy gold
- No leaderboard-ready / production benchmark claim
- No independently human-verified disagreement-cause taxonomy

## Provenance fence (Wave-1 vs v1.1)

| Stage | Instrument | Empirical status |
|-------|------------|------------------|
| Wave-1 annotations | codebook-v1.0.0 / guidelines-v1.0 | Completed two-coder diagnostic pilot (N = 100) |
| Post-Wave-1 revision | codebook-v1.1.0 / guidelines-v1.1 | Documented revision only; **not** independently reliability-tested |

Do not treat Wave-1 labels as coded under v1.1.

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make test
make release-validate
```

Wave-1 public annotations and metrics:

```bash
ls annotation/pilot_001/
python -m analysis.pilot.agreement_analysis \
  --annotator-a annotation/pilot_001/pilot_100_units_annotator_a.csv \
  --annotator-b annotation/pilot_001/pilot_100_units_annotator_b.csv
```

Release bundle:

```bash
ls releases/v1.0.1/
cat releases/v1.0.1/MANIFEST.json
```

## Repository layout

```
annotation/     Guidelines, codebooks (v1.0 + v1.1), Wave-1 pilot packages
analysis/       Agreement, disagreement, and ontology-compatibility tooling
docs/           Pipeline, ethics, release notes, source notes
labels/         Ontology TSV inventories (+ historical v1.0.0 snapshot)
schemas/        JSON Schema for discourse units and pipeline output
scripts/        Ingestion, sampling, validation, release helpers
releases/       Versioned release bundles (samples + manifest + checksums)
data/           Local raw/processed data (gitignored; see data/*/README.md)
```

## How to cite

**Concept DOI (all versions):** [10.5281/zenodo.20745403](https://doi.org/10.5281/zenodo.20745403)

Historical Zenodo version DOI for the alpha deposit: [10.5281/zenodo.20745404](https://doi.org/10.5281/zenodo.20745404) (`0.1.0-alpha`). Prefer the **v1.0.1 version DOI** once Zenodo assigns it. Machine-readable metadata: [`CITATION.cff`](CITATION.cff).

**APA (concept DOI; update version DOI after Zenodo assigns it)**

> Baena Rojas, J. J., Pinto Pajares, D., & Andrés, C. (2026). *SPDB v1.0.1 — Spanish Political Discourse Annotation Resource* (Version 1.0.1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.20745403

## Licence

Original SPDB material: **CC BY 4.0**. ParlaMint-derived text remains under upstream **CC BY 4.0** with attribution. See [`LICENSE`](LICENSE) and [`docs/sources/parlamint.md`](docs/sources/parlamint.md).

## Authors

Jose Jaime Baena Rojas · Daniel Pinto Pajares · César Andrés (corresponding author for the companion manuscript)

Funding: no external/specific funding for this work. Competing interests: none.
