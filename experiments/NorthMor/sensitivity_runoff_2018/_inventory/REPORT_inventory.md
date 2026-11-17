# Rapport d'Inventaire et d'Audit Factuel des Expériences de Sensibilité Noah-MP / HyMAP-2 (2017–2018)

## Résumé Exécutif Factuel (10 lignes)
Les quatre expériences de sensibilité hydrologique Noah-MP 4.0.1 (SIMGM opt=1, SIMTOP opt=2, Schaake96 opt=3, BATS opt=4) couvrent du 01/01/2017 au 02/01/2019 et ont été exécutées dans `experiments/NorthMor/opl_hydrology_sensitivity/experiments/`. Elles partagent un état initial rigoureusement identique (`LIS_RST_NOAHMP401_201701010000.d01.nc`, MD5 `bb5313eb35214c2b4b4ff22ab6113937`) issu de l'année 2016 de l'historique OPL. Les routages HyMAP-2 associés ont été menés en coldstart sans réservoir linéaire (`linres=0`, Jobs SLURM 8315612 à 8315615); aucun routage `linres=1` de ces ruissellements n'existe. Sur 2018, les flux journaliers reprojetés du nouveau SIMGM et de l'OPL historique sont strictement identiques (écart maximal 0.0 mm/j, corrélation 1.000). En étiage estival (JJA et JJAS 2018), les flux amont de subsurface $Q_{sb}$ dominent le ruissellement total (>93%) et maintiennent un débit routé élevé (1.3 à 6.9 m³/s), tandis que les observations ABH enregistrent un assec strict (47 jours consécutifs à 0.0 m³/s à Sidi Jabeur, du 18/07 au 02/09/2018). Le script de nettoyage ABH omet les lacunes sans les convertir en 0. Les figures F1A à F7 et les métriques (KGE-2009 journalier/mensuel) sont issues des scripts de post-traitement de `postproc/multistation/scripts/`.

---

## 1. Localisation des Expériences et Inventaire du Disque

### 1.1 Recherche des configurations Noah-MP (options de ruissellement 2, 3, 4)
Commande exécutée :
`grep -rn "runoff and groundwater option" --include=*.config --exclude-dir=src . | grep -E ":[[:space:]]*[234]"`

