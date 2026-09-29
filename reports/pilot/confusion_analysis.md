# Confusion analysis

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
