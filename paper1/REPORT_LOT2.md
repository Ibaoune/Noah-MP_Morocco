# Rapport d'Exécution — LOT 2/4 : Routage HyMAP-2 (linres = 0) et Évaluations Débits & ET (RQ3)

**Date de génération :** 2026-11-22 01:00:15  
**Dépôt principal :** `paper1-closure` (`1d4efc3151504c9b1d914a56a28e91f2cccb1be1`)  
**Dépôt smap-xai-audit :** `elaabar` (`18d694ecd3d29477133b95e68875a8735644c198`)  

Ce rapport technique consigne l'exécution intégrale du **Lot 2/4** conformément au cahier des charges :
1. **Bloc B** : Routage HyMAP-2 (`linres = 0`) des expériences 2018 et extraction des références de production.
2. **Bloc C1** : Évaluation hydrologique des débits (RQ3) aux stations hydrométriques retenues.
3. **Bloc C2** : Évaluation de l'évapotranspiration (RQ3) face aux produits satellitaires GLEAM et WaPOR.

> [!NOTE]
> Conformément aux règles méthodologiques permanentes, ce rapport est généré par script à partir des fichiers CSV produits. Il ne contient aucune interprétation scientifique subjective.

---

## 1. Statut des Simulations et Routages HyMAP-2 (linres = 0)

Toutes les simulations de routage ont été exécutées avec la physique HyMAP-2, option réservoir linéaire désactivée (`linres = 0`), sur la grille 180×120 via le remapping de ruissellement validé.

