# Pilot annotation round 001

## Purpose

Round 001 is a **human reliability pilot** for the Spanish Political Discourse Benchmark (SPDB). It tests whether annotators can consistently apply the v1 pragmatic-function ontology — and related label sets — on real parliamentary text before scaling annotation to the full corpus.

Success criteria and thresholds are defined in `annotation/pilot_001/pilot_metrics.md`.

## Sample source

| Field | Value |
|-------|-------|
| **Corpus layer** | Parliamentary (ParlaMint-ES) |
| **Processed file** | `data/processed/parlamint_100_units.jsonl` |
| **Selection** | 100 discourse units, stable random sample (`seed=42`) from segmented ParlaMint sessions |
| **Provenance** | See `docs/sources/parlamint.md`; `provenance.license_status = to_be_verified` |
| **Pilot export** | `annotation/pilot_001/pilot_100_units.csv` |

Units retain SPDB pipeline fields (`unit_id`, segmented `text`, speaker metadata, session `date`). Annotation columns start empty for double coding.

## Package contents

```
annotation/pilot_001/
  pilot_100_units.csv      # annotation worksheet
  pilot_protocol.md        # instructions and workflow
  pilot_metrics.md         # κ / α targets and go/no-go rules
  disagreement_log.csv       # disagreement tracker (header only)
  results/                 # agreement analysis outputs (see results/README.md)
```

## Expected outcomes

1. **Reliability estimate** for `pragmatic_function` (primary): Cohen's κ and Krippendorff's α with tiered interpretation (excellent ≥ 0.80, acceptable ≥ 0.67, needs revision < 0.67).
2. **Guideline feedback** — confusing label pairs, missing definitions, or excessive borderline cases.
3. **Throughput estimate** — median minutes per unit to plan full annotation budget.
4. **Go/no-go decision** — proceed to scaled SPDB annotation, conditional revision re-pilot, or ontology redesign.

Negative outcomes (κ < 0.67 on pragmatic function) are valuable: they prevent expensive full-corpus annotation on an unreliable schema.

## Related documentation

- `annotation/labelstudio/instructions.md` — full Label Studio ontology reference
- `labels/*.tsv` — label definitions
- `docs/sources/parlamint.md` — upstream corpus notes
