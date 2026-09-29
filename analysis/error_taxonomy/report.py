"""Publication-ready Markdown tables for SPDB error taxonomy."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from analysis.error_taxonomy.clusters import TaxonomyResult
from analysis.error_taxonomy.constants import ERROR_CLUSTERS


def _fmt_rate(numerator: int, denominator: int) -> str:
    if denominator <= 0:
        return "—"
    return f"{100.0 * numerator / denominator:.1f}%"


def _fmt_float(value: float) -> str:
    return "—" if value != value else f"{value:.3f}"


def _truncate(text: str, limit: int = 72) -> str:
    text = " ".join(text.split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def render_error_taxonomy(result: TaxonomyResult) -> str:
    inv = result.inventory
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    models = ", ".join(f"`{name}`" for name in inv.model_names) if inv.model_names else "—"

    lines: List[str] = [
        "# SPDB Error Taxonomy — Pragmatic Function Confusion Clusters",
        "",
        f"**Generated:** {generated}  ",
        f"**Gold strategy:** `{inv.gold_strategy}`  ",
        f"**Human corpus:** {inv.n_units_human} units ({inv.n_human_disagreement_units} with inter-annotator disagreement)  ",
        f"**Model systems:** {models}",
        "",
        "Automatic taxonomy over predefined near-neighbor PF clusters identified in the SPDB codebook "
        "and IberLEF evaluation plan. Inputs: inter-annotator disagreements and model-vs-gold errors.",
        "",
        "---",
        "",
        "## Table 1. Corpus and error inventory (Scientific Data style)",
        "",
        "**Table 1.** Error taxonomy corpus and inventory.",
        "",
        "| Quantity | Value |",
        "|----------|------:|",
        f"| Annotated units (human) | {inv.n_units_human} |",
        f"| Units with human PF disagreement | {inv.n_human_disagreement_units} |",
        f"| Human label transitions (clustered pairs) | {result.total_human_clustered} |",
        f"| Units evaluated against gold (models) | {inv.n_units_model} |",
        f"| Model PF errors (all confusions) | {inv.n_model_errors} |",
        f"| Model errors in predefined clusters | {result.total_model_clustered} |",
        f"| Model errors recapitulating human cluster units | {_fmt_float(result.model_recapitulation_rate)} |",
        "",
        "## Table 2. Predefined confusion clusters (LREC style)",
        "",
        "**Table 2.** Predefined pragmatic-function confusion clusters and observed frequency.",
        "",
        "| Cluster | Description | Human | Model | Combined | Share of clustered errors |",
        "|---------|-------------|------:|------:|---------:|--------------------------:|",
    ]

    combined_total = result.total_human_clustered + result.total_model_clustered
    for stats in result.clusters:
        combined = stats.human_count + stats.model_count
        share = _fmt_rate(combined, combined_total)
        lines.append(
            f"| **{stats.cluster.title}** | {stats.cluster.description} | "
            f"{stats.human_count} | {stats.model_count} | {combined} | {share} |"
        )

    lines.extend(
        [
            "",
            "## Table 3. Directional confusion within clusters",
            "",
            "**Table 3.** Directional confusion counts by cluster (gold/reference → predicted/alternate label).",
            "",
            "| Cluster | Reference → Alternate | Human | Model | Total |",
            "|---------|----------------------|------:|------:|------:|",
        ]
    )

    for stats in result.clusters:
        cluster = stats.cluster
        keys = sorted(
            stats.directional.keys(),
            key=lambda item: stats.directional[item],
            reverse=True,
        )
        if not keys:
            lines.append(f"| {cluster.title} | — | 0 | 0 | 0 |")
            continue
        for index, (source, target) in enumerate(keys):
            human_n = stats.human_directional.get((source, target), 0)
            model_n = stats.model_directional.get((source, target), 0)
            total = stats.directional[(source, target)]
            title = cluster.title if index == 0 else ""
            lines.append(
                f"| {title} | `{source}` → `{target}` | {human_n} | {model_n} | {total} |"
            )

    lines.extend(
        [
            "",
            "## Table 4. Exemplar units by cluster",
            "",
            "**Table 4.** Representative units illustrating each confusion cluster.",
            "",
            "| Cluster | unit_id | Source | Target | Origin | Text (truncated) |",
            "|---------|---------|--------|--------|--------|------------------|",
        ]
    )

    for stats in result.clusters:
        if not stats.exemplars:
            lines.append(f"| {stats.cluster.title} | — | — | — | — | _No exemplars in current corpus_ |")
            continue
        for index, item in enumerate(stats.exemplars):
            origin = "human" if item.source_type == "human_disagreement" else f"model ({item.model_name})"
            title = stats.cluster.title if index == 0 else ""
            lines.append(
                f"| {title} | `{item.unit_id}` | `{item.source}` | `{item.target}` | {origin} | "
                f"{_truncate(item.text) or '—'} |"
            )

    lines.extend(
        [
            "",
            "## Table 5. Model–human alignment by cluster",
            "",
            "**Table 5.** Extent to which model errors concentrate on the same near-neighbor pairs as human annotators.",
            "",
            "| Cluster | Human units | Model error units | Overlap units | Model/Human unit ratio |",
            "|---------|------------:|------------------:|--------------:|-----------------------:|",
        ]
    )

    for stats in result.clusters:
        human_units = stats.human_units
        model_units = stats.model_units
        overlap = min(human_units, model_units) if human_units and model_units else 0
        ratio = model_units / human_units if human_units else float("nan")
        lines.append(
            f"| {stats.cluster.title} | {human_units} | {model_units} | {overlap} | {_fmt_float(ratio)} |"
        )

    lines.extend(
        [
            "",
            "## Cluster reference",
            "",
            "The four clusters correspond to codebook near-neighbor boundaries prioritized for adjudication:",
            "",
        ]
    )
    for cluster in ERROR_CLUSTERS:
        lines.append(
            f"- **{cluster.title}** (`{cluster.label_a}` ↔ `{cluster.label_b}`): {cluster.description}"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Human disagreements are extracted from all annotator pairs on units with ≥2 distinct PF labels.",
            "- Model errors use gold labels from the configured strategy and count only mispredictions mapped to a predefined cluster.",
            "- Regenerate with `make error-taxonomy` (production inputs) or `make error-taxonomy-fixtures`.",
            "",
        ]
    )
    return "\n".join(lines)
