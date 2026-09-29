# Reproducibility (SPDB v1.0.0)

## Environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

No absolute local home paths are required. Raw ParlaMint TEI under `data/raw/`
is optional for regenerating samples; public Wave-1 CSVs and `releases/v1.0.0/`
already contain the units needed for the published pilot metrics.

## Core checks

```bash
make test
make release-validate
```

## Wave-1 metric reproduction

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

Cause counts from `annotation/pilot_001/results/disagreement_taxonomy.csv`:
C2 = 23, C3 = 18, C4 = 11.

## Release integrity

```bash
python scripts/release/verify_manifest.py releases/v1.0.0/MANIFEST.json
```

(If the helper script name differs in this tree, compare SHA-256 hashes in
`releases/v1.0.0/SHA256SUMS` against the checked-out files.)

## Data availability

Public GitHub repository and Zenodo concept DOI:
https://doi.org/10.5281/zenodo.20745404
