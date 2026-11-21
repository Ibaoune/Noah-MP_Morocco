# Rapport d'Exécution — Bouclage Papier 1 — LOT 1/4

**Périmètre strict du Lot 1** : Bloc A (Lancement des runs), Bloc E (Table des stations), Bloc D partie 1 (Inventaire des diagnostics DA).
*Généré automatiquement par `paper1/scripts/generate_report_lot1.py` à partir des fichiers CSV et des logs HPC.*

## 1. Bloc A1 — Sélection Traçable de l'Année Sèche

Calcul de la précipitation annuelle IMERG moyenne sur le domaine (16 030 mailles terrestres) à partir des sorties journalières `TotalPrecip_tavg` de `OPL_noirr_2016_2020` (P réellement lue par le modèle) :

| year | n_days_expected | n_days_found | P_annual_mm_landmean | is_candidate | da_nocdf_surf_restart_0101_exists | da_nocdf_pert_restart_0101_exists |
| --- | --- | --- | --- | --- | --- | --- |
| 2016 | 366 | 366 | 281.65 | False | False | False |
| 2017 | 365 | 365 | 177.03 | True | True | True |
| 2018 | 365 | 365 | 379.39 | False | True | True |
| 2019 | 365 | 365 | 184.13 | True | True | True |
| 2020 | 366 | 366 | 192.30 | True | True | True |

**Décision automatique** :
| selected_year | P_annual_mm_landmean | rule | status |
| --- | --- | --- | --- |
| 2017 | 177.03 | min P among 2017,2019,2020 with complete days and DA_nocdf restarts at 01-01 | OK |

- **Année retenue (YYYY)** : **2017** avec **177.03 mm/an** (plus sèche que 2019 avec 184.13 mm et 2020 avec 192.30 mm).
- **Intégrité temporelle** : 365/365 jours trouvés sans aucune interpolation.
- **Disponibilité des restarts DA_nocdf** : restart surface (`LIS_RST_NOAHMP401_201701010000.d01.nc`) et restart perturbation (`LIS_DAPERT_201701010000.d01.bin`) présents et validés.

## 2. Bloc A2 & A3 & A4 — Statut des Runs Soumis sur HPC Toubkal

Table des 5 simulations configurées, générées et soumises via Slurm :

| run_name | priority | job_id | status | period | binary | walltime |
| --- | --- | --- | --- | --- | --- | --- |
| ENS_OPL_2017 | P1 | 8360359 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf/lis/make/LIS | 16:00:00 |
| OL_DAIC_2017 | P1 | 8360360 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf/lis/make/LIS | 03:30:00 |
| DA_nocdf_nowilt_2017 | P2 | 8360361 | SUBMITTED | 2017-01 to 2018-01 | ./src/lisf_nowilt/lis/LIS | 16:00:00 |
| DA_nocdf_nostate_2018MAM | P2 | 8360362 | SUBMITTED | 2018-03 to 2018-06 | ./src/lisf/lis/make/LIS | 06:00:00 |
| DA_nocdf_diag_2018ND | P1 | 8360363 | SUBMITTED | 2018-11 to 2019-01 | ./src/lisf/lis/make/LIS | 04:30:00 |

**État d'exécution Slurm (sacct instantané)** :
```
8360359           ENS_OPL_17    RUNNING   00:05:43 2026-11-21T22:42:31 slurm-compute-h21a5-u12-+ 
8360360           OL_DAIC_17    RUNNING   00:05:43 2026-11-21T22:42:31 slurm-compute-h24d8-u8-s+ 
8360361         DA_nowilt_17    RUNNING   00:05:43 2026-11-21T22:42:31 slurm-compute-h22b8-u9-s+ 
8360362        DA_nost_18MAM    RUNNING   00:05:43 2026-11-21T22:42:31 slurm-compute-h22d5-u3-s+ 
8360363         DA_diag_18ND    RUNNING   00:05:43 2026-11-21T22:42:31 slurm-compute-h22d5-u30-+
```

### 2.1. Contrôle de l'Écart de Stock Initial OL_DAIC_2017 (Bloc A2)

Même méthode et script qu'en 2018 : sélection par maille du membre le plus proche de l'humidité de colonne moyenne d'ensemble (source : `DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc`).

| component | ens_mean_mm | daic_selected_mm | delta_daic_minus_ens_mm | mean_abs_diff_pixel_mm | selection_criterion |
| --- | --- | --- | --- | --- | --- |
| SMC_col_mm | 450.89 | 450.86 | -0.03 | 1.25 | MIN_ABS_DIFF_SMC_COL |
| WA_mm | 4785.21 | 4783.98 | -1.23 | 3.65 | COPIED_FROM_SMC_SELECTION |
| CANWAT_mm | 0.0001 | 0.0001 | -0.0000 | 0.0000 | COPIED_FROM_SMC_SELECTION |
| SNEQV_mm | 1.01 | 1.01 | -0.0002 | 0.19 | COPIED_FROM_SMC_SELECTION |
| TOTAL_STOCK_mm | 5237.10 | 5235.84 | -1.26 | 4.41 | SUM_OF_COMPONENTS |

