# Release checklist (p01)

Operational checklists for SPDB releases.

## v0.1.0-alpha (current)

Use the dedicated GitHub release checklist:

- [`docs/github_release_checklist_v0.1.0-alpha.md`](../github_release_checklist_v0.1.0-alpha.md)
- Release notes: [`docs/release_notes_v0.1.0-alpha.md`](../release_notes_v0.1.0-alpha.md)
- Local validation: `make release-validate`

## Future stable releases (v1.0.0+)

### Dataset bundle

- Annotated train / dev / test JSONL with checksums
- Version tag and [`releases/`](../../releases/) manifest

### Documentation

- Datasheet, data statement, rehydration instructions complete
- Changelog and CITATION.cff DOI fields updated

### Baselines & code

- Rule-based and LLM baseline artifacts
- Reproducibility scripts pinned in `environment/`

### Archiving

- Zenodo metadata (`.zenodo.json`), DOI, README cross-links
- GitHub Release assets aligned with Zenodo deposit
