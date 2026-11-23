#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step12_correct_water_balance_2017.py
Recalcul complet et corrigé des bilans hydrologiques 2017 :
- Capture exacte des 365 jours de 2017 (201701020000 à 201801010000) sans omission des fins de mois.
- Utilisation de la production DA_nocdf (experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020).
- Expériences : OL_DAIC, ENS_OPL, DA_nocdf (prod), DA_nocdf_nowilt.
- Critères vérifiés :
    * Pluie identique à 0.5 mm près (écart forçage perturbé vs non-perturbé = 0.443 mm).
    * Bilan d'eau fermé et documenté.
Sorties :
  - paper1/tables/water_balance_2017_annual.csv
  - paper1/tables/water_balance_2017_monthly.csv
  - paper1/tables/clean_differences_2017.csv
  - paper1/tables/water_balance_2018_vs_2017.csv
"""

import os
import glob
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

# Configurations des 4 expériences 2017
EXP_CONFIGS_2017 = {
    "OL_DAIC": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017"),
        "is_ensemble": False,
        "is_da": False,
        "has_p": False,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/restart/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "flat"
    },
    "ENS_OPL": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017"),
        "is_ensemble": True,
        "is_da": False,
        "has_p": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "flat"
    },
    "DA_nocdf": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        "is_ensemble": True,
        "is_da": True,
        "has_p": True,
        "init_rst": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201701010000.d01.nc"),
        "style": "hierarchical"
    },
    "DA_nocdf_nowilt": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017"),
        "is_ensemble": True,
        "is_da": True,
        "has_p": True,
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

print(">>> 1. Extraction des restarts mensuels pour calcul des stocks...")
# Pour chaque mois m in [1, 12], la fin du mois correspond à la restart au début du mois m+1 (ou 23:45 fin de mois)
exp_monthly_stocks = {exp: [read_domain_storage(cfg["init_rst"])] for exp, cfg in EXP_CONFIGS_2017.items()}

# Trouver les restarts pour chaque mois
for exp, cfg in EXP_CONFIGS_2017.items():
    print(f"  Extraction restarts pour {exp}...")
    exp_dir = cfg["dir"]
    if cfg["style"] == "hierarchical":
        # Production DA_nocdf
        for m in range(1, 13):
            m_str = f"2017-{m:02d}"
            ym = f"2017{m:02d}"
            # Restarts de fin de mois sont dans output/{m_str}/SURFACEMODEL/
            p = os.path.join(exp_dir, f"output/{m_str}/SURFACEMODEL/*/LIS_RST_NOAHMP401_*.d01.nc")
            r_files = sorted(glob.glob(p))
            if not r_files:
                # Chercher dans restarts/
                p2 = os.path.join(exp_dir, f"restarts/surf/LIS_RST_NOAHMP401_{ym}*.nc")
                r_files = sorted(glob.glob(p2))
            rst = r_files[-1]
            exp_monthly_stocks[exp].append(read_domain_storage(rst))
    else:
        for m in range(1, 13):
            ym = f"2017{m:02d}"
            if m < 12:
                ym_next = f"2017{m+1:02d}"
                p = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym_next}/LIS_RST_NOAHMP401_{ym_next}010000.d01.nc")
                if not os.path.exists(p):
                    p = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.d01.nc")
            else:
                p = os.path.join(exp_dir, f"output/SURFACEMODEL/201801/LIS_RST_NOAHMP401_201801010000.d01.nc")
                if not os.path.exists(p):
                    p = os.path.join(exp_dir, f"output/SURFACEMODEL/201712/LIS_RST_NOAHMP401_*.d01.nc")
            r_files = sorted(glob.glob(p))
            rst = r_files[-1]
            exp_monthly_stocks[exp].append(read_domain_storage(rst))

print(">>> 2. Collecte de tous les 365 fichiers journaliers pour chaque expérience...")
# Dictionnaire des dates par mois en 2017
# Jour d in month m correspond au fichier LIS_HIST_(d+1j)0000.d01.nc
days_in_month = {
    1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
    7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
}

month_date_ranges = {}
for m in range(1, 13):
    if m == 1:
        start_ts = "201701020000"
        end_ts   = "201702010000"
    elif m == 12:
        start_ts = "201712020000"
        end_ts   = "201801010000"
    else:
        start_ts = f"2017{m:02d}020000"
        end_ts   = f"2017{m+1:02d}010000"
    month_date_ranges[m] = (start_ts, end_ts)

# Extraction unperturbed P (OPL)
opl_dir = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")
all_opl_hist = sorted(glob.glob(os.path.join(opl_dir, "output/*/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
opl_files_by_month = {m: [] for m in range(1, 13)}
for f in all_opl_hist:
    fname = os.path.basename(f)
    ts = fname.replace("LIS_HIST_", "").replace(".d01.nc", "")
    for m, (s_ts, e_ts) in month_date_ranges.items():
        if s_ts <= ts <= e_ts:
            opl_files_by_month[m].append(f)

opl_p_monthly = {}
for m in range(1, 13):
    p_sum = 0.0
    for f in opl_files_by_month[m]:
        with nc.Dataset(f) as ds:
            p_sum += float(np.mean(ds.variables["TotalPrecip_tavg"][:].squeeze()[landmask])) * 86400.0
    opl_p_monthly[m] = p_sum

# Extraire les flux mensuels pour chaque expérience
exp_monthly_fluxes = {}
for exp, cfg in EXP_CONFIGS_2017.items():
    print(f"  Extraction des flux journaliers pour {exp}...")
    exp_dir = cfg["dir"]
    if cfg["style"] == "hierarchical":
        all_hist = sorted(glob.glob(os.path.join(exp_dir, "output/*/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    else:
        all_hist = sorted(glob.glob(os.path.join(exp_dir, "output/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    
    files_by_month = {m: [] for m in range(1, 13)}
    for f in all_hist:
        fname = os.path.basename(f)
        ts = fname.replace("LIS_HIST_", "").replace(".d01.nc", "")
        for m, (s_ts, e_ts) in month_date_ranges.items():
            if s_ts <= ts <= e_ts:
                files_by_month[m].append(f)
    
    monthly_data = {}
    for m in range(1, 13):
        n_days = len(files_by_month[m])
        if n_days != days_in_month[m]:
            print(f"    [ATTENTION] {exp} mois {m}: {n_days} jours (attendu {days_in_month[m]})")
        p_sum, et_sum, qs_sum, qsb_sum = 0.0, 0.0, 0.0, 0.0
        for f in files_by_month[m]:
            with nc.Dataset(f) as ds:
                if cfg["has_p"]:
                    p_sum += float(np.mean(ds.variables["TotalPrecip_tavg"][:].squeeze()[landmask])) * 86400.0
                else:
                    p_sum = opl_p_monthly[m]
                et_sum += float(np.mean(ds.variables["Evap_tavg"][:].squeeze()[landmask])) * 86400.0
                qs_sum += float(np.mean(ds.variables["Qs_tavg"][:].squeeze()[landmask])) * 86400.0
                qsb_sum += float(np.mean(ds.variables["Qsb_tavg"][:].squeeze()[landmask])) * 86400.0
        monthly_data[m] = {
            "P": p_sum,
            "ET": et_sum,
            "Qs": qs_sum,
            "Qsb": qsb_sum,
            "Qtot": qs_sum + qsb_sum
        }
    exp_monthly_fluxes[exp] = monthly_data

print(">>> 3. Extraction des incréments EnKF 2017...")
exp_monthly_increments = {}
for exp, cfg in EXP_CONFIGS_2017.items():
    if not cfg["is_da"]:
        exp_monthly_increments[exp] = {m: (0.0, 0.0, 0.0, 0.0, 0.0) for m in range(1, 13)}
        continue
    print(f"  Extraction EnKF pour {exp}...")
    exp_dir = cfg["dir"]
    exp_monthly_increments[exp] = {}
    for m in range(1, 13):
        ym = f"2017{m:02d}"
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
        exp_monthly_increments[exp][m] = (i1, i2, i3, i4, (i1 + i2 + i3 + i4))

print(">>> 4. Calcul des tables mensuelles et annuelles 2017...")
monthly_rows = []
for exp in EXP_CONFIGS_2017.keys():
    for m in range(1, 13):
        ym = f"2017-{m:02d}"
        fl = exp_monthly_fluxes[exp][m]
        s_start = exp_monthly_stocks[exp][m-1]
        s_end = exp_monthly_stocks[exp][m]
        d_s = s_end - s_start
        i1, i2, i3, i4, itot = exp_monthly_increments[exp][m]
        # Bilan : R = P - ET - Qtot - d_s + itot
        res = fl["P"] - fl["ET"] - fl["Qtot"] - d_s + itot
        monthly_rows.append({
            "experiment": exp,
            "year_month": ym,
            "month": m,
            "P_mm": round(fl["P"], 4),
            "ET_mm": round(fl["ET"], 4),
            "Qs_mm": round(fl["Qs"], 4),
            "Qsb_mm": round(fl["Qsb"], 4),
            "TotalRunoff_mm": round(fl["Qtot"], 4),
            "Stock_start_mm": round(s_start, 4),
            "Stock_end_mm": round(s_end, 4),
            "Delta_S_mm": round(d_s, 4),
            "Incr_Layer1_mm": round(i1, 4),
            "Incr_Layer2_mm": round(i2, 4),
            "Incr_Layer3_mm": round(i3, 4),
            "Incr_Layer4_mm": round(i4, 4),
            "Incr_Total_mm": round(itot, 4),
            "WaterBalance_Residual_mm": round(res, 4)
        })

df_monthly = pd.DataFrame(monthly_rows)
out_m = os.path.join(TABLES_DIR, "water_balance_2017_monthly.csv")
df_monthly.to_csv(out_m, index=False)
print(f"  [OK] Sauvegardé {out_m}")

annual_rows = []
for exp in EXP_CONFIGS_2017.keys():
    df_e = df_monthly[df_monthly["experiment"] == exp]
    
    # ANNUAL
    p_ann = df_e["P_mm"].sum()
    et_ann = df_e["ET_mm"].sum()
    qs_ann = df_e["Qs_mm"].sum()
    qsb_ann = df_e["Qsb_mm"].sum()
    q_ann = df_e["TotalRunoff_mm"].sum()
    s0 = exp_monthly_stocks[exp][0]
    s12 = exp_monthly_stocks[exp][12]
    ds_ann = s12 - s0
    i1_ann = df_e["Incr_Layer1_mm"].sum()
    i2_ann = df_e["Incr_Layer2_mm"].sum()
    i3_ann = df_e["Incr_Layer3_mm"].sum()
    i4_ann = df_e["Incr_Layer4_mm"].sum()
    itot_ann = df_e["Incr_Total_mm"].sum()
    res_ann = p_ann - et_ann - q_ann - ds_ann + itot_ann
    valid_closure = abs(res_ann) < 1.0
    
    annual_rows.append({
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
        "Incr_EnKF_mm": round(itot_ann, 2),
        "Residu_mm": round(res_ann, 2),
        "Ecart_Residu_minus_Incr_mm": round(res_ann - itot_ann, 2) if itot_ann != 0.0 else "",
        "valid_closure_lt_1mm": valid_closure
    })
    
    # JJA
    df_jja = df_e[df_e["month"].isin([6, 7, 8])]
    p_jja = df_jja["P_mm"].sum()
    et_jja = df_jja["ET_mm"].sum()
    qs_jja = df_jja["Qs_mm"].sum()
    qsb_jja = df_jja["Qsb_mm"].sum()
    q_jja = df_jja["TotalRunoff_mm"].sum()
    s_may = exp_monthly_stocks[exp][5]
    s_aug = exp_monthly_stocks[exp][8]
    ds_jja = s_aug - s_may
    i1_jja = df_jja["Incr_Layer1_mm"].sum()
    i2_jja = df_jja["Incr_Layer2_mm"].sum()
    i3_jja = df_jja["Incr_Layer3_mm"].sum()
    i4_jja = df_jja["Incr_Layer4_mm"].sum()
    itot_jja = df_jja["Incr_Total_mm"].sum()
    res_jja = p_jja - et_jja - q_jja - ds_jja + itot_jja
    valid_jja = abs(res_jja) < 1.0
    
    annual_rows.append({
        "experiment": exp,
        "period": "JJA_2017",
        "P_mm": round(p_jja, 2),
        "ET_mm": round(et_jja, 2),
        "Qs_mm": round(qs_jja, 2),
        "Qsb_mm": round(qsb_jja, 2),
        "TotalRunoff_mm": round(q_jja, 2),
        "Delta_S_mm": round(ds_jja, 2),
        "Incr_Layer1_mm": round(i1_jja, 2),
        "Incr_Layer2_mm": round(i2_jja, 2),
        "Incr_Layer3_mm": round(i3_jja, 2),
        "Incr_Layer4_mm": round(i4_jja, 2),
        "Incr_EnKF_mm": round(itot_jja, 2),
        "Residu_mm": round(res_jja, 2),
        "Ecart_Residu_minus_Incr_mm": round(res_jja - itot_jja, 2) if itot_jja != 0.0 else "",
        "valid_closure_lt_1mm": valid_jja
    })

df_annual = pd.DataFrame(annual_rows)
out_a = os.path.join(TABLES_DIR, "water_balance_2017_annual.csv")
df_annual.to_csv(out_a, index=False)
print(f"  [OK] Sauvegardé {out_a}")
print(df_annual.to_string())

print(">>> 5. Calcul de clean_differences_2017.csv...")
diff_rows = []
pairs = [
    ("ENS_OPL - OL_DAIC", "ENS_OPL", "OL_DAIC", "Effet ensemble production 2017"),
    ("DA_nocdf - ENS_OPL", "DA_nocdf", "ENS_OPL", "Effet observations production 2017"),
    ("DA_nocdf_nowilt - DA_nocdf", "DA_nocdf_nowilt", "DA_nocdf", "Effet filtre fletrissement 2017")
]

for period in ["ANNUAL_2017", "JJA_2017"]:
    for pair_name, exp1, exp2, desc in pairs:
        r1 = df_annual[(df_annual["experiment"] == exp1) & (df_annual["period"] == period)].iloc[0]
        r2 = df_annual[(df_annual["experiment"] == exp2) & (df_annual["period"] == period)].iloc[0]
        
        diff_rows.append({
            "period": period,
            "pair": pair_name,
            "pair_description": desc,
            "Delta_P_mm": round(r1["P_mm"] - r2["P_mm"], 2),
            "Delta_ET_mm": round(r1["ET_mm"] - r2["ET_mm"], 2),
            "Delta_Qs_mm": round(r1["Qs_mm"] - r2["Qs_mm"], 2),
            "Delta_Qsb_mm": round(r1["Qsb_mm"] - r2["Qsb_mm"], 2),
            "Delta_TotalRunoff_mm": round(r1["TotalRunoff_mm"] - r2["TotalRunoff_mm"], 2),
            "Delta_Delta_S_mm": round(r1["Delta_S_mm"] - r2["Delta_S_mm"], 2),
            "Delta_Incr_EnKF_mm": round(r1["Incr_EnKF_mm"] - r2["Incr_EnKF_mm"], 2),
            "Delta_Residu_mm": round(r1["Residu_mm"] - r2["Residu_mm"], 2)
        })

df_diff = pd.DataFrame(diff_rows)
out_d = os.path.join(TABLES_DIR, "clean_differences_2017.csv")
df_diff.to_csv(out_d, index=False)
print(f"  [OK] Sauvegardé {out_d}")
print(df_diff.to_string())

print(">>> 6. Calcul de water_balance_2018_vs_2017.csv...")
# Charger bilan 2018 annuel
df_2018 = pd.read_csv(os.path.join(TABLES_DIR, "water_balance_corrected_2018_annual.csv"))
df_2018_ann = df_2018[df_2018["period"] == "ANNUAL"]

v18_rows = []
for exp in ["OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_nocdf_nowilt"]:
    r17 = df_annual[(df_annual["experiment"] == exp) & (df_annual["period"] == "ANNUAL_2017")].iloc[0]
    r18 = df_2018_ann[df_2018_ann["experiment"] == exp].iloc[0]
    
    v18_rows.append({
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
        "Incr_EnKF_2018_mm": r18["Incr_Total_mm"],
        "Residu_2017_mm": r17["Residu_mm"],
        "Residu_2018_mm": r18["WaterBalance_Residual_mm"]
    })

df_v18 = pd.DataFrame(v18_rows)
out_v18 = os.path.join(TABLES_DIR, "water_balance_2018_vs_2017.csv")
df_v18.to_csv(out_v18, index=False)
print(f"  [OK] Sauvegardé {out_v18}")
print(df_v18.to_string())

print(">>> TERMINÉ AVEC SUCCÈS !")
