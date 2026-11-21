#!/usr/bin/env python3
"""
c1_compute_march2018_ryu_test.py

Génère la table comparative march2018_ryu_test.csv pour les 7 runs :
- OL_DAIC
- NOSTATE
- FORC
- STATE
- ENS
- STATE_noRyu
- FORC_noRyu

Pour chaque run :
- Bilan interne de mars 2018 : P_mm, ET_mm, Qs_mm, Qsb_mm, dStock_mm, Residu_mm
- Écart entre moyenne d'ensemble et membre 20 au 31 mars 2018 (SH2O couches 1-4, WA)
- Dispersion de SH2O par couche au 31 mars 2018 (écart-type moyen et étendue moyenne)

Règle : Les anciennes lignes sont relues depuis les CSV existants (sensitivity_internal_water_balance_201803.csv)
sans recalcul des flux 201803 existants.
Sortie : paper1/tables/march2018_ryu_test.csv
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR  = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao"
PARAM_NC  = os.path.join(BASE_DIR, "NoahMP_Morocco/data/lis_input/lis_input_NorthMor_5km.nc")
SENS_DIR  = os.path.join(BASE_DIR, "NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018")
AUDIT_CSV = os.path.join(BASE_DIR, "smap-xai-audit/reports/audits/diag2018_e6_clean/sensitivity_internal_water_balance_201803.csv")
OUT_CSV   = os.path.join(BASE_DIR, "NoahMP_Morocco/paper1/tables/march2018_ryu_test.csv")

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32) * 1000.0 # mm

with nc.Dataset(PARAM_NC) as ds:
    landmask = ds.variables['LANDMASK'][:].squeeze() > 0.5

def read_storage_ens(fp):
    with nc.Dataset(fp) as ds:
        smc = ds.variables['SMC'][:]
        wa = ds.variables['WA'][:]
        can = ds.variables['CANWAT'][:]
        sneqv = ds.variables['SNEQV'][:]
        n_ens = 20
        n_tiles = 16030
        
        smc_m = np.mean(smc.reshape(4, n_tiles, n_ens), axis=2)
        wa_m = np.mean(wa.reshape(n_tiles, n_ens), axis=1)
        can_m = np.mean(can.reshape(n_tiles, n_ens), axis=1)
        sn_m = np.mean(sneqv.reshape(n_tiles, n_ens), axis=1)
        
        smc_col = np.sum(smc_m * dz[:, None], axis=0)
        tot = smc_col + wa_m + can_m + sn_m
        return float(np.mean(tot))

def get_monthly_fluxes(base_out_dir):
    start_dt = datetime.datetime(2018, 3, 1)
    p_tot, et_tot, qs_tot, qsb_tot = 0.0, 0.0, 0.0, 0.0
    for d in range(31):
        dt_curr = start_dt + datetime.timedelta(days=d)
        dt_next = dt_curr + datetime.timedelta(days=1)
        ym_next = dt_next.strftime("%Y%m")
        d_next_str = dt_next.strftime("%Y%m%d")
        f = os.path.join(base_out_dir, f"SURFACEMODEL/{ym_next}/LIS_HIST_{d_next_str}0000.d01.nc")
        if not os.path.exists(f):
            return None # not complete
        with nc.Dataset(f) as ds:
            p_tot   += float(np.mean(ds.variables['TotalPrecip_tavg'][:].squeeze()[landmask] * 86400.0))
            et_tot  += float(np.mean(ds.variables['Evap_tavg'][:].squeeze()[landmask] * 86400.0))
            qs_tot  += float(np.mean(ds.variables['Qs_tavg'][:].squeeze()[landmask] * 86400.0))
            qsb_tot += float(np.mean(ds.variables['Qsb_tavg'][:].squeeze()[landmask] * 86400.0))
    return p_tot, et_tot, qs_tot, qsb_tot

def read_restart_dispersion(rst_fp, is_1m=False):
    if not os.path.exists(rst_fp):
        return None
    with nc.Dataset(rst_fp) as ds:
        sh2o = ds.variables['SH2O'][:]
        wa   = ds.variables['WA'][:]
        
        if is_1m:
            return {
                'sh2o_l1_ens_minus_m20_mean': 0.0,
                'sh2o_l2_ens_minus_m20_mean': 0.0,
                'sh2o_l3_ens_minus_m20_mean': 0.0,
                'sh2o_l4_ens_minus_m20_mean': 0.0,
                'wa_ens_minus_m20_mean': 0.0,
                'sh2o_l1_std_mean': 0.0,
                'sh2o_l2_std_mean': 0.0,
                'sh2o_l3_std_mean': 0.0,
                'sh2o_l4_std_mean': 0.0,
                'sh2o_l1_range_mean': 0.0,
                'sh2o_l2_range_mean': 0.0,
                'sh2o_l3_range_mean': 0.0,
                'sh2o_l4_range_mean': 0.0,
            }
            
        n_tiles = 16030
        n_ens = 20
        sh2o_cube = sh2o.reshape(4, n_tiles, n_ens)
        wa_cube   = wa.reshape(n_tiles, n_ens)
        
        sh2o_mean = sh2o_cube.mean(axis=2)
        wa_mean   = wa_cube.mean(axis=1)
        sh2o_m20  = sh2o_cube[:, :, 19]
        wa_m20    = wa_cube[:, 19]
        
        sh2o_std   = sh2o_cube.std(axis=2)
        sh2o_range = sh2o_cube.max(axis=2) - sh2o_cube.min(axis=2)
        
        res = {}
        for l in range(4):
            lay = l + 1
            res[f'sh2o_l{lay}_ens_minus_m20_mean'] = float(np.mean(sh2o_mean[l] - sh2o_m20[l]))
            res[f'sh2o_l{lay}_std_mean']           = float(np.mean(sh2o_std[l]))
            res[f'sh2o_l{lay}_range_mean']         = float(np.mean(sh2o_range[l]))
        res['wa_ens_minus_m20_mean'] = float(np.mean(wa_mean - wa_m20))
        return res

def main():
    # Read existing baseline from CSV
    df_old = pd.read_csv(AUDIT_CSV)
    old_wb_dict = {}
    for _, row in df_old.iterrows():
        r = row['run']
        old_wb_dict[r] = row.to_dict()
        
    run_defs = [
        ("OL_DAIC", "OL_DAIC_2018", "OL_DAIC_2018", True),
        ("NOSTATE", "ENS_NOSTATE_201803", "ENS_NOSTATE_201803", False),
        ("FORC", "ENS_FORC_201803", "ENS_FORC_201803", False),
        ("STATE", "ENS_STATE_201803", "ENS_STATE_201803", False),
        ("ENS", "ENS_OPL_2018", "ENS_OPL_2018", False),
        ("STATE_noRyu", "ENS_STATE_201803_noRyu", "ENS_STATE_201803_noRyu", False),
        ("FORC_noRyu", "ENS_FORC_201803_noRyu", "ENS_FORC_201803_noRyu", False)
    ]
    
    rows = []
    rst_start = os.path.join(SENS_DIR, "ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")
    
    for label, folder, old_key, is_1m in run_defs:
        row = {'run': label}
        rst_fp = os.path.join(SENS_DIR, f"{folder}/output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
        out_dir = os.path.join(SENS_DIR, f"{folder}/output")
        
        # 1. Water balance
        if old_key in old_wb_dict:
            wb = old_wb_dict[old_key]
            row['P_mm']       = wb['P_mm']
            row['ET_mm']      = wb['ET_mm']
            row['Qs_mm']      = wb['Qs_mm']
            row['Qsb_mm']     = wb['Qsb_mm']
            row['dStock_mm']  = wb['dStock_mm']
            row['Residu_mm']  = wb['Residu_mm']
            row['Stock_start_mm'] = wb['Stock_start_mm']
            row['Stock_end_mm']   = wb['Stock_end_mm']
            row['wb_status']  = "LOADED_FROM_CSV"
        else:
            # Need to compute if run finished
            if os.path.exists(rst_fp):
                fluxes = get_monthly_fluxes(out_dir)
                if fluxes is not None:
                    p, et, qs, qsb = fluxes
                    s_st = read_storage_ens(rst_start)
                    s_en = read_storage_ens(rst_fp)
                    ds = s_en - s_st
                    res = (p - et - qs - qsb) - ds
                    row['P_mm']       = round(p, 2)
                    row['ET_mm']      = round(et, 2)
                    row['Qs_mm']      = round(qs, 2)
                    row['Qsb_mm']     = round(qsb, 2)
                    row['dStock_mm']  = round(ds, 2)
                    row['Residu_mm']  = round(res, 2)
                    row['Stock_start_mm'] = round(s_st, 2)
                    row['Stock_end_mm']   = round(s_en, 2)
                    row['wb_status']  = "COMPUTED"
                else:
                    row['P_mm'] = row['ET_mm'] = row['Qs_mm'] = row['Qsb_mm'] = np.nan
                    row['dStock_mm'] = row['Residu_mm'] = row['Stock_start_mm'] = row['Stock_end_mm'] = np.nan
                    row['wb_status'] = "INCOMPLETE_FLUXES"
            else:
                row['P_mm'] = row['ET_mm'] = row['Qs_mm'] = row['Qsb_mm'] = np.nan
                row['dStock_mm'] = row['Residu_mm'] = row['Stock_start_mm'] = row['Stock_end_mm'] = np.nan
                row['wb_status'] = "RUN_NOT_FINISHED"
                
        # 2. Restart dispersion & difference to Member 20
        metrics = read_restart_dispersion(rst_fp, is_1m=is_1m)
        if metrics is not None:
            row.update(metrics)
        else:
            for lay in range(1, 5):
                row[f'sh2o_l{lay}_ens_minus_m20_mean'] = np.nan
                row[f'sh2o_l{lay}_std_mean']           = np.nan
                row[f'sh2o_l{lay}_range_mean']         = np.nan
            row['wa_ens_minus_m20_mean'] = np.nan

        rows.append(row)
        
    df_out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    df_out.to_csv(OUT_CSV, index=False)
    print(f"[OK] Table générée : {OUT_CSV}")
    print(df_out[['run', 'P_mm', 'ET_mm', 'Qs_mm', 'Qsb_mm', 'dStock_mm', 'Residu_mm', 
                  'sh2o_l1_ens_minus_m20_mean', 'sh2o_l2_ens_minus_m20_mean', 'sh2o_l1_std_mean']].to_string(index=False))

if __name__ == "__main__":
    main()
