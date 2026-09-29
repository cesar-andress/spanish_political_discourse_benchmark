# Release notes — SPDB v1.0.0

**Title:** SPDB v1.0.0 — Spanish Political Discourse Annotation Resource

**Date:** 2026-09-29

First stable, citable release of the SPDB pragmatic-function annotation resource,
Wave-1 diagnostic reliability evidence, versioned instruments, and reproducibility
tooling.

## What is new since `spdb-v0.1.0`

- Frozen Wave-1 public annotations (N = 100; two independent annotators; seed = 42)
- Verified agreement results: observed agreement 0.350; Cohen κ ≈ 0.235;
  Krippendorff α ≈ 0.223; Fleiss κ ≈ 0.219; 65 disagreements
- Corrected sampling description (simple random sample without replacement from the
  ParlaMint-derived development pool, N = 878)
- Systematic disagreement taxonomy (public CSV; C2 = 23, C3 = 18, C4 = 11 among
  cause classes)
- Historical preservation of codebook-v1.0.0 (Wave-1 instrument)
- Documented revised codebook-v1.1.0 and guidelines-v1.1 (not independently
  revalidated)
- Improved README, CITATION.cff, Zenodo metadata, and licence documentation
- Release manifest with SHA-256 checksums
- Ontology-compatibility tooling for external fallacy resources (external corpora
  not redistributed)

## Limitations

- Two-coder N = 100 diagnostic study (not a multi-wave production annotation)
- Human annotation in this release covers pragmatic function only
- No adjudicated gold labels
- codebook-v1.1.0 is not independently reliability-tested in this release
- Not a validated production multi-register labelled benchmark

## Provenance

Wave-1 labels were produced under the v1.0-era instrument. codebook-v1.1.0 is a
post-Wave-1 revision. Do not mix the two under a single reliability claim.

## Canonical identifiers

- Git tag: `v1.0.0`
- Concept DOI: https://doi.org/10.5281/zenodo.20745404
- Version DOI: assigned by Zenodo upon publication of this release
