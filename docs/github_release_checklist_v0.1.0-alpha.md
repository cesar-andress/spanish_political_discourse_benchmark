# GitHub release checklist — v0.1.0-alpha

Use this checklist when creating the GitHub Release. **Do not run until maintainers approve publication.**

## Pre-flight (local)

- [ ] Branch `main` is clean and up to date with intended release commit
- [ ] `make test` passes
- [ ] `make release-validate` passes (metadata, manifest, checksums, sample counts)
- [ ] [`docs/release_notes_v0.1.0-alpha.md`](release_notes_v0.1.0-alpha.md) reviewed
- [ ] [`CITATION.cff`](../CITATION.cff) version is `0.1.0-alpha`
- [ ] [`.zenodo.json`](../.zenodo.json) version is `0.1.0-alpha`
- [ ] LICENSE text finalized (currently under review)
- [ ] No secrets or local paths in committed files

## Tag

- [ ] Create annotated tag: `v0.1.0-alpha`
- [ ] Tag points to the release commit on `main`
- [ ] Push tag: `git push origin v0.1.0-alpha`

```bash
git tag -a v0.1.0-alpha -m "SPDB v0.1.0-alpha: guidelines, schemas, pipeline docs, 100-unit pilot sample"
git push origin v0.1.0-alpha
```

## GitHub Release (draft first)

- [ ] Open **Releases → Draft a new release**
- [ ] Choose tag: `v0.1.0-alpha`
- [ ] Title: `v0.1.0-alpha — Alpha release (guidelines + pilot sample)`
- [ ] Mark as **pre-release**
- [ ] Paste release body from [`release_notes_v0.1.0-alpha.md`](release_notes_v0.1.0-alpha.md) (Summary + Included + Not included)
- [ ] Attach optional assets (if desired):
  - [ ] `releases/v0.1.0-alpha/samples/parlamint_100_units.jsonl`
  - [ ] `releases/v0.1.0-alpha/samples/pilot_100_units.csv`
  - [ ] `annotation/codebook/SPDB_Codebook_v1.pdf`
- [ ] Review diff of tag vs previous tag
- [ ] **Publish** only after final approval

## Post-release

- [ ] Update README badge / status line if DOI is added later
- [ ] Sync [`zenodo/releases/v0.1.0-alpha/`](../zenodo/releases/v0.1.0-alpha/) if Zenodo deposit follows
- [ ] Announce alpha scope clearly (no gold annotations, not for benchmark numbers)
- [ ] Open follow-up issues for v0.2.0 / v1.0.0 milestones

## Zenodo (optional, separate step)

- [ ] Connect GitHub repo to Zenodo (if not already)
- [ ] Trigger deposit for tag `v0.1.0-alpha` or upload tarball
- [ ] Copy DOI into `CITATION.cff`, README, and release notes
- [ ] Re-run `make release-validate` after DOI fields are added

## Rollback

If the release was published prematurely:

- [ ] Unpublish or mark GitHub pre-release as withdrawn with explanation
- [ ] Do not delete tags without team agreement (prefer new corrective tag)
- [ ] Do not mint conflicting Zenodo versions for the same tag
