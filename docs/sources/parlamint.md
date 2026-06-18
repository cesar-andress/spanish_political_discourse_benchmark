# ParlaMint source (SPDB parliamentary layer)

| Field | Value |
|-------|-------|
| **Source** | ParlaMint |
| **Project URL** | https://www.clarin.eu/parlamint |
| **GitHub** | https://github.com/clarin-eric/ParlaMint |
| **CLARIN.SI handle (ParlaMint 5.0)** | https://www.clarin.si/repository/xmlui/handle/11356/2004 |
| **Access date** | 2026-06-18 |
| **Status** | License **to be verified** before public release |

## Intended use in SPDB

ParlaMint provides harmonised TEI/XML parliamentary corpora. For SPDB it serves as the
**parliamentary source layer** while direct Congreso ingestion is finalised:

- utterance-level `<u>` elements with speaker metadata;
- session dates and identifiers;
- person and party registries (`listPerson`, `listOrg`);
- Spanish coverage via `ParlaMint-ES` (Congreso de los Diputados).

The local ingestor writes intermediate JSONL without downloading data automatically.

## Redistribution note

**Do not redistribute raw ParlaMint texts or SPDB slices derived from them until:**

1. licence terms for the exact ParlaMint 5.0 Spanish deposit are verified;
2. citation and attribution requirements are documented;
3. SPDB release policy explicitly permits the derived sample.

Every ingested record carries `provenance.license_status = "to_be_verified"`.

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
make parlamint-500
make validate-parlamint-500
```

See `reports/parlamint_500_sampling_report.md` for stratified 500-unit candidate sampling (current pool ceiling: 398 units under speaker cap).
