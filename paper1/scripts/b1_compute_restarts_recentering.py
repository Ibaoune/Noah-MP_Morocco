#!/usr/bin/env python3
"""
b1_compute_restarts_recentering.py

Analyse empirique des restarts au niveau membre pour :
- ENS_OPL_2018 (restarts mensuelles et finale 201901010000)
- ENS_STATE_201803 (201803312345 et 201804010000)
Comparaison avec Member 20 (membre non perturbé) et avec OL_DAIC_2018.

Métriques calculées sur chaque restart :
1. Écart entre moyenne d'ensemble et Membre 20 (ens_mean - mem20) pour SH2O (couches 1 à 4) et WA.
2. Écart entre Membre 20 et OL_DAIC (mem20 - ol_daic) pour SH2O (couches 1 à 4) et WA.
3. Dispersion d'ensemble de SH2O par couche (écart-type moyen et étendue moyenne max - min).

Sortie : paper1/tables/recentering_check_restarts.csv
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018")
OUT_CSV  = os.path.join(BASE_DIR, "paper1/tables/recentering_check_restarts.csv")

def analyze_restart(ens_run, ens_fp, ol_fp=None):
    fname = os.path.basename(ens_fp)
    date_str = fname.replace("LIS_RST_NOAHMP401_", "").replace(".d01.nc", "")
    
    with nc.Dataset(ens_fp) as ds:
        sh2o = ds.variables['SH2O'][:] # (4, 320600)
        wa   = ds.variables['WA'][:]   # (320600,)
        n_tiles = 16030
        n_ens = 20
        
        sh2o_cube = sh2o.reshape(4, n_tiles, n_ens) # (4, tiles, ens)
        wa_cube   = wa.reshape(n_tiles, n_ens)
        
        sh2o_mean = sh2o_cube.mean(axis=2) # (4, tiles)
        wa_mean   = wa_cube.mean(axis=1)   # (tiles,)
        
        # Member 20 is index 19 (0-indexed)
        sh2o_m20  = sh2o_cube[:, :, 19]
        wa_m20    = wa_cube[:, 19]
        
        # 1. Ens Mean - Member 20
        d_ens_m20_sh2o = sh2o_mean - sh2o_m20
        d_ens_m20_wa   = wa_mean - wa_m20
        
        # 2. Dispersion (std and range)
        sh2o_std   = sh2o_cube.std(axis=2) # (4, tiles)
        sh2o_range = sh2o_cube.max(axis=2) - sh2o_cube.min(axis=2)
        
    # 3. Member 20 vs OL_DAIC
    has_ol = ol_fp is not None and os.path.exists(ol_fp)
    if has_ol:
        with nc.Dataset(ol_fp) as ds_ol:
            sh2o_ol = ds_ol.variables['SH2O'][:] # (4, 16030)
            wa_ol   = ds_ol.variables['WA'][:]   # (16030,)
            d_m20_ol_sh2o = sh2o_m20 - sh2o_ol
            d_m20_ol_wa   = wa_m20 - wa_ol
    else:
        d_m20_ol_sh2o = None
        d_m20_ol_wa   = None

    row = {
        'run': ens_run,
        'restart_file': fname,
        'date': date_str,
        'has_matching_ol_daic': has_ol,
        'same_ic_as_ol_daic': "NON (composite DAIC)" if has_ol else "N/A"
    }
    
    # Layer metrics
    for l in range(4):
        lay = l + 1
        # Ens mean - M20
        row[f'sh2o_l{lay}_ens_minus_m20_mean'] = float(np.mean(d_ens_m20_sh2o[l]))
        row[f'sh2o_l{lay}_ens_minus_m20_maxabs'] = float(np.max(np.abs(d_ens_m20_sh2o[l])))
        
        # Dispersion
        row[f'sh2o_l{lay}_std_mean'] = float(np.mean(sh2o_std[l]))
        row[f'sh2o_l{lay}_range_mean'] = float(np.mean(sh2o_range[l]))
        
        # M20 - OL_DAIC
        if has_ol:
            row[f'sh2o_l{lay}_m20_minus_ol_mean'] = float(np.mean(d_m20_ol_sh2o[l]))
            row[f'sh2o_l{lay}_m20_minus_ol_maxabs'] = float(np.max(np.abs(d_m20_ol_sh2o[l])))
        else:
            row[f'sh2o_l{lay}_m20_minus_ol_mean'] = np.nan
            row[f'sh2o_l{lay}_m20_minus_ol_maxabs'] = np.nan

    # WA metrics
    row['wa_ens_minus_m20_mean'] = float(np.mean(d_ens_m20_wa))
    row['wa_ens_minus_m20_maxabs'] = float(np.max(np.abs(d_ens_m20_wa)))
    row['wa_std_mean'] = float(np.mean(wa_cube.std(axis=1)))
    row['wa_range_mean'] = float(np.mean(wa_cube.max(axis=1) - wa_cube.min(axis=1)))
    
    if has_ol:
        row['wa_m20_minus_ol_mean'] = float(np.mean(d_m20_ol_wa))
        row['wa_m20_minus_ol_maxabs'] = float(np.max(np.abs(d_m20_ol_wa)))
    else:
        row['wa_m20_minus_ol_mean'] = np.nan
        row['wa_m20_minus_ol_maxabs'] = np.nan
        
    return row

def main():
    rows = []
    
    # 1. ENS_STATE_201803 restarts
    stat_dir = os.path.join(SENS_DIR, "ENS_STATE_201803/output/SURFACEMODEL")
    stat_rsts = sorted(glob.glob(f"{stat_dir}/*/LIS_RST_NOAHMP401_*.d01.nc"))
    
    for rst in stat_rsts:
        fname = os.path.basename(rst)
        ym = fname[18:24]
        # Matching OL_DAIC restart
        ol_cand = os.path.join(SENS_DIR, f"OL_DAIC_2018/output/SURFACEMODEL/{ym}/{fname}")
        row = analyze_restart("ENS_STATE_201803", rst, ol_cand if os.path.exists(ol_cand) else None)
        rows.append(row)
        
    # 2. ENS_OPL_2018 restarts
    opl_dir = os.path.join(SENS_DIR, "ENS_OPL_2018/output/SURFACEMODEL")
    opl_rsts = sorted(glob.glob(f"{opl_dir}/*/LIS_RST_NOAHMP401_*.d01.nc"))
    
    for rst in opl_rsts:
        fname = os.path.basename(rst)
        ym = fname[18:24]
        ol_cand = os.path.join(SENS_DIR, f"OL_DAIC_2018/output/SURFACEMODEL/{ym}/{fname}")
        row = analyze_restart("ENS_OPL_2018", rst, ol_cand if os.path.exists(ol_cand) else None)
        rows.append(row)
        
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"[OK] Table générée : {OUT_CSV}")

if __name__ == "__main__":
    main()
