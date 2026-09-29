# Open Fallacy Dataset Inventory

Structured inventory of public fallacy and related persuasion datasets relevant to
SPDB external validation planning.

**Status:** planning document only. No external evaluation has been run.

**Datasets catalogued:** 8

## 1. FallacyES-Political

- **ID:** `fallacyes_political`
- **Citation:** Cruz, F. L., Enríquez, F., Ortega, F. J., & Troyano, J. A. (2025). FallacyES-Political: A Multiclass Dataset of Fallacies in Spanish Political Debates. Procesamiento del Lenguaje Natural, 74, 127--138.
- **URL:** https://zenodo.org/records/14836328
- **Language:** Spanish (ES)
- **Domain:** Spanish general-election debates (1993--2023); televised/radio candidate debates
- **Annotation scheme:** Single-label fallacy type (16 classes); span + prev/foll context; speaker metadata
- **Examples:** ~1,944 annotated fallacy spans (paper reports ~1,965)
- **License:** Zenodo deposit; scientific use; see record for terms
- **Availability:** Public (Zenodo); annotation guidelines bundled
- **Mapping potential to SPDB FAL labels:** Highest overlap with SPDB fallacy inventory among Spanish resources; supports label-level mapping and future zero-shot / fine-tuned transfer experiments.
- **External label inventory (16):** `Ad Hominem`, `Ad Populum`, `Appeal to Authority`, `Appeal to Emotion`, `Appeal to Fear`, `Complex Question`, `False Analogy`, `False Cause` ...

## 2. FallacyES

- **ID:** `fallacyes`
- **Citation:** Cruz, F. L., Troyano, J. A., Enríquez, F., & Ortega, F. J. (2023). Detección y clasificación de falacias prototípicas y espontáneas en español. Procesamiento del Lenguaje Natural, 71.
- **URL:** https://github.com/ITALIC-US/FallacyES
- **Language:** Spanish (ES)
- **Domain:** Prototypical (educational) + spontaneous (Meneame news comments); mixed topics
- **Annotation scheme:** Binary fallacy detection + multi-class type (LOGIC-derived taxonomy); non-fallacy controls
- **Examples:** Two partitions (prototypical, spontaneous); non-fallacious controls included
- **License:** GitHub repository; upstream LOGIC/MIT and Meneame CC BY 3.0 components
- **Availability:** Public (GitHub); IDUS research collection mirror
- **Mapping potential to SPDB FAL labels:** Spanish fallacy baseline outside parliamentary plenary genre; useful for cross-genre robustness checks.
- **External label inventory (17):** `ad hominem`, `ad populum`, `appeal to authority`, `appeal to emotion`, `appeal to nature`, `appeal to tradition`, `causal oversimplification`, `equivocation` ...

## 3. SemEval-2020 Task 11 (Propaganda Techniques)

- **ID:** `semeval2020_propaganda`
- **Citation:** Da San Martino, G., Barrón-Cedeño, A., Wachsmuth, H., Petrov, R., & Nakov, P. (2020). SemEval-2020 Task 11: Detection of Propaganda Techniques in News Articles. In Proceedings of SemEval-2020, pages 1377--1414.
- **URL:** https://zenodo.org/records/3952415
- **Language:** English (EN)
- **Domain:** English news articles (multiple outlets)
- **Annotation scheme:** Span identification + 14 propaganda-technique classes (persuasion frames)
- **Examples:** ~350 articles (train/dev/test splits); thousands of annotated spans
- **License:** SemEval task license; research use
- **Availability:** Public (Zenodo + task GitHub)
- **Mapping potential to SPDB FAL labels:** Partial overlap via whataboutism, false dilemma, appeal to fear/emotion; useful for cross-task positioning, not direct fallacy equivalence.
- **External label inventory (14):** `Loaded Language`, `Name Calling or Labeling`, `Repetition`, `Exaggeration or Minimisation`, `Doubt`, `Appeal to fear-prejudice`, `Flag-waving`, `Causal Oversimplification` ...

## 4. Argotario

