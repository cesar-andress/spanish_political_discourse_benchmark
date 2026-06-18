#!/usr/bin/env python3
"""Run the full SPDB pilot analytics pipeline."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable, List, Sequence

from analysis.pilot.agreement_analysis import run_agreement_analysis
from analysis.pilot.confusion_analysis import run_confusion_analysis
from analysis.pilot.constants import (
    DEFAULT_FIGURES_DIR,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_REPORT,
    DEFAULT_TEMPLATE,
    DEFAULT_TEMPLATE_FILE,
)
from analysis.pilot.io import load_pilot_dataset
from analysis.pilot.ontology_diagnostics import run_ontology_diagnostics
from analysis.pilot.report_generator import generate_pilot_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate SPDB pilot annotation analytics.")
    parser.add_argument(
        "--annotator",
        action="append",
        type=Path,
        default=[],
        help="Annotator CSV export (repeat for 2–3 annotators)",
    )
    parser.add_argument(
        "--template",
        type=Path,
        default=DEFAULT_TEMPLATE,
        help="Pilot unit template CSV (used before annotations arrive)",
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    parser.add_argument("--template-file", type=Path, default=DEFAULT_TEMPLATE_FILE)
    parser.add_argument("--figures-dir", type=Path, default=DEFAULT_FIGURES_DIR)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--no-figures", action="store_true")
    return parser


def run_pilot_analytics(
    *,
    annotator_paths: Sequence[Path],
    template_path: Path,
    output_dir: Path,
    report_path: Path,
    template_file: Path = DEFAULT_TEMPLATE_FILE,
    figures_dir: Path = DEFAULT_FIGURES_DIR,
    seed: int = 42,
    no_figures: bool = False,
):
    dataset = load_pilot_dataset(
        annotator_paths=annotator_paths,
        template_path=template_path,
    )
    agreement = run_agreement_analysis(dataset)
    confusion = run_confusion_analysis(
        dataset,
        figures_dir=figures_dir if not no_figures else output_dir / "figures",
    )
    if no_figures:
        confusion = type(confusion)(
            status=confusion.status,
            by_column=confusion.by_column,
            disagreement_units=confusion.disagreement_units,
            markdown_tables=confusion.markdown_tables,
            figure_paths=[],
        )
    ontology = run_ontology_diagnostics(dataset)

    make_args = " ".join(
        [
            f"PILOT_TEMPLATE={template_path}",
            *[f"PILOT_ANNOTATOR_{index}={path}" for index, path in enumerate(annotator_paths, start=1)],
        ]
    )
    return generate_pilot_report(
        dataset,
        agreement,
        confusion,
        ontology,
        report_path=report_path,
        output_dir=output_dir,
        template_path=template_file,
        seed=seed,
        make_args=make_args,
    )


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    if not args.template.exists() and not args.annotator:
        raise SystemExit(
            f"Template not found ({args.template}) and no annotator CSVs provided."
        )

    bundle = run_pilot_analytics(
        annotator_paths=args.annotator,
        template_path=args.template,
        output_dir=args.output_dir,
        report_path=args.report,
        template_file=args.template_file,
        figures_dir=args.figures_dir,
        seed=args.seed,
        no_figures=args.no_figures,
    )
    print(f"Annotation status: {bundle.dataset.status.value}")
    print(f"Wrote report to {bundle.report_path}")
    print(f"Wrote artefacts to {bundle.output_dir}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
