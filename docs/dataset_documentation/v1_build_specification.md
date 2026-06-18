# v1 Build Specification — Spanish Political Discourse Benchmark (SPDB)

**Document status:** Draft v1.0 (operational)  
**Paper slug:** `p01_spanish_political_discourse_benchmark`  
**Target release:** GitHub (code + docs) + Zenodo (data DOI)  
**Execution horizon:** 6 months  

This document defines scope, procedures, and release criteria for SPDB v1. It is not manuscript text.

---

## 1. Final dataset scope (v1)

### 1.1 Mission

Build a **legally reusable, persistent, stratified** Spanish political discourse benchmark with:

- **Core supervision:** pragmatic function (primary) + reduced political fallacy (primary, multi-label allowed).
- **Experimental supervision:** semantic vacuity + conceptual anachronism (subset only in v1).
- **Baselines:** majority, rule-based, classical ML, transformer, LLM.
- **Long-term reuse:** stable IDs, versioned annotation guidelines, IberLEF-compatible export optional in v1 / required before any shared task.

### 1.2 Target size (v1)

| Component | Target | Hard floor (MVP) |
|-----------|--------|------------------|
| Annotated units (core labels) | **8,000** | **5,000** |
| Double-annotated QC subset | 1,600 (20%) | 1,000 (20%) |
| Experimental-label subset | 2,000 | 1,000 |
| Distinct source documents | ≥400 | ≥250 |
| Time coverage | 2015–2025 | 2018–2024 |

**Rationale:** 8k units ≈ 400–500 annotator hours at 15–20 units/hour with double-coding overhead; feasible in 6 months with 2 FTE annotators + PI/adjudicator.

### 1.3 Source mix (by annotated unit count)

| Source type | Target share | Units @ 8k | Units @ 5k (MVP) |
|-------------|--------------|------------|------------------|
| Parliamentary discourse | **60%** (range 55–65%) | 4,800 | 3,000 |
| Party manifestos | **12%** (range 10–15%) | 960 | 600 |
| Elite social media (IDs only) | **28%** (range 20–30%) | 2,240 | 1,400 |

**Geographic scope (v1):** Spain (state + autonomous communities where license permits redistribution of text).

**Language:** Spanish (`es`); exclude code-switched segments &lt;70% Spanish unless tagged `mixed`.

### 1.4 Inclusion / exclusion (instance level)

**Include:**

- Political speech acts by elected officials, party organs, or candidates in official capacity.
- Units containing at least one claim, evaluative statement, or procedural move with political referent.

**Exclude:**

- Pure procedural boilerplate without political content (e.g., roll-call only).
- Duplicate near-verbatim repeats across sources (keep earliest; hash dedupe).
- Segments &lt;20 characters or &gt;2,000 characters after normalization.
- Sources without documented redistribution rights for **text** (social media: IDs-only path).

---

## 2. Unit of analysis and segmentation rules

### 2.1 Unit definition

**Primary unit:** `discourse_unit` — the smallest span an informed reader would treat as carrying **one dominant pragmatic function** toward a political target (actor, policy, institution, or electorate).

- One unit → one **primary** pragmatic function label.
- Fallacy labels apply to the same span (multi-label).
- Optional experimental labels apply to the same span.

### 2.2 Segmentation by source

| Source | Raw document | Segmentation rule | Split trigger |
|--------|--------------|-------------------|---------------|
| Parliamentary | Speaker intervention (HTML/PDF/XML) | Split on speaker change; within intervention split on `\n\n` or sentence if &gt;400 tokens | New unit if topic shift marker + new claim (adjudicator rulebook §S2) |
| Manifesto | Section/paragraph in MARPOR or PDF | One paragraph = one unit if ≤400 tokens; else split on sentence boundaries | Heading-only paragraphs merged with next content paragraph |
| Social media | Single post (reconstructed from ID) | 1 post = 1 unit; threadded replies excluded in v1 | N/A |

**Tokenization:** Count with `BETO` tokenizer (`dccuchile/bert-base-spanish-wwm-cased`) for caps; store `char_start`, `char_end` in source document.

**Overlap:** No overlapping units. Adjacent units must not share sentences.

### 2.3 Normalization (non-destructive)

Store `text_raw` and `text_norm`:

1. Unicode NFC.
2. Preserve casing; optional lowercase copy `text_norm_lower` for baselines only.
3. Collapse whitespace; keep single newlines as space.
4. Do not remove punctuation affecting modality or negation.
5. Mask URLs as `<URL>`, @mentions as `<USER>`, hashtags kept.

