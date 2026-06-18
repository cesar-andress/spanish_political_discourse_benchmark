.PHONY: ingest segment validate test pipeline pipeline-fixture check-ingest-input release-validate artifact-audit pilot-analytics ontology-validation
.PHONY: ingest-parlamint segment-parlamint parlamint-100 validate-parlamint-100
.PHONY: parlamint-500 validate-parlamint-500 pilot-agreement

PYTHON ?= python3.11
INTERMEDIATE ?= data/intermediate/parliament_documents.jsonl
PROCESSED ?= data/processed/discourse_units.jsonl
PIPELINE_FIXTURE_INPUT = tests/fixtures/pipeline/sample_parliament_documents.jsonl

PARLAMINT_RAW ?= data/raw/parlamint
PARLAMINT_INTERMEDIATE = data/intermediate/parlamint_documents.jsonl
PARLAMINT_UNITS = data/processed/parlamint_units.jsonl
PARLAMINT_100 = data/processed/parlamint_100_units.jsonl
PARLAMINT_500 = data/processed/parlamint_500_units.jsonl
PARLAMINT_500_REPORT = reports/parlamint_500_sampling_report.md
PARLAMINT_SAMPLE_N ?= 100
PARLAMINT_SAMPLE_SEED ?= 42
PARLAMINT_500_N ?= 500
PARLAMINT_500_SEED ?= 42
PARLAMINT_500_MAX_PER_SPEAKER ?= 5

check-ingest-input:
ifndef INGEST_INPUT
	$(error INGEST_INPUT is required for real pipeline runs. Example: make pipeline INGEST_INPUT=data/raw/parliamentary/interventions.jsonl. For tests, use: make pipeline-fixture)
endif

ingest: check-ingest-input
	$(PYTHON) -m scripts.ingestion.ingest_parliament \
		--input $(INGEST_INPUT) \
		--output $(INTERMEDIATE)

segment:
	$(PYTHON) -m scripts.segmentation.segment_discourse_units \
		--input $(INTERMEDIATE) \
		--output $(PROCESSED)

validate:
	$(PYTHON) -m scripts.validation.validate_dataset \
		--input $(PROCESSED) \
		$(if $(ALLOW_FIXTURES),--allow-fixtures,)

pipeline: check-ingest-input ingest segment validate

pipeline-fixture:
	$(MAKE) ingest INGEST_INPUT=$(PIPELINE_FIXTURE_INPUT)
	$(MAKE) segment
	$(MAKE) validate ALLOW_FIXTURES=1

ingest-parlamint:
	@test -d "$(PARLAMINT_RAW)" || (echo "Missing $(PARLAMINT_RAW). See docs/sources/parlamint.md" && exit 1)
	$(PYTHON) -m scripts.ingestion.ingest_parlamint \
		--input $(PARLAMINT_RAW) \
		--output $(PARLAMINT_INTERMEDIATE)

segment-parlamint:
	$(PYTHON) -m scripts.segmentation.segment_discourse_units \
		--input $(PARLAMINT_INTERMEDIATE) \
		--output $(PARLAMINT_UNITS)

parlamint-100:
	$(PYTHON) -m scripts.sampling.sample_units \
		--input $(PARLAMINT_UNITS) \
		--output $(PARLAMINT_100) \
		--n $(PARLAMINT_SAMPLE_N) \
		--seed $(PARLAMINT_SAMPLE_SEED)

validate-parlamint-100:
	$(PYTHON) -m scripts.validation.validate_dataset \
		--input $(PARLAMINT_100) \
		--allow-real-data

parlamint-500:
	$(PYTHON) -m scripts.analysis.parlamint_500_sampling_report \
		--input $(PARLAMINT_UNITS) \
		--output $(PARLAMINT_500) \
		--report $(PARLAMINT_500_REPORT) \
		--n $(PARLAMINT_500_N) \
		--seed $(PARLAMINT_500_SEED) \
		--max-per-speaker $(PARLAMINT_500_MAX_PER_SPEAKER)

validate-parlamint-500:
	$(PYTHON) -m scripts.validation.validate_dataset \
		--input $(PARLAMINT_500) \
		--allow-real-data

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests/ analysis/pilot/tests/ analysis/ontology_validation/tests/ scripts/ingestion/tests/ scripts/segmentation/tests/ scripts/sampling/tests/ scripts/analysis/tests/ -q

release-validate:
	$(PYTHON) scripts/release/validate_release_metadata.py

ARTIFACT_AUDIT_INPUT ?= tests/fixtures/annotation/artifact_audit_sample.csv

