# SPDB Annotation Codebook v1

**Spanish Political Discourse Benchmark (SPDB)**  
**Version:** `codebook-v1.0.0` (aligned with `guidelines-v1.0`)  
**Date:** 2026-06-18  
**Audience:** Primary annotators, lead annotators, adjudicators  
**Canonical ontology:** `labels/*.tsv`

---

## Document control

| Field | Value |
|-------|-------|
| Guideline version | `guidelines-v1.0` |
| Label inventory | 8 pragmatic functions · 7 fallacies + explicit none · 2 experimental arms |
| Unit of analysis | Discourse unit (one dominant pragmatic function per span) |
| Language of text | Spanish (`es`) |
| Language of label IDs | English codes (`PF_*`, `FAL_*`, …) |

**Reliability target (codebook design goal):** Cohen's κ and Krippendorff's α **> 0.80** on pragmatic function after calibration (excellent tier per `annotation/pilot_001/pilot_metrics.md`). Release MVP floor remains κ ≥ 0.67; this codebook is written to reach the **0.80** target through definitions, decision trees, and adjudication rules below.

---

## 1. Purpose and scope

This codebook operationalises human annotation for SPDB v1. Annotators assign:

1. **Pragmatic function** — exactly one `PF_*` label (required, primary supervision).
2. **Political fallacies** — zero to three `FAL_*` labels, or explicit none (required).
3. **Experimental labels** — `SV_*` and `CA_*` when `experimental_subset=true` (optional arm).

Labels apply to the **entire discourse unit** in the task, not to a sentence fragment inside it. Metadata (`speaker_name`, `speaker_party`, `date`, `source_type`) provides context only.

**Independence rule:** Pragmatic function and fallacy labels are coded **independently**. A evidence-based `PF_ATTACK` may co-occur with no fallacy; `PF_ATTACK` may co-occur with `FAL_ADHOM`.

---

## 2. Unit of analysis

A **discourse unit** is the smallest contiguous span an informed reader treats as carrying **one dominant pragmatic function** toward a political target (actor, policy, institution, or electorate).

| Rule | Specification |
|------|----------------|
| Span | Full `text` field in Label Studio / CSV row |
| Overlap | Units do not overlap; adjacent units do not share sentences |
| Length | 20–2,000 characters after normalisation (pre-annotation pool) |
| Context | Read ±1 adjacent unit from same `document_id` when needed for fallacies or borderline PF |
| External context | **Not allowed** (no web search, no speaker biography beyond metadata) |

---

## 3. Annotation workflow (summary)

```
Primary coding (blind) → disagreement detection → lead third pass → PI adjudication → gold label
```

| Step | Actor | Action |
|------|-------|--------|
| 1 | Annotator A & B | Independent primary labels on double-coded sample (20%) or single pass |
| 2 | Pipeline | Flag PF or fallacy mismatches; flag `borderline=true` |
| 3 | Lead annotator | Third pass on disagreements |
| 4 | PI / adjudicator | Gold label within **72 h** if disagreement persists |
| 5 | Export | `adjudicated=true`; log in `adjudication_log.jsonl` (IDs only) |

Full UI order: Context → (Adjudication panel if applicable) → PF → Fallacies → Experimental → Quality flags.

---

## 4. Master decision tree — pragmatic function

Apply **top to bottom**; assign the **first** category whose dominant-move criterion is satisfied. If two categories tie, use the tie-breakers in §4.1.