- **Écart d'humidité colonne moyenne domaine** : `-0.0290 mm` (critère requis `< 0.5 mm` : **VALIDÉ**).
- **Fichier de restart 1 membre créé** : `experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc` (1.57 Mo).

### 2.2. Test de Reproduction Exacte pour DA_nocdf_diag_2018ND (Bloc A4)

Vérification bit-à-bit sur le jour test 2018-11-01 (`LIS_HIST_201811020000.d01.nc`) entre le run diagnostic et la production `DA_nocdf_noirr_2016_2020` :

| variable | test_date | max_abs_diff | mean_abs_diff | threshold | status |
| --- | --- | --- | --- | --- | --- |
| SoilMoist_tavg | 2018-11-01 | 0.0000 | 0.0000 | 0.0000 | PASSED |
| Evap_tavg | 2018-11-01 | 0.0000 | 0.0000 | 0.0000 | PASSED |
| Qs_tavg | 2018-11-01 | 0.0000 | 0.0000 | 0.0000 | PASSED |
| Qsb_tavg | 2018-11-01 | 0.0000 | 0.0000 | 0.0000 | PASSED |
| TotalPrecip_tavg | 2018-11-01 | 0.0000 | 0.0000 | 0.0000 | PASSED |

- **Résultat** : Accord numérique parfait (`Max Abs Diff = 0.000e+00 < 1e-6`) sur l'humidité du sol multi-couches et sur l'ensemble des flux (ET, Qs, Qsb, P).

## 3. Bloc E — Table des Stations Hydrométriques (Table 2 du Papier)

Générée par `paper1/scripts/e_table2_stations.py` par croisement de `station_inventory_2018.csv`, `hymap_stations_pairing.csv` et des séries d'observations `data/streamflow_clean/` :

| id | nom | bassin | sous_bassin | aire_officielle_km2 | aire_hymap_km2 | ecart_aire_pct | pas_temps | n_obs_2018 | n_obs_2017 | usage_papier |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| b_l_chafia | Lalla Chafia | Bouregreg | Bouregreg |  | 3341.60 |  | journalier | 364 | 365 | journalier |
| b_s_jabeur | Sidi Jabeur | Bouregreg | Bouregreg |  | 3138.50 |  | journalier | 365 | 365 | journalier |
| ain_timedrine | Ain Timedrine | Sebou | Sebou | 4387.00 | 4448.60 | 1.15 | mensuel | 12 | 12 | mensuel |
| ait_khabbach | Ait Khabbach | Sebou | Guigou | 1240.00 | 1343.00 | 8.03 | mensuel | 12 | 12 | mensuel |
| azzaba | Azzaba | Sebou | Sebou | 4640.00 | 4660.70 | 0.20 | mensuel | 12 | 12 | mensuel |
| dar_el_hamra | Dar El Hamra | Sebou | Zloul | 670.00 | 656.30 | -2.28 | mensuel | 12 | 12 | mensuel |
| pont_de_mdez | Pont de Mdez | Sebou | Sebou | 3435.00 | 3429.10 | -0.42 | mensuel | 12 | 12 | mensuel |
| b_a_loudah | Ain Loudah | Bouregreg | Bouregreg |  | 697.50 |  | journalier | 365 | 365 | exclu |
| b_s_cherif | S.M. Cherif | Bouregreg | Bouregreg |  | 649.50 |  | journalier | 365 | 365 | exclu |
| pont_ait_aissa | Pont Ait Aissa | Sebou | Guiguou | 205.00 | 253.70 | 23.46 | mensuel | 12 | 12 | mensuel (sensibilité) |
| b_a_ziar | Ain Ziar | Bouregreg | Bouregreg |  |  |  | journalier | 365 | 365 | exclu |
| b_r_fathia | Ras Fathia | Bouregreg | Bouregreg |  |  |  | journalier | 365 | 365 | exclu |
| adamna | Adamna | Ksob | Ksob |  | 1617.00 |  | mensuel | 0 | 8 | exclu |
| igrounzar | Igrounzar | Ksob | Igrounzar |  |  |  | mensuel | 0 | 0 | exclu |
| zelten | Zelten | Ksob | Igrounzar |  |  |  | mensuel | 0 | 0 | exclu |
| ain_aicha | Ain Aicha | Sebou | Ouergha | 2420.00 |  |  | mensuel | 0 | 0 | exclu |
| ain_al_ouali | Ain Al Ouali | Sebou | Lyhoudi | 408.00 |  |  | mensuel | 0 | 0 | exclu |
| azib_soltane | Azib Soltane | Sebou | Sebou | 16150.00 |  |  | mensuel | 0 | 0 | exclu |
| el_mers | El Mers | Sebou | Masser | 1004.00 | 972.20 | -3.41 | mensuel | 0 | 8 | exclu |
| allal_tazi | Sidi Allal Tazi | Sebou | SEBOU | 26600.00 |  |  | mensuel | 0 | 0 | exclu |

