# Data dictionary (SPDB v1.0.1)

Concise variable reference for public Wave-1 and release artefacts.

## Wave-1 annotation CSVs (`annotation/pilot_001/`)

| Field | Type | Description |
|-------|------|-------------|
| `unit_id` | string | Stable SPDB unit identifier |
| `text` | string | Unit text (ParlaMint-derived; CC BY 4.0 with attribution) |
| `speaker_name` | string | Speaker display name from ParlaMint metadata |
| `speaker_party` | string | Party / role label when available |
| `date` | date | Session date |
| `pragmatic_function` | enum | One of eight `PF_*` labels (Wave-1 / codebook-v1.0.0) |
| `notes` / free-text columns | string | Optional coder notes (may be empty) |

## Disagreement taxonomy (`annotation/pilot_001/results/disagreement_taxonomy.csv`)

| Field | Description |
|-------|-------------|
| `unit_id` | Disagreement unit |
| `daniel_label` / `jose_jaime_label` | Wave-1 human coder labels |
| `label_pair` | Ordered pair string |
| `cause_primary` | Exploratory post-hoc diagnostic classification generated with AI-assisted workflow support; **not** independently human-verified |
| `codebook_sections` | Relevant guideline sections referenced in the diagnostic note |
| `rationale` | Short interpretive diagnostic note |
| `text_preview` | Truncated unit text for inspection |

See `annotation/pilot_001/results/disagreement_taxonomy.provenance.json` and
`annotation/pilot_001/results/README.md`.

## Release JSONL units (`releases/*/samples/*.jsonl`)

Core fields: `unit_id`, `text`, `document_id`, `language`, `character_count`,
`token_count`, `metadata`, `provenance` (includes `license_status`, source file).

Schemas: [`schemas/`](../schemas/).
