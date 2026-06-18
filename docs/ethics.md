# Ethics and responsible use

**Status:** under development (`v0.1.0-dev`)

SPDB documents ethical constraints for collecting, annotating, and redistributing Spanish political text. This is a **living policy**; per-source rows will be completed before annotation wave 2 and before Zenodo v1.0.0.

## Scope of materials

SPDB targets **public political communication**:

- Parliamentary interventions and official party manifestos
- Elite social media by elected officials, party organs, and candidates in official capacity

It does **not** target private citizens' communication or non-public personal data.

## Legal and platform compliance

| Slice | Redistribution approach | Status |
|-------|-------------------------|--------|
| Parliamentary text | Per-source licence documented in `license_ref` | Planned |
| Manifestos | MARPOR terms + per-document clearance | Planned |
| Social media | **IDs-only** public release where ToS restrict text; local rebuild for annotation | Planned |

Detailed matrix: [`dataset_documentation/licensing_and_ethics.md`](dataset_documentation/licensing_and_ethics.md).

## Annotator welfare

- Annotators code political content that may include attacks or inflammatory rhetoric; guidelines include breaks, escalation paths, and adjudication for borderline cases.
- Annotator IDs are pseudonymized in exports; adjudication logs store label deltas without text.

## Misuse considerations

SPDB is intended for research on political discourse structure, annotation quality, and modelling—not for automated targeting of individuals, voter manipulation, or surveillance.

Users must:

- Respect original source licences and platform terms
- Not attempt to re-identify pseudonymized speaker handles beyond what public sources already expose
- Cite SPDB and underlying corpora when publishing derivatives

## Human subjects review

Institutional requirements depend on deployment context. The PI team documents whether formal IRB/ethics review applies to annotation workflows in the jurisdiction of data collection.

## Contact

Ethics or licensing questions: [josejaime.baena@unir.net](mailto:josejaime.baena@unir.net).
