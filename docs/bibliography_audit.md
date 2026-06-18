# Bibliography audit — SPDB paper (p01)

**Audit date:** 2026-06-18  
**Scope:** All `\input{}` sections, appendices, and tables in `paper/main.tex`  
**Bibliography:** `papers_unir/bibliography.bib` (shared; referenced as `../../bibliography.bib`)

## Executive summary

| Check | Result |
|-------|--------|
| `\cite*` keys matching `placeholder_*` in manuscript | **0** |
| `@misc{placeholder_*}` stubs in `bibliography.bib` | **0** (28 removed) |
| Peer-reviewed sources added in this audit | **9** |
| Grey-literature keys still cited (non-placeholder) | **4** (see §Residual grey literature) |
| Sections without citations (stub TODO) | §5–§8, §9–§10, appendices |

**Target:** fewer than five placeholder citations remaining — **met** (zero placeholders in manuscript and bibliography).

---

## Manuscript coverage by section

| Section | File | Citations | Placeholder status |
|---------|------|-----------|-------------------|
| Abstract | `00_abstract.tex` | 0 | N/A (no `\cite`) |
| Introduction | `01_introduction.tex` | 28+ | Resolved |
| Related work | `02_related_work.tex` | 45+ | Resolved |
| Dataset design | `03_dataset_design.tex` | 35+ | Resolved |
| Corpus exploration | `03b_corpus_exploration.tex` | 1 | Resolved |
| Annotation scheme | `04_annotation_scheme.tex` | 8 | Resolved (+ methodology cites added) |
| Human annotation | `05_human_annotation.tex` | 0 | Stub; cite `artstein2008inter`, `krippendorff2018content` when written |
| Baseline models | `06_baseline_models.tex` | 0 | Stub; cite `canete2020beto`, `wang2019glue` when written |
| Evaluation protocol | `07_evaluation_protocol.tex` | 0 | Stub; cite `mohammad2016semeval`, `gorman2019we` when written |
| Results / Discussion / Conclusion | `08`–`10` | 0 | Stub |
| Benchmark table | `tables/benchmark_comparison.tex` | 7 | Resolved |
| Appendices A–D | `appendices/*.tex` | 0 | Stub |

---

## Placeholder → replacement registry

Each row lists the former `placeholder_*` key, the peer-reviewed (or standard reference) replacement, and the rationale grouped by audit priority.

### Priority 1 — Computational Social Science benchmarks

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_css_benchmarking` | `salganik2021bit`; `wang2019glue`; `mohammad2016semeval`; `lazer2014parable` | CSS/digital-methods framing; NLP benchmark culture (SuperGLUE); shared-task evaluation precedent; methodological caution on big-data inference |
| `placeholder_reproducible_css` | `salganik2021bit`; `king1995replication` | Reproducible social research workflow and replication norms |
| `placeholder_evaluation_campaigns` | `chiruzzo2024iberlef`; `mohammad2016semeval` | Iberian evaluation forum; stance-detection campaign template |
| `placeholder_benchmark_leakage` | `gorman2019we` | Standard splits and leakage in NLP evaluation |
| `placeholder_nlp_splits` | `gorman2019we` | Document-level split hygiene for benchmark design |

### Priority 2 — FAIR datasets

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_fair_datasets` | `wilkinson2016fair` | FAIR guiding principles for scientific data stewardship |
| `placeholder_data_statements` | `gebru2021datasheets` | Dataset documentation and transparency (datasheets) |
| `placeholder_dataset_versioning` | `zenodo2013`; `wilkinson2016fair` | Persistent archiving and versioned release (repository + FAIR) |
| `placeholder_zenodo` | `zenodo2013`; `wilkinson2016fair` | Zenodo deposit architecture for benchmark bundle |
| `placeholder_zenodo_social_data` | `zenodo2013`; `zimmer2018address` | Identifier-only social data release under platform constraints |
| `placeholder_corpus_licensing` | `erjavec2023parlamint`; `gebru2021datasheets` | Corpus redistribution terms and provenance documentation |

