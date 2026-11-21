#!/usr/bin/env python3
"""
c2_verify_noryu_restarts.py

Preuve de la lecture de pert_bias_corr = 0 dans les runs noRyu au 31-03-2018 23:45 :
1. Comparaison membre 20 de ENS_STATE_201803_noRyu vs ENS_STATE_201803 sur SH2O couche 1.
2. Calcul de la moyenne d'ensemble moins membre 20 dans ENS_STATE_201803_noRyu et ENS_FORC_201803_noRyu
   au même format que recentering_check_restarts.csv.

Sorties :
- paper1/tables/m20_noryu_comparison.csv
- paper1/tables/recentering_check_noRyu_restarts.csv
"""

import os
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018")
OUT_M20_CSV = os.path.join(BASE_DIR, "paper1/tables/m20_noryu_comparison.csv")
OUT_REC_CSV = os.path.join(BASE_DIR, "paper1/tables/recentering_check_noRyu_restarts.csv")

def check_m20_difference():
    fp_with_ryu = os.path.join(SENS_DIR, "ENS_STATE_201803/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
    fp_no_ryu   = os.path.join(SENS_DIR, "ENS_STATE_201803_noRyu/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
    
    if not os.path.exists(fp_no_ryu):
        print(f"[WAIT] {fp_no_ryu} not yet ready.")
        return False
        
    n_tiles = 16030
    n_ens = 20
    
    with nc.Dataset(fp_with_ryu) as ds_w, nc.Dataset(fp_no_ryu) as ds_no:
        sh2o_w  = ds_w.variables['SH2O'][:].reshape(4, n_tiles, n_ens)
        sh2o_no = ds_no.variables['SH2O'][:].reshape(4, n_tiles, n_ens)
        
        # Member 20 (index 19)
        m20_w_l1  = sh2o_w[0, :, 19]
        m20_no_l1 = sh2o_no[0, :, 19]
        
        diff = m20_no_l1 - m20_w_l1
        abs_diff = np.abs(diff)
        
        row = {
            'comparison': 'ENS_STATE_201803_noRyu_m20 vs ENS_STATE_201803_m20',
            'variable': 'SH2O_layer_1',
            'date': '2018-03-31 23:45',
            'm20_withRyu_mean': float(np.mean(m20_w_l1)),
            'm20_noRyu_mean': float(np.mean(m20_no_l1)),
            'mean_diff': float(np.mean(diff)),
            'mean_abs_diff': float(np.mean(abs_diff)),
            'max_abs_diff': float(np.max(abs_diff)),
            'n_tiles_total': int(n_tiles),
            'n_tiles_different': int(np.sum(abs_diff > 1e-6)),
            'are_different': bool(np.max(abs_diff) > 1e-6)
        }
        
    df = pd.DataFrame([row])
    os.makedirs(os.path.dirname(OUT_M20_CSV), exist_ok=True)
    df.to_csv(OUT_M20_CSV, index=False)
    print(f"[OK] M20 comparison written to {OUT_M20_CSV}")
    print(df.to_string(index=False))
    return True

def compute_recentering_noRyu():
    runs = [
        ("ENS_STATE_201803_noRyu", os.path.join(SENS_DIR, "ENS_STATE_201803_noRyu/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")),
        ("ENS_FORC_201803_noRyu",  os.path.join(SENS_DIR, "ENS_FORC_201803_noRyu/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc"))
    ]
    
    ol_fp = os.path.join(SENS_DIR, "OL_DAIC_2018/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
    has_ol = os.path.exists(ol_fp)
    if has_ol:
        with nc.Dataset(ol_fp) as ds_ol:
            sh2o_ol = ds_ol.variables['SH2O'][:]
            wa_ol   = ds_ol.variables['WA'][:]
    else:
        sh2o_ol = wa_ol = None
        
    rows = []
    n_tiles = 16030
    n_ens = 20
    
    for rname, rst_fp in runs:
        if not os.path.exists(rst_fp):
            print(f"[WAIT] {rst_fp} not ready.")
            continue
        fname = os.path.basename(rst_fp)
        with nc.Dataset(rst_fp) as ds:
            sh2o = ds.variables['SH2O'][:]
            wa   = ds.variables['WA'][:]
            
            sh2o_cube = sh2o.reshape(4, n_tiles, n_ens)
            wa_cube   = wa.reshape(n_tiles, n_ens)
            
            sh2o_mean = sh2o_cube.mean(axis=2)
            wa_mean   = wa_cube.mean(axis=1)
            sh2o_m20  = sh2o_cube[:, :, 19]
            wa_m20    = wa_cube[:, 19]
            
            d_ens_m20_sh2o = sh2o_mean - sh2o_m20
            d_ens_m20_wa   = wa_mean - wa_m20
            
            sh2o_std   = sh2o_cube.std(axis=2)
            sh2o_range = sh2o_cube.max(axis=2) - sh2o_cube.min(axis=2)
            
            if has_ol:
                d_m20_ol_sh2o = sh2o_m20 - sh2o_ol
                d_m20_ol_wa   = wa_m20 - wa_ol
            else:
                d_m20_ol_sh2o = d_m20_ol_wa = None

            row = {
                'run': rname,
                'restart_file': fname,
                'date': '201803312345',
                'has_matching_ol_daic': has_ol,
                'same_ic_as_ol_daic': "NON (composite DAIC)" if has_ol else "N/A"
            }
            
            for l in range(4):
                lay = l + 1
                row[f'sh2o_l{lay}_ens_minus_m20_mean']   = float(np.mean(d_ens_m20_sh2o[l]))
                row[f'sh2o_l{lay}_ens_minus_m20_maxabs'] = float(np.max(np.abs(d_ens_m20_sh2o[l])))
                row[f'sh2o_l{lay}_std_mean']             = float(np.mean(sh2o_std[l]))
                row[f'sh2o_l{lay}_range_mean']           = float(np.mean(sh2o_range[l]))
                
                if has_ol:
                    row[f'sh2o_l{lay}_m20_minus_ol_mean']   = float(np.mean(d_m20_ol_sh2o[l]))
                    row[f'sh2o_l{lay}_m20_minus_ol_maxabs'] = float(np.max(np.abs(d_m20_ol_sh2o[l])))
                else:
                    row[f'sh2o_l{lay}_m20_minus_ol_mean'] = np.nan
                    row[f'sh2o_l{lay}_m20_minus_ol_maxabs'] = np.nan
                    
            row['wa_ens_minus_m20_mean']   = float(np.mean(d_ens_m20_wa))
            row['wa_ens_minus_m20_maxabs'] = float(np.max(np.abs(d_ens_m20_wa)))
            row['wa_std_mean']             = float(np.mean(wa_cube.std(axis=1)))
            row['wa_range_mean']           = float(np.mean(wa_cube.max(axis=1) - wa_cube.min(axis=1)))
            
            if has_ol:
                row['wa_m20_minus_ol_mean']   = float(np.mean(d_m20_ol_wa))
                row['wa_m20_minus_ol_maxabs'] = float(np.max(np.abs(d_m20_ol_wa)))
            else:
                row['wa_m20_minus_ol_mean'] = np.nan
                row['wa_m20_minus_ol_maxabs'] = np.nan
                
            rows.append(row)
            
    if rows:
        df = pd.DataFrame(rows)
        os.makedirs(os.path.dirname(OUT_REC_CSV), exist_ok=True)
        df.to_csv(OUT_REC_CSV, index=False)
        print(f"[OK] Recentering noRyu written to {OUT_REC_CSV}")
        print(df.to_string(index=False))
        return True
    return False

if __name__ == '__main__':
    ok1 = check_m20_difference()
    ok2 = compute_recentering_noRyu()
    if ok1 and ok2:
        print("[SUCCESS] Both noRyu restart verifications complete.")
    else:
        print("[NOTICE] One or more restarts not ready yet.")
