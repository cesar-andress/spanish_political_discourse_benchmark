# Workflow (SPDB v1.0.0)

1. **Acquire** ParlaMint-ES TEI locally under `data/raw/parlamint/` when regenerating samples.
2. **Ingest / segment** via Makefile targets (`make ingest-parlamint`, `make segment-parlamint`).
3. **Annotate** using versioned codebooks under `annotation/codebook/` (Wave-1 used codebook-v1.0.0).
4. **Analyse** agreement with `make pilot-agreement` / `analysis.pilot`.
5. **Release** via Git tag + GitHub Release + Zenodo (version DOI 10.5281/zenodo.23039355).

Frozen Wave-1 evidence for v1.0.0 lives under `annotation/pilot_001/` and `releases/v1.0.0/`.
Do not alter annotation values when updating documentation.
