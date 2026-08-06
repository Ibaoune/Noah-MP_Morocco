# Documentation des figures d'Assimilation

**Author:** M. EL Aabaribaoune (@um6p)

## 1. Description
Cette section du pipeline génère les diagnostics internes du filtre de Kalman (EnKF) pour évaluer la qualité de l'assimilation des données SMAP.

## 2. Fichiers de configuration associés
- `configs/recipes/smap_cdf_sensitivity_2016_2020.yaml` (section `assimilation`)

## 3. Scripts utilisés
- **Point d'entrée principal:** `src/diagnostics/assimilation/adapter.py`
- **Modules de calcul:** 
  - `diag_innovations.py` (Innovations & Incréments spatiaux)
  - `diag_seasonal_increments.py` (Incréments saisonniers)
  - `diag_coverage.py` (Fréquence d'assimilation)
  - `diag_spread.py` (Incertitude d'ensemble)

## 4. Données d'entrée (inputs)
- Fichiers LIS DA bruts: `experiments/NorthMor/<name_main_dir>/<DA_exp>/EnKF/`
- Fichiers ciblés: `*_innov.a01.d01.nc`, `*_incr.a01.d01.nc`

## 5. Pipeline exact
1. Le script `adapter.py` lit la configuration et boucle sur les expériences DA (ex: `DA_NoCDF`).
2. `diag_innovations.py` boucle sur chaque mois, ouvre chaque fichier d'innovation et cumule spatialement les valeurs (innovation = Obs - Forecast).
3. Le résultat est moyenné par pixel et tracé avec une colormap divergente.
4. Les paramètres géographiques et les échelles de couleur sont standardisés.
5. Les cartes sont sauvegardées dans `<name_main_dir>/figures/<name_exp>/assimilation/<DA_exp>/`.

## 6. Sorties (outputs)
- `DA_NoCDF_innovation_map.png`
- `DA_NoCDF_increment_map.png`
- `DA_NoCDF_obs_count.png`
- `DA_NoCDF_spread_consistency.png`