- **Fichiers exportés** : [`paper1/tables/table2_stations.csv`](tables/table2_stations.csv) et [`paper1/tables/table2_stations.md`](tables/table2_stations.md).
- **Données manquantes signalées** : Superficies officielles administratives manquantes dans les archives ABH pour les stations Bouregreg (`b_l_chafia`, `b_s_jabeur`, `b_a_loudah`, `b_s_cherif`) et Ksob (`adamna`, `igrounzar`, `zelten`). Ces cases restent rigoureusement vides sans estimation manuelle.

## 4. Bloc D (partie 1) — Inventaire des Diagnostics DA Archivés et Vérification Code

- **Fichier d'inventaire complet** : [`paper1/tables/da_diagnostics_inventory.md`](tables/da_diagnostics_inventory.md).
- **Fichiers archivés en production 2016–2020** :
  - 4 619 fichiers d'innovations (`*_innov.nc` : `innov_01`, `ninnov_01`, `analysis_residual_01`, `forecast_sigma_01`).
  - 4 619 fichiers d'incréments d'analyse (`*_incr.nc` : couches 1 à 4).
  - 1 827 fichiers quotidiens de spread d'ensemble (`*_spread.nc` : couches 1 à 4).
  - 4 619 fichiers d'observations SMAP prétraitées (`DAOBS`).
- **Vérification dans le code source LIS 7.5 (`src/lisf/lis/core/LIS_historyMod.F90`)** :
  - **Lignes 7949–7971** : Le calcul de l'écart-type (`std_v = sqrt(...)`) est désactivé à la compilation par un bloc `#if 0 ... #endif`.
  - **Lignes 7973–7985 (Ligne 7980)** : Le code actif exécuté calcule `gtmp(c,r) = max_v - min_v`.
  - **Constat** : Le « spread » LIS archivé est formellement une **ÉTENDUE (MAX − MIN)** et **NON un écart-type**.

## 5. Traçabilité des Hashes de Commit et Sources Utilisées

# Sources et Hashes de Commit — Papier 1 (Lot 1)

Ce fichier consigne l'ensemble des dépôts, commits, patchs et binaires utilisés pour garantir la reproductibilité intégrale des résultats du papier 1.

## 1. Dépôts Git

| Dépôt | Branche | Commit Hash (HEAD) | Dernier Message de Commit |
|---|---|---|---|
| **`Ibaoune/Noah-MP_Morocco`** | `paper1-closure` | `b4e9b170f2c02ff9beba1e0b76f269cf6250ee89` | 2026-11-21 22:48:06 +0100 (paper1: execute Lot 1 (robustness runs launch, station table 2, DA diagnostics inventory)) |
| **`Ibaoune/smap-xai-audit`** | `elaabar` | `18d694ecd3d29477133b95e68875a8735644c198` | 2026-11-20 00:19:52 +0100 (audit(diag2018): extension annuelle 2018 et totaux JJA des bilans hydriques et de censure) |

## 2. Binaires et Exécutables LISF 7.5

| Binaire | Usage | Chemin Relatif | Somme de Contrôle MD5 |
|---|---|---|---|
| **LIS Production** | Runs standard (OPL, DA, Sensibilité) | `src/lisf/lis/make/LIS` | `04150c14d7bcee2f83567688254b5a95` |
| **LIS NoWilt** | Runs audit sans filtre flétrissement | `src/lisf_nowilt/lis/LIS` | `748798ad2db5ec35fa692dc6bc48633e` |

## 3. Fichiers de Données Clés et Paramètres

| Fichier | Rôle | MD5 |
|---|---|---|
| `data/lis_input/lis_input_NorthMor_5km.nc` | Domaine de référence 181×121 (16 030 mailles terre) | `9f6d71b86147343461c63ed4ccf8750f` |
| `patches/lisf_nowilt_qc_wilting.patch` | Patch Fortran supprimant le filtre QC flétrissement | `e779084ac14137cf3945e264eaf60b47` |
| `patches/lisf_hymap1_fixes.patch` | Patch correctifs routage HyMAP v1 | `2c84e56f45a09a4ad94a95e5203a5761` |

## 4. Fichiers d'Entrée des Stations et Forçages

- **Inventaire 2018 des stations** : `experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv`
- **Appariement HyMAP des stations** : `experiments/NorthMor/routing/stations/hymap_stations_pairing.csv`
- **Données débit nettoyées** : `data/streamflow_clean/obs_daily.csv`, `obs_monthly.csv`, `stations.csv`
- **Forçages météorologiques** : MERRA-2 (NASA GMAO) + GPM IMERG Final Run v07B (`data/forcing/`)
- **Observations satellitaires** : SMAP L3 Enhanced 9 km `SPL3SMP_E` (`data/observations/SMAP_SPL3SMP_E/`)


---
### Fin du Lot 1 — Tous les éléments demandés sont produits, vérifiés et tracés. En attente des instructions pour le Lot 2.
