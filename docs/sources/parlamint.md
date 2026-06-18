# ParlaMint source (SPDB development sample)

| Field | Value |
|-------|-------|
| Source name | ParlaMint 5.0 — Spanish (Congreso de los Diputados) |
| Project URL | https://www.clarin.eu/parlamint |
| GitHub | https://github.com/clarin-eric/ParlaMint |
| CLARIN.SI handle | https://www.clarin.si/repository/xmlui/handle/11356/2004 |
| Access date | 2026-06-18 |
| License / status | **To be verified** before any public SPDB release |

## Why ParlaMint fits SPDB

ParlaMint provides harmonised TEI/XML parliamentary corpora with:

- utterance-level segmentation (`<u>` elements) aligned with speaker metadata;
- ISO dates and session identifiers;
- person and party registries (`listPerson`, `listOrg`);
- Spanish coverage for the Congreso de los Diputados (corpus `ParlaMint-ES`).

This makes it suitable for bootstrapping SPDB parliamentary discourse units with documented provenance while the project finalises direct Congreso ingestion.

## Redistribution warning

ParlaMint data is research infrastructure output with its own licence terms (typically CC BY 4.0 for many releases, but **must be confirmed per deposit version**).

**Do not redistribute SPDB slices derived from ParlaMint until:**

1. licence terms for the exact ParlaMint 5.0 Spanish files are verified;
2. downstream citation requirements are documented;
3. SPDB release policy explicitly permits the derived sample.

The ingestor records `provenance.license_status = "to_be_verified"` on every document.

## Local acquisition (manual)

The ingestor **does not download** data. Place files under `data/raw/parlamint/`:

```bash
# Example: copy ParlaMint-ES session TEI files and registries locally
# (obtain from CLARIN.SI handle 11356/2004 or ParlaMint GitHub Samples/ParlaMint-ES)
data/raw/parlamint/
  ParlaMint-ES-listPerson.xml
  ParlaMint-ES-listOrg.xml
  ParlaMint-ES_2017-11-28-CD171128.xml
  ...
```

Then run:

```bash
make ingest-parlamint
make parlamint-100
make validate-parlamint-100
```
