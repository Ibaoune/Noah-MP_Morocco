# Documentation de la Validation Indépendante

**Author:** M. EL Aabaribaoune (@um6p)

## 1. Description
Évaluation croisée des sorties LIS par rapport aux jeux de données satellitaires de référence (GLEAM, WaPOR, FLUXSAT, SMAP, ESA-CCI).

## 2. Fichiers de configuration associés
- `configs/recipes/smap_cdf_independent_validation_2016_2020.yaml`
- `configs/observations/*.yaml`

## 3. Scripts utilisés
- **Point d'entrée principal:** `src/diagnostics/independent_ob_validation/adapter.py`
- **Modules de calcul:** `lsm_benchmark.py`, `spatial_alignment.py`, `statistical_summary.py`

## 4. Données d'entrée (inputs)
- Fichiers LIS HIST: `experiments/NorthMor/<name_main_dir>/<exp>/SURFACEMODEL/`
- Datasets observationnels: Répertoires externes définis dans `configs/observations/`

## 5. Pipeline exact
1. Chargement de la grille LIS cible.
2. Pour chaque dataset observationnel, `spatial_alignment.py` fait une projection conservative (bincount Zéro-RAM) sur la grille modèle.
3. Alignement temporel (moyennes mensuelles) pour correspondre au pas de temps.
4. Calcul des métriques statistiques pixel par pixel (R, RMSD, ubRMSD, Biais) dans `statistical_summary.py`.
5. Sauvegarde des tableaux dans `<name_main_dir>/tables/<name_exp>/`.
6. Tracé des métriques et des différences DA vs OL.

## 6. Sorties (outputs)
- Tableaux CSV: `independent_validation_results_2016_2020.txt`
- Figures: Cartes de corrélations et RMSD dans `<name_main_dir>/figures/<name_exp>/independent_obs_validation/`
