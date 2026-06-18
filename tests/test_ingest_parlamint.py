from __future__ import annotations

from pathlib import Path

from scripts.ingestion.ingest_parlamint import ingest_parlamint, validate_parlamint_document
from scripts.ingestion.common import read_jsonl, validate_pipeline_discourse_unit
from scripts.segmentation.segment_discourse_units import main as segment_main
from scripts.sampling.sample_units import sample_units
from tests.conftest import FIXTURES

PARLAMINT_FIXTURES = FIXTURES / "parlamint"


def test_parlamint_ingestor_parses_tei_and_preserves_metadata(tmp_path: Path):
    output = tmp_path / "parlamint_documents.jsonl"
    count, errors = ingest_parlamint(PARLAMINT_FIXTURES, output)
    assert errors == []
    assert count == 2

    documents = list(read_jsonl(output))
    chair = documents[0]
    speech = documents[1]

    assert chair["speaker_name"] == "Presidencia"
    assert chair["date"] == "2017-11-28"
    assert chair["provenance"]["license_status"] == "to_be_verified"
    assert not validate_parlamint_document(chair)

    assert speech["speaker_name"] == "Eva García Sempere"
    assert speech["speaker_party"] == "PSOE"
    assert speech["document_id"] == "ParlaMint-ES_test-session.u2"


def test_parlamint_pipeline_generates_valid_units(tmp_path: Path):
    intermediate = tmp_path / "parlamint_documents.jsonl"
    processed = tmp_path / "units.jsonl"
    sample = tmp_path / "sample.jsonl"

    ingest_parlamint(PARLAMINT_FIXTURES, intermediate)
    assert segment_main(["--input", str(intermediate), "--output", str(processed), "--log-level", "ERROR"]) == 0

    units = list(read_jsonl(processed))
    assert units
    assert all(not validate_pipeline_discourse_unit(unit) for unit in units)
    assert all(unit["metadata"]["source_name"] == "ParlaMint" for unit in units)
    assert all(unit.get("provenance", {}).get("license_status") == "to_be_verified" for unit in units)

    sample_units(processed, sample, n=1, seed=42)
    assert len(list(read_jsonl(sample))) == 1
