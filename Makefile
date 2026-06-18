.PHONY: ingest segment validate test pipeline pipeline-fixture check-ingest-input
.PHONY: ingest-parlamint parlamint-100 validate-parlamint-100

PYTHON ?= python3.11
INTERMEDIATE ?= data/intermediate/parliament_documents.jsonl
PROCESSED ?= data/processed/discourse_units.jsonl
PIPELINE_FIXTURE_INPUT = tests/fixtures/pipeline/sample_parliament_documents.jsonl

PARLAMINT_RAW ?= data/raw/parlamint
PARLAMINT_INTERMEDIATE = data/intermediate/parlamint_documents.jsonl
PARLAMINT_ALL_UNITS = data/processed/parlamint_all_units.jsonl
PARLAMINT_100 = data/processed/parlamint_100_units.jsonl
PARLAMINT_LIMIT ?= 200
PARLAMINT_SAMPLE_N ?= 100
PARLAMINT_SAMPLE_SEED ?= 42

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
		--output $(PARLAMINT_INTERMEDIATE) \
		--limit-documents $(PARLAMINT_LIMIT)

parlamint-100: ingest-parlamint
	$(PYTHON) -m scripts.segmentation.segment_discourse_units \
		--input $(PARLAMINT_INTERMEDIATE) \
		--output $(PARLAMINT_ALL_UNITS)
	$(PYTHON) -m scripts.sampling.sample_units \
		--input $(PARLAMINT_ALL_UNITS) \
		--output $(PARLAMINT_100) \
		--n $(PARLAMINT_SAMPLE_N) \
		--seed $(PARLAMINT_SAMPLE_SEED)

validate-parlamint-100:
	$(PYTHON) -m scripts.validation.validate_dataset \
		--input $(PARLAMINT_100) \
		--allow-real-data

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests/ scripts/ingestion/tests/ scripts/segmentation/tests/ -q

dataset-inventory:
	$(PYTHON) code/src/discourse_classifier/dataset_inventory.py
