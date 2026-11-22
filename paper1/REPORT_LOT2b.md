# Rapport d'Exécution — LOT 2b : Vérifications Préalables au Lot 3

**Date de génération :** 2026-11-22 01:50:20  
**Branche Git :** `paper1-closure` (`ec79869c041b50fab16b9c6e57ce09898ad2ac8c`)  

Ce rapport technique consigne l'ensemble des vérifications factuelles prescrites pour le **Lot 2b**, sans interprétation subjective :
1. **Débit DA_nocdf à Lalla Chafia : vérifications sur l'origine du ruissellement et contrôle des artefacts** ;
2. **Corrections factuelles intégrées dans `paper1/REPORT_LOT2.md`** ;
3. **Indépendance des produits satellitaires d'évapotranspiration (GLEAM v4.3a et WaPOR v3) vis-à-vis de SMAP**.

---

## 0. Contrôle de l'Arborescence Git et Poussée de Branche

- Commande de vérification d'absence de binaires et NetCDF suivis :
  ```bash
  git ls-files | grep -E "\.nc$|\.bin$|/LIS$"
  ```
  *Résultat :* Seuls les fichiers historiques archivés dans le dépôt initial (`experiments/NorthMor/routing/ldt_hymap/*.nc`) sont présents ; aucun fichier NetCDF ni binaire issu des nouveaux calculs n'est suivi.
- Statut de la branche : `paper1-closure` synchronisée avec `origin/paper1-closure` (`https://github.com/Ibaoune/Noah-MP_Morocco.git`).

---

## 1. Débit DA_nocdf à Lalla Chafia : Analyse Factuelle de Ruissellement et Routage

### 1.a. Séries Journalières 2018 et Figure de Contrôle (Échelle Log)

- **Fichier de données journalières :** [`paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv) (365 pas de temps journaliers pour 2 stations et 6 expériences + obs).
- **Figure de contrôle hydrographe journalier :**
  - Format PNG haute résolution : [`paper1/figures/fig_control_daily_streamflow_log.png`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_control_daily_streamflow_log.png)
  - Format vectoriel PDF : [`paper1/figures/fig_control_daily_streamflow_log.pdf`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_control_daily_streamflow_log.pdf)

Statistiques annuelles journalières 2018 observées sur les séries produites :

| Station | Expérience / Obs | Débit Moyen (m³/s) | Débit Médian (m³/s) | Débit Max (m³/s) | Débit Min (m³/s) | Jours nuls (Q = 0) |
|---|---|---|---|---|---|---|
| Lalla Chafia | **`Observation ABH`** | 9.74 | 3.07 | 199.00 | 0.05 | 0 / 364 |
| Lalla Chafia | **`OPL (linres=0)`** | 7.97 | 6.73 | 68.90 | 1.43 | 0 / 365 |
| Lalla Chafia | **`OL_DAIC (linres=0)`** | 13.43 | 9.25 | 109.38 | 4.15 | 0 / 365 |
| Lalla Chafia | **`ENS_OPL (linres=0, 20m)`** | 15.68 | 10.39 | 116.68 | 5.14 | 0 / 365 |
| Lalla Chafia | **`DA_nocdf (linres=0)`** | 35.83 | 24.44 | 180.62 | 6.86 | 0 / 365 |
| Lalla Chafia | **`DA_cdf (linres=0)`** | 15.80 | 11.27 | 111.48 | 5.22 | 0 / 365 |
| Lalla Chafia | **`DA_nocdf_nowilt (linres=0)`** | 35.97 | 25.07 | 180.60 | 6.86 | 0 / 365 |
| Sidi Jabeur | **`Observation ABH`** | 10.87 | 1.54 | 349.00 | 0.00 | 47 / 365 |
| Sidi Jabeur | **`OPL (linres=0)`** | 3.93 | 3.17 | 31.77 | 1.32 | 0 / 365 |
| Sidi Jabeur | **`OL_DAIC (linres=0)`** | 6.10 | 5.05 | 43.28 | 2.93 | 0 / 365 |
| Sidi Jabeur | **`ENS_OPL (linres=0, 20m)`** | 7.64 | 6.43 | 53.25 | 3.46 | 0 / 365 |
| Sidi Jabeur | **`DA_nocdf (linres=0)`** | 18.76 | 14.34 | 117.61 | 3.61 | 0 / 365 |
| Sidi Jabeur | **`DA_cdf (linres=0)`** | 12.16 | 9.11 | 85.05 | 4.29 | 0 / 365 |
| Sidi Jabeur | **`DA_nocdf_nowilt (linres=0)`** | 18.72 | 14.36 | 117.56 | 3.61 | 0 / 365 |

### 1.b. Débit Moyen Mensuel 2018 par Expérience

Table issue de [`paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv) :

