"""Tests for stratified discourse-unit sampling."""

from __future__ import annotations

from pathlib import Path

from scripts.ingestion.common import read_jsonl, write_jsonl
from scripts.sampling.stratified_sample import allocate_quotas, stratified_sample_units


def _unit(
    unit_id: str,
    *,
    party: str,
    year: str,
    speaker: str,
) -> dict:
    return {
        "unit_id": unit_id,
        "document_id": f"doc-{unit_id}",
        "language": "es",
        "text": f"texto {unit_id}",
        "character_count": 10,
        "token_count": 2,
        "metadata": {
            "source_type": "parliamentary",
            "source_name": "ParlaMint",
            "date": f"{year}-06-01",
            "speaker_name": speaker,
            "speaker_party": party,
            "segment_index": 0,
            "char_start": 0,
            "char_end": 10,
        },
    }


def test_allocate_quotas_largest_remainder():
    sizes = {("A", "2017"): 60, ("B", "2020"): 40}
    quotas = allocate_quotas(sizes, 100)
    assert sum(quotas.values()) == 100
    assert quotas[("A", "2017")] == 60
    assert quotas[("B", "2020")] == 40


def test_stratified_sample_respects_speaker_cap():
    units = []
    for i in range(20):
        units.append(_unit(f"u{i}", party="PSOE", year="2017", speaker="Alice"))
    result = stratified_sample_units(units, n=10, seed=42, max_per_speaker=5)
    assert len(result.units) == 5
    assert result.speaker_selected["Alice"] == 5
    assert result.shortfall_reason is not None


def test_stratified_sample_deterministic():
    units = [
        _unit(f"u{i}", party="PSOE" if i % 2 == 0 else "PP", year="2017", speaker=f"sp{i % 4}")
        for i in range(30)
    ]
    a = stratified_sample_units(units, n=12, seed=7, max_per_speaker=5)
    b = stratified_sample_units(units, n=12, seed=7, max_per_speaker=5)
    assert [u["unit_id"] for u in a.units] == [u["unit_id"] for u in b.units]


def test_stratified_sample_party_year_coverage():
    units = []
    for party in ("PSOE", "PP"):
        for year in ("2017", "2020"):
            for i in range(5):
                units.append(_unit(f"{party}-{year}-{i}", party=party, year=year, speaker=f"{party}-{i}"))
    result = stratified_sample_units(units, n=16, seed=42, max_per_speaker=5)
    assert len(result.units) == 16
    assert len(result.party_selected) == 2
    assert len(result.year_selected) == 2
    assert max(result.speaker_selected.values()) <= 5


def test_stratified_sample_round_robin_before_reuse():
    units = []
    for i in range(8):
        units.append(_unit(f"a{i}", party="PSOE", year="2017", speaker="Alice"))
    for i in range(8):
        units.append(_unit(f"b{i}", party="PSOE", year="2017", speaker="Bob"))
    result = stratified_sample_units(units, n=6, seed=42, max_per_speaker=5)
    assert result.speaker_selected["Alice"] == 3
    assert result.speaker_selected["Bob"] == 3
    assert len(result.units) == 6


def test_stratified_sample_cli(tmp_path: Path):
    units_path = tmp_path / "units.jsonl"
    write_jsonl(
        units_path,
        [
            _unit("u1", party="PSOE", year="2017", speaker="A"),
            _unit("u2", party="PP", year="2020", speaker="B"),
        ],
    )
    output = tmp_path / "sample.jsonl"
    report = tmp_path / "report.md"
    from scripts.analysis.parlamint_500_sampling_report import run

    result = run(
        input_path=units_path,
        output_path=output,
        report_path=report,
        n=2,
        seed=42,
        max_per_speaker=5,
    )
    assert len(result.units) == 2
    assert output.exists()
    assert "Sampling constraints" in report.read_text(encoding="utf-8")
    assert len(list(read_jsonl(output))) == 2