- **ID:** `argotario`
- **Citation:** Habernal, I., Hannemann, R., Pollak, C., Klamm, C., Pauli, P., & Gurevych, I. (2017). Argotario: Computational Argumentation Meets Serious Games. In EMNLP 2017 System Demonstrations, pages 7--12.
- **URL:** https://www.ukp.tu-darmstadt.de/data/argumentation-mining/argotario-corpus/
- **Language:** English (EN)
- **Domain:** Crowdsourced everyday arguments (serious game)
- **Annotation scheme:** Multi-class logical fallacy labels + gamified collection
- **Examples:** ~1,600 annotated arguments (public subset varies by release)
- **License:** Research use; UKP terms
- **Availability:** Public (UKP); widely cited English fallacy baseline
- **Mapping potential to SPDB FAL labels:** English fallacy taxonomy reference; cross-lingual mapping via label semantics.
- **External label inventory (21):** `ad hominem`, `ad populum`, `appeal to authority`, `appeal to emotion`, `appeal to fear`, `appeal to nature`, `appeal to tradition`, `appeal to worse problems` ...

## 5. LOGIC / Logical Fallacy Dataset

- **ID:** `logic`
- **Citation:** Jin, Z., Wei, X., O'Connor, B., & Oard, D. W. (2022). Logical Fallacy Detection. In Findings of EMNLP 2022.
- **URL:** https://github.com/causalNLP/logical-fallacy
- **Language:** English (EN)
- **Domain:** Educational / synthetic logical fallacy examples
- **Annotation scheme:** Multi-class fallacy type; corrected releases (tmakesense fork)
- **Examples:** ~756 instances (corrected Logical Fallacy Dataset release)
- **License:** MIT (non-commercial caveats in upstream README)
- **Availability:** Public (GitHub)
- **Mapping potential to SPDB FAL labels:** Upstream schema for FallacyES prototypical section; English transfer baseline.
- **External label inventory (17):** `ad hominem`, `ad populum`, `appeal to authority`, `appeal to emotion`, `appeal to nature`, `appeal to tradition`, `causal oversimplification`, `equivocation` ...

## 6. DIPROMATS (IberLEF 2024)

- **ID:** `dipromats`
- **Citation:** Chiruzzo et al. (2024). IberLEF 2024 shared tasks (DIPROMATS track).
- **URL:** https://sites.google.com/view/iberlef-2024/
- **Language:** Spanish / English (ES/EN)
- **Domain:** Diplomats' tweets; propaganda techniques and strategic narratives
- **Annotation scheme:** Propaganda-technique and narrative-frame labels (campaign task partitions)
- **Examples:** Campaign-year dependent (IberLEF 2024)
- **License:** Shared-task terms
- **Availability:** Task snapshots (not persistent corpus release)
- **Mapping potential to SPDB FAL labels:** Spanish political social text; propaganda frames partially overlap SPDB fallacies.
- **External label inventory (2):** `propaganda techniques`, `strategic narratives`

## 7. Multilingual fallacy benchmarks (LLM evaluation literature)

- **ID:** `multifallacy_llm_benchmark`
- **Citation:** Recent LLM fallacy studies aggregate Argotario, LOGIC, COVID-fallacy, and political debate sets for zero-shot evaluation (e.g., ArgMining 2025 surveys).
- **URL:** https://aclanthology.org/2025.argmining-1.36/
- **Language:** Multilingual (EN primary; ES via FallacyES-Political)
- **Domain:** Mixed (debates, social, news, educational)
- **Annotation scheme:** Heterogeneous per source corpus
- **Examples:** Corpus-dependent aggregates
- **License:** Per-source licenses
- **Availability:** Public components only where upstream permits
- **Mapping potential to SPDB FAL labels:** Positioning SPDB within broader fallacy-detection literature once SPDB gold exists.
- **External label inventory (15):** `c`, `o`, `r`, `p`, `u`, `s`, `-`, `s` ...

## 8. English parliamentary / debate fallacy resources

- **ID:** `parliamentary_fallacy_en`
- **Citation:** MM-USED-fallacy (Mancini et al., 2024) and related U.S. presidential-debate multimodal fallacy datasets.
- **URL:** https://aclanthology.org/
- **Language:** English (EN)
- **Domain:** U.S. presidential debates (multimodal); English political debates
- **Annotation scheme:** Fallacy classes with audio+text in MM-USED-fallacy
- **Examples:** Corpus-dependent (multimodal debate subsets)
- **License:** Per-paper release terms
- **Availability:** Partial public releases
- **Mapping potential to SPDB FAL labels:** Cross-lingual institutional-debate comparison after translation or multilingual models.
- **External label inventory (4):** `Appeal to Emotion`, `Appeal to Authority`, `Ad Hominem`, `...`

## Notes

- SPDB human gold labels are not yet available; this inventory supports future
  external validation once adjudicated pilot annotations exist.
- Parliamentary plenary spans (SPDB) differ from debate excerpts (FallacyES-Political)
  in segmentation and context packaging.

