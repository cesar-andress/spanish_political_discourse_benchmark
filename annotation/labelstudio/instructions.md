# SPDB v1 — Label Studio annotation instructions

**Project:** Spanish Political Discourse Benchmark (SPDB) v1  
**Configuration:** `annotation/labelstudio/config.xml`  
**Label ontology:** `labels/*.tsv`  
**Canonical spec:** `docs/dataset_documentation/v1_build_specification.md` (§5–§6, §8–§9)

These instructions describe how to use the Label Studio project. They do **not** contain annotated examples.

---

## 1. Purpose

Annotators label **discourse units** — short spans of Spanish political text — with:

1. **Pragmatic function** (single label, required)
2. **Political fallacies** (multi-label or explicit none, required)
3. **Semantic vacuity** (single label, experimental arm only)
4. **Conceptual anachronism** (single label, experimental arm only)

Language of the **text** is Spanish. Label IDs and definitions follow the English operational definitions in the v1 specification.

---

## 2. Task modes

Each imported task includes `task_type`:

| Value | Who | Goal |
|-------|-----|------|
| `primary` | Annotators | First-pass (or second-pass double coding) labels |
| `adjudication` | PI / lead annotator / adjudicator | Set **gold** labels after disagreement |

### 2.1 Primary annotation

- Complete steps **1 → 2** for every task.
- Complete step **3** only when `experimental_subset` is `true`.
- Ignore the adjudication panel content (it should be empty).

### 2.2 Adjudication workflow

Adjudication tasks are created when:

- `borderline=true` on pragmatic function, or
- Inter-annotator disagreement on pragmatic function or fallacies (§6 rule 5, §9.3)

**Procedure:**

1. Read the **Adjudication** panel (`adjudication_context`), which summarizes prior annotator labels.
2. Re-read the unit and ±1 context units.
3. Set gold labels using the **same** controls as primary annotation (steps 1–3).
4. Fill **Adjudication notes** with a brief rationale, especially when overriding both annotators.
5. Submit — exported gold labels replace conflicting primary annotations in the build pipeline.

Target turnaround: **72 hours** from queue assignment (§6 rule 5).

---

## 3. Interface order

Follow the numbered sections in the labeling UI (matches §8.2):

```
Context (read-only)
  → Adjudication panel (if task_type=adjudication)
  → 1. Pragmatic function
  → 2. Fallacies
  → 3. Experimental labels (if experimental_subset=true)
  → Quality flags
```

---

## 4. Task 1 — Pragmatic function (single-label)

**Control name:** `pragmatic_function`  
**Cardinality:** exactly **one** label per unit (§5.1)

| label_id | label_name |
|----------|------------|
| `PF_ADVOCACY` | Policy advocacy |
| `PF_ATTACK` | Position attack |
| `PF_DEFENSE` | Defense / rebuttal |
| `PF_PROPOSAL` | Proposal / commitment |
| `PF_APPEAL` | Mobilization appeal |
| `PF_INFO` | Informational |
| `PF_DEFLECT` | Deflection / evasion |
| `PF_PROCEDURAL` | Ritual / procedural |

**Rules:**

- Select the **dominant** function toward the primary political target.
- If truly tied, choose the function directed at the primary target and enable **Borderline PF case**.
- Borderline cases should be **≤5%** of submissions (§5.1).
- Pragmatic function is **independent** of fallacy labels (§6 rule 4).

Definitions: see `labels/pragmatic_functions.tsv`.

---

## 5. Task 2 — Political fallacies (multi-label)

**Control names:** `fallacy_labels`, `fallacy_none_explicit`  
**Cardinality:** zero to three fallacy labels, **or** explicit none (§5.2)

| label_id | label_name |
|----------|------------|
| `FAL_ADHOM` | Ad hominem |
| `FAL_STRAW` | Straw man / distortion |
| `FAL_DILEMMA` | False dilemma |
| `FAL_SLOPE` | Slippery slope |
| `FAL_EMOTION` | Appeal to emotion / fear |
| `FAL_GENERAL` | Hasty generalization |
| `FAL_WHATABOUT` | Whataboutism / tu quoque |
| `FAL_NONE` | No fallacy (via `fallacy_none_explicit=true`) |

**Rules:**

- Label a fallacy only if a minimally competent reader would agree it is present **in the span** (§6 rule 1).
- You may read **±1 adjacent unit** from the same `document_id` (shown as context); no external web context (§6 rule 2).
- **Maximum three** fallacy labels; if more are suspected, keep the top three by salience (§5.2).
- If **no fallacy** is present: select **No fallacy present (FAL_NONE)** and leave `fallacy_labels` empty.
- **Do not combine** `FAL_NONE` with any `FAL_*` label (§5.2).
- Do not infer speaker intent beyond text + minimal in-document context (§5.2).

Definitions: see `labels/fallacies.tsv`.

---

## 6. Task 3a — Semantic vacuity (experimental)

**Control name:** `semantic_vacuity`  
**Cardinality:** exactly one label when `experimental_subset=true` (§5.3)

