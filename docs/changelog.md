# Changelog

All notable changes to this repository are documented here. Versioning follows [Semantic Versioning](https://semver.org/) with `-dev` suffix while the benchmark is under construction.

## [Unreleased]

### Planned
- Complete ingestion parsers for parliamentary HTML/PDF and manifesto PDF
- Label Studio export → SPDB JSONL converter
- Pilot annotation (200 units) and inter-annotator agreement report
- Pinned `environment/requirements.txt`
- Zenodo v1.0.0 deposit and DOI

## [0.1.0-dev] — 2026-06-18

**Status:** under development — dataset **not yet released**

### Added
- `discourse_unit` JSON Schema and label ontologies (`labels/`)
- Ingestion layer skeleton (`scripts/ingestion/`)
- Segmentation layer with Spanish sentence boundaries (`scripts/segmentation/`)
- Label Studio annotation configuration (`annotation/labelstudio/`)
- v1 build specification (`docs/dataset_documentation/v1_build_specification.md`)
- Repository documentation: README, datasheet stubs, ethics, data availability, reproducibility
- Author metadata in `CITATION.cff` and `.zenodo.json`

### Not available
- Annotated JSONL splits
- Zenodo DOI
- Baseline leaderboard

---

Release notes for future public versions: [`../datasheet/release_notes.md`](../datasheet/release_notes.md).
