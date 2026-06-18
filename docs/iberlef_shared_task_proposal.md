# IberLEF shared task proposal: SPDB (Spanish Political Discourse Benchmark)

**Status:** Draft proposal (pre-submission)  
**Campaign name (proposed):** *SPDB@IberLEF* — Pragmatic Function and Political Fallacy Detection in Spanish Political Discourse  
**Dataset:** [Spanish Political Discourse Benchmark (SPDB)](dataset_documentation/v1_build_specification.md)  
**Target edition:** IberLEF 2027 (contingent on SPDB v1.0.0 release and organiser acceptance)  
**Contact (proposed):** Jose Jaime Baena Rojas — [josejaime.baena@unir.net](mailto:josejaime.baena@unir.net)

---

## 1. Overview

We propose a three-track shared task built on **SPDB**, a stratified benchmark of Spanish political discourse units annotated for **pragmatic function** (single-label) and **political fallacies** (multi-label). Participants will receive train/dev splits with gold labels, a **locked test set** without labels, and IberLEF-compatible TSV exports. Evaluation will run on a hosted leaderboard with published baseline implementations.

| Track | Task | Label type | Primary metric |
|-------|------|------------|----------------|
| **A** | Pragmatic function classification | Single-label (8 classes) | Macro-F1 |
| **B** | Political fallacy detection | Multi-label (7 + explicit none) | Macro-F1 (label-wise) |
| **C** | Multi-task prediction | PF + fallacies jointly | Macro average of Track A and B primary metrics |

Tracks A and B are **independent** official rankings. Track C rewards systems that perform well on **both** layers without task-specific ensembling beyond a single model or unified pipeline.

---

## 2. Motivation

### 2.1 Scientific gap

Spanish political NLP has strong shared-task activity (e.g., PoliticES, DIPROMATS at IberLEF) and durable corpora (ParlaMint-ES, MARPOR), yet no Iberian benchmark jointly supervises:

1. **Illocutionary / pragmatic function** at discourse-unit granularity (advocacy, attack, defense, proposal, appeal, information, deflection, procedural).
2. **Political fallacies** on the **same spans** under a reduced, reliability-oriented inventory.
3. **Multi-register coverage** — parliamentary speech, party manifestos, and elite social media — under one ontology and split protocol.

Topic, sentiment, and stance resources answer *what* is discussed and *how* actors evaluate targets; they under-specify *what communicative move* a span performs. Argument-mining and English fallacy corpora rarely combine institutional pragmatic coding with Spanish elite registers.

### 2.2 Why IberLEF

IberLEF is the established evaluation forum for Spanish and Iberian languages. Hosting SPDB at IberLEF would:

- Standardise metrics and submission formats across research groups.
- Accelerate adoption of pragmatic–argumentative layers in Spanish political NLP.
- Provide a reproducible comparison point for transformer and LLM systems on register-shifted political text.
- Complement (not replace) existing IberLEF political tasks by fixing a **persistent** train/dev/test harness linked to Zenodo.

### 2.3 Expected impact

- **Political communication:** Descriptive studies of pragmatic moves and fallacy rates by party, period, and register.
- **NLP:** Hard multi-class and multi-label baselines for Spanish BERT-family models and open LLMs.
- **CSS:** Leakage-safe, document-grouped splits for credible generalisation claims.

---

## 3. Task definition

### 3.1 Input

Each instance is a **discourse unit**: a contiguous Spanish text span with metadata (`source_type`, `party_family`, `date`, speaker fields where licensed). Units are drawn from:

| Register | Target share (SPDB v1) |
|----------|------------------------|
| Parliamentary | 60% |
| Party manifestos | 12% |
| Elite social media | 28% |

Social-media instances may require **local rehydration** from post IDs where platform terms restrict text redistribution; annotations and IDs will always be provided.

### 3.2 Track A — Pragmatic function classification

**Goal:** Predict exactly one pragmatic-function label per unit.