### 2.4 QC rules

- 5% random sample reviewed by PI for segmentation errors before annotation wave 2.
- Segmentation error rate &gt;10% on sample → halt and revise rules (kill criterion §14).

---

## 3. Source acquisition plan

### 3.1 Parliamentary discourse (60%)

| Priority | Corpus | Access | License / terms | v1 quota |
|----------|--------|--------|-----------------|----------|
| P1 | Congreso de Diputados — Diario de Sesiones (API/scrape where permitted) | Official portal + bulk where available | Verify `datos.gob.es` / session terms; document per snapshot date | 2,400 units |
| P2 | Senado — plenary/interventions | Same | Same | 800 units |
| P3 | Parlament de Catalunya / Euskal Herria (if license OK) | Open data portals | Per-portal license | 800 units each max |
| P4 | Europarl Spanish interventions | EP open data | EP reuse policy | 400 units |

**Procedure:**

1. Register source in `data/raw/parliamentary/{jurisdiction}/{fetch_date}/`.
2. Store fetch script + checksum manifest in `code/`.
3. Parse to canonical JSONL: `{doc_id, speaker, party, date, chamber, text_raw, url, license_ref}`.

### 3.2 Party manifestos (12%)

| Priority | Source | Access | License | v1 quota |
|----------|--------|--------|---------|----------|
| M1 | Manifesto Project (MARPOR) — Spain | MRG download | MRG terms + cite | 500 units |
| M2 | National/autonomic elections — official PDFs | Party websites + historical archives | Per-document: allow redistribution or excerpt under fair-use doc only | 460 units |

**Procedure:**

- Prefer MARPOR where paragraph alignment exists.
- For PDFs: OCR only if necessary; flag `ocr=true`; manual spot-check 10%.

### 3.3 Elite social media — IDs only (28%)

**Policy:** Release **post IDs + metadata + annotations** on Zenodo; text reconstruction via documented script from public endpoints/archives. GitHub stores no full text for this slice if platform ToS restricts redistribution.

| Step | Action |
|------|--------|
| 1 | Define elite list: MPs, party leaders, main party accounts (2015–2025); cap party balance. |
| 2 | Collect post IDs via Academic Research access / public timelines / Internet Archive snapshots. |
| 3 | Store `platform`, `post_id`, `author_handle`, `author_party`, `timestamp`, `url`, `rehydration_method`. |
| 4 | Local rebuild for annotation only; export checksum of rebuilt text, not text itself, if required. |

**v1 quota:** 2,240 units from ≥150 accounts; stratify by party family and pre/post-electoral periods.

**Fallback:** If rebuild success rate &lt;85%, reduce social slice to 15% and compensate with parliamentary (kill criterion §14).

### 3.4 Legal review gate

Before annotation starts:

- [ ] `licensing_and_ethics.md` completed with per-source rows.
- [ ] External text redistribution cleared for parliamentary + manifesto slices.
- [ ] Social slice approved as IDs-only + rehydration script.

---

## 4. Metadata schema

### 4.1 File format

- **Canonical store:** JSONL UTF-8, one object per unit.
- **Filename:** `spdb_v1_{split}.jsonl` where `split ∈ {train, dev, test}`.
- **Companion:** `spdb_v1_{split}.csv` (same fields, flat) for IberLEF-style consumption.

### 4.2 Required fields (all units)

| Field | Type | Description |
|-------|------|-------------|
| `instance_id` | string | Stable SHA256 prefix: `spdb-v1-{split}-{seq:06d}` |
| `text` | string | Annotatable text (empty string if `text_redistributable=false`) |
| `text_redistributable` | bool | False for IDs-only social slice in public release |
| `source_type` | enum | `parliamentary` \| `manifesto` \| `social_media` |
| `source_corpus` | string | e.g. `congreso_es`, `marpor_es`, `elite_x_ids` |
| `document_id` | string | Source-native doc ID |
| `segment_index` | int | 0-based within document |
| `char_start` | int | Offset in source document |
| `char_end` | int | Offset in source document |
| `language` | string | ISO 639-1 (`es`) |
| `date` | string | ISO 8601 (speech/manifesto/post date) |
| `speaker_id` | string | Pseudonymized hash or account ID |
| `speaker_role` | enum | `legislator` \| `party_org` \| `executive` \| `candidate` \| `unknown` |
| `party_family` | string | Controlled vocab (see §7) |
| `chamber_or_level` | string | e.g. `congreso`, `senado`, `autonomic`, `eu`, `n/a` |
| `election_cycle` | string | e.g. `2019-11`, `2023-07`, or `n/a` |
| `platform` | string | `n/a` except social (`x`, etc.) |
| `platform_post_id` | string | Required if `source_type=social_media` |
| `rehydration_url` | string | Optional archive URL |
| `license_ref` | string | SPDX or custom doc pointer |
| `split` | enum | `train` \| `dev` \| `test` |
| `annotated` | bool | Core labels present |
| `annotation_version` | string | e.g. `v1.0.0` |
| `token_count_beto` | int | Precomputed |

