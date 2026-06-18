# SPDB data pipeline (v0.1)

First-stage pipeline for parliamentary discourse: **ingest → segment → validate**.

All steps operate on **local files only**. No automatic downloads and no synthetic benchmark text.

## Layout

| Stage | Script | Input | Output |
|-------|--------|-------|--------|
| Ingest | `scripts/ingestion/ingest_parliament.py` | Local `.jsonl`, `.json`, `.csv`, `.txt` | `data/intermediate/parliament_documents.jsonl` |
| Segment | `scripts/segmentation/segment_discourse_units.py` | `data/intermediate/parliament_documents.jsonl` | `data/processed/discourse_units.jsonl` |
| Validate | `scripts/validation/validate_dataset.py` | `data/processed/discourse_units.jsonl` | exit code + log |

JSON Schemas:

- `schemas/parliament_document.schema.json`
- `schemas/pipeline_discourse_unit.schema.json`

## Makefile targets

```bash
make ingest    # local raw file → intermediate JSONL
make segment   # intermediate → discourse units
make validate  # schema + duplicate + empty-text checks
make pipeline  # ingest + segment + validate
```

Override input paths when needed:

```bash
make ingest INGEST_INPUT=/path/to/local/records.jsonl
make segment INTERMEDIATE=data/intermediate/parliament_documents.jsonl
make validate PROCESSED=data/processed/discourse_units.jsonl
```

## CLI examples

### Ingest

```bash
# JSONL / JSON (structured records)
python -m scripts.ingestion.ingest_parliament \
  --input data/raw/parliamentary/interventions.jsonl

# CSV with header row
python -m scripts.ingestion.ingest_parliament \
  --input data/raw/parliamentary/interventions.csv

# Plain text (optional sidecar metadata: speech.txt + speech.json)
python -m scripts.ingestion.ingest_parliament \
  --input data/raw/parliamentary/speech.txt \
  --document-id congreso-2023-001 \
  --source-name congreso \
  --date 2023-07-12 \
  --speaker-name "Ana Example" \
  --speaker-party PSOE

# Directory of .txt files (document_id = filename stem)
python -m scripts.ingestion.ingest_parliament \
  --input data/raw/parliamentary/txt/
```

### Segment

```bash
python -m scripts.segmentation.segment_discourse_units \
  --input data/intermediate/parliament_documents.jsonl \
  --output data/processed/discourse_units.jsonl \
  --max-tokens 400 \
  --min-chars 20
```

### Validate

```bash
python -m scripts.validation.validate_dataset \
  --input data/processed/discourse_units.jsonl
```

## Expected JSONL schemas

### Intermediate: `parliament_documents.jsonl`

One JSON object per parliamentary intervention (document level):

```json
{
  "document_id": "congreso-2023-001",
  "source_type": "parliamentary",
  "source_name": "congreso",
  "date": "2023-07-12",
  "speaker_name": "Ana Example",
  "speaker_party": "PSOE",
  "language": "es",
  "text": "Señorías, proponemos una reforma fiscal justa."
}
```

Legacy field names (`doc_id`, `speaker`, `party`, `text_raw`, `chamber`) are accepted at ingest time and normalised to this schema.

### Processed: `discourse_units.jsonl`

One JSON object per discourse unit (segment level):

```json
{
  "unit_id": "spdb-v1-unassigned-a1b2c3d4e5f6",
  "document_id": "congreso-2023-001",
  "language": "es",
  "text": "Señorías, proponemos una reforma fiscal justa.",
  "character_count": 45,
  "token_count": 12,
  "metadata": {
    "source_type": "parliamentary",
    "source_name": "congreso",
    "date": "2023-07-12",
    "speaker_name": "Ana Example",
    "speaker_party": "PSOE",
    "segment_index": 0,
    "char_start": 0,
    "char_end": 45
  }
}
```

`unit_id` is stable for a given `(document_id, segment_index, split)` triple.

## Validation checks

`validate_dataset.py` reports errors for:

- missing required top-level or metadata fields
- duplicate `unit_id`
- empty `text`
- schema violations (language code, ISO date, counts, offsets)
- non-parliamentary `metadata.source_type`

## Segmentation rules

Spanish paragraph-aware splitting with sentence-boundary refinement when token or character caps are exceeded (defaults: 400 tokens, 20–2000 characters per unit). Token counts use a BETO estimate offline; pass `--use-beto-model` when the Hugging Face tokenizer is available locally.

## Related documentation

- `docs/reproducibility.md` — release reproducibility
- `docs/dataset_documentation/v1_build_specification.md` — full SPDB v1 build spec
- `data/intermediate/README.md` — intermediate storage policy
