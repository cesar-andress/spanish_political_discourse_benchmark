# Spanish Political Discourse Benchmark (SPDB)

[![Status: under development](https://img.shields.io/badge/status-under%20development-orange)](docs/changelog.md)
[![Version: v0.1.0-dev](https://img.shields.io/badge/version-v0.1.0--dev-blue)](docs/changelog.md)
[![License: TBD](https://img.shields.io/badge/license-TBD-lightgrey)](LICENSE)

> **Warning:** This repository is under active development. The benchmark dataset has **not yet been released**. Data files, Zenodo DOI, and leaderboard results marked **planned** or **not yet available** should not be treated as final.

## Overview

The **Spanish Political Discourse Benchmark (SPDB)** is a reusable, stratified corpus of Spanish political discourse designed for computational social science and NLP. Each instance is a **discourse unit**—a contiguous text span annotated for **pragmatic function** (single label) and **political fallacies** (multi-label), with an experimental arm for **semantic vacuity** and **conceptual anachronism**.

SPDB combines parliamentary speech, party manifestos, and elite social media (identifiers-only public path where platform terms require it). The repository provides schemas, ingestion and segmentation tooling, annotation configuration, label ontologies, baseline plans, and release documentation.

| Item | Status |
|------|--------|
| Repository scaffolding | **Available** (v0.1.0-dev) |
| Schemas & label ontologies | **Available** |
| Ingestion / segmentation scripts | **Under development** |
| Human annotations | **Not yet available** |
| Public JSONL splits (`train` / `dev` / `test`) | **Planned** (v1.0.0) |
| Zenodo DOI | **Not yet available** |
| Baseline leaderboard | **Planned** |

Full construction protocol: [`docs/dataset_documentation/v1_build_specification.md`](docs/dataset_documentation/v1_build_specification.md).

## Intended dataset scope (v1 — planned)

| Component | Target | Minimum viable (planned) |
|-----------|--------|--------------------------|
| Annotated units (core labels) | 8,000 | 5,000 |
| Double-annotated QC subset | 20% | 20% |
| Experimental-label subset (SV/CA) | 2,000 | 1,000 |
| Distinct source documents | ≥400 | ≥250 |
| Temporal coverage | 2015–2025 | 2018–2024 |

**Source mix (by annotated unit count, planned):**

| Source type | Target share |
|-------------|--------------|
| Parliamentary discourse | 60% (55–65%) |
| Party manifestos | 12% (10–15%) |
| Elite social media (IDs-only where required) | 28% (20–30%) |

Geographic scope: Spain (state and autonomous-community sources where text redistribution is permitted). Language: Spanish (`es`).

## Planned labels

Label definitions live in [`labels/`](labels/). Summary:

| Task | Cardinality | Codes (planned) |
|------|-------------|-----------------|
| Pragmatic function | Single-label | `PF_ADVOCACY`, `PF_ATTACK`, `PF_DEFENSE`, `PF_PROPOSAL`, `PF_APPEAL`, `PF_INFO`, `PF_DEFLECT`, `PF_PROCEDURAL` |
| Political fallacies | Multi-label (max 3) or explicit none | `FAL_ADHOM`, `FAL_STRAW`, `FAL_DILEMMA`, `FAL_SLOPE`, `FAL_EMOTION`, `FAL_GENERAL`, `FAL_WHATABOUT`; `FAL_NONE` via empty list + `fallacy_none_explicit` |
| Semantic vacuity (experimental) | Single-label | `SV_0`, `SV_1`, `SV_UNCLEAR` |
| Conceptual anachronism (experimental) | Single-label | `CA_0`, `CA_1`, `CA_UNCLEAR` |

Annotation interface: [`annotation/labelstudio/`](annotation/labelstudio/).

## Repository structure

| Path | Purpose | Status |
|------|---------|--------|
| [`annotation/`](annotation/) | Label Studio config and instructions | Available |
| [`code/`](code/) | Classifier utilities and package metadata | Under development |
| [`data/`](data/) | Raw, intermediate, and processed data (not tracked in Git) | **Not yet available** (placeholders only) |
| [`datasheet/`](datasheet/) | Datasheet, data statement, release notes | Under development |
| [`datasets/`](datasets/) | Inventory and catalog metadata | Under development |
| [`docs/`](docs/) | Reproducibility, ethics, availability, changelog | Available |
| [`environment/`](environment/) | Python environment specifications | Planned |
| [`labels/`](labels/) | Machine-readable label ontologies (TSV) | Available |
| [`protocol/`](protocol/) | Annotation and baseline protocols | Under development |
| [`results/`](results/) | Metrics and model outputs | **Not yet available** |
| [`schemas/`](schemas/) | JSON Schema (`discourse_unit.schema.json`) | Available |
| [`scripts/`](scripts/) | Ingestion and segmentation pipelines | Under development |
| [`zenodo/`](zenodo/) | Release bundles and archive metadata | Planned |

## Installation (placeholder)

**Status:** environment pinning is **planned**. Current minimum for running scripts and tests:

```bash
git clone <repository-url>
cd spanish_political_discourse_benchmark
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e code/   # planned: pinned requirements in environment/requirements.txt
```

Run ingestion/segmentation tests (development snapshot):

```bash
PYTHONPATH=. python3.11 -m pytest scripts/ingestion/tests/ scripts/segmentation/tests/
```

Update dataset inventory (local paths only):

```bash
make dataset-inventory
```

See [`docs/reproducibility.md`](docs/reproducibility.md) and [`environment/reproducibility_setup.md`](environment/reproducibility_setup.md).

## Expected data format (planned release)

Canonical store: **UTF-8 JSONL**, one `discourse_unit` object per line, validated against [`schemas/discourse_unit.schema.json`](schemas/discourse_unit.schema.json).

Planned release files:

- `spdb_v1_train.jsonl`, `spdb_v1_dev.jsonl`, `spdb_v1_test.jsonl`
- Companion flat CSV for shared-task-style consumption
- `label_inventory.tsv` (aggregated from `labels/`)
- `test_manifest.sha256` (locked test IDs)

Key fields: `instance_id`, `text`, `source_type`, `document_id`, `party_family`, `pragmatic_function`, `fallacy_labels`, provenance and split metadata. Social-media public releases may set `text_redistributable=false` with IDs and rehydration instructions.

Dictionary: [`docs/DATA_DICTIONARY.md`](docs/DATA_DICTIONARY.md) (under development).

## Citation (provisional)

The benchmark is **not yet published**. When using development artefacts (schemas, code, documentation), please cite the provisional metadata below. A Zenodo DOI will be added at v1.0.0 release.

```bibtex
@misc{spdb2026,
  title        = {Spanish Political Discourse Benchmark (SPDB)},
  author       = {Baena Rojas, Jose Jaime and Pinto Pajares, Daniel and Andr{\'e}s, C{\'e}sar},
  year         = {2026},
  note         = {Under development; v0.1.0-dev. Dataset not yet released.},
  publisher    = {Universidad Internacional de La Rioja (UNIR)},
  howpublished = {GitHub/Zenodo repository},
  url          = {https://github.com/PLACEHOLDER/spdb}
}
```

Machine-readable citation: [`CITATION.cff`](CITATION.cff) (`version: 0.1.0-dev`).

### Authors

| Author | Email | ORCID |
|--------|-------|-------|
| Jose Jaime Baena Rojas | josejaime.baena@unir.net | [0000-0002-0915-4087](https://orcid.org/0000-0002-0915-4087) |
| Daniel Pinto Pajares | daniel.pinto@unir.net | [0000-0001-9397-811X](https://orcid.org/0000-0001-9397-811X) |
| César Andrés | cesar.andres@unir.net | [0009-0001-8968-3404](https://orcid.org/0009-0001-8968-3404) |

Affiliation (all authors): Universidad Internacional de La Rioja (UNIR).

## Licensing

| Component | Planned license | Status |
|-----------|-----------------|--------|
| Annotations (project work) | CC BY 4.0 | Planned |
| Code | Apache 2.0 or MIT | **TBD** — see [`LICENSE`](LICENSE) |
| Source text | Per-source (`license_ref` field) | Documented at release |
| Social-media text (public set) | Not redistributed; IDs + rehydration | Planned |

Details: [`docs/ethics.md`](docs/ethics.md), [`docs/dataset_documentation/licensing_and_ethics.md`](docs/dataset_documentation/licensing_and_ethics.md).

## Ethics and data availability

- **Human subjects:** Public political speech and programmatic text; social media handled under platform terms and IDs-only release where required.
- **Data availability:** JSONL splits and Zenodo deposit — **not yet available**. See [`docs/data_availability.md`](docs/data_availability.md).
- **Rehydration:** Elite social posts may require local rebuild from public IDs; instructions will ship with the release.

## Roadmap

| Milestone | Version | Status |
|-----------|---------|--------|
| Schemas, labels, tooling skeleton | v0.1.0-dev | **Current** |
| Ingestion + segmentation QC | v0.2.0-dev | Planned |
| Pilot annotation + IA report | v0.5.0-dev | Planned |
| Locked test manifest | v0.9.0-beta | Planned |
| Public release (GitHub tag + Zenodo DOI) | v1.0.0 | Planned |

See [`docs/changelog.md`](docs/changelog.md) and [`datasheet/release_notes.md`](datasheet/release_notes.md).

## Contact

- **Jose Jaime Baena Rojas** — [josejaime.baena@unir.net](mailto:josejaime.baena@unir.net)
- **Daniel Pinto Pajares** — [daniel.pinto@unir.net](mailto:daniel.pinto@unir.net)
- **César Andrés** — [cesar.andres@unir.net](mailto:cesar.andres@unir.net)

For contributions, see [`docs/contributing.md`](docs/contributing.md). For conduct expectations, see [`docs/CODE_OF_CONDUCT.md`](docs/CODE_OF_CONDUCT.md).
