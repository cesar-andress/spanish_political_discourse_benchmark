# Contributing

**Status:** under development (`v0.1.0-dev`)

Thank you for your interest in SPDB. The benchmark is under active construction; contribution guidelines will tighten before v1.0.0.

## Ways to contribute

- **Issues:** Bug reports, documentation gaps, schema clarifications
- **Pull requests:** Small, focused changes to scripts, schemas, docs, or tests
- **Annotation:** Coordinated with the PI team only during pilot/production waves—not open crowdsourcing in v1

## Workflow

1. Fork the repository (or branch within the team org).
2. Create a descriptive branch, e.g. `fix/segmentation-offsets` or `docs/datasheet-motivation`.
3. Keep PRs scoped; avoid unrelated refactors.
4. Run tests for touched pipeline code:

   ```bash
   PYTHONPATH=. python3.11 -m pytest scripts/ingestion/tests/ scripts/segmentation/tests/
   ```

5. Do **not** commit large data files, credentials, or manuscript LaTeX.

## Standards

- **Python:** ≥3.11; match existing style in `scripts/`
- **Data:** JSONL UTF-8; validate against `schemas/discourse_unit.schema.json`
- **Labels:** Update `labels/*.tsv` and Label Studio config together
- **Docs:** Mark unfinished features as *planned* or *not yet available*

## What we cannot accept

- Fake or synthetic annotated data presented as gold labels
- Bulk scraped social-media text violating platform ToS
- LaTeX manuscripts or private paper drafts in this public repository

## Code of conduct

See [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

## Contact

[Daniel Pinto Pajares](mailto:daniel.pinto@unir.net) (tooling) or [Jose Jaime Baena Rojas](mailto:josejaime.baena@unir.net) (project direction).
