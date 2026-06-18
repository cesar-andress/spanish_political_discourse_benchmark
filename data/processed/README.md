# Processed data (local)

Large or regenerated artefacts under `data/processed/` are **gitignored** by default.

## Pilot 100-unit sample (v0.1.0-alpha)

The versioned alpha sample lives in the repository:

```
releases/v0.1.0-alpha/samples/parlamint_100_units.jsonl
releases/v0.1.0-alpha/samples/pilot_100_units.csv
```

## Regenerate locally

From a full ParlaMint processed pool:

```bash
make parlamint-100
```

This writes `data/processed/parlamint_100_units.jsonl` (100 lines, seed 42). Copy into the release bundle if refreshing the alpha sample:

```bash
cp data/processed/parlamint_100_units.jsonl releases/v0.1.0-alpha/samples/
make release-validate
```

See [`docs/pipeline.md`](../docs/pipeline.md) and [`docs/sources/parlamint.md`](../docs/sources/parlamint.md).