| Expérience | Rôle | Job ID | Nœud Slurm | Durée | Statut | Code Sortie | Emplacement Sorties |
|---|---|---|---|---|---|---|---|
| **`OL_DAIC_2018_linres0`** | Sensibilité condition initiale DAIC | `8360678` | `slurm-compute-h21a5-u12-svn1` | 00:06:03 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/OL_DAIC_2018_linres0/` |
| **`ENS_OPL_2018_linres0`** | Contrôle ensemble 12 membres | `8360679` | `slurm-compute-h22b8-u9-svn2` | 00:06:00 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/ENS_OPL_2018_linres0/` |
| **`DA_nocdf_nowilt_2018_linres0`** | DA sans filtre flétrissement | `8360680` | `slurm-compute-h24d8-u8-svn1` | 00:06:01 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/DA_nocdf_nowilt_2018_linres0/` |
| **`DA_nocdf_linres0_2016_2020`** | Référence DA-NoCDF 5 ans | `8360645` | `slurm-compute-h21a5-u12-svn1` | 00:29:30 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/` |
| **`DA_cdf_linres0_2016_2020`** | Référence DA-CDF 5 ans | `8360646` | `slurm-compute-h22b8-u9-svn2` | 00:29:11 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/DA_cdf_linres0_2016_2020/` |
| **`OPL_linres0_2016_2020`** | Référence Open-Loop 5 ans | `8272794` | Toubkal Cluster | ~00:28:00 | **COMPLETED** | `0:0` | `experiments/NorthMor/routing/output/OPL_linres0_2016_2020/` |

### Note sur les simulations YYYY (2017) de Lot 1
Les simulations Noah-MP de robustesse sur l'année 2017 lancées lors du Lot 1 (`ENS_OPL_2017` Job 8360359, `OL_DAIC_2017` Job 8360360, `DA_nowilt_2017` Job 8360361, `DA_nostate_2017` Job 8360362, `DA_diag_2017` Job 8360363) sont toujours en cours d'exécution sur le cluster Toubkal (~2h20 écoulées). Comme prescrit par la consigne du Lot 2, elles seront routées et évaluées dès la fin de leur exécution dans le cadre du Lot 3.

---

## 2. Bloc B — Protocole de Routage et État Initial

- **Fichier de Restart Initial HyMAP :** `experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc`
  - Vérification de cohérence : `BSFSTO = 0.0`, `RNFSTO = 0.0` (linres = 0 strictement respecté) ; `RIVSTO_max = 7.38 × 10⁶ m³`.
  - Appliqué comme condition initiale au 2018-01-01 00:00 pour `OL_DAIC_2018`, `ENS_OPL_2018` et `DA_nocdf_nowilt_2018`.
- **Remapping du ruissellement :** script unifié `paper1/scripts/remap_runoff_2018_experiments.py` (application de la formule validée dans `routing/checks/03_remapping_ruissellement.md`).
  - Grille source : 181×121 (Noah-MP) $\to$ Grille cible : 180×120 (HyMAP-2).
  - Fichiers régularisés : 365 pas de temps journaliers 2018 + pas de raccordement frontière `201901020000.d01.nc`.
- **Stations sélectionnées :** 10 stations hydrométriques retenues selon `experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv` :
  - 4 stations journalières (Bouregreg) : Lalla Chafia, Sidi Jabeur (évaluation principale) ; Ain Loudah, S.M. Cherif (avec réserves).
  - 6 stations mensuelles (Sebou) : Ain Timedrine, Ait Khabbach, Azzaba, Dar El Hamra, Pont de Mdez (évaluation principale) ; Pont Ait Aissa (avec réserves).

---

## 3. Bloc C1 — Évaluation Hydrologique des Débits (RQ3)

Fichiers de données produits dans `paper1/tables/` :
- `streamflow_metrics.csv` : **336** lignes d'enregistrements (6 expériences, 10 stations, 4 saisons, pas journalier et mensuel).
- `streamflow_nic.csv` : **224** lignes d'enregistrements (4 paires NIC, 10 stations, 4 saisons, IC 95% bootstrap).

### 3.1. Métriques Journalières Annuelles aux Stations Principales du Bouregreg

Évaluation sur 364–365 jours journaliers observés face aux simulations HyMAP-2 (linres = 0) :

| Expérience | Station | Débit Obs (m³/s) | Débit Sim (m³/s) | Biais (m³/s) | r (Pearson) | γ (Kling 2012) | β (Biais ratio) | KGE (2012) | NSE | NSE log(Q+ε) | Biais JJA (m³/s) | Jours nuls (Sim/Obs) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **`OPL`** | Lalla Chafia | 9.736 | 7.990 | -1.746 | 0.456 | 0.339 | 0.821 | **0.125** | 0.169 | -0.120 | +6.238 | 0 / 0 |
| **`OL_DAIC`** | Lalla Chafia | 9.736 | 13.446 | +3.709 | 0.513 | 0.374 | 1.381 | **0.120** | 0.231 | -0.418 | +8.952 | 0 / 0 |
| **`ENS_OPL`** | Lalla Chafia | 9.736 | 15.695 | +5.959 | 0.520 | 0.394 | 1.612 | **0.014** | 0.174 | -0.519 | +9.645 | 0 / 0 |
| **`DA_nocdf`** | Lalla Chafia | 9.736 | 35.897 | +26.161 | 0.510 | 0.408 | 3.687 | **-1.795** | -2.339 | -1.364 | +14.406 | 0 / 0 |
| **`DA_cdf`** | Lalla Chafia | 9.736 | 15.809 | +6.072 | 0.535 | 0.338 | 1.624 | **-0.022** | 0.200 | -0.563 | +10.120 | 0 / 0 |
| **`DA_nocdf_nowilt`** | Lalla Chafia | 9.736 | 36.034 | +26.298 | 0.511 | 0.408 | 3.701 | **-1.808** | -2.358 | -1.356 | +14.198 | 0 / 0 |
| **`OPL`** | Sidi Jabeur | 10.871 | 3.931 | -6.940 | 0.656 | 0.260 | 0.362 | **-0.036** | 0.054 | 0.066 | +2.862 | 0 / 47 |
| **`OL_DAIC`** | Sidi Jabeur | 10.871 | 6.097 | -4.774 | 0.670 | 0.235 | 0.561 | **0.059** | 0.131 | -0.129 | +4.702 | 0 / 47 |
| **`ENS_OPL`** | Sidi Jabeur | 10.871 | 7.638 | -3.233 | 0.590 | 0.233 | 0.703 | **0.081** | 0.154 | -0.280 | +6.064 | 0 / 47 |
| **`DA_nocdf`** | Sidi Jabeur | 10.871 | 18.763 | +7.892 | 0.348 | 0.265 | 1.726 | **-0.221** | 0.032 | -0.959 | +10.781 | 0 / 47 |
| **`DA_cdf`** | Sidi Jabeur | 10.871 | 12.159 | +1.288 | 0.406 | 0.253 | 1.118 | **0.039** | 0.148 | -0.605 | +8.898 | 0 / 47 |
| **`DA_nocdf_nowilt`** | Sidi Jabeur | 10.871 | 18.718 | +7.847 | 0.350 | 0.265 | 1.722 | **-0.218** | 0.034 | -0.958 | +10.785 | 0 / 47 |

> Documentations des paramètres : $\epsilon = 0.01 \times \bar{Q}_{\text{obs}}$ (Lalla Chafia : $\epsilon = 0.091$ m³/s ; Sidi Jabeur : $\epsilon = 0.061$ m³/s). Seuil de débit nul : $Q < 0.001$ m³/s.

### 3.2. Contribution Relative d'Information (NIC) et Incertitude Bootstrap (IC à 95%)

Bootstrap par blocs mobiles (longueur de bloc = 30 jours, 1 000 tirages avec remise) sur le pas journalier annuel :

| Paire d'évaluation | Station | KGE Cible | KGE Réf | ΔKGE | NIC | NIC Moyenne Bootstrap | NIC IC 95% Bas | NIC IC 95% Haut | Statut |
|---|---|---|---|---|---|---|---|---|---|
| **`DA_nocdf vs ENS_OPL`**<br>(Effet des observations) | Lalla Chafia | -1.795 | 0.014 | -1.809 | **-1.835** | -1.692 | -2.548 | -1.021 | Dégradation |
| **`ENS_OPL vs OL_DAIC`**<br>(Effet de l'ensemble) | Lalla Chafia | 0.014 | 0.120 | -0.106 | **-0.120** | -0.115 | -0.225 | +0.003 | Dégradation |
| **`DA_nocdf vs OPL`**<br>(Comparaison naïve) | Lalla Chafia | -1.795 | 0.125 | -1.920 | **-2.195** | -2.289 | -4.295 | -0.963 | Dégradation |
| **`DA_nocdf_nowilt vs DA_nocdf`**<br>(Effet du filtre QC) | Lalla Chafia | -1.808 | -1.795 | -0.014 | **-0.005** | -0.004 | -0.015 | +0.005 | Dégradation |
| **`DA_nocdf vs ENS_OPL`**<br>(Effet des observations) | Sidi Jabeur | -0.221 | 0.081 | -0.303 | **-0.329** | -0.453 | -1.384 | -0.018 | Dégradation |
| **`ENS_OPL vs OL_DAIC`**<br>(Effet de l'ensemble) | Sidi Jabeur | 0.081 | 0.059 | +0.023 | **+0.024** | +0.016 | -0.064 | +0.050 | Gain |
| **`DA_nocdf vs OPL`**<br>(Comparaison naïve) | Sidi Jabeur | -0.221 | -0.036 | -0.185 | **-0.178** | -0.312 | -1.253 | +0.090 | Dégradation |
| **`DA_nocdf_nowilt vs DA_nocdf`**<br>(Effet du filtre QC) | Sidi Jabeur | -0.218 | -0.221 | +0.003 | **+0.003** | +0.003 | -0.001 | +0.008 | Gain |

### 3.3. Synthèse Mensuelle sur les 10 Stations Retenues (Année 2018 Complète)

| Station | Bassin | Statut | OPL KGE | OL_DAIC KGE | ENS_OPL KGE | DA_nocdf KGE | DA_cdf KGE | DA_nocdf_nowilt KGE | NIC (DA_nocdf vs ENS_OPL) |
|---|---|---|---|---|---|---|---|---|---|
| Lalla Chafia | Bouregreg | Retenue | 0.178 | 0.365 | 0.259 | -1.710 | 0.175 | -1.724 | **-2.657** |
| Sidi Jabeur | Bouregreg | Retenue | -0.003 | 0.146 | 0.233 | 0.121 | 0.396 | 0.126 | **-0.145** |
| Ain Timedrine | Sebou | Retenue | 0.071 | 0.077 | 0.070 | 0.156 | 0.141 | 0.148 | **+0.092** |
| Ait Khabbach | Sebou | Retenue | -0.063 | -0.064 | -0.038 | 0.513 | 0.194 | 0.540 | **+0.530** |
| Azzaba | Sebou | Retenue | -0.055 | -0.050 | -0.055 | 0.124 | 0.008 | 0.151 | **+0.170** |
| Dar El Hamra | Sebou | Retenue | -0.110 | -0.077 | -0.092 | 0.212 | -0.073 | 0.211 | **+0.279** |
| Pont de Mdez | Sebou | Retenue | -0.037 | -0.043 | -0.037 | -0.062 | 0.093 | -0.004 | **-0.023** |
| Ain Loudah | Bouregreg | Retenue | 0.246 | 0.334 | 0.266 | -1.850 | -0.881 | -1.916 | **-2.885** |
| S.M. Cherif | Bouregreg | Retenue | 0.259 | 0.271 | 0.165 | -2.401 | -1.247 | -2.415 | **-3.074** |
| Pont Ait Aissa | Sebou | Retenue | -0.332 | -0.324 | -0.316 | -0.427 | -0.318 | -0.491 | **-0.084** |

---

## 4. Bloc C2 — Évaluation de l'Évapotranspiration face à GLEAM v4.3a et WaPOR v3 (RQ3)

Fichiers de données produits dans `paper1/tables/` :
- `et_evaluation.csv` : **84** lignes d'enregistrements (évaluations par domaine, bassins Sebou et Bouregreg, saisons MAM et JJA, séries 2018 et 2016–2020).
- `et_evaluation_by_texture.csv` : **72** lignes d'enregistrements (stratifications par classes texturales dominantes USDA).
- `et_direction_of_change.csv` : **18** lignes d'enregistrements (quantification exacte du rapprochement / éloignement face aux observations).

### 4.1. Caractéristiques Réelles des Produits d'Observation Observées dans les Données

| Produit | Variable | Résolution Réelle Détectée | Pas de Temps Détecté | Période Disponible | Remarques Méthodologiques |
|---|---|---|---|---|---|
| **GLEAM v4.3a** | `E` (ET réelle), `Ep` (ET pot.) | **0,10° × 0,10°** (1800×3600 global) | Journalier (mm/jour) | 2016–2020 | Résolution native réelle 0,10° (contrairement au YAML qui mentionnait 0,25°). Variables composantes Et, Eb, Ei non présentes dans les données brutes téléchargées. |
| **WaPOR v3 AETI** | `AETI` (ET réelle annuelle) | **~250 m** (0,002246°) | Annuel (mm/an) | 2018–2020 | Couverture complète du Nord Marocain (1 410 mailles modèle communes). Composantes `WaPOR_v3_E` et `WaPOR_v3_T` disponibles. |
| **WaPOR v2 AETI** | `AETI` (ET réelle décadaire) | ~250 m (0,002246°) | Décadaire (mm/décade) | **2016 uniquement** | Seule l'année 2016 (36 décades) est téléchargée dans le sous-dossier `WaPOR_v2_AETI/`. L'année 2018 n'est pas disponible pour WaPOR v2. |
| **Masque Irrigation** | `IRRIGFRAC` | 0,05° × 0,05° | Constant | Fixe | La fraction d'irrigation est strictement nulle (`IRRIGFRAC = 0.0`) sur l'intégralité du domaine dans `lis_input_NorthMor_5km.nc`. Aucun masque externe disponible ; stratification omise conformément à la consigne. |

### 4.2. Question Clé : La réduction d'ET (DA_nocdf − ENS_OPL : −110,6 mm) rapproche-t-elle ou éloigne-t-elle le modèle des observations ?

Changement de la valeur absolue du biais ($\Delta |\text{Biais}| = |\text{Biais}_X| - |\text{Biais}_Y|$) et fraction de mailles se rapprochant des observations :

| Paire testée | Produit Réf. | Échelle / Bassin | Biais X (mm/an) | Biais Y (mm/an) | Différence (mm/an) | Δ|Biais| (mm/an) | Fraction se rapprochant (%) | Direction |
|---|---|---|---|---|---|---|---|---|
| **`DA_nocdf - ENS_OPL`** | GLEAM_v4.3a | Domain | +1.75 | +113.08 | -111.33 | **-111.33** | **62.22%** | **Rapprochement** |
| **`DA_nocdf - ENS_OPL`** | GLEAM_v4.3a | Sebou | +94.56 | +246.41 | -151.85 | **-151.85** | **79.11%** | **Rapprochement** |
| **`DA_nocdf - ENS_OPL`** | GLEAM_v4.3a | Bouregreg | +153.68 | +193.86 | -40.18 | **-40.18** | **66.67%** | **Rapprochement** |
| **`DA_nocdf - ENS_OPL`** | WaPOR_v3 | Domain | +62.64 | +183.71 | -121.07 | **-121.07** | **75.04%** | **Rapprochement** |
| **`DA_nocdf - ENS_OPL`** | WaPOR_v3 | Sebou | +74.72 | +226.09 | -151.37 | **-151.37** | **80.13%** | **Rapprochement** |
| **`DA_nocdf - ENS_OPL`** | WaPOR_v3 | Bouregreg | +145.99 | +185.56 | -39.58 | **-39.58** | **67.16%** | **Rapprochement** |
| **`ENS_OPL - OL_DAIC`** | GLEAM_v4.3a | Domain | +113.08 | +45.89 | +67.19 | **+67.19** | **22.65%** | **Éloignement** |
| **`ENS_OPL - OL_DAIC`** | GLEAM_v4.3a | Sebou | +246.41 | +180.78 | +65.63 | **+65.63** | **2.53%** | **Éloignement** |
| **`ENS_OPL - OL_DAIC`** | GLEAM_v4.3a | Bouregreg | +193.86 | +127.62 | +66.24 | **+66.24** | **0.00%** | **Éloignement** |
| **`ENS_OPL - OL_DAIC`** | WaPOR_v3 | Domain | +183.71 | +121.88 | +61.83 | **+61.83** | **8.87%** | **Éloignement** |
| **`ENS_OPL - OL_DAIC`** | WaPOR_v3 | Sebou | +226.09 | +160.50 | +65.59 | **+65.59** | **3.79%** | **Éloignement** |
| **`ENS_OPL - OL_DAIC`** | WaPOR_v3 | Bouregreg | +185.56 | +120.31 | +65.25 | **+65.25** | **4.48%** | **Éloignement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | GLEAM_v4.3a | Domain | -29.30 | +1.75 | -31.05 | **+27.54** | **43.13%** | **Éloignement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | GLEAM_v4.3a | Sebou | +48.31 | +94.56 | -46.25 | **-46.25** | **62.66%** | **Rapprochement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | GLEAM_v4.3a | Bouregreg | +131.86 | +153.68 | -21.82 | **-21.82** | **80.30%** | **Rapprochement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | WaPOR_v3 | Domain | +41.57 | +62.64 | -21.07 | **-21.07** | **54.61%** | **Rapprochement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | WaPOR_v3 | Sebou | +28.62 | +74.72 | -46.10 | **-46.10** | **59.31%** | **Rapprochement** |
| **`DA_nocdf_nowilt - DA_nocdf`** | WaPOR_v3 | Bouregreg | +124.50 | +145.99 | -21.49 | **-21.49** | **77.61%** | **Rapprochement** |

### 4.3. Évaluation Annuelle Complète 2018 par Domaine et Bassin Versant

| Expérience | Réf. Obs | Zone | ET Modèle (mm/an) | ET Obs (mm/an) | Biais (mm/an) | Biais Relatif (%) | RMSD (mm/an) | ubRMSD (mm/an) | R Mensuel |
|---|---|---|---|---|---|---|---|---|---|
| **`OPL`** | GLEAM_v4.3a | Domain | 328.0 | 268.8 | +59.3 | +22.1% | 123.5 | 108.4 | 0.792 |
| **`OPL`** | GLEAM_v4.3a | Sebou | 635.8 | 450.1 | +185.7 | +41.2% | 221.4 | 120.7 | -0.254 |
| **`OPL`** | GLEAM_v4.3a | Bouregreg | 573.5 | 446.5 | +127.0 | +28.4% | 143.7 | 67.3 | -0.042 |
| **`OL_DAIC`** | GLEAM_v4.3a | Domain | 314.6 | 268.8 | +45.9 | +17.1% | 118.7 | 109.4 | 0.790 |
| **`OL_DAIC`** | GLEAM_v4.3a | Sebou | 630.9 | 450.1 | +180.8 | +40.2% | 212.9 | 112.5 | -0.198 |
| **`OL_DAIC`** | GLEAM_v4.3a | Bouregreg | 574.1 | 446.5 | +127.6 | +28.6% | 140.6 | 59.0 | 0.125 |
| **`ENS_OPL`** | GLEAM_v4.3a | Domain | 381.8 | 268.8 | +113.1 | +42.1% | 160.4 | 113.8 | 0.774 |
| **`ENS_OPL`** | GLEAM_v4.3a | Sebou | 696.6 | 450.1 | +246.4 | +54.7% | 279.8 | 132.5 | -0.201 |
| **`ENS_OPL`** | GLEAM_v4.3a | Bouregreg | 640.4 | 446.5 | +193.9 | +43.4% | 203.9 | 63.3 | 0.063 |
| **`DA_nocdf`** | GLEAM_v4.3a | Domain | 270.5 | 268.8 | +1.8 | +0.7% | 130.0 | 130.0 | 0.710 |
| **`DA_nocdf`** | GLEAM_v4.3a | Sebou | 544.7 | 450.1 | +94.6 | +21.0% | 159.3 | 128.2 | 0.229 |
| **`DA_nocdf`** | GLEAM_v4.3a | Bouregreg | 600.2 | 446.5 | +153.7 | +34.4% | 170.0 | 72.7 | 0.623 |
| **`DA_cdf`** | GLEAM_v4.3a | Domain | 341.8 | 268.8 | +73.1 | +27.2% | 135.3 | 113.8 | 0.758 |
| **`DA_cdf`** | GLEAM_v4.3a | Sebou | 626.2 | 450.1 | +176.0 | +39.1% | 218.4 | 129.3 | -0.150 |
| **`DA_cdf`** | GLEAM_v4.3a | Bouregreg | 570.0 | 446.5 | +123.4 | +27.6% | 140.5 | 67.1 | -0.121 |
| **`DA_nocdf_nowilt`** | GLEAM_v4.3a | Domain | 239.5 | 268.8 | -29.3 | -10.9% | 132.8 | 129.5 | 0.727 |
| **`DA_nocdf_nowilt`** | GLEAM_v4.3a | Sebou | 498.5 | 450.1 | +48.3 | +10.7% | 133.5 | 124.5 | 0.343 |
| **`DA_nocdf_nowilt`** | GLEAM_v4.3a | Bouregreg | 578.4 | 446.5 | +131.9 | +29.5% | 160.2 | 90.9 | 0.623 |
| **`OPL`** | WaPOR_v3 | Domain | 483.6 | 353.4 | +130.2 | +36.8% | 180.9 | 125.6 | 0.675 |
| **`OPL`** | WaPOR_v3 | Sebou | 636.0 | 470.7 | +165.3 | +35.1% | 199.4 | 111.4 | 0.344 |
| **`OPL`** | WaPOR_v3 | Bouregreg | 565.0 | 445.3 | +119.7 | +26.9% | 150.1 | 90.6 | 0.478 |
| **`OL_DAIC`** | WaPOR_v3 | Domain | 475.3 | 353.4 | +121.9 | +34.5% | 173.3 | 123.2 | 0.696 |
| **`OL_DAIC`** | WaPOR_v3 | Sebou | 631.2 | 470.7 | +160.5 | +34.1% | 190.4 | 102.4 | 0.404 |
| **`OL_DAIC`** | WaPOR_v3 | Bouregreg | 565.6 | 445.3 | +120.3 | +27.0% | 146.6 | 83.8 | 0.541 |
| **`ENS_OPL`** | WaPOR_v3 | Domain | 537.1 | 353.4 | +183.7 | +52.0% | 224.9 | 129.7 | 0.664 |
| **`ENS_OPL`** | WaPOR_v3 | Sebou | 696.8 | 470.7 | +226.1 | +48.0% | 254.6 | 117.1 | 0.389 |
| **`ENS_OPL`** | WaPOR_v3 | Bouregreg | 630.8 | 445.3 | +185.6 | +41.7% | 208.5 | 95.0 | 0.464 |
| **`DA_nocdf`** | WaPOR_v3 | Domain | 416.1 | 353.4 | +62.6 | +17.7% | 160.7 | 147.9 | 0.668 |
| **`DA_nocdf`** | WaPOR_v3 | Sebou | 545.4 | 470.7 | +74.7 | +15.9% | 145.0 | 124.2 | 0.425 |
| **`DA_nocdf`** | WaPOR_v3 | Bouregreg | 591.2 | 445.3 | +146.0 | +32.8% | 171.1 | 89.2 | 0.641 |
| **`DA_cdf`** | WaPOR_v3 | Domain | 480.8 | 353.4 | +127.4 | +36.0% | 185.1 | 134.3 | 0.642 |
| **`DA_cdf`** | WaPOR_v3 | Sebou | 626.6 | 470.7 | +155.9 | +33.1% | 195.6 | 118.1 | 0.369 |
| **`DA_cdf`** | WaPOR_v3 | Bouregreg | 561.5 | 445.3 | +116.2 | +26.1% | 146.1 | 88.5 | 0.489 |
| **`DA_nocdf_nowilt`** | WaPOR_v3 | Domain | 395.0 | 353.4 | +41.6 | +11.8% | 162.6 | 157.2 | 0.617 |
| **`DA_nocdf_nowilt`** | WaPOR_v3 | Sebou | 499.3 | 470.7 | +28.6 | +6.1% | 134.4 | 131.3 | 0.366 |
| **`DA_nocdf_nowilt`** | WaPOR_v3 | Bouregreg | 569.8 | 445.3 | +124.5 | +28.0% | 161.0 | 102.1 | 0.613 |
| **`GLEAM_v4.3a`** | WaPOR_v3 | Domain | 393.3 | 360.0 | +33.3 | +9.3% | 117.0 | 112.2 | 0.714 |
| **`GLEAM_v4.3a`** | WaPOR_v3 | Sebou | 450.1 | 471.7 | -21.5 | -4.6% | 84.7 | 81.9 | 0.433 |
| **`GLEAM_v4.3a`** | WaPOR_v3 | Bouregreg | 446.5 | 448.9 | -2.4 | -0.5% | 74.8 | 74.7 | 0.454 |

### 4.4. Incertitude de Référence entre Produits d'Observation (GLEAM v4.3a vs WaPOR v3)

| Zone d'Analyse | Nb Mailles Communes | GLEAM v4.3a (mm/an) | WaPOR v3 (mm/an) | Écart GLEAM − WaPOR (mm/an) | RMSD Inter-produits (mm/an) |
|---|---|---|---|---|---|

---

## 5. Données Manquantes, Réserves et Traçabilité (Règle Permanente 5)

1. **Composantes de l'ET GLEAM (Et, Eb, Ei) :** non présentes dans l'archive téléchargée `data/validation/evapotranspiration/GLEAM/raw/` (seules les variables globales `E` et `Ep` sont présentes). L'évaluation a donc été menée sur l'ET totale.
2. **WaPOR v2 AETI en 2018 :** seule l'année 2016 est disponible dans `data/validation/evapotranspiration/WaPOR/WaPOR_v2_AETI/`. L'évaluation 2018 a été réalisée avec WaPOR v3 AETI (couverture complète du Nord Marocain).
3. **Masque d'irrigation :** `IRRIGFRAC` est égal à 0,0 sur 100% des mailles du domaine dans `data/lis_input/lis_input_NorthMor_5km.nc`. En l'absence de masque d'irrigation externe téléchargeable, la stratification irrigué/pluvial a été omise et documentée.
4. **Pas de temps 2018-05-31 Noah-MP :** segment historique 1 des runs `ENS_OPL_2018` et `DA_nocdf_nowilt_2018` arrêté le 2018-05-31 avant minuit. Le fichier de ruissellement a été régularisé pour assurer la stricte continuité temporelle de HyMAP-2 sans fausser les bilans annuels.
5. **Runs YYYY (2017) de robustesse :** toujours en cours d'exécution sur le cluster Toubkal (Jobs Slurm 8360359 à 8360363). Ils seront routés et évalués au Lot 3.

---

## 6. Sommes de Contrôle MD5 des Fichiers et Scripts Produits

| Fichier Produit | Rôle | Somme de Contrôle MD5 |
|---|---|---|
| `paper1/scripts/remap_runoff_2018_experiments.py` | Livrable Lot 2 | `87f9f168e94fb8271d5b71b640e13768` |
| `paper1/scripts/c1_evaluate_streamflow.py` | Livrable Lot 2 | `34bdafaf80da1da3b70a6ee35e1e5776` |
| `paper1/scripts/c2_evaluate_et.py` | Livrable Lot 2 | `5fc2091d1b14e01d407e2d33bb33cd0d` |
| `paper1/scripts/generate_report_lot2.py` | Livrable Lot 2 | `30317c075192d2a0863a9e61eb83b263` |
| `paper1/tables/streamflow_metrics.csv` | Livrable Lot 2 | `afa26a1f4af9aa87785342435d5d417c` |
| `paper1/tables/streamflow_nic.csv` | Livrable Lot 2 | `8351c2bc33c15384003cbda5a42bdd58` |
| `paper1/tables/et_evaluation.csv` | Livrable Lot 2 | `428ee6111e04a4f6e0551b19fe5dc082` |
| `paper1/tables/et_evaluation_by_texture.csv` | Livrable Lot 2 | `14dbbe2211fddbb31cca0c943f1690dd` |
| `paper1/tables/et_direction_of_change.csv` | Livrable Lot 2 | `74ffb8a177ef10e89af0a076b763496b` |

