# Changelog

All notable changes to this repository are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Planned
- Complete ingestion parsers for parliamentary HTML/PDF and manifesto PDF
- Label Studio export → SPDB JSONL converter
- Pilot annotation agreement report (100 units)
- Annotated train / dev / test splits
- Zenodo stable release and DOI
- Baseline leaderboard

## [0.1.0-alpha] — 2026-06-18

**Status:** prepared locally — **not published** to GitHub Releases or Zenodo

First public alpha: documentation, schemas, guidelines, and an unannotated pilot sample.

### Added
- Release bundle [`releases/v0.1.0-alpha/`](releases/v0.1.0-alpha/) with manifest, checksums, and 100-unit sample
- [`docs/release_notes_v0.1.0-alpha.md`](release_notes_v0.1.0-alpha.md)
- [`docs/github_release_checklist_v0.1.0-alpha.md`](github_release_checklist_v0.1.0-alpha.md)
- [`scripts/release/validate_release_metadata.py`](../scripts/release/validate_release_metadata.py) and `make release-validate`
- Annotation guidelines index [`annotation/guidelines/README.md`](../annotation/guidelines/README.md)
- Updated README, `CITATION.cff`, `.zenodo.json` for alpha scope

### Not included
- Annotated JSONL splits
- Zenodo DOI
- Baseline leaderboard

## [0.1.0-dev] — 2026-06-18

**Status:** superseded by `0.1.0-alpha` preparation

### Added
- `discourse_unit` JSON Schema and label ontologies (`labels/`)
- Ingestion and segmentation pipeline (`scripts/`)
- Label Studio configuration (`annotation/labelstudio/`)
- v1 build specification (`docs/dataset_documentation/v1_build_specification.md`)

---

Release notes: [`release_notes_v0.1.0-alpha.md`](release_notes_v0.1.0-alpha.md).
