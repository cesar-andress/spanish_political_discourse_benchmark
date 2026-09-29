# Ontology diagnostics

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
