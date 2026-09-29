"""Structured inventory of public fallacy resources and SPDB label mappings."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Tuple

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REPORT_DIR = ROOT / "reports/external_validation"

MatchKind = Literal["exact", "partial", "approximate", "none"]
CompatibilityLevel = Literal["LOW", "MEDIUM", "HIGH"]

SPDB_FAL_LABELS: Tuple[str, ...] = (
    "FAL_ADHOM",
    "FAL_STRAW",
    "FAL_DILEMMA",
    "FAL_SLOPE",
    "FAL_EMOTION",
    "FAL_GENERAL",
    "FAL_WHATABOUT",
    "FAL_NONE",
)

# Aliases used in planning documents (user-facing names map to SPDB ids above).
SPDB_FAL_ALIASES = {
    "FAL_AD_HOMINEM": "FAL_ADHOM",
    "FAL_FALSE_DILEMMA": "FAL_DILEMMA",
    "FAL_HASTY_GENERALIZATION": "FAL_GENERAL",
}


@dataclass(frozen=True)
class CompatibilityScores:
    direct_comparison: CompatibilityLevel
    transfer_learning: CompatibilityLevel
    external_validation: CompatibilityLevel
    cross_lingual: CompatibilityLevel
    notes: str


@dataclass(frozen=True)
class LabelMapping:
    spdb_label: str
    external_label: str
    match: MatchKind
    rationale: str


@dataclass(frozen=True)
class ExternalDataset:
    dataset_id: str
    name: str
    citation: str
    url: str
    language: str
    domain: str
    annotation_scheme: str
    num_examples: str
    license_info: str
    availability: str
    mapping_potential: str
    external_labels: Tuple[str, ...]
    compatibility: CompatibilityScores


FALLACYES_POLITICAL_LABELS: Tuple[str, ...] = (
    "Ad Hominem",
    "Ad Populum",
    "Appeal to Authority",
    "Appeal to Emotion",
    "Appeal to Fear",
    "Complex Question",
    "False Analogy",
    "False Cause",
    "False Dilemma",
    "Flag Waving",
    "Guilt by Association",
    "Hasty Generalization",
    "Poisoning the Well",
    "Slippery Slope",
    "Strawman",
    "Wishful Thinking",
)

SEMEval20_PROPAGANDA_LABELS: Tuple[str, ...] = (
    "Loaded Language",
    "Name Calling or Labeling",
    "Repetition",
    "Exaggeration or Minimisation",
    "Doubt",
    "Appeal to fear-prejudice",
    "Flag-waving",
    "Causal Oversimplification",
    "Black-and-white Fallacy / Dictatorship",
    "Thought-terminating cliché",
    "Whataboutism",
    "Reductio ad hitlerum",
    "Red Herring",
    "Bandwagon",
)

ARGOTARIO_LABELS: Tuple[str, ...] = (
    "ad hominem",
    "ad populum",
    "appeal to authority",
    "appeal to emotion",
    "appeal to fear",
    "appeal to nature",
    "appeal to tradition",
    "appeal to worse problems",
    "causal oversimplification",
    "false causality",
    "false dilemma",
    "genetic fallacy",
    "guilt by association",
    "hasty generalization",
    "no true scotsman",
    "red herring",
    "reductio ad hitlerum",
    "slippery slope",
    "straw man",
    "tu quoque",
    "whataboutism",
)

LOGIC_LABELS: Tuple[str, ...] = (
    "ad hominem",
    "ad populum",
    "appeal to authority",
    "appeal to emotion",
    "appeal to nature",
    "appeal to tradition",
    "causal oversimplification",
    "equivocation",
    "fallacy of logic",
    "false causality",
    "false dilemma",
    "genetic fallacy",
    "hasty generalization",
    "intentional",
    "slippery slope",
    "straw man",
    "tu quoque",
)

EXTERNAL_DATASETS: Tuple[ExternalDataset, ...] = (
    ExternalDataset(
        dataset_id="fallacyes_political",
        name="FallacyES-Political",
        citation=(
            "Cruz, F. L., Enríquez, F., Ortega, F. J., & Troyano, J. A. (2025). "
            "FallacyES-Political: A Multiclass Dataset of Fallacies in Spanish Political Debates. "
            "Procesamiento del Lenguaje Natural, 74, 127--138."
        ),
        url="https://zenodo.org/records/14836328",
        language="Spanish (ES)",
        domain="Spanish general-election debates (1993--2023); televised/radio candidate debates",
        annotation_scheme="Single-label fallacy type (16 classes); span + prev/foll context; speaker metadata",
        num_examples="~1,944 annotated fallacy spans (paper reports ~1,965)",
        license_info="Zenodo deposit; scientific use; see record for terms",
        availability="Public (Zenodo); annotation guidelines bundled",
        mapping_potential=(
            "Highest overlap with SPDB fallacy inventory among Spanish resources; "
            "supports label-level mapping and future zero-shot / fine-tuned transfer experiments."
        ),
        external_labels=FALLACYES_POLITICAL_LABELS,
        compatibility=CompatibilityScores(
            direct_comparison="MEDIUM",
            transfer_learning="HIGH",
            external_validation="HIGH",
            cross_lingual="LOW",
            notes=(
                "Same language and political genre, but unit definition differs "
                "(debate excerpt vs. SPDB discourse unit) and label granularity differs (16 vs. 7+none)."
            ),
        ),
    ),
    ExternalDataset(
        dataset_id="fallacyes",
        name="FallacyES",
        citation=(
            "Cruz, F. L., Troyano, J. A., Enríquez, F., & Ortega, F. J. (2023). "
            "Detección y clasificación de falacias prototípicas y espontáneas en español. "
            "Procesamiento del Lenguaje Natural, 71."
        ),
        url="https://github.com/ITALIC-US/FallacyES",
        language="Spanish (ES)",
        domain="Prototypical (educational) + spontaneous (Meneame news comments); mixed topics",
        annotation_scheme="Binary fallacy detection + multi-class type (LOGIC-derived taxonomy); non-fallacy controls",
        num_examples="Two partitions (prototypical, spontaneous); non-fallacious controls included",
        license_info="GitHub repository; upstream LOGIC/MIT and Meneame CC BY 3.0 components",
        availability="Public (GitHub); IDUS research collection mirror",
        mapping_potential=(
            "Spanish fallacy baseline outside parliamentary plenary genre; useful for cross-genre robustness checks."
        ),
        external_labels=LOGIC_LABELS,
        compatibility=CompatibilityScores(
            direct_comparison="MEDIUM",
            transfer_learning="HIGH",
            external_validation="MEDIUM",
            cross_lingual="LOW",
            notes="Genre shift from news comments / textbook examples to institutional political speech.",
        ),
    ),
    ExternalDataset(
        dataset_id="semeval2020_propaganda",
        name="SemEval-2020 Task 11 (Propaganda Techniques)",
        citation=(
            "Da San Martino, G., Barrón-Cedeño, A., Wachsmuth, H., Petrov, R., & Nakov, P. (2020). "
            "SemEval-2020 Task 11: Detection of Propaganda Techniques in News Articles. "
            "In Proceedings of SemEval-2020, pages 1377--1414."
        ),
        url="https://zenodo.org/records/3952415",
        language="English (EN)",
        domain="English news articles (multiple outlets)",
        annotation_scheme="Span identification + 14 propaganda-technique classes (persuasion frames)",
        num_examples="~350 articles (train/dev/test splits); thousands of annotated spans",
        license_info="SemEval task license; research use",
        availability="Public (Zenodo + task GitHub)",
        mapping_potential=(
            "Partial overlap via whataboutism, false dilemma, appeal to fear/emotion; "
            "useful for cross-task positioning, not direct fallacy equivalence."
        ),
        external_labels=SEMEval20_PROPAGANDA_LABELS,
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="MEDIUM",
            external_validation="MEDIUM",
            cross_lingual="MEDIUM",
            notes="Propaganda techniques are related but not isomorphic to SPDB political-fallacy codes.",
        ),
    ),
    ExternalDataset(
        dataset_id="argotario",
        name="Argotario",
        citation=(
            "Habernal, I., Hannemann, R., Pollak, C., Klamm, C., Pauli, P., & Gurevych, I. (2017). "
            "Argotario: Computational Argumentation Meets Serious Games. "
            "In EMNLP 2017 System Demonstrations, pages 7--12."
        ),
        url="https://www.ukp.tu-darmstadt.de/data/argumentation-mining/argotario-corpus/",
        language="English (EN)",
        domain="Crowdsourced everyday arguments (serious game)",
        annotation_scheme="Multi-class logical fallacy labels + gamified collection",
        num_examples="~1,600 annotated arguments (public subset varies by release)",
        license_info="Research use; UKP terms",
        availability="Public (UKP); widely cited English fallacy baseline",
        mapping_potential="English fallacy taxonomy reference; cross-lingual mapping via label semantics.",
        external_labels=ARGOTARIO_LABELS,
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="MEDIUM",
            external_validation="MEDIUM",
            cross_lingual="MEDIUM",
            notes="Informal argument genre; English-only gold.",
        ),
    ),
    ExternalDataset(
        dataset_id="logic",
        name="LOGIC / Logical Fallacy Dataset",
        citation=(
            "Jin, Z., Wei, X., O'Connor, B., & Oard, D. W. (2022). "
            "Logical Fallacy Detection. In Findings of EMNLP 2022."
        ),
        url="https://github.com/causalNLP/logical-fallacy",
        language="English (EN)",
        domain="Educational / synthetic logical fallacy examples",
        annotation_scheme="Multi-class fallacy type; corrected releases (tmakesense fork)",
        num_examples="~756 instances (corrected Logical Fallacy Dataset release)",
        license_info="MIT (non-commercial caveats in upstream README)",
        availability="Public (GitHub)",
        mapping_potential="Upstream schema for FallacyES prototypical section; English transfer baseline.",
        external_labels=LOGIC_LABELS,
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="MEDIUM",
            external_validation="MEDIUM",
            cross_lingual="MEDIUM",
            notes="Prototypical English examples; not political institutional text.",
        ),
    ),
    ExternalDataset(
        dataset_id="dipromats",
        name="DIPROMATS (IberLEF 2024)",
        citation="Chiruzzo et al. (2024). IberLEF 2024 shared tasks (DIPROMATS track).",
        url="https://sites.google.com/view/iberlef-2024/",
        language="Spanish / English (ES/EN)",
        domain="Diplomats' tweets; propaganda techniques and strategic narratives",
        annotation_scheme="Propaganda-technique and narrative-frame labels (campaign task partitions)",
        num_examples="Campaign-year dependent (IberLEF 2024)",
        license_info="Shared-task terms",
        availability="Task snapshots (not persistent corpus release)",
        mapping_potential="Spanish political social text; propaganda frames partially overlap SPDB fallacies.",
        external_labels=("propaganda techniques", "strategic narratives"),
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="LOW",
            external_validation="LOW",
            cross_lingual="MEDIUM",
            notes="Task snapshot; label inventory not aligned to SPDB fallacy ontology.",
        ),
    ),
    ExternalDataset(
        dataset_id="multifallacy_llm_benchmark",
        name="Multilingual fallacy benchmarks (LLM evaluation literature)",
        citation=(
            "Recent LLM fallacy studies aggregate Argotario, LOGIC, COVID-fallacy, "
            "and political debate sets for zero-shot evaluation (e.g., ArgMining 2025 surveys)."
        ),
        url="https://aclanthology.org/2025.argmining-1.36/",
        language="Multilingual (EN primary; ES via FallacyES-Political)",
        domain="Mixed (debates, social, news, educational)",
        annotation_scheme="Heterogeneous per source corpus",
        num_examples="Corpus-dependent aggregates",
        license_info="Per-source licenses",
        availability="Public components only where upstream permits",
        mapping_potential="Positioning SPDB within broader fallacy-detection literature once SPDB gold exists.",
        external_labels=("corpus-specific"),
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="MEDIUM",
            external_validation="MEDIUM",
            cross_lingual="HIGH",
            notes="Requires harmonised label projection; no unified Spanish parliamentary benchmark yet.",
        ),
    ),
    ExternalDataset(
        dataset_id="parliamentary_fallacy_en",
        name="English parliamentary / debate fallacy resources",
        citation=(
            "MM-USED-fallacy (Mancini et al., 2024) and related U.S. presidential-debate "
            "multimodal fallacy datasets."
        ),
        url="https://aclanthology.org/",
        language="English (EN)",
        domain="U.S. presidential debates (multimodal); English political debates",
        annotation_scheme="Fallacy classes with audio+text in MM-USED-fallacy",
        num_examples="Corpus-dependent (multimodal debate subsets)",
        license_info="Per-paper release terms",
        availability="Partial public releases",
        mapping_potential="Cross-lingual institutional-debate comparison after translation or multilingual models.",
        external_labels=("Appeal to Emotion", "Appeal to Authority", "Ad Hominem", "..."),
        compatibility=CompatibilityScores(
            direct_comparison="LOW",
            transfer_learning="MEDIUM",
            external_validation="MEDIUM",
            cross_lingual="HIGH",
            notes="Different legislature and language; institutional genre similarity only.",
        ),
    ),
)
