.PHONY: ingest segment validate test pipeline

PYTHON ?= python3.11
INGEST_INPUT ?= scripts/ingestion/tests/fixtures/sample_parliament_documents.jsonl
INTERMEDIATE ?= data/intermediate/parliament_documents.jsonl
PROCESSED ?= data/processed/discourse_units.jsonl

ingest:
	$(PYTHON) -m scripts.ingestion.ingest_parliament \
		--input $(INGEST_INPUT) \
		--output $(INTERMEDIATE)

segment:
	$(PYTHON) -m scripts.segmentation.segment_discourse_units \
		--input $(INTERMEDIATE) \
		--output $(PROCESSED)

validate:
	$(PYTHON) -m scripts.validation.validate_dataset \
		--input $(PROCESSED)

pipeline: ingest segment validate

test:
	PYTHONPATH=. $(PYTHON) -m pytest tests/ scripts/ingestion/tests/ scripts/segmentation/tests/ -q

dataset-inventory:
	$(PYTHON) code/src/discourse_classifier/dataset_inventory.py
