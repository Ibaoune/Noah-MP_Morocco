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
