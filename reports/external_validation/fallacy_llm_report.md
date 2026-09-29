# SPDB external fallacy LLM batch report

**Model:** `mock-local`  
**Dataset:** `external_validation/fallacy_sample`  
**Input rows:** 6  
**Output records:** 6  
**Validation status:** OK

## Quality metrics

| Metric | Value |
|--------|------:|
| Valid outputs | 6 |
| Parse failure rate | 0.000 |
| Invalid label rate | 0.000 |
| FAL_NONE rate (explicit none) | 0.167 |
| Average confidence | 0.720 |
| Duplicate row_id | 0 |
| Missing row_id | 0 |

## FAL label distribution

| Label | Count | Share |
|-------|------:|------:|
| `FAL_ADHOM` | 2 | 33.3% |
| `FAL_STRAW` | 2 | 33.3% |
| `FAL_WHATABOUT` | 1 | 16.7% |
| `FAL_EMOTION` | 1 | 16.7% |

## Notes

This report summarizes JSON outputs from the SPDB external fallacy batch pipeline. It does **not** constitute external validation against gold labels.
