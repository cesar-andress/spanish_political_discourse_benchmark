# Pilot 001 — reliability metrics and go/no-go criteria

## Primary research question

Can trained annotators apply the SPDB v1 **pragmatic-function ontology** with sufficient agreement on real parliamentary discourse units?

Secondary (exploratory in this pilot): fallacy multi-labeling, semantic vacuity, and conceptual anachronism.

## Metrics

| Metric | Scope | Rationale |
|--------|-------|-----------|
| **Cohen's κ** | Pairwise, per label dimension | Standard for two-rater nominal agreement on the same fixed set of units |
| **Krippendorff's α** | Multi-rater / missing data | Robust when adjudication or partial overlap is introduced later |

Compute κ and α **separately** for:

1. `pragmatic_function` (primary gate)
2. `fallacy_labels` (set overlap or exact-match variant — document choice in analysis notebook)
3. `semantic_vacuity` (experimental)
4. `conceptual_anachronism` (experimental)

## Target values

| Tier | Cohen's κ | Krippendorff's α | Interpretation |
|------|-----------|------------------|----------------|
| **Excellent** | ≥ 0.80 | ≥ 0.80 | Ontology and guidelines ready for scaled annotation |
| **Acceptable** | ≥ 0.67 | ≥ 0.67 | Proceed with guideline revisions and adjudication rules documented |
| **Needs revision** | < 0.67 | < 0.67 | Halt scaled annotation; revise ontology, definitions, or training |

## Go / no-go decision rules

### Go (scale to full SPDB annotation)

All of the following:

- Pragmatic function κ ≥ **0.67** on the pilot sample (n = 100 double-coded units).
- Pragmatic function α ≥ **0.67** if more than two coders contribute.
- Borderline / `PF_*` unclear cases ≤ **5%** of units (per v1 spec expectation).
- Adjudication resolves ≥ **90%** of pragmatic-function disagreements without ontology change.

### Conditional go

- Pragmatic function κ in **[0.67, 0.80)** → revise guidelines, add 2–3 worked examples, re-pilot on 30 units before full scale.
- Fallacy κ < 0.67 → pragmatic function may still proceed; fallacy arm deferred or simplified.

### No-go

Any of the following:

- Pragmatic function κ < **0.67**.
- Systematic confusion between two label pairs in > **10%** of disagreements (signals ontology merge/split needed).
- Median annotation time > **6 min/unit** without quality gain (guidelines too heavy for throughput).

## Reporting checklist

- [ ] Pairwise κ matrix (annotators × dimensions)
- [ ] α with 95% bootstrap CI
- [ ] Confusion matrix for `pragmatic_function`
- [ ] Disagreement rate and adjudication outcome summary from `disagreement_log.csv`
- [ ] Written go/no-go recommendation signed by PI
