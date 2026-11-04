# Matrice d'Expériences LIS / Noah-MP (2016–2020) — NorthMor

Ce répertoire contient la matrice expérimentale sur 5 ans (2016–2020) pour l'assimilation d'humidité du sol NASA SMAP dans Noah-MP 4.0.1 sur le domaine Nord Maroc (**NorthMor**, 180 × 120 mailles à 0.05°, 16 030 points continentaux).

---

## Organisation des Dossiers

### 1. Runs de Production (Sanctuarisés)
* **`OPL_noirr_2016_2020/`** : Simulation Open Loop déterministe (1 membre, sans assimilation, sans irrigation). Baseline de référence unperturbed 60 mois.
* **`DA_nocdf_noirr_2016_2020/`** : Assimilation SMAP brute via EnKF (20 membres, aucun scaling CDF, sans irrigation). 60 mois complets.
* **`DA_cdf_noirr_2016_2020/`** : Assimilation SMAP via EnKF (20 membres, mise à l'échelle par CDF matching NorthMor, sans irrigation). 60 mois complets.
* **`CDF/`** : Traitements LDT pour la génération des CDF modèles et observations sur NorthMor (dépendance critique de `DA_cdf_noirr`).
* **`_ARCHIVE_WRONG_CDF_DOMAIN/`** : Archive historique de la première simulation DA-CDF exécutée avec une CDF calculée par erreur sur le domaine national complet.

### 2. Sous-Dossiers Structurés
* **`tests/`** : Regroupement de toutes les expériences de sensibilité, de validation et d'audit :
  - `DA_nocdf_TEST_nowilt/` : Test d'audit de l'effet du seuil de flétrissement du QC (juillet–août 2018).
  - `DA_cdf_TEST/` : Test de validation préliminaire de la CDF NorthMor (janvier et août 2018).
  - `DA_cdf_TEST_1619/` : Test de sensibilité à la période de calcul de la CDF (janvier et août 2018).
  - `DA_repro_check_3days/` : Test de reproductibilité numérique 3 jours (juillet 2018).
  - `ENS_OPL_TEST_3days/` : Test d'ensemble OL 3 jours (non concluant).
  - `OPL_hourly_201807/` : Test diagnostique sorties horaires déterministes (juillet 2018).
* **`planned/`** : Expériences préparées, prévues ou suspendues :
  - `DA_anomaly_noirr_2016_2020/` : Assimilation SMAP par scaling d'anomalies (prévue, template à corriger).
  - `ENS_OPL_2018/` : Ensemble Open Loop 2018 (tâche suspendue).

---

## Références Détaillées
Consulter [`docs/RUNS.md`](../../../docs/RUNS.md) pour le registre complet des paramètres, membres et fichiers restarts.
