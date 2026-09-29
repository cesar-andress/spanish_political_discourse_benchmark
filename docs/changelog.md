# Changelog

All notable changes to this repository are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

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
- Canonical version identifier: `v1.0.0` (concept DOI remains 10.5281/zenodo.20745404)
- ParlaMint licence status documented as verified **CC BY 4.0**
- Public documentation narrowed: not a validated / gold / production benchmark

### Explicit non-claims
- No adjudicated gold; no validated multi-register labelled corpus
- codebook-v1.1.0 does not claim improved reliability
- Calibration / Wave-2 packages are not part of completed empirical evidence

## [0.1.0 / spdb-v0.1.0] — 2026-06-18

Published historical GitHub release `spdb-v0.1.0` (alpha-era infrastructure and
unannotated sample lineage). Preserved; not rewritten.

## [0.1.0-alpha] — 2026-06-18

Historical tag `v0.1.0-alpha` (failed / incomplete Zenodo webhook lineage).
Preserved for provenance; **v1.0.0** is the canonical stable release.
