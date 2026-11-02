#!/usr/bin/env python3
# scripts/check_cntime_floor.py
# Recalcul indépendant de l'effet plancher cntime dans HyMAP2.
# Audit de cohérence (Point A) pour la branche hymap-routing.

import os
import sys
import numpy as np
import netCDF4 as nc

DEFAULT_NETCDF = "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"

def get_stats(arr):
    arr_clean = arr.compressed() if isinstance(arr, np.ma.MaskedArray) else np.asarray(arr)
    return {
        "min": float(np.min(arr_clean)),
        "p10": float(np.percentile(arr_clean, 10)),
        "med": float(np.median(arr_clean)),
        "p90": float(np.percentile(arr_clean, 90)),
        "max": float(np.max(arr_clean)),
        "mean": float(np.mean(arr_clean)),
    }

def print_stats_row(name, stats, unit=""):
    print(f"{name:<28s} | {stats['min']:10.4f} | {stats['p10']:10.4f} | {stats['med']:10.4f} | {stats['p90']:10.4f} | {stats['max']:10.4f} | {unit}")

def main():
    nc_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_NETCDF
    if not os.path.exists(nc_path):
        print(f"[ERREUR] Fichier introuvable : {nc_path}")
        sys.exit(1)

    print("=" * 95)
    print(f"AUDIT DU PLANCHER CNTIME — HYMAP2 (Fichier : {nc_path})")
    print("=" * 95)

    with nc.Dataset(nc_path, 'r') as ds:
        if "HYMAP_basin_mask" not in ds.variables:
            print("[ERREUR] Variable HYMAP_basin_mask absente du fichier NetCDF.")
            sys.exit(1)

        mask_raw = ds.variables["HYMAP_basin_mask"][:]
        active_mask = (mask_raw > 0)
        n_total = mask_raw.size
        n_active = int(np.sum(active_mask))
        print(f"Critere de maille active : HYMAP_basin_mask > 0")
        print(f"Dimensions de grille      : {mask_raw.shape} ({n_total} cellules)")
        print(f"Nombre de mailles actives : {n_active} sur {n_total} ({n_active / n_total * 100:.2f} %)")

        tbsflw_var = ds.variables["HYMAP_baseflow_time_delay"]
        cntime_var = ds.variables["HYMAP_runoff_time_delay"]
        trnoff_var = ds.variables["HYMAP_runoff_time_delay_multiplier"]

        tbsflw = tbsflw_var[:][active_mask]
        cntime = cntime_var[:][active_mask]
        trnoff = trnoff_var[:][active_mask]

        tbsflw_units = getattr(tbsflw_var, "units", "none")
        cntime_units = getattr(cntime_var, "units", "none")
        trnoff_units = getattr(trnoff_var, "units", "none")

        print("")
        print(f"Variables lues (attributs units) :")
        print(f"  HYMAP_baseflow_time_delay         : units = '{tbsflw_units}'")
        print(f"  HYMAP_runoff_time_delay           : units = '{cntime_units}'")
        print(f"  HYMAP_runoff_time_delay_multiplier: units = '{trnoff_units}'")

        plancher = cntime / 86400.0
        cond_floor = (tbsflw < plancher) & (cntime > 0)
        n_clipped = int(np.sum(cond_floor))
        pct_clipped = n_clipped / n_active * 100.0

        tbsflw_eff = np.where(cond_floor, plancher, tbsflw)

        print("")
        print(f"Resultat du test plancher (tbsflw < cntime/86400 et cntime > 0) :")
        print(f"  Mailles ecretees par le plancher : {n_clipped} / {n_active} ({pct_clipped:.4f} %)")
        print(f"  Mailles conservant tbsflw brut  : {n_active - n_clipped} / {n_active} ({100.0 - pct_clipped:.4f} %)")

        print("")
        print(f"Tableau des distributions statistiques (sur {n_active} mailles actives) :")
        print("-" * 95)
        print(f"{'Grandeur / Variable':<28s} | {'Min':>10s} | {'P10':>10s} | {'Mediane':>10s} | {'P90':>10s} | {'Max':>10s} | Unite")
        print("-" * 95)
        print_stats_row("tbsflw (fourni corrige)", get_stats(tbsflw), "jours")
        print_stats_row("cntime (brut LISF)", get_stats(cntime), "secondes")
        print_stats_row("plancher (cntime / 86400)", get_stats(plancher), "jours")
        print_stats_row("tbsflw_eff (effectif LISF)", get_stats(tbsflw_eff), "jours")
        print_stats_row("trnoff (multiplicateur)", get_stats(trnoff), "[-]")
        print("-" * 95)

if __name__ == '__main__':
    main()
