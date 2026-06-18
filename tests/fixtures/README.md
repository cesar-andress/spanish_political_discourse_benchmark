# Test fixtures (not SPDB benchmark data)

Files under `tests/fixtures/` are **synthetic technical fixtures** for automated tests and local pipeline smoke checks. They are **not** part of the Spanish Political Discourse Benchmark release and **must not** be treated as empirical data.

| Path | Purpose |
|------|---------|
| `pipeline/` | Ingestion and segmentation JSONL samples |
| `labelstudio_*.json` | Label Studio import/export validator samples |

Run the guarded test pipeline with:

```bash
make pipeline-fixture
```

Real corpus builds must use local raw files under `data/raw/` and:

```bash
make pipeline INGEST_INPUT=data/raw/parliamentary/your_file.jsonl
```
