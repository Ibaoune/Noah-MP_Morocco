#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step6_water_balance_2017.py
Bilan interne hydrologique 2017 (Partie B1) :
- Expériences : OL_DAIC_2017, ENS_OPL_2017, DA_nocdf (production 2017), DA_nocdf_nowilt_2017
- Bilan : R = P - ET - Qs - Qsb - Delta_S
- Delta_S = SMC (4 couches) + WA + CANWAT + SNEQV
- Différences propres :
    * ENS_OPL - OL_DAIC
    * DA_nocdf - ENS_OPL
    * DA_nocdf_nowilt - DA_nocdf
- Comparaison 2018 vs 2017

Sorties :
  - paper1/tables/water_balance_2017_annual.csv
  - paper1/tables/water_balance_2017_monthly.csv
  - paper1/tables/clean_differences_2017.csv
  - paper1/tables/water_balance_2018_vs_2017.csv
"""

import os
import glob
import re
import time
from multiprocessing import Pool
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
PARAM_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

with nc.Dataset(PARAM_NC) as ds:
    landmask = ds.variables["LANDMASK"][:].squeeze() > 0.5
n_land_cells = int(np.sum(landmask))

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

EXP_CONFIGS_2017 = {
    "OL_DAIC": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017"),
        "is_ensemble": False,
        "is_da": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "flat"
    },
    "ENS_OPL": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017"),
        "is_ensemble": True,
        "is_da": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "flat"
    },
    "DA_nocdf": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        "is_ensemble": True,
        "is_da": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "hierarchical"
    },
    "DA_nocdf_nowilt": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017"),
        "is_ensemble": True,
        "is_da": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "flat"
    }
}

def read_domain_storage(fp):
    with nc.Dataset(fp) as ds:
        smc = ds.variables["SMC"][:]
        wa = ds.variables["WA"][:]
        can = ds.variables["CANWAT"][:]
        sneqv = ds.variables["SNEQV"][:]
        
        if smc.ndim == 3:
            smc_m = np.mean(smc, axis=2)
            wa_m = np.mean(wa, axis=1)
            can_m = np.mean(can, axis=1)
            sn_m = np.mean(sneqv, axis=1)
        elif smc.ndim == 2 and smc.shape[1] == 320600:
            smc_m = np.mean(smc.reshape(4, 16030, 20), axis=2)
            wa_m = np.mean(wa.reshape(16030, 20), axis=1)
            can_m = np.mean(can.reshape(16030, 20), axis=1)
            sn_m = np.mean(sneqv.reshape(16030, 20), axis=1)
        else:
            smc_m, wa_m, can_m, sn_m = smc, wa, can, sneqv

        smc_col = np.sum(smc_m * dz[:, None], axis=0) * 1000.0  # mm
        tot_tile = smc_col + wa_m + can_m + sn_m
        return float(np.mean(tot_tile))

print(">>> Lecture des stocks initiaux et mensuels 2017...")
exp_stocks = {}
for exp, cfg in EXP_CONFIGS_2017.items():
    print(f"  Extraction restarts pour {exp}...")
    stocks = [read_domain_storage(cfg["init_rst"])]
    exp_dir = cfg["dir"]
    for m in range(1, 13):
        ym = f"2017{m:02d}"
        if cfg["style"] == "hierarchical":
            m_str = f"2017-{m:02d}"
            p_rst = os.path.join(exp_dir, f"output/{m_str}/SURFACEMODEL/*/LIS_RST_NOAHMP401_*.d01.nc")
        else:
            p_rst = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.d01.nc")
            if m == 12:
                p_rst = os.path.join(exp_dir, "output/SURFACEMODEL/201801/LIS_RST_NOAHMP401_*.d01.nc")
                
        r_files = sorted(glob.glob(p_rst))
        if not r_files:
            raise FileNotFoundError(f"Restart introuvable pour {exp} mois {m}: {p_rst}")
        rst_file = r_files[-1]
        stocks.append(read_domain_storage(rst_file))
    exp_stocks[exp] = stocks

print(">>> Extraction des forçages P non perturbés (OPL 2017)...")
opl_p_monthly = {}
opl_dir = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")
for m in range(1, 13):
    m_str = f"2017-{m:02d}"
    ym = f"2017{m:02d}"
    flist = sorted(glob.glob(os.path.join(opl_dir, f"output/{m_str}/SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")))
    p_sum = 0.0
    for f in flist:
        with nc.Dataset(f) as ds:
            p_sum += float(np.mean(ds.variables["TotalPrecip_tavg"][:].squeeze()[landmask])) * 86400.0
    opl_p_monthly[m] = p_sum

def get_enkf_increments_domain(exp, m):
    cfg = EXP_CONFIGS_2017[exp]
    if not cfg["is_da"]:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    ym = f"2017{m:02d}"
    exp_dir = cfg["dir"]
    if cfg["style"] == "hierarchical":
        m_str = f"2017-{m:02d}"
        p_inc = os.path.join(exp_dir, f"output/{m_str}/EnKF/{ym}/*_incr.*.nc")
    else:
        p_inc = os.path.join(exp_dir, f"output/EnKF/{ym}/*_incr.*.nc")
    files = sorted(glob.glob(p_inc))
    
    i1, i2, i3, i4 = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            v1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
            v2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
            v3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
            v4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
            i1 += float(np.mean(v1[landmask])) * dz[0] * 1000.0
            i2 += float(np.mean(v2[landmask])) * dz[1] * 1000.0
            i3 += float(np.mean(v3[landmask])) * dz[2] * 1000.0
            i4 += float(np.mean(v4[landmask])) * dz[3] * 1000.0
    return i1, i2, i3, i4, (i1 + i2 + i3 + i4)

def process_flux_month(args):
    exp, m = args
    cfg = EXP_CONFIGS_2017[exp]
    exp_dir = cfg["dir"]
    ym = f"2017{m:02d}"
    
    if cfg["style"] == "hierarchical":
        m_str = f"2017-{m:02d}"
        p_hist = os.path.join(exp_dir, f"output/{m_str}/SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")
    else:
        p_hist = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")
        
    files = sorted(glob.glob(p_hist))
    files = [f for f in files if "LIS_HIST_" in f and not f.endswith("0000.d01.nc.tmp")]
    
    p_tot, et_tot, qs_tot, qsb_tot = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            p_val = ds.variables["TotalPrecip_tavg"][:].squeeze()[landmask] if "TotalPrecip_tavg" in ds.variables else None
            et_val = ds.variables["Evap_tavg"][:].squeeze()[landmask]
            qs_val = ds.variables["Qs_tavg"][:].squeeze()[landmask]
            qsb_val = ds.variables["Qsb_tavg"][:].squeeze()[landmask]
            
            if p_val is not None:
                p_tot += float(np.mean(p_val)) * 86400.0
            et_tot += float(np.mean(et_val)) * 86400.0
            qs_tot += float(np.mean(qs_val)) * 86400.0
            qsb_tot += float(np.mean(qsb_val)) * 86400.0
            
    if p_tot == 0.0 and exp == "OL_DAIC":
        p_tot = opl_p_monthly[m]
        
    i1, i2, i3, i4, itot = get_enkf_increments_domain(exp, m)
    
    # Delta S pour ce mois
    ds_val = exp_stocks[exp][m] - exp_stocks[exp][m-1]
    q_tot = qs_tot + qsb_tot
    residu = p_tot - et_tot - q_tot - ds_val
    
    return {
        "experiment": exp,
        "year": 2017,
        "month": m,
        "year_month": f"2017-{m:02d}",
        "P_mm": round(p_tot, 4),
        "ET_mm": round(et_tot, 4),
        "Qs_mm": round(qs_tot, 4),
        "Qsb_mm": round(qsb_tot, 4),
        "TotalRunoff_mm": round(q_tot, 4),
        "Delta_S_mm": round(ds_val, 4),
        "Incr_Layer1_mm": round(i1, 4),
        "Incr_Layer2_mm": round(i2, 4),
        "Incr_Layer3_mm": round(i3, 4),
        "Incr_Layer4_mm": round(i4, 4),
        "Incr_EnKF_mm": round(itot, 4),
        "Residu_mm": round(residu, 4)
    }

print(">>> Extraction parallèle des flux mensuels 2017...")
tasks = [(exp, m) for exp in EXP_CONFIGS_2017.keys() for m in range(1, 13)]
t0 = time.time()
with Pool(processes=16) as pool:
    monthly_results = pool.map(process_flux_month, tasks)
print(f"Extraction terminée en {time.time()-t0:.1f} s.")

df_monthly = pd.DataFrame(monthly_results).sort_values(["experiment", "month"]).reset_index(drop=True)
out_monthly = os.path.join(TABLES_DIR, "water_balance_2017_monthly.csv")
df_monthly.to_csv(out_monthly, index=False)
print(f"[OK] Table mensuelle sauvegardée : {out_monthly}")

# --- Table Annuelle et JJA 2017 ---
print(">>> Calcul des bilans annuels et saisonniers 2017...")
annual_records = []

for exp in EXP_CONFIGS_2017.keys():
    sub = df_monthly[df_monthly["experiment"] == exp]
    
    # Annuel
    p_ann = sub["P_mm"].sum()
    et_ann = sub["ET_mm"].sum()
    qs_ann = sub["Qs_mm"].sum()
    qsb_ann = sub["Qsb_mm"].sum()
    q_ann = qs_ann + qsb_ann
    ds_ann = exp_stocks[exp][12] - exp_stocks[exp][0]
    i1_ann = sub["Incr_Layer1_mm"].sum()
    i2_ann = sub["Incr_Layer2_mm"].sum()
    i3_ann = sub["Incr_Layer3_mm"].sum()
    i4_ann = sub["Incr_Layer4_mm"].sum()
    inc_ann = sub["Incr_EnKF_mm"].sum()
    r_ann = p_ann - et_ann - q_ann - ds_ann
    gap_ann = r_ann - inc_ann if EXP_CONFIGS_2017[exp]["is_da"] else np.nan

    annual_records.append({
        "experiment": exp,
        "period": "ANNUAL_2017",
        "P_mm": round(p_ann, 2),
        "ET_mm": round(et_ann, 2),
        "Qs_mm": round(qs_ann, 2),
        "Qsb_mm": round(qsb_ann, 2),
        "TotalRunoff_mm": round(q_ann, 2),
        "Delta_S_mm": round(ds_ann, 2),
        "Incr_Layer1_mm": round(i1_ann, 2),
        "Incr_Layer2_mm": round(i2_ann, 2),
        "Incr_Layer3_mm": round(i3_ann, 2),
        "Incr_Layer4_mm": round(i4_ann, 2),
        "Incr_EnKF_mm": round(inc_ann, 2),
        "Residu_mm": round(r_ann, 2),
        "Ecart_Residu_minus_Incr_mm": round(gap_ann, 2) if not np.isnan(gap_ann) else np.nan,
        "valid_closure_lt_1mm": abs(r_ann) < 1.0
    })

    # JJA
    sub_jja = sub[sub["month"].isin([6, 7, 8])]
    p_jja = sub_jja["P_mm"].sum()
    et_jja = sub_jja["ET_mm"].sum()
    qs_jja = sub_jja["Qs_mm"].sum()
    qsb_jja = sub_jja["Qsb_mm"].sum()
    q_jja = qs_jja + qsb_jja
    ds_jja = exp_stocks[exp][8] - exp_stocks[exp][5]
    inc_jja = sub_jja["Incr_EnKF_mm"].sum()
    r_jja = p_jja - et_jja - q_jja - ds_jja
    gap_jja = r_jja - inc_jja if EXP_CONFIGS_2017[exp]["is_da"] else np.nan

    annual_records.append({
        "experiment": exp,
        "period": "JJA_2017",
        "P_mm": round(p_jja, 2),
        "ET_mm": round(et_jja, 2),
        "Qs_mm": round(qs_jja, 2),
        "Qsb_mm": round(qsb_jja, 2),
        "TotalRunoff_mm": round(q_jja, 2),
        "Delta_S_mm": round(ds_jja, 2),
        "Incr_Layer1_mm": round(sub_jja["Incr_Layer1_mm"].sum(), 2),
        "Incr_Layer2_mm": round(sub_jja["Incr_Layer2_mm"].sum(), 2),
        "Incr_Layer3_mm": round(sub_jja["Incr_Layer3_mm"].sum(), 2),
        "Incr_Layer4_mm": round(sub_jja["Incr_Layer4_mm"].sum(), 2),
        "Incr_EnKF_mm": round(inc_jja, 2),
        "Residu_mm": round(r_jja, 2),
        "Ecart_Residu_minus_Incr_mm": round(gap_jja, 2) if not np.isnan(gap_jja) else np.nan,
        "valid_closure_lt_1mm": abs(r_jja) < 1.0
    })

df_ann = pd.DataFrame(annual_records)
out_annual = os.path.join(TABLES_DIR, "water_balance_2017_annual.csv")
df_ann.to_csv(out_annual, index=False)
print(f"[OK] Table annuelle sauvegardée : {out_annual}")

# --- Différences Propres 2017 ---
print(">>> Calcul des différences propres 2017...")
PAIRS_2017 = [
    ("ENS_OPL", "OL_DAIC", "ENS_OPL - OL_DAIC", "Effet ensemble production 2017"),
    ("DA_nocdf", "ENS_OPL", "DA_nocdf - ENS_OPL", "Effet observations production 2017"),
    ("DA_nocdf_nowilt", "DA_nocdf", "DA_nocdf_nowilt - DA_nocdf", "Effet filtre fletrissement 2017")
]

diff_records = []
for p_lbl in ["ANNUAL_2017", "JJA_2017"]:
    df_p = df_ann[df_ann["period"] == p_lbl].set_index("experiment")
    for exp_x, exp_y, pair_code, pair_desc in PAIRS_2017:
        rx = df_p.loc[exp_x]
        ry = df_p.loc[exp_y]
        diff_records.append({
            "period": p_lbl,
            "pair": pair_code,
            "pair_description": pair_desc,
            "Delta_P_mm": round(rx["P_mm"] - ry["P_mm"], 2),
            "Delta_ET_mm": round(rx["ET_mm"] - ry["ET_mm"], 2),
            "Delta_Qs_mm": round(rx["Qs_mm"] - ry["Qs_mm"], 2),
            "Delta_Qsb_mm": round(rx["Qsb_mm"] - ry["Qsb_mm"], 2),
            "Delta_TotalRunoff_mm": round(rx["TotalRunoff_mm"] - ry["TotalRunoff_mm"], 2),
            "Delta_Delta_S_mm": round(rx["Delta_S_mm"] - ry["Delta_S_mm"], 2),
            "Delta_Incr_EnKF_mm": round(rx["Incr_EnKF_mm"] - ry["Incr_EnKF_mm"], 2),
            "Delta_Residu_mm": round(rx["Residu_mm"] - ry["Residu_mm"], 2)
        })

df_diff = pd.DataFrame(diff_records)
out_diff = os.path.join(TABLES_DIR, "clean_differences_2017.csv")
df_diff.to_csv(out_diff, index=False)
print(f"[OK] Table différences propres sauvegardée : {out_diff}")

# --- Comparaison 2018 vs 2017 ---
print(">>> Comparaison 2018 vs 2017...")
df_ann_2018 = pd.read_csv(os.path.join(TABLES_DIR, "water_balance_corrected_2018_annual.csv"))
df_ann_2018_sub = df_ann_2018[df_ann_2018["period"].isin(["ANNUAL", "ANNUAL_2018"])].set_index("experiment")
df_ann_2017_sub = df_ann[df_ann["period"].isin(["ANNUAL", "ANNUAL_2017"])].set_index("experiment")

common_exps = ["OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_nocdf_nowilt"]
comp_records = []
for exp in common_exps:
    r17 = df_ann_2017_sub.loc[exp]
    r18 = df_ann_2018_sub.loc[exp]
    incr_18 = r18["Incr_Total_mm"] if "Incr_Total_mm" in r18 else r18.get("Incr_EnKF_mm", 0.0)
    res_18 = r18["WaterBalance_Residual_mm"] if "WaterBalance_Residual_mm" in r18 else r18.get("Residu_mm", 0.0)
    comp_records.append({
        "experiment": exp,
        "P_2017_mm": r17["P_mm"],
        "P_2018_mm": r18["P_mm"],
        "Delta_P_18_minus_17_mm": round(r18["P_mm"] - r17["P_mm"], 2),
        "ET_2017_mm": r17["ET_mm"],
        "ET_2018_mm": r18["ET_mm"],
        "Delta_ET_18_minus_17_mm": round(r18["ET_mm"] - r17["ET_mm"], 2),
        "Qs_2017_mm": r17["Qs_mm"],
        "Qs_2018_mm": r18["Qs_mm"],
        "Delta_Qs_18_minus_17_mm": round(r18["Qs_mm"] - r17["Qs_mm"], 2),
        "Qsb_2017_mm": r17["Qsb_mm"],
        "Qsb_2018_mm": r18["Qsb_mm"],
        "Delta_Qsb_18_minus_17_mm": round(r18["Qsb_mm"] - r17["Qsb_mm"], 2),
        "TotalRunoff_2017_mm": r17["TotalRunoff_mm"],
        "TotalRunoff_2018_mm": r18["TotalRunoff_mm"],
        "Delta_TotalRunoff_18_minus_17_mm": round(r18["TotalRunoff_mm"] - r17["TotalRunoff_mm"], 2),
        "Delta_S_2017_mm": r17["Delta_S_mm"],
        "Delta_S_2018_mm": r18["Delta_S_mm"],
        "Incr_EnKF_2017_mm": r17["Incr_EnKF_mm"],
        "Incr_EnKF_2018_mm": incr_18,
        "Residu_2017_mm": r17["Residu_mm"],
        "Residu_2018_mm": res_18
    })

df_comp = pd.DataFrame(comp_records)
out_comp = os.path.join(TABLES_DIR, "water_balance_2018_vs_2017.csv")
df_comp.to_csv(out_comp, index=False)
print(f"[OK] Table 2018 vs 2017 sauvegardée : {out_comp}")
