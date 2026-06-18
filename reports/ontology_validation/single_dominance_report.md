# Single-dominant-function audit

**Status:** `complete`

## Aggregate rates

| Metric | Value | Pilot threshold |
|--------|------:|-----------------|
| Unanimous rate | 0.7500 | — |
| Majority rate | 0.9583 | — |
| Full-split rate (3 distinct labels) | 0.0417 | ≤ 0.20 |
| Mean vote entropy | 0.1784 | — |
| Borderline rate | 0.1250 | ≤ 0.25 |
| Second-choice usage rate | 0.0833 | — |

## Entropy distribution

| Entropy (rounded) | Units |
|------------------|------:|
| 0.00 | 18 |
| 0.64 | 5 |
| 1.10 | 1 |

## Unit-level audit (first 20 rows)

| unit_id | votes | entropy | borderline | second_choice |
|---------|-------|--------:|------------|---------------|
| `u001` | `PF_ATTACK|PF_ATTACK|PF_ATTACK` | 0.000 | `||` | `||` |
| `u002` | `PF_DEFENSE|PF_DEFENSE|PF_DEFENSE` | 0.000 | `||` | `||` |
| `u003` | `PF_ADVOCACY|PF_ADVOCACY|PF_ADVOCACY` | 0.000 | `||` | `||` |
| `u004` | `PF_PROPOSAL|PF_PROPOSAL|PF_PROPOSAL` | 0.000 | `||` | `||` |
| `u005` | `PF_APPEAL|PF_APPEAL|PF_APPEAL` | 0.000 | `||` | `||` |
| `u006` | `PF_INFO|PF_INFO|PF_INFO` | 0.000 | `||` | `||` |
| `u007` | `PF_DEFLECT|PF_DEFLECT|PF_DEFLECT` | 0.000 | `||` | `||` |
| `u008` | `PF_PROCEDURAL|PF_PROCEDURAL|PF_PROCEDURAL` | 0.000 | `||` | `||` |
| `u009` | `PF_ATTACK|PF_ATTACK|PF_ATTACK` | 0.000 | `||` | `||` |
| `u010` | `PF_DEFENSE|PF_DEFENSE|PF_DEFENSE` | 0.000 | `||` | `||` |
| `u011` | `PF_ADVOCACY|PF_ADVOCACY|PF_ADVOCACY` | 0.000 | `||` | `||` |
| `u012` | `PF_PROPOSAL|PF_PROPOSAL|PF_PROPOSAL` | 0.000 | `||` | `||` |
| `u013` | `PF_APPEAL|PF_APPEAL|PF_APPEAL` | 0.000 | `||` | `||` |
| `u014` | `PF_INFO|PF_INFO|PF_INFO` | 0.000 | `||` | `||` |
| `u015` | `PF_DEFLECT|PF_DEFLECT|PF_DEFLECT` | 0.000 | `||` | `||` |
| `u016` | `PF_PROCEDURAL|PF_PROCEDURAL|PF_PROCEDURAL` | 0.000 | `||` | `||` |
| `u017` | `PF_ATTACK|PF_ATTACK|PF_DEFENSE` | 0.637 | `||` | `||PF_ATTACK` |
| `u018` | `PF_DEFENSE|PF_DEFENSE|PF_ATTACK` | 0.637 | `||` | `||` |
| `u019` | `PF_ADVOCACY|PF_ADVOCACY|PF_PROPOSAL` | 0.637 | `||true` | `||` |
| `u020` | `PF_PROPOSAL|PF_INFO|PF_PROCEDURAL` | 1.099 | `||` | `||` |
