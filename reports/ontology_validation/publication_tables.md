# Publication tables — SPDB pragmatic-function ontology validation

Draft tables formatted for *Language Resources and Evaluation* (LREC) and *Scientific Data* submissions.

## Table 1. Pilot corpus and annotation design (Scientific Data style)

**Table 1.** SPDB pilot ontology-validation corpus.

| Attribute | Value |
|-----------|-------|
| Discourse units | 24 |
| Annotators | 3 |
| Primary ontology | 8-class pragmatic function (`PF_*`) |
| Annotation status | `complete` |
| Ontology decision | PASS |

## Table 2. Overall inter-annotator reliability (LREC style)

**Table 2.** Overall reliability for pragmatic-function labels (nominal metrics with 95% bootstrap CI, 2,000 resamples).

| Metric | Estimate | 95% CI |
|--------|---------:|--------|
| Krippendorff α | 0.797 | [0.633, 0.935] |
| Fleiss κ | 0.793 | [0.626, 0.934] |
| Gwet AC1 | 0.794 | [0.644, 0.937] |

## Table 3. Per-class reliability and support

**Table 3.** One-vs-rest reliability by pragmatic-function label.

| Label | Support | κ (1 vs rest) | α (1 vs rest) | PSA |
|-------|--------:|--------------:|--------------:|----:|
| `PF_ADVOCACY` | 8 | 0.852 | 0.854 | 0.778 |
| `PF_ATTACK` | 10 | 0.667 | 0.672 | 0.467 |
| `PF_DEFENSE` | 10 | 0.667 | 0.672 | 0.467 |
| `PF_PROPOSAL` | 8 | 0.725 | 0.730 | 0.500 |
| `PF_APPEAL` | 8 | 0.852 | 0.854 | 0.778 |
| `PF_INFO` | 9 | 0.745 | 0.748 | 0.583 |
| `PF_DEFLECT` | 9 | 1.000 | 1.000 | 1.000 |
| `PF_PROCEDURAL` | 10 | 0.889 | 0.891 | 0.750 |

## Table 4. Dominant-function audit and disagreement structure

**Table 4.** Single-dominant-function audit metrics and leading confusion pairs.

| Metric | Value |
|--------|------:|
| Unanimous rate | 0.750 |
| Majority rate | 0.958 |
| Full-split rate | 0.042 |
| Borderline rate | 0.125 |
| Mean vote entropy | 0.178 |

| Top confusion pair | Count | Mass |
|--------------------|------:|-----:|
| `PF_ADVOCACY` → `PF_PROPOSAL` | 2 | 0.154 |
