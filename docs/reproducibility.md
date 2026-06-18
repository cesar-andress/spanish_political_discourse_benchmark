# Reproducibility

**Status:** under development (`v0.1.0-dev`)

This document describes how SPDB artefacts are versioned, built, and verified. The annotated dataset is **not yet available**; steps below apply to repository tooling and planned release workflows.

## Principles

1. **Stable identifiers** — `instance_id`, `document_id`, and pipeline version stamps on every record.
2. **Schema validation** — JSONL exports validated against `schemas/discourse_unit.schema.json`.
3. **Pinned environments** — Python ≥3.11; dependency pins planned in `environment/requirements.txt`.
4. **Split integrity** — Document-level and account-level grouping; locked test manifest at v1.0.0.
5. **Dual archive** — GitHub (code + docs) and Zenodo (data DOI) at public release.

## Environment setup (planned)

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -e code/
```

Full instructions: [`environment/reproducibility_setup.md`](../environment/reproducibility_setup.md).

## Pipeline stages

| Stage | Script / path | Output |
|-------|---------------|--------|
| Ingestion | `scripts/ingestion/ingest_*.py` | `data/intermediate/` JSONL |
| Segmentation | `scripts/segmentation/segment_discourse_units.py` | `data/processed/segmented/` JSONL |
| Annotation | Label Studio → export converter (planned) | `data/processed/annotations/` |
| Release | Build spec §12 | `spdb_v1_{split}.jsonl` on Zenodo |

Construction protocol: [`dataset_documentation/v1_build_specification.md`](dataset_documentation/v1_build_specification.md).

## Verification checklist (development)

```bash
# Schema + pipeline unit tests
PYTHONPATH=. python3.11 -m pytest scripts/ingestion/tests/ scripts/segmentation/tests/

# Dataset inventory (local paths)
make dataset-inventory
```

At release, the following will be added: test-manifest hash verification, baseline config hashes, and Zenodo bundle checksums.

## Provenance fields

Each `discourse_unit` records `pipeline_version`, `created_at`, `annotation_version`, and `guideline_version` (when annotated). See [`DATA_DICTIONARY.md`](DATA_DICTIONARY.md).

## Archiving

- **Git tags:** `spdb-v1.0.0` aligned with Zenodo concept DOI (planned).
- **Zenodo:** [`zenodo/`](../zenodo/) release notes and `.zenodo.json` metadata.
- **No large data in Git:** raw/processed blobs excluded via `.gitignore`; distributed via Zenodo.

## Related documents

- [`reproducibility.md`](reproducibility.md) (this file)
- [`../datasheet/datasheet.md`](../datasheet/datasheet.md)
- [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) — legacy stub; prefer this file
