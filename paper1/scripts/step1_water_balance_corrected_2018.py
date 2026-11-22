#!/usr/bin/env python3
"""
step1_water_balance_corrected_2018.py

Calcule le bilan hydrique interne annuel, mensuel et JJA pour les 6 experiences 2018 :
  - OL_DAIC_2018
  - ENS_OPL_2018
  - ENS_corr_2018
  - DA_nocdf (production 2018)
  - DA_nocdf_nowilt_2018
  - DA_corr_2018

Methode :
  - R = P - ET - Qs - Qsb - Delta_S
  - Delta_S = SMC (4 couches) + WA + CANWAT + SNEQV (lus dans les restarts mensuels, moyenne ensemble)
  - Moyenne spatiale sur les 16 030 mailles terrestres du domaine (LANDMASK > 0.5)
  - Increments archives EnKF par couche pour chaque DA
  - Calcul des differences propres avec Delta_P mesure

Genere :
  - paper1/tables/water_balance_corrected_2018_monthly.csv
  - paper1/tables/water_balance_corrected_2018_annual.csv
  - paper1/tables/clean_differences_2018.csv
"""

import os
import glob
import datetime
import multiprocessing as mp
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
PARAM_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
OPL_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")

os.makedirs(TABLES_DIR, exist_ok=True)

# 1. Masque domaine
with nc.Dataset(PARAM_NC) as ds:
    landmask = ds.variables["LANDMASK"][:].squeeze() > 0.5
n_land = int(np.sum(landmask))
print(f"Mailles terrestres actives (LANDMASK > 0.5) : {n_land}")

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

EXP_CONFIGS = {
    "OL_DAIC": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
        "is_ensemble": False,
        "is_da": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "flat"
    },
    "ENS_OPL": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
        "is_ensemble": True,
        "is_da": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "flat"
    },
    "ENS_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018"),
        "is_ensemble": True,
        "is_da": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "flat"
    },
    "DA_nocdf": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        "is_ensemble": True,
        "is_da": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "hierarchical"
    },
    "DA_nocdf_nowilt": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018"),
        "is_ensemble": True,
        "is_da": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "flat"
    },
    "DA_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018"),
        "is_ensemble": True,
        "is_da": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc"),
        "style": "flat"
    }
}

def read_domain_storage(fp):
    with nc.Dataset(fp) as ds:
        smc = ds.variables["SMC"][:]
        wa = ds.variables["WA"][:]
        can = ds.variables["CANWAT"][:]
        sneqv = ds.variables["SNEQV"][:]
        
        if smc.ndim == 3: # (4, ntiles, nens)
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

        smc_col = np.sum(smc_m * dz[:, None], axis=0) * 1000.0 # mm
        tot_tile = smc_col + wa_m + can_m + sn_m
        return float(np.mean(tot_tile))

print(">>> Lecture des stocks initiaux et mensuels pour chaque experience...")
exp_stocks = {}
for exp, cfg in EXP_CONFIGS.items():
    print(f"  Extraction restarts pour {exp}...")
    stocks = [read_domain_storage(cfg["init_rst"])]
    exp_dir = cfg["dir"]
    for m in range(1, 13):
        ym = f"2018{m:02d}"
        if cfg["style"] == "hierarchical":
            m_str = f"2018-{m:02d}"
            p_rst = os.path.join(exp_dir, f"output/{m_str}/SURFACEMODEL/*/LIS_RST_NOAHMP401_*.d01.nc")
        else:
            p_rst = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.d01.nc")
            if m == 12:
                p_rst = os.path.join(exp_dir, "output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_*.d01.nc")
                
        r_files = sorted(glob.glob(p_rst))
        if not r_files:
            raise FileNotFoundError(f"Restart introuvable pour {exp} mois {m}: {p_rst}")
        rst_file = r_files[-1]
        stocks.append(read_domain_storage(rst_file))
    exp_stocks[exp] = stocks

print(">>> Extraction des flux et des increments EnKF...")

