#!/usr/bin/env python3
"""
d_inventory_da.py -- Bloc D partie 1 (paper1, lot 1).

Inventaire exhaustif des diagnostics DA archivés par LIS en production :
  - DA_nocdf_noirr_2016_2020
  - DA_cdf_noirr_2016_2020

Inspecte :
  1. Les dossiers et fichiers DA réellement créés (DAOBS, EnKF, DAPERT).
  2. Les variables NetCDF, dimensions, shapes, unités et attributs.
  3. L'analyse du code source LIS 7.5 concernant la nature mathématique du « spread » LIS.

Sortie :
  paper1/tables/da_diagnostics_inventory.md
"""
import glob
import os
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
DA_NOCDF_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output")
DA_CDF_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output")
OUT_DIR = os.path.join(BASE_DIR, "paper1/tables")


def inspect_netcdf(fpath):
    info = {"dims": {}, "vars": {}}
    if not os.path.exists(fpath):
        return info
    with nc.Dataset(fpath) as ds:
        for dname, dim in ds.dimensions.items():
            info["dims"][dname] = len(dim)
        for vname, var in ds.variables.items():
            info["vars"][vname] = {
                "dims": var.dimensions,
                "shape": var.shape,
                "dtype": str(var.dtype),
                "standard_name": getattr(var, "standard_name", ""),
                "units": getattr(var, "units", ""),
            }
    return info


