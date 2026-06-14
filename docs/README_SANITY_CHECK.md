# README : Sanity Check Experiment (Noah-MP over Sebou Basin)

**Objectif :** Valider la stabilité numérique du modèle Noah-MP (v4.0.1) couplé à LIS, vérifier les chemins d'entrée/sortie (I/O) des forçages, et confirmer que les paramétrisations physiques (végétation dynamique, neige, nappe) réagissent logiquement aux forçages avant de lancer le spin-up de 14 ans.

## 1. Période de Simulation

| Paramètre | Valeur | Raison |
|-----------|--------|--------|
| Start Date | 2020-02-01 00:00:00 | Début de la période humide/neigeuse. |
| End Date | 2020-04-30 23:00:00 | Fin de la saison de fonte et pic végétatif. |
| Duration | 3 mois | Capture une transition saisonnière complète. |
| Time step | 15 ou 30 minutes | Standard pour assurer la stabilité numérique des flux d'énergie. |

## 2. Configuration du Domaine (Sebou & Saïss)

| Paramètre | Valeur |
|-----------|--------|
| Spatial Resolution | 0.05° × 0.05° (~5 km) |
| South-West Corner | 32.5° N, 7.0° W |
| North-East Corner | 35.5° N, 3.5° W |
| Soil Layers | 4 couches (0.1, 0.3, 0.6, 1.0 m) |

## 3. Forçages Météorologiques (Overlay Method)

| Variable | Source | Résolution d'origine | Traitement LIS |
|----------|--------|----------------------|----------------|
| Precipitation | GPM IMERG (Final Run v06) | 0.1° | Spatial interpolation |
| Autres champs (T, Q, SW, LW, Wind, P) | MERRA-2 | 0.50° × 0.625° | Spatial interpolation + Topographic lapse-rate correction |

## 4. Paramétrisations Physiques (Noah-MP Options)

Ces options doivent être strictement identiques à celles qui seront utilisées pour le run final et l'assimilation.

| Option Namelist | Valeur | Description |
|-----------------|--------|-------------|
| opt_run | 1 | SIMGM (Simple Groundwater Model) |
| opt_veg | 2 | Prognostic Phenology (Dynamic Vegetation ON) |
| opt_crs | 1 | Ball-Berry Stomatal Resistance |
| opt_rad | 1 | Modified Two-stream (gap fraction dynamique) |
| opt_sfc | 1 | Monin-Obukhov Similarity Theory |
| opt_alb | 1 | BATS Snow Albedo |
| opt_snf | 1 | Jordan 1991 (Rain/Snow Partition) |
| opt_tbv | 2 | Thermal diffusion equation (Bottom temperature) |
| Irrigation | OFF | Pas d'irrigation explicite dans la configuration de base |

## 5. Checklist de Validation Post-Run

Une fois le run terminé, extraire les sorties (NetCDF ou GRIB) et vérifier rapidement ces points critiques (un simple plot spatial ou une série temporelle sur un pixel suffit) :

- [ ] **SoilMoist (Couche 1)** : Augmente après un événement de précipitation IMERG et s'assèche progressivement (évaporation).
- [ ] **TVeg (Transpiration) & EVap (Evaporation)** : Suivent un cycle diurne clair (zéro la nuit, pic à midi).
- [ ] **LAI (Leaf Area Index)** : Doit varier au cours des 3 mois. S'il reste strictement figé à sa valeur initiale du 1er Février, c'est que opt_veg=2 n'est pas bien activé.
- [ ] **SnowDepth (ou SWE)** : Doit s'accumuler sur les pixels du Moyen Atlas (sud du domaine) lors des précipitations froides, et fondre en Avril. Doit rester à 0 sur la plaine du Saïss.
- [ ] **Qsb (Subsurface Runoff / Baseflow)** : Vérifier que les valeurs ne sont pas remplies de NaN (Not a Number), ce qui indiquerait un crash du module SIMGM.
- [ ] **Restart File** : Vérifier qu'un fichier de restart (ex: LIS_RST_NOAHMP401_202004302300.d01.nc) a bien été généré à la dernière heure de la simulation.
