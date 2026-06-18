# Datasheet: Spanish Political Discourse Benchmark (SPDB)

**Version:** 0.1.0-dev  
**Status:** under development — dataset **not yet released**  
**Last updated:** 2026-06-18

This datasheet follows the structure of [Gebru et al.](https://arxiv.org/abs/1803.09010) adapted for a political NLP benchmark under construction.

## Motivation

### For what purpose was the dataset created?

SPDB is being created to provide a **persistent, stratified, legally reusable** benchmark of Spanish political discourse with expert annotations for pragmatic function and political fallacies, enabling comparable evaluation of rule-based, classical ML, transformer, and LLM approaches in computational social science.

### Who created the dataset and on behalf of which entity?

| Author | Affiliation |
|--------|-------------|
| Jose Jaime Baena Rojas | Universidad Internacional de La Rioja (UNIR) |
| Daniel Pinto Pajares | Universidad Internacional de La Rioja (UNIR) |
| César Andrés | Universidad Internacional de La Rioja (UNIR) |

Funding and grant identifiers: **planned** (to be added at release).

## Composition

### What do the instances represent?

Each instance is a **discourse unit**: a contiguous span carrying one dominant pragmatic function toward a political target (actor, policy, institution, or electorate).

### What data does each instance consist of?

Text (where redistribution permitted), source metadata, character offsets, token counts, and (when annotated) pragmatic and fallacy labels. Schema: `schemas/discourse_unit.schema.json`.

### How many instances are planned?

| Split | Share | Units @ 8k target |
|-------|-------|-------------------|
| train | 70% | 5,600 |
| dev | 15% | 1,200 |
| test | 15% | 1,200 |

Total annotated core units: **8,000 target**, **5,000 minimum viable** — **not yet available**.

### Source mixture (planned)

60% parliamentary, 12% manifestos, 28% elite social media (IDs-only path where required).

## Collection process

### How was the data associated with each instance acquired?

Through documented ingestion from parliamentary records, MARPOR/manifesto archives, and elite social post IDs—see `docs/dataset_documentation/v1_build_specification.md`. **Collection is in progress; no public JSONL yet.**

### What mechanisms were used for selecting data?

Stratified sampling over `source_type × party_family × temporal_bin` after deduplication (MinHash, threshold 0.85). **Planned.**

## Preprocessing / segmentation

- Unicode NFC normalisation; URL and @-mention masking
- Paragraph- and sentence-aware segmentation; BETO token cap 400
- Character offsets stored per unit

Tooling: `scripts/segmentation/`.

## Distribution

### Will the dataset be distributed? How?

**Planned:** Zenodo DOI + GitHub tag `spdb-v1.0.0`. **Current status: not yet available.**

### License

Annotations: CC BY 4.0 (planned). Code: TBD. Source text: per `license_ref`.

## Maintenance

### Who will be supporting / hosting the dataset?

The author team at UNIR; long-term hosting on Zenodo with GitHub for code and documentation.

### Will the dataset be updated?

Yes. Versioned releases with changelog and concept DOI on Zenodo.

## Known limitations

- Spanish-only in v1; code-switching segments largely excluded
- Social text may not be redistributed in public files
- Experimental labels (semantic vacuity, conceptual anachronism) cover a subset only

## Contact

josejaime.baena@unir.net
