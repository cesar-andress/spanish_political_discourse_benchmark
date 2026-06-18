# Human-vs-LLM analysis pending

Human annotation files are not yet available. Run this analysis again once the following files exist:

- `annotation/pilot_001/pilot_100_units_annotator_a.csv`
- `annotation/pilot_001/pilot_100_units_annotator_b.csv`
- `annotation/pilot_001/pilot_100_units_annotator_c.csv`

Optional adjudicated gold:

- `annotation/pilot_001/pilot_100_units_adjudicated.csv`

Expected LLM outputs (one per model):

- `data/experiments/llm_annotations/{MODEL_NAME}_pilot_100.jsonl`

When ready:

```bash
make human-vs-llm
```
