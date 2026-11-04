# Registre des Expériences — Projet NoahMP_Morocco

Ce document constitue le registre de référence exhaustif de toutes les simulations et expériences du projet **NoahMP_Morocco** sous NASA LIS (Land Information System) et Noah-MP 4.0.1 sur le domaine **NorthMor** (181 × 121 = 21 901 points de grille, résolution ~5 km).

---

## 1. Expériences de Production (Sanctuarisées)

| Nom de l'expérience | Type | Membres | Scaling | Irrigation | Période simulée | Statut & Sorties | Emplacement | Rôle scientifique |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- |
| **`SPINUP_OPL`** | OL (déterministe) | 1 | Aucun | Non | 2005-01-01 à 2016-01-01 | 11 ans terminés (11 tranches annuelles) | `experiments/NorthMor/SPINUP/SPINUP_OPL` | Étape 1 du spinup : équilibrage physique des stocks profonds et de la nappe. Génère le restart 20160101 pour OPL. |
| **`ENS_OPL_2015`** | Ensemble OL | 20 | Aucun | Non | 2015-01-01 à 2016-01-01 | 12 mois terminés (1 an) | `experiments/NorthMor/SPINUP/ENS_OPL_2015` | Étape 2 du spinup : propagation de la dispersion d'ensemble pour initialiser les perturbations d'assimilation. |
| **`SPINUP_DA`** | DA EnKF | 20 | Aucun | Non | 2015-04-01 à 2016-01-01 | 9 mois terminés (avr–déc 2015) | `experiments/NorthMor/SPINUP/SPINUP_DA` | Étape 3 du spinup : stabilisation du filtre EnKF avec SMAP. Génère les restarts surf + pert au 20160101 pour les runs DA 2016–2020. |
| **`OPL_noirr_2016_2020`** | OL (déterministe) | 1 | Aucun | Non | 2016-01-01 à 2021-01-01 | 60 mois terminés (100%) | `experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020` | Simulation de référence unperturbed (Open Loop). Sert de base au calcul de la climatologie modèle pour la CDF. |
| **`DA_nocdf_noirr_2016_2020`** | DA EnKF | 20 | Aucun (direct) | Non | 2016-01-01 à 2021-01-01 | 60 mois terminés (100%) | `experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020` | Assimilation SMAP brute sans correction de biais. Baseline pour quantifier l'impact de la CDF. |
| **`DA_cdf_noirr_2016_2020`** | DA EnKF | 20 | CDF matching | Non | 2016-01-01 à 2021-01-01 | 60 mois terminés (100%) | `experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020` | Simulation DA principale de production avec CDF corrigée sur NorthMor (16 030 points terre). |
| **`CDF`** | LDT CDF matching | 1 | CDF matching | Non | 2016-01-01 à 2021-01-01 | Terminé | `experiments/NorthMor/matrix_2016_2020/CDF` | Dépendance critique : calcul des paramètres CDF modèle (`noahmp_model_cdf_NorthMor.nc`) et obs (`smap_obs_cdf_NorthMor.nc`). |
| **`_ARCHIVE_WRONG_CDF_DOMAIN`** | DA EnKF | 20 | CDF (Maroc global) | Non | 2016-01-01 à 2021-01-01 | 60 mois | `experiments/NorthMor/matrix_2016_2020/_ARCHIVE_WRONG_CDF_DOMAIN` | Archive historique : simulation initiale avec CDF calculée sur le domaine national au lieu de NorthMor. |

---

## 2. Expériences de Test et Diagnostics (`matrix_2016_2020/tests/`)

| Nom | Type | Membres | Période | Statut | Binaire LIS | Objet & Conclusion |
| :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **`DA_nocdf_TEST_nowilt`** | DA EnKF | 20 | 2018-07 à 2018-09 | 2 mois terminés | `src/lisf_nowilt/lis/LIS` | Test de l'effet du seuil de flétrissement du QC : condition `smobs - smcwlt < 0.02` désactivée dans `noahmp401_qc_soilmobs.F90`. |
| **`DA_cdf_TEST`** | DA EnKF | 20 | 2018-01 & 2018-08 | 2 mois terminés | `src/lisf/lis/LIS` | Test de validation préliminaire de la chaîne DA avec la nouvelle CDF NorthMor corrigée. |
| **`DA_cdf_TEST_1619`** | DA EnKF | 20 | 2018-01 & 2018-08 | 2 mois terminés | `src/lisf/lis/LIS` | Test de sensibilité sur la fenêtre d'échantillonnage de la CDF (calculée sur 2016–2019 au lieu de 2016–2020). |
| **`DA_repro_check_3days`** | DA EnKF | 20 | 2018-07-01 au 2018-07-04 | 3 jours terminés | `src/lisf/lis/LIS` | Test court de reproductibilité numérique du filtre EnKF sur juillet 2018. |
| **`ENS_OPL_TEST_3days`** | ENS OL | 20 | 3 jours (2018) | Terminé | `src/lisf/lis/LIS` | **NON CONCLUANT** : la dispersion des membres était héritée du restart DA initial plutôt qu'induite par les perturbations de forçage pures. |
| **`OPL_hourly_201807`** | OL (déterministe) | 1 | 2018-07 | 1 mois terminé | `src/lisf/lis/LIS` | Test diagnostique avec pas de sortie horaire pour analyser le cycle diurne en été. |

---

## 3. Expériences Prévues (`matrix_2016_2020/planned/`)

| Nom | Type | Membres | Scaling | Statut | Remarques critiques |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **`DA_anomaly_noirr_2016_2020`** | DA EnKF | 20 | Anomaly (Kwon et al. 2022) | Non exécutée | Scaling par anomalies SMAP. **ATTENTION :** son template pointe actuellement vers un chemin CDF obsolète (`matrix_2016/CDF/OUTPUT_noirr/smap_cdf.nc`) et doit impérativement être mis à jour avant exécution. |
| **`ENS_OPL_2018`** | ENS OL | 20 | Aucun | Suspendue | Ensemble Open Loop 2018 (20 membres). Tâche suspendue conformément aux consignes. |

---

## 4. Module de Routage Hydraulique (`experiments/NorthMor/routing/`)

* **Simulation active** : `lis_hymap_opl_2018` (routage HyMAP déterministe couplé à LIS sur l'année 2018).
* **Prétraitements** : `ldt_hymap/` (paramètres physiographiques Augusto), `runoff_remap_180x120/` (remapping du ruissellement de surface et subsurfacique vers la grille HyMAP).
* **Documentation interne** : `experiments/NorthMor/routing/docs/Hymap_troubleshooting.txt`.
