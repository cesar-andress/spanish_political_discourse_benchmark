"""Generate publication-ready pilot annotation reports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from analysis.pilot.agreement_analysis import AgreementAnalysisResult, write_agreement_outputs
from analysis.pilot.confusion_analysis import ConfusionAnalysisResult, write_confusion_outputs
from analysis.pilot.constants import DEFAULT_TEMPLATE_FILE
from analysis.pilot.io import AnnotationStatus, PilotDataset
from analysis.pilot.ontology_diagnostics import OntologyDiagnosticsResult, write_ontology_outputs


@dataclass(frozen=True)
class PilotReportBundle:
    dataset: PilotDataset
    agreement: AgreementAnalysisResult
    confusion: ConfusionAnalysisResult
    ontology: OntologyDiagnosticsResult
    report_path: Path
    output_dir: Path


def _render_template(template_path: Path, values: Dict[str, str]) -> str:
    text = template_path.read_text(encoding="utf-8")
    for key, value in values.items():
        text = text.replace(f"{{{{{key}}}}}", value)
    return text


def _format_metric(value: object) -> str:
    if isinstance(value, float) and value != value:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _executive_summary(bundle: PilotReportBundle) -> str:
    status = bundle.dataset.status
    if status is AnnotationStatus.PENDING:
        return (
            "Pre-annotation mode: pilot units and ontology inventories are loaded, "
            "but human labels have not been submitted yet. Agreement and confusion "
            "sections will populate automatically once annotator CSV files are available."
        )

    agreement_bits = []
    pf = bundle.agreement.by_column.get("pragmatic_function", {})
    if pf:
        agreement_bits.append(
            f"Pragmatic-function Fleiss κ = {_format_metric(pf.get('fleiss_kappa'))} "
            f"(Krippendorff α = {_format_metric(pf.get('krippendorff_alpha'))})."
        )
    disagreement_n = len(bundle.confusion.disagreement_units)
    agreement_bits.append(
        f"{disagreement_n} / {bundle.dataset.n_units} units show cross-annotator disagreement."
    )
    pf_onto = bundle.ontology.by_column.get("pragmatic_function", {})
    if pf_onto:
        agreement_bits.append(
            f"Primary ontology imbalance assessment: `{pf_onto['imbalance']['assessment']}`."
        )
    return " ".join(agreement_bits)


def generate_pilot_report(
    dataset: PilotDataset,
    agreement: AgreementAnalysisResult,
    confusion: ConfusionAnalysisResult,
    ontology: OntologyDiagnosticsResult,
    *,
    report_path: Path,
    output_dir: Path,
    template_path: Path = DEFAULT_TEMPLATE_FILE,
    seed: int = 42,
    make_args: str = "",
) -> PilotReportBundle:
    write_agreement_outputs(agreement, output_dir, dataset)
    write_confusion_outputs(confusion, output_dir)
    write_ontology_outputs(ontology, output_dir)

    agreement_section = "\n".join(
        agreement.markdown_tables.get("summary", [])
        + [
            line
            for key, lines in agreement.markdown_tables.items()
            if key.startswith("per_class_")
            for line in lines
        ]
    )
    confusion_section = "\n".join(
        confusion.markdown_tables.get("summary", [])
        + [
            line
            for key, lines in confusion.markdown_tables.items()
            if key.startswith("matrix_") or key == "concentration"
            for line in lines
        ]
    )
    if confusion.figure_paths:
        confusion_section += "\n\n| Figure | Path |\n|--------|------|\n"
        for path in confusion.figure_paths:
            confusion_section += f"| Confusion heatmap | `{path.as_posix()}` |\n"

    ontology_section = "\n".join(
        ontology.markdown_tables.get("summary", [])
        + [
            line
            for key, lines in ontology.markdown_tables.items()
            if key.startswith("support_") or key.startswith("pairs_")
            for line in lines
        ]
    )

    bundle = PilotReportBundle(
        dataset=dataset,
        agreement=agreement,
        confusion=confusion,
        ontology=ontology,
        report_path=report_path,
        output_dir=output_dir,
    )

    rendered = _render_template(
        template_path,
        {
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            "seed": str(seed),
            "status": dataset.status.value,
            "template_path": str(dataset.template_path or "n/a"),
            "annotator_list": ", ".join(f"`{name}`" for name in dataset.annotator_names),
            "n_units": str(dataset.n_units),
            "executive_summary": _executive_summary(bundle),
            "agreement_section": agreement_section,
            "confusion_section": confusion_section,
            "ontology_section": ontology_section,
            "output_dir": output_dir.as_posix(),
            "make_args": make_args,
        },
    )
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(rendered, encoding="utf-8")
    return bundle
