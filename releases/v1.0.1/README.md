# SPDB release bundle v1.0.1

Provenance and metadata correction over immutable v1.0.0.

- `MANIFEST.json` — version, commit, primary Wave-1 counts, exploratory taxonomy provenance, file inventory
- `SHA256SUMS` — SHA-256 checksums for inventoried paths
- `samples/` — Wave-1 unit JSONL (byte-identical payload to v1.0.0 sample)

Primary Wave-1 annotations and metrics live under `annotation/pilot_001/`.
Exploratory disagreement-cause labels are **not** independently human-verified;
see `annotation/pilot_001/results/disagreement_taxonomy.provenance.json`.
