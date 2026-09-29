# External validation — multilabel metrics

**Framing:** preliminary cross-dataset fallacy projection (not full SPDB validation).

**Dataset:** `fallacyes_political`  
**Model:** `mistral`  
**Evaluated samples:** 1753  
**Label inventory:** 7 SPDB fallacy codes

## Multilabel metrics

| Metric | Value |
|--------|------:|
| Micro Precision | 0.2143 |
| Micro Recall | 0.2365 |
| Micro F1 | 0.2249 |
| Macro Precision | 0.2496 |
| Macro Recall | 0.2039 |
| Macro F1 | 0.1758 |
| Exact Match Ratio | 0.1865 |
| Hamming Loss | 0.2337 |
| Jaccard Similarity | 0.2118 |

## Per-label F1

| Label | Precision | Recall | F1 | Support |
|-------|----------:|-------:|---:|--------:|
| `FAL_ADHOM` | 0.3354 | 0.3670 | 0.3505 | 436 |
| `FAL_STRAW` | 0.2500 | 0.1880 | 0.2146 | 351 |
| `FAL_DILEMMA` | 0.5000 | 0.0276 | 0.0524 | 181 |
| `FAL_SLOPE` | 0.0302 | 0.3043 | 0.0549 | 23 |
| `FAL_EMOTION` | 0.2749 | 0.2768 | 0.2759 | 289 |
| `FAL_GENERAL` | 0.3516 | 0.2238 | 0.2735 | 429 |
| `FAL_WHATABOUT` | 0.0051 | 0.0400 | 0.0090 | 50 |

## Notes

- Predictions are filtered to valid SPDB `FAL_*` labels before scoring.
- Gold labels come from ontology projection in the mapped external dataset.
- Metrics support multi-label predictions (0–3 labels per unit).
