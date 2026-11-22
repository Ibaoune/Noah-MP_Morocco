# Sources et Hashes de Commit — Papier 1 (Lots 1 et 2)

Ce fichier consigne l'ensemble des dépôts, commits, patchs et binaires utilisés pour garantir la reproductibilité intégrale des résultats du papier 1.

## 1. Dépôts Git

| Dépôt | Branche | Commit Hash (HEAD) | Dernier Message de Commit |
|---|---|---|---|
| **`Ibaoune/Noah-MP_Morocco`** | `paper1-closure` | `48dc170fd16c1f90a9445b538bb8b30fbad205e1` | 2026-11-22 00:23:41 +0100 (paper1: execute Lot 1c (noRyu completion, EnKF 15min analysis check, spread audit)) |
| **`Ibaoune/smap-xai-audit`** | `elaabar` | `18d694ecd3d29477133b95e68875a8735644c198` | 2026-11-20 00:19:52 +0100 (audit(diag2018): extension annuelle 2018 et totaux JJA des bilans hydriques et de censure) |

## 2. Binaires et Exécutables LISF 7.5

| Binaire | Usage | Chemin Relatif | Somme de Contrôle MD5 |
|---|---|---|---|
| **LIS Production** | Runs standard (OPL, DA, Sensibilité, Routage HyMAP) | `src/lisf/lis/make/LIS` | `04150c14d7bcee2f83567688254b5a95` |
| **LIS NoWilt** | Runs audit sans filtre flétrissement | `src/lisf_nowilt/lis/LIS` | `748798ad2db5ec35fa692dc6bc48633e` |

## 3. Fichiers de Données Clés et Paramètres

| Fichier | Rôle | MD5 |
|---|---|---|
| `data/lis_input/lis_input_NorthMor_5km.nc` | Domaine de référence 181×121 (16 030 mailles terre) | `9f6d71b86147343461c63ed4ccf8750f` |
| `patches/lisf_nowilt_qc_wilting.patch` | Patch Fortran supprimant le filtre QC flétrissement | `e779084ac14137cf3945e264eaf60b47` |
| `patches/lisf_hymap1_fixes.patch` | Patch correctifs routage HyMAP v1 | `2c84e56f45a09a4ad94a95e5203a5761` |

## 4. Fichiers et Configurations du Bloc B (Routage HyMAP-2 linres = 0)

| Fichier | Rôle | MD5 |
|---|---|---|
| `paper1/runs/routing/configs/lis_hymap2_ol_daic_2018_linres0.config` | Config HyMAP-2 linres=0 OL_DAIC | `a7ef50b609c80966ed6a1a06addd2095` |
| `paper1/runs/routing/configs/lis_hymap2_ens_opl_2018_linres0.config` | Config HyMAP-2 linres=0 ENS_OPL | `1b2d8df40c267ba698dfe28b8efbcd89` |
| `paper1/runs/routing/configs/lis_hymap2_da_nocdf_nowilt_2018_linres0.config` | Config HyMAP-2 linres=0 NoWilt | `59832cb1f5ccfdd090ba6bb23d108001` |
| `experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc` | Restart HyMAP linres0 01-01-2018 | `6d00dbcfca6f3d6df2c0d4fdf756593f` |

## 5. Données d'Observation pour l'Évaluation (Blocs C1 et C2)

- **Inventaire 2018 des stations** : `experiments/NorthMor/opl_hydrology_sensitivity/postproc/tables/station_inventory_2018.csv`
- **Appariement HyMAP des stations** : `experiments/NorthMor/routing/stations/hymap_stations_pairing.csv`
- **Données débit nettoyées** : `data/streamflow_clean/obs_daily.csv` (Bouregreg), `obs_monthly.csv` (Sebou)
- **Évapotranspiration GLEAM v4.3a** : `data/validation/evapotranspiration/GLEAM/raw/` (0,10° natif, journalier mm/jour, variables `E` et `Ep`)
- **Évapotranspiration WaPOR v3 AETI** : `data/validation/evapotranspiration/WaPOR/WaPOR_v3_AETI/` (~250m natif, annuel mm/an 2018-2020)
- **Forçages météorologiques** : MERRA-2 (NASA GMAO) + GPM IMERG Final Run v07B (`data/forcing/`)
- **Observations satellitaires** : SMAP L3 Enhanced 9 km `SPL3SMP_E` (`data/observations/SMAP_SPL3SMP_E/`)