#### Lalla Chafia (Bouregreg) : Débit Moyen Mensuel 2018 (m³/s)

| Mois | Obs ABH | OPL | OL_DAIC | ENS_OPL | DA_nocdf | DA_cdf | DA_nocdf_nowilt | Écart DA_nocdf − ENS_OPL |
|---|---|---|---|---|---|---|---|---|
| 2018-01 | 8.28 | 3.79 | 8.44 | 10.92 | **20.23** | 9.58 | 20.23 | **+9.31** |
| 2018-02 | 8.36 | 2.93 | 8.81 | 11.35 | **44.58** | 12.77 | 44.58 | **+33.23** |
| 2018-03 | 39.57 | 10.52 | 30.03 | 41.36 | **108.11** | 34.09 | 108.11 | **+66.76** |
| 2018-04 | 16.79 | 16.62 | 31.91 | 36.63 | **73.61** | 35.85 | 73.60 | **+36.97** |
| 2018-05 | 9.56 | 11.11 | 18.26 | 20.49 | **39.01** | 21.70 | 38.96 | **+18.52** |
| 2018-06 | 1.20 | 7.90 | 11.74 | 12.89 | **20.55** | 13.80 | 20.42 | **+7.66** |
| 2018-07 | 0.24 | 6.66 | 9.17 | 9.76 | **13.81** | 10.01 | 13.57 | **+4.05** |
| 2018-08 | 0.58 | 6.17 | 8.01 | 8.37 | **11.02** | 8.64 | 10.78 | **+2.66** |
| 2018-09 | 0.92 | 6.81 | 8.33 | 8.60 | **10.67** | 8.63 | 10.48 | **+2.07** |
| 2018-10 | 7.50 | 10.17 | 11.64 | 11.90 | **13.79** | 11.73 | 13.76 | **+1.89** |
| 2018-11 | 19.90 | 8.82 | 9.99 | 10.22 | **27.76** | 11.93 | 29.27 | **+17.54** |
| 2018-12 | 3.76 | 3.97 | 4.62 | 5.45 | **47.31** | 10.77 | 48.34 | **+41.87** |

#### Sidi Jabeur (Grou) : Débit Moyen Mensuel 2018 (m³/s)

| Mois | Obs ABH | OPL | OL_DAIC | ENS_OPL | DA_nocdf | DA_cdf | DA_nocdf_nowilt | Écart DA_nocdf − ENS_OPL |
|---|---|---|---|---|---|---|---|---|
| 2018-01 | 15.74 | 2.61 | 5.03 | 5.54 | **7.82** | 6.45 | 7.82 | **+2.28** |
| 2018-02 | 15.36 | 2.56 | 4.82 | 5.48 | **19.60** | 10.52 | 19.60 | **+14.11** |
| 2018-03 | 32.41 | 4.92 | 8.16 | 10.84 | **39.96** | 20.90 | 39.96 | **+29.12** |
| 2018-04 | 19.41 | 5.43 | 9.53 | 14.06 | **40.63** | 27.75 | 40.62 | **+26.57** |
| 2018-05 | 9.82 | 4.09 | 6.93 | 9.97 | **24.18** | 18.97 | 24.16 | **+14.21** |
| 2018-06 | 0.53 | 3.13 | 5.29 | 7.19 | **14.14** | 11.89 | 14.12 | **+6.95** |
| 2018-07 | 0.10 | 3.00 | 4.80 | 6.07 | **10.32** | 8.32 | 10.35 | **+4.25** |
| 2018-08 | 0.00 | 3.08 | 4.66 | 5.59 | **8.62** | 7.20 | 8.61 | **+3.03** |
| 2018-09 | 4.85 | 3.80 | 5.34 | 6.14 | **8.65** | 7.23 | 8.73 | **+2.51** |
| 2018-10 | 14.29 | 5.98 | 7.76 | 8.54 | **11.03** | 9.12 | 11.03 | **+2.49** |
| 2018-11 | 16.81 | 5.92 | 7.38 | 8.01 | **15.14** | 9.10 | 14.91 | **+7.13** |
| 2018-12 | 1.50 | 2.62 | 3.43 | 4.18 | **25.28** | 8.53 | 24.90 | **+21.10** |