### 4.3 Annotation fields (core)

| Field | Type | Description |
|-------|------|-------------|
| `pragmatic_function` | enum | Single primary label (§5.1) |
| `fallacy_labels` | list[enum] | Zero or more (§5.2); empty list = no fallacy |
| `fallacy_none_explicit` | bool | True if annotator checked "no fallacy" |
| `annotator_id` | string | Pseudonym |
| `adjudicated` | bool | True if gold after adjudication |
| `guideline_version` | string | e.g. `guidelines-v1.2` |

### 4.4 Experimental fields (subset)

| Field | Type | Description |
|-------|------|-------------|
| `semantic_vacuity` | enum | `0_absent` \| `1_present` \| `unclear` |
| `conceptual_anachronism` | enum | `0_absent` \| `1_present` \| `unclear` |
| `experimental_subset` | bool | True if unit in experimental arm |

### 4.5 Provenance fields

| Field | Type | Description |
|-------|------|-------------|
| `created_at` | string | ISO 8601 |
| `pipeline_version` | string | Git tag of build scripts |
| `duplicate_of` | string | `instance_id` if deduped |

---

## 5. Annotation schema

### 5.1 Pragmatic function (primary, mutually exclusive)

Annotators select **one** dominant function. If truly tied, choose the function directed at the **primary political target**; flag `borderline=true` (≤5% expected).

| Label | Code | Definition (operational) |
|-------|------|---------------------------|
| Policy advocacy | `PF_ADVOCACY` | Supports/advances a policy position, program, or normative goal. |
| Position attack | `PF_ATTACK` | Challenges an actor's competence, integrity, legitimacy, or record. |
| Defense / rebuttal | `PF_DEFENSE` | Rebuts criticism or protects actor/policy reputation. |
| Proposal / commitment | `PF_PROPOSAL` | Commits to future action, concrete measure, or implementation pledge. |
| Mobilization appeal | `PF_APPEAL` | Seeks electoral/civic support via identity, values, fear, hope, or solidarity. |
| Informational | `PF_INFO` | Conveys factual or procedural information with minimal evaluative framing. |
| Deflection / evasion | `PF_DEFLECT` | Avoids question/topic; pivots without substantive engagement. |
| Ritual / procedural | `PF_PROCEDURAL` | Order of business, courtesy, formal parliamentary ritual with political context. |

**IberLEF mapping (future):** export `pragmatic_function` as single-label column `label_pf`; maintain label inventory file `label_inventory.tsv`.

### 5.2 Reduced political fallacy scheme (multi-label)

Apply when the **reasoning move** in the unit matches definition. Multiple fallacies allowed; do not infer intent beyond text + minimal context (speaker, addressee in same document).

| Label | Code | Definition (operational) |
|-------|------|---------------------------|
| Ad hominem | `FAL_ADHOM` | Rejects/challenges claim primarily via personal attack on actor rather than claim merits. |
| Straw man / distortion | `FAL_STRAW` | Misrepresents opponent position (stronger/weaker) then refutes the distortion. |
| False dilemma | `FAL_DILEMMA` | Presents two (or few) exclusive options when reasonable alternatives exist. |
| Slippery slope | `FAL_SLOPE` | Claims action inevitably leads to extreme outcome without sufficient evidential steps. |
| Appeal to emotion / fear | `FAL_EMOTION` | Replaces/evades evidentiary support with fear, outrage, or pity as primary warrant. |
| Hasty generalization | `FAL_GENERAL` | Generalizes from unrepresentative or insufficient evidence. |
| Whataboutism / tu quoque | `FAL_WHATABOUT` | Deflects criticism by pointing to opponent's unrelated or symmetric behavior without addressing merit. |
| No fallacy | `FAL_NONE` | No fallacy present (store as empty list + `fallacy_none_explicit=true`) |

