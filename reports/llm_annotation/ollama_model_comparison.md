# Ollama multi-model comparison

> **Note:** This is not human validation. It measures model convergence and disagreement only.

Models compared: 3
Units compared: 5

## Pragmatic function consensus

| Metric | Value |
|--------|------:|
| Unanimous agreement rate | 0.4000 |
| Majority agreement rate | 0.8000 |
| Full disagreement rate | 0.2000 |
| Mean vote entropy | 0.4743 |
| Krippendorff α | 0.4440 |

## Fallacy-label convergence

| Krippendorff α (fallacy signature) | 0.1176 |

## Per-model pragmatic-function distribution

### `model_alpha`

| Label | Count |
|-------|------:|
| `PF_ADVOCACY` | 1 |
| `PF_ATTACK` | 2 |
| `PF_INFO` | 1 |
| `PF_PROCEDURAL` | 1 |

### `model_beta`

| Label | Count |
|-------|------:|
| `PF_ADVOCACY` | 2 |
| `PF_ATTACK` | 2 |
| `PF_INFO` | 1 |

### `model_gamma`

| Label | Count |
|-------|------:|
| `PF_ATTACK` | 1 |
| `PF_DEFENSE` | 2 |
| `PF_INFO` | 1 |
| `PF_PROCEDURAL` | 1 |

## Pairwise pragmatic-function agreement

| Model A | Model B | Observed agreement | Cohen κ | Units |
|---------|---------|-------------------:|--------:|------:|
| `model_alpha` | `model_beta` | 0.6000 | 0.4444 | 5 |
| `model_alpha` | `model_gamma` | 0.6000 | 0.5238 | 5 |
| `model_beta` | `model_gamma` | 0.4000 | 0.3182 | 5 |

## Top pragmatic-function disagreement pairs

| From | To | Count | Mass |
|------|----|------:|-----:|
| `PF_ADVOCACY` | `PF_DEFENSE` | 3 | 0.429 |
| `PF_ATTACK` | `PF_ADVOCACY` | 1 | 0.143 |
| `PF_ATTACK` | `PF_DEFENSE` | 1 | 0.143 |
| `PF_ATTACK` | `PF_PROCEDURAL` | 1 | 0.143 |
| `PF_PROCEDURAL` | `PF_ATTACK` | 1 | 0.143 |

## Units with maximum pragmatic-function disagreement

| unit_id | entropy | labels |
|---------|--------:|--------|
| `u003` | 1.0986 | `PF_ATTACK|PF_ADVOCACY|PF_DEFENSE` |

## Parse-failure rates

- `model_alpha`: 0.000
- `model_beta`: 0.000
- `model_gamma`: 0.000
