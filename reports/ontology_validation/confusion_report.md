# Disagreement structure — pragmatic function ontology

**Status:** `complete`

## Aggregated 8×8 confusion matrix

Rows and columns index annotator label pairs (A→B) aggregated across all annotator pairs.

| A \ B | `PF_ADVOCACY` | `PF_APPEAL` | `PF_ATTACK` | `PF_DEFENSE` | `PF_DEFLECT` | `PF_INFO` | `PF_PROCEDURAL` | `PF_PROPOSAL` |
|-------|---:|---:|---:|---:|---:|---:|---:|---:|
| `PF_ADVOCACY` | 7 | 0 | 0 | 0 | 0 | 0 | 0 | 2 |
| `PF_APPEAL` | 0 | 7 | 2 | 0 | 0 | 0 | 0 | 0 |
| `PF_ATTACK` | 0 | 0 | 7 | 2 | 0 | 0 | 0 | 0 |
| `PF_DEFENSE` | 0 | 0 | 2 | 7 | 0 | 0 | 0 | 0 |
| `PF_DEFLECT` | 0 | 0 | 0 | 0 | 9 | 0 | 0 | 0 |
| `PF_INFO` | 0 | 0 | 0 | 2 | 0 | 7 | 1 | 0 |
| `PF_PROCEDURAL` | 0 | 0 | 0 | 0 | 0 | 0 | 9 | 0 |
| `PF_PROPOSAL` | 0 | 0 | 0 | 0 | 0 | 1 | 1 | 6 |

## Top confusion pairs

| From | To | Count | Disagreement mass |
|------|----|------:|------------------:|
| `PF_ADVOCACY` | `PF_PROPOSAL` | 2 | 0.154 |
| `PF_APPEAL` | `PF_ATTACK` | 2 | 0.154 |
| `PF_ATTACK` | `PF_DEFENSE` | 2 | 0.154 |
| `PF_DEFENSE` | `PF_ATTACK` | 2 | 0.154 |
| `PF_INFO` | `PF_DEFENSE` | 2 | 0.154 |
| `PF_INFO` | `PF_PROCEDURAL` | 1 | 0.077 |
| `PF_PROPOSAL` | `PF_INFO` | 1 | 0.077 |
| `PF_PROPOSAL` | `PF_PROCEDURAL` | 1 | 0.077 |

## Symmetry analysis

- Symmetric mass: 2
- Asymmetric mass: 9
- Symmetry ratio: 0.18181818181818182

## Disagreement concentration

| unit_id | labels | unique_labels | party |
|---------|--------|--------------:|-------|
| `u020` | `PF_PROPOSAL|PF_INFO|PF_PROCEDURAL` | 3 | PSOE |
| `u017` | `PF_ATTACK|PF_ATTACK|PF_DEFENSE` | 2 | VOX |
| `u018` | `PF_DEFENSE|PF_DEFENSE|PF_ATTACK` | 2 | ERC |
| `u019` | `PF_ADVOCACY|PF_ADVOCACY|PF_PROPOSAL` | 2 | PP |
| `u021` | `PF_APPEAL|PF_APPEAL|PF_ATTACK` | 2 | Cs |
| `u022` | `PF_INFO|PF_INFO|PF_DEFENSE` | 2 | UP |

![Confusion heatmap](figures/ontology_validation/confusion_heatmap.png)