**Constraints:**

- Max 3 fallacy labels per unit; if more suspected, pick top 3 by salience.
- `FAL_NONE` is not combined with other fallacy labels.

### 5.3 Optional experimental labels (v1 subset only)

| Label | Code | Definition (operational) |
|-------|------|---------------------------|
| Semantic vacuity absent | `SV_0` | Unit conveys specifiable propositional content about politics/policy. |
| Semantic vacuity present | `SV_1` | Unit is largely empty of propositional content (slogans, pure applause lines, content-free assent). |
| Conceptual anachronism absent | `CA_0` | Concepts/terms used in historically/contextually appropriate frame. |
| Conceptual anachronism present | `CA_1` | Applies concept/term anachronistically to past actors/events or misdates political category. |
| Unclear | `*_UNCLEAR` | Insufficient context; use sparingly (&lt;3% per label). |

**Experimental arm:** 2,000 units double-annotated for SV/CA; not required for leaderboard v1.

---

## 6. Reduced fallacy taxonomy — annotator decision rules

1. **Evidence standard:** Label fallacy only if a minimally competent reader of Spanish political discourse would agree the move is present **in the span** (not whole speech).
2. **Context window:** Annotators may view ±1 adjacent unit from same `document_id`; no external web context.
3. **Sarcasm/irony:** Label literal rhetorical move; flag `irony_possible=true` (analysis only, not a label).
4. **PF vs FAL independence:** A unit may be `PF_ATTACK` without fallacy (evidence-based critique) or with `FAL_ADHOM`.
5. **Borderline adjudication:** All `borderline=true` or inter-annotator disagreement on fallacy → adjudicator within 72h.

**Gold standard:** Adjudicated label on QC subset + single-annotator on remainder only if IA thresholds met (§9).

---

## 7. Sampling and stratification plan

### 7.1 Controlled vocabularies

**`party_family` (minimum):**

`PSOE`, `PP`, `VOX`, `SUMAR/UP`, `ERC`, `JxCat`, `PNV`, `Bildu`, `CC`, `other_national`, `other_regional`, `non_partisan`, `unknown`

**Temporal bins:** `2015–2017`, `2018–2020`, `2021–2023`, `2024–2025`

### 7.2 Pool construction

1. Build universe U after segmentation (~40k–80k candidate units expected).
2. Dedupe (MinHash, threshold 0.85) → U'.
3. Classify strata: `source_type × party_family × temporal_bin`.
4. Allocate quotas proportionally to U' subject to §1.3 source mix floors/caps.

### 7.3 Selection algorithm

- **Stratified random sample** with minimum 50 units per non-rare stratum (rare → merge to `other_*`).
- **Active sampling (optional, max 10% of pool):** upsample units where rule-based classifier confidence is low (entropy &gt; threshold) to improve benchmark difficulty.
- Lock **test** set before any baseline hyperparameter tuning on dev.

### 7.4 Social media ID sampling

- Balance party families ±5% of parliamentary seat share (2019–2023 baseline).
- Cap any single account at 2% of social slice.
- Exclude pure retweets without quote comment.

---

## 8. Annotation workflow

### 8.1 Roles

| Role | FTE (6 mo) | Responsibility |
|------|------------|----------------|
| PI / adjudicator | 0.2 | Guidelines, adjudication, kill decisions |
| Lead annotator | 0.5 | Training, QC, coder support |
| Annotators (×2) | 1.0 each | Primary coding |
| NLP engineer | 0.5 | Tooling, export, baselines |

### 8.2 Tooling

- **Platform:** Label Studio or Doccano (self-hosted); export JSON.
- **Repo paths:** Guidelines in `protocol/`; exports to `data/processed/annotations/`.
- **Interface order:** (1) PF → (2) fallacies → (3) SV/CA if in experimental arm.

### 8.3 Training phases

| Phase | Duration | Output |
|-------|----------|--------|
| Pilot 1 | Week 5–6 | 200 units, 100% double-coded |
| Guideline revision | Week 7 | `guidelines-v1.1` |
| Pilot 2 | Week 8 | 200 units; IA computed |
| Production wave 1 | Week 9–16 | 4,000 units |
| Midpoint audit | Week 13 | Drift check |
| Production wave 2 | Week 17–22 | 4,000 units |
| Adjudication backlog | Week 18–24 | All disagreements resolved |

