# SPDB pilot annotation report

**Generated:** 2026-09-29 09:22 UTC  
**Random seed:** 42  
**Annotation status:** `partial`  
**Template:** `annotation/pilot_001/pilot_100_units.csv`  
**Annotators:** `pilot_100_units_annotator_a`, `pilot_100_units_annotator_b`  
**Units in scope:** 100

## Executive summary

Pragmatic-function Fleiss κ = 0.219 (Krippendorff α = 0.223). 65 / 100 units show cross-annotator disagreement. Primary ontology imbalance assessment: `balanced`.

## 1. Agreement analysis

| Dimension | Units | Fleiss κ | Krippendorff α | Mean pairwise κ |
|-----------|------:|---------:|---------------:|----------------:|
| `pragmatic_function` | 100 | 0.2187 | 0.2227 | 0.2350 |

### Per-class agreement — `pragmatic_function`

| Label | Units with label | Unanimous units | Unanimous rate |
|-------|-----------------:|----------------:|---------------:|
| `PF_ADVOCACY` | 28 | 6 | 0.2143 |
| `PF_APPEAL` | 16 | 3 | 0.1875 |
| `PF_ATTACK` | 26 | 3 | 0.1154 |
| `PF_DEFENSE` | 12 | 0 | 0.0000 |
| `PF_DEFLECT` | 4 | 0 | 0.0000 |
| `PF_INFO` | 24 | 1 | 0.0417 |
| `PF_PROCEDURAL` | 36 | 20 | 0.5556 |
| `PF_PROPOSAL` | 19 | 2 | 0.1053 |

## 2. Confusion analysis

| Dimension | Pairwise comparisons | Dominant off-diagonal pair | Count |
|-----------|---------------------:|----------------------------|------:|
| `pragmatic_function` | 100 | `PF_PROCEDURAL` → `PF_INFO` | 11 |

### Confusion matrix — `pragmatic_function`

| A \ B | `PF_ADVOCACY` | `PF_APPEAL` | `PF_ATTACK` | `PF_DEFENSE` | `PF_DEFLECT` | `PF_INFO` | `PF_PROCEDURAL` | `PF_PROPOSAL` |
|-------|---:|---:|---:|---:|---:|---:|---:|---:|
| `PF_ADVOCACY` | 6 | 1 | 0 | 1 | 1 | 4 | 0 | 1 |
| `PF_APPEAL` | 2 | 3 | 0 | 0 | 0 | 0 | 0 | 2 |
| `PF_ATTACK` | 5 | 5 | 3 | 2 | 2 | 1 | 1 | 2 |
| `PF_DEFENSE` | 3 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| `PF_DEFLECT` | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `PF_INFO` | 0 | 0 | 1 | 2 | 0 | 1 | 0 | 0 |
| `PF_PROCEDURAL` | 1 | 0 | 1 | 0 | 0 | 11 | 20 | 1 |
| `PF_PROPOSAL` | 3 | 2 | 2 | 0 | 0 | 3 | 1 | 2 |

## Disagreement concentration

**Units with any disagreement:** 65 / 100

| unit_id | speaker_party | changed_columns | disagreement_count |
|---------|---------------|-----------------|-------------------:|
| `spdb-v1-unassigned-783020218722` | Cs | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-7bc5528e899b` | EAJPNV | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-eb453642ca5f` | EAJPNV | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-b57f53b63185` | ERCCATSÍ | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-05d607df9c93` | non_partisan | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-35a6117f0c82` | PSOE | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-483e95cc103b` | EAJPNV | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-082ee9dc9ec7` | PSOE | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-60dd3e86e761` | PP | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-af494fedf1eb` | non_partisan | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-f4efaf8c67ab` | non_partisan | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-91b87988aed6` | Cs | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-6d6700eea2a4` | ECUP | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-dff8b57dc1a6` | Cs | `pragmatic_function` | 1 |
| `spdb-v1-unassigned-1b02f725631c` | ECP | `pragmatic_function` | 1 |

| Figure | Path |
|--------|------|
| Confusion heatmap | `figures/pilot/confusion_pragmatic_function.png` |


## 3. Ontology diagnostics

| Dimension | Observed assignments | Entropy | Max class share | Imbalance |
|-----------|---------------------:|--------:|----------------:|-----------|
| `pragmatic_function` | 200 | 1.9049 | 0.280 | balanced |
| `fallacy_labels` | 0 | 2.0794 | 0.000 | pending |
| `semantic_vacuity` | 0 | 1.0986 | 0.000 | pending |
| `conceptual_anachronism` | 0 | 1.0986 | 0.000 | pending |

### Class support — `pragmatic_function`

| Label | Observed count | Inventory |
|-------|---------------:|:---------:|
| `PF_ADVOCACY` | 34 | yes |
| `PF_ATTACK` | 29 | yes |
| `PF_DEFENSE` | 12 | yes |
| `PF_PROPOSAL` | 21 | yes |
| `PF_APPEAL` | 19 | yes |
| `PF_INFO` | 25 | yes |
| `PF_DEFLECT` | 4 | yes |
| `PF_PROCEDURAL` | 56 | yes |

### Dominant confusion pairs — `pragmatic_function`

| From | To | Count |
|------|----|------:|
| `PF_PROCEDURAL` | `PF_INFO` | 11 |
| `PF_ATTACK` | `PF_ADVOCACY` | 5 |
| `PF_ATTACK` | `PF_APPEAL` | 5 |
| `PF_ADVOCACY` | `PF_INFO` | 4 |
| `PF_DEFENSE` | `PF_ADVOCACY` | 3 |
| `PF_PROPOSAL` | `PF_ADVOCACY` | 3 |
| `PF_PROPOSAL` | `PF_INFO` | 3 |
| `PF_APPEAL` | `PF_ADVOCACY` | 2 |
| `PF_APPEAL` | `PF_PROPOSAL` | 2 |
| `PF_ATTACK` | `PF_DEFENSE` | 2 |

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
make pilot-analytics PILOT_TEMPLATE=annotation/pilot_001/pilot_100_units.csv PILOT_ANNOTATOR_1=annotation/pilot_001/pilot_100_units_annotator_a.csv PILOT_ANNOTATOR_2=annotation/pilot_001/pilot_100_units_annotator_b.csv
```

Intermediate artefacts are written to `reports/pilot/`.
