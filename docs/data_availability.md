# Data availability

**Status:** under development (`v0.1.0-dev`)

## Current availability

| Artefact | Location | Status |
|----------|----------|--------|
| Annotated JSONL splits | Zenodo + `data/processed/` | **Not yet available** |
| Raw source corpora | `data/raw/` | **Not yet available** (not tracked in Git) |
| Label ontologies | `labels/*.tsv` | **Available** |
| JSON Schema | `schemas/discourse_unit.schema.json` | **Available** |
| Ingestion / segmentation code | `scripts/` | **Under development** |
| Baseline predictions | `results/` | **Not yet available** |
| Zenodo DOI | — | **Not yet available** |

> **Warning:** This repository is under active development. The benchmark dataset has not yet been released.

## Planned release (v1.0.0)

The public release will include:

- `spdb_v1_train.jsonl`, `spdb_v1_dev.jsonl`, `spdb_v1_test.jsonl`
- Flat CSV companions
- `label_inventory.tsv`
- `test_manifest.sha256`
- De-identified adjudication logs (IDs + label deltas)
- Social slice: post ID tables + rehydration script (where applicable)
- Optional baseline prediction files and model configs

Target archive: **Zenodo concept DOI** with versioned uploads; Git tag `spdb-v1.0.0` on GitHub.

## Access before release

Development collaborators may obtain intermediate exports under team agreement. No public download is offered until v1.0.0 checklist completion: [`dataset_documentation/release_checklist.md`](dataset_documentation/release_checklist.md).

## Rehydration (social media)

Where full text cannot be redistributed, researchers will rebuild posts locally from `platform_post_id` and documented endpoints/archives. Instructions: [`dataset_documentation/rehydration_instructions.md`](dataset_documentation/rehydration_instructions.md) (under development).

## Provisional citation

See [`../CITATION.cff`](../CITATION.cff) and README citation block. Do not cite a DOI until Zenodo registration is complete.
