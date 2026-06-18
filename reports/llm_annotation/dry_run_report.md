# SPDB LLM annotation — dry run report

**Model placeholder:** `dry-run-mock`  
**Prompt mode:** `zero_shot`  
**Pilot units loaded:** 100  
**Validation status:** OK

## Summary

Dry-run mode builds prompts for the 100-unit pilot, applies deterministic mock responses, and validates JSON output against `schemas/llm_annotation_output.schema.json`. No external or paid API is called.

| Check | Result |
|-------|--------|
| Expected units | 100 |
| Mock records validated | 100 |
| Parse failure rate | 0.000 |
| Invalid label rate | 0.000 |
| Missing unit_id | 0 |
| Duplicate unit_id | 0 |

## Sample prompt (first unit)

```text
You are annotating Spanish political discourse for the SPDB benchmark.

## Task — pragmatic function (exactly one label)

Select **exactly one** `PF_*` label for the discourse unit below.

### Label inventory

- `PF_ADVOCACY`
- `PF_ATTACK`
- `PF_DEFENSE`
- `PF_PROPOSAL`
- `PF_APPEAL`
- `PF_INFO`
- `PF_DEFLECT`
- `PF_PROCEDURAL`

### Rules

- Output **one** pragmatic function only (`PF_*`).
- Do **not** include explanations, rationale, or commentary unless the output schema explicitly includes an optional `rationale` field and you are instructed to fill it.
- Return **only** valid JSON matching the required output schema.

### Discourse unit

- unit_id: spdb-v1-unassigned-783020218722
- speaker_name: Inés Arrimadas García
- speaker_party: Cs
- date: 2020-11-12
- text:
"""
Así pasa, que aparece un partido que se sienta a negociar con ambos, como hacen los liberales europeos, que negocian con los conservadores y con los socialdemócratas, y todo el mundo: Oh, ¿qué es esto? Es un ovni. No, es política y no politiqueo bipartidista, que es a lo que ustedes nos tienen acostumbrados desde hace cuarenta años. ¿Qué hemos hecho nosotros para no presentar una enmienda a la totalidad? Presentar líneas naranjas al Gobierno y no centrarnos en Twitter, en gritar mucho o en convocar manifestaciones para que la gente se vaya a tocar el claxon por la Castellana. No, hemos hecho un trabajo discreto, de hormiguita, presentando al Gobierno unas líneas naranjas y diciéndole que, si quiere que estemos en la negociación de presupuestos, estas locuras no pueden estar en el proyecto. Es una lástima que no esté el señor Echenique - no sé si es que no quería escuchar nuestro discurso -, porque le he visto un poco molesto. Ha dedicado la mitad de su discurso a hablar de Ciudadanos y ha dicho que no hemos conseguido nada. Pues para no haber conseguido nada, que Echenique haya dedicado la mitad de su discurso a hablar de nosotros es un poco desproporcionado, ¿no? Lo entiendo. Para el señor Echenique no tiene que ser plato de buen gusto darse cuenta de que no lo han visto venir. Lo entiendo. Pero, miren, vamos a decir cosas que ha anunciado el Gobierno, cosas que ha llevado en su programa electoral o cosas que han dado por hecho que iban a hacer y que finalmente no están en el proyecto de presupuestos, que son líneas naranjas. Por ejemplo, este Gobierno quería gravar con el 21 % de IVA a la educación concertada, a la especial y también a la sanidad que no fuera exclusivamente pública. ¿Por qué?
"""

### Required JSON output shape

```json
{
  "unit_id": "spdb-v1-unassigned-783020218722",
  "model_name": "dry-run-mock",
  "pragmatic_function": "PF_*",
  "fallacy_labels": ["FAL_*"],
  "confidence": 0.0,
  "rationale": ""
}
```

Replace `PF_*` with exactly one inventory label. For fallacy labels use the fallacy task rules (may be filled in a combined pass).

## Task — political fallacies (zero or more labels)

Annotate **fallacy_labels** for the same discourse unit.

### Fallacy inventory

- `FAL_ADHOM`
- `FAL_STRAW`
- `FAL_DILEMMA`
- `FAL_SLOPE`
- `FAL_EMOTION`
- `FAL_GENERAL`
- `FAL_WHATABOUT`
- `FAL_NONE` (use alone when no fallacy is present)

### Rules

- Select **zero or more** fallacy labels (`FAL_*`) present in the unit (max 3 by salience).
- If **no fallacy** is present, output `"fallacy_labels": ["FAL_NONE"]` only.
- **Never** combine `FAL_NONE` with any other fallacy label.
- Do **not** include explanations unless optional `rationale` is explicitly requested.
- Return labels only; no free-text analysis outside the JSON object.

### FAL_NONE handling

| Situation | fallacy_labels |
|-----------|----------------|
| No fallacy detected | `["FAL_NONE"]` |
| One or more fallacies | `["FAL_ADHOM", ...]` (max 3, no `FAL_NONE`) |

### Required JSON fields (combined with pragmatic function)

```json
{
  "unit_id": "spdb-v1-unassigned-783020218722",
  "model_name": "dry-run-mock",
  "pragmatic_function": "PF_*",
  "fallacy_labels": ["FAL_*"],
  "confidence": 0.0
```

## Next step — local model run

```bash
make llm-annotation-local MODEL_NAME=llama-local BACKEND_COMMAND="ollama run llama3"
```
