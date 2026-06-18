# Intermediate data

Parsed and normalized records produced by `scripts/ingestion/` before segmentation into
`discourse_unit` JSONL under `data/processed/`.

## Layout

| Path | Producer | Format |
|------|----------|--------|
| `parliamentary/` | `ingest_parliament.py` | Document-level JSONL |
| `manifestos/` | `ingest_manifestos.py` | Paragraph-level JSONL |
| `social/` | `ingest_social_ids.py` | Post-ID metadata JSONL |

## Storage policy

Large intermediate files are not tracked in Git. Regenerate from raw inputs using the
ingestion scripts documented in `docs/dataset_documentation/v1_build_specification.md`.
