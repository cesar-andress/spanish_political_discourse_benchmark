# Release notes — SPDB v1.0.1

**Title:** SPDB v1.0.1 — Provenance and Metadata Correction

**Date:** 2026-09-29

Patch release over immutable `v1.0.0`. This corrects documentation and metadata
provenance only.

## What did not change

- No human annotation labels changed
- No sample identifiers changed
- No primary Wave-1 agreement statistics changed
- No codebook definitions changed as part of this patch
- No new annotation was added

Locked primary evidence remains: N = 100; observed agreement = 0.350;
Cohen κ ≈ 0.235; Krippendorff α ≈ 0.223; Fleiss κ ≈ 0.219; 65 disagreements.

## Corrections

1. C1–C6 disagreement-cause classifications are now clearly labelled as
   exploratory, post-hoc, and AI-assisted (see
   `annotation/pilot_001/results/README.md` and
   `disagreement_taxonomy.provenance.json`).
2. Public documentation no longer presents those classifications as
   independently human-audited evidence.
3. Zenodo **concept DOI** metadata is corrected to
   `10.5281/zenodo.20745403` (historical alpha version DOI remains
   ``).
4. Manifest and data-dictionary wording are aligned with the corrected
   companion manuscript.

## Canonical identifiers

- Git tag: `v1.0.1`
- Version DOI (published v1.0.0): https://doi.org/10.5281/zenodo.23039355
- Concept DOI: https://doi.org/10.5281/zenodo.20745403
