"""Orchestrate SPDB ontology validation analyses."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from analysis.ontology_validation.constants import (
    BOOTSTRAP_ITERATIONS,
    DEFAULT_FIGURES_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TEMPLATE,
    FIXTURE_ANNOTATORS,
    FIXTURE_TEMPLATE,
    RANDOM_SEED,
)
from analysis.ontology_validation.dashboard import evaluate_dashboard, write_dashboard
from analysis.ontology_validation.disagreement import run_disagreement_structure, write_disagreement_structure
from analysis.ontology_validation.dominance import run_dominance_audit, write_dominance_audit
from analysis.ontology_validation.io import load_ontology_dataset
from analysis.ontology_validation.per_class import run_per_class_reliability, write_per_class_reliability
from analysis.ontology_validation.publication import generate_publication_tables, write_publication_tables
from analysis.ontology_validation.reliability import run_overall_reliability, write_overall_reliability


@dataclass(frozen=True)
class OntologyValidationBundle:
    output_dir: Path
    report_paths: tuple[Path, ...]


def run_ontology_validation(
    *,
    annotator_paths: Sequence[Path],
    template_path: Path,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    figures_dir: Path = DEFAULT_FIGURES_DIR,
    bootstrap_iterations: int = BOOTSTRAP_ITERATIONS,
    seed: int = RANDOM_SEED,
) -> OntologyValidationBundle:
    dataset = load_ontology_dataset(annotator_paths=annotator_paths, template_path=template_path)

    reliability = run_overall_reliability(
        dataset,
        bootstrap_iterations=bootstrap_iterations,
        seed=seed,
    )
    per_class = run_per_class_reliability(dataset)
    disagreement = run_disagreement_structure(dataset)
    dominance = run_dominance_audit(dataset)
    dashboard = evaluate_dashboard(
        dataset_status=dataset.status,
        reliability=reliability,
        disagreement=disagreement,
        dominance=dominance,
    )

    write_overall_reliability(reliability, output_dir, dataset)
    write_per_class_reliability(per_class, output_dir)
    write_disagreement_structure(disagreement, output_dir, figures_dir=figures_dir)
    write_dominance_audit(dominance, output_dir)
    write_dashboard(dashboard, output_dir)
    publication = generate_publication_tables(
        dataset, reliability, per_class, disagreement, dominance, dashboard
    )
    write_publication_tables(publication, output_dir)

    report_paths = (
        output_dir / "overall_reliability.md",
        output_dir / "per_class_reliability.md",
        output_dir / "confusion_report.md",
        output_dir / "single_dominance_report.md",
        output_dir / "ontology_decision.md",
        output_dir / "publication_tables.md",
    )
    return OntologyValidationBundle(output_dir=output_dir, report_paths=report_paths)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run SPDB ontology validation framework.")
    parser.add_argument("--annotator", action="append", type=Path, default=[])
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES_DIR)
    parser.add_argument("--bootstrap", type=int, default=BOOTSTRAP_ITERATIONS)
    parser.add_argument("--seed", type=int, default=RANDOM_SEED)
    parser.add_argument("--fixtures", action="store_true", help="Use bundled synthetic fixtures")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    annotators = list(FIXTURE_ANNOTATORS) if args.fixtures else args.annotator
    template = FIXTURE_TEMPLATE if args.fixtures else args.template
    if not template.exists() and not annotators:
        raise SystemExit("Provide --template or --fixtures.")

    bundle = run_ontology_validation(
        annotator_paths=annotators,
        template_path=template,
        output_dir=args.output_dir,
        figures_dir=args.figures_dir,
        bootstrap_iterations=args.bootstrap,
        seed=args.seed,
    )
    print(f"Wrote ontology validation outputs to {bundle.output_dir}/")
    for path in bundle.report_paths:
        print(f"  - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
