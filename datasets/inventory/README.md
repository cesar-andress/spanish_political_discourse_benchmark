# Dataset inventory

This folder holds the auto-generated dataset catalog for `papers_unir`.

## Catalog file

- **`dataset_catalog.csv`** — one row per detected dataset file under `data/` and `datasets/`.

## How the catalog is generated

From the benchmark repository root (`spanish_political_discourse_benchmark/`):

```bash
make dataset-inventory
```

Or:

```bash
python3 code/src/discourse_classifier/dataset_inventory.py
```

The script:

1. Scans `data/` and `datasets/` recursively.
2. Detects files with extensions: `.csv`, `.json`, `.jsonl`, `.parquet`, `.xlsx`, `.txt`, `.xml`, `.zip`.
3. Skips directories: `build/`, `.git/`, `__pycache__/`, `.venv/`, `node_modules/`.
4. Writes or updates `datasets/inventory/dataset_catalog.csv`.

## Column policy

| Column | Source |
|--------|--------|
| `dataset_id`, `dataset_name`, `local_path`, `file_type`, `size_bytes`, `status` | Inferred from the file |
| `language`, `source_type`, `license`, `full_text_allowed`, `topic`, `start_year`, `end_year`, `notes` | Set to `unknown` until filled manually in `datasets/metadata/` |

## Update rules

- Existing rows are **never deleted**.
- If a `local_path` is already registered, only `size_bytes` and `status` are updated.
- New files receive a new row with inferred fields and `unknown` placeholders elsewhere.

## Manual metadata

Use `datasets/metadata/dataset_template.yaml` as a template for curated metadata. Link entries to catalog rows via `dataset_id` or `local_path`.
