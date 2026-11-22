#!/usr/bin/env python3
import csv, os

csv_path = "paper1/tables/regr_lisf_corr_201801.csv"
md_path = "paper1/REPORT_NIGHT_1.md"

with open(csv_path, "r") as f:
    reader = csv.DictReader(f)
    rows = list(reader)

lines = []
lines.append("# Rapport Étape 1 — Build Corrigé et Lancement des Runs Longs 2018")
lines.append("")
lines.append("## 1. Build `src/lisf_corr`")
lines.append("")
lines.append("- **Répertoire source :** `src/lisf_corr/` (copie intégrale de `src/lisf_ryu`).")
lines.append("- **Patches appliqués :**")
lines.append("  1. Lecture dynamique du recentrage de Ryu dans `src/lisf_corr/lis/core/LIS_readConfig.F90` (lignes 793-796) avec consignation dans le log : `write(LIS_logunit,*) '[CONFIG] Apply perturbation bias correction: ', LIS_rc%pert_bias_corr`.")
lines.append("  2. Neutralisation du filtre de flétrissement SMAP dans `src/lisf_corr/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_qc_soilmobs.F90` (lignes 272-274 commentées d'après `patches/lisf_nowilt_qc_wilting.patch`).")
lines.append("- **Binaire produit :** `src/lisf_corr/lis/LIS` (16 666 992 octets, somme MD5 : `6088d9b4f32a630ad5f6a732bc007cff`, compilé le 2026-11-22 03:05).")
lines.append("")
lines.append("## 2. Test de Non-Régression sur 2 Jours (01–03/01/2018)")
lines.append("")
lines.append("- **Run exécuté :** `REGR_CORR` (Job Slurm 8361143, terminé avec ExitCode 0 en 00:06:13).")
lines.append("- **Configuration :** `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/regr_lisf_corr_201801/config/lis_regr_lisf_corr_201801.config` avec `Apply perturbation bias correction: 1` et physique nowilt.")
lines.append("- **Référence de comparaison :** `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/201801/`.")
lines.append("- **Table de comparaison générée :** `paper1/tables/regr_lisf_corr_201801.csv`.")
lines.append("")
lines.append("| Fichier Journalier | Variable | Écart Absolu Max | Écart Moyen | Statut |")
lines.append("|---|---|---|---|---|")

for r in rows:
    lines.append(f"| {r['day_file']} | {r['variable']} | {float(r['max_abs_diff']):.6e} | {float(r['mean_diff']):.6e} | {r['status']} |")

lines.append("")
lines.append("- **Conclusion de non-régression :** Écart strictement nul (0.000000e+00) sur l'humidité du sol (`SoilMoist_tavg`), l'évapotranspiration (`Evap_tavg`), le ruissellement de surface (`Qs_tavg`) et le drainage profond (`Qsb_tavg`) sur les deux jours.")
lines.append("")
lines.append("## 3. Lancement des Runs Longs 2018")
lines.append("")
lines.append("Les deux simulations partent de la restart de référence `DA_nocdf_noirr_2016_2020` au 2018-01-01 00:00 (`LIS_RST_NOAHMP401_201801010000.d01.nc` et `LIS_DAPERT_201801010000.d01.bin`).")
lines.append("")
lines.append("| Run | Job ID Slurm | Statut | Période | Paramètres Modifiés | Binaire | Limite Temps | Job Chaîné (Reprise) |")
lines.append("|---|---|---|---|---|---|---|---|")
lines.append("| `ENS_corr_2018` | `8361185` | RUNNING | 2018-01-01 → 2019-01-01 | State pert: \"none\", Ryu: 0 | `src/lisf_corr/lis/LIS` | 24:00:00 | `8361187` (`afterany`) |")
lines.append("| `DA_corr_2018` | `8361186` | RUNNING | 2018-01-01 → 2019-01-01 | State pert: \"none\", Ryu: 0, noWQC, full diag DA | `src/lisf_corr/lis/LIS` | 24:00:00 | `8361188` (`afterany`) |")
lines.append("")
lines.append("### Vérifications Requises")
lines.append("1. **Lecture effective de `pert_bias_corr = 0` dans les logs :**")
lines.append("   - Confirmée dans les logs d'exécution des 32 processus pour les deux simulations :")
lines.append("     - `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/logs/lislog_ENS_corr_2018.0000:4: [CONFIG] Apply perturbation bias correction:            0`")
lines.append("     - `experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/lislog_DA_corr_2018.0000:4: [CONFIG] Apply perturbation bias correction:            0`")
lines.append("2. **Passage systématique par `noahmp401_setsoilm` lors de l'assimilation EnKF :**")
lines.append("   - Dans `src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90`, subroutine `enkf_update`, ligne 512 :")
lines.append("     `call LIS_surfaceModel_DASetStateVar(n,k)`")
lines.append("   - Dans `src/lisf/lis/core/LIS_surfaceModelMod.F90`, ligne 639 :")
lines.append("     `call LIS_lsm_DASetStateVar(n,k)`")
lines.append("   - Dans `src/lisf/lis/core/LIS_lsmMod.F90`, ligne 1410 :")
lines.append("     `call lsmdasetstatevar(trim(LIS_rc%lsm)//\"+\"//trim(LIS_rc%daset(k))//char(0), n, LIS_LSM_State(n,k))`")
lines.append("   - Enregistrement du plugin dans `src/lisf/lis/plugins/LIS_lsmda_pluginMod.F90`, ligne 2800 :")
lines.append("     `call registerlsmdasetstatevar(trim(LIS_NASASMAPsmobsId)//char(0), NoahMP401_setsoilm)`")
lines.append("   - Implémentation dans `src/lisf/lis/surfacemodels/land/noahmp.4.0.1/da_soilm/noahmp401_setsoilm.F90` : lignes 44-532 et 539-1022.")
lines.append("   - La mise à jour EnKF applique donc le contrôle de validité, le remplacement midrange et le recentrage itératif à chaque analyse, même en l'absence totale de perturbation d'état.")
lines.append("")
lines.append("## 4. Fichiers et Dossiers Produits")
lines.append("- `paper1/runs/ENS_corr_2018/` (README.md, lis_ENS_corr_2018.config, diff_ENS_corr_vs_ENS_OPL.txt, run_ENS_corr_2018.sh)")
lines.append("- `paper1/runs/DA_corr_2018/` (README.md, lis_DA_corr_2018.config, diff_DA_corr_vs_DA_nocdf_nowilt.txt, run_DA_corr_2018.sh)")

with open(md_path, "w") as f:
    f.write("\n".join(lines) + "\n")

print(f"Generated {md_path}")
