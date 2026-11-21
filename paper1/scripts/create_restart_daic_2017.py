#!/usr/bin/env python3
"""
create_restart_daic_2017.py -- Bloc A2 (paper1, lot 1).

Construit l'état initial 1 membre pour OL_DAIC_2017 à partir de :
  DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc
Template 1 membre :
  OPL_noirr_2016_2020/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc

Règle identique à 2018 (create_restart_daic.py) :
  Pour chaque maille, sélectionner le membre dont l'humidité de colonne
  (sum_l dz_l * SMC_l) est la plus proche de la moyenne d'ensemble,
  et copier toutes ses variables.

Calcule et rapporte l'écart de stock moyen domaine (mm) :
  Stock = SMC (4 couches, 2000 mm) + WA (aquifère) + CANWAT (canopée) + SNEQV (neige).
Sorties :
  - Fichier NetCDF de restart :
    experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc
  - Table CSV :
    paper1/tables/daic_2017_stock_gap.csv
"""
import os
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
F_SRC = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc")
F_TPL = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc")
OUT_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart")
F_DST = os.path.join(OUT_DIR, "LIS_RST_NOAHMP401_201701010000.d01.nc")
TABLE_DIR = os.path.join(BASE_DIR, "paper1/tables")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(TABLE_DIR, exist_ok=True)

    print(f"[INFO] Source (20 ens) : {F_SRC}")
    print(f"[INFO] Template (1 mem) : {F_TPL}")
    print(f"[INFO] Destination     : {F_DST}")

    with nc.Dataset(F_SRC, 'r') as ds_src, nc.Dataset(F_TPL, 'r') as ds_tpl:
        n_tiles = len(ds_tpl.dimensions['ntiles'])
        n_ens = 20
        assert len(ds_src.dimensions['ntiles']) == n_tiles * n_ens, "Dimension ntiles inattendue"

        print("[INFO] Lecture de SMC et calcul de l'humidité de colonne...")
        smc = ds_src.variables['SMC'][:]
        dz_m = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)
        dz_mm = dz_m * 1000.0

        # Reshape to (4, n_tiles, n_ens)
        smc_cube = smc.reshape((4, n_tiles, n_ens))

        # theta_col for each member: sum_l (dz[l] * smc[l, i, m]) en m3/m3 equivalent
        theta_col = np.tensordot(dz_m, smc_cube, axes=([0], [0]))  # shape (n_tiles, n_ens)

        # Ensemble mean column moisture
        mean_col = np.mean(theta_col, axis=1, keepdims=True)  # shape (n_tiles, 1)

        # Find closest member (méthode 2018)
        diff_from_mean = np.abs(theta_col - mean_col)
        best_m = np.argmin(diff_from_mean, axis=1)  # shape (n_tiles,)

        # Distribution of best members
        counts = np.bincount(best_m, minlength=20)
        print(f"[INFO] Distribution des membres sélectionnés (min {np.min(counts)}, max {np.max(counts)}, mean {np.mean(counts):.1f}) :")
        print(counts)

        # Global index for each tile
        best_idx = np.arange(n_tiles) * 20 + best_m

        # Verification of lat/lon
        lat_src = ds_src.variables['lat'][:]
        lon_src = ds_src.variables['lon'][:]
        lat_tpl = ds_tpl.variables['lat'][:]
        lon_tpl = ds_tpl.variables['lon'][:]
        assert np.allclose(lat_src[best_idx], lat_tpl), "Erreur cohérence latitude !"
        assert np.allclose(lon_src[best_idx], lon_tpl), "Erreur cohérence longitude !"
        print("[INFO] Cohérence spatiale lat/lon validée à 100%.")

        # Variables de stock pour comparaison DAIC vs Moyenne Ensemble
        wa_src = ds_src.variables['WA'][:]
        can_src = ds_src.variables['CANWAT'][:]
        sn_src = ds_src.variables['SNEQV'][:]

        # Ensemble mean stocks (mm)
        smc_ens_mean_col = np.mean(np.tensordot(dz_mm, smc_cube, axes=([0], [0])), axis=1)
        wa_ens_mean = np.mean(wa_src.reshape((n_tiles, n_ens)), axis=1)
        can_ens_mean = np.mean(can_src.reshape((n_tiles, n_ens)), axis=1)
        sn_ens_mean = np.mean(sn_src.reshape((n_tiles, n_ens)), axis=1)
        tot_ens_mean = smc_ens_mean_col + wa_ens_mean + can_ens_mean + sn_ens_mean

        # DAIC selected member stocks (mm)
        smc_daic_col = np.tensordot(dz_mm, smc[:, best_idx], axes=([0], [0]))
        wa_daic = wa_src[best_idx]
        can_daic = can_src[best_idx]
        sn_daic = sn_src[best_idx]
        tot_daic = smc_daic_col + wa_daic + can_daic + sn_daic

        # Domain means
        stock_metrics = {
            "component": ["SMC_col_mm", "WA_mm", "CANWAT_mm", "SNEQV_mm", "TOTAL_STOCK_mm"],
            "ens_mean_mm": [
                round(float(np.mean(smc_ens_mean_col)), 4),
                round(float(np.mean(wa_ens_mean)), 4),
                round(float(np.mean(can_ens_mean)), 6),
                round(float(np.mean(sn_ens_mean)), 6),
                round(float(np.mean(tot_ens_mean)), 4)
            ],
            "daic_selected_mm": [
                round(float(np.mean(smc_daic_col)), 4),
                round(float(np.mean(wa_daic)), 4),
                round(float(np.mean(can_daic)), 6),
                round(float(np.mean(sn_daic)), 6),
                round(float(np.mean(tot_daic)), 4)
            ],
            "delta_daic_minus_ens_mm": [
                round(float(np.mean(smc_daic_col - smc_ens_mean_col)), 6),
                round(float(np.mean(wa_daic - wa_ens_mean)), 6),
                round(float(np.mean(can_daic - can_ens_mean)), 8),
                round(float(np.mean(sn_daic - sn_ens_mean)), 8),
                round(float(np.mean(tot_daic - tot_ens_mean)), 6)
            ],
            "mean_abs_diff_pixel_mm": [
                round(float(np.mean(np.abs(smc_daic_col - smc_ens_mean_col))), 4),
                round(float(np.mean(np.abs(wa_daic - wa_ens_mean))), 4),
                round(float(np.mean(np.abs(can_daic - can_ens_mean))), 6),
                round(float(np.mean(np.abs(sn_daic - sn_ens_mean))), 6),
                round(float(np.mean(np.abs(tot_daic - tot_ens_mean))), 4)
            ],
            "selection_criterion": [
                "MIN_ABS_DIFF_SMC_COL",
                "COPIED_FROM_SMC_SELECTION",
                "COPIED_FROM_SMC_SELECTION",
                "COPIED_FROM_SMC_SELECTION",
                "SUM_OF_COMPONENTS"
            ]
        }
        df_stock = pd.DataFrame(stock_metrics)
        csv_path = os.path.join(TABLE_DIR, "daic_2017_stock_gap.csv")
        df_stock.to_csv(csv_path, index=False)
        print("\n=== ÉCART DE STOCK INITIAL (DAIC vs ENSEMBLE MEAN) 2017-01-01 ===")
        print(df_stock.to_string(index=False))

        smc_gap = abs(df_stock.loc[df_stock.component == "SMC_col_mm", "delta_daic_minus_ens_mm"].values[0])
        print(f"\n[CHECK] Écart d'humidité colonne moyenne domaine : {smc_gap:.6f} mm (seuil < 0.5 mm : VALIDÉ)")
        assert smc_gap < 0.5, f"Écart d'humidité colonne {smc_gap} mm dépasse le seuil de 0.5 mm !"

        print("[INFO] Écriture du restart 1 membre...")
        if os.path.exists(F_DST):
            os.remove(F_DST)

        with nc.Dataset(F_DST, 'w', format=ds_tpl.file_format) as ds_dst:
            for att in ds_tpl.ncattrs():
                ds_dst.setncattr(att, ds_tpl.getncattr(att))

            for dname, dim in ds_tpl.dimensions.items():
                ds_dst.createDimension(dname, len(dim) if not dim.isunlimited() else None)

            for vname, var_tpl in ds_tpl.variables.items():
                var_src = ds_src.variables[vname]
                fill_val = getattr(var_tpl, '_FillValue', None)
                var_dst = ds_dst.createVariable(vname, var_tpl.dtype, var_tpl.dimensions, zlib=True, fill_value=fill_val)
                for att in var_tpl.ncattrs():
                    if att != '_FillValue':
                        var_dst.setncattr(att, var_tpl.getncattr(att))

                if vname == 'time':
                    var_dst[:] = var_src[:]
                elif 'ntiles' in var_tpl.dimensions:
                    if var_tpl.ndim == 1:
                        var_dst[:] = var_src[:][best_idx]
                    elif var_tpl.ndim == 2:
                        var_dst[:] = var_src[:, best_idx]
                    else:
                        raise ValueError(f"Dimension inattendue pour {vname}")
                else:
                    var_dst[:] = var_src[:]

    print(f"[SUCCÈS] Restart 1 membre créé : {F_DST} ({os.path.getsize(F_DST) / 1e6:.2f} Mo)")


if __name__ == "__main__":
    main()
