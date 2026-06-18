.PHONY: ingest segment validate test pipeline pipeline-fixture check-ingest-input

PYTHON ?= python3.11
INTERMEDIATE ?= data/intermediate/parliament_documents.jsonl
PROCESSED ?= data/processed/discourse_units.jsonl
PIPELINE_FIXTURE_INPUT = tests/fixtures/pipeline/sample_parliament_documents.jsonl

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

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests/ scripts/ingestion/tests/ scripts/segmentation/tests/ -q

dataset-inventory:
	$(PYTHON) code/src/discourse_classifier/dataset_inventory.py
