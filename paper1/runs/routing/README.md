# Configurations de Routage HyMAP-2 (linres = 0) — Papier 1

Ce dossier rassemble les configurations et scripts d'exécution Slurm utilisés pour le routage hydrodynamique HyMAP-2 (`linres = 0`) dans le cadre de la clôture du papier 1.

## 1. Configurations de Sensibilité 2018 (Bloc B)

Trois expériences de sensibilité 2018 ont été routées avec la physique HyMAP-2 linres=0 identique à la production :
- `configs/lis_hymap2_ol_daic_2018_linres0.config` (Job Slurm 8360678)
- `configs/lis_hymap2_ens_opl_2018_linres0.config` (Job Slurm 8360679)
- `configs/lis_hymap2_da_nocdf_nowilt_2018_linres0.config` (Job Slurm 8360680)

### Condition Initiale Partagée
Toutes ces simulations 2018 démarrent au **2018-01-01 00:00** à partir du fichier de restart hydrodynamique unique de `DA_nocdf` linres0 :
- Fichier : `experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc`
- Somme de contrôle MD5 : `6d00dbcfca6f3d6df2c0d4fdf756593f`
- Vérification d'état : `BSFSTO = 0.0`, `RNFSTO = 0.0` (linres = 0 strictement respecté) ; `RIVSTO_max = 7.38 × 10⁶ m³`.

## 2. Documentation du Diff des Configurations de Référence 5 ans (2016–2020)

Les configurations de référence de production linres0 préparées le 9 novembre 2026 pour `DA_nocdf` et `DA_cdf` (`experiments/NorthMor/routing/configs/lis_hymap2_da_nocdf_2016_2020_linres0.config` et `lis_hymap2_da_cdf_2016_2020_linres0.config`) contenaient initialement :
```ini
HYMAP2 routing model start mode:         restart
HYMAP2 routing model restart file:       "experiments/NorthMor/routing/output/DA_nocdf_linres0_spinup_2016/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
```
Or, le dossier `DA_nocdf_linres0_spinup_2016` n'avait jamais été exécuté et n'existait pas sur le cluster.

### Modification appliquée :
Les lignes ont été ajustées en :
```ini
HYMAP2 routing model start mode:         coldstart
HYMAP2 routing model restart file:       none
```

### Justification et comparabilité :
1. **Harmonisation avec OPL :** La simulation de référence 5 ans `OPL_linres0_2016_2020` (Job Slurm 8272794) a elle-même été démarrée en `coldstart` au 2016-01-01 00:00 (`HYMAP2 routing model start mode: coldstart`). Le passage de `DA_nocdf` et `DA_cdf` en `coldstart` garantit que les trois expériences 5 ans partagent le même protocole d'initialisation et un spinup hydrologique strictement équivalent.
2. **Absence d'écrasement :** Les répertoires de sortie `experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/` et `experiments/NorthMor/routing/output/DA_cdf_linres0_2016_2020/` étaient inexistants avant le lancement des jobs 8360645 et 8360646. Aucune sortie antérieure n'a été écrasée.

## 3. Remapping du Ruissellement 181×121 → 180×120

- Script : `paper1/scripts/remap_runoff_2018_experiments.py`
- Formule nodale validée (`routing/checks/03_remapping_ruissellement.md`) :
  $$\text{flux}_{180}[j, i] = \frac{1}{4} \left( \text{flux}_{181}[j, i] + \text{flux}_{181}[j, i+1] + \text{flux}_{181}[j+1, i] + \text{flux}_{181}[j+1, i+1] \right)$$
- Répertoires cibles créés sous `experiments/NorthMor/routing/runoff_remap_180x120/` :
  - `OL_DAIC_2018/SURFACEMODEL/` (366 fichiers)
  - `ENS_OPL_2018/SURFACEMODEL/` (366 fichiers)
  - `DA_nocdf_nowilt_2018/SURFACEMODEL/` (366 fichiers)
