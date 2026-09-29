# SPDB Fallacy Ontology Mapping

Mapping between SPDB v1 political-fallacy labels and external dataset schemes.

**SPDB labels:** `FAL_ADHOM`, `FAL_STRAW`, `FAL_DILEMMA`, `FAL_SLOPE`, `FAL_EMOTION`, `FAL_GENERAL`, `FAL_WHATABOUT`, `FAL_NONE`

**Status:** planning document only. No labels have been projected or evaluated.

## FallacyES-Political (`fallacyes_political`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | Ad Hominem | **exact** | Direct label correspondence. |
| `FAL_ADHOM` | Poisoning the Well | **partial** | Both attack speaker credibility; SPDB requires personal disqualification salience. |
| `FAL_ADHOM` | Guilt by Association | **approximate** | Associative attack; may map to ad hominem or attack PF layer depending on span. |
| `FAL_STRAW` | Strawman | **exact** | Direct label correspondence. |
| `FAL_DILEMMA` | False Dilemma | **exact** | Direct label correspondence. |
| `FAL_SLOPE` | Slippery Slope | **exact** | Direct label correspondence. |
| `FAL_EMOTION` | Appeal to Emotion | **exact** | Direct label correspondence. |
| `FAL_EMOTION` | Appeal to Fear | **partial** | Fear is a subtype; SPDB FAL_EMOTION covers fear/outrage/pity warrants. |
| `FAL_EMOTION` | Flag Waving | **partial** | Patriotic emotional appeal; often co-occurs with PF_APPEAL. |
| `FAL_GENERAL` | Hasty Generalization | **exact** | Direct label correspondence. |
| `FAL_GENERAL` | False Cause | **approximate** | Causal overgeneralization; SPDB may code as generalization when leap is explicit. |
| `FAL_GENERAL` | False Analogy | **approximate** | Weak analogy can function as hasty generalization across domains. |
| `FAL_WHATABOUT` | Ad Populum | **approximate** | Populist bandwagon differs; no direct FallacyES-Political whataboutism class. |
| `FAL_WHATABOUT` | Complex Question | **none** | Loaded question structure; not SPDB whataboutism. |
| `FAL_NONE` | Wishful Thinking | **none** | External positive fallacy; SPDB none is explicit absence of fallacy inventory. |
| `FAL_NONE` | (no fallacy in FallacyES controls) | **partial** | Both support explicit non-fallacy baselines but with different export semantics. |

**SPDB labels with at least one mapping row:** 8/8.

## FallacyES (`fallacyes`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | ad hominem | **exact** | LOGIC-derived taxonomy in prototypical section. |
| `FAL_STRAW` | straw man | **exact** | Direct correspondence. |
| `FAL_DILEMMA` | false dilemma | **exact** | Direct correspondence. |
| `FAL_SLOPE` | slippery slope | **exact** | Direct correspondence. |
| `FAL_EMOTION` | appeal to emotion | **exact** | Direct correspondence. |
| `FAL_GENERAL` | hasty generalization | **exact** | Direct correspondence. |
| `FAL_WHATABOUT` | tu quoque | **partial** | Tu quoque overlaps deflection/whataboutism; SPDB requires merit non-engagement. |
| `FAL_WHATABOUT` | appeal to worse problems | **approximate** | Deflection via comparative harm; partial overlap. |
| `FAL_NONE` | non-fallacy controls | **partial** | FallacyES includes non-fallacious controls; export semantics differ from FAL_NONE. |

**SPDB labels with at least one mapping row:** 8/8.

## SemEval-2020 Task 11 (Propaganda Techniques) (`semeval2020_propaganda`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | Name Calling or Labeling | **approximate** | Insult framing; not always ad hominem rejection of claim merits. |
| `FAL_STRAW` | Loaded Language | **none** | Persuasive wording without misrepresentation requirement. |
| `FAL_DILEMMA` | Black-and-white Fallacy / Dictatorship | **partial** | Forced binary framing; SPDB requires exclusion of reasonable alternatives. |
| `FAL_SLOPE` | Causal Oversimplification | **approximate** | Oversimplified causal chain; not always extreme-outcome slope. |
| `FAL_EMOTION` | Appeal to fear-prejudice | **partial** | Fear-based persuasion overlap. |
| `FAL_EMOTION` | Flag-waving | **partial** | Nationalist emotional appeal. |
| `FAL_GENERAL` | Causal Oversimplification | **approximate** | May encode hasty causal claims. |
| `FAL_WHATABOUT` | Whataboutism | **exact** | Direct technique match (propaganda frame). |
| `FAL_NONE` | non-propaganda spans | **partial** | Absence label differs from explicit SPDB FAL_NONE coding. |

