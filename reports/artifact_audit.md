# SPDB artifact audit — pragmatic function labels

**Input:** `tests/fixtures/annotation/artifact_audit_sample.csv`  
**Metadata merge:** none  
**Generated:** 2026-06-18 10:48 UTC  
**Units audited:** 30

## Purpose

Estimate how predictable `pragmatic_function` labels are from trivial corpus signals (length, party, speaker role, source type). High trivial baseline performance suggests potential annotation artifacts or confounds to control in modeling.

## ⚠ Artifact warnings

The following trivial predictors reached suspicious performance or reflect strong label skew:

- **Party-only** — accuracy 0.767, macro-F1 0.721. Trivial signal may encode label information; review for annotation artifacts.

## Label distribution

| Label | Count | Share |
|--------|------:|------:|
| `PF_ATTACK` | 6 | 20.0% |
| `PF_ADVOCACY` | 6 | 20.0% |
| `PF_DEFENSE` | 5 | 16.7% |
| `PF_PROPOSAL` | 4 | 13.3% |
| `PF_INFO` | 3 | 10.0% |
| `PF_APPEAL` | 2 | 6.7% |
| `PF_PROCEDURAL` | 2 | 6.7% |
| `PF_DEFLECT` | 2 | 6.7% |

## Average text length by label

| Label | Mean characters |
|-------|----------------:|
| `PF_ADVOCACY` | 61.3 |
| `PF_APPEAL` | 57.5 |
| `PF_ATTACK` | 42.8 |
| `PF_DEFENSE` | 51.6 |
| `PF_DEFLECT` | 54.0 |
| `PF_INFO` | 40.7 |
| `PF_PROCEDURAL` | 27.0 |
| `PF_PROPOSAL` | 52.0 |

## Average token count by label

| Label | Mean tokens |
|-------|------------:|
| `PF_ADVOCACY` | 9.0 |
| `PF_APPEAL` | 9.0 |
| `PF_ATTACK` | 6.7 |
| `PF_DEFENSE` | 7.2 |
| `PF_DEFLECT` | 10.0 |
| `PF_INFO` | 7.3 |
| `PF_PROCEDURAL` | 3.5 |
| `PF_PROPOSAL` | 7.5 |

## Speaker-role distribution by label

| Label | `candidate` | `executive` | `legislator` | `party_org` |
|-------|------:|------:|------:|------:|
| `PF_ADVOCACY` | 1 (17%) | 0 (0%) | 4 (67%) | 1 (17%) |
| `PF_APPEAL` | 0 (0%) | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_ATTACK` | 1 (17%) | 0 (0%) | 5 (83%) | 0 (0%) |
| `PF_DEFENSE` | 0 (0%) | 0 (0%) | 5 (100%) | 0 (0%) |
| `PF_DEFLECT` | 0 (0%) | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_INFO` | 0 (0%) | 1 (33%) | 2 (67%) | 0 (0%) |
| `PF_PROCEDURAL` | 0 (0%) | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_PROPOSAL` | 0 (0%) | 0 (0%) | 3 (75%) | 1 (25%) |

## Party distribution by label

| Label | `Cs` | `EAJPNV` | `ERC` | `PP` | `PSOE` | `UP` | `VOX` |
|-------|------:|------:|------:|------:|------:|------:|------:|
| `PF_ADVOCACY` | 5 (83%) | 0 (0%) | 0 (0%) | 0 (0%) | 1 (17%) | 0 (0%) | 0 (0%) |
| `PF_APPEAL` | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 2 (100%) |
| `PF_ATTACK` | 0 (0%) | 0 (0%) | 0 (0%) | 5 (83%) | 1 (17%) | 0 (0%) | 0 (0%) |
| `PF_DEFENSE` | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 5 (100%) | 0 (0%) | 0 (0%) |
| `PF_DEFLECT` | 0 (0%) | 0 (0%) | 2 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) |
| `PF_INFO` | 0 (0%) | 2 (67%) | 0 (0%) | 0 (0%) | 1 (33%) | 0 (0%) | 0 (0%) |
| `PF_PROCEDURAL` | 0 (0%) | 2 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) | 0 (0%) |
| `PF_PROPOSAL` | 0 (0%) | 0 (0%) | 0 (0%) | 1 (25%) | 0 (0%) | 3 (75%) | 0 (0%) |

## Source-type distribution by label

| Label | `manifesto` | `parliamentary` | `social_media` |
|-------|------:|------:|------:|
| `PF_ADVOCACY` | 1 (17%) | 4 (67%) | 1 (17%) |
| `PF_APPEAL` | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_ATTACK` | 0 (0%) | 5 (83%) | 1 (17%) |
| `PF_DEFENSE` | 0 (0%) | 5 (100%) | 0 (0%) |
| `PF_DEFLECT` | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_INFO` | 0 (0%) | 3 (100%) | 0 (0%) |
| `PF_PROCEDURAL` | 0 (0%) | 2 (100%) | 0 (0%) |
| `PF_PROPOSAL` | 1 (25%) | 3 (75%) | 0 (0%) |

## Trivial baseline performance (stratified cross-validation)

| Baseline | Accuracy | Macro-F1 | Flagged | Notes |
|----------|----------:|---------:|:-------:|-------|
| Majority-class | 0.200 | 0.042 | no | Random-guess baseline ≈ 0.125. |
| Length-only | 0.033 | 0.021 | no |  |
| Speaker-role-only | 0.200 | 0.042 | no |  |
| Party-only | 0.767 | 0.721 | yes | Trivial signal may encode label information; review for annotation artifacts. |

## Figures

| Figure | Description |
|--------|-------------|
| `figures/artifact_audit/label_distribution.png` | Pragmatic-function label counts |
| `figures/artifact_audit/avg_length_by_label.png` | Mean character length by label |
| `figures/artifact_audit/avg_tokens_by_label.png` | Mean token count by label |
| `figures/artifact_audit/party_by_label.png` | Party share within each label |
| `figures/artifact_audit/baseline_accuracy.png` | Trivial baseline cross-validated accuracy |
