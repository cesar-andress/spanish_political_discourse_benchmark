# Data statement: Spanish Political Discourse Benchmark (SPDB)

**Version:** 0.1.0-dev  
**Status:** under development — dataset **not yet released**

Structured data statement following Bender & Friedman (2018) conventions. Fields marked **TBD** will be completed at v1.0.0 release.

## A. Source of language

| Field | Value |
|-------|-------|
| Language variety | Standard Spanish (`es`); institutional and campaign registers |
| Geographic origin | Spain (state + selected autonomous communities) |
| Time period | 2015–2025 (planned); MVP floor 2018–2024 |
| Domains | Parliament, party manifestos, elite social media |

## B. Source of annotations

| Field | Value |
|-------|-------|
| Annotators | Trained project annotators under PI/adjudicator supervision (**planned**) |
| Guidelines | Versioned protocol in `protocol/`; Label Studio config in `annotation/` |
| Double annotation | 20% of core units (planned) |
| Adjudication | PI/lead for disagreements and borderline cases (planned) |
| Inter-annotator agreement | To be reported at release; targets in build spec §9 |

## C. Data composition

| Field | Planned value |
|-------|---------------|
| Total discourse units (annotated) | 8,000 target / 5,000 MVP |
| Train / dev / test | 70% / 15% / 15% |
| Label sets | 8 PF + 7 fallacies + experimental SV/CA |
| Empty or missing text | Social slice may ship empty `text` with IDs only |

## D. Preprocessing and segmentation

Discourse units segmented with paragraph-aware, Spanish sentence-boundary rules; max 400 BETO tokens per unit; min 20 / max 2,000 characters. See `scripts/segmentation/` and build spec §2.

## E. Distribution and access

| Field | Status |
|-------|--------|
| Public download | **Not yet available** |
| Zenodo DOI | **Not yet available** |
| Rehydration required | Yes, for social slice (planned) |

## F. Legal and ethical considerations

Public political speech; platform ToS govern social text. IDs-only release where redistribution is restricted. See `docs/ethics.md`.

## G. Provisional citation

```text
Baena Rojas, J. J., Pinto Pajares, D., & Andrés, C. (2026).
Spanish Political Discourse Benchmark (SPDB) [under development; v0.1.0-dev].
Universidad Internacional de La Rioja (UNIR).
```

Machine-readable: `CITATION.cff`.

## H. Maintainer contact

josejaime.baena@unir.net