def get_enkf_increments_domain(exp, m):
    cfg = EXP_CONFIGS[exp]
    if not cfg["is_da"]:
        return 0.0, 0.0, 0.0, 0.0, 0.0
    ym = f"2018{m:02d}"
    exp_dir = cfg["dir"]
    if cfg["style"] == "hierarchical":
        m_str = f"2018-{m:02d}"
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

def get_month_flux_files(exp, m):
    cfg = EXP_CONFIGS[exp]
    exp_dir = cfg["dir"]
    if cfg["style"] == "hierarchical":
        m_str = f"2018-{m:02d}"
        files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_str}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    else:
        start_dt = datetime.datetime(2018, m, 1)
        if m == 12:
            next_m = datetime.datetime(2019, 1, 1)
        else:
            next_m = datetime.datetime(2018, m+1, 1)
        n_days = (next_m - start_dt).days
        files = []
        for d in range(n_days):
            dt_curr = start_dt + datetime.timedelta(days=d)
            dt_hist = dt_curr + datetime.timedelta(days=1)
            f = os.path.join(exp_dir, f"output/SURFACEMODEL/{dt_hist.strftime('%Y%m')}/LIS_HIST_{dt_hist.strftime('%Y%m%d0000')}.d01.nc")
            files.append(f)
    return files

