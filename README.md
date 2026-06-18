# Spanish Political Discourse Benchmark (SPDB)

<!-- TODO: One-paragraph description and badges (GitHub, Zenodo DOI). -->

## Layout

| Path | Purpose |
|------|---------|
| `data/` | Raw and processed benchmark data |
| `datasets/` | Inventory and metadata |
| `code/` | Ingestion, baselines, evaluation |
| `docs/` | Documentation including `dataset_documentation/` |
| `environment/` | Reproducibility setup |
| `protocol/` | Annotation and baseline plans |
| `schemas/` | JSON/CSV schemas for releases |
| `results/` | Metrics and model outputs |
| `zenodo/` | Release notes and archive metadata |

## Build specification

See `docs/dataset_documentation/v1_build_specification.md`.

## Dataset inventory

```bash
make dataset-inventory
```

## Environment

See `environment/reproducibility_setup.md`.

## License

See `LICENSE`. Per-source licensing: `docs/dataset_documentation/licensing_and_ethics.md`.

## Citation

See `CITATION.cff`.
