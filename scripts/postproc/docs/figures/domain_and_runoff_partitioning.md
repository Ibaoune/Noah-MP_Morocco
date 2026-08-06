# Documentation du Domaine et Partitionnement du Ruissellement

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