artifact-audit:
	$(PYTHON) -m scripts.analysis.artifact_audit \
		--input $(ARTIFACT_AUDIT_INPUT) \
		--markdown reports/artifact_audit.md \
		--figures-dir figures/artifact_audit

PILOT_ANNOTATOR_A ?= annotation/pilot_001/pilot_100_units_annotator_a.csv
PILOT_ANNOTATOR_B ?= annotation/pilot_001/pilot_100_units_annotator_b.csv
PILOT_ANNOTATOR_C ?= annotation/pilot_001/pilot_100_units_annotator_c.csv
PILOT_TEMPLATE ?= annotation/pilot_001/pilot_100_units.csv
PILOT_RESULTS = annotation/pilot_001/results
PILOT_FIXTURE_A = tests/fixtures/annotation/pilot_annotator_a.csv
PILOT_FIXTURE_B = tests/fixtures/annotation/pilot_annotator_b.csv
PILOT_FIXTURE_C = tests/fixtures/annotation/pilot_annotator_c.csv
PILOT_FIXTURE_TEMPLATE = tests/fixtures/annotation/pilot_template.csv

pilot-analytics:
	$(PYTHON) -m scripts.analysis.pilot_analytics \
		--template $(PILOT_TEMPLATE) \
		$(if $(filter 1,$(PILOT_USE_FIXTURES)),--annotator $(PILOT_FIXTURE_A) --annotator $(PILOT_FIXTURE_B) --annotator $(PILOT_FIXTURE_C),) \
		$(if $(wildcard $(PILOT_ANNOTATOR_A)),--annotator $(PILOT_ANNOTATOR_A),) \
		$(if $(wildcard $(PILOT_ANNOTATOR_B)),--annotator $(PILOT_ANNOTATOR_B),) \
		$(if $(wildcard $(PILOT_ANNOTATOR_C)),--annotator $(PILOT_ANNOTATOR_C),) \
		--output-dir reports/pilot \
		--report reports/pilot_annotation_report.md \
		--figures-dir figures/pilot \
		--seed 42

pilot-analytics-fixtures:
	$(PYTHON) -m scripts.analysis.pilot_analytics \
		--template $(PILOT_FIXTURE_TEMPLATE) \
		--annotator $(PILOT_FIXTURE_A) \
		--annotator $(PILOT_FIXTURE_B) \
		--annotator $(PILOT_FIXTURE_C) \
		--output-dir reports/pilot \
		--report reports/pilot_annotation_report.md \
		--figures-dir figures/pilot \
		--seed 42

ontology-validation:
	$(PYTHON) -m scripts.analysis.ontology_validation \
		--template $(PILOT_TEMPLATE) \
		$(if $(wildcard $(PILOT_ANNOTATOR_A)),--annotator $(PILOT_ANNOTATOR_A),) \
		$(if $(wildcard $(PILOT_ANNOTATOR_B)),--annotator $(PILOT_ANNOTATOR_B),) \
		$(if $(wildcard $(PILOT_ANNOTATOR_C)),--annotator $(PILOT_ANNOTATOR_C),) \
		--output-dir reports/ontology_validation \
		--figures-dir figures/ontology_validation \
		--seed 42

ontology-validation-fixtures:
	$(PYTHON) -m scripts.analysis.ontology_validation --fixtures \
		--output-dir reports/ontology_validation \
		--figures-dir figures/ontology_validation \
		--seed 42

pilot-agreement:
	$(PYTHON) -m scripts.analysis.compute_cohen_kappa \
		--annotator-a $(PILOT_ANNOTATOR_A) \
		--annotator-b $(PILOT_ANNOTATOR_B) \
		--output-dir $(PILOT_RESULTS)
	$(PYTHON) -m scripts.analysis.compute_krippendorff_alpha \
		--annotator-a $(PILOT_ANNOTATOR_A) \
		--annotator-b $(PILOT_ANNOTATOR_B) \
		--output-dir $(PILOT_RESULTS)
	$(PYTHON) -m scripts.analysis.compute_confusion_matrix \
		--annotator-a $(PILOT_ANNOTATOR_A) \
		--annotator-b $(PILOT_ANNOTATOR_B) \
		--output-dir $(PILOT_RESULTS)
	$(PYTHON) -m scripts.analysis.generate_disagreement_report \
		--annotator-a $(PILOT_ANNOTATOR_A) \
		--annotator-b $(PILOT_ANNOTATOR_B) \
		--output-dir $(PILOT_RESULTS)

dataset-inventory:
	$(PYTHON) code/src/discourse_classifier/dataset_inventory.py
