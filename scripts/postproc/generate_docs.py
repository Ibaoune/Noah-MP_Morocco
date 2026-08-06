import os

DOCS_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/docs/figures"

os.makedirs(DOCS_DIR, exist_ok=True)

docs = {
    "hydrology_seasonal_impact.md": """# Documentation des figures d'hydrologie saisonnière

**Author:** M. EL Aabaribaoune (@um6p)

## 1. Description
Cette section du pipeline génère les cartes d'impact hydrologique saisonnier, comparant l'expérience Open-Loop (OL) avec les expériences d'assimilation (DA-NoCDF, DA-CDF).

## 2. Fichiers de configuration associés
- `configs/recipes/paper_manuscript_figures.yaml`
- `configs/manuscripts/hydrology_seasonal_impact.yaml`

## 3. Scripts utilisés
- **Point d'entrée principal:** `src/diagnostics/hydrology/manuscript_plots.py`
- **Module de traçage:** `src/diagnostics/hydrology/seasonal_impact_maps.py`

## 4. Données d'entrée (inputs)
- Fichiers de climatologie générés: `<name_main_dir>/climatology_nc/<name_exp>/` (ex: `matrix_2016_2020/climatology_nc/DA_NoCDF/`)
- Variables concernées: `SoilMoist_tavg`, `Evap_tavg`, `Qs_tavg`, `Qsb_tavg`, `Rainf_f_tavg`

## 5. Pipeline exact
1. Le script `manuscript_plots.py` lit les chemins relatifs depuis la configuration.
2. Si les climatologies n'existent pas, la fonction `compute_seasonal_climatologies` agrège les moyennes temporelles (DJF et JJA).
3. `seasonal_impact_maps.py` calcule les différences entre expériences (DA - OL) pour chaque variable.
4. Les masques (irrigation, test t de Student) sont appliqués pour ne garder que les signaux significatifs.
5. Les cartes sont sauvegardées dans `<name_main_dir>/figures/hydrology_seasonal_impact/`.

## 6. Sorties (outputs)
- `fig_sm_seasonal_OPL_vs_DA_NoCDF_2016_2020.png` (Humidité du sol)
- `fig_runoff_seasonal_OPL_vs_DA_NoCDF_2016_2020.png` (Ruissellement)
- `fig_precip_runoff_OPL_vs_DA_NoCDF_2016_2020.png` (Ratio précipitations/ruissellement)
""",
    
    "assimilation_diagnostics.md": """# Documentation des figures d'Assimilation

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
""",

    "independent_validation.md": """# Documentation de la Validation Indépendante

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
""",

    "domain_and_runoff_partitioning.md": """# Documentation du Domaine et Partitionnement du Ruissellement

**Author:** M. EL Aabaribaoune (@um6p)

## 1. Description
Cette section documente deux diagnostics : la représentation du domaine de modélisation physique (topographie, bassins versants) et le diagnostic de partitionnement du ruissellement (Surface Runoff / Baseflow).

## 2. Scripts utilisés
- **Domaine:** `src/diagnostics/domain/adapter.py` et `plot_domain_map.py`
- **Partitionnement:** `src/diagnostics/runoff_partitioning/adapter.py` et `plot_partitioning.py`

## 3. Données d'entrée (inputs)
- LIS param files: `lis_input.d01.nc` (Elevation, dominant soil, land cover).
- LIS HIST files: `Qs_tavg` (Surface Runoff), `Qsb_tavg` (Baseflow).

## 4. Pipeline exact
- **Domaine**: Extraction des variables 2D statiques depuis le fichier de paramètres géographiques et tracé cartographique.
- **Partitionnement**: Rapport entre ruissellement de surface et ruissellement total (`Qs / (Qs + Qsb)`). Le ratio est cartographié pour mettre en évidence les zones de percolation vs écoulement de surface.

## 5. Sorties (outputs)
- `domain_topography.png`
- `domain_landcover.png`
- Cartes de ratio Qs/Q_total dans `figures/<name_exp>/runoff_partitioning/`
"""
}

for filename, content in docs.items():
    filepath = os.path.join(DOCS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(content)
        
print("Documentation generated.")
