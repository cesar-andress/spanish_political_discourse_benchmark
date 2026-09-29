# Rehydration (v1.0.0)

1. Clone the GitHub repository at tag `v1.0.0` (or download the Zenodo archive).
2. `python -m venv .venv && source .venv/bin/activate && pip install -e ".[dev]"`.
3. Verify Wave-1 CSVs under `annotation/pilot_001/` and `releases/v1.0.0/`.
4. Run `make test` and reproduce agreement metrics per `docs/REPRODUCIBILITY.md`.
5. Optional: place ParlaMint TEI under `data/raw/parlamint/` to regenerate samples.
