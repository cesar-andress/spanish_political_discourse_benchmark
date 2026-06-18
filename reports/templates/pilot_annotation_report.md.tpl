# SPDB pilot annotation report

**Generated:** {{generated_at}}  
**Random seed:** {{seed}}  
**Annotation status:** `{{status}}`  
**Template:** `{{template_path}}`  
**Annotators:** {{annotator_list}}  
**Units in scope:** {{n_units}}

## Executive summary

{{executive_summary}}

## 1. Agreement analysis

{{agreement_section}}

## 2. Confusion analysis

{{confusion_section}}

## 3. Ontology diagnostics

{{ontology_section}}

## Reproducibility

Re-run the full pipeline with:

```bash
make pilot-analytics {{make_args}}
```

Intermediate artefacts are written to `{{output_dir}}/`.
