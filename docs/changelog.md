# Changelog

All notable changes to this repository are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

## [1.0.1] — 2026-09-29

Corrected provenance documentation for exploratory disagreement-cause
classifications and Zenodo concept DOI metadata. No primary data, annotations,
or reported Wave-1 agreement results changed.

### Changed
- README, REPRODUCIBILITY, DATA_DICTIONARY, CITATION.cff, and `.zenodo.json`
  aligned with concept DOI `10.5281/zenodo.20745403`
- Exploratory taxonomy provenance documented beside
  `disagreement_taxonomy.csv`
- Release bundle `releases/v1.0.1/`

### Explicit non-changes
- Wave-1 dual-coder labels and primary agreement metrics unchanged from v1.0.0
- Tag `v1.0.0` remains immutable

## [1.0.0] — 2026-09-29

First stable, citable public release of the SPDB annotation resource and Wave-1
diagnostic evidence.

### Added
- Public Wave-1 pragmatic-function annotations (`annotation/pilot_001/`) with frozen metrics
- Disagreement taxonomy CSV (`annotation/pilot_001/results/disagreement_taxonomy.csv`)
- `codebook-v1.1.0` / guidelines-v1.1 as documented post-Wave-1 revision (**not** independently revalidated)
- Historical label snapshot `labels/historical/pragmatic_functions_v1.0.0.tsv`
- Release bundle `releases/v1.0.0/` (manifest + SHA-256 checksums)
- Updated README, `CITATION.cff`, `.zenodo.json`, `LICENSE`, ethics and source notes

### Changed
- Canonical version identifier: `v1.0.0`
- ParlaMint licence status documented as verified **CC BY 4.0**
- Public documentation narrowed: not a validated / gold / production benchmark

### Explicit non-claims
- No adjudicated gold; no validated multi-register labelled corpus
- codebook-v1.1.0 does not claim improved reliability
- Calibration / Wave-2 packages are not part of completed empirical evidence

### Provenance note (superseded by v1.0.1)
v1.0.0 public docs presented exploratory C1–C6 cause tallies without adequate
AI-assisted / post-hoc provenance. Corrected in **v1.0.1** without changing
primary labels. The frozen `releases/v1.0.0/` snapshot is retained historically.

## [0.1.0 / spdb-v0.1.0] — 2026-06-18

Published historical GitHub release `spdb-v0.1.0` (alpha-era infrastructure and
unannotated sample lineage). Preserved; not rewritten.

## [0.1.0-alpha] — 2026-06-18

Historical tag `v0.1.0-alpha` (failed / incomplete Zenodo webhook lineage).
Preserved for provenance. Zenodo version DOI: `10.5281/zenodo.20745404`.
