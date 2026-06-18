# Pilot 001 — annotation protocol

**Package:** `annotation/pilot_001/`  
**Sample:** `pilot_100_units.csv` (100 units from `data/processed/parlamint_100_units.jsonl`)  
**Ontology:** `labels/pragmatic_functions.tsv`, `labels/fallacies.tsv`, `labels/semantic_vacuity.tsv`, `labels/conceptual_anachronism.tsv`  
**Reference UI spec:** `annotation/labelstudio/instructions.md`

---

## 1. Objective

Test whether the SPDB v1 pragmatic-function ontology is **operational and reliable** on real Spanish parliamentary discourse before committing to full-scale annotation.

Specifically:

1. Measure inter-annotator agreement on `pragmatic_function` (primary).
2. Collect preliminary disagreement patterns for fallacies and experimental labels.
3. Estimate per-unit annotation time and guideline clarity.

This pilot is **not** a benchmark release. Outputs inform ontology and protocol revisions only.

---

## 2. Annotators and design

- **Design:** double independent coding on all 100 units (annotator A and annotator B).
- **Blinding:** annotators do not see each other's labels during primary coding.
- **Language:** unit text is Spanish; label IDs are English (`PF_*`, `FAL_*`, etc.).
- **Training:** complete Label Studio instructions (§4–§7) and label one shared practice batch of 5 units (excluded from κ) before the pilot CSV.

---

## 3. Annotation instructions

Work **row by row** in `pilot_100_units.csv`. Read `text` plus metadata (`speaker_name`, `speaker_party`, `date`) for context only — labels apply to the unit span, not the speaker's entire career.

### 3.1 Pragmatic function (required)

- **Column:** `pragmatic_function`
- **Cardinality:** exactly **one** label ID (`PF_ADVOCACY`, `PF_ATTACK`, `PF_DEFENSE`, `PF_PROPOSAL`, `PF_APPEAL`, `PF_INFO`, `PF_DEFLECT`, `PF_PROCEDURAL`).
- **Rule:** mutually exclusive primary function directed at the main political target in the span.
- **Borderline:** if genuinely tied, choose the best single label and note `borderline` in personal notes (do not add columns).

### 3.2 Fallacies (required)

- **Column:** `fallacy_labels`
- **Cardinality:** up to **three** salient fallacy IDs, pipe-separated (e.g. `FAL_ADHOM|FAL_WHATABOUT`), or `FAL_NONE` when no fallacy is present.
- **Rule:** label only what is explicit in the span; do not infer intent beyond minimal context.

### 3.3 Experimental labels (required for this pilot)

- **Columns:** `semantic_vacuity`, `conceptual_anachronism`
- **Values:** one ID each from the respective TSV files (`SV_0` / `SV_1` / `SV_UNCLEAR`; `CA_0` / `CA_1` / `CA_UNCLEAR`).
- Use `*_UNCLEAR` sparingly (< 3% of units).

### 3.4 Quality checks before saving a row

- No empty required fields.
- `pragmatic_function` is a single valid `PF_*` ID.
- `fallacy_labels` is either `FAL_NONE` or a pipe-separated list of `FAL_*` (max 3, no mix with `FAL_NONE`).

---

## 4. Estimated time

| Phase | Per unit | Total (100 units) |
|-------|----------|-------------------|
| Reading + primary labels | 2.5–4 min | ~4–7 h per annotator |
| Shared calibration (5 practice units) | — | ~45 min (once) |
| Adjudication (PI / lead) | 3–5 min | ~1–2 h (≈15–25 disagreements expected) |

**Pilot wall-clock:** plan **one working day per annotator** for primary coding plus **half a day** for reconciliation.

---

## 5. Disagreement recording procedure

1. After both annotators submit, run a diff on `pragmatic_function` and `fallacy_labels`.
2. For each disagreement, append one row to `disagreement_log.csv`:
   - `unit_id` — from the CSV
   - `annotator_a`, `annotator_b` — label values or annotator IDs
   - `disagreement_type` — e.g. `pragmatic_function`, `fallacy_labels`, `semantic_vacuity`, `conceptual_anachronism`, `multi`
   - `notes` — brief rationale from each side or adjudicator summary
3. **Pragmatic-function disagreements** → mandatory adjudication; gold label recorded in notes as `gold:PF_*`.
4. **Fallacy disagreements** → adjudicate if pragmatic function already agreed; otherwise batch for weekly review.
5. Log **all** pragmatic-function disagreements even if later resolved by quick call.
6. Compute κ / α per `pilot_metrics.md` before go/no-go meeting.

---

## 6. Deliverables

| File | Owner | When |
|------|-------|------|
| `pilot_100_units.csv` (filled) | Each annotator | End of primary pass |
| `disagreement_log.csv` | PI / lead | Within 48 h of primary merge |
| Go/no-go memo | PI | Within 1 week, citing `pilot_metrics.md` thresholds |
