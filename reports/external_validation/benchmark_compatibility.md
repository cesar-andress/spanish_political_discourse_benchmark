# Benchmark Compatibility Matrix

Compatibility of SPDB with external fallacy and persuasion datasets.

**Status:** planning assessment only. No models have been trained or evaluated.

| Dataset | Direct comparison | Transfer learning | External validation | Cross-lingual | Notes |
| --- | --- | --- | --- | --- | --- |
| FallacyES-Political | MEDIUM | HIGH | HIGH | LOW | Same language and political genre, but unit definition differs (debate excerpt vs. SPDB discourse unit) and label granularity differs (16 vs. 7+none). |
| FallacyES | MEDIUM | HIGH | MEDIUM | LOW | Genre shift from news comments / textbook examples to institutional political speech. |
| SemEval-2020 Task 11 (Propaganda Techniques) | LOW | MEDIUM | MEDIUM | MEDIUM | Propaganda techniques are related but not isomorphic to SPDB political-fallacy codes. |
| Argotario | LOW | MEDIUM | MEDIUM | MEDIUM | Informal argument genre; English-only gold. |
| LOGIC / Logical Fallacy Dataset | LOW | MEDIUM | MEDIUM | MEDIUM | Prototypical English examples; not political institutional text. |
| DIPROMATS (IberLEF 2024) | LOW | LOW | LOW | MEDIUM | Task snapshot; label inventory not aligned to SPDB fallacy ontology. |
| Multilingual fallacy benchmarks (LLM evaluation literature) | LOW | MEDIUM | MEDIUM | HIGH | Requires harmonised label projection; no unified Spanish parliamentary benchmark yet. |
| English parliamentary / debate fallacy resources | LOW | MEDIUM | MEDIUM | HIGH | Different legislature and language; institutional genre similarity only. |

## Evaluation questions

| Question | Interpretation |
| --- | --- |
| Can SPDB be compared directly? | Requires harmonised units and label projection;  feasible for FallacyES-Political at MEDIUM, most English sets at LOW. |
| Can transfer learning be tested? | YES for Spanish FallacyES resources (HIGH); English sets at MEDIUM with multilingual models. |
| Can external validation be performed? | Planned after SPDB adjudicated gold exists; FallacyES-Political is the primary candidate (HIGH). |
| Can cross-lingual validation be performed? | MEDIUM--HIGH using English fallacy corpora and projection tables; not a substitute for Spanish human gold. |

## Recommended validation roadmap

1. Phase 0 (current): document inventory, ontology mappings, and compatibility constraints without running external evaluation.
2. Phase 1 (post-pilot): project adjudicated SPDB fallacy labels onto nearest external classes for FallacyES-Political and FallacyES; report label-wise coverage and gaps.
3. Phase 2 (post-pilot): train or fine-tune SPDB fallacy models on external Spanish data and evaluate on held-out SPDB dev units (transfer-in) and vice versa (transfer-out).
4. Phase 3 (scale-up): add cross-lingual checks using English resources (Argotario, LOGIC, SemEval-2020 propaganda) via multilingual encoders; report macro-F1 with harmonised projection tables only.
5. Phase 4 (release): pre-register any schema-repair or label-projection rules before official external-validation numbers are reported.

## Ranking summary (planning)

- **Strongest overall external-validation candidate:** `fallacyes_political` (FallacyES-Political).
- **Strongest cross-lingual planning candidate:** `multifallacy_llm_benchmark` (Multilingual fallacy benchmarks (LLM evaluation literature)).
- **Important constraint:** external validation supports construct positioning; it does not replace SPDB human pilot adjudication.