### 8.4 Productivity assumptions

- 16–22 units/annotator/hour after pilot (multi-label).
- Weekly target per annotator: 350–450 units.
- Adjudication load: ~15% of double-coded units.

### 8.5 Quality controls

- Gold items (5% hidden): pre-adjudicated units; annotator must maintain ≥85% agreement on PF, ≥75% on fallacies.
- Weekly feedback sessions.
- Freeze `guideline_version` after Pilot 2 except patch releases (logged).

---

## 9. Inter-annotator agreement plan

### 9.1 Design

- **Double annotation:** 20% of all core units (random, stratified).
- **Experimental subset:** 100% double-annotated for SV/CA (2,000 units).

### 9.2 Metrics

| Task | Metric | Target (v1 release) | MVP floor |
|------|--------|---------------------|-----------|
| Pragmatic function | Cohen's κ (pairwise mean) | ≥0.72 | ≥0.65 |
| Pragmatic function | Krippendorff's α (multi-annotator) | ≥0.70 | ≥0.63 |
| Fallacy (multi-label) | Macro-F1 on annotator pairs | ≥0.55 | ≥0.48 |
| Fallacy presence (binary) | Cohen's κ | ≥0.60 | ≥0.52 |
| Semantic vacuity | Cohen's κ | ≥0.65 | ≥0.58 |
| Conceptual anachronism | Cohen's κ | ≥0.60 | ≥0.52 |

### 9.3 Disagreement handling

1. Pair disagreement → third pass by lead annotator.
2. Persistent disagreement → PI adjudication (gold label).
3. Log all changes in `adjudication_log.jsonl` (no text, IDs + label deltas only).

### 9.4 Reporting

- Report IA on **dev** only; **test** labels never used for guideline iteration after lock (Week 10).
- Paper/repository: IA tables by source_type and label.

---

## 10. Baseline model plan

All baselines predict **same label spaces** as core schema. Hyperparameter tuning **dev only**; **single locked test evaluation** for v1 release.

### 10.1 Majority / prior baseline

- **PF:** Predict most frequent `pragmatic_function` in train.
- **Fallacies:** Per-label majority threshold (predict label if train frequency &gt;50%) or empty set baseline reported separately.
- **Purpose:** Lower bound; sanity check.

### 10.2 Rule-based baseline

- **Input:** `text_norm` + metadata rules (party, chamber) optional.
- **Implementation:** `code/src/discourse_classifier/` — extend existing rule sets for PF + reduced fallacies.
- **Output:** Deterministic labels + rule hit log.
- **Release:** Rules YAML + script on GitHub; predictions on Zenodo.

### 10.3 Classical ML baseline

- **Features:** TF-IDF word (1–2 grams) + char (3–5 grams), Spanish stopword list.
- **Models:**
  - PF: linear SVM (one-vs-rest) or multinomial LogReg.
  - Fallacies: binary relevance LogReg per fallacy label (multi-label).
- **Stack:** scikit-learn; seed=42; train script in `code/`.

### 10.4 Transformer baseline

- **Model:** `dccuchile/bert-base-spanish-wwm-cased` (primary); optional secondary: `PlanTL-GOB-ES/roberta-base-bne`.
- **Setup:**
  - PF: single-label sequence classification.
  - Fallacies: multi-label with sigmoid heads (8 labels).
- **Training:** 3 epochs max, early stopping on dev macro-F1 (PF) / micro-F1 (fallacies); batch 16, lr 2e-5.
- **Release:** dev/test predictions + config JSON; **weights optional** on Zenodo (not GitHub LFS).

### 10.5 LLM baseline

- **Models (open, reproducible):** Llama-3.1-8B-Instruct or Mistral-7B-Instruct (exact checkpoint pinned).
- **Method:** Fixed prompts from `protocol/llm_prompt_registry.md`; JSON-only output schema; temperature=0; 0–3 shot from train (frozen shots sampled once, IDs logged).
- **Runs:** 3 seeds for parsing stability; majority vote per label field.
- **Optional non-repro row:** One proprietary API model for comparison table only (clearly marked non-reproducible; not part of official leaderboard).
- **Metrics:** Same as fine-tuned models; report parsing failure rate (kill if &gt;5% on dev).

### 10.6 Evaluation metrics (leaderboard v1)

