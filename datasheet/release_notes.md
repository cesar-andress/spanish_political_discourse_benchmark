# Release notes

**Repository version:** v0.1.0-dev  
**Dataset release:** not yet available  
**Last updated:** 2026-06-18

> **Warning:** This repository is under active development. The benchmark dataset has not yet been released.

## v0.1.0-dev (current)

**Type:** development snapshot — infrastructure only

### Included
- JSON Schema for `discourse_unit`
- Label ontologies (`labels/*.tsv`)
- Ingestion and segmentation script skeletons with unit tests
- Label Studio configuration
- Build specification and repository documentation

### Not included
- Annotated JSONL files
- Zenodo DOI
- Baseline model weights or leaderboard CSV
- Raw or processed data blobs in Git

### Upgrade notes
Not applicable — no prior public release.

---

## Planned: v1.0.0

**Type:** first public benchmark release (planned)

Expected artefacts:
- `spdb_v1_{train,dev,test}.jsonl` on Zenodo
- Locked `test_manifest.sha256`
- Baseline evaluation configs and dev/test predictions
- Complete datasheet and licensing matrix
- Git tag `spdb-v1.0.0` + Zenodo concept DOI

See [`docs/changelog.md`](../docs/changelog.md) and [`../docs/dataset_documentation/release_checklist.md`](../docs/dataset_documentation/release_checklist.md).