### Priority 3 — Political communication

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_spanish_politics_media` | `sanchez2020twitter10n`; `garciadiaz2023politices`; `entman1993framing` | Spanish election Twitter corpus; IberLEF political NLP; framing theory in mediated politics |
| `placeholder_elite_social_media_css` | `sanchez2020twitter10n`; `antypas2022negativity` | Elite social-media corpora; peer-reviewed MP Twitter sentiment study |
| `placeholder_political_nlp` | `pang2008sentiment`; `garciadiaz2023politices`; `mohammad2016semeval`; SentiMP → `rodriguez2022sentimps`, `antypas2022negativity` | Sentiment/stance paradigm; Spanish political shared tasks; adjudicated MP sentiment dataset |

### Priority 4 — Pragmatics

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_pragmatics_political_discourse` | `vandijk1997discourse`; `searle1969speech`; `reinig2024politicswords` | Discourse structure; speech-act theory; contemporary parliamentary speech-act annotation |
| `placeholder_congreso_es` | `erjavec2023parlamint` | ParlaMint-ES harmonised Congreso proceedings |
| `placeholder_senado_es` | `senado2024proceedings` | Official Senate proceedings portal (institutional source; grey literature) |
| `placeholder_multilingual_political_text` | `koehn2005europarl`; `erjavec2023parlamint` | Multilingual legislative corpora for cross-lingual political text |

### Priority 5 — Argumentation theory

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_argument_mining` | `habernal2017argmin`; `habernal2017argotario` | Argument-mining survey; fallacy annotation in user-generated argumentation |
| `placeholder_argumentation_discourse` | `habernal2017argmin`; `cominetti2024impaqts`; `vaneemeren2015handbook` | Argument structure in discourse; implicit strategies in political speech; argumentation theory handbook |

### Priority 6 — Annotation methodology

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| *(new in §4)* | `artstein2008inter`; `krippendorff2018content` | Inter-annotator agreement in NLP; content-analysis reliability for adjudication |
| `placeholder_active_learning_nlp` | `settles2009active` | Active learning for annotation pool sampling |

### Priority 7 — Dataset papers

| Placeholder | Replacement citation | Reason |
|-------------|---------------------|--------|
| `placeholder_marpor` | `volkens2020manifesto` | Manifesto Project programmatic text infrastructure |
| `placeholder_europarl` | `koehn2005europarl` | Europarl parallel legislative corpus |
| `placeholder_beto` / `placeholder_spanish_language_models` | `canete2020beto` | Spanish BERT baseline and tokenizer alignment |
| `placeholder_text_normalisation_nlp` | `jurafsky2023speech` | Standard NLP text-processing reference |
| `placeholder_social_media_research_ethics` | `zimmer2018address`; `fiesler2018no` | Social-media research ethics; platform policy narratives |
| `placeholder_platform_tos` | `zimmer2018address`; `fiesler2018no` | Terms-of-service constraints on redistribution |

---

## New peer-reviewed entries (2026-06-18 audit)

| Key | Venue | Priority domain |
|-----|-------|-----------------|
| `lazer2014parable` | *Science* | CSS benchmarks / big-data pitfalls |
| `wang2019glue` | NeurIPS (SuperGLUE) | NLP benchmark culture |
| `entman1993framing` | *Journal of Communication* | Political communication |
| `searle1969speech` | CUP book | Pragmatics / speech acts |
| `vaneemeren2015handbook` | Springer handbook | Argumentation theory |
| `artstein2008inter` | *Computational Linguistics* | Annotation methodology |
| `krippendorff2018content` | Sage (4th ed.) | Annotation reliability |
| `antypas2022negativity` | *Online Social Networks and Media* | Spanish MP Twitter / dataset context |

---

## Residual grey literature (not placeholders)

These keys remain cited but are **not** peer-reviewed journal/conference papers. Acceptable as infrastructure or dataset pointers; upgrade when formal publications exist.

| Key | Type | Used for |
|-----|------|----------|
| `zenodo2013` | Repository website | Zenodo archiving |
| `senado2024proceedings` | Institutional portal | Senate proceedings access |
| `rodriguez2022sentimps` | Hugging Face dataset card | SentiMP-Sp adjudicated labels |
| `jurafsky2023speech` | Draft textbook (online) | Text normalisation conventions |

---

## Recommended citations when stub sections are written

| Section | Suggested keys |
|---------|----------------|
| §5 Human annotation | `artstein2008inter`, `krippendorff2018content`, `settles2009active` |
| §6 Baselines | `canete2020beto`, `wang2019glue`, `pang2008sentiment` |
| §7 Evaluation | `mohammad2016semeval`, `gorman2019we`, `chiruzzo2024iberlef` |
| §9 Discussion | `lazer2014parable`, `entman1993framing`, `vaneemeren2015handbook` |

Do **not** reintroduce `placeholder_*` keys; add verified BibTeX entries to `bibliography.bib` instead.

---

## Build verification

```bash
cd paper && make pdf
```

Last verified: 2026-06-18 — compiles with `pdflatex` + `bibtex`; no undefined `placeholder_*` citations.

---

## Maintenance

- Supersedes `docs/bibliography_gap_report.md` (initial 2026-06-18 pass).
- Prune duplicate consecutive keys in `\citep{}` during section drafting.
- When §5–§8 are written, extend this audit with section-level citation maps.