| Task | Primary metric | Secondary |
|------|----------------|-----------|
| PF | Macro-F1 | Accuracy, per-class F1 |
| Fallacies | Macro-F1 (label-wise) | Micro-F1, sample-wise F1 |
| Combined | Macro average of PF macro-F1 and fallacy macro-F1 | — |

**Leaderboard file:** `results/metrics/baseline_leaderboard_v1.csv` (versioned, small CSV allowed in Git).

---

## 11. Train / dev / test split strategy

### 11.1 Ratios

| Split | Share | Units @ 8k | Purpose |
|-------|-------|------------|---------|
| train | 70% | 5,600 | Training baselines |
| dev | 15% | 1,200 | Tuning, IA monitoring, error analysis |
| test | 15% | 1,200 | **Locked** final evaluation |

### 11.2 Constraints (all must hold)

1. **Document-level grouping:** All segments from same `document_id` in same split.
2. **Stratification:** Match marginal distributions of `source_type`, `party_family`, `temporal_bin` within ±2% per split.
3. **Social IDs:** Account-level grouping — all posts from one account in same split (prevents leakage).
4. **Test lock:** Week 10; hash of test `instance_id` list committed (`test_manifest.sha256`); no peeking during annotation guideline edits after Week 7 except adjudication logs without test labels.

### 11.3 Splits for experimental labels

- SV/CA subset drawn entirely from **train+dev** for annotation training; include 300 dev + 200 test only if IA targets met; otherwise report SV/CA on dev-only exploratory track.

---

## 12. Release architecture

### 12.1 GitHub (repository `papers_unir`)

| Artifact | Path | Notes |
|----------|------|-------|
| Build spec (this doc) | `docs/dataset_documentation/v1_build_specification.md` | Version tagged |
| Guidelines | `protocol/` | Annotation + baselines |
| Code | `code/` | Ingestion, segmentation, baselines, eval |
| Small sample | `data/processed/spdb_v1_sample_100.jsonl` | Demo only, no test units |
| Leaderboard | `results/metrics/baseline_leaderboard_v1.csv` | |
| CI | `.github/workflows/` | Tests + optional LaTeX |

**Git tag:** `spdb-v1.0.0` aligned with Zenodo DOI.

### 12.2 Zenodo

| Deposit | Contents |
|---------|----------|
| **Primary data record** | `spdb_v1_train/dev/test.jsonl`, `label_inventory.tsv`, `test_manifest.sha256`, annotation logs (de-identified) |
| **Social slice** | `social_post_ids.csv`, rehydration script, rebuild checksums |
| **Models (optional)** | Transformer checkpoint, baseline predictions |
| **Metadata** | `.zenodo.json`, CITATION.cff, version, license fields |

**Versioning:** Zenodo concept DOI; v1.0.0 first public release.

### 12.3 Documentation bundle

| Doc | Location | Status gate |
|-----|----------|-------------|
| Datasheet | `dataset_documentation/datasheet.md` | Complete before DOI |
| Data statement | `dataset_documentation/data_statement.md` | Complete before DOI |
| Licensing & ethics | `dataset_documentation/licensing_and_ethics.md` | Complete before acquisition wave 2 |
| Rehydration | `dataset_documentation/rehydration_instructions.md` | Required if social &gt;0 |
| Release checklist | `dataset_documentation/release_checklist.md` | Sign-off before upload |

### 12.4 License matrix (v1 default — confirm per source)

| Component | Default license | Condition |
|-----------|-----------------|-----------|
| Annotations (our work) | CC BY 4.0 | Always |
| Parliamentary/manifesto text | CC BY 4.0 or source license | Per `license_ref`; exclude if incompatible |
| Social media text in public set | **Not redistributed** | IDs + rehydration only |
| Code | Apache 2.0 or MIT | Project default |
| Trained model weights | CC BY 4.0 | If base model license permits |

**Incompatible source:** Drop text, keep IDs/metadata/labels, document in datasheet.

### 12.5 IberLEF compatibility (v1 prep)

- Export TSV: `id \t text \t label_pf \t labels_fal` (+ optional SV/CA columns).
- Provide `README_iberlef.md` with label definitions and download script.
- Full shared-task packaging deferred to v1.1 unless IberLEF timeline confirmed.

---

## 13. Minimum viable v1 vs v2 extensions

### 13.1 MVP v1 (must ship)

