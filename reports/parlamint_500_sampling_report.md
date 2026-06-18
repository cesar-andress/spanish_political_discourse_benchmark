# ParlaMint 500-unit benchmark candidate sample

**Input pool:** `data/processed/parlamint_units.jsonl` (878 units)  
**Output sample:** `data/processed/parlamint_500_units.jsonl` (398 units)  
**Generated:** 2026-06-18 10:12 UTC  
**Seed:** `42` (deterministic)  

## Sampling constraints

| Constraint | Setting |
|------------|---------|
| Target size (`n`) | 500 |
| Stratification | `speaker_party` × session year |
| Quota allocation | Proportional (largest remainder) |
| Speaker selection | Round-robin within stratum |
| Max units per speaker | 5 (global, before reuse) |

## Summary

| Metric | Value |
|--------|------:|
| Selected units | 398 |
| Unique parties | 25 |
| Unique speakers | 99 |
| Session years | 2017, 2020, 2023 |
| Max units from one speaker | 5 |
| Speakers at cap (5) | 45 |
| Speaker-cap ceiling (current pool) | 398 |

> **Shortfall:** Requested n=500 but only 398 unit(s) could be selected under max_per_speaker=5 (theoretical ceiling=398). With the current six-session ParlaMint pool (878 units, 99 speakers), at most **398** units can be selected before any speaker contributes a sixth unit. Ingest additional sessions to approach the n=500 target.

## Pool vs sample (year)

| Year | Pool units | Pool share | Sample units | Sample share |
|------|----------:|-----------:|-------------:|-------------:|
| 2017 | 610 | 69.5% | 325 | 81.7% |
| 2020 | 155 | 17.7% | 32 | 8.0% |
| 2023 | 113 | 12.9% | 41 | 10.3% |

## Party × year quotas

| Party | Year | Pool | Quota | Selected |
|-------|------|-----:|------:|---------:|
| BNG | 2023 | 2 | 1 | 2 |
| CCNCPNC | 2017 | 4 | 2 | 4 |
| CDC | 2017 | 18 | 10 | 12 |
| COMPROMÍSQ | 2023 | 3 | 2 | 3 |
| CPEUPV | 2017 | 10 | 6 | 10 |
| Cs | 2017 | 115 | 65 | 54 |
| Cs | 2020 | 17 | 10 | 3 |
| Cs | 2023 | 8 | 5 | 2 |
| EAJPNV | 2017 | 42 | 24 | 17 |
| EAJPNV | 2020 | 13 | 7 | 2 |
| EAJPNV | 2023 | 6 | 3 | 2 |
| ECP | 2017 | 21 | 12 | 17 |
| ECPGUAYEMELCANVI | 2017 | 13 | 7 | 10 |
| ECUP | 2017 | 5 | 3 | 5 |
| EHBildu | 2017 | 2 | 1 | 1 |
| EHBildu | 2020 | 14 | 8 | 4 |
| EHBildu | 2023 | 5 | 3 | 5 |
| ERCCATSÍ | 2017 | 22 | 12 | 19 |
| ERCS | 2017 | 5 | 3 | 5 |
| ERCS | 2020 | 10 | 6 | 5 |
| JxCatJUNTS | 2017 | 9 | 5 | 9 |
| PP | 2017 | 75 | 43 | 66 |
| PP | 2023 | 5 | 3 | 5 |
| PPFORO | 2017 | 8 | 4 | 5 |
| PSCPSOE | 2017 | 11 | 6 | 11 |
| PSOE | 2017 | 52 | 30 | 38 |
| PSOE | 2020 | 72 | 41 | 11 |
| PSOE | 2023 | 16 | 9 | 7 |
| PSdGPSOE | 2017 | 8 | 4 | 5 |
| UP | 2017 | 35 | 20 | 32 |
| UP | 2020 | 10 | 6 | 5 |
| UP | 2023 | 5 | 3 | 5 |
| UPN | 2017 | 2 | 1 | 2 |
| UPNPP | 2017 | 1 | 1 | 1 |
| Vox | 2023 | 7 | 4 | 5 |
| non_partisan | 2017 | 152 | 87 | 2 |
| non_partisan | 2020 | 19 | 11 | 2 |
| non_partisan | 2023 | 52 | 30 | 1 |
| unknown | 2023 | 4 | 2 | 4 |

## Marginal distribution by party

| Label | Units | Share |
|-------|------:|------:|
| PP | 71 | 17.8% |
| Cs | 59 | 14.8% |
| PSOE | 56 | 14.1% |
| UP | 42 | 10.6% |
| EAJPNV | 21 | 5.3% |
| ERCCATSÍ | 19 | 4.8% |
| ECP | 17 | 4.3% |
| CDC | 12 | 3.0% |
| PSCPSOE | 11 | 2.8% |
| CPEUPV | 10 | 2.5% |
| ECPGUAYEMELCANVI | 10 | 2.5% |
| EHBildu | 10 | 2.5% |
| ERCS | 10 | 2.5% |
| JxCatJUNTS | 9 | 2.3% |
| ECUP | 5 | 1.3% |
| PPFORO | 5 | 1.3% |
| PSdGPSOE | 5 | 1.3% |
| Vox | 5 | 1.3% |
| non_partisan | 5 | 1.3% |
| CCNCPNC | 4 | 1.0% |
| unknown | 4 | 1.0% |
| COMPROMÍSQ | 3 | 0.8% |
| BNG | 2 | 0.5% |
| UPN | 2 | 0.5% |
| UPNPP | 1 | 0.3% |

## Marginal distribution by year

| Label | Units | Share |
|-------|------:|------:|
| 2017 | 325 | 81.7% |
| 2023 | 41 | 10.3% |
| 2020 | 32 | 8.0% |

## Top 25 speakers in sample

| Label | Units | Share |
|-------|------:|------:|
| Albert Rivera Díaz | 5 | 1.3% |
| Aina Vidal Sáez | 5 | 1.3% |
| Yolanda Díaz Pérez | 5 | 1.3% |
| Oskar Matute García Jalón | 5 | 1.3% |
| Alicia Sánchez-Camacho Pérez | 5 | 1.3% |
| Isidro Martínez Oblanca | 5 | 1.3% |
| Esther Peña Camarero | 5 | 1.3% |
| María Galovart Carrera | 5 | 1.3% |
| Inés Cañizares Pacheco | 5 | 1.3% |
| Presidencia | 5 | 1.3% |
| Inés Arrimadas García | 5 | 1.3% |
| Idoia Sagastizabal Unzetabarrenetxea | 5 | 1.3% |
| Gabriel Rufián Romero | 5 | 1.3% |
| Gabriel Elorriaga Pisarik | 5 | 1.3% |
| Adriana Lastra Fernández | 5 | 1.3% |
| Pablo Echenique Robba | 5 | 1.3% |
| Mertxe Aizpurua Arzallus | 5 | 1.3% |
| María Montero Cuadrado | 5 | 1.3% |
| Pilar Garrido Gutiérrez | 5 | 1.3% |
| Jaume Moya Matas | 5 | 1.3% |
| María García Puig | 5 | 1.3% |
| Ester Capella Farré | 5 | 1.3% |
| María Perea Conillas | 5 | 1.3% |
| Jordi Xuclà Costa | 5 | 1.3% |
| Joseba Agirretxea Urresti | 5 | 1.3% |

## Reproduction

```bash
make segment-parlamint   # if pool missing
make parlamint-500
```