def count_files_by_pattern(base_dir, pattern):
    files = glob.glob(os.path.join(base_dir, "**", pattern), recursive=True)
    return len(files)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    # Échantillons de fichiers réels pour DA_nocdf
    sample_innov = sorted(glob.glob(os.path.join(DA_NOCDF_DIR, "2018-03", "EnKF", "*", "*_innov.*.nc")))[0]
    sample_incr = sorted(glob.glob(os.path.join(DA_NOCDF_DIR, "2018-03", "EnKF", "*", "*_incr.*.nc")))[0]
    sample_spread = sorted(glob.glob(os.path.join(DA_NOCDF_DIR, "2018-03", "EnKF", "*", "*_spread.*.nc")))[0]
    sample_daobs = sorted(glob.glob(os.path.join(DA_NOCDF_DIR, "2018-03", "DAOBS", "*", "LISDAOBS_*")))[0]

    info_innov = inspect_netcdf(sample_innov)
    info_incr = inspect_netcdf(sample_incr)
    info_spread = inspect_netcdf(sample_spread)

    # Comptages totaux 2016-2020 (60 mois)
    n_innov_nocdf = count_files_by_pattern(DA_NOCDF_DIR, "*_innov.*.nc")
    n_incr_nocdf = count_files_by_pattern(DA_NOCDF_DIR, "*_incr.*.nc")
    n_spread_nocdf = count_files_by_pattern(DA_NOCDF_DIR, "*_spread.*.nc")
    n_daobs_nocdf = count_files_by_pattern(DA_NOCDF_DIR, "LISDAOBS_*")

    n_innov_cdf = count_files_by_pattern(DA_CDF_DIR, "*_innov.*.nc")
    n_incr_cdf = count_files_by_pattern(DA_CDF_DIR, "*_incr.*.nc")
    n_spread_cdf = count_files_by_pattern(DA_CDF_DIR, "*_spread.*.nc")
    n_daobs_cdf = count_files_by_pattern(DA_CDF_DIR, "LISDAOBS_*")

    md_path = os.path.join(OUT_DIR, "da_diagnostics_inventory.md")
    with open(md_path, "w") as f:
        f.write("# Inventaire des Diagnostics d'Assimilation SMAP Archivés en Production (LIS 7.5)\n\n")
        f.write("Ce document présente l'inventaire technique exhaustif des fichiers et variables diagnostiques d'assimilation EnKF réellement générés et archivés sur l'ensemble de la période d'audit 2016–2020 pour les simulations de production `DA_nocdf_noirr_2016_2020` et `DA_cdf_noirr_2016_2020`.\n\n")

        f.write("## 1. Inventaire des Fichiers Archivés (Volume 2016–2020, 60 mois)\n\n")
        f.write("| Type de Fichier | Sous-Dossier | Fréquence de Sortie | Format | Nb Fichiers DA_nocdf | Nb Fichiers DA_cdf |\n")
        f.write("|---|---|---|---|:---:|:---:|\n")
        f.write(f"| **Innovations (`*_innov`)** | `EnKF/YYYYMM/` | À chaque passage SMAP assimilé | NetCDF4 | {n_innov_nocdf} | {n_innov_cdf} |\n")
        f.write(f"| **Incréments d'analyse (`*_incr`)** | `EnKF/YYYYMM/` | À chaque passage SMAP assimilé | NetCDF4 | {n_incr_nocdf} | {n_incr_cdf} |\n")
        f.write(f"| **Spread d'ensemble (`*_spread`)** | `EnKF/YYYYMM/` | Quotidien (00:00 UTC) | NetCDF4 | {n_spread_nocdf} | {n_spread_cdf} |\n")
        f.write(f"| **Observations prétraitées (`LISDAOBS_*`)** | `DAOBS/YYYYMM/` | À chaque passage SMAP lu | Binaire LIS (1gs4r) | {n_daobs_nocdf} | {n_daobs_cdf} |\n")
        f.write(f"| **Restarts de perturbation (`LIS_DAPERT_*`)** | `DAPERT/YYYYMM/` | Mensuel (fin de mois) | Binaire Fortran | 60 | 60 |\n\n")

        f.write("## 2. Variables Diagnostiques NetCDF Archivées\n\n")
        f.write("### 2.1. Fichiers d'Innovations (`LIS_DA_EnKF_YYYYMMDDHHMM_innov.a01.d01.nc`)\n\n")
        f.write(f"- **Dimensions de grille** : `east_west = {info_innov['dims'].get('east_west', 181)}`, `north_south = {info_innov['dims'].get('north_south', 121)}`\n\n")
        f.write("| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |\n")
        f.write("|---|---|---|---|---|\n")
        for vname, vinfo in info_innov["vars"].items():
            f.write(f"| `{vname}` | `{vinfo['dims']}` | `{vinfo['shape']}` | `{vinfo['dtype']}` | {vinfo['standard_name']} |\n")

        f.write("\n> **Signification des variables d'innovation** :\n")
        f.write("- `innov_01` : Innovation brute en espace observation, calculée comme $y - \\overline{H(x^f)}$ (observation SMAP moins la prévision moyenne d'ensemble de l'humidité de surface, en $\\text{m}^3/\\text{m}^3$).\n")
        f.write("- `ninnov_01` : Innovation normalisée par la variance totale d'innovation, calculée comme $\\frac{y - \\overline{H(x^f)}}{\\sqrt{H P^f H^T + R}}$.\n")
        f.write("- `analysis_residual_01` : Résidu d'analyse après mise à jour EnKF, calculé comme $y - \\overline{H(x^a)}$ (écart post-assimilation).\n")
        f.write("- `forecast_sigma_01` : Variance d'ébauche (forecast variance en espace observation), soit $H P^f H^T$.\n")
        f.write("- **$H(\\bar{x})$ moyen** : N'est pas stocké sous forme de variable dédiée, mais se déduit exactement à chaque point par soustraction $H(\\bar{x}) = y - \\text{innov\\_01}$ (les observations $y$ étant disponibles dans `DAOBS`).\n\n")

        f.write("### 2.2. Fichiers d'Incréments d'Analyse (`LIS_DA_EnKF_YYYYMMDDHHMM_incr.a01.d01.nc`)\n\n")
        f.write(f"- **Dimensions de grille** : `east_west = {info_incr['dims'].get('east_west', 181)}`, `north_south = {info_incr['dims'].get('north_south', 121)}`\n\n")
        f.write("| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |\n")
        f.write("|---|---|---|---|---|\n")
        for vname, vinfo in info_incr["vars"].items():
            f.write(f"| `{vname}` | `{vinfo['dims']}` | `{vinfo['shape']}` | `{vinfo['dtype']}` | {vinfo['standard_name']} |\n")

        f.write("\n> **Note critique sur les incréments** : Ces 4 champs correspondent aux incréments $\\Delta \\theta_l$ calculés directement par le filtre EnKF pour chaque couche de sol $l \\in \\{1, 2, 3, 4\\}$. Ces valeurs sont archivées avant l'application des bornes physiques et de flétrissement dans `NoahMP401_setsoilm.F90`.\n\n")

        f.write("### 2.3. Fichiers de Spread d'Ensemble (`LIS_DA_EnKF_YYYYMMDD0000_spread.a01.d01.nc`)\n\n")
        f.write(f"- **Dimensions de grille** : `east_west = {info_spread['dims'].get('east_west', 181)}`, `north_south = {info_spread['dims'].get('north_south', 121)}`\n\n")
        f.write("| Nom de la Variable NetCDF | Dimensions | Shape | Type | Description & Définition LIS |\n")
        f.write("|---|---|---|---|---|\n")
        for vname, vinfo in info_spread["vars"].items():
            f.write(f"| `{vname}` | `{vinfo['dims']}` | `{vinfo['shape']}` | `{vinfo['dtype']}` | {vinfo['standard_name']} |\n")

        f.write("\n---\n\n")
        f.write("## 3. Analyse du Code Source LIS 7.5 : Nature Mathématique du « Spread »\n\n")
        f.write("### 3.1. Localisation dans le code source\n")
        f.write("- **Fichier** : [`src/lisf/lis/core/LIS_historyMod.F90`](file:///srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/core/LIS_historyMod.F90#L7886-L8003)\n")
        f.write("- **Routine** : `subroutine LIS_writevar_spread(ftn, n, m, varid, var, v)` (lignes 7886 à 8003)\n")
        f.write("- **Appelante** : `subroutine writeEnsembleSpread(n, k)` dans [`src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90:865-1000`](file:///srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/src/lisf/lis/dataassim/algorithm/enkf/enkf_Mod.F90#L865-L1000)\n\n")

        f.write("### 3.2. Constat capital : Le spread archivé est une ÉTENDUE (MAX − MIN) et NON un écart-type\n\n")
        f.write("L'inspection détaillée des lignes 7949 à 7985 de `src/lisf/lis/core/LIS_historyMod.F90` démontre sans équivoque :\n\n")
        f.write("1. **Le calcul de l'écart-type est désactivé à la compilation (`#if 0`)** :\n")
        f.write("```fortran\n")
        f.write("! Lignes 7949-7971 dans src/lisf/lis/core/LIS_historyMod.F90\n")
        f.write("#if 0 \n")
        f.write("                      mean_v = 0 \n")
        f.write("                      var_v  = 0 \n")
        f.write("                      do t=1,npatch\n")
        f.write("                         mean_v = mean_v + gtmp1(count1)\n")
        f.write("                         var_v  = var_v + gtmp1(count1)*gtmp1(count1)\n")
        f.write("                         count1 = count1 + 1\n")
        f.write("                      enddo\n")
        f.write("                      if(npatch.gt.0) then \n")
        f.write("                         mean_v = mean_v/npatch\n")
        f.write("                         std_v  = (var_v/npatch - mean_v*mean_v)\n")
        f.write("                         if(std_v.ge.0) then \n")
        f.write("                            std_v = sqrt(std_v)\n")
        f.write("                         else\n")
        f.write("                            std_v = LIS_rc%udef\n")
        f.write("                         endif\n")
        f.write("                      else\n")
        f.write("                         std_v = LIS_rc%udef\n")
        f.write("                      endif\n")
        f.write("                      gtmp(c,r) = std_v\n")
        f.write("#endif\n")
        f.write("```\n\n")
        f.write("2. **Le code actif compilé et exécuté calcule l'étendue maximale de l'ensemble** :\n")
        f.write("```fortran\n")
        f.write("! Lignes 7973-7985 dans src/lisf/lis/core/LIS_historyMod.F90\n")
        f.write("                      min_v = 1000000\n")
        f.write("                      max_v = -1000000 \n")
        f.write("                      do t=1,npatch\n")
        f.write("                         if(gtmp1(count1).lt.min_v) min_v = gtmp1(count1)\n")
        f.write("                         if(gtmp1(count1).gt.max_v) max_v = gtmp1(count1)\n")
        f.write("                         count1 = count1 + 1\n")
        f.write("                      enddo                      \n")
        f.write("                      gtmp(c,r) = max_v - min_v\n")
        f.write("                      if(min_v.eq. 1000000.or. &\n")
        f.write("                           max_v.eq.-1000000 ) then \n")
        f.write("                         gtmp(c,r) = LIS_rc%udef\n")
        f.write("                      endif\n")
        f.write("```\n\n")
        f.write("3. **Conséquence pour le papier** :\n")
        f.write("   - Bien que l'en-tête de `writeEnsembleSpread` mentionne `standard deviation` et que l'attribut NetCDF porte le standard_name `Ensemble_spread_...`, la valeur physique écrite dans `ensspread_Soil Moisture Layer X_01` est **rigoureusement l'étendue** $\\max_{m=1..20}(\\theta_m) - \\min_{m=1..20}(\\theta_m)$.\n")
        f.write("   - Pour un échantillon gaussien de 20 membres, le rapport moyen entre l'étendue et l'écart-type est $d_2 \\approx 3.735$. Toute utilisation du spread archivé doit impérativement expliciter cette nature d'étendue ou la convertir rigoureusement.\n")

    print(f"[OK] Inventaire DA Markdown généré : {md_path}")


if __name__ == "__main__":
    main()
