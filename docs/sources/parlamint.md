# ParlaMint source (SPDB parliamentary layer)

| Field | Value |
|-------|-------|
| **Source** | ParlaMint 5.0 (ParlaMint-ES) |
| **Project URL** | https://www.clarin.eu/parlamint |
| **GitHub** | https://github.com/clarin-eric/ParlaMint |
| **CLARIN.SI handle** | https://www.clarin.si/repository/xmlui/handle/11356/2004 |
| **Licence** | **CC BY 4.0** (verified from CLARIN.SI deposit metadata) |
| **Access date (project)** | 2026-06-18 |

## Intended use in SPDB

ParlaMint provides harmonised TEI/XML parliamentary corpora. For SPDB it is the
parliamentary source layer:

- utterance-level `<u>` elements with speaker metadata;
- session dates and identifiers;
- person and party registries (`listPerson`, `listOrg`);
- Spanish coverage via `ParlaMint-ES` (Congreso de los Diputados).

The local ingestor writes intermediate JSONL without downloading data automatically.

## Redistribution

ParlaMint 5.0 is licensed **CC BY 4.0**. SPDB may redistribute derived unit texts
in release samples and Wave-1 packages provided that:

1. ParlaMint / CLARIN.SI attribution is retained;
2. the CC BY 4.0 notice remains visible (see repository `LICENSE`);
3. provenance fields record the upstream source file and licence.

Released JSONL units use `provenance.license_status = "CC-BY-4.0"` with a
ParlaMint attribution note.

## Local acquisition (manual)

Place TEI/XML session files and registries under `data/raw/parlamint/`:

```text
data/raw/parlamint/
  ParlaMint-ES-listPerson.xml
  ParlaMint-ES-listOrg.xml
  ParlaMint-ES_2017-11-28-CD171128.xml
  ...
```

Then run:

```bash
make ingest-parlamint
make segment-parlamint
make parlamint-100
make validate-parlamint-100
```

Processed pool files under `data/processed/` are gitignored; release samples under
`releases/` and Wave-1 CSVs under `annotation/pilot_001/` are the public units.
