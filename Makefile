.PHONY: dataset-inventory

PYTHON ?= python3

dataset-inventory:
	$(PYTHON) code/src/discourse_classifier/dataset_inventory.py