| label_id | label_name |
|----------|------------|
| `SV_0` | Semantic vacuity absent |
| `SV_1` | Semantic vacuity present |
| `SV_UNCLEAR` | Semantic vacuity unclear |

**Rules:**

- Skip this section when `experimental_subset` is `false`.
- `SV_UNCLEAR`: use sparingly (**&lt;3%** per label) (§5.3).
- Experimental arm: 2,000 units, 100% double-annotated (§9.1).

Definitions: see `labels/semantic_vacuity.tsv`.

---

## 7. Task 3b — Conceptual anachronism (experimental)

**Control name:** `conceptual_anachronism`  
**Cardinality:** exactly one label when `experimental_subset=true` (§5.3)

| label_id | label_name |
|----------|------------|
| `CA_0` | Conceptual anachronism absent |
| `CA_1` | Conceptual anachronism present |
| `CA_UNCLEAR` | Conceptual anachronism unclear |

**Rules:**

- Same applicability and `*_UNCLEAR` frequency cap as semantic vacuity (§5.3).

Definitions: see `labels/conceptual_anachronism.tsv`.

---

## 8. Quality flags

| Control | Purpose |
|---------|---------|
| `borderline` | PF tie-break / borderline pragmatic function (§5.1) |
| `irony_possible` | Sarcasm/irony suspected — **analysis flag only**, not a training label (§6 rule 3) |
| `adjudication_notes` | Free-text rationale on adjudication tasks (§9.3) |

---

## 9. Expected task JSON (import)

Minimal primary task:

```json
{
  "data": {
    "instance_id": "spdb-v1-unassigned-abc123",
    "document_id": "congreso-2023-001",
    "text": "…Spanish unit text…",
    "context_prev": "",
    "context_next": "",
    "task_type": "primary",
    "experimental_subset": "false",
    "adjudication_context": "",
    "source_type": "parliamentary",
    "source_corpus": "congreso_es",
    "party_family": "PSOE",
    "date": "2023-07-12"
  }
}
```

Adjudication task (prior labels rendered into HTML by the import script):

```json
{
  "data": {
    "instance_id": "spdb-v1-unassigned-abc123",
    "document_id": "congreso-2023-001",
    "text": "…Spanish unit text…",
    "context_prev": "…",
    "context_next": "…",
    "task_type": "adjudication",
    "experimental_subset": "false",
    "adjudication_context": "<p><b>Annotator A</b>: PF=PF_ATTACK; fallacies=[FAL_ADHOM]</p><p><b>Annotator B</b>: PF=PF_DEFENSE; fallacies=[]</p>",
    "source_type": "parliamentary",
    "source_corpus": "congreso_es",
    "party_family": "PSOE",
    "date": "2023-07-12"
  }
}
```

Experimental task: set `"experimental_subset": "true"` and complete section 3.

---

## 10. Export mapping

Label Studio exports must be post-processed to SPDB JSONL schema (`schemas/discourse_unit.schema.json`):

| Label Studio result | SPDB field |
|---------------------|------------|
| `pragmatic_function` | `pragmatic_function` |
| `fallacy_labels` (list) | `fallacy_labels` |
| `fallacy_none_explicit` = true | `fallacy_labels=[]`, `fallacy_none_explicit=true` |
| `semantic_vacuity` | `semantic_vacuity` |
| `conceptual_anachronism` | `conceptual_anachronism` |
| `borderline` | stored in annotation metadata / adjudication trigger |
| `irony_possible` | analysis metadata (not a core leaderboard label) |
| `adjudication_notes` | `adjudication_log.jsonl` entry (IDs + notes, no text) |

Set on export:

- `annotated=true`
- `adjudicated=true` when `task_type=adjudication`
- `guideline_version` per frozen protocol (§8.5)

Exports land in `data/processed/annotations/` (§8.2).

---

## 11. Quality control reminders

- **Gold items (5% hidden):** maintain ≥85% agreement on PF, ≥75% on fallacies (§8.5).
- **Double annotation:** 20% of core units (§9.1).
- **Disagreement path:** pair disagreement → lead annotator third pass → PI adjudication if persistent (§9.3).
- Do not use test-split units for guideline iteration after test lock (§9.4).

---

## 12. Related files

| Path | Content |
|------|---------|
| `labels/pragmatic_functions.tsv` | PF ontology |
| `labels/fallacies.tsv` | Fallacy ontology |
| `labels/semantic_vacuity.tsv` | SV ontology |
| `labels/conceptual_anachronism.tsv` | CA ontology |
| `protocol/coding_scheme.md` | Coding scheme (mirror of spec) |
| `protocol/annotation_protocol.md` | Workflow protocol |
| `protocol/inter_annotator_agreement_plan.md` | IA metrics and sampling |

---

## Document control

| Version | Date | Change |
|---------|------|--------|
| 1.0 | 2026-06-18 | Initial Label Studio config + instructions for SPDB v1 |