| Label ID | Name |
|----------|------|
| `PF_ADVOCACY` | Policy advocacy |
| `PF_ATTACK` | Position attack |
| `PF_DEFENSE` | Defense / rebuttal |
| `PF_PROPOSAL` | Proposal / commitment |
| `PF_APPEAL` | Mobilization appeal |
| `PF_INFO` | Informational |
| `PF_DEFLECT` | Deflection / evasion |
| `PF_PROCEDURAL` | Ritual / procedural |

Definitions and worked examples: [`labels/pragmatic_functions.tsv`](../labels/pragmatic_functions.tsv), [`annotation/guidelines/pragmatic_function_examples.md`](../annotation/guidelines/pragmatic_function_examples.md).

### 3.3 Track B — Political fallacy detection

**Goal:** Predict a set of fallacy labels present in the span (maximum three), or explicit **none**.

| Label ID | Name |
|----------|------|
| `FAL_ADHOM` | Ad hominem |
| `FAL_STRAW` | Straw man / distortion |
| `FAL_DILEMMA` | False dilemma |
| `FAL_SLOPE` | Slippery slope |
| `FAL_EMOTION` | Appeal to emotion / fear |
| `FAL_GENERAL` | Hasty generalization |
| `FAL_WHATABOUT` | Whataboutism / tu quoque |
| *(none)* | Empty set + `fallacy_none_explicit=true` |

Definitions: [`labels/fallacies.tsv`](../labels/fallacies.tsv). Fallacy labels are **independent** of pragmatic function (e.g., evidence-based attack without ad hominem).

### 3.4 Track C — Multi-task prediction

**Goal:** Submit **both** Track A and Track B predictions from a **single unified system** (one checkpoint, one pipeline, or one LLM prompt producing both outputs). Allowed:

- Shared encoder with task-specific heads.
- Single LLM call returning JSON with `pragmatic_function` and `fallacy_labels`.

**Not allowed for Track C official ranking:**

- Training separate models per track and merging predictions post hoc.
- Using gold Track A labels as input features for Track B (or vice versa) at test time.

Track C ranking uses the **combined score** (§5.3). Teams may still compete in A and B separately with task-specific systems.

---

## 4. Data and release format

### 4.1 Splits (planned SPDB v1)

| Split | Share | Units @ 8k target | Labels released |
|-------|------:|------------------:|-----------------|
| Train | 70% | 5,600 | Gold |
| Dev | 15% | 1,200 | Gold |
| Test | 15% | 1,200 | **Withheld** (organisers only) |

**Leakage controls:** document-level grouping; social-account grouping; stratification of `source_type`, `party_family`, and temporal bin within ±2% across splits.

### 4.2 IberLEF export package (proposed)

| File | Description |
|------|-------------|
| `spdb_train.tsv` | `id`, `text`, `label_pf`, `labels_fal`, metadata columns |
| `spdb_dev.tsv` | Same schema |
| `spdb_test.tsv` | `id`, `text`, metadata only |
| `label_inventory.tsv` | Label IDs, names, definitions |
| `README_iberlef.md` | Download, rehydration, submission format |
| `test_manifest.sha256` | Locked test ID list (published after campaign close) |

Fallacy column `labels_fal`: pipe-separated sorted `FAL_*` IDs, or empty for none.

### 4.3 Prerequisites

Shared task launch requires:

- SPDB v1.0.0 public release (Zenodo DOI + GitHub tag `spdb-v1.0.0`).
- Inter-annotator agreement meeting MVP thresholds on pragmatic function (see [`annotation/pilot_001/pilot_metrics.md`](../annotation/pilot_001/pilot_metrics.md)).
- Signed licence matrix for upstream text ([`docs/dataset_documentation/licensing_and_ethics.md`](dataset_documentation/licensing_and_ethics.md)).

---

## 5. Evaluation

### 5.1 Submission format

One zip per team per track (or one zip for Track C covering both tasks):

```text
team_id_track_a.zip
  predictions.tsv    # columns: id, label_pf
team_id_track_b.zip
  predictions.tsv    # columns: id, labels_fal
team_id_track_c.zip
  predictions.tsv    # columns: id, label_pf, labels_fal
```