**SPDB labels with at least one mapping row:** 8/8.

## Argotario (`argotario`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | ad hominem | **exact** | Direct correspondence. |
| `FAL_STRAW` | straw man | **exact** | Direct correspondence. |
| `FAL_DILEMMA` | false dilemma | **exact** | Direct correspondence. |
| `FAL_SLOPE` | slippery slope | **exact** | Direct correspondence. |
| `FAL_EMOTION` | appeal to emotion | **exact** | Direct correspondence. |
| `FAL_EMOTION` | appeal to fear | **partial** | Fear subtype under SPDB FAL_EMOTION. |
| `FAL_GENERAL` | hasty generalization | **exact** | Direct correspondence. |
| `FAL_WHATABOUT` | whataboutism | **exact** | Direct correspondence. |
| `FAL_WHATABOUT` | tu quoque | **partial** | Closely related deflection pattern. |
| `FAL_NONE` | no fallacy | **partial** | Argotario fallacy vs. non-fallacy distinction; schema differs. |

**SPDB labels with at least one mapping row:** 8/8.

## LOGIC / Logical Fallacy Dataset (`logic`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | ad hominem | **exact** | Direct correspondence. |
| `FAL_STRAW` | straw man | **exact** | Direct correspondence. |
| `FAL_DILEMMA` | false dilemma | **exact** | Direct correspondence. |
| `FAL_SLOPE` | slippery slope | **exact** | Direct correspondence. |
| `FAL_EMOTION` | appeal to emotion | **exact** | Direct correspondence. |
| `FAL_GENERAL` | hasty generalization | **exact** | Direct correspondence. |
| `FAL_WHATABOUT` | tu quoque | **partial** | Partial overlap with SPDB whataboutism. |
| `FAL_NONE` | non-fallacy / intentional | **none** | LOGIC 'intentional' is not SPDB none. |

**SPDB labels with at least one mapping row:** 8/8.

## DIPROMATS (IberLEF 2024) (`dipromats`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | propaganda techniques (various) | **none** | Task labels are propaganda/narrative frames. |
| `FAL_WHATABOUT` | propaganda techniques (various) | **approximate** | Possible overlap at technique level only. |
| `FAL_NONE` | non-propaganda | **none** | No shared explicit none code. |

**SPDB labels with at least one mapping row:** 3/8.

## Multilingual fallacy benchmarks (LLM evaluation literature) (`multifallacy_llm_benchmark`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | corpus-specific ad hominem | **partial** | Requires per-corpus projection table. |
| `FAL_STRAW` | corpus-specific straw man | **partial** | Requires per-corpus projection table. |
| `FAL_DILEMMA` | corpus-specific false dilemma | **partial** | Requires per-corpus projection table. |
| `FAL_SLOPE` | corpus-specific slippery slope | **partial** | Requires per-corpus projection table. |
| `FAL_EMOTION` | corpus-specific appeal to emotion | **partial** | Requires per-corpus projection table. |
| `FAL_GENERAL` | corpus-specific hasty generalization | **partial** | Requires per-corpus projection table. |
| `FAL_WHATABOUT` | corpus-specific whataboutism/tu quoque | **partial** | Requires per-corpus projection table. |
| `FAL_NONE` | corpus-specific non-fallacy | **partial** | Harmonisation needed across sources. |

**SPDB labels with at least one mapping row:** 8/8.

## English parliamentary / debate fallacy resources (`parliamentary_fallacy_en`)

| SPDB label | External label | Match | Rationale |
| --- | --- | --- | --- |
| `FAL_ADHOM` | Ad Hominem | **exact** | Shared construct in debate fallacy sets. |
| `FAL_STRAW` | Straw Man | **partial** | Label naming varies by release. |
| `FAL_DILEMMA` | False Dilemma | **partial** | Institutional debate annotations. |
| `FAL_SLOPE` | Slippery Slope | **partial** | Institutional debate annotations. |
| `FAL_EMOTION` | Appeal to Emotion | **exact** | Multimodal debate datasets include this class. |
| `FAL_GENERAL` | Hasty Generalization | **partial** | Coverage varies by corpus. |
| `FAL_WHATABOUT` | Whataboutism | **approximate** | May appear under deflection labels. |
| `FAL_NONE` | non-fallacy | **partial** | Export semantics differ. |

**SPDB labels with at least one mapping row:** 8/8.

## Match legend

- **exact:** definitions and annotation intent align closely.
- **partial:** substantial overlap with SPDB boundary conditions.
- **approximate:** related construct; projection requires adjudication rules.
- **none:** no meaningful mapping without ontology revision.