```
START: Read full unit (+ metadata). Ignore speaker's career outside this span.

1. Is the dominant move chamber/order-of-business management by the chair
   (turn-taking, votes, rule reminders) with no substantive policy argument?
   YES → PF_PROCEDURAL
   NO  → continue

2. Does the speaker avoid the pending question/topic and pivot to a different
   issue without substantive engagement?
   YES → PF_DEFLECT
   NO  → continue

3. Does the span commit to a future legislative/government action by this
   actor (presentaremos, nos comprometemos, votaremos a favor/en contra as pledge)?
   YES → PF_PROPOSAL
   NO  → continue

4. Is the dominant move mobilising citizens/voters via hope, fear, solidarity,
   or shared identity (not primarily policy detail or opponent attack)?
   YES → PF_APPEAL
   NO  → continue

5. Is the speaker primarily rebutting criticism directed at self/party/policy
   (reactive defense)?
   YES → PF_DEFENSE
   NO  → continue

6. Is the primary target a political actor/group's competence, integrity, record,
   or legitimacy (not merely abstract policy)?
   YES → PF_ATTACK
   NO  → continue

7. Does the span argue for/against a policy/programme/normative goal as the
   dominant move?
   YES → PF_ADVOCACY
   NO  → continue

8. Does the span convey facts, figures, or bill content with minimal evaluative
   framing as the dominant move?
   YES → PF_INFO
   NO  → re-read; apply tie-breakers (§4.1); flag borderline if still tied
```

### 4.1 Tie-breakers (PF)

1. Choose the function directed at the **primary political target** in the span.
2. If courtesy opener + substance: label the **substance**, not the opener.
3. If attack and advocacy coexist: whichever occupies **more rhetorical labour** (sentences devoted to the move).
4. If still tied: select best label and enable **Borderline PF case** (`borderline=true`); expected ≤ **5%** of units.
5. Never assign two PF labels; never leave PF empty.

---

## 5. Pragmatic function labels

Enter **label ID** only (e.g. `PF_ADVOCACY`), not the English name.

### 5.1 PF_ADVOCACY — Policy advocacy

**Definition:** Supports or advances a policy position, programme, or normative goal.

**Decision rule:** Dominant move argues **for or against a policy design**, law, or normative outcome. Criticism of **policy** (not primarily personal character) belongs here unless the span is reactive defense (`PF_DEFENSE`).

**Example (positive):**

> «En Ciudadanos abogamos […] que se tenía que definir la figura del consumidor vulnerable […] que se tenía que fijar un criterio de renta […]»

— Melisa Rodríguez Hernández (Cs). Unit `spdb-v1-unassigned-ceada2c252a1`.

**Counterexample:**

> «Tienen ustedes la osadía de hablar de la contratación temporal cuando precisamente la reforma del año 1984 es la que rompe el principio de causalidad […]»

— Carolina España Reina (PP). **Not advocacy** → `PF_ATTACK` (opponent record).

| Confused with | Resolution |
|---------------|------------|
| `PF_ATTACK` | Advocacy → **policy**; attack → **actor** competence/integrity/record |
| `PF_PROPOSAL` | Proposal **commits** to action; advocacy **argues** for a position |
| `PF_INFO` | Advocacy embeds facts in **normative** argument; info is **descriptive** |

---

### 5.2 PF_ATTACK — Position attack

**Definition:** Challenges an actor's competence, integrity, legitimacy, or record.

**Decision rule:** Primary target is a **political actor or group**. Personalised charges, record comparisons, and legitimacy challenges qualify. Evidence-based policy disagreement **without** personal targeting → `PF_ADVOCACY`.

**Example (positive):**

> «No es así, señora Arrimadas. Ustedes ni siquiera han estado sentados en la mesa donde se tomaban estas decisiones […] tampoco han conseguido nada.»

— Pablo Echenique Robba (UP). Unit `spdb-v1-unassigned-b2eaf6b9bc1c`.

**Counterexample:**

> «son tres principalmente las reformas que plantea esta proposición de ley: por una parte, permitir la rectificación registral […]»

— Joseba Agirretxea Urresti (EAJPNV). **Not attack** → `PF_INFO`.

| Confused with | Resolution |
|---------------|------------|
| `PF_DEFENSE` | Defense **reacts** to criticism; attack **initiates** criticism |
| `PF_DEFLECT` | Attack **engages** opponent on a charge; deflect **changes subject** away |

---

### 5.3 PF_DEFENSE — Defense / rebuttal

**Definition:** Rebuts criticism or protects actor or policy reputation.

**Decision rule:** Speaker responds to **prior or implied criticism** by denying, correcting, or shielding their party, government, or policy.

