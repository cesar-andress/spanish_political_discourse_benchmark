# SPDB Error Taxonomy — Pragmatic Function Confusion Clusters

**Generated:** 2026-06-18 11:20 UTC  
**Gold strategy:** `adjudicated_file`  
**Human corpus:** 10 units (8 with inter-annotator disagreement)  
**Model systems:** `mock_model_pilot`

Automatic taxonomy over predefined near-neighbor PF clusters identified in the SPDB codebook and IberLEF evaluation plan. Inputs: inter-annotator disagreements and model-vs-gold errors.

---

## Table 1. Corpus and error inventory (Scientific Data style)

**Table 1.** Error taxonomy corpus and inventory.

| Quantity | Value |
|----------|------:|
| Annotated units (human) | 10 |
| Units with human PF disagreement | 8 |
| Human label transitions (clustered pairs) | 32 |
| Units evaluated against gold (models) | 10 |
| Model PF errors (all confusions) | 8 |
| Model errors in predefined clusters | 8 |
| Model errors recapitulating human cluster units | 1.000 |

## Table 2. Predefined confusion clusters (LREC style)

**Table 2.** Predefined pragmatic-function confusion clusters and observed frequency.

| Cluster | Description | Human | Model | Combined | Share of clustered errors |
|---------|-------------|------:|------:|---------:|--------------------------:|
| **ATTACK vs DEFENSE** | Oppositional stance boundary between criticizing a target and rebutting criticism. | 8 | 2 | 10 | 25.0% |
| **ADVOCACY vs PROPOSAL** | Policy endorsement vs concrete legislative or programmatic commitment. | 8 | 2 | 10 | 25.0% |
| **APPEAL vs ADVOCACY** | Electoral or mobilizational call vs programmatic support for a policy line. | 8 | 2 | 10 | 25.0% |
| **DEFLECT vs DEFENSE** | Topic shift away from the question vs direct rebuttal of an accusation. | 8 | 2 | 10 | 25.0% |

## Table 3. Directional confusion within clusters

**Table 3.** Directional confusion counts by cluster (gold/reference → predicted/alternate label).

| Cluster | Reference → Alternate | Human | Model | Total |
|---------|----------------------|------:|------:|------:|
| ATTACK vs DEFENSE | `PF_ATTACK` → `PF_DEFENSE` | 4 | 1 | 5 |
|  | `PF_DEFENSE` → `PF_ATTACK` | 4 | 1 | 5 |
| ADVOCACY vs PROPOSAL | `PF_ADVOCACY` → `PF_PROPOSAL` | 4 | 1 | 5 |
|  | `PF_PROPOSAL` → `PF_ADVOCACY` | 4 | 1 | 5 |
| APPEAL vs ADVOCACY | `PF_APPEAL` → `PF_ADVOCACY` | 4 | 1 | 5 |
|  | `PF_ADVOCACY` → `PF_APPEAL` | 4 | 1 | 5 |
| DEFLECT vs DEFENSE | `PF_DEFLECT` → `PF_DEFENSE` | 4 | 1 | 5 |
|  | `PF_DEFENSE` → `PF_DEFLECT` | 4 | 1 | 5 |

## Table 4. Exemplar units by cluster

**Table 4.** Representative units illustrating each confusion cluster.

| Cluster | unit_id | Source | Target | Origin | Text (truncated) |
|---------|---------|--------|--------|--------|------------------|
| ATTACK vs DEFENSE | `u001` | `PF_ATTACK` | `PF_DEFENSE` | human | Critica directa al gobierno por la gestion. |
|  | `u002` | `PF_DEFENSE` | `PF_ATTACK` | human | Replicamos a las acusaciones del grupo rival. |
| ADVOCACY vs PROPOSAL | `u003` | `PF_ADVOCACY` | `PF_PROPOSAL` | human | Apoyamos esta reforma porque mejora la sanidad publica. |
|  | `u004` | `PF_PROPOSAL` | `PF_ADVOCACY` | human | Proponemos aprobar la enmienda antes del pleno. |
| APPEAL vs ADVOCACY | `u005` | `PF_APPEAL` | `PF_ADVOCACY` | human | Pedimos el voto de la ciudadania en las proximas elecciones. |
|  | `u006` | `PF_ADVOCACY` | `PF_APPEAL` | human | Defendemos una politica social mas justa para las familias. |
| DEFLECT vs DEFENSE | `u007` | `PF_DEFLECT` | `PF_DEFENSE` | human | Esa pregunta no corresponde a este punto del orden del dia. |
|  | `u008` | `PF_DEFENSE` | `PF_DEFLECT` | human | Explicamos por que la critica es injusta y fundada. |

## Table 5. Model–human alignment by cluster

**Table 5.** Extent to which model errors concentrate on the same near-neighbor pairs as human annotators.

| Cluster | Human units | Model error units | Overlap units | Model/Human unit ratio |
|---------|------------:|------------------:|--------------:|-----------------------:|
| ATTACK vs DEFENSE | 2 | 2 | 2 | 1.000 |
| ADVOCACY vs PROPOSAL | 2 | 2 | 2 | 1.000 |
| APPEAL vs ADVOCACY | 2 | 2 | 2 | 1.000 |
| DEFLECT vs DEFENSE | 2 | 2 | 2 | 1.000 |

## Cluster reference

The four clusters correspond to codebook near-neighbor boundaries prioritized for adjudication:

- **ATTACK vs DEFENSE** (`PF_ATTACK` ↔ `PF_DEFENSE`): Oppositional stance boundary between criticizing a target and rebutting criticism.
- **ADVOCACY vs PROPOSAL** (`PF_ADVOCACY` ↔ `PF_PROPOSAL`): Policy endorsement vs concrete legislative or programmatic commitment.
- **APPEAL vs ADVOCACY** (`PF_APPEAL` ↔ `PF_ADVOCACY`): Electoral or mobilizational call vs programmatic support for a policy line.
- **DEFLECT vs DEFENSE** (`PF_DEFLECT` ↔ `PF_DEFENSE`): Topic shift away from the question vs direct rebuttal of an accusation.

## Notes

- Human disagreements are extracted from all annotator pairs on units with ≥2 distinct PF labels.
- Model errors use gold labels from the configured strategy and count only mispredictions mapped to a predefined cluster.
- Regenerate with `make error-taxonomy` (production inputs) or `make error-taxonomy-fixtures`.