### 1.c. Bilan Moyen Mensuel et Annuel sur le Bassin Versant Amont Réel (D8 HyMAP)

- **Délimitation D8 HyMAP :**
  - **Lalla Chafia :** 133 mailles, aire calculée = **3 333,35 km²** (aire table d'inventaire = 3 341,60 km², écart = −8,25 km², soit **−0,25%**).
  - **Sidi Jabeur :** 121 mailles, aire calculée = **3 130,55 km²** (aire table d'inventaire = 3 138,52 km², écart = −7,97 km², soit **−0,25%**).

#### Synthèse Annuelle du Bilan Hydrique 2018 sur le Bassin Amont de Lalla Chafia (mm/an)

| Expérience | P (mm) | ET (mm) | Qs (mm) | Qsb (mm) | Qs+Qsb (mm) | ΔS (mm) | Incr L1 (mm) | Incr L2 (mm) | Incr L3 (mm) | Incr L4 (mm) | Incr Total (mm) | Résidu Bilan (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`DA_cdf`** | 698.0 | 568.3 | 35.3 | 120.5 | **155.9** | -11.9 | -1.9 | -36.5 | -56.7 | -24.4 | **-119.4** | -133.7 |
| **`DA_nocdf`** | 698.0 | 629.8 | 57.5 | 295.4 | **352.9** | +39.6 | +26.5 | +43.8 | +69.7 | +61.4 | **+201.4** | -123.0 |
| **`DA_nocdf_nowilt`** | 698.0 | 648.3 | 57.6 | 296.5 | **354.1** | +35.4 | +5.1 | +44.3 | +68.5 | +53.7 | **+171.6** | -168.1 |
| **`ENS_OPL`** | 698.0 | 687.3 | 37.6 | 116.6 | **154.2** | +47.6 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -191.1 |
| **`OL_DAIC`** | 698.0 | 628.0 | 34.9 | 97.3 | **132.2** | +19.4 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -81.6 |
| **`OPL`** | 698.0 | 585.1 | 25.0 | 54.1 | **79.1** | +50.2 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -16.3 |

#### Synthèse Annuelle du Bilan Hydrique 2018 sur le Bassin Amont de Sidi Jabeur (mm/an)

| Expérience | P (mm) | ET (mm) | Qs (mm) | Qsb (mm) | Qs+Qsb (mm) | ΔS (mm) | Incr L1 (mm) | Incr L2 (mm) | Incr L3 (mm) | Incr L4 (mm) | Incr Total (mm) | Résidu Bilan (mm) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`DA_cdf`** | 578.3 | 520.8 | 25.9 | 102.0 | **127.9** | +8.1 | -8.7 | -32.4 | -47.9 | -27.4 | **-116.4** | -195.1 |
| **`DA_nocdf`** | 578.3 | 540.9 | 34.9 | 162.8 | **197.6** | +54.0 | -15.4 | +14.9 | +43.8 | +8.8 | **+52.1** | -162.1 |
| **`DA_nocdf_nowilt`** | 578.3 | 563.9 | 34.8 | 162.2 | **197.0** | +53.1 | -34.3 | +12.9 | +41.7 | +4.4 | **+24.7** | -211.1 |
| **`ENS_OPL`** | 578.3 | 615.5 | 23.9 | 56.6 | **80.5** | +44.0 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -161.7 |
| **`OL_DAIC`** | 578.3 | 547.8 | 21.8 | 42.6 | **64.4** | +35.8 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -69.7 |
| **`OPL`** | 578.3 | 511.7 | 16.6 | 25.3 | **41.9** | +45.6 | +0.0 | +0.0 | +0.0 | +0.0 | **+0.0** | -20.9 |

#### Ruissellement Annuel Multi-Annuel (2016–2020) de DA_nocdf sur les Deux Bassins

Données issues de [`paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv) :

| Station | Année | Nb Jours | Qs (mm) | Qsb (mm) | Qs + Qsb (mm) | Volume Ruissellement (hm³) | Débit Moyen Équivalent (m³/s) |
|---|---|---|---|---|---|---|---|
| Lalla Chafia | 2016 | 366 | 11.44 | 36.12 | **47.56** | 158.5 | **5.01** |
| Sidi Jabeur | 2016 | 366 | 8.66 | 19.98 | **28.63** | 89.6 | **2.83** |
| Lalla Chafia | 2017 | 365 | 19.49 | 127.37 | **146.86** | 489.5 | **15.52** |
| Sidi Jabeur | 2017 | 365 | 11.83 | 73.89 | **85.73** | 268.4 | **8.51** |
| Lalla Chafia | 2018 | 365 | 53.50 | 286.81 | **340.31** | 1134.4 | **35.97** |
| Sidi Jabeur | 2018 | 365 | 32.20 | 157.80 | **190.00** | 594.8 | **18.86** |
| Lalla Chafia | 2019 | 365 | 13.60 | 130.93 | **144.54** | 481.8 | **15.28** |
| Sidi Jabeur | 2019 | 365 | 9.47 | 74.61 | **84.07** | 263.2 | **8.35** |
| Lalla Chafia | 2020 | 366 | 12.81 | 104.64 | **117.45** | 391.5 | **12.38** |
| Sidi Jabeur | 2020 | 366 | 9.15 | 53.03 | **62.18** | 194.7 | **6.16** |

### 1.d. Contrôle du Ruissellement Remappé (180×120) vs Natif (181×121 Projeté)

Évaluation de la conservation de masse lors du remapping sur le bassin amont de Lalla Chafia en 2018 :

Données issues de [`paper1/tables/remap_runoff_check_lalla_chafia_2018.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/remap_runoff_check_lalla_chafia_2018.csv) :

| Expérience | Station | Qs Natif (mm) | Qsb Natif (mm) | Total Natif (mm) | Qs Remappé (mm) | Qsb Remappé (mm) | Total Remappé (mm) | Écart (mm) | Écart Relatif (%) |
|---|---|---|---|---|---|---|---|---|---|
| **`DA_nocdf`** | Lalla Chafia | 49.28 | 277.32 | **326.60** | 53.50 | 286.81 | **340.31** | **+13.71** | **+4.20%** |
| **`ENS_OPL`** | Lalla Chafia | 37.90 | 116.95 | **154.85** | 35.08 | 113.18 | **148.26** | **-6.59** | **-4.26%** |

### 1.e. Comparaison avec le Routage Historique (linres = 1 vs linres = 0)

Débit moyen annuel 2018 simulé à Lalla Chafia par DA_nocdf face aux observations :

| Configuration Routage | Expérience | Débit Moyen 2018 (m³/s) | Biais face Obs (m³/s) | Source des Données |
|---|---|---|---|---|
| **Observation ABH** | In-situ | **9,74** | 0,00 | `data/streamflow_clean/obs_daily.csv` |
| **Routage Historique (linres = 1)** | `DA_nocdf_2016_2020` | **35,63** | +25,89 | `experiments/NorthMor/routing/output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv` |
| **Routage Actuel (linres = 0)** | `DA_nocdf_linres0_2016_2020` | **35,90** | +26,16 | `paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv` |
| **Différence (linres = 0 − linres = 1)** | DA_nocdf | **+0,27** (+0,76%) | — | Écart lié à la dynamique de stockage fluvial |

### 1.f. Carte et Top 20 Mailles de Différence de Qsb Annuel (DA_nocdf − ENS_OPL)

- **Carte de la différence de ruissellement souterrain Qsb (2018) :**
  - Image PNG : [`paper1/figures/fig_map_qsb_difference_da_minus_ens.png`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_map_qsb_difference_da_minus_ens.png)
  - Fichier PDF vectoriel : [`paper1/figures/fig_map_qsb_difference_da_minus_ens.pdf`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/figures/fig_map_qsb_difference_da_minus_ens.pdf)
- **Table des 20 mailles où l'écart est le plus marqué :** [`paper1/tables/top20_cells_qsb_difference.csv`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/tables/top20_cells_qsb_difference.csv)

| Rang | Coordonnées (Lon, Lat) | Texture Dominante (USDA) | Qsb DA_nocdf (mm) | Qsb ENS_OPL (mm) | Différence Qsb (mm) | Bassin Hydrographique | Amont Lalla Chafia | Amont Sidi Jabeur |
|---|---|---|---|---|---|---|---|---|
| 1 | (-5.6250°E, 35.2750°N) | Loam (ID 6) | 805.3 | 363.8 | **+441.5** | Hors Sebou/Bouregreg | Non | Non |
| 2 | (-5.6750°E, 35.3250°N) | Loam (ID 6) | 842.3 | 404.4 | **+437.9** | Hors Sebou/Bouregreg | Non | Non |
| 3 | (-5.6750°E, 35.2750°N) | Loam (ID 6) | 819.9 | 384.3 | **+435.6** | Hors Sebou/Bouregreg | Non | Non |
| 4 | (-5.6250°E, 35.0250°N) | Loam (ID 6) | 830.9 | 408.4 | **+422.5** | Hors Sebou/Bouregreg | Non | Non |
| 5 | (-5.7250°E, 35.3250°N) | Loam (ID 6) | 795.3 | 376.4 | **+418.9** | Hors Sebou/Bouregreg | Non | Non |
| 6 | (-5.6250°E, 35.3250°N) | Loam (ID 6) | 776.5 | 364.0 | **+412.5** | Hors Sebou/Bouregreg | Non | Non |
| 7 | (-5.6750°E, 35.2250°N) | Loam (ID 6) | 740.5 | 329.9 | **+410.6** | Hors Sebou/Bouregreg | Non | Non |
| 8 | (-5.1750°E, 34.8250°N) | Loam (ID 6) | 797.4 | 386.8 | **+410.6** | Sebou | Non | Non |
| 9 | (-5.2250°E, 34.8750°N) | Loam (ID 6) | 826.4 | 417.9 | **+408.5** | Sebou | Non | Non |
| 10 | (-5.6250°E, 35.0750°N) | Loam (ID 6) | 798.4 | 390.3 | **+408.2** | Hors Sebou/Bouregreg | Non | Non |
| 11 | (-5.2250°E, 34.8250°N) | Loam (ID 6) | 840.7 | 433.9 | **+406.8** | Sebou | Non | Non |
| 12 | (-5.1750°E, 34.8750°N) | Loam (ID 6) | 801.8 | 399.1 | **+402.6** | Sebou | Non | Non |
| 13 | (-5.5250°E, 35.1250°N) | Loam (ID 6) | 780.0 | 383.0 | **+397.0** | Hors Sebou/Bouregreg | Non | Non |
| 14 | (-5.6250°E, 34.7750°N) | Loam (ID 6) | 745.2 | 353.3 | **+391.9** | Hors Sebou/Bouregreg | Non | Non |
| 15 | (-5.6250°E, 34.8250°N) | Loam (ID 6) | 705.8 | 316.1 | **+389.7** | Hors Sebou/Bouregreg | Non | Non |
| 16 | (-5.5250°E, 35.1750°N) | Loam (ID 6) | 812.9 | 423.5 | **+389.4** | Hors Sebou/Bouregreg | Non | Non |
| 17 | (-5.1250°E, 34.8250°N) | Loam (ID 6) | 779.8 | 394.4 | **+385.4** | Sebou | Non | Non |
| 18 | (-5.4250°E, 35.3250°N) | Loam (ID 6) | 724.4 | 339.9 | **+384.5** | Hors Sebou/Bouregreg | Non | Non |
| 19 | (-5.0750°E, 34.7750°N) | Loam (ID 6) | 770.7 | 386.2 | **+384.4** | Sebou | Non | Non |
| 20 | (-5.1250°E, 34.7750°N) | Loam (ID 6) | 773.5 | 389.5 | **+384.1** | Sebou | Non | Non |

---

## 2. Synthèse des Corrections Factuelles Appliquées dans `paper1/REPORT_LOT2.md`

Le script de génération [`paper1/scripts/generate_report_lot2.py`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/scripts/generate_report_lot2.py) a été mis à jour et exécuté pour régénérer [`paper1/REPORT_LOT2.md`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/REPORT_LOT2.md) avec les corrections suivantes :

1. **Taille de l'ensemble ENS_OPL :** mention corrigée de 12 à **20 membres** (`Number of ensembles per tile: 20` dans `lis.config`).
2. **Dénomination exacte des runs du Lot 1 :**
   - `ENS_OPL_2017` (Job 8360359), `OL_DAIC_2017` (Job 8360360, terminé), `DA_nocdf_nowilt_2017` (Job 8360361) ;
   - `DA_nocdf_nostate_2018MAM` (Job 8360362, diagnostic blocage état MAM 2018) et `DA_nocdf_diag_2018ND` (Job 8360363, diagnostic incréments ND 2018) — et non « DA_nostate_2017 » ou « DA_diag_2017 » ;
   - `DA_nocdf_diag_15min_2018Nov` (diagnostic pas fin 15 min novembre 2018).
3. **Fichier de raccordement du 31-05-2018 (ENS_OPL, DA_nocdf_nowilt) :**
   - Jour dupliqué dans le ruissellement : **30 mai 2018** (`LIS_HIST_201805310000.d01.nc`).
   - Jour manquant dans le répertoire principal : **31 mai 2018** (`LIS_HIST_201806010000.d01.nc`, préservé dans `output/_partial_201806_hang/SURFACEMODEL_201806/`).
   - Traitement dans `smap-xai-audit` : les scripts de bilan antérieurs lisaient directement le dossier standard sans inclure `_partial_201806_hang/`.
   - Ordre de grandeur de l'effet sur le domaine : strictly inférieur à 0,11 mm sur l'ET (−0,094 mm pour ENS_OPL, −0,105 mm pour DA_nowilt), inférieur à 0,012 mm sur Qs, et inférieur à 0,001 mm sur Qsb (+0,0007 mm pour ENS_OPL, +0,0010 mm pour DA_nowilt), soit un impact relatif < 0,03% sur l'ET.
4. **Configurations de routage DA (coldstart 2016–2020) :**
   - Diff documenté dans [`paper1/runs/routing/README.md`](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/paper1/runs/routing/README.md).
   - Confirmation : `OPL_linres0_2016_2020` est également configuré en coldstart (`Routing restart mode: 0`) au 01-01-2016.
   - Aucune sortie préalable n'a été écrasée (dossiers de sortie vierges).

---

## 3. Produits d'Évapotranspiration : Indépendance Méthodologique vis-à-vis de SMAP

Conformément à la consigne, les données et la documentation disponibles rapportent les éléments factuels suivants :

### 3.1. GLEAM v4.3a (Global Land Evaporation Amsterdam Model)

- **Référence bibliographique officielle (attributs NetCDF) :**
  > Miralles, D.G. et al. 2025: global land evaporation and soil moisture dataset at 0.1° resolution from 1980 to near present, *Scientific Data*, 12, 416, doi: [10.1038/s41597-025-04610-y](https://doi.org/10.1038/s41597-025-04610-y).
- **Utilisation d'humidité du sol micro-ondes :**
  - Le modèle GLEAM v4 assimile explicitement l'humidité de surface satellitaire issue des micro-ondes via un schéma de *nudging newtonien* dans sa première couche de sol pour corriger le bilan hydrique.
  - La source de données micro-ondes utilisée est le produit multi-satellites **ESA CCI Soil Moisture** (COMBINED / ACTIVE / PASSIVE).
  - Depuis avril 2015, l'archive ESA CCI intègre directement les radiomètres micro-ondes en bande L de la mission **SMAP**, ainsi que SMOS et ASCAT.
  - GLEAM v4 utilise en outre la profondeur optique de la végétation micro-ondes (VODCA L, issue conjointement de SMAP et SMOS).
- **Statut d'indépendance vis-à-vis de SMAP :** **Non indépendant de SMAP** (assimilation indirecte de données micro-ondes incluant SMAP).

### 3.2. WaPOR v3 (Water Productivity through Open-access of Remotely sensed derived data / ETLook)

- **Référence méthodologique officielle (FAO / eLEAF) :**
  > FAO (2020, 2023): WaPOR Database Methodology: Version 2 & 3. Food and Agriculture Organization of the United Nations, Rome.
  > Collection GEE : `projects/UNFAO/wapor/v3/L1-AETI-D`.
- **Utilisation d'humidité du sol micro-ondes :**
  - L'algorithme ETLook de WaPOR v3 repose sur une formulation à deux couches (évaporation du sol nu et transpiration de la végétation selon l'équation de Penman-Monteith) contrainte par le bilan d'énergie en surface.
  - Les forçages satellitaires d'ETLook sont : la température de surface thermique infrarouge (**LST** issue de MODIS et VIIRS), les indices spectraux de végétation (**NDVI**, albédo issus de Sentinel-2 et PROBA-V), et les réanalyses météorologiques horaires (**ERA5**).
  - Le calcul de l'humidité relative du sol dans WaPOR v3 est dérivé en interne par inversion de la température de surface thermique infrarouge et du bilan hydrique ; il **n'assimile ni n'ingère aucune observation d'humidité du sol par micro-ondes** (ni SMAP, ni SMOS, ni ESA CCI).
- **Statut d'indépendance vis-à-vis de SMAP :** **Strictement indépendant de SMAP** (aucune donnée micro-ondes SMAP en entrée).

---

## 4. Sommes de Contrôle MD5 des Fichiers et Scripts Produits (Lot 2b)

| Fichier Produit | Rôle | Somme de Contrôle MD5 |
|---|---|---|
| `paper1/scripts/c1_verify_lalla_chafia_streamflow.py` | Livrable Lot 2b | `4b4608c8413083488303ce0cde03012e` |
| `paper1/scripts/calc_catchment_water_balance.py` | Livrable Lot 2b | `fbd1ffbe4d47d5519a965204f9d35290` |
| `paper1/scripts/generate_report_lot2.py` | Livrable Lot 2b | `40805abe5a46d044b330b375bc5c9677` |
| `paper1/scripts/generate_report_lot2b.py` | Livrable Lot 2b | `5305fceb5bca2bd74ccb7f214c482540` |
| `paper1/runs/routing/README.md` | Livrable Lot 2b | `a47cc726bdcd481056dc549d8575e5ae` |
| `paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv` | Livrable Lot 2b | `8e2fec42bbd8c38cf3a56d3e275733fd` |
| `paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv` | Livrable Lot 2b | `bef059a5dc21d5bfcfc1741c18d3f0b6` |
| `paper1/tables/water_balance_upstream_catchments_2018.csv` | Livrable Lot 2b | `ba320a476a0cbe7d548fe83f303fbeb3` |
| `paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv` | Livrable Lot 2b | `4c3e684a0895db46f8dbf46ce99aa7d0` |
| `paper1/tables/remap_runoff_check_lalla_chafia_2018.csv` | Livrable Lot 2b | `81f2beb44fddfd40ec4666adab509de0` |
| `paper1/tables/top20_cells_qsb_difference.csv` | Livrable Lot 2b | `6d13e7b45c514f07415bf973cd73a058` |
| `paper1/figures/fig_control_daily_streamflow_log.png` | Livrable Lot 2b | `45343a5268a6b32bba291a93b9e8108e` |
| `paper1/figures/fig_map_qsb_difference_da_minus_ens.png` | Livrable Lot 2b | `c5a8c9aca1946c02609d527add2bd4d9` |
| `paper1/REPORT_LOT2.md` | Livrable Lot 2b | `3b651574941ffbdcddd04bd4956bf2e8` |