- ≥5,000 core-labeled units meeting source mix ±5%.
- PF + fallacy gold on train/dev/test with locked test.
- Five baseline families evaluated (§10).
- GitHub + Zenodo DOI + datasheet + data statement + license matrix.
- IA report on double-coded subset meeting MVP floors (§9.2).

### 13.2 Target v1 (preferred)

- 8,000 units; IA at target thresholds.
- 2,000 experimental SV/CA subset.
- Transformer + LLM baselines with full reproducible configs.
- IberLEF export format documented.

### 13.3 v2 extensions (out of scope v1)

- Catalan/Bilingual track.
- Thread-level social media discourse.
- Fine-grained fallacy ontology (12+ labels).
- Adversarial / contrast sets for robustness.
- Active leaderboard with hidden test (CodaLab).
- Full IberLEF shared task host package.
- Cross-lingual Portuguese comparison subset.

---

## 14. Risks and kill criteria

| Risk | Indicator | Kill / pivot action |
|------|-----------|---------------------|
| License block on text redistribution | Legal review fails for &gt;30% planned parliamentary text | Pivot to excerpt-only or IDs+rehydration; reduce affected slice |
| Social rehydration failure | &lt;85% posts recoverable at annotation time | Cap social at 15%; reallocate to parliamentary |
| IA below MVP on PF after Pilot 2 | κ &lt;0.60 | Halt production; revise guidelines + re-pilot (max 3 weeks); drop to 6 PF labels if needed |
| Annotation throughput | &lt;60% of weekly quota for 2 consecutive weeks | Reduce target to 5k MVP; extend 4 weeks or add annotator |
| Fallacy IA chronically low | Macro-F1 &lt;0.45 after adjudication | Collapse to 5 fallacy labels or binary `fallacy_present`; document for v1.1 expansion |
| LLM parse failures | &gt;5% dev set unparseable | Drop LLM from official leaderboard; report exploratory only |
| Source political imbalance | Any party &lt;2% of corpus unintentionally | Resample before test lock |
| Test leakage detected | Document in multiple splits | Re-split; reset baselines |
| **Global kill** | Cannot meet MVP v1 by Month 6 + 4 weeks | Publish partial release (protocol + sample + baselines on dev only) as `spdb-v0.9-beta`; delay Q1 submission |

---

## 15. Six-month execution timeline

| Month | Weeks | Milestones | Deliverables |
|-------|-------|------------|--------------|
| **M1** | 1–2 | Legal scan; source registry; dev environment | `licensing_and_ethics.md` draft; ingestion scripts v0.1 |
| | 3–4 | Fetch parliamentary + MARPOR; social ID harvest starts | Raw data manifests; segmentation v0.1; pool U' |
| **M2** | 5–6 | Pilot annotation 1; test split locked | 200 double-coded units; `guidelines-v1.0`; test manifest hash |
| | 7–8 | Pilot 2; IA report; guideline patch | `guidelines-v1.1`; go/no-go for production |
| **M3** | 9–10 | Production wave 1 (2k); classical + rule baselines on dev | 2k annotated; baseline v0.1 leaderboard |
| | 11–12 | Production wave 1 cont. (2k); transformer dev runs | 4k cumulative; BETO dev scores |
| **M4** | 13–14 | Midpoint audit; production wave 2 (2k) | Drift report; 6k cumulative |
| | 15–16 | Wave 2 (2k); LLM baseline dev | 8k target; LLM prompt registry frozen |
| **M5** | 17–18 | Adjudication; experimental SV/CA arm | Gold core set; 2k SV/CA subset |
| | 19–20 | Final baselines on locked test (once); export IberLEF TSV | Test leaderboard; `spdb_v1_*.jsonl` |
| **M6** | 21–22 | Datasheet, Zenodo upload, GitHub tag | DOI live; `spdb-v1.0.0` tag |
| | 23–24 | Buffer: rebuttal fixes, v1.0.1 patch if needed | Release checklist signed; paper sections populated from specs |

**Critical path:** legal clearance → segmentation QC → Pilot 2 IA → test lock (Week 10) → production → test evaluation → Zenodo.

**Staffing minimum:** PI + 2 annotators + 0.5 NLP engineer continuously; +0.5 annotator lead Weeks 5–16.

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-18 | Initial operational spec |

**Related files:** `protocol/annotation_protocol.md`, `protocol/coding_scheme.md`, `protocol/baseline_model_plan.md`, `protocol/inter_annotator_agreement_plan.md`, `dataset_documentation/release_checklist.md`.
