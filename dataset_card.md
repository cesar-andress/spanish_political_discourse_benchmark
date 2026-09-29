---
language:
  - es
license: cc-by-4.0
pretty_name: SPDB — Spanish Political Discourse Annotation Resource
tags:
  - political-discourse
  - pragmatics
  - pragmatic-function
  - spanish
  - parliamentary-discourse
  - inter-annotator-agreement
  - language-resources
size_categories:
  - n<1K
task_categories:
  - text-classification
dataset_info:
  features:
    - name: unit_id
      dtype: string
    - name: text
      dtype: string
    - name: pragmatic_function
      dtype: string
    - name: speaker_name
      dtype: string
    - name: speaker_party
      dtype: string
    - name: date
      dtype: string
---

# SPDB dataset card (v1.0.0)

Diagnostic pragmatic-function annotation resource for Spanish parliamentary discourse.

- Pool used for sampling: N = 878 ParlaMint-derived units
- Wave-1 double-coded pilot: N = 100 (seed = 42)
- Not an adjudicated gold split; no train/dev/test production partitions in this release
- codebook-v1.1.0 included as unvalidated revision documentation

See README.md and docs/release_notes_v1.0.0.md.