Validation script: `scripts/validation/validate_submission.py` (to be added before campaign open).

### 5.2 Track metrics

| Track | Primary | Secondary (reported) |
|-------|---------|----------------------|
| **A** | **Macro-F1** over `PF_*` | Accuracy; per-class F1 |
| **B** | **Macro-F1** (label-wise, 7 fallacy labels) | Micro-F1; sample-wise F1; exact-set match |
| **C** | **Combined = (macro-F1_A + macro-F1_B) / 2** | Same secondaries as A and B |

Macro-F1 for Track B treats each `FAL_*` as a binary label (presence/absence). Explicit none is correct when both gold and prediction are empty sets.

### 5.3 Tie-breaking

1. Higher Track C combined score (Track C only).
2. Higher Track A macro-F1.
3. Higher Track B macro-F1.
4. Earlier valid submission timestamp.

### 5.4 Post-hoc analysis (not for ranking)

- Per-register breakdown (parliamentary / manifesto / social).
- Per-class confusion matrices (published for dev; summary for test after campaign).
- Parsing failure rate for LLM submissions (reported; systems with &gt;5% unparseable dev outputs may be marked exploratory).

---

## 6. Leaderboard design

### 6.1 Platform

**Primary:** CodaLab / Codabench competition bundle (hidden test, automatic scoring).  
**Mirror:** `results/metrics/spdb_iberlef_leaderboard.csv` in the SPDB repository (updated after evaluation window closes).

### 6.2 Leaderboard views

| View | Tracks | Sort key |
|------|--------|----------|
| Official — Pragmatic function | A | macro-F1 (PF) |
| Official — Fallacies | B | macro-F1 (fallacy) |
| Official — Multi-task | C | combined score |
| Exploratory — LLM non-repro | A, B, C | Marked `non_reproducible` |
| Exploratory — Register slice | A, B | Dev-only during campaign |

### 6.3 Submission rules

- **Dev:** Unlimited submissions; scores visible immediately (for debugging).
- **Test:** Maximum **three** submissions per team per track during the test phase; best test score counts.
- **Open resources:** External data and pre-trained models allowed if documented in the system description paper.
- **Prohibited:** Manual annotation of test set; use of test labels for training or guideline iteration; sharing test predictions before deadline.

### 6.4 Baseline row policy

Organiser baselines (§7) appear as `SPDB-org-*` on each leaderboard. Participant systems must beat the **BETO fine-tuned** baseline on at least one primary metric to be highlighted in the overview paper (soft expectation, not eligibility gate).

---

## 7. Baseline models

Organisers will ship reproducible baselines and pre-computed dev predictions. All baselines use the **same label inventories** as participants.

| Tier | Model | Track A | Track B | Track C | Notes |
|------|-------|---------|---------|---------|-------|
| B0 | Majority / prior | ✓ | ✓ | ✓ | Train-set majority class; per-label fallacy threshold |
| B1 | Rule-based | ✓ | partial | partial | [`code/src/discourse_classifier/`](../code/src/discourse_classifier/) heuristics |
| B2 | TF–IDF + linear | ✓ | ✓ | ✓ | One-vs-rest for fallacies |
| B3 | BETO fine-tuned | ✓ | ✓ | ✓ | `dccuchile/bert-base-spanish-wwm-cased`; multi-head for C |
| B4 | Open LLM | ✓ | ✓ | ✓ | Pinned checkpoint; JSON-only prompts; 3-seed vote |

**B3 training defaults (organiser baseline):** 3 epochs max; early stopping on dev macro-F1 (A) / micro-F1 (B); batch 16; lr 2e-5.  
**B4:** Fixed prompts from `protocol/llm_prompt_registry.md`; temperature 0; parsing failures logged.

Optional **non-reproducible** row: one proprietary API model for comparison only (excluded from official winner selection).

---

## 8. Timeline (proposed)

Assumes IberLEF **2027** campaign; shift all dates ±1 year if SPDB v1.0.0 slips.