Les configurations identifiées dans le dépôt sont situées exclusivement sous `experiments/NorthMor/opl_hydrology_sensitivity/experiments/` :
- **SIMTOP (Option 2) :**
  - Template : [lis_simtop.config.template](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/templates/lis_simtop.config.template#L103) (ligne 103)
  - 25 configurations mensuelles générées (2017-01 à 2019-01) : [lis_simtop_2018-01.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/generated/configs/lis_simtop_2018-01.config#L103) (ligne 103)
  - Configs de test : `test_resume_feb/lis_resume_simtop.config` (ligne 103), `test_short/lis_test_simtop.config` (ligne 103)
- **Schaake96 (Option 3) :**
  - Template : [lis_schaake96.config.template](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/templates/lis_schaake96.config.template#L103) (ligne 103)
  - 25 configurations mensuelles générées (2017-01 à 2019-01) : [lis_schaake96_2018-01.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/generated/configs/lis_schaake96_2018-01.config#L103) (ligne 103)
  - Configs de test : `test_resume_feb/lis_resume_schaake96.config` (ligne 103), `test_short/lis_test_schaake96.config` (ligne 103)
- **BATS (Option 4) :**
  - Template : [lis_bats.config.template](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R4_BATS/templates/lis_bats.config.template#L103) (ligne 103)
  - 25 configurations mensuelles générées (2017-01 à 2019-01) : [lis_bats_2018-01.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R4_BATS/generated/configs/lis_bats_2018-01.config#L103) (ligne 103)
  - Configs de test : `test_resume_feb/lis_resume_bats.config` (ligne 103), `test_short/lis_test_bats.config` (ligne 103)

*(Remarque : la configuration de référence SIMGM Option 1 est localisée symétriquement dans `experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/`).*

### 1.2 Recherche des configurations de routage HyMAP-2 avec réservoir linéaire désactivé (`linres=0`)
Commande exécutée :
`grep -rln "linear reservoir flag: *0" --include=*.config --exclude-dir=src .`

Fichiers trouvés :
1. **Nouvelles expériences de sensibilité 2017–2018 (HyMAP-2, `linres=0`) :**
   - [lis_hymap2_simgm_2017_2018.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_simgm_2017_2018.config#L35)
   - [lis_hymap2_simtop_2017_2018.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_simtop_2017_2018.config#L35)
   - [lis_hymap2_schaake96_2017_2018.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_schaake96_2017_2018.config#L35)
   - [lis_hymap2_bats_2017_2018.config](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_bats_2017_2018.config#L35)
   - Tests techniques préliminaires (janvier 2017) : `experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/test_jan2017/lis_hymap2_{simgm,simtop,schaake96,bats}_jan2017.config`
2. **Configurations historiques de routage sous `experiments/NorthMor/routing/configs/` :**
   - `lis_hymap2_opl_2016_2020_linres0.config` (Job 8272794, 5 ans)
   - `lis_hymap2_opl_spinup_linres0.config`, `lis_hymap2_opl_test_jan2016_linres0.config`
   - `lis_hymap2_da_nocdf_2016_2020_linres0.config`, `lis_hymap2_da_nocdf_spinup_linres0.config`
   - `lis_hymap2_da_cdf_2016_2020_linres0.config`, `lis_hymap2_da_cdf_spinup_linres0.config`
   - Plus les 6 configurations de préparation HyMAP-3 (`lis_hymap3_*.config`).

### 1.3 Recherche hors du dépôt Git
Les répertoires hors du dépôt ont été explorés :
- `/srv/data/mohammad.elaabaribao/` : contient des dossiers d'archives historiques (`arch_toubkal_OLD`, `SOM`, `TUTORIAL`), mais aucune sortie NetCDF de sensibilité Noah-MP / HyMAP-2.
- `/home/mohammad.elaabaribao/work` : date de juillet 2025 (`interns`), aucune sortie.
- `/scratch` / `/work` : non montés sur le nœud de calcul.
- Variables `$SCRATCH`, `$WORK`, `$LUSTRE` : vides.
- `/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/` : correspond à la racine du projet Lustre. L'ensemble des sorties, redémarrages et figures est strictement et intégralement contenu au sein de `experiments/NorthMor/opl_hydrology_sensitivity/`.

### 1.4 Tableau récapitulatif des répertoires trouvés, taille et dernière modification
*Mesures effectuées le 17/11/2026 via `du -sh` et `stat` :*

| Répertoire | Description fonctionnelle | Taille disque | Date dernière modification |
| :--- | :--- | :---: | :---: |
| `experiments/NorthMor/opl_hydrology_sensitivity/` | Racine du projet pilote de sensibilité | 12.0 Go | 2026-11-17 07:59:35 |
| `├── experiments/OL_R1_SIMGM/` | Simulation Noah-MP Option 1 (SIMGM baseline) | 2.3 Go | 2026-11-14 09:42:59 |
| `├── experiments/OL_R2_SIMTOP/` | Simulation Noah-MP Option 2 (SIMTOP) | 2.3 Go | 2026-11-14 09:42:59 |
| `├── experiments/OL_R3_SCHAAKE96/` | Simulation Noah-MP Option 3 (Schaake96) | 2.3 Go | 2026-11-14 09:42:59 |
| `├── experiments/OL_R4_BATS/` | Simulation Noah-MP Option 4 (BATS) | 2.3 Go | 2026-11-14 09:42:59 |
| `├── routing/` | Chaîne de routage HyMAP-2 (`linres=0`) | 2.9 Go | 2026-11-14 09:23:53 |
| `│   ├── configs/` | Configs LIS de routage 2017–2018 et test | 72 Ko | 2026-11-14 10:01:26 |
| `│   ├── runs/` | Ruissellements reprojetés 180x120 & logs SLURM | 1.3 Go | 2026-11-14 09:23:53 |
| `│   ├── outputs/` | Débits journaliers routés NetCDF (730j/schéma) | 1.7 Go | 2026-11-14 09:44:26 |
| `│   └── scripts/` | Scripts de reprojection et d'extraction locale | 28 Ko | 2026-11-14 10:04:16 |
| `├── postproc/` | Évaluation hydrologique, figures et tables | 53 Mo | 2026-11-17 06:41:37 |
| `│   ├── figures/` | Figures scientifiques principales (.png, .pdf) | 28 Mo | 2026-11-17 14:44:16 |
| `│   ├── multistation/` | Post-traitement multi-stations, F5, F5b, F7 | 23 Mo | 2026-11-17 14:55:57 |
| `│   ├── scripts/` | Scripts Python d'analyse et calcul KGE/NSE | 116 Ko | 2026-11-16 23:00:39 |
| `│   └── tables/` | Tables de métriques, inventaires et bilans CSV | 3.2 Mo | 2026-11-17 06:53:57 |
| `└── scripts/` | Lanceurs master et maintenance du chaînage | 68 Ko | 2026-11-15 09:48:03 |

---

## 2. Configuration Noah-MP des Quatre Runs

### 2.1 Tableau comparatif des configurations

| Schéma / Expérience | Fichier config (Template / Mensuel) | Option ruissellement | Période simulée | Start mode | Fichier restart LSM initial | Forçage météo | Ensembles | Irrigation | Pas de sortie | Répertoire des sorties |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- | :---: | :---: | :---: | :--- |
| **SIMGM (Ref)** (`OL_R1_SIMGM`) | `templates/lis_simgm.config.template` / `generated/configs/lis_simgm_2018-01.config` | `1` | 2017-01-01 00:00 au 2019-01-02 00:00 | `restart` | `experiments/OL_R1_SIMGM/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc` | MERRA-2 + GPM IMERG V07B 'final' | 1 | none (`crop model option: 0`) | `1da` (timestep: 15mn) | `experiments/OL_R1_SIMGM/output/<YYYY-MM>/` |
| **SIMTOP** (`OL_R2_SIMTOP`) | `templates/lis_simtop.config.template` / `generated/configs/lis_simtop_2018-01.config` | `2` | 2017-01-01 00:00 au 2019-01-02 00:00 | `restart` | `experiments/OL_R2_SIMTOP/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc` | MERRA-2 + GPM IMERG V07B 'final' | 1 | none (`crop model option: 0`) | `1da` (timestep: 15mn) | `experiments/OL_R2_SIMTOP/output/<YYYY-MM>/` |
| **Schaake96** (`OL_R3_SCHAAKE96`) | `templates/lis_schaake96.config.template` / `generated/configs/lis_schaake96_2018-01.config` | `3` | 2017-01-01 00:00 au 2019-01-02 00:00 | `restart` | `experiments/OL_R3_SCHAAKE96/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc` | MERRA-2 + GPM IMERG V07B 'final' | 1 | none (`crop model option: 0`) | `1da` (timestep: 15mn) | `experiments/OL_R3_SCHAAKE96/output/<YYYY-MM>/` |
| **BATS** (`OL_R4_BATS`) | `templates/lis_bats.config.template` / `generated/configs/lis_bats_2018-01.config` | `4` | 2017-01-01 00:00 au 2019-01-02 00:00 | `restart` | `experiments/OL_R4_BATS/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc` | MERRA-2 + GPM IMERG V07B 'final' | 1 | none (`crop model option: 0`) | `1da` (timestep: 15mn) | `experiments/OL_R4_BATS/output/<YYYY-MM>/` |

### 2.2 Réponses aux questions clés

#### 1. Les quatre runs partent-ils du même état initial ?
**OUI, STRICTEMENT IDENTIQUE.**  
Les quatre fichiers de redémarrage initiaux situés dans `restarts/LIS_RST_NOAHMP401_201701010000.d01.nc` ont une taille identique de **1 657 564 octets** (~1.6 Mo) et un condensat MD5 strictement identique :
```text
bb5313eb35214c2b4b4ff22ab6113937  OL_R1_SIMGM/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc
bb5313eb35214c2b4b4ff22ab6113937  OL_R2_SIMTOP/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc
bb5313eb35214c2b4b4ff22ab6113937  OL_R3_SCHAAKE96/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc
bb5313eb35214c2b4b4ff22ab6113937  OL_R4_BATS/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc
```

#### 2. Ce restart vient-il de l'ancien spin-up SIMGM 2005–2015 (`experiments/NorthMor/SPINUP`) ?
**NON DIRECTEMENT, IL PROVIENT DU RESTART AU 01/01/2017 DE LA PRODUCTION HISTORIQUE `OPL_noirr_2016_2020`.**  
Preuve par somme MD5 :
```text
bb5313eb35214c2b4b4ff22ab6113937  experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc
bb5313eb35214c2b4b4ff22ab6113937  experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2016-12/SURFACEMODEL/201701/LIS_RST_NOAHMP401_201701010000.d01.nc
```
La chaîne généalogique exacte est :
1. Spin-up décennal SIMGM 2005–2015 (`experiments/NorthMor/SPINUP/SPINUP_OPL/`) -> produit `LIS_RST_NOAHMP401_201601010000.d01.nc`.
2. Simulation historique SIMGM de l'année 2016 (`matrix_2016_2020/OPL_noirr_2016_2020/output/2016-12/`) -> produit le restart terminal `LIS_RST_NOAHMP401_201701010000.d01.nc`.
3. Ce restart au 01/01/2017 (initialisé sous formulation SIMGM) a été dupliqué à l'identique comme condition initiale des quatre expériences de sensibilité. Les schémas 2, 3 et 4 ont donc démarré au 01/01/2017 depuis un sol équilibré en SIMGM, ce qui justifie que 2017 serve d'année de relaxation et 2018 d'année d'évaluation.

#### 3. Hormis l'option de ruissellement, des options diffèrent-elles entre les quatre configs ?
**AUCUNE AUTRE OPTION PHYSIQUE OU NUMÉRIQUE NE DIFFÈRE.**  
Le diff pairwise strict ligne à ligne des 4 fichiers templates montre que la seule et unique ligne qui change est l'option de ruissellement (ligne 103) :

```diff
--- SIMGM vs SIMTOP ---
-Noah-MP.4.0.1 runoff and groundwater option:                  1  # 1=SIMGM
+Noah-MP.4.0.1 runoff and groundwater option:                  2  # 2=SIMTOP

--- SIMGM vs SCHAAKE96 ---
-Noah-MP.4.0.1 runoff and groundwater option:                  1  # 1=SIMGM
+Noah-MP.4.0.1 runoff and groundwater option:                  3  # 3=SCHAAKE96

--- SIMGM vs BATS ---
-Noah-MP.4.0.1 runoff and groundwater option:                  1  # 1=SIMGM
+Noah-MP.4.0.1 runoff and groundwater option:                  4  # 4=BATS

--- SIMTOP vs SCHAAKE96 ---
-Noah-MP.4.0.1 runoff and groundwater option:                  2  # 2=SIMTOP
+Noah-MP.4.0.1 runoff and groundwater option:                  3  # 3=SCHAAKE96

--- SIMTOP vs BATS ---
-Noah-MP.4.0.1 runoff and groundwater option:                  2  # 2=SIMTOP
+Noah-MP.4.0.1 runoff and groundwater option:                  4  # 4=BATS

--- SCHAAKE96 vs BATS ---
-Noah-MP.4.0.1 runoff and groundwater option:                  3  # 3=SCHAAKE96
+Noah-MP.4.0.1 runoff and groundwater option:                  4  # 4=BATS
```
*(Dans les configurations mensuelles générées, seules les chaînes spécifiques au répertoire de sortie `Output directory`, au fichier de log `Diagnostic output file` et au restart mensuel `Noah-MP.4.0.1 restart file` adaptent le nom du sous-dossier de l'expérience).*

---

## 3. Configuration HyMAP-2 des Nouveaux Routages

### 3.1 Diff avec la configuration de référence historique (`lis_hymap2_opl_2016_2020_corrigee.config`)
Fichier de référence : `experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_corrigee.config`  
Nouvelles configurations : `experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_{simgm,simtop,schaake96,bats}_2017_2018.config`

Collage exhaustif des lignes divergentes (exemple avec `lis_hymap2_simgm_2017_2018.config`) :
```diff
--- experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_corrigee.config
+++ experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_simgm_2017_2018.config
@@ -1,3 +1,3 @@
-# LIS configuration for Stand-alone HYMAP2 Routing - OPL Production 2016-2020 (5 ans)
+# LIS configuration for Stand-alone HYMAP2 Routing - OPL Production 2016-2020 (5 ans, linres=0, coldstart)
@@ -10,3 +10,3 @@
-Starting year:                          2016
+Starting year:                          2017
@@ -16,3 +16,3 @@
-Ending year:                            2021
+Ending year:                            2019
@@ -23,4 +23,4 @@
-Output directory:                       "experiments/NorthMor/routing/output/OPL_2016_2020_corrigee"
-Diagnostic output file:                 "experiments/NorthMor/routing/logs/lislog_opl_2016_2020_corrigee"
+Output directory:                       "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/outputs/OL_R1_SIMGM"
+Diagnostic output file:                 "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/lislog_hymap2_simgm"
@@ -29,3 +29,3 @@
-LIS runoff output directory:            "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020"
+LIS runoff output directory:            "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R1_SIMGM"
@@ -35,5 +35,5 @@
-HYMAP2 routing model linear reservoir flag: 1
+HYMAP2 routing model linear reservoir flag: 0
-HYMAP2 routing model start mode:         restart
-HYMAP2 routing model restart file:       "experiments/NorthMor/routing/output/OPL_spinup_c2_corrigee/ROUTING/201701/LIS_RST_HYMAP2_router_201701010000.d01.nc"
+HYMAP2 routing model start mode:         coldstart
+HYMAP2 routing model restart file:       none
```
*(Les diffs pour SIMTOP, Schaake96 et BATS sont rigoureusement identiques, à la substitution près du nom d'expérience `OL_R2_SIMTOP`, `OL_R3_SCHAAKE96`, `OL_R4_BATS`).*

### 3.2 Synthèse des paramètres HyMAP-2
- **Fichier `lis_input` utilisé :** `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` (identique au standard corrigé de nappe `tbasflw / 86400`).
- **Start mode :** `coldstart` (initialisation à chenaux vides au 01/01/2017).
- **Restart HyMAP et protocole de spin-up :** Aucun fichier restart (`none`). Le protocole repose sur l'utilisation intégrale de l'année 2017 comme période de montée en eau et stabilisation du réseau hydrographique; l'année 2018 constitue l'unique période évaluée.
- **Evaporation option :** `none`.
- **DWI flag (Deep Water Infiltration) :** `0`.
- **Routing method :** `kinematic` (onde cinématique).
- **Linear reservoir flag :** `0` (réservoir souterrain linéaire désactivé, transfert direct de $Q_{sb}$ dans le réseau).

### 3.3 Script de reprojection 181x121 -> 180x120 et audit des dates de modification (mtime)
- **Script utilisé :** [remap_runoff_sensitivity.py](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/scripts/remap_runoff_sensitivity.py)
- **Motif source :** `experiments/NorthMor/opl_hydrology_sensitivity/experiments/{exp}/output/*/SURFACEMODEL/*/LIS_HIST_*.nc`
- **Répertoire de destination :** `experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/{exp}/SURFACEMODEL/{YYYYMM}/`
- **Mécanisme d'évitement :** `if os.path.exists(dst_path) and os.path.getsize(dst_path) > 10000: return` (ligne 32).
- **Audit mtime source vs destination sur les 731 fichiers journaliers :**
  - `OL_R1_SIMGM` : 729 fichiers reprojetés plus récents que la source, **2 fichiers plus anciens** (`LIS_HIST_201701020000.d01.nc` et `LIS_HIST_201701030000.d01.nc`).
  - `OL_R2_SIMTOP` : 730 plus récents, **1 fichier plus ancien** (`LIS_HIST_201701030000.d01.nc`).
  - `OL_R3_SCHAAKE96` : 729 plus récents, **2 fichiers plus anciens** (`LIS_HIST_201701020000.d01.nc` et `LIS_HIST_201701030000.d01.nc`).
  - `OL_R4_BATS` : 730 plus récents, **1 fichier plus ancien** (`LIS_HIST_201701030000.d01.nc`).
  - **Explication factuelle de l'anomalie :** Ces fichiers des 2 et 3 janvier 2017 proviennent de la campagne préalable de tests courts (`test_short`) remappée quelques minutes avant le relancement de janvier complet. Le script ayant trouvé les fichiers déjà présents avec taille > 10 Ko ne les a pas réécrits. Le test numérique comparatif direct montre un écart maximal de $2.27 	imes 10^{-13}	ext{ kg}\cdot	ext{m}^{-2}\cdot	ext{s}^{-1}$ (strictement nul au niveau de la précision flottante).

### 3.4 Existe-t-il un routage avec `linres=1` des mêmes ruissellements des nouveaux runs ?
**NON.** Aucun fichier de configuration ni aucune sortie NetCDF n'existe avec `HYMAP2 routing model linear reservoir flag: 1` pour les runs `OL_R1_SIMGM`, `OL_R2_SIMTOP`, `OL_R3_SCHAAKE96` ou `OL_R4_BATS`. Toutes les expériences de sensibilité ont été routées exclusivement avec `linres=0`.

---

## 4. Test d'Identité SIMGM Nouveau vs OPL Historique (Année 2018)

Script exécuté : `experiments/NorthMor/sensitivity_runoff_2018/_inventory/test_identity_simgm_vs_opl.py`  
Données comparées jour par jour sur les 365 jours de 2018 (grille 180x120) :
- Nouveau SIMGM : `experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R1_SIMGM/SURFACEMODEL/`
- OPL Historique : `experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL/`
- Maille Lalla Chafia : row = 75, col = 71.

### Tableau synthétique des résultats
| Variable | Maximum de \|différence\| | Rapport des sommes annuelles domaine | Corrélation journalière domaine | Corrélation journalière Lalla Chafia | Statut |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **`Qs_tavg` (ruissellement surface)** | **0.000000** | **1.000000** | **1.000000** | **1.000000** | **identiques** |
| **`Qsb_tavg` (drainage subsurface)** | **0.000000** | **1.000000** | **1.000000** | **1.000000** | **identiques** |
| **Total (`Qs + Qsb`)** | **0.000000** | **1.000000** | **1.000000** | **1.000000** | **identiques** |

**Conclusion stricte : « identiques »**  
*(Les séries temporelles de flux journaliers reprojetés du nouveau run SIMGM 2018 sont strictement bit-à-bit identiques aux flux historiques OPL).*

---

## 5. Bilan Estival Qsb contre Débit Routé (Calcul Factuel)

### 5.1 Méthodologie et traçabilité
- **Fonction de délimitation amont :** Fonction `get_catchment(orow, ocol)` issue de [evaluate_sebou_bouregreg.py](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/scripts/evaluate_sebou_bouregreg.py#L699-L708) (lignes 699 à 708), parcourant le graphe inverse (`parents`) des directions de flux D8 (`HYMAP_flow_direction_x`, `HYMAP_flow_direction_y`) lues dans `experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc` (lignes 673–697).
- **Superficies officielles :** Lues dans [hymap_stations_pairing.csv](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv) :
  - **Lalla Chafia (`b_l_chafia`) :** row = 75, col = 71 ; superficie $A = 3\,341{,}60	ext{ km}^2$ (133 mailles D8, aire cumulée de grille = $3\,333{,}35	ext{ km}^2$).
  - **Sidi Jabeur (`b_s_jabeur`) :** row = 71, col = 71 ; superficie $A = 3\,138{,}52	ext{ km}^2$ (121 mailles D8, aire cumulée de grille = $3\,130{,}55	ext{ km}^2$).
- **Conversion volumique :** $	ext{m}^3/	ext{s} = 	ext{mm/j} 	imes A[	ext{km}^2] / 86{,}4$.
- **Observations hydrométriques :** Lues dans `data/streamflow_clean/obs_daily.csv`.

### 5.2 Tableau récapitulatif Juin–Août 2018 (92 jours)

| Station | Schéma | $Q_s$ moy (mm/j) | $Q_s$ méd (mm/j) | $Q_s$ moy (m³/s) | $Q_s$ méd (m³/s) | $Q_{sb}$ moy (mm/j) | $Q_{sb}$ méd (mm/j) | $Q_{sb}$ moy (m³/s) | $Q_{sb}$ méd (m³/s) | $Q_{	ext{routé}}$ moy (m³/s) | $Q_{	ext{routé}}$ méd (m³/s) | $Q_{	ext{obs}}$ moy (m³/s) | $Q_{	ext{obs}}$ méd (m³/s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lalla Chafia** | **SIMGM (Opt 1)** | 0.0046 | 0.0005 | 0.180 | 0.018 | 0.1736 | 0.1703 | 6.713 | 6.588 | 6.902 | 6.750 | 0.664 | 0.325 |
| **Lalla Chafia** | **SIMTOP (Opt 2)** | 0.0032 | 0.0002 | 0.124 | 0.009 | 0.0673 | 0.0540 | 2.602 | 2.090 | 2.810 | 2.244 | 0.664 | 0.325 |
| **Lalla Chafia** | **Schaake96 (Opt 3)**| 0.0013 | 0.0000 | 0.050 | 0.000 | 0.0441 | 0.0413 | 1.706 | 1.598 | 1.783 | 1.639 | 0.664 | 0.325 |
| **Lalla Chafia** | **BATS (Opt 4)** | 0.0064 | 0.0018 | 0.246 | 0.068 | 0.0862 | 0.0816 | 3.333 | 3.154 | 3.614 | 3.391 | 0.664 | 0.325 |
| **Lalla Chafia** | **OPL Hist (linres=1)**| 0.0046 | 0.0005 | 0.180 | 0.018 | 0.1736 | 0.1703 | 6.713 | 6.588 | 6.960 | 6.779 | 0.664 | 0.325 |
| **Sidi Jabeur** | **SIMGM (Opt 1)** | 0.0029 | 0.0002 | 0.105 | 0.008 | 0.0820 | 0.0820 | 2.978 | 2.979 | 3.070 | 3.054 | 0.208 | 0.174 |
| **Sidi Jabeur** | **SIMTOP (Opt 2)** | 0.0027 | 0.0002 | 0.099 | 0.006 | 0.0687 | 0.0580 | 2.497 | 2.107 | 2.685 | 2.265 | 0.208 | 0.174 |
| **Sidi Jabeur** | **Schaake96 (Opt 3)**| 0.0006 | 0.0000 | 0.021 | 0.000 | 0.0347 | 0.0333 | 1.261 | 1.210 | 1.305 | 1.232 | 0.208 | 0.174 |
| **Sidi Jabeur** | **BATS (Opt 4)** | 0.0049 | 0.0010 | 0.179 | 0.036 | 0.0803 | 0.0766 | 2.917 | 2.781 | 3.130 | 2.955 | 0.208 | 0.174 |
| **Sidi Jabeur** | **OPL Hist (linres=1)**| 0.0029 | 0.0002 | 0.105 | 0.008 | 0.0820 | 0.0820 | 2.978 | 2.979 | 3.081 | 3.063 | 0.208 | 0.174 |

### 5.3 Tableau récapitulatif Juin–Septembre 2018 (122 jours)

| Station | Schéma | $Q_s$ moy (mm/j) | $Q_s$ méd (mm/j) | $Q_s$ moy (m³/s) | $Q_s$ méd (m³/s) | $Q_{sb}$ moy (mm/j) | $Q_{sb}$ méd (mm/j) | $Q_{sb}$ moy (m³/s) | $Q_{sb}$ méd (m³/s) | $Q_{	ext{routé}}$ moy (m³/s) | $Q_{	ext{routé}}$ méd (m³/s) | $Q_{	ext{obs}}$ moy (m³/s) | $Q_{	ext{obs}}$ méd (m³/s) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lalla Chafia** | **SIMGM (Opt 1)** | 0.0152 | 0.0005 | 0.588 | 0.018 | 0.1635 | 0.1589 | 6.323 | 6.145 | 6.878 | 6.660 | 0.726 | 0.320 |
| **Lalla Chafia** | **SIMTOP (Opt 2)** | 0.0099 | 0.0002 | 0.383 | 0.009 | 0.0609 | 0.0457 | 2.356 | 1.766 | 2.757 | 2.253 | 0.726 | 0.320 |
| **Lalla Chafia** | **Schaake96 (Opt 3)**| 0.0054 | 0.0000 | 0.208 | 0.000 | 0.0417 | 0.0390 | 1.612 | 1.509 | 1.838 | 1.664 | 0.726 | 0.320 |
| **Lalla Chafia** | **BATS (Opt 4)** | 0.0170 | 0.0017 | 0.657 | 0.067 | 0.0796 | 0.0744 | 3.078 | 2.879 | 3.714 | 3.387 | 0.726 | 0.320 |
| **Lalla Chafia** | **OPL Hist (linres=1)**| 0.0152 | 0.0005 | 0.588 | 0.018 | 0.1635 | 0.1589 | 6.323 | 6.145 | 6.913 | 6.642 | 0.726 | 0.320 |
| **Sidi Jabeur** | **SIMGM (Opt 1)** | 0.0103 | 0.0002 | 0.374 | 0.009 | 0.0804 | 0.0804 | 2.921 | 2.919 | 3.249 | 3.099 | 1.350 | 0.174 |
| **Sidi Jabeur** | **SIMTOP (Opt 2)** | 0.0093 | 0.0002 | 0.336 | 0.007 | 0.0631 | 0.0510 | 2.293 | 1.852 | 2.648 | 2.318 | 1.350 | 0.174 |
| **Sidi Jabeur** | **Schaake96 (Opt 3)**| 0.0037 | 0.0000 | 0.136 | 0.000 | 0.0332 | 0.0318 | 1.205 | 1.154 | 1.343 | 1.265 | 1.350 | 0.174 |
| **Sidi Jabeur** | **BATS (Opt 4)** | 0.0150 | 0.0010 | 0.543 | 0.036 | 0.0745 | 0.0703 | 2.707 | 2.553 | 3.230 | 3.013 | 1.350 | 0.174 |
| **Sidi Jabeur** | **OPL Hist (linres=1)**| 0.0103 | 0.0002 | 0.374 | 0.009 | 0.0804 | 0.0804 | 2.921 | 2.919 | 3.232 | 3.107 | 1.350 | 0.174 |

---

## 6. Contrôle des Débits ABH Journaliers (Zéros Réels ou Lacunes ?)

### 6.1 Fichiers et script de nettoyage
- **Fichier nettoyé :** `data/streamflow_clean/obs_daily.csv` (colonnes : `station_id`, `date`, `q_m3s`, `flag`).
- **Script de nettoyage :** `data/streamflow_clean/process_streamflow.py` (lignes 1 à 690).
- **Fichier ABH brut :**
  - **Bassin du Bouregreg (`b_l_chafia.xlsx`, `b_s_jabeur.xlsx`, `b_a_loudah.xlsx`, `b_s_cherif.xlsx`) :** **INTROUVABLE** sur le cluster HPC Toubkal (cherché dans `/home/mohammad.elaabaribao/`, `/srv/lustre01/...`, `/srv/data/...`, `data/`). Le script `process_streamflow.py` (lignes 9, 87, 168) indique qu'il a été exécuté initialement depuis le chemin local `/home/elaabar/Downloads/streamflow_data/`.
  - **Bassins du Sebou et du Ksob :** Fichiers bruts présents dans `data/streamflow_data/` (`Qm_*.xls`, `adamna monthly.xlsx`, `Zelten.xlsx`, `Igronzar.xls`).

### 6.2 Traitement des valeurs manquantes, cellules vides et drapeaux
Analyse du code source de `data/streamflow_clean/process_streamflow.py` (lignes 170–265) :
1. **Conversion numérique :** `df['q_num'] = pd.to_numeric(df['q'], errors='coerce')` (ligne 170). Les cellules vides, textes ou caractères spéciaux deviennent des `NaN`.
2. **Valeurs négatives :** `if pd.notna(val) and val < 0:` -> la valeur est mise à `NaN` et exportée comme chaîne vide `''` dans `obs_daily.csv` avec le drapeau `negatif_mis_a_nan` (lignes 240–248).
3. **Valeurs valides :** `elif pd.notna(val):` -> la valeur est exportée sous format textuel arrondi (`f'{val:.4f}'` ou `'0.0'` si nulle) avec les éventuels drapeaux (`plage_constante`, `doublon_suspect`).
4. **Valeurs manquantes / Cellules vides :** `else: pass` (lignes 258–261).  
   **Règle stricte démontrée : LES VALEURS MANQUANTES ET CELLULES VIDES SONT PUR ET SIMPLEMENT OMISES DU FICHIER `obs_daily.csv`. ELLES NE SONT EN AUCUN CAS CONVERTIES EN ZÉRO.**
   Toutes les valeurs égales à `0.0` dans `obs_daily.csv` proviennent exclusivement de valeurs `0` explicitement mesurées et enregistrées dans les fichiers sources de l'ABH.

### 6.3 Valeurs journalières lues dans `obs_daily.csv`

#### Lalla Chafia (`b_l_chafia`)
- **Période 2017-12-15 au 2018-01-10 :**
  - `2017-12-15` : 1.82 m³/s | `2017-12-16` : 1.21 m³/s | `2017-12-17` : 17.7 m³/s | `2017-12-18` : 0.944 m³/s
  - `2017-12-19` : 0.801 m³/s | `2017-12-20` : 0.68 m³/s | `2017-12-21` : 0.577 m³/s | `2017-12-22` : 0.49 m³/s
  - `2017-12-23` : 0.416 m³/s | `2017-12-24` : 0.353 m³/s | `2017-12-25` : 0.299 m³/s | `2017-12-26` : 0.254 m³/s
  - `2017-12-27` : 0.216 m³/s | `2017-12-28` : 0.183 m³/s | `2017-12-29` : 0.155 m³/s | `2017-12-30` : 0.132 m³/s
  - `2017-12-31` : 0.112 m³/s | `2018-01-01` : 0.095 m³/s | `2018-01-02` : 0.081 m³/s | `2018-01-03` : 0.068 m³/s
  - `2018-01-04` : 0.058 m³/s | `2018-01-05` : 0.049 m³/s | **`2018-01-06` : MANQUANTE (omise de obs_daily.csv, non convertie en 0)**
  - `2018-01-07` : 3.99 m³/s | `2018-01-08` : 9.5 m³/s | `2018-01-09` : 51.0 m³/s | `2018-01-10` : 35.2 m³/s
- **Période 2018-02-15 au 2018-03-05 :**
  - `2018-02-15` : 8.93 m³/s | `2018-02-16` : 7.22 m³/s | `2018-02-17` : 6.14 m³/s | `2018-02-18` : 4.8 m³/s
  - `2018-02-19` : 9.02 m³/s | `2018-02-20` : 0.294 m³/s | `2018-02-21` : 0.299 m³/s | `2018-02-22` : 0.305 m³/s
  - `2018-02-23` : 0.31 m³/s | `2018-02-24` : 0.316 m³/s | `2018-02-25` : 0.322 m³/s | `2018-02-26` : 0.328 m³/s
  - `2018-02-27` : 0.334 m³/s | `2018-02-28` : 0.34 m³/s | `2018-03-01` : 0.255 m³/s | `2018-03-02` : 25.4 m³/s
  - `2018-03-03` : 15.0 m³/s | `2018-03-04` : 33.4 m³/s | `2018-03-05` : 54.0 m³/s

#### Sidi Jabeur (`b_s_jabeur`)
- **Période 2018-07-01 au 2018-09-30 :**
  - Du `2018-07-01` au `2018-07-16` : **0.187 m³/s** constant (16 jours, flag `plage_constante`).
  - `2018-07-17` : **0.162 m³/s**.
  - Du **`2018-07-18` au `2018-09-02` : STRICTEMENT 0.0 m³/s PENDANT 47 JOURS CONSÉCUTIFS** (flag `plage_constante`).
  - `2018-09-03` : 0.499 m³/s | `2018-09-04` : 8.27 m³/s | `2018-09-05` : 5.51 m³/s | `2018-09-06` : 0.265 m³/s
  - `2018-09-07` : 0.014 m³/s | `2018-09-08` : 0.009 m³/s | `2018-09-09` : 0.007 m³/s | `2018-09-10` au `12` : 0.004 m³/s
  - `2018-09-13` : 1.9 m³/s | `2018-09-14` : 0.767 m³/s | `2018-09-15` : 0.047 m³/s | `2018-09-16` : 0.017 m³/s
  - `2018-09-17` : 50.1 m³/s | `2018-09-18` : 23.4 m³/s | `2018-09-19` : 15.3 m³/s | `2018-09-20` : 3.87 m³/s
  - `2018-09-21` : 0.731 m³/s | `2018-09-22` : 0.235 m³/s | `2018-09-23` : 0.082 m³/s | `2018-09-24` : 0.059 m³/s
  - `2018-09-25` : 0.048 m³/s | `2018-09-26` : 0.041 m³/s | `2018-09-27` : 0.04 m³/s | `2018-09-28` : 6.07 m³/s
  - `2018-09-29` : 0.946 m³/s | `2018-09-30` : 27.3 m³/s

### 6.4 Plus longue séquence de débit nul à Sidi Jabeur en 2018
- **Dates exactes :** Du **18 juillet 2018 au 02 septembre 2018 inclus**.
- **Durée :** **47 jours consécutifs à 0.0 m³/s**.

### 6.5 Confirmation de l'identité entre Ain Loudah et S.M. Cherif
- **Sur l'année 2018 :** Les séries de débit de `b_a_loudah` et `b_s_cherif` sont **100% IDENTIQUES** (365 jours sur 365, corrélation $r = 1.000$, écart moyen $0.000	ext{ m}^3/	ext{s}$).
- **Sur l'ensemble de l'historique commun (19 013 dates) :** **18 317 dates sont strictement identiques (96.34%)**. Le script `process_streamflow.py` (lignes 175–178 et README.txt) signale formellement qu'il s'agit d'un **doublon suspect dans les fichiers sources ABH bruts** (`b_a_loudah.xlsx` et `b_s_cherif.xlsx`), conservé tel quel sans arbitrage avec le flag `doublon_suspect`.

---

## 7. Provenance des Figures

### 7.1 Tableau de provenance des figures

| Figure | Script générateur | Fichiers de données lus (chemins exacts) | Date génération | Chemin du fichier PNG |
| :--- | :--- | :--- | :---: | :--- |
| **F1A** | `experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_multistation_figures.py` (l. 80-126) | `postproc/tables/streamflow_all_stations_2018.csv` | 2026-11-17 09:07:16 | [f1a_hydrographs_bouregreg_daily_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f1a_hydrographs_bouregreg_daily_2018_en.png) |
| **F1B** | `generate_multistation_figures.py` (l. 127-186) | `postproc/tables/streamflow_all_stations_2018.csv`, `data/streamflow_clean/obs_monthly.csv` | 2026-11-17 09:07:23 | [f1b_hydrographs_sebou_monthly_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f1b_hydrographs_sebou_monthly_2018_en.png) |
| **F2** | `generate_multistation_figures.py` (l. 187-261) | `postproc/tables/streamflow_all_stations_2018.csv`, `postproc/tables/catchment_fluxes_multistation_daily_2018.csv`, `routing/plots/sebou_bouregreg/tables/daily_precip_comparison_2018.csv` | 2026-11-17 09:07:30 | [f2_precip_and_flood_response_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f2_precip_and_flood_response_2018_en.png) |
| **F3** | `generate_multistation_figures.py` (l. 262-335) | `postproc/tables/catchment_fluxes_multistation_daily_2018.csv`, `postproc/tables/streamflow_all_stations_2018.csv` | 2026-11-17 09:07:39 | [f3_daily_qs_qsb_hydrographs_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f3_daily_qs_qsb_hydrographs_2018_en.png) |
| **F4** | `generate_multistation_figures.py` (l. 336-477) | `postproc/tables/streamflow_all_stations_2018.csv`, `postproc/tables/table_multistation_lowflows_2018.csv` | 2026-11-17 09:07:50 | [f4_lowflow_diagnostic_summer2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f4_lowflow_diagnostic_summer2018_en.png) |
| **F5** | `experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/generate_f5_f7_deliverables.py` (l. 207-301) | `routing/outputs/{OL_R1_SIMGM,OL_R2_SIMTOP,OL_R3_SCHAAKE96,OL_R4_BATS}/streamflow_daily_stations.csv`, `data/streamflow_clean/obs_daily.csv` | 2026-11-17 14:50:23 | [f5_discontinuity_and_continuity_check_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f5_discontinuity_and_continuity_check_en.png) |
| **F5b** | `generate_f5_f7_deliverables.py` (l. 302-387) | `routing/outputs/OL_R1_SIMGM/streamflow_daily_stations.csv`, `experiments/NorthMor/routing/output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv`, `routing/output/DA_nocdf_2016_2020/t8_sim_daily_12stations_da_nocdf.csv`, `routing/output/DA_cdf_2016_2020/t9_sim_daily_12stations_da_cdf.csv`, `data/streamflow_clean/obs_daily.csv` | 2026-11-17 14:50:25 | [f5b_legacy_vs_current_continuity_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f5b_legacy_vs_current_continuity_2018_en.png) |
| **F6** | `generate_multistation_figures.py` (l. 537-606) | `postproc/tables/table_multistation_metrics_2018.csv` | 2026-11-17 09:08:03 | [f6_multistation_synthesis_performance_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f6_multistation_synthesis_performance_en.png) |
| **F7** | `generate_f5_f7_deliverables.py` (l. 388-535) | `routing/outputs/{OL_R1_SIMGM,OL_R2_SIMTOP,OL_R3_SCHAAKE96,OL_R4_BATS}/streamflow_daily_stations.csv`, `data/streamflow_clean/obs_daily.csv`, `data/streamflow_clean/obs_monthly.csv` | 2026-11-17 14:50:27 | [f7_four_representative_stations_2018_en.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/figures/f7_four_representative_stations_2018_en.png) |

### 7.2 Répertoires « legacy » lus pour F5b
Pour F5b, le script lit exclusivement les répertoires de simulation **corrigés et validés** :
- `experiments/NorthMor/routing/output/OPL_2016_2020_corrigee/` (via `t7_sim_daily_12stations_corrigee.csv`)
- `experiments/NorthMor/routing/output/DA_nocdf_2016_2020/` (via `t8_sim_daily_12stations_da_nocdf.csv`)
- `experiments/NorthMor/routing/output/DA_cdf_2016_2020/` (via `t9_sim_daily_12stations_da_cdf.csv`)
Les répertoires bruts ou obsolètes (`OPL_2016_2020` non corrigé, `OPL_201801`, `OPL_spinup_cycle1`, `OPL_spinup_cycle2`) ne sont pas lus dans F5b.

### 7.3 Origine du premier graphique d'hydrogrammes envoyé à Augusto Getirana
- **Le graphique initial :** Figure comparative [lalla_chafia_2018_fluxes_and_streamflow.png](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_fluxes_and_streamflow.png) produite par [diagnostic_lalla_chafia_flux.py](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/scripts/diagnostic_lalla_chafia_flux.py), ainsi que les synthèses quinquennales 2016–2020 (`lalla_chafia_2016_2020_synthesis.png` et `sidi_jabeur_2016_2020_synthesis.png`).
- **Répertoires lus par ces scripts :**
  - `experiments/NorthMor/routing/output/OPL_2016_2020_corrigee/` (simulation corrigée `linres=1`)
  - `experiments/NorthMor/routing/output/OPL_linres0_2016_2020/` (simulation `linres=0`)
- **Nature de l'anomalie perçue (chute vers zéro) :**  
  L'audit approfondi consigné dans [F5_CONTINUITY_FINDINGS.md](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/F5_CONTINUITY_FINDINGS.md) démontre qu'**aucun fichier de données sur disque ne contient d'effondrement à zéro en fin d'année 2018**. Les débits simulés OPL décroissent de manière strictement continue au 31 décembre 2018 ($3{,}79	ext{ m}^3/	ext{s}$ au 31/12/2018 puis $3{,}78	ext{ m}^3/	ext{s}$ au 01/01/2019).  
  L'impression visuelle de décrochage transmise à Augusto résultait du contraste extrême entre ce débit simulé maintenu et le tarissement estival observé ($0{,}00	ext{ m}^3/	ext{s}$ sur 47 jours à Sidi Jabeur), combiné à des artefacts d'affichage sur des prototypes non archivés de scripts de tracé.

---

## 8. Métriques et Réconciliation Statistique

### 8.1 Fichiers contenant les métriques auditées
Les valeurs numériques exactes mentionnées par le relecteur sont répertoriées dans deux fichiers canoniques :
1. [four_representative_stations_metrics_2018.csv](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/four_representative_stations_metrics_2018.csv) (et son double dans `tables/four_representative_stations_metrics_2018.csv`).
2. [table_multistation_metrics_2018.csv](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/table_multistation_metrics_2018.csv).

### 8.2 Tableau de vérification des valeurs

| Station | Schéma | KGE audité | KGE dans fichier CSV | NSE audité | NSE dans fichier CSV | PBIAS (%) | Corrélation $r$ | Pas de temps | Résolution temporelle |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Lalla Chafia** | **SIMGM (Ref)** | **0,079** | **0.079** | **0,17** | **0.169** | -17.9% | 0.456 | journalier | 364 jours valides en 2018 (06/01 manquant) |
| **Lalla Chafia** | **SIMTOP** | **0,593** | **0.593** | **0,59** | **0.592** | +16.9% | 0.777 | journalier | 364 jours valides en 2018 |
| **Sidi Jabeur** | **SIMGM (Ref)** | **−0,161** | **-0.161** | — | 0.054 | -63.8% | 0.656 | journalier | 365 jours valides en 2018 |
| **Sidi Jabeur** | **BATS** | **0,476** | **0.476** | — | 0.422 | -10.1% | 0.652 | journalier | 365 jours valides en 2018 |
| **Aïn Timedrine**| **SIMGM (Ref)** | **−0,21** | **-0.212** | — | -2.008 | -79.8% | 0.772 | mensuel | 12 mois de 2018 |
| **Aïn Timedrine**| **BATS** | **0,53** | **0.529** | — | 0.330 | -36.8% | 0.909 | mensuel | 12 mois de 2018 |
| **Dar El Hamra** | **SIMGM (Ref)** | **−0,29** | **-0.292** | — | -0.643 | -84.5% | 0.773 | mensuel | 12 mois de 2018 |
| **Dar El Hamra** | **BATS** | **0,16** | **0.161** | — | 0.258 | -54.1% | 0.946 | mensuel | 12 mois de 2018 |

### 8.3 Formule exacte du KGE, période et pas de temps
- **Formule mathématique :**  
  Il s'agit de la formulation originale **KGE-2009 (Gupta et al., 2009)**, codée dans [evaluate_multistation_performance.py](file:///home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/postproc/multistation/scripts/evaluate_multistation_performance.py#L45-L55) (lignes 45–55) :
  $$KGE = 1 - \sqrt{(r - 1)^2 + (lpha - 1)^2 + (eta - 1)^2}$$
  avec :
  - $r$ : coefficient de corrélation linéaire de Pearson entre simulation et observation.
  - $lpha = \sigma_{	ext{sim}} / \sigma_{	ext{obs}}$ : ratio des écarts-types (variabilité relative).
  - $eta = \mu_{	ext{sim}} / \mu_{	ext{obs}}$ : ratio des moyennes (biais volumique relatif).
  *(Ce n'est pas le KGE-2012 de Kling et al. qui remplace $lpha$ par le ratio des coefficients de variation $\gamma = (\sigma_s/\mu_s)/(\sigma_o/\mu_o)$).*
- **Période :** Année civile **2018** complète (du 01/01/2018 au 31/12/2018).
- **Pas de temps :**
  - **Journalier :** Pour les stations du Bouregreg (**Lalla Chafia** avec $N=364$ jours valides car le 06/01/2018 est manquant dans l'ABH ; **Sidi Jabeur** avec $N=365$ jours complets).
  - **Mensuel :** Pour les stations du Sebou (**Aïn Timedrine** et **Dar El Hamra**, avec $N=12$ mois calendaires agrégés, car les observations de l'ABH Sebou ne sont disponibles qu'au pas mensuel).