# Precalcul de P non perturbe pour OL_DAIC depuis OPL
opl_precip_monthly = {}
for m in range(1, 13):
    m_str = f"2018-{m:02d}"
    opl_files = sorted(glob.glob(os.path.join(OPL_DIR, f"output/{m_str}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    p_sum = 0.0
    for f in opl_files:
        with nc.Dataset(f) as ds:
            p_sum += float(np.mean(ds["TotalPrecip_tavg"][:].squeeze()[landmask] * 86400.0))
    opl_precip_monthly[m] = p_sum

def process_exp_month(args):
    exp, m = args
    files = get_month_flux_files(exp, m)
    p_val, et_val, qs_val, qsb_val = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            if "TotalPrecip_tavg" in ds.variables:
                p_val += float(np.mean(ds["TotalPrecip_tavg"][:].squeeze()[landmask] * 86400.0))
            et_val  += float(np.mean(ds["Evap_tavg"][:].squeeze()[landmask] * 86400.0))
            qs_val  += float(np.mean(ds["Qs_tavg"][:].squeeze()[landmask] * 86400.0))
            qsb_val += float(np.mean(ds["Qsb_tavg"][:].squeeze()[landmask] * 86400.0))
            
    if exp == "OL_DAIC":
        p_val = opl_precip_monthly[m]
        
    ds_val = exp_stocks[exp][m] - exp_stocks[exp][m-1]
    i1, i2, i3, i4, itot = get_enkf_increments_domain(exp, m)
    
    r_val = p_val - et_val - (qs_val + qsb_val) - ds_val
    res_minus_incr = r_val - itot if EXP_CONFIGS[exp]["is_da"] else 0.0
    
    return {
        "experiment": exp,
        "year_month": f"2018-{m:02d}",
        "month": m,
        "P_mm": round(p_val, 4),
        "ET_mm": round(et_val, 4),
        "Qs_mm": round(qs_val, 4),
        "Qsb_mm": round(qsb_val, 4),
        "TotalRunoff_mm": round(qs_val + qsb_val, 4),
        "Stock_start_mm": round(exp_stocks[exp][m-1], 4),
        "Stock_end_mm": round(exp_stocks[exp][m], 4),
        "Delta_S_mm": round(ds_val, 4),
        "Incr_Layer1_mm": round(i1, 4),
        "Incr_Layer2_mm": round(i2, 4),
        "Incr_Layer3_mm": round(i3, 4),
        "Incr_Layer4_mm": round(i4, 4),
        "Incr_Total_mm": round(itot, 4),
        "WaterBalance_Residual_mm": round(r_val, 4),
        "Residual_minus_Incr_mm": round(res_minus_incr, 4)
    }

tasks = [(exp, m) for m in range(1, 13) for exp in EXP_CONFIGS]
print(f"Calcul en parallele de {len(tasks)} couples (experience, mois)...")
with mp.Pool(processes=16) as pool:
    monthly_records = pool.map(process_exp_month, tasks)

# Sort by experiment, month
df_monthly = pd.DataFrame(monthly_records)
df_monthly = df_monthly.sort_values(by=["experiment", "month"]).reset_index(drop=True)
out_m_csv = os.path.join(TABLES_DIR, "water_balance_corrected_2018_monthly.csv")
df_monthly.to_csv(out_m_csv, index=False)
print(f"[OK] Sauve : {out_m_csv}")

# 2. Table Annuelle et JJA
print(">>> Synthese Annuelle et JJA...")
annual_records = []
for exp in EXP_CONFIGS:
    sub = df_monthly[df_monthly["experiment"] == exp]
    
    # ANNUAL (months 1..12)
    p_ann = sub["P_mm"].sum()
    et_ann = sub["ET_mm"].sum()
    qs_ann = sub["Qs_mm"].sum()
    qsb_ann = sub["Qsb_mm"].sum()
    tot_q_ann = qs_ann + qsb_ann
    ds_ann = exp_stocks[exp][12] - exp_stocks[exp][0]
    i1_ann = sub["Incr_Layer1_mm"].sum()
    i2_ann = sub["Incr_Layer2_mm"].sum()
    i3_ann = sub["Incr_Layer3_mm"].sum()
    i4_ann = sub["Incr_Layer4_mm"].sum()
    itot_ann = sub["Incr_Total_mm"].sum()
    r_ann = p_ann - et_ann - tot_q_ann - ds_ann
    r_m_i_ann = r_ann - itot_ann if EXP_CONFIGS[exp]["is_da"] else 0.0
    
    annual_records.append({
        "experiment": exp,
        "period": "ANNUAL",
        "P_mm": round(p_ann, 4),
        "ET_mm": round(et_ann, 4),
        "Qs_mm": round(qs_ann, 4),
        "Qsb_mm": round(qsb_ann, 4),
        "TotalRunoff_mm": round(tot_q_ann, 4),
        "Stock_start_mm": round(exp_stocks[exp][0], 4),
        "Stock_end_mm": round(exp_stocks[exp][12], 4),
        "Delta_S_mm": round(ds_ann, 4),
        "Incr_Layer1_mm": round(i1_ann, 4),
        "Incr_Layer2_mm": round(i2_ann, 4),
        "Incr_Layer3_mm": round(i3_ann, 4),
        "Incr_Layer4_mm": round(i4_ann, 4),
        "Incr_Total_mm": round(itot_ann, 4),
        "WaterBalance_Residual_mm": round(r_ann, 4),
        "Residual_minus_Incr_mm": round(r_m_i_ann, 4)
    })
    
    # JJA (months 6, 7, 8)
    sub_jja = sub[sub["month"].isin([6, 7, 8])]
    p_jja = sub_jja["P_mm"].sum()
    et_jja = sub_jja["ET_mm"].sum()
    qs_jja = sub_jja["Qs_mm"].sum()
    qsb_jja = sub_jja["Qsb_mm"].sum()
    tot_q_jja = qs_jja + qsb_jja
    ds_jja = exp_stocks[exp][8] - exp_stocks[exp][5]
    i1_jja = sub_jja["Incr_Layer1_mm"].sum()
    i2_jja = sub_jja["Incr_Layer2_mm"].sum()
    i3_jja = sub_jja["Incr_Layer3_mm"].sum()
    i4_jja = sub_jja["Incr_Layer4_mm"].sum()
    itot_jja = sub_jja["Incr_Total_mm"].sum()
    r_jja = p_jja - et_jja - tot_q_jja - ds_jja
    r_m_i_jja = r_jja - itot_jja if EXP_CONFIGS[exp]["is_da"] else 0.0
    
    annual_records.append({
        "experiment": exp,
        "period": "JJA",
        "P_mm": round(p_jja, 4),
        "ET_mm": round(et_jja, 4),
        "Qs_mm": round(qs_jja, 4),
        "Qsb_mm": round(qsb_jja, 4),
        "TotalRunoff_mm": round(tot_q_jja, 4),
        "Stock_start_mm": round(exp_stocks[exp][5], 4),
        "Stock_end_mm": round(exp_stocks[exp][8], 4),
        "Delta_S_mm": round(ds_jja, 4),
        "Incr_Layer1_mm": round(i1_jja, 4),
        "Incr_Layer2_mm": round(i2_jja, 4),
        "Incr_Layer3_mm": round(i3_jja, 4),
        "Incr_Layer4_mm": round(i4_jja, 4),
        "Incr_Total_mm": round(itot_jja, 4),
        "WaterBalance_Residual_mm": round(r_jja, 4),
        "Residual_minus_Incr_mm": round(r_m_i_jja, 4)
    })

df_annual = pd.DataFrame(annual_records)
out_a_csv = os.path.join(TABLES_DIR, "water_balance_corrected_2018_annual.csv")
df_annual.to_csv(out_a_csv, index=False)
print(f"[OK] Sauve : {out_a_csv}")

# 3. Table des differences propres
print(">>> Calcul des differences propres...")
PAIRS = [
    ("ENS_corr", "OL_DAIC", "effet residuel de l'ensemble corrige"),
    ("ENS_OPL", "OL_DAIC", "effet de l'ensemble de production"),
    ("DA_corr", "ENS_corr", "effet des observations, systeme corrige"),
    ("DA_nocdf", "ENS_OPL", "effet des observations, systeme de production"),
    ("DA_nocdf_nowilt", "DA_nocdf", "effet du filtre de fletrissement")
]

diff_records = []
periods = ["ANNUAL", "JJA"] + [f"2018-{m:02d}" for m in range(1, 13)]

for b_exp, a_exp, meaning in PAIRS:
    for per in periods:
        if per in ["ANNUAL", "JJA"]:
            row_b = df_annual[(df_annual["experiment"] == b_exp) & (df_annual["period"] == per)].iloc[0]
            row_a = df_annual[(df_annual["experiment"] == a_exp) & (df_annual["period"] == per)].iloc[0]
        else:
            row_b = df_monthly[(df_monthly["experiment"] == b_exp) & (df_monthly["year_month"] == per)].iloc[0]
            row_a = df_monthly[(df_monthly["experiment"] == a_exp) & (df_monthly["year_month"] == per)].iloc[0]
            
        dp = row_b["P_mm"] - row_a["P_mm"]
        det = row_b["ET_mm"] - row_a["ET_mm"]
        dqs = row_b["Qs_mm"] - row_a["Qs_mm"]
        dqsb = row_b["Qsb_mm"] - row_a["Qsb_mm"]
        dqtot = row_b["TotalRunoff_mm"] - row_a["TotalRunoff_mm"]
        dds = row_b["Delta_S_mm"] - row_a["Delta_S_mm"]
        dr = row_b["WaterBalance_Residual_mm"] - row_a["WaterBalance_Residual_mm"]
        
        incr_b = row_b["Incr_Total_mm"]
        incr_a = row_a["Incr_Total_mm"]
        d_incr = incr_b - incr_a
        
        diff_records.append({
            "pair": f"{b_exp} - {a_exp}",
            "exp_B": b_exp,
            "exp_A": a_exp,
            "meaning": meaning,
            "period": per,
            "delta_P_mm": round(dp, 4),
            "delta_ET_mm": round(det, 4),
            "delta_Qs_mm": round(dqs, 4),
            "delta_Qsb_mm": round(dqsb, 4),
            "delta_TotalRunoff_mm": round(dqtot, 4),
            "delta_Delta_S_mm": round(dds, 4),
            "delta_Residual_mm": round(dr, 4),
            "Incr_Total_B_mm": round(incr_b, 4),
            "Incr_Total_A_mm": round(incr_a, 4),
            "delta_Incr_Total_mm": round(d_incr, 4),
            "residual_gap_vs_incr_mm": round(dr - d_incr, 4)
        })

df_diff = pd.DataFrame(diff_records)
out_d_csv = os.path.join(TABLES_DIR, "clean_differences_2018.csv")
df_diff.to_csv(out_d_csv, index=False)
print(f"[OK] Sauve : {out_d_csv}")
print("Bilan 2018 termine avec succes.")
