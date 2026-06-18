# SPDB pilot annotation report

**Generated:** 2026-06-18 10:54 UTC  
**Random seed:** 42  
**Annotation status:** `pending`  
**Template:** `annotation/pilot_001/pilot_100_units.csv`  
**Annotators:** `pending`  
**Units in scope:** 100

## Executive summary

Pre-annotation mode: pilot units and ontology inventories are loaded, but human labels have not been submitted yet. Agreement and confusion sections will populate automatically once annotator CSV files are available.

## 1. Agreement analysis

_Agreement metrics pending: no filled annotation labels were found._

## 2. Confusion analysis

_Confusion analysis pending: no filled annotation labels were found._

## 3. Ontology diagnostics

| Dimension | Observed assignments | Entropy | Max class share | Imbalance |
|-----------|---------------------:|--------:|----------------:|-----------|
| `pragmatic_function` | 0 | 2.0794 | 0.000 | pending |
| `fallacy_labels` | 0 | 2.0794 | 0.000 | pending |
| `semantic_vacuity` | 0 | 1.0986 | 0.000 | pending |
| `conceptual_anachronism` | 0 | 1.0986 | 0.000 | pending |

_Ontology diagnostics are in pre-annotation mode: inventories are loaded, but observed support counts are zero until labels are submitted._

### Class support — `pragmatic_function`

| Label | Observed count | Inventory |
|-------|---------------:|:---------:|
| `PF_ADVOCACY` | 0 | yes |
| `PF_ATTACK` | 0 | yes |
| `PF_DEFENSE` | 0 | yes |
| `PF_PROPOSAL` | 0 | yes |
| `PF_APPEAL` | 0 | yes |
| `PF_INFO` | 0 | yes |
| `PF_DEFLECT` | 0 | yes |
| `PF_PROCEDURAL` | 0 | yes |

### Class support — `fallacy_labels`

| Label | Observed count | Inventory |
|-------|---------------:|:---------:|
| `FAL_ADHOM` | 0 | yes |
| `FAL_STRAW` | 0 | yes |
| `FAL_DILEMMA` | 0 | yes |
| `FAL_SLOPE` | 0 | yes |
| `FAL_EMOTION` | 0 | yes |
| `FAL_GENERAL` | 0 | yes |
| `FAL_WHATABOUT` | 0 | yes |
| `FAL_NONE` | 0 | yes |

### Class support — `semantic_vacuity`

| Label | Observed count | Inventory |
|-------|---------------:|:---------:|
| `SV_0` | 0 | yes |
| `SV_1` | 0 | yes |
| `SV_UNCLEAR` | 0 | yes |

### Class support — `conceptual_anachronism`

| Label | Observed count | Inventory |
|-------|---------------:|:---------:|
| `CA_0` | 0 | yes |
| `CA_1` | 0 | yes |
| `CA_UNCLEAR` | 0 | yes |

## Reproducibility

Re-run the full pipeline with:

```bash
make pilot-analytics PILOT_TEMPLATE=annotation/pilot_001/pilot_100_units.csv
```

Intermediate artefacts are written to `reports/pilot/`.
