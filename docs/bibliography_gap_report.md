# Bibliography gap report — SPDB paper (p01)

**Date:** 2026-06-18  
**Manuscript:** `paper/sections/{01_introduction,02_related_work,03_dataset_design}.tex`  
**Shared bibliography:** `papers_unir/bibliography.bib` (symlinked from `paper/main.tex` as `../../bibliography.bib`)

## Summary

| Metric | Before | After |
|--------|--------|-------|
| Active `\citep{placeholder_*}` in manuscript | ~86 key uses across 27 placeholder types | **0** |
| Placeholder types still cited in body text | 27 | **0** |
| Verified bibliographic entries used | 15 | **37** |
| New real entries added to `bibliography.bib` | — | **12** |

**Target:** fewer than five placeholder citations remaining — **met** (zero in running text).

## New bibliographic entries added

| Key | Role in manuscript |
|-----|-------------------|
| `salganik2021bit` | Computational social science / digital research methods |
| `gebru2021datasheets` | Dataset documentation and datasheets |
| `wilkinson2016fair` | FAIR data principles and versioning |
| `zimmer2018address` | Social-media research ethics |
| `fiesler2018no` | Platform policies and user narratives |
| `gorman2019we` | Train/dev/test splits and leakage hygiene |
| `settles2009active` | Active learning for annotation sampling |
| `zenodo2013` | Zenodo archiving |
| `jurafsky2023speech` | Text normalisation and NLP preprocessing |
| `king1995replication` | Reproducible social-science research |
| `rodriguez2022sentimps` | SentiMP-Sp (Spanish MP sentiment) |
| `senado2024proceedings` | Senado de España proceedings portal |

## Placeholder → replacement mapping

| Former placeholder key | Replacement key(s) | Primary sections |
|------------------------|-------------------|------------------|
| `placeholder_css_benchmarking` | `salganik2021bit`, `mohammad2016semeval` | §1, §2 |
| `placeholder_data_statements` | `gebru2021datasheets` | §1, §3 |
| `placeholder_political_nlp` | `pang2008sentiment`, `garciadiaz2023politices`, `mohammad2016semeval`; SentiMP → `rodriguez2022sentimps` | §1, §2 |
| `placeholder_argument_mining` | `habernal2017argmin`, `habernal2017argotario` | §1, §2, §3 |
| `placeholder_spanish_politics_media` | `sanchez2020twitter10n`, `garciadiaz2023politices` | §1, §2, §3 |
| `placeholder_nlp_splits` | `gorman2019we` | §2, §3 |
| `placeholder_social_media_research_ethics` | `zimmer2018address`, `fiesler2018no` | §2, §3 |
| `placeholder_platform_tos` | `zimmer2018address`, `fiesler2018no` | §2, §3 |
| `placeholder_pragmatics_political_discourse` | `vandijk1997discourse`, `reinig2024politicswords` | §1, §2, §3 |
| `placeholder_argumentation_discourse` | `habernal2017argmin`, `cominetti2024impaqts` | §1, §2, §3 |
| `placeholder_spanish_language_models` | `canete2020beto` | §1, §2, §3 |
| `placeholder_congreso_es` | `erjavec2023parlamint` | §1, §2, §3 |
| `placeholder_senado_es` | `senado2024proceedings` | §2, §3 |
| `placeholder_europarl` | `koehn2005europarl` | §1, §2, §3 |
| `placeholder_marpor` | `volkens2020manifesto` | §1, §2 |
| `placeholder_elite_social_media_css` | `sanchez2020twitter10n` | §1, §2, §3 |
| `placeholder_multilingual_political_text` | `koehn2005europarl`, `erjavec2023parlamint` | §1, §2, §3 |
| `placeholder_reproducible_css` | `salganik2021bit`, `king1995replication` | §1, §2, §3 |
| `placeholder_beto` | `canete2020beto` | §3 |
| `placeholder_text_normalisation_nlp` | `jurafsky2023speech` | §3 |
| `placeholder_zenodo_social_data` | `zenodo2013`, `zimmer2018address` | §3 |
| `placeholder_active_learning_nlp` | `settles2009active` | §3 |
| `placeholder_benchmark_leakage` | `gorman2019we` | §2, §3 |
| `placeholder_zenodo` | `zenodo2013`, `wilkinson2016fair` | §3 |
| `placeholder_fair_datasets` | `wilkinson2016fair` | §1, §2, §3 |
| `placeholder_corpus_licensing` | `erjavec2023parlamint`, `gebru2021datasheets` | §1, §3 |
| `placeholder_evaluation_campaigns` | `chiruzzo2024iberlef`, `mohammad2016semeval` | §1, §2, §3 |
| `placeholder_dataset_versioning` | `zenodo2013`, `wilkinson2016fair` | §1, §2, §3 |

## Orphaned placeholder records in `bibliography.bib`

Twenty-eight `@misc{placeholder_*}` stubs remain in the shared bibliography file. They are **no longer cited** by the SPDB manuscript and can be deleted in a future bibliography cleanup pass without affecting `make pdf`.

## Residual gaps (optional future citations)

These topics are not yet cited in the manuscript but may warrant dedicated entries if expanded in later sections (baselines, discussion, LLM evaluation):

1. **DIPROMATS task paper** — IberLEF 2024 propaganda task (overview currently via `chiruzzo2024iberlef` only).
2. **Spanish sentiment shared tasks** — e.g. InterTASS / TASS (for contrast with SentiMP-Sp).
3. **LLM evaluation for discourse** — when §6–§8 baseline results are written.
4. **Semantic change in political lexicon** — if diachronic analysis is expanded beyond design prose.
5. **Democratic deliberation / normative political theory** — if discussion section engages normative literature directly.

None of these use `placeholder_*` keys in the current manuscript.

## Build verification

```bash
cd paper && make pdf
```

Compiles successfully with `pdflatex` + `bibtex`; no undefined citation warnings for placeholder keys.

## Maintenance notes

- Keep `bibliography.bib` as the single source of truth under `papers_unir/`.
- When adding §5–§10 content, prefer existing verified keys before introducing new stubs.
- Remove unused `placeholder_*` BibTeX entries once all papers in the monorepo are migrated.
