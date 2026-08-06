# Documentation des figures d'hydrologie saisonnière

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
