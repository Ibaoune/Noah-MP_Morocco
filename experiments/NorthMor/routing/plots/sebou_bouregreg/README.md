# Résultats Scientifiques Validés : Sebou & Bouregreg

Ce dossier regroupe les résultats validés comparant les trois expériences de routage HyMAP (2016–2020) :
1. **OPL** : Simulation Open-Loop Noah-MP v3.6 (sans assimilation).
2. **DA-NoCDF** : Assimilation SMAP EnKF brute (sans prétraitement CDF).
3. **DA-CDF** : Assimilation SMAP EnKF avec correction préalable par CDF matching.

Le périmètre scientifique concerne exclusivement les bassins contrastés du **Sebou** et du **Bouregreg**. Le bassin du Ksob (station Adamna) est documenté dans les fiches techniques d'audit (`checks/`), le périmètre scientifique validé étant centré sur Sebou et Bouregreg.

---

## 1. Inventaire des Figures et Tables Présentes

### 1.1. Figures Scientifiques Actuelles (`figures/streamflow/`)

Seules trois figures validées comparant les trois simulations (OPL, DA-NoCDF, DA-CDF) et les observations aux stations sont actuellement retenues comme résultats scientifiques courants :

| Fichier canonique | Script générateur | Type de tracé | Station(s) & Période |
| :--- | :--- | :--- | :--- |
| [`figures/streamflow/fig_detaillee_2018_b_s_jabeur.png`](figures/streamflow/fig_detaillee_2018_b_s_jabeur.png) | `scripts/evaluate_sebou_bouregreg.py` | Hydrogramme journalier double panneau : crue linéaire + étiage log (avec points d'assec observés stricts) | Sidi Jabeur (`b_s_jabeur`, Grou), Année civile 2018 |
| [`figures/streamflow/fig_detaillee_2018_b_l_chafia.png`](figures/streamflow/fig_detaillee_2018_b_l_chafia.png) | `scripts/evaluate_sebou_bouregreg.py` | Hydrogramme journalier double panneau : crue linéaire + étiage log | Lalla Chafia (`b_l_chafia`, Bouregreg moyen), Année civile 2018 |
| [`figures/streamflow/fig_comparative_mensuelle_sebou.png`](figures/streamflow/fig_comparative_mensuelle_sebou.png) | `scripts/evaluate_sebou_bouregreg.py` | Chroniques mensuelles avec métriques intégrées (KGE, r, NSE, PBIAS) | Ain Timedrine, Dar El Hamra, Pont de Mdez (2016–2020) |

*Note sur les figures prévues : Les figures F1 (carte du domaine et des 11 stations Sebou-Bouregreg), F2 (diagrammes de partitionnement Qs/Qsb), F3-3exp (courbes de débits classés 3 simulations) et F4 (synthèse globale des performances) restent à produire ultérieurement dans leurs dossiers respectifs (`domain/`, `runoff/`, `performance/`).*

### 1.2. Tables Validées (`tables/`)

| Fichier CSV | Script générateur | Contenu & Variables | Périmètre |
| :--- | :--- | :--- | :---: |
| [`tables/tableau_synthese_11stations_sebou_bouregreg.csv`](tables/tableau_synthese_11stations_sebou_bouregreg.csv) | `scripts/evaluate_sebou_bouregreg.py` | Métriques globales KGE, NSE, r, PBIAS, débits moyens, note de duplication ABH | 11 stations |
| [`tables/tableau_diagnostic_5stations.csv`](tables/tableau_diagnostic_5stations.csv) | `scripts/evaluate_sebou_bouregreg.py` | Statistiques fines : moyennes, médianes, quantiles P95/P99, débits de pointe ($Q_{\max}$), ratios de pic | 5 stations cibles |
| [`tables/tableau_apports_noahmp_2018.csv`](tables/tableau_apports_noahmp_2018.csv) | `scripts/evaluate_sebou_bouregreg.py` | Volumes annuels Noah-MP amont délimités : $Q_s$, $Q_{sb}$, $V_{\text{tot}}$ en $\text{hm}^3$ | 5 stations cibles |

---

## 2. Distinction des Superficies des Bassins Versants

Pour chaque station cible, trois grandeurs de surface distinctes sont documentées :
1. **Aire officielle ABH** : Valeur administrative fournie par les Agences de Bassin Hydraulique dans l'inventaire des stations.
2. **Aire `HYMAP_drain_area`** : Aire de drainage amont calculée à la maille d'exutoire par le préprocesseur LDT HyMAP (`lis_input_corrigee.d01.nc`).
3. **Somme des superficies du masque amont** : Somme des aires géométriques des mailles Noah-MP connectées par les directions de drainage HyMAP, utilisée pour intégrer les flux volumiques ($Q_s$ et $Q_{sb}$) dans `tableau_apports_noahmp_2018.csv`.

| Station ID | Nom de station | Bassin | Aire officielle ABH ($\text{km}^2$) | Aire `HYMAP_drain_area` ($\text{km}^2$) | Somme masque amont ($\text{km}^2$) | Nombre de mailles |
| :--- | :--- | :--- | :---: | :---: | :---: | :---: |
| `b_s_jabeur` | Sidi Jabeur | Bouregreg | *Non renseignée* | 3 138.5 | 3 130.6 | 121 |
| `b_l_chafia` | Lalla Chafia | Bouregreg | *Non renseignée* | 3 341.6 | 3 333.3 | 133 |
| `ain_timedrine` | Ain Timedrine | Sebou | 4 387.0 | 4 448.6 | 4 437.6 | 175 |
| `dar_el_hamra` | Dar El Hamra | Sebou | 670.0 | 656.3 | 654.7 | 26 |
| `pont_de_mdez` | Pont de Mdez | Sebou | 3 435.0 | 3 429.1 | 3 420.6 | 135 |

---

## 3. Données Numériques Validées aux Stations Prioritaires

*Les métriques ci-dessous sont issues de `tables/tableau_diagnostic_5stations.csv` calculées strictement sur les périodes d'observation disponibles.*

### 3.1. Performances Hydrologiques Observées vs Simulées

| Station | Pas de temps | $Q_{\text{obs}}$ moyen | OPL KGE (PBIAS) | DA-NoCDF KGE (PBIAS) | DA-CDF KGE (PBIAS) | Corrélation $r$ (OPL / NoCDF / CDF) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Sidi Jabeur** | Journalier | 4.15 m³/s | -0.14 (-42.8 %) | -0.41 (+114.6 %) | **-0.08 (+53.0 %)** | 0.465 / 0.323 / 0.373 |
| **Lalla Chafia** | Journalier | 3.49 m³/s | +0.10 (+4.3 %) | -2.89 (+380.6 %) | **-0.66 (+151.6 %)** | 0.472 / 0.468 / 0.496 |
| **Ain Timedrine** | Mensuel | 9.17 m³/s | -0.32 (-77.3 %) | -0.07 (-65.0 %) | **-0.01 (-56.8 %)** | 0.380 / 0.568 / 0.622 |
| **Dar El Hamra** | Mensuel | 1.94 m³/s | -0.26 (-78.1 %) | +0.25 (-25.4 %) | **-0.14 (-45.4 %)** | 0.668 / 0.537 / 0.377 |
| **Pont de Mdez** | Mensuel | 3.97 m³/s | -0.19 (-57.9 %) | -0.12 (-57.3 %) | **+0.07 (-37.9 %)** | 0.390 / 0.463 / 0.616 |

*Note sur les observations : Les stations Ain Loudah et S.M. Cherif présentent des séries journalières 100 % identiques dans l'archive ABH (duplication de mesure).*

### 3.2. Volumes de Ruissellement Amont Intégrés (Année 2018)

*Volumes calculés sur les mailles du masque contributif amont (`tables/tableau_apports_noahmp_2018.csv`).*

| Station | OPL $Q_s / Q_{sb}$ ($\text{hm}^3$) | OPL $V_{\text{tot}}$ | DA-NoCDF $Q_s / Q_{sb}$ ($\text{hm}^3$) | DA-NoCDF $V_{\text{tot}}$ | DA-CDF $Q_s / Q_{sb}$ ($\text{hm}^3$) | DA-CDF $V_{\text{tot}}$ | Ratio CDF / NoCDF |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Sidi Jabeur** | 47.6 / 76.7 | 124.3 hm³ | 100.8 / 492.5 | 593.3 hm³ | 74.9 / 309.1 | 384.0 hm³ | 64.7 % |
| **Lalla Chafia** | 77.4 / 174.6 | 252.0 hm³ | 178.3 / 953.2 | 1 131.6 hm³ | 109.8 / 388.9 | 498.7 hm³ | 44.1 % |
| **Ain Timedrine** | 38.7 / 39.9 | 78.6 hm³ | 44.1 / 102.3 | 146.5 hm³ | 48.7 / 104.4 | 153.2 hm³ | 104.6 % |
| **Dar El Hamra** | 8.0 / 9.8 | 17.7 hm³ | 13.8 / 63.5 | 77.3 hm³ | 11.6 / 30.7 | 42.3 hm³ | 54.7 % |
| **Pont de Mdez** | 27.9 / 28.1 | 56.0 hm³ | 27.5 / 36.8 | 64.4 hm³ | 33.4 / 68.3 | 101.8 hm³ | 158.1 % |

---

## 4. Observations Factuelles sur les Régimes et Extrêmes

1. **Plancher d'étiage simulé dans le Bouregreg** : À la station de Sidi Jabeur, 310 jours à débit strictement nul ($Q_{\text{obs}} = 0.000\text{ m}^3/\text{s}$) sont enregistrés entre 2016 et 2020. Dans les trois simulations (OPL, DA-NoCDF, DA-CDF), les débits estivaux simulés restent systématiquement supérieurs à 1.4 m³/s.
2. **Débits de pointe journaliers** : Lors de l'événement de crue du 7 mars 2018 à Sidi Jabeur, le débit observé journalier moyen atteint 349.0 m³/s, tandis que les débits simulés atteignent 15.2 m³/s (OPL), 49.6 m³/s (DA-NoCDF) et 32.1 m³/s (DA-CDF).
