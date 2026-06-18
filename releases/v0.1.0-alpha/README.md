# SPDB v0.1.0-alpha release bundle

**Status:** prepared locally; **not published** to GitHub Releases or Zenodo.

This directory holds the **alpha sample data** shipped with tag `v0.1.0-alpha`. It is not the v1 benchmark gold release.

## Samples

| File | Description |
|------|-------------|
| [`samples/parlamint_100_units.jsonl`](samples/parlamint_100_units.jsonl) | 100 unannotated discourse units (ParlaMint-ES, seed 42) |
| [`samples/pilot_100_units.csv`](samples/pilot_100_units.csv) | Same units in flat CSV for pilot annotation |
| [`CHECKSUMS.sha256`](CHECKSUMS.sha256) | SHA-256 checksums |

Regenerate from the full pool:

```bash
make parlamint-100
cp data/processed/parlamint_100_units.jsonl releases/v0.1.0-alpha/samples/
# Re-export CSV from annotation/pilot_001/pilot_100_units.csv if regenerated
make release-validate
```

See [`docs/release_notes_v0.1.0-alpha.md`](../../docs/release_notes_v0.1.0-alpha.md).
