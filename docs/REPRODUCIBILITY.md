# Reproducibility (SPDB v1.0.1)

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

No absolute local home paths are required. Raw ParlaMint TEI under `data/raw/`
is optional for regenerating samples; public Wave-1 CSVs and `releases/v1.0.1/`
already contain the units needed for the published pilot metrics.

## Core checks

```bash
make test
make release-validate
```

## Primary reproducible human evidence

```bash
python -m analysis.pilot.agreement_analysis \
  --annotator-a annotation/pilot_001/pilot_100_units_annotator_a.csv \
  --annotator-b annotation/pilot_001/pilot_100_units_annotator_b.csv \
  --output-dir /tmp/spdb_wave1_repro
```

Expected locked summary (rounded as in the companion paper):

- N = 100
- observed agreement = 0.350
- Cohen κ ≈ 0.235
- Krippendorff α ≈ 0.223
- Fleiss κ ≈ 0.219
- disagreements = 65

Authoritative artefacts: dual-coder CSVs, `cohen_kappa.json`,
`krippendorff_alpha.json`, confusion matrix, and `disagreement_report.*`.

## Exploratory post-hoc diagnostic material

`annotation/pilot_001/results/disagreement_taxonomy.csv` is an exploratory
post-hoc AI-assisted disagreement review. It is **not** independently
human-verified. Reproduce or inspect it only as diagnostic context; do not
treat cause tallies as validated qualitative findings. See
`disagreement_taxonomy.provenance.json`.

## Release integrity

Compare SHA-256 hashes in `releases/v1.0.1/SHA256SUMS` against the checked-out
files.

## Data availability

Public GitHub repository and Zenodo **version** DOI:
https://doi.org/10.5281/zenodo.23039355

Concept DOI (all versions): https://doi.org/10.5281/zenodo.20745403
