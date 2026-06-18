# Annotation workflow (Label Studio)

**Status:** under development (`v0.1.0-dev`)

This document describes how to import tasks, export annotations, and validate exports for SPDB v1 using Label Studio. It covers **technical workflow only**—not annotation guidelines (see `annotation/labelstudio/instructions.md` and `protocol/`).

> **Warning — synthetic fixtures only:** Files under `tests/fixtures/` (e.g. `labelstudio_import_sample.json`) are **synthetic technical fixtures** for import/export testing. They are **not** benchmark data, **not** research examples, and **must not** be used as dataset instances or cited as empirical samples.

## Prerequisites

- Label Studio project with SPDB labeling interface
- Configuration: [`annotation/labelstudio/config.xml`](../annotation/labelstudio/config.xml)
- Annotator instructions: [`annotation/labelstudio/instructions.md`](../annotation/labelstudio/instructions.md)

## 1. Import tasks into Label Studio

### Use the synthetic import fixture (smoke test)

For pipeline testing only:

```bash
# File: tests/fixtures/labelstudio_import_sample.json
# Contains 3 synthetic tasks (primary ×2, adjudication ×1)
```

**Steps:**

1. Open your Label Studio project → **Settings** → **Labeling Interface** → paste `annotation/labelstudio/config.xml`.
2. Go to **Import** and upload `tests/fixtures/labelstudio_import_sample.json`.
3. Confirm each task displays:
   - `instance_id`, `document_id`, `task_type`, `experimental_subset`
   - Synthetic text beginning with *"Texto sintético de prueba…"*
   - Adjudication panel content only on the adjudication task

### Production import (planned)

Production tasks will be exported from the segmentation pipeline as JSON arrays with a `data` object per discourse unit. Required fields:

| Field | Description |
|-------|-------------|
| `instance_id` | Stable unit ID |
| `document_id` | Source document ID |
| `text` | Annotatable span |
| `task_type` | `primary` or `adjudication` |
| `experimental_subset` | `true` or `false` |
| `adjudication_context` | HTML summary for adjudication tasks; empty otherwise |

Optional: `context_prev`, `context_next`, `source_type`, `source_corpus`, `party_family`, `date`.

**Not yet available:** automated export from `data/processed/` to Label Studio import format.

## 2. Annotate (development)

During development, use the synthetic fixture to verify the interface. Do **not** treat fixture labels as gold data.

Annotation order in the UI:

1. Pragmatic function (exactly one)
2. Fallacies (multi-label **or** explicit none)
3. Experimental labels (only when `experimental_subset=true`)

## 3. Export annotations

1. In Label Studio, open **Export**.
2. Choose **JSON** (full export with annotations).
3. Save locally, e.g. `export/labelstudio_dev_export.json`.

Export structure (simplified):

```json
[
  {
    "id": 9001,
    "data": { "instance_id": "...", "text": "...", "experimental_subset": "false", ... },
    "annotations": [
      {
        "result": [
          { "from_name": "pragmatic_function", "value": { "choices": ["PF_INFO"] } },
          { "from_name": "fallacy_none_explicit", "value": { "choices": ["true"] } }
        ]
      }
    ]
  }
]
```

A matching **synthetic export fixture** for validator testing lives at `tests/fixtures/labelstudio_export_sample.json`.

## 4. Validate the export

Run the SPDB export validator:

```bash
cd spanish_political_discourse_benchmark

python scripts/validation/validate_labelstudio_export.py \
  --input tests/fixtures/labelstudio_export_sample.json

python scripts/validation/validate_labelstudio_export.py \
  --input path/to/your/export.json \
  --output reports/labelstudio_validation.txt
```

**Exit codes:** `0` = all tasks pass; `2` = one or more tasks failed; `1` = input/parse error.

### Validation rules

| Rule | Description |
|------|-------------|
| Required `data` fields | `instance_id`, `document_id`, `text`, `task_type`, `experimental_subset`, `adjudication_context` |
| Pragmatic function | Exactly one `PF_*` label |
| Fallacies | One or more `FAL_*` labels **or** `fallacy_none_explicit=true` (not both); max 3 fallacy labels |
| Experimental labels | `semantic_vacuity` and `conceptual_anachronism` required iff `experimental_subset=true`; forbidden when `false` |

## 5. Convert to SPDB JSONL (planned)

Post-validation conversion from Label Studio export → `discourse_unit` JSONL is **not yet implemented**. Validated exports will be mapped to schema fields documented in `schemas/discourse_unit.schema.json`.

## Related files

| Path | Purpose |
|------|---------|
| `tests/fixtures/labelstudio_import_sample.json` | Synthetic import smoke-test tasks |
| `tests/fixtures/labelstudio_export_sample.json` | Synthetic valid export for validator |
| `tests/fixtures/labelstudio_export_invalid.json` | Synthetic invalid export for validator tests |
| `scripts/validation/validate_labelstudio_export.py` | Export validator CLI |
| `labels/*.tsv` | Label ontology |

## Contact

Tooling questions: [daniel.pinto@unir.net](mailto:daniel.pinto@unir.net)
