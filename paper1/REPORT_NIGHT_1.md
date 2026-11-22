# Rapport Étape 1 — Build Corrigé et Lancement des Runs Longs 2018

## 1. Build `src/lisf_corr`

- **Répertoire source :** `src/lisf_corr/` (copie intégrale de `src/lisf_ryu`).
- **Patches appliqués :**
  1. Lecture dynamique du recentrage de Ryu dans `src/lisf_corr/lis/core/LIS_readConfig.F90` (lignes 793-796) avec consignation dans le log : `write(LIS_logunit,*) '[CONFIG] Apply perturbation bias correction: ', LIS_rc%pert_bias_corr`.
  2. Neutralisation du filtre de flétrissement SMAP dans `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90` (lignes 272-274 commentées d'après `patches/lisf_nowilt_qc_wilting.patch`).
- **Binaire produit :** `src/lisf_corr/lis/LIS` (16 666 992 octets, somme MD5 : `6088d9b4f32a630ad5f6a732bc007cff`, compilé le 2026-11-22 03:05).

## 2. Test de Non-Régression sur 2 Jours (01–03/01/2018)

- **Run exécuté :** `REGR_CORR` (Job Slurm 8361143, terminé avec ExitCode 0 en 00:06:13).
- **Configuration :** `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/regr_lisf_corr_201801/config/lis_regr_lisf_corr_201801.config` avec `Apply perturbation bias correction: 1` et physique nowilt.
- **Référence de comparaison :** `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/201801/`.
- **Table de comparaison générée :** `paper1/tables/regr_lisf_corr_201801.csv`.

| Fichier Journalier | Variable | Écart Absolu Max | Écart Moyen | Statut |
|---|---|---|---|---|
| LIS_HIST_201801020000.d01.nc | SoilMoist_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801020000.d01.nc | Evap_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801020000.d01.nc | Qs_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801020000.d01.nc | Qsb_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801030000.d01.nc | SoilMoist_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801030000.d01.nc | Evap_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801030000.d01.nc | Qs_tavg | 0.000000e+00 | 0.000000e+00 | PASS |
| LIS_HIST_201801030000.d01.nc | Qsb_tavg | 0.000000e+00 | 0.000000e+00 | PASS |

- **Conclusion de non-régression :** Écart strictement nul (0.000000e+00) sur l'humidité du sol (`SoilMoist_tavg`), l'évapotranspiration (`Evap_tavg`), le ruissellement de surface (`Qs_tavg`) et le drainage profond (`Qsb_tavg`) sur les deux jours.

## 3. Lancement des Runs Longs 2018

Les deux simulations partent de la restart de référence `DA_nocdf_noirr_2016_2020` au 2018-01-01 00:00 (`LIS_RST_NOAHMP401_201801010000.d01.nc` et `LIS_DAPERT_201801010000.d01.bin`).

| Run | Job ID Slurm | Statut | Période | Paramètres Modifiés | Binaire | Limite Temps | Job Chaîné (Reprise) |
|---|---|---|---|---|---|---|---|
| `ENS_corr_2018` | `8361185` | RUNNING | 2018-01-01 → 2019-01-01 | State pert: "none", Ryu: 0 | `src/lisf_corr/lis/LIS` | 24:00:00 | `8361187` (`afterany`) |
| `DA_corr_2018` | `8361186` | RUNNING | 2018-01-01 → 2019-01-01 | State pert: "none", Ryu: 0, noWQC, full diag DA | `src/lisf_corr/lis/LIS` | 24:00:00 | `8361188` (`afterany`) |

### Vérifications Requises
1. **Lecture effective de `pert_bias_corr = 0` dans les logs :**
   - Confirmée dans les logs d'exécution des 32 processus pour les deux simulations :
     - `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/logs/lislog_ENS_corr_2018.0000:4: [CONFIG] Apply perturbation bias correction:            0`
     - `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/lislog_DA_corr_2018.0000:4: [CONFIG] Apply perturbation bias correction:            0`
2. **Passage systématique par `noahmp401_setsoilm` lors de l'assimilation EnKF :**
   - Dans `src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90`, subroutine `enkf_update`, ligne 512 :
     `call LIS_surfaceModel_DASetStateVar(n,k)`
   - Dans `src/lisf/lis/core/LIS_surfaceModelMod.F90`, ligne 639 :
     `call LIS_lsm_DASetStateVar(n,k)`
   - Dans `src/lisf/lis/core/LIS_lsmMod.F90`, ligne 1410 :
     `call lsmdasetstatevar(trim(LIS_rc%lsm)//"+"//trim(LIS_rc%daset(k))//char(0), n, LIS_LSM_State(n,k))`
   - Enregistrement du plugin dans `src/lisf/lis/plugins/LIS_lsmda_pluginMod.F90`, ligne 2800 :
     `call registerlsmdasetstatevar(trim(LIS_NASASMAPsmobsId)//char(0), NoahMP401_setsoilm)`
   - Implémentation dans `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90` : lignes 44-532 et 539-1022.
   - La mise à jour EnKF applique donc le contrôle de validité, le remplacement midrange et le recentrage itératif à chaque analyse, même en l'absence totale de perturbation d'état.

## 4. Fichiers et Dossiers Produits
- `paper1/runs/ENS_corr_2018/` (README.md, lis_ENS_corr_2018.config, diff_ENS_corr_vs_ENS_OPL.txt, run_ENS_corr_2018.sh)
- `paper1/runs/DA_corr_2018/` (README.md, lis_DA_corr_2018.config, diff_DA_corr_vs_DA_nocdf_nowilt.txt, run_DA_corr_2018.sh)
