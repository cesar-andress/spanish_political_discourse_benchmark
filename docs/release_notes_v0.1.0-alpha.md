# Release notes — v0.1.0-alpha

**Date (prepared):** 2026-06-18  
**Status:** repository prepared; **not published** (no GitHub Release, no Zenodo DOI).

## Summary

First **public alpha** of the Spanish Political Discourse Benchmark (SPDB). This release documents the v1 annotation framework and ingestion pipeline, and ships an **unannotated** 100-unit ParlaMint pilot sample for guideline testing and tooling development.

This is **not** a benchmark gold release. Do not use these units as training or evaluation data for published results.

## Included

| Component | Location |
|-----------|----------|
| Repository README | [`README.md`](../README.md) |
| Citation metadata | [`CITATION.cff`](../CITATION.cff) |
| Zenodo deposit config | [`.zenodo.json`](../.zenodo.json) |
| Annotation guidelines index | [`annotation/guidelines/README.md`](../annotation/guidelines/README.md) |
| Label Studio instructions | [`annotation/labelstudio/instructions.md`](../annotation/labelstudio/instructions.md) |
| Codebook v1 | [`annotation/codebook/`](../annotation/codebook/) |
| JSON schemas | [`schemas/`](../schemas/) |
| Label inventories | [`labels/`](../labels/) |
| Pipeline documentation | [`docs/pipeline.md`](../pipeline.md) |
| 100-unit pilot sample (JSONL + CSV) | [`releases/v0.1.0-alpha/samples/`](../releases/v0.1.0-alpha/samples/) |
| Release manifest | [`releases/v0.1.0-alpha/MANIFEST.json`](../releases/v0.1.0-alpha/MANIFEST.json) |

## Pilot sample

- **Source:** ParlaMint-ES (see [`docs/sources/parlamint.md`](sources/parlamint.md))
- **Selection:** 100 discourse units, deterministic seed 42 from the processed pool
- **Format:** `pipeline_discourse_unit.schema.json` (JSONL) and flat CSV for Label Studio import
- **Annotations:** none (empty label columns)

## Versioning

| Artefact | Version |
|----------|---------|
| Release tag | `v0.1.0-alpha` |
| Guidelines | `guidelines-v1.0` |
| Codebook | `codebook-v1.0.0` |
| Schemas | as committed at tag |

## Not included (planned for later releases)

- Annotated train / dev / test splits
- Zenodo DOI and archived tarball
- Baseline model results and leaderboard
- Full raw ParlaMint TEI tree (download instructions only)

## Validation

Before tagging or publishing:

```bash
make release-validate
make test
```

## Citation

When citing this alpha release, use [`CITATION.cff`](../CITATION.cff). A DOI will be added after Zenodo deposit of a stable release.

## Next steps

See [`github_release_checklist_v0.1.0-alpha.md`](github_release_checklist_v0.1.0-alpha.md).
