#!/usr/bin/env python3
"""
c3_analyze_da_15min_increments.py

Analyse systématique des 16 événements d'assimilation EnKF dans le run court 15-min
(DA_nocdf_diag_15min_2018Nov) :
Compare l'incrément archivé (_incr.nc) au changement réel appliqué à l'état du modèle
entre le pas immédiatement avant (T - 15 min) et le pas immédiatement après (T).

Sortie : paper1/tables/da_15min_applied_vs_archived_increments.csv
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
RUN_DIR  = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/output")
OUT_CSV  = os.path.join(BASE_DIR, "paper1/tables/da_15min_applied_vs_archived_increments.csv")

def parse_time_from_incr_file(fname):
    # LIS_DA_EnKF_201811010600_incr.a01.d01.nc
    parts = os.path.basename(fname).split('_')
    # parts[3] is '201811010600'
    t_str = parts[3]
    return datetime.datetime.strptime(t_str, "%Y%m%d%H%M")

def main():
    incr_files = sorted(glob.glob(f"{RUN_DIR}/EnKF/201811/LIS_DA_EnKF_*_incr.a01.d01.nc"))
    print(f"Trouvé {len(incr_files)} fichiers d'incréments EnKF.")
    
    rows = []
    
    for inc_f in incr_files:
        dt_da = parse_time_from_incr_file(inc_f)
        dt_pre = dt_da - datetime.timedelta(minutes=15)
        
        ym_da  = dt_da.strftime("%Y%m")
        f_post = os.path.join(RUN_DIR, f"SURFACEMODEL/{ym_da}/LIS_HIST_{dt_da.strftime('%Y%m%d%H%M')}.d01.nc")
        f_pre  = os.path.join(RUN_DIR, f"SURFACEMODEL/{ym_da}/LIS_HIST_{dt_pre.strftime('%Y%m%d%H%M')}.d01.nc")
        
        if not (os.path.exists(f_post) and os.path.exists(f_pre)):
            print(f"[SKIP] Fichiers historiques manquants pour {dt_da}")
            continue
            
        with nc.Dataset(inc_f) as ds_i, nc.Dataset(f_pre) as ds_pre, nc.Dataset(f_post) as ds_post:
            sm_pre  = ds_pre.variables['SoilMoist_inst'][:]   # (4, 121, 181)
            sm_post = ds_post.variables['SoilMoist_inst'][:]  # (4, 121, 181)
            
            delta_applied = sm_post - sm_pre # (4, 121, 181)
            
            for lay in range(1, 5):
                varname = f"anlys_incr_Soil Moisture Layer {lay}_01"
                if varname not in ds_i.variables:
                    continue
                raw_incr = ds_i.variables[varname][:] # (121, 181)
                
                # Valid mask
                valid_mask = (raw_incr > -10.0) & (raw_incr < 10.0)
                n_valid = int(np.sum(valid_mask))
                
                if n_valid > 0:
                    v_raw = raw_incr[valid_mask]
                    v_app = delta_applied[lay-1][valid_mask]
                    
                    mean_raw = float(np.mean(v_raw))
                    mean_abs_raw = float(np.mean(np.abs(v_raw)))
                    max_abs_raw = float(np.max(np.abs(v_raw)))
                    
                    mean_app = float(np.mean(v_app))
                    mean_abs_app = float(np.mean(np.abs(v_app)))
                    max_abs_app = float(np.max(np.abs(v_app)))
                    
                    # Correlation if std > 0
                    if np.std(v_raw) > 1e-9 and np.std(v_app) > 1e-9:
                        corr = float(np.corrcoef(v_raw, v_app)[0, 1])
                    else:
                        corr = np.nan
                else:
                    mean_raw = mean_abs_raw = max_abs_raw = np.nan
                    mean_app = mean_abs_app = max_abs_app = corr = np.nan
                    
                rows.append({
                    'timestamp': dt_da.strftime('%Y-%m-%d %H:%M'),
                    'layer': lay,
                    'n_assimilated_cells': n_valid,
                    'raw_incr_mean': mean_raw,
                    'raw_incr_mean_abs': mean_abs_raw,
                    'raw_incr_max_abs': max_abs_raw,
                    'applied_delta_mean': mean_app,
                    'applied_delta_mean_abs': mean_abs_app,
                    'applied_delta_max_abs': max_abs_app,
                    'corr_raw_vs_applied': corr
                })
                
    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    print(f"[OK] Table générée : {OUT_CSV}")
    print(df[df['layer'] == 1][['timestamp', 'n_assimilated_cells', 'raw_incr_mean', 'raw_incr_max_abs', 'applied_delta_mean', 'applied_delta_max_abs', 'corr_raw_vs_applied']].to_string(index=False))

if __name__ == '__main__':
    main()