**Example (positive):**

> «Falso, no llegan ni al 1 %.» (rebutting opponents' fiscal claims in debate context)

— Carolina España Reina (PP). Unit `spdb-v1-unassigned-c6349a3fb522`.

**Counterexample:**

> «nos vemos obligados a abstenernos en esta votación.»

— Íñigo Barandiaran Benito (EAJPNV). **Not defense** → position-taking / `PF_ADVOCACY`.

---

### 5.4 PF_PROPOSAL — Proposal / commitment

**Definition:** Commits to future action, concrete measure, or implementation pledge.

**Decision rule:** Explicit **forward-looking commitment** (legislative initiative, amendment pledge, implementation promise). General policy praise without commitment → `PF_ADVOCACY`.

**Example (positive):**

> «Desde ahora anunciamos que presentaremos una enmienda de eliminación […] nos comprometemos a que en breve en esta Cámara se debata su toma en consideración.»

— María Galovart Carrera (PSOE). Unit `spdb-v1-unassigned-46bb18b3c74a`.

**Counterexample:**

> «Comienza la votación.» — Presidencia. **Not proposal** → `PF_PROCEDURAL`.

---

### 5.5 PF_APPEAL — Mobilization appeal

**Definition:** Seeks electoral or civic support via identity, values, fear, hope, or solidarity.

**Decision rule:** Dominant move **mobilises** audience (citizens, voters) through shared identity, hope, fear, or solidarity—not policy detail or opponent attack.

**Example (positive):**

> «A todos los españoles queremos transmitirles un mensaje de esperanza […] juntos, con responsabilidad, pero también con determinación.»

— María Montero Cuadrado (PSOE). Unit `spdb-v1-unassigned-2063abcb1366`.

**Counterexample:**

> «Creo que ha quedado muy claro quién quiere que este país pueda salir de la crisis […] y quién prefiere que no.»

— Same unit, different excerpt. **Not appeal** → implicit `PF_ATTACK`.

---

### 5.6 PF_INFO — Informational

**Definition:** Conveys factual or procedural information with minimal evaluative framing.

**Decision rule:** **Reports** facts, figures, bill contents, or technical information without dominant persuasion, attack, or mobilisation.

**Example (positive):**

> «son tres principalmente las reformas que plantea esta proposición de ley […] permitir la rectificación registral […] suprimir la obligación de aportar documento médico […]»

— Joseba Agirretxea Urresti (EAJPNV). Unit `spdb-v1-unassigned-eb453642ca5f`.

**Counterexample:**

> Statistics deployed to condemn opponents' record → `PF_ATTACK` / `PF_ADVOCACY`, not neutral info.

---

### 5.7 PF_DEFLECT — Deflection / evasion

**Definition:** Avoids question or topic; pivots without substantive engagement.

**Decision rule:** Speaker **does not address** the pending question/bill/challenge and shifts topic. **Rare** in prepared plenary speech; expect low frequency and higher adjudication.

**Example (positive):**

> Pivot from bill substance to criticising an opponent's newspaper terminology instead of engaging the law.

— Patricia Reyes Rivera (Cs). Unit `spdb-v1-unassigned-e022d9750540`.

**Counterexample:**

> Direct rebuttal «No es así, señora Arrimadas» → `PF_ATTACK` / `PF_DEFENSE`, not deflect.

---

### 5.8 PF_PROCEDURAL — Ritual / procedural

**Definition:** Order of business, courtesy, formal parliamentary ritual with political context.

**Decision rule:** **Presidencia** (chair) managing agenda, speaking time, votes, rules; formulaic chamber management without substantive policy.

**Example (positive):**

> «Comenzamos ahora, señorías, con el punto del orden del día […] tiene la palabra el señor Rodríguez Rodríguez.»

— Presidencia. Unit `spdb-v1-unassigned-88da342f1158`.

**Counterexample:**

> «Gracias, presidenta. […] había 4,5 millones de españoles con graves problemas […]»

— Substantive speech after courtesy → **not** procedural.

---

## 6. Master decision tree — fallacies

Fallacies are **multi-label** (max **3**). Label only moves **explicit in the span** (±1 adjacent unit for context). Do not infer hidden intent.

```
START: Read unit (+ optional ±1 context).

1. Is there NO reasoning move matching any FAL_* definition below?
   YES → FAL_NONE (fallacy_none_explicit=true; empty fallacy_labels)
   NO  → continue

2. For each suspected fallacy, verify definition in §7.
   - Ad hominem present? → FAL_ADHOM
   - Straw-man distortion present? → FAL_STRAW
   - False dilemma present? → FAL_DILEMMA
   - Slippery slope present? → FAL_SLOPE
   - Emotion/fear replaces evidence as primary warrant? → FAL_EMOTION
   - Hasty generalization present? → FAL_GENERAL
   - Whataboutism/tu quoque present? → FAL_WHATABOUT

3. If >3 fallacies suspected → keep top 3 by salience in this span.

4. Never combine FAL_NONE with any FAL_* label.

5. PF label is independent (code separately).
```

**Evidence standard:** A minimally competent reader of Spanish political discourse would agree the fallacy is present **in the span**.

**Sarcasm/irony:** Code the **literal rhetorical move**; flag `irony_possible=true` (analysis only, not a training label).

---

## 7. Political fallacy labels

Export: pipe-separated sorted IDs (e.g. `FAL_ADHOM|FAL_WHATABOUT`) or empty list + `fallacy_none_explicit=true`.

### 7.1 FAL_ADHOM — Ad hominem

**Definition:** Rejects or challenges a claim primarily via **personal attack** on the actor rather than the claim's merits.

**Example (positive):**

> «Ustedes ni siquiera han estado sentados en la mesa donde se tomaban estas decisiones» — challenges Arrimadas' **standing**, not only the VAT policy merits.

**Counterexample:**

> Evidence-based critique of a minister's **policy outcomes** with figures, without personal disqualification → no `FAL_ADHOM` (may still be `PF_ATTACK`).

**Note:** `PF_ATTACK` + `FAL_ADHOM` is common; `PF_ATTACK` without fallacy is valid when critique stays on policy/record with adequate evidential basis.

---

### 7.2 FAL_STRAW — Straw man / distortion

**Definition:** Misrepresents an opponent's position (stronger or weaker), then refutes the **distortion**.

**Example (positive):**

> «Ustedes quieren eliminar todo el sector privado de la sanidad» when opponents proposed regulating one segment only — refuting an exaggerated caricature.

**Counterexample:**

> Fair summary of opponent's published bill text followed by disagreement → not straw man.

---

### 7.3 FAL_DILEMMA — False dilemma

**Definition:** Presents two (or few) **exclusive** options when reasonable alternatives exist.

**Example (positive):**

> «O están con la democracia española o están con el golpismo» — excludes intermediate positions or partial agreements.

**Counterexample:**

> Binary vote on a **genuinely** two-option chamber division (sí/no to a single decree) described procedurally → not a false dilemma in argument.

---

### 7.4 FAL_SLOPE — Slippery slope

**Definition:** Claims an action **inevitably** leads to an extreme outcome without sufficient evidential steps.

**Example (positive):**

> «Si permitimos esta enmienda, acabaremos disolviendo el Estado autonómico por completo» — no intermediate steps demonstrated.

**Counterexample:**

> Cited chain of **documented** legislative precedents with explicit causal reasoning → not slippery slope (may be advocacy).

---

### 7.5 FAL_EMOTION — Appeal to emotion / fear

**Definition:** Replaces or evades evidentiary support with **fear, outrage, or pity** as the primary warrant.

**Example (positive):**

> «Nuestros mayores morirán solos y abandonados» as the **main** reason to reject a bill, without policy engagement with the bill's measures.

**Counterexample:**

> Citing **verified mortality statistics** from poverty-energy studies as evidence in policy advocacy → not emotion fallacy (may be `PF_INFO` / `PF_ADVOCACY`).

---

### 7.6 FAL_GENERAL — Hasty generalization

**Definition:** Generalizes from **unrepresentative or insufficient** evidence.

**Example (positive):**

> «Un municipio gobernado por X colapsó; por tanto, X no puede gobernar España» — single case → national conclusion.

**Counterexample:**

> Aggregate national statistics from official sources applied to a general claim → not hasty generalization.

---

### 7.7 FAL_WHATABOUT — Whataboutism / tu quoque

**Definition:** Deflects criticism by pointing to opponent's **unrelated or symmetric** behaviour without addressing the merit of the original charge.

**Example (positive):**

> When asked about party financing transparency: «Y ustedes, ¿qué dicen del caso Gürtel?» — pivot without answering the question.

**Counterexample:**

> Direct rebuttal with **on-topic** counter-evidence addressing the same policy domain → `PF_DEFENSE`, not whataboutism.

---

### 7.8 FAL_NONE — No fallacy

**Definition:** No fallacy from §7.1–7.7 is present in the span.

**Export:** `fallacy_labels` empty; `fallacy_none_explicit=true`. **Never** combine with any `FAL_*`.

---

## 8. Experimental labels (subset only)

Skip when `experimental_subset=false`.

| ID | Name | Rule |
|----|------|------|
| `SV_0` | Semantic vacuity absent | Specifiable propositional political content |
| `SV_1` | Semantic vacuity present | Slogans, applause lines, content-free assent |
| `SV_UNCLEAR` | Unclear | < **3%** of SV annotations |
| `CA_0` | Conceptual anachronism absent | Terms used in appropriate historical frame |
| `CA_1` | Conceptual anachronism present | Anachronistic projection onto past actors/events |
| `CA_UNCLEAR` | Unclear | < **3%** of CA annotations |

Experimental labels do **not** affect IberLEF leaderboard v1 ranking.

---

## 9. Edge cases compendium

| # | Situation | PF guidance | Fallacy guidance |
|---|-----------|-------------|------------------|
| E1 | Courtesy opener + long policy speech | Label **substance** | Code fallacies in full unit |
| E2 | Presidencia with mild political remark | Still `PF_PROCEDURAL` if agenda management dominates | Usually `FAL_NONE` |
| E3 | Quote of opponent then rebuttal | Label **speaker's move**, not quoted voice | Straw man if speaker distorts quote |
| E4 | Rhetorical question attacking opponent | `PF_ATTACK` | `FAL_EMOTION` only if fear/outrage is primary warrant |
| E5 | Manifesto programmatic list | Often `PF_ADVOCACY` or `PF_PROPOSAL` | Rare fallacies; avoid over-tagging |
| E6 | Social-media post, sarcasm suspected | Code literal move; `irony_possible=true` | Do not guess hidden intent |
| E7 | Policy attack with strong evidence | `PF_ATTACK` | **No** `FAL_ADHOM` if attack stays on merits/record |
| E8 | «Todos los partidos menos nosotros» | Often `PF_ATTACK` or `PF_APPEAL` | Possible `FAL_DILEMMA` if exclusive framing |
| E9 | Voting intention without new commitment | `PF_ADVOCACY` unless explicit pledge → `PF_PROPOSAL` | Usually none |
| E10 | Multi-function long unit (segmentation error) | Pick **dominant** function; flag `borderline` | Top 3 fallacies by salience |
| E11 | Speaker cites statistics from opponents | If correcting → `PF_DEFENSE`; if endorsing → `PF_INFO`/`PF_ADVOCACY` | Rare |
| E12 | Empty or near-empty span | Should not appear in pool; escalate to PI | — |

---

## 10. Adjudication rules

### 10.1 Triggers (mandatory queue)

- Any **pragmatic function** disagreement between annotators A and B.
- Any **fallacy** disagreement when PF already agrees (or after PF adjudicated).
- Any unit with `borderline=true` on PF.
- Gold-item failures below QC thresholds (§11).

### 10.2 Procedure

1. Read `adjudication_context` (prior labels) and ±1 context units.
2. Re-apply decision trees (§4, §6) **without** defaulting to majority vote.
3. Set gold labels using the same controls as primary annotation.
4. Fill **Adjudication notes** with brief rationale, especially when overriding both annotators.
5. Record gold in export: `adjudicated=true`; log label delta in `adjudication_log.jsonl`.
6. Complete within **72 hours** of queue assignment.

### 10.3 Precedence

| Conflict type | Rule |
|---------------|------|
| PF split between advocacy vs attack | Apply §4 tree; check **primary target** (policy vs actor) |
| PF split defense vs attack | **Reactive** → defense; **offensive** → attack |
| PF procedural vs info (chair) | Chair agenda → always procedural |
| Fallacy present vs none | Apply **evidence standard**; when genuinely indeterminate after context, prefer **none** |
| >3 fallacies | Adjudicator selects top 3 by salience |

### 10.4 Ontology changes

Adjudicators **must not** invent labels outside `labels/*.tsv`. Repeated confusion between the same pair (>10% of PF disagreements) triggers ontology/guideline revision (pilot go/no-go rule).

---

## 11. Quality control and reliability

### 11.1 Targets

| Task | Metric | Codebook target | MVP release floor |
|------|--------|-----------------|-------------------|
| Pragmatic function | Cohen's κ | **> 0.80** | ≥ 0.67 |
| Pragmatic function | Krippendorff's α | **> 0.80** | ≥ 0.70 |
| Fallacy (multi-label) | Macro-F1 (pairs) | ≥ 0.60 | ≥ 0.48 |
| Fallacy presence (binary) | Cohen's κ | ≥ 0.70 | ≥ 0.52 |

### 11.2 Training protocol (to reach κ > 0.80)

1. Read this codebook and `annotation/labelstudio/instructions.md`.
2. Complete **5 practice units** (excluded from κ) with group review.
3. Annotate pilot batch; review disagreements with lead annotator.
4. Do **not** begin production until pilot PF κ ≥ 0.67; recalibrate if below.
5. Monthly refresher on top confusion pairs from disagreement reports.

### 11.3 Hidden gold items

Maintain ≥ **85%** agreement on PF and ≥ **75%** on fallacies on 5% hidden gold subset during production.

### 11.4 Borderline budget

`borderline=true` on PF expected ≤ **5%** of submissions; higher rates trigger guideline clarification.

---

## 12. Quick reference — label IDs

### Pragmatic function

| ID | Name |
|----|------|
| `PF_ADVOCACY` | Policy advocacy |
| `PF_ATTACK` | Position attack |
| `PF_DEFENSE` | Defense / rebuttal |
| `PF_PROPOSAL` | Proposal / commitment |
| `PF_APPEAL` | Mobilization appeal |
| `PF_INFO` | Informational |
| `PF_DEFLECT` | Deflection / evasion |
| `PF_PROCEDURAL` | Ritual / procedural |

### Fallacies

| ID | Name |
|----|------|
| `FAL_ADHOM` | Ad hominem |
| `FAL_STRAW` | Straw man / distortion |
| `FAL_DILEMMA` | False dilemma |
| `FAL_SLOPE` | Slippery slope |
| `FAL_EMOTION` | Appeal to emotion / fear |
| `FAL_GENERAL` | Hasty generalization |
| `FAL_WHATABOUT` | Whataboutism / tu quoque |
| `FAL_NONE` | No fallacy (explicit) |

---

## 13. Related files

| Path | Content |
|------|---------|
| `labels/pragmatic_functions.tsv` | PF ontology (machine-readable) |
| `labels/fallacies.tsv` | Fallacy ontology |
| `annotation/guidelines/pragmatic_function_examples.md` | Extended ParlaMint worked examples |
| `annotation/labelstudio/instructions.md` | Label Studio UI workflow |
| `annotation/pilot_001/pilot_protocol.md` | Pilot workflow |
| `scripts/analysis/compute_cohen_kappa.py` | Agreement analysis toolkit |

---

## Revision history

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-06-18 | Initial complete codebook: PF + fallacies, decision trees, adjudication, IA target κ > 0.80 |
