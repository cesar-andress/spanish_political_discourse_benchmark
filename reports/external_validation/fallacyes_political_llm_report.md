# FallacyES-Political — preliminary cross-dataset fallacy projection

**Framing:** external compatibility analysis / preliminary cross-dataset fallacy projection. This is **not** full SPDB validation, **not** human validation, and **does not** modify the SPDB ontology.

**Model:** `mistral`  
**Source dataset:** [FallacyES-Political](https://zenodo.org/records/14836328)  
**Ingested records:** 1954  
**Mapped records:** 1954  
**LLM predictions:** 1954  

## Dataset ingestion

- Official source: https://zenodo.org/records/14836328
- Normalized JSONL: `data/external/fallacyes_political/fallacyes_political.jsonl`
- Records ingested: 1954

## SPDB label projection (FallacyES-Political → SPDB)

- Mapping coverage (rows with ≥1 projected SPDB label): **89.8%** (1754/1954)

| Mapping type | Count | Share |
|--------------|------:|------:|
| exact | 1052 | 53.8% |
| partial | 283 | 14.5% |
| approximate | 419 | 21.4% |
| none | 200 | 10.2% |

## LLM batch quality (SPDB JSON schema)

| Metric | Value |
|--------|------:|
| Valid outputs | 1931 |
| Parse failure rate | 0.001 |
| Invalid label rate | 0.011 |
| FAL_NONE rate (`fallacy_none_explicit=true`) | 0.024 |
| Average confidence | 0.837 |

## SPDB fallacy label distribution (LLM predictions)

| Label | Count | Share |
|-------|------:|------:|
| `FAL_ADHOM` | 507 | 23.4% |
| `FAL_WHATABOUT` | 475 | 21.9% |
| `FAL_EMOTION` | 312 | 14.4% |
| `FAL_GENERAL` | 296 | 13.7% |
| `FAL_STRAW` | 294 | 13.6% |
| `FAL_SLOPE` | 249 | 11.5% |
| `FAL_DILEMMA` | 10 | 0.5% |
| `FAL_NONE` | 6 | 0.3% |
| `FAL_HYPocrisy` | 3 | 0.1% |
| `FAL_HYPOCRISY` | 2 | 0.1% |
| `FAL_COMPARE` | 2 | 0.1% |
| `FAL_CONTRADICTION` | 1 | 0.0% |
| `FAL_FLATTERY` | 1 | 0.0% |
| `FAL_BINARY` | 1 | 0.0% |
| `FAL_HYPOCrisy` | 1 | 0.0% |
| `FAL_REPETITION` | 1 | 0.0% |
| `FAL_MISLEAD` | 1 | 0.0% |
| `FAL_CONFLICT` | 1 | 0.0% |
| `FAL_INCONSISTENCY` | 1 | 0.0% |
| `FAL_SLOGAN` | 1 | 0.0% |

## Comparison against projected labels (exact + partial mappings only)

- Comparable rows: 1334
- Any-label overlap rate: **24.9%**
- Primary projected-label match rate: **24.9%**

Comparison is indicative only: FallacyES-Political spans, label granularity, and debate genre differ from SPDB discourse units. Multi-label and approximate mappings are excluded from strict comparison.

## Limitations

- FallacyES-Political annotates debate excerpts with 16+ fallacy types; SPDB uses seven political fallacy codes plus explicit none.
- Not all external labels project onto SPDB (`none` and unmapped classes remain).
- Zero-shot LLM projection is not calibrated against SPDB gold and must not be read as benchmark accuracy.
- Debate transcripts ≠ parliamentary plenary units; register and interaction context differ.
- No human adjudication was performed for this compatibility run.

## Validation notes

- line 15 (fep_1993-05-24_0015): fallacy_labels: invalid label(s) ['FAL_CONTRADICTION']
- line 158 (fep_2011-11-07_0158): fallacy_labels: invalid label(s) ['FAL_FLATTERY']
- line 239 (fep_2016-06-13_0239): fallacy_labels: invalid label(s) ['FAL_BINARY']
- line 275 (fep_2016-06-13_0275): fallacy_labels must not contain FAL_NONE
- line 275 (fep_2016-06-13_0275): fallacy_labels: invalid label(s) ['FAL_NONE']
- line 275 (fep_2016-06-13_0275): fallacy_none_explicit must be false when fallacy_labels is non-empty
- line 322 (fep_2019-04-20_0322): fallacy_labels: invalid label(s) ['FAL_HYPocrisy']
- line 337 (fep_2019-04-20_0337): fallacy_labels: invalid label(s) ['FAL_HYPOCrisy']
- line 609 (fep_2019-11-04_0609): fallacy_labels must not contain FAL_NONE
- line 609 (fep_2019-11-04_0609): fallacy_labels: invalid label(s) ['FAL_NONE']
- line 609 (fep_2019-11-04_0609): fallacy_none_explicit must be false when fallacy_labels is non-empty
- line 614 (fep_2019-11-04_0614): fallacy_labels: invalid label(s) ['FAL_REPETITION']
- line 710 (fep_2023-07-10_0710): fallacy_labels must not contain FAL_NONE
- line 710 (fep_2023-07-10_0710): fallacy_labels: invalid label(s) ['FAL_NONE']
- line 710 (fep_2023-07-10_0710): fallacy_none_explicit must be false when fallacy_labels is non-empty
- line 712 (fep_2023-07-10_0712): fallacy_labels must not contain FAL_NONE
- line 712 (fep_2023-07-10_0712): fallacy_labels: invalid label(s) ['FAL_NONE']
- line 712 (fep_2023-07-10_0712): fallacy_none_explicit must be false when fallacy_labels is non-empty
- line 737 (fep_2023-07-13_0737): fallacy_labels: invalid label(s) ['FAL_MISLEAD']
- line 784 (fep_2023-07-19_0784): fallacy_labels: invalid label(s) ['FAL_HYPocrisy']
