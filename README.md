# Spanish Political Discourse Benchmark (SPDB)

[![Version](https://img.shields.io/badge/version-v0.1.0--alpha-orange)](docs/release_notes_v0.1.0-alpha.md)
[![License](https://img.shields.io/badge/license-TBD-lightgrey)](LICENSE)

Multilayer annotated corpus of Spanish political discourse for computational pragmatics, argumentation analysis, and semantic drift research.

**Current release:** [`v0.1.0-alpha`](docs/release_notes_v0.1.0-alpha.md) — alpha documentation and an unannotated 100-unit pilot sample. **Not a gold benchmark release.**

## What is in v0.1.0-alpha

| Component | Location |
|-----------|----------|
| Annotation guidelines | [`annotation/guidelines/`](annotation/guidelines/) |
| Codebook v1 | [`annotation/codebook/SPDB_Codebook_v1.md`](annotation/codebook/SPDB_Codebook_v1.md) |
| JSON schemas | [`schemas/`](schemas/) |
| Label inventories | [`labels/`](labels/) |
| Ingestion pipeline | [`docs/pipeline.md`](docs/pipeline.md), [`scripts/`](scripts/) |
| 100-unit pilot sample | [`releases/v0.1.0-alpha/samples/`](releases/v0.1.0-alpha/samples/) |

## Quick start

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
make test
make release-validate
```

Inspect the pilot sample:

```bash
head -n 1 releases/v0.1.0-alpha/samples/parlamint_100_units.jsonl | python -m json.tool
```

Regenerate the sample from ParlaMint (requires processed pool):

```bash
make parlamint-100
```

## Repository layout

```
annotation/     Guidelines, codebook, Label Studio config, pilot protocol
docs/           Pipeline, workflow, release notes
labels/         Ontology TSV inventories
schemas/        JSON Schema for discourse units and pipeline output
scripts/        Ingestion, segmentation, validation
releases/       Versioned release bundles (samples + manifest)
data/           Local processed data (gitignored; see data/processed/README.md)
```

## Citation

See [`CITATION.cff`](CITATION.cff). A Zenodo DOI will be added when a stable release is deposited.

## License

Dataset and annotation guidelines: intended **CC BY 4.0** (see codebook). Repository code license under review — see [`LICENSE`](LICENSE).

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Annotation changes require codebook and schema updates.

## Links

- Release notes: [`docs/release_notes_v0.1.0-alpha.md`](docs/release_notes_v0.1.0-alpha.md)
- GitHub release checklist: [`docs/github_release_checklist_v0.1.0-alpha.md`](docs/github_release_checklist_v0.1.0-alpha.md)
- Repository: https://github.com/cesar-andress/spanish_political_discourse_benchmark
