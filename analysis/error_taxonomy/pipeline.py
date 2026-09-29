"""Orchestrate SPDB error taxonomy generation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Sequence

from analysis.error_taxonomy.clusters import TaxonomyResult, analyze_taxonomy
from analysis.error_taxonomy.constants import (
    DEFAULT_ADJUDICATED,
    DEFAULT_ANNOTATORS,
    DEFAULT_EXPORT_DIR,
    DEFAULT_LLM_DIR,
    DEFAULT_OUTPUT,
    FIXTURE_ADJUDICATED,
    FIXTURE_ANNOTATORS,
    FIXTURE_LLM,
)
from analysis.error_taxonomy.io import build_inventory
from analysis.error_taxonomy.report import render_error_taxonomy
from analysis.human_vs_llm.io import discover_llm_jsonl_files


@dataclass(frozen=True)
class ErrorTaxonomyResult:
    pending: bool
    output_path: Path
    export_dir: Path
    taxonomy: TaxonomyResult | None
    missing_inputs: tuple[str, ...] = ()


def _write_pending(output_path: Path, missing: Sequence[str]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# SPDB Error Taxonomy — Pending",
        "",
        "Required inputs for automatic error taxonomy generation are not yet available.",
        "",
        "## Missing",
        "",
    ]
    lines.extend(f"- `{item}`" for item in missing)
    lines.extend(
        [
            "",
            "## Expected inputs",
            "",
            "- Human annotator CSV exports with `pragmatic_function` (`annotation/pilot_001/pilot_100_units_annotator_*.csv`)",
            "- Optional adjudicated gold CSV",
            "- Model prediction JSONL files (`data/experiments/llm_annotations/*_pilot_100.jsonl`)",
            "",
            "Run `make error-taxonomy-fixtures` to render from test fixtures.",
            "",
        ]
    )
    output_path.write_text("\n".join(lines), encoding="utf-8")


def run_error_taxonomy(
    *,
    annotator_paths: Sequence[Path] = DEFAULT_ANNOTATORS,
    adjudicated_path: Path | None = DEFAULT_ADJUDICATED,
    llm_dir: Path = DEFAULT_LLM_DIR,
    llm_paths: Sequence[Path] | None = None,
    output_path: Path = DEFAULT_OUTPUT,
    export_dir: Path = DEFAULT_EXPORT_DIR,
    gold_strategy: str = "majority_vote",
) -> ErrorTaxonomyResult:
    resolved_llm = list(llm_paths) if llm_paths is not None else discover_llm_jsonl_files(llm_dir)

    inventory = build_inventory(
        annotator_paths=annotator_paths,
        adjudicated_path=adjudicated_path if adjudicated_path and adjudicated_path.exists() else None,
        llm_paths=resolved_llm,
        gold_strategy=gold_strategy,
    )
    if inventory is None:
        missing = [str(path) for path in annotator_paths if not path.exists()]
        _write_pending(output_path, missing)
        return ErrorTaxonomyResult(
            pending=True,
            output_path=output_path,
            export_dir=export_dir,
            taxonomy=None,
            missing_inputs=tuple(missing),
        )

    taxonomy = analyze_taxonomy(inventory)
    content = render_error_taxonomy(taxonomy)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")

    export_dir.mkdir(parents=True, exist_ok=True)
    _write_cluster_csv(taxonomy, export_dir / "cluster_summary.csv")
    _write_directional_csv(taxonomy, export_dir / "directional_confusions.csv")

    return ErrorTaxonomyResult(
        pending=False,
        output_path=output_path,
        export_dir=export_dir,
        taxonomy=taxonomy,
    )


def run_error_taxonomy_fixtures(output_path: Path = DEFAULT_OUTPUT) -> ErrorTaxonomyResult:
    return run_error_taxonomy(
        annotator_paths=FIXTURE_ANNOTATORS,
        adjudicated_path=FIXTURE_ADJUDICATED,
        llm_paths=[FIXTURE_LLM],
        output_path=output_path,
        gold_strategy="adjudicated_file",
    )


def _write_cluster_csv(taxonomy: TaxonomyResult, path: Path) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["cluster_id", "title", "human_count", "model_count", "human_units", "model_units"],
        )
        writer.writeheader()
        for stats in taxonomy.clusters:
            writer.writerow(
                {
                    "cluster_id": stats.cluster.cluster_id,
                    "title": stats.cluster.title,
                    "human_count": stats.human_count,
                    "model_count": stats.model_count,
                    "human_units": stats.human_units,
                    "model_units": stats.model_units,
                }
            )


def _write_directional_csv(taxonomy: TaxonomyResult, path: Path) -> None:
    import csv

    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["cluster_id", "source", "target", "human_count", "model_count", "total"],
        )
        writer.writeheader()
        for stats in taxonomy.clusters:
            for (source, target), total in sorted(
                stats.directional.items(),
                key=lambda item: item[1],
                reverse=True,
            ):
                writer.writerow(
                    {
                        "cluster_id": stats.cluster.cluster_id,
                        "source": source,
                        "target": target,
                        "human_count": stats.human_directional.get((source, target), 0),
                        "model_count": stats.model_directional.get((source, target), 0),
                        "total": total,
                    }
                )