| Phase | Window | Milestone |
|-------|--------|-----------|
| **T0 — Dataset lock** | Sep 2026 | SPDB v1.0.0 Zenodo release; test IDs frozen |
| **T1 — Pilot task pack** | Oct 2026 | Dev-only CodaLab sandbox; baseline B0–B2 |
| **T2 — Proposal submission** | Nov 2026 | IberLEF task proposal to SEPLN organisers |
| **T3 — Train/dev release** | Jan 2027 | Public train/dev TSV + BETO baseline; task website live |
| **T4 — Registration** | Jan–Feb 2027 | Team registration; starter kit + evaluation script |
| **T5 — Development** | Feb–Apr 2027 | Unlimited dev submissions; optional mid-campaign webinar |
| **T6 — Test phase** | May 2027 | Test texts released; ≤3 submissions/team/track |
| **T7 — Evaluation freeze** | May 2027 | Leaderboard sealed; error analysis begins |
| **T8 — IberLEF workshop** | Sep 2027 | Results session at IberLEF / SEPLN; overview paper |
| **T9 — Post-campaign** | Oct 2027 | Test labels + per-class analysis published; v1.1 export fixes |

If SPDB MVP (5k units) ships without full 8k target, the shared task may launch with documented scale reduction; combined Track C remains unchanged.

---

## 9. Organiser responsibilities

| Item | Owner |
|------|-------|
| Dataset release & licence audit | SPDB PI / data steward |
| Annotation guidelines & adjudication log | Lead annotator |
| Baseline code & configs | NLP engineer |
| CodaLab bundle & scorer | NLP engineer |
| Participant support (forum / email) | Task chairs |
| Overview paper | All organisers + invited participants |

**Proposed task chairs:** Jose Jaime Baena Rojas, Daniel Pinto Pajares, César Andrés (UNIR).

---

## 10. Participant deliverables

1. **System runs:** Valid prediction files for registered track(s).
2. **Task description paper** (4–6 pages): data use, model, training details, dev results, ablation (IberLEF proceedings format).
3. **Optional:** Release of model weights or prompts under open licence (encouraged, not required).

---

## 11. Risks and mitigations

| Risk | Mitigation |
|------|------------|
| Social-media text not redistributable | IDs + rehydration script; parallel leaderboard slice on parliamentary+manifesto only |
| Low fallacy prevalence | Report macro-F1 with prevalence-weighted analysis; maintain explicit-none convention |
| LLM parse failures | JSON schema validator; exploratory table separate from official rank |
| Guideline drift | Frozen `guideline_version` field; test lock before dev tuning window |
| Delayed SPDB v1.0.0 | Defer to IberLEF 2028; run dev-only pilot at IberLEF 2027 as optional lab |

---

## 12. Related documentation

| Document | Path |
|----------|------|
| v1 build specification | [`docs/dataset_documentation/v1_build_specification.md`](dataset_documentation/v1_build_specification.md) |
| Dataset card | [`dataset_documentation/dataset_card.md`](../dataset_documentation/dataset_card.md) |
| Benchmark comparison | [`paper/tables/benchmark_comparison.md`](../../paper/tables/benchmark_comparison.md) (manuscript) |
| Pilot metrics & κ targets | [`annotation/pilot_001/pilot_metrics.md`](../annotation/pilot_001/pilot_metrics.md) |
| IberLEF export prep | Build spec §12.5 |

---

## 13. Summary

**SPDB@IberLEF** will offer three tracks — pragmatic function classification, political fallacy detection, and joint multi-task prediction — on a multi-register Spanish political discourse benchmark with locked test evaluation, macro-F1-based leaderboards, and tiered organiser baselines from majority class through BETO and open LLMs. The campaign converts SPDB from a static resource into a recurring Iberian evaluation hub for communicative and argumentative structure in political NLP.

**Next steps:** Finalise SPDB v1.0.0 release checklist; implement CodaLab scorer; submit formal proposal to IberLEF organisers upon PI approval.
