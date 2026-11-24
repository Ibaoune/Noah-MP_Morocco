#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape A2 : Du sol au débit (H6/H7).
Règles :
- Pas de nouveau run (ni LIS ni HyMAP), pas de téléchargement, pas d'interprétation.
- Chiffres générés par script depuis les sorties.
- "absent" si variable/fichier manquant (aucune substitution).
- Sorties : paper1/tables/A2_*.csv, figures A2_*.png, REPORT_A2.md.
"""

import os
import glob
import time
from collections import OrderedDict
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A2.md")
ROOT_REPORT_PATH = os.path.join(BASE_DIR, "REPORT_A2.md")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

def df_to_markdown_simple(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

print("=" * 80)
print("Étape A2 : Du sol au débit (H6/H7)")
print("=" * 80)

# 1. Grilles, Masques et Aires des Bassins
print("\n>>> [1/5] Chargement des grilles et masques des bassins...")
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = (ds_in.variables["LANDMASK"][:] == 1.0)
    dom_lc_181 = np.argmax(ds_in.variables["LANDCOVER"][:], axis=0) + 1
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

ldt_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
with nc.Dataset(ldt_path) as ds_ldt:
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    grid_area = ds_ldt["HYMAP_grid_area"][:]

R, C = flow_x.shape
down_r = np.full((R, C), -1, dtype=int)
down_c = np.full((R, C), -1, dtype=int)
for c in range(C):
    for r in range(R):
        if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
            vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
            if 1 <= vx <= C and 1 <= vy <= R:
                down_c[r, c], down_r[r, c] = vx - 1, vy - 1

parents = {}
for r in range(R):
    for c in range(C):
        pr, pc = down_r[r, c], down_c[r, c]
        if pr >= 0 and pc >= 0:
            parents.setdefault((pr, pc), []).append((r, c))

def get_catchment(outlet_r, outlet_c):
    vis = set([(outlet_r, outlet_c)])
    q = [(outlet_r, outlet_c)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis

cells_lc = get_catchment(75, 71)
cells_sj = get_catchment(71, 71)
cells_az = get_catchment(75, 108)

def make_mask_121(ccells):
    w = np.zeros((121, 181), dtype=bool)
    for r, c in ccells:
        w[r, c] = True
        w[r, c+1] = True
        w[r+1, c] = True
        w[r+1, c+1] = True
    return w & landmask_181

area_lc = sum(grid_area[r, c] for r, c in cells_lc)
area_sj = sum(grid_area[r, c] for r, c in cells_sj)
area_az = sum(grid_area[r, c] for r, c in cells_az)

BASSIN_AREAS = {
    "Lalla Chafia": float(area_lc),
    "Sidi Jabeur": float(area_sj),
    "Sebou amont": float(area_az),
}

REGIONS = OrderedDict([
    ("Domaine complet", landmask_181),
    ("Lalla Chafia", make_mask_121(cells_lc)),
    ("Sidi Jabeur", make_mask_121(cells_sj)),
    ("Sebou amont", make_mask_121(cells_az)),
])

for rname, rmask in REGIONS.items():
    print(f"  Région {rname} : {int(np.count_nonzero(rmask))} mailles valides")

# 2. Chargement des sorties journalières des 6 runs 2018
print("\n>>> [2/5] Chargement des sorties journalières 2018 (365 jours par run)...")
RUNS_2018 = OrderedDict([
    ("OL_DAIC", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_gws": False}),
    ("ENS_OPL", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_gws": True}),
    ("ENS_corr", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_gws": True}),
    ("DA_nocdf", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"), "has_gws": True}),
    ("DA_nocdf_nowilt", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_gws": True}),
    ("DA_corr", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_gws": True}),
])

# État initial au 2018-01-01 00:00 (défini depuis les sorties ou restarts)
f_init_opl = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2017-12/SURFACEMODEL/201801/LIS_HIST_201801010000.d01.nc")
f_init_da = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2017-12/SURFACEMODEL/201801/LIS_HIST_201801010000.d01.nc")

with nc.Dataset(f_init_opl) as ds:
    sm_init_opl = ds.variables["SoilMoist_tavg"][:].squeeze()
    gws_init_opl = ds.variables["GWS_tavg"][:].squeeze() if "GWS_tavg" in ds.variables else None

with nc.Dataset(f_init_da) as ds:
    sm_init_da = ds.variables["SoilMoist_tavg"][:].squeeze()
    gws_init_da = ds.variables["GWS_tavg"][:].squeeze() if "GWS_tavg" in ds.variables else None

INITIAL_STATES = {
    "OL_DAIC": {"sm": sm_init_da, "gws": None},
    "ENS_OPL": {"sm": sm_init_opl, "gws": gws_init_opl},
    "ENS_corr": {"sm": sm_init_da, "gws": gws_init_da},
    "DA_nocdf": {"sm": sm_init_da, "gws": gws_init_da},
    "DA_nocdf_nowilt": {"sm": sm_init_da, "gws": gws_init_da},
    "DA_corr": {"sm": sm_init_da, "gws": gws_init_da},
}

DZ_MM = [100.0, 300.0, 600.0, 1000.0]

def get_day_files(exp_name, pattern):
    files = sorted(glob.glob(pattern, recursive=True))
    day_files = []
    for f in files:
        fname = os.path.basename(f)
        if not fname.startswith("LIS_HIST_") or fname.endswith(".tmp"): continue
        ymd = fname[9:17]
        if "20180102" <= ymd <= "20190101":
            day_files.append((ymd, f))
    day_files = sorted(day_files, key=lambda x: x[0])
    if len(day_files) != 365:
        raise ValueError(f"Exp {exp_name} a {len(day_files)} fichiers (attendu 365)")
    return day_files

daily_data = {}
all_dates = []

for exp_name, cfg in RUNS_2018.items():
    t0 = time.time()
    day_files = get_day_files(exp_name, cfg["pattern"])
    if not all_dates:
        for ymd, _ in day_files:
            dt = pd.to_datetime(ymd) - pd.Timedelta(days=1)
            all_dates.append(dt.strftime("%Y-%m-%d"))
            
    qs_arr = np.zeros((365, 121, 181), dtype=np.float32)
    qsb_arr = np.zeros((365, 121, 181), dtype=np.float32)
    et_arr = np.zeros((365, 121, 181), dtype=np.float32)
    sm_arr = np.zeros((365, 4, 121, 181), dtype=np.float32)
    gws_arr = np.zeros((365, 121, 181), dtype=np.float32) if cfg["has_gws"] else None
    
    # Vérification présence précipitation dans le premier fichier
    with nc.Dataset(day_files[0][1]) as ds_test:
        has_p = ("TotalPrecip_tavg" in ds_test.variables)
    
    p_arr = np.zeros((365, 121, 181), dtype=np.float32) if has_p else None
    
    for d_idx, (ymd, f) in enumerate(day_files):
        with nc.Dataset(f) as ds:
            if has_p:
                p_arr[d_idx] = np.where(ds["TotalPrecip_tavg"][:] > -900, ds["TotalPrecip_tavg"][:].squeeze(), 0.0) * 86400.0
            qs_arr[d_idx] = np.where(ds["Qs_tavg"][:] > -900, ds["Qs_tavg"][:].squeeze(), 0.0) * 86400.0
            qsb_arr[d_idx] = np.where(ds["Qsb_tavg"][:] > -900, ds["Qsb_tavg"][:].squeeze(), 0.0) * 86400.0
            et_arr[d_idx] = np.where(ds["Evap_tavg"][:] > -900, ds["Evap_tavg"][:].squeeze(), 0.0) * 86400.0
            sm_arr[d_idx] = ds["SoilMoist_tavg"][:].squeeze()
            if cfg["has_gws"] and "GWS_tavg" in ds.variables:
                gws_arr[d_idx] = ds["GWS_tavg"][:].squeeze()
                
    daily_data[exp_name] = {
        "P": p_arr, "has_p": has_p, "Qs": qs_arr, "Qsb": qsb_arr, "ET": et_arr,
        "SM": sm_arr, "GWS": gws_arr, "has_gws": cfg["has_gws"]
    }
    t1 = time.time()
    p_str = f"{np.mean(np.sum(p_arr, axis=0)[landmask_181]):.1f} mm" if has_p else "absent (non sorti)"
    print(f"  Exp {exp_name} chargée en {t1-t0:.2f} s. P domaine : {p_str}")

# 3. Partition des écoulements et contrastes (par saison/mois/région)
print("\n>>> [3/5] Calcul de la partition des écoulements et des contrastes...")

# Découpage temporel
TIME_PERIODS = OrderedDict()
TIME_PERIODS["Annuel"] = ("annual", list(range(365)))
# Saisons
season_defs = OrderedDict([
    ("JF+D_2018", [m in [1, 2, 12] for m in pd.to_datetime(all_dates).month]),
    ("MAM", [m in [3, 4, 5] for m in pd.to_datetime(all_dates).month]),
    ("JJA", [m in [6, 7, 8] for m in pd.to_datetime(all_dates).month]),
    ("SON", [m in [9, 10, 11] for m in pd.to_datetime(all_dates).month]),
])
for sname, smask in season_defs.items():
    TIME_PERIODS[sname] = ("seasonal", [i for i, b in enumerate(smask) if b])

# Mois
for m in range(1, 13):
    m_mask = [pd.to_datetime(d).month == m for d in all_dates]
    TIME_PERIODS[f"2018-{m:02d}"] = ("monthly", [i for i, b in enumerate(m_mask) if b])

# Chargement du fichier de contrôle water_balance_upstream_catchments_2018.csv
wb_upstream_path = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")
df_wb_ctrl = pd.read_csv(wb_upstream_path) if os.path.exists(wb_upstream_path) else None

# Pre-agrégation du contrôle par expérience, station et période
ctrl_dict = {}
if df_wb_ctrl is not None:
    for _, row in df_wb_ctrl.iterrows():
        key = (row["station"], row["experiment"], row["year_month"])
        ctrl_dict[key] = {"TotalRunoff": float(row["TotalRunoff_mm"]), "ET": float(row["ET_mm"])}
    
    # Agrégation annuelle et saisonnière pour le contrôle
    for st in ["Lalla Chafia", "Sidi Jabeur"]:
        for exp in df_wb_ctrl["experiment"].unique():
            sub = df_wb_ctrl[(df_wb_ctrl["station"] == st) & (df_wb_ctrl["experiment"] == exp)].copy()
            sub["month"] = pd.to_datetime(sub["year_month"] + "-01").dt.month
            
            # Annuel
            ctrl_dict[(st, exp, "Annuel")] = {"TotalRunoff": float(sub["TotalRunoff_mm"].sum()), "ET": float(sub["ET_mm"].sum())}
            
            # Saisons
            ctrl_dict[(st, exp, "JF+D_2018")] = {
                "TotalRunoff": float(sub[sub["month"].isin([1, 2, 12])]["TotalRunoff_mm"].sum()),
                "ET": float(sub[sub["month"].isin([1, 2, 12])]["ET_mm"].sum())
            }
            ctrl_dict[(st, exp, "MAM")] = {
                "TotalRunoff": float(sub[sub["month"].isin([3, 4, 5])]["TotalRunoff_mm"].sum()),
                "ET": float(sub[sub["month"].isin([3, 4, 5])]["ET_mm"].sum())
            }
            ctrl_dict[(st, exp, "JJA")] = {
                "TotalRunoff": float(sub[sub["month"].isin([6, 7, 8])]["TotalRunoff_mm"].sum()),
                "ET": float(sub[sub["month"].isin([6, 7, 8])]["ET_mm"].sum())
            }
            ctrl_dict[(st, exp, "SON")] = {
                "TotalRunoff": float(sub[sub["month"].isin([9, 10, 11])]["TotalRunoff_mm"].sum()),
                "ET": float(sub[sub["month"].isin([9, 10, 11])]["ET_mm"].sum())
            }

flow_records = []
for exp_name, exp_d in daily_data.items():
    sm_init_exp = INITIAL_STATES[exp_name]["sm"]
    gws_init_exp = INITIAL_STATES[exp_name]["gws"]
    has_p = exp_d["has_p"]
    
    for pname, (ptype, pindices) in TIME_PERIODS.items():
        first_d = pindices[0]
        last_d = pindices[-1]
        
        # État initial au début de la période
        if first_d == 0:
            sm_start = sm_init_exp
            gws_start = gws_init_exp
        else:
            sm_start = exp_d["SM"][first_d - 1]
            gws_start = exp_d["GWS"][first_d - 1] if exp_d["has_gws"] else None
            
        sm_end = exp_d["SM"][last_d]
        gws_end = exp_d["GWS"][last_d] if exp_d["has_gws"] else None
        
        # Sommes de flux sur la période
        p_sum = np.sum(exp_d["P"][pindices], axis=0) if has_p else None
        qs_sum = np.sum(exp_d["Qs"][pindices], axis=0)
        qsb_sum = np.sum(exp_d["Qsb"][pindices], axis=0)
        et_sum = np.sum(exp_d["ET"][pindices], axis=0)
        
        # Delta S par couche
        d_sm_l = [(sm_end[l] - sm_start[l]) * DZ_MM[l] for l in range(4)]
        d_sm_tot = sum(d_sm_l)
        d_gws = (gws_end - gws_start) if exp_d["has_gws"] else None
        
        for rname, rmask in REGIONS.items():
            n_cells = int(np.count_nonzero(rmask))
            qs_val = float(np.mean(qs_sum[rmask]))
            qsb_val = float(np.mean(qsb_sum[rmask]))
            qtot_val = qs_val + qsb_val
            et_val = float(np.mean(et_sum[rmask]))
            
            dsl1 = float(np.mean(d_sm_l[0][rmask]))
            dsl2 = float(np.mean(d_sm_l[1][rmask]))
            dsl3 = float(np.mean(d_sm_l[2][rmask]))
            dsl4 = float(np.mean(d_sm_l[3][rmask]))
            dstot = float(np.mean(d_sm_tot[rmask]))
            dgws_val = round(float(np.mean(d_gws[rmask])), 2) if exp_d["has_gws"] else "absent"
            
            if has_p:
                p_val = float(np.mean(p_sum[rmask]))
                p_str = round(p_val, 2)
                coeff_qs = round(qs_val / p_val, 4) if p_val > 1e-6 else np.nan
                coeff_qsb = round(qsb_val / p_val, 4) if p_val > 1e-6 else np.nan
                coeff_qtot = round(qtot_val / p_val, 4) if p_val > 1e-6 else np.nan
                res_val = round(p_val - et_val - qtot_val - dstot, 2)
            else:
                p_str = "absent"
                coeff_qs = "absent"
                coeff_qsb = "absent"
                coeff_qtot = "absent"
                res_val = "absent"
            
            # Contrôle avec water_balance_upstream_catchments_2018.csv
            ctrl_key = (rname, exp_name, pname)
            if ctrl_key in ctrl_dict:
                c_q = ctrl_dict[ctrl_key]["TotalRunoff"]
                c_et = ctrl_dict[ctrl_key]["ET"]
                diff_q = round(qtot_val - c_q, 2)
                diff_et = round(et_val - c_et, 2)
                c_q_str = round(c_q, 2)
                c_et_str = round(c_et, 2)
            else:
                c_q_str = "absent"
                c_et_str = "absent"
                diff_q = "absent"
                diff_et = "absent"
                
            flow_records.append({
                "period": "2018",
                "experiment": exp_name,
                "region": rname,
                "time_scale": ptype,
                "season_or_month": pname,
                "n_cells": n_cells,
                "P_mm": p_str,
                "Qs_mm": round(qs_val, 2),
                "Qsb_mm": round(qsb_val, 2),
                "TotalRunoff_mm": round(qtot_val, 2),
                "ET_mm": round(et_val, 2),
                "coeff_Qs_over_P": coeff_qs,
                "coeff_Qsb_over_P": coeff_qsb,
                "coeff_TotalRunoff_over_P": coeff_qtot,
                "Delta_S_L1_mm": round(dsl1, 2),
                "Delta_S_L2_mm": round(dsl2, 2),
                "Delta_S_L3_mm": round(dsl3, 2),
                "Delta_S_L4_mm": round(dsl4, 2),
                "Delta_S_total_mm": round(dstot, 2),
                "Delta_GWS_mm": dgws_val,
                "Recharge_mm": "absent",
                "water_balance_check_P_minus_ET_minus_Q_minus_DS_mm": res_val,
                "ctrl_TotalRunoff_upstream_cb_mm": c_q_str,
                "ctrl_ET_upstream_cb_mm": c_et_str,
                "diff_TotalRunoff_vs_upstream_cb_mm": diff_q,
                "diff_ET_vs_upstream_cb_mm": diff_et,
            })

df_flow = pd.DataFrame(flow_records)
out_csv_flow = os.path.join(TABLES_DIR, "A2_flow_partition_runs.csv")
df_flow.to_csv(out_csv_flow, index=False)
print(f"  [OK] Table {out_csv_flow} enregistrée ({len(df_flow)} lignes)")

# 3.2 Contrastes C1, C2, C3, C4
CONTRASTS = [
    ("C1", "ENS_OPL − OL_DAIC", "ENS_OPL", "OL_DAIC"),
    ("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"),
    ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr"),
    ("C4", "DA_nocdf_nowilt − DA_nocdf", "DA_nocdf_nowilt", "DA_nocdf"),
]

contrasts_flow_records = []
for cid, cname, run_a, run_b in CONTRASTS:
    for pname, (ptype, _) in TIME_PERIODS.items():
        for rname in REGIONS.keys():
            row_a = df_flow[(df_flow["experiment"] == run_a) & (df_flow["season_or_month"] == pname) & (df_flow["region"] == rname)].iloc[0]
            row_b = df_flow[(df_flow["experiment"] == run_b) & (df_flow["season_or_month"] == pname) & (df_flow["region"] == rname)].iloc[0]
            
            d_qs = round(float(row_a["Qs_mm"]) - float(row_b["Qs_mm"]), 2)
            d_qsb = round(float(row_a["Qsb_mm"]) - float(row_b["Qsb_mm"]), 2)
            d_qtot = round(float(row_a["TotalRunoff_mm"]) - float(row_b["TotalRunoff_mm"]), 2)
            d_et = round(float(row_a["ET_mm"]) - float(row_b["ET_mm"]), 2)
            d_ds = round(float(row_a["Delta_S_total_mm"]) - float(row_b["Delta_S_total_mm"]), 2)
            
            if row_a["P_mm"] != "absent" and row_b["P_mm"] != "absent":
                d_p = round(float(row_a["P_mm"]) - float(row_b["P_mm"]), 2)
                d_c_qs = round(float(row_a["coeff_Qs_over_P"]) - float(row_b["coeff_Qs_over_P"]), 4) if pd.notnull(row_a["coeff_Qs_over_P"]) and pd.notnull(row_b["coeff_Qs_over_P"]) else np.nan
                d_c_qsb = round(float(row_a["coeff_Qsb_over_P"]) - float(row_b["coeff_Qsb_over_P"]), 4) if pd.notnull(row_a["coeff_Qsb_over_P"]) and pd.notnull(row_b["coeff_Qsb_over_P"]) else np.nan
                d_c_qtot = round(float(row_a["coeff_TotalRunoff_over_P"]) - float(row_b["coeff_TotalRunoff_over_P"]), 4) if pd.notnull(row_a["coeff_TotalRunoff_over_P"]) and pd.notnull(row_b["coeff_TotalRunoff_over_P"]) else np.nan
            else:
                d_p = "absent"
                d_c_qs = "absent"
                d_c_qsb = "absent"
                d_c_qtot = "absent"
            
            if row_a["Delta_GWS_mm"] != "absent" and row_b["Delta_GWS_mm"] != "absent":
                d_gws = round(float(row_a["Delta_GWS_mm"]) - float(row_b["Delta_GWS_mm"]), 2)
            else:
                d_gws = "absent"
                
            contrasts_flow_records.append({
                "period": "2018",
                "contrast_id": cid,
                "contrast_name": cname,
                "region": rname,
                "time_scale": ptype,
                "season_or_month": pname,
                "n_cells": row_a["n_cells"],
                "delta_P_mm": d_p,
                "delta_Qs_mm": d_qs,
                "delta_Qsb_mm": d_qsb,
                "delta_TotalRunoff_mm": d_qtot,
                "delta_ET_mm": d_et,
                "delta_Delta_S_total_mm": d_ds,
                "delta_Delta_GWS_mm": d_gws,
                "delta_coeff_Qs_over_P": d_c_qs,
                "delta_coeff_Qsb_over_P": d_c_qsb,
                "delta_coeff_TotalRunoff_over_P": d_c_qtot,
            })

df_contrasts_flow = pd.DataFrame(contrasts_flow_records)
out_csv_c_flow = os.path.join(TABLES_DIR, "A2_flow_partition_contrasts.csv")
df_contrasts_flow.to_csv(out_csv_c_flow, index=False)
print(f"  [OK] Table {out_csv_c_flow} enregistrée ({len(df_contrasts_flow)} lignes)")

# 4. Événements de pluie et réponse hydrologique
print("\n>>> [4/5] Identification des événements de pluie et analyse de la réponse hydrologique...")

events_per_basin = {}
for bname in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
    bmask = REGIONS[bname]
    daily_p_basin = np.mean(daily_data["ENS_corr"]["P"][:, bmask], axis=1) # shape (365,)
    rainy = daily_p_basin[daily_p_basin >= 1.0]
    p95 = float(np.percentile(rainy, 95))
    is_ev = daily_p_basin >= p95
    events = []
    in_ev = False
    start_idx = 0
    for i in range(len(daily_p_basin)):
        if is_ev[i] and not in_ev:
            in_ev = True
            start_idx = i
        elif not is_ev[i] and in_ev:
            in_ev = False
            events.append((start_idx, i - 1))
    if in_ev:
        events.append((start_idx, len(daily_p_basin) - 1))
    events_per_basin[bname] = {"p95": p95, "events": events, "daily_p": daily_p_basin}
    print(f"  Bassin {bname} : P95 = {p95:.2f} mm ({len(rainy)} jours pluvieux), {len(events)} événements identifiés")

events_records = []
for bname, ev_dict in events_per_basin.items():
    bmask = REGIONS[bname]
    p95 = ev_dict["p95"]
    for ev_id, (s_idx, e_idx) in enumerate(ev_dict["events"], 1):
        ev_label = f"EV{ev_id:02d}"
        s_date = all_dates[s_idx]
        e_date = all_dates[e_idx]
        dur = e_idx - s_idx + 1
        p_event = float(np.sum(ev_dict["daily_p"][s_idx:e_idx+1]))
        
        j0_j5_end = min(s_idx + 5, 364)
        j0_j5_indices = list(range(s_idx, j0_j5_end + 1))
        
        for exp_name, exp_d in daily_data.items():
            # Stock de la veille
            if s_idx == 0:
                sm_eve = INITIAL_STATES[exp_name]["sm"]
            else:
                sm_eve = exp_d["SM"][s_idx - 1]
                
            stk_L = [float(np.mean(sm_eve[l][bmask])) * DZ_MM[l] for l in range(4)]
            stk_tot = sum(stk_L)
            
            qs_cum = float(np.sum(np.mean(exp_d["Qs"][j0_j5_indices][:, bmask], axis=1)))
            qsb_cum = float(np.sum(np.mean(exp_d["Qsb"][j0_j5_indices][:, bmask], axis=1)))
            qtot_cum = qs_cum + qsb_cum
            
            if exp_d["has_p"]:
                p_ev_val = float(np.sum(np.mean(exp_d["P"][s_idx:e_idx+1][:, bmask], axis=1)))
                p_ev_str = round(p_ev_val, 2)
                c_qs = round(qs_cum / p_ev_val, 4) if p_ev_val > 1e-6 else np.nan
                c_qtot = round(qtot_cum / p_ev_val, 4) if p_ev_val > 1e-6 else np.nan
            else:
                p_ev_str = "absent"
                c_qs = "absent"
                c_qtot = "absent"
            
            events_records.append({
                "basin": bname,
                "event_id": ev_label,
                "start_date": s_date,
                "end_date": e_date,
                "duration_days": dur,
                "P95_threshold_mm": round(p95, 2),
                "P_event_mm": p_ev_str,
                "experiment": exp_name,
                "stock_L1_eve_mm": round(stk_L[0], 2),
                "stock_L2_eve_mm": round(stk_L[1], 2),
                "stock_L3_eve_mm": round(stk_L[2], 2),
                "stock_L4_eve_mm": round(stk_L[3], 2),
                "stock_total_eve_mm": round(stk_tot, 2),
                "Qs_cum_j0_j5_mm": round(qs_cum, 2),
                "Qsb_cum_j0_j5_mm": round(qsb_cum, 2),
                "TotalRunoff_cum_j0_j5_mm": round(qtot_cum, 2),
                "runoff_coeff_Qs": c_qs,
                "runoff_coeff_Total": c_qtot,
            })

df_events = pd.DataFrame(events_records)
out_csv_events = os.path.join(TABLES_DIR, "A2_rainfall_events_runoff.csv")
df_events.to_csv(out_csv_events, index=False)
print(f"  [OK] Table {out_csv_events} enregistrée ({len(df_events)} lignes)")

# 4.2 Contrastes C2 et C3 sur les événements et régression linéaire
reg_records = []
for cid, cname, run_a, run_b in [("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"), ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr")]:
    for bname in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
        sub_a = df_events[(df_events["basin"] == bname) & (df_events["experiment"] == run_a)]
        sub_b = df_events[(df_events["basin"] == bname) & (df_events["experiment"] == run_b)]
        
        d_stk_list = []
        d_qtot_list = []
        
        for ev_id in sub_a["event_id"].unique():
            row_a = sub_a[sub_a["event_id"] == ev_id].iloc[0]
            row_b = sub_b[sub_b["event_id"] == ev_id].iloc[0]
            
            d_stk = round(float(row_a["stock_total_eve_mm"]) - float(row_b["stock_total_eve_mm"]), 2)
            d_qtot = round(float(row_a["TotalRunoff_cum_j0_j5_mm"]) - float(row_b["TotalRunoff_cum_j0_j5_mm"]), 2)
            d_qs = round(float(row_a["Qs_cum_j0_j5_mm"]) - float(row_b["Qs_cum_j0_j5_mm"]), 2)
            d_qsb = round(float(row_a["Qsb_cum_j0_j5_mm"]) - float(row_b["Qsb_cum_j0_j5_mm"]), 2)
            
            d_stk_list.append(d_stk)
            d_qtot_list.append(d_qtot)
            
            reg_records.append({
                "record_type": "event",
                "basin": bname,
                "contrast_id": cid,
                "contrast_name": cname,
                "event_id": ev_id,
                "start_date": row_a["start_date"],
                "end_date": row_a["end_date"],
                "P_event_mm": row_a["P_event_mm"],
                "delta_stock_total_eve_mm": d_stk,
                "delta_TotalRunoff_cum_j0_j5_mm": d_qtot,
                "delta_Qs_cum_j0_j5_mm": d_qs,
                "delta_Qsb_cum_j0_j5_mm": d_qsb,
                "slope": np.nan, "intercept": np.nan, "pearson_r": np.nan, "r_squared": np.nan, "p_value": np.nan, "n_events": len(sub_a)
            })
            
        # Régression linéaire sur le bassin
        if len(d_stk_list) >= 3 and np.std(d_stk_list) > 1e-9:
            res_reg = stats.linregress(d_stk_list, d_qtot_list)
            sl, ic, r_val, p_val = res_reg.slope, res_reg.intercept, res_reg.rvalue, res_reg.pvalue
            r2 = r_val ** 2
        else:
            sl, ic, r_val, r2, p_val = np.nan, np.nan, np.nan, np.nan, np.nan
            
        reg_records.append({
            "record_type": "summary_regression",
            "basin": bname,
            "contrast_id": cid,
            "contrast_name": cname,
            "event_id": "ALL_EVENTS",
            "start_date": "ALL",
            "end_date": "ALL",
            "P_event_mm": np.nan,
            "delta_stock_total_eve_mm": round(float(np.mean(d_stk_list)), 2),
            "delta_TotalRunoff_cum_j0_j5_mm": round(float(np.mean(d_qtot_list)), 2),
            "delta_Qs_cum_j0_j5_mm": np.nan,
            "delta_Qsb_cum_j0_j5_mm": np.nan,
            "slope": round(float(sl), 4) if pd.notnull(sl) else np.nan,
            "intercept": round(float(ic), 4) if pd.notnull(ic) else np.nan,
            "pearson_r": round(float(r_val), 4) if pd.notnull(r_val) else np.nan,
            "r_squared": round(float(r2), 4) if pd.notnull(r2) else np.nan,
            "p_value": round(float(p_val), 4) if pd.notnull(p_val) else np.nan,
            "n_events": len(d_stk_list)
        })

df_reg = pd.DataFrame(reg_records)
out_csv_reg = os.path.join(TABLES_DIR, "A2_rainfall_events_contrasts_regression.csv")
df_reg.to_csv(out_csv_reg, index=False)
print(f"  [OK] Table {out_csv_reg} enregistrée ({len(df_reg)} lignes)")

# 5. Débit et métriques aux stations Lalla Chafia et Sidi Jabeur
print("\n>>> [5/5] Calcul des métriques hydrologiques, bootstrap NIC et bilan exutoire vs bassin...")
streamflow_csv_path = os.path.join(TABLES_DIR, "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
df_sf = pd.read_csv(streamflow_csv_path)

def compute_hydrological_metrics(obs_arr, sim_arr, dates_arr=None):
    valid = ~np.isnan(obs_arr) & ~np.isnan(sim_arr)
    o = obs_arr[valid]
    s = sim_arr[valid]
    n = len(o)
    if n < 10:
        return {}
    mu_o = float(np.mean(o))
    mu_s = float(np.mean(s))
    std_o = float(np.std(o, ddof=0))
    std_s = float(np.std(s, ddof=0))
    
    r = float(np.corrcoef(o, s)[0, 1]) if std_o > 1e-12 and std_s > 1e-12 else np.nan
    alpha = float(std_s / std_o) if std_o > 1e-12 else np.nan
    beta = float(mu_s / mu_o) if mu_o > 1e-12 else np.nan
    gamma = float(alpha / beta) if (pd.notnull(alpha) and pd.notnull(beta) and beta > 1e-12) else np.nan
    
    kge_2012 = float(1.0 - np.sqrt((r - 1.0)**2 + (gamma - 1.0)**2 + (beta - 1.0)**2)) if (pd.notnull(r) and pd.notnull(gamma) and pd.notnull(beta)) else np.nan
    kge_2009 = float(1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)) if (pd.notnull(r) and pd.notnull(alpha) and pd.notnull(beta)) else np.nan
    
    ss_tot = np.sum((o - mu_o)**2)
    nse = float(1.0 - np.sum((s - o)**2) / ss_tot) if ss_tot > 1e-12 else np.nan
    
    bias_m3s = float(mu_s - mu_o)
    vol_bias_pct = float(bias_m3s / mu_o * 100.0) if mu_o > 1e-12 else np.nan
    
    peak_obs = float(np.max(o))
    peak_sim = float(np.max(s))
    
    if dates_arr is not None:
        d = np.array(dates_arr)[valid]
        peak_obs_date = str(d[np.argmax(o)])
        peak_sim_date = str(d[np.argmax(s)])
        peak_timing = int((pd.to_datetime(peak_sim_date) - pd.to_datetime(peak_obs_date)).days)
    else:
        peak_obs_date = ""
        peak_sim_date = ""
        peak_timing = np.nan
        
    peak_bias = peak_sim - peak_obs
    
    return {
        "n_days": n, "mean_obs_m3s": round(mu_o, 3), "mean_sim_m3s": round(mu_s, 3),
        "kge_2012": round(kge_2012, 4), "r": round(r, 4), "beta": round(beta, 4), "gamma": round(gamma, 4),
        "kge_2009": round(kge_2009, 4), "alpha": round(alpha, 4), "nse": round(nse, 4),
        "volume_bias_m3s": round(bias_m3s, 3),
        "rel_volume_bias_pct": round(vol_bias_pct, 2),
        "peak_obs_m3s": round(peak_obs, 2), "peak_obs_date": peak_obs_date,
        "peak_sim_m3s": round(peak_sim, 2), "peak_sim_date": peak_sim_date,
        "peak_bias_m3s": round(peak_bias, 2), "peak_timing_days": peak_timing
    }

def moving_block_bootstrap_nic(obs_arr, sim_t_arr, sim_r_arr, block_len=30, n_boot=1000):
    valid = ~np.isnan(obs_arr) & ~np.isnan(sim_t_arr) & ~np.isnan(sim_r_arr)
    o = obs_arr[valid]
    st = sim_t_arr[valid]
    sr = sim_r_arr[valid]
    n = len(o)
    if n < block_len * 2:
        return np.nan, np.nan, np.nan
    num_blocks = int(np.ceil(n / block_len))
    max_start = n - block_len + 1
    rng = np.random.RandomState(42)
    nic_dist = []
    for _ in range(n_boot):
        starts = rng.randint(0, max_start, size=num_blocks)
        indices = np.concatenate([np.arange(s, s + block_len) for s in starts])[:n]
        o_b, st_b, sr_b = o[indices], st[indices], sr[indices]
        
        m_t = compute_hydrological_metrics(o_b, st_b)
        m_r = compute_hydrological_metrics(o_b, sr_b)
        
        kt = m_t.get("kge_2012", np.nan)
        kr = m_r.get("kge_2012", np.nan)
        
        if pd.notnull(kt) and pd.notnull(kr) and abs(1.0 - kr) > 1e-6:
            nic_dist.append((kt - kr) / (1.0 - kr))
            
    if not nic_dist:
        return np.nan, np.nan, np.nan
    return round(float(np.mean(nic_dist)), 4), round(float(np.percentile(nic_dist, 2.5)), 4), round(float(np.percentile(nic_dist, 97.5)), 4)

sf_metrics_records = []
sf_runs = ["OL_DAIC", "ENS_OPL", "ENS_corr", "DA_nocdf", "DA_nocdf_nowilt", "DA_corr", "OPL", "DA_cdf"]

for st_col, st_name in [("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]:
    obs_series = df_sf[f"obs_{st_col}"].values
    dates_series = df_sf["date"].values
    
    metrics_by_exp = {}
    for exp in sf_runs:
        col = f"{exp}_{st_col}"
        if col in df_sf.columns:
            sim_series = df_sf[col].values
            m = compute_hydrological_metrics(obs_series, sim_series, dates_series)
            metrics_by_exp[exp] = m
        else:
            metrics_by_exp[exp] = None
            
    # Calcul des NIC pour C1, C2, C3, C4
    nic_pairs = {
        "C1": ("ENS_OPL", "OL_DAIC"),
        "C2": ("DA_nocdf", "ENS_OPL"),
        "C3": ("DA_corr", "ENS_corr"),
        "C4": ("DA_nocdf_nowilt", "DA_nocdf"),
    }
    nic_by_exp = {exp: ("none", "none", np.nan, np.nan, np.nan, np.nan) for exp in sf_runs}
    for cid, (t_exp, r_exp) in nic_pairs.items():
        if metrics_by_exp[t_exp] and metrics_by_exp[r_exp]:
            kt = metrics_by_exp[t_exp]["kge_2012"]
            kr = metrics_by_exp[r_exp]["kge_2012"]
            val_nic = round((kt - kr) / (1.0 - kr), 4) if abs(1.0 - kr) > 1e-6 else np.nan
            b_mean, b_low, b_high = moving_block_bootstrap_nic(obs_series, df_sf[f"{t_exp}_{st_col}"].values, df_sf[f"{r_exp}_{st_col}"].values)
            nic_by_exp[t_exp] = (cid, r_exp, val_nic, b_mean, b_low, b_high)

    for exp in sf_runs:
        m = metrics_by_exp[exp]
        cid, r_exp, nic_val, nic_bm, nic_bl, nic_bh = nic_by_exp[exp]
        if m:
            sf_metrics_records.append({
                "period": "2018",
                "station": st_name,
                "station_id": f"b_{st_col[0]}_{st_col[6:]}",
                "experiment": exp,
                "status": "routed",
                "file_used": "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv",
                **m,
                "nic_contrast_id": cid,
                "nic_reference_run": r_exp,
                "nic_kge_2012": nic_val,
                "nic_bootstrap_mean": nic_bm,
                "nic_bootstrap_ci_low": nic_bl,
                "nic_bootstrap_ci_high": nic_bh
            })
        else:
            sf_metrics_records.append({
                "period": "2018",
                "station": st_name,
                "station_id": f"b_{st_col[0]}_{st_col[6:]}",
                "experiment": exp,
                "status": "absent",
                "file_used": "absent"
            })

# Ajout explicite de Sebou amont (non routé en journalier 2018)
for exp in sf_runs:
    sf_metrics_records.append({
        "period": "2018",
        "station": "Sebou amont",
        "station_id": "b_az_upstream",
        "experiment": exp,
        "status": "absent (non routé en journalier 2018)",
        "file_used": "absent",
        "n_days": "absent", "mean_obs_m3s": "absent", "mean_sim_m3s": "absent",
        "kge_2012": "absent", "r": "absent", "beta": "absent", "gamma": "absent",
        "kge_2009": "absent", "alpha": "absent", "nse": "absent",
        "volume_bias_m3s": "absent", "rel_volume_bias_pct": "absent",
        "peak_obs_m3s": "absent", "peak_obs_date": "absent",
        "peak_sim_m3s": "absent", "peak_sim_date": "absent",
        "peak_bias_m3s": "absent", "peak_timing_days": "absent",
        "nic_contrast_id": "absent", "nic_reference_run": "absent",
        "nic_kge_2012": "absent", "nic_bootstrap_mean": "absent",
        "nic_bootstrap_ci_low": "absent", "nic_bootstrap_ci_high": "absent"
    })

df_sf_metrics = pd.DataFrame(sf_metrics_records)
out_csv_sf = os.path.join(TABLES_DIR, "A2_streamflow_metrics_stations.csv")
df_sf_metrics.to_csv(out_csv_sf, index=False)
print(f"  [OK] Table {out_csv_sf} enregistrée ({len(df_sf_metrics)} lignes)")

# 5.2 Comparaison Delta volume exutoire vs Delta (Qs+Qsb) pour C2 et C3
sf_comp_records = []
for cid, cname, run_a, run_b in [("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"), ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr")]:
    for st_col, st_name in [("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]:
        basin_area = BASSIN_AREAS[st_name]
        q_a_series = df_sf[f"{run_a}_{st_col}"].values
        q_b_series = df_sf[f"{run_b}_{st_col}"].values
        
        # Période annuelle
        v_a_ann = float(np.sum(q_a_series) * 86400.0)
        v_b_ann = float(np.sum(q_b_series) * 86400.0)
        d_v_ann = v_a_ann - v_b_ann
        d_r_ann_mm = (d_v_ann / basin_area) * 1000.0
        
        # Runoff généré sur le bassin (depuis flow partition contrasts)
        c_row_ann = df_contrasts_flow[(df_contrasts_flow["contrast_id"] == cid) & (df_contrasts_flow["region"] == st_name) & (df_contrasts_flow["season_or_month"] == "Annuel")].iloc[0]
        d_qtot_ann_mm = float(c_row_ann["delta_TotalRunoff_mm"])
        d_qtot_ann_vol_m3 = (d_qtot_ann_mm / 1000.0) * basin_area
        ratio_ann = round(d_v_ann / d_qtot_ann_vol_m3, 4) if abs(d_qtot_ann_vol_m3) > 1e-4 else np.nan
        
        sf_comp_records.append({
            "station": st_name,
            "contrast_id": cid,
            "contrast_name": cname,
            "time_scale": "annual",
            "season_or_month": "Annuel",
            "basin_area_km2": round(basin_area / 1e6, 2),
            "delta_streamflow_volume_m3": round(d_v_ann, 1),
            "delta_streamflow_depth_mm": round(d_r_ann_mm, 2),
            "delta_TotalRunoff_volume_m3": round(d_qtot_ann_vol_m3, 1),
            "delta_TotalRunoff_depth_mm": round(d_qtot_ann_mm, 2),
            "ratio_streamflow_over_runoff": ratio_ann
        })
        
        # Périodes mensuelles
        for m in range(1, 13):
            m_mask = [pd.to_datetime(d).month == m for d in df_sf["date"]]
            v_a_m = float(np.sum(q_a_series[m_mask]) * 86400.0)
            v_b_m = float(np.sum(q_b_series[m_mask]) * 86400.0)
            d_v_m = v_a_m - v_b_m
            d_r_m_mm = (d_v_m / basin_area) * 1000.0
            
            c_row_m = df_contrasts_flow[(df_contrasts_flow["contrast_id"] == cid) & (df_contrasts_flow["region"] == st_name) & (df_contrasts_flow["season_or_month"] == f"2018-{m:02d}")].iloc[0]
            d_qtot_m_mm = float(c_row_m["delta_TotalRunoff_mm"])
            d_qtot_m_vol_m3 = (d_qtot_m_mm / 1000.0) * basin_area
            ratio_m = round(d_v_m / d_qtot_m_vol_m3, 4) if abs(d_qtot_m_vol_m3) > 1e-4 else np.nan
            
            sf_comp_records.append({
                "station": st_name,
                "contrast_id": cid,
                "contrast_name": cname,
                "time_scale": "monthly",
                "season_or_month": f"2018-{m:02d}",
                "basin_area_km2": round(basin_area / 1e6, 2),
                "delta_streamflow_volume_m3": round(d_v_m, 1),
                "delta_streamflow_depth_mm": round(d_r_m_mm, 2),
                "delta_TotalRunoff_volume_m3": round(d_qtot_m_vol_m3, 1),
                "delta_TotalRunoff_depth_mm": round(d_qtot_m_mm, 2),
                "ratio_streamflow_over_runoff": ratio_m
            })

df_sf_comp = pd.DataFrame(sf_comp_records)
out_csv_sf_comp = os.path.join(TABLES_DIR, "A2_streamflow_vs_runoff_contrasts.csv")
df_sf_comp.to_csv(out_csv_sf_comp, index=False)
print(f"  [OK] Table {out_csv_sf_comp} enregistrée ({len(df_sf_comp)} lignes)")

# 6. Figures PNG
print("\n>>> Génération des figures depuis les CSV...")

# 6.1 Hydrogrammes observés vs simulés par station
fig, axes = plt.subplots(2, 1, figsize=(14, 8), dpi=300, sharex=True)
dates_dt = pd.to_datetime(df_sf["date"]).values

for idx, (st_col, st_name) in enumerate([("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]):
    ax = axes[idx]
    ax.plot(dates_dt, df_sf[f"obs_{st_col}"].values, color="black", linewidth=1.5, label="Observé", zorder=5)
    ax.plot(dates_dt, df_sf[f"OL_DAIC_{st_col}"].values, color="#7f7f7f", linestyle="--", linewidth=1.0, label="OL_DAIC")
    ax.plot(dates_dt, df_sf[f"ENS_OPL_{st_col}"].values, color="#1f77b4", linewidth=1.1, label="ENS_OPL")
    ax.plot(dates_dt, df_sf[f"ENS_corr_{st_col}"].values, color="#2ca02c", linewidth=1.1, label="ENS_corr")
    ax.plot(dates_dt, df_sf[f"DA_nocdf_{st_col}"].values, color="#d62728", linewidth=1.1, label="DA_nocdf")
    ax.plot(dates_dt, df_sf[f"DA_corr_{st_col}"].values, color="#9467bd", linewidth=1.2, label="DA_corr")
    ax.set_yscale("log")
    ax.set_ylabel("Débit ($m^3/s$)", fontsize=10)
    ax.set_title(f"Hydrogramme journalier 2018 — Station {st_name}", fontsize=11, fontweight="bold")
    ax.grid(True, which="both", linestyle=":", alpha=0.5)
    ax.legend(loc="upper right", frameon=True, fontsize=8, ncol=3)

axes[1].set_xlabel("Date (2018)", fontsize=10)
plt.tight_layout()
out_fig_hydro = os.path.join(FIGURES_DIR, "A2_streamflow_hydrographs_2018.png")
plt.savefig(out_fig_hydro)
plt.close()
print(f"  [OK] Figure {out_fig_hydro} enregistrée")

# 6.2 Barres Qs, Qsb, ET, Delta_S par contraste et bassin (Annuel)
fig, axes = plt.subplots(1, 3, figsize=(15, 5), dpi=300, sharey=True)
sub_bar = df_contrasts_flow[(df_contrasts_flow["season_or_month"] == "Annuel") & (df_contrasts_flow["region"].isin(["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]))]

basins = ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]
components = ["delta_Qs_mm", "delta_Qsb_mm", "delta_ET_mm", "delta_Delta_S_total_mm"]
comp_labels = ["ΔQs", "ΔQsb", "ΔET", "Δ(ΔS)"]
colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

for b_idx, bname in enumerate(basins):
    ax = axes[b_idx]
    sub_b = sub_bar[sub_bar["region"] == bname]
    x = np.arange(4) # C1, C2, C3, C4
    width = 0.2
    for c_idx, comp in enumerate(components):
        vals = [sub_b[sub_b["contrast_id"] == cid][comp].values[0] for cid in ["C1", "C2", "C3", "C4"]]
        ax.bar(x + (c_idx - 1.5) * width, vals, width, label=comp_labels[c_idx], color=colors[c_idx], alpha=0.85)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax.set_xticks(x)
    ax.set_xticklabels(["C1", "C2", "C3", "C4"], fontsize=10, fontweight="bold")
    ax.set_title(f"Bassin {bname}", fontsize=11, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5, axis="y")
    if b_idx == 0:
        ax.set_ylabel("Variation annuelle (mm/an)", fontsize=10)
        ax.legend(frameon=True, fontsize=9)

plt.suptitle("Décomposition annuelle des bilans par contraste et par bassin (2018)", fontsize=12, fontweight="bold", y=0.98)
plt.tight_layout()
out_fig_bars = os.path.join(FIGURES_DIR, "A2_flow_partition_bars.png")
plt.savefig(out_fig_bars)
plt.close()
print(f"  [OK] Figure {out_fig_bars} enregistrée")

# 6.3 Nuage Delta stock veille vs Delta écoulement événementiel pour C2 et C3
fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
ev_reg_sub = df_reg[df_reg["record_type"] == "event"]

marker_dict = {"Lalla Chafia": "o", "Sidi Jabeur": "s", "Sebou amont": "^"}
color_dict = {"Lalla Chafia": "#1f77b4", "Sidi Jabeur": "#ff7f0e", "Sebou amont": "#2ca02c"}

for idx, cid in enumerate(["C2", "C3"]):
    ax = axes[idx]
    sub_c = ev_reg_sub[ev_reg_sub["contrast_id"] == cid]
    for bname in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
        sub_b = sub_c[sub_c["basin"] == bname]
        ax.scatter(sub_b["delta_stock_total_eve_mm"].values, sub_b["delta_TotalRunoff_cum_j0_j5_mm"].values,
                   label=bname, marker=marker_dict[bname], color=color_dict[bname], s=50, alpha=0.85)
        
    # Ligne de régression globale par bassin
    for bname in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
        sum_row = df_reg[(df_reg["record_type"] == "summary_regression") & (df_reg["contrast_id"] == cid) & (df_reg["basin"] == bname)].iloc[0]
        sl = sum_row["slope"]
        ic = sum_row["intercept"]
        r_val = sum_row["pearson_r"]
        if pd.notnull(sl) and pd.notnull(ic):
            x_vals = sub_c[sub_c["basin"] == bname]["delta_stock_total_eve_mm"].values
            if len(x_vals) >= 2:
                x_fit = np.linspace(min(x_vals), max(x_vals), 50)
                ax.plot(x_fit, sl * x_fit + ic, color=color_dict[bname], linestyle="--", linewidth=1.0,
                        label=f"{bname} fit (r={r_val:.2f}, sl={sl:.2f})")
                
    ax.axhline(0, color="black", linestyle=":", linewidth=0.8)
    ax.axvline(0, color="black", linestyle=":", linewidth=0.8)
    ax.set_xlabel("Δ Stock du sol veille de l'événement (mm)", fontsize=10)
    ax.set_ylabel("Δ(Qs+Qsb) cumulé J0→J+5 (mm)", fontsize=10)
    ax.set_title(f"Contraste {cid} ({'DA_nocdf − ENS_OPL' if cid=='C2' else 'DA_corr − ENS_corr'})", fontsize=11, fontweight="bold")
    ax.grid(True, linestyle=":", alpha=0.5)
    ax.legend(frameon=True, fontsize=8)

plt.suptitle("Sensibilité de la réponse en écoulement au stock initial du sol (2018)", fontsize=12, fontweight="bold", y=0.98)
plt.tight_layout()
out_fig_scatter = os.path.join(FIGURES_DIR, "A2_rainfall_events_scatter.png")
plt.savefig(out_fig_scatter)
plt.close()
print(f"  [OK] Figure {out_fig_scatter} enregistrée")

# 7. Génération du rapport factuel REPORT_A2.md
print("\n>>> Génération de REPORT_A2.md (tableaux uniquement)...")

rep_lines = [
    "# Rapport d'Étape A2 — Du sol au débit (H6/H7)",
    "",
    "Ce rapport présente strictement les tableaux générés par script depuis les sorties brutes et les tables de l'étape A2.",
    "Conformément aux consignes, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.",
    "",
    "## 1. Partition Annuelle des Écoulements et Bilan Hydrique (2018)",
    "",
    "### 1.1 Totaux Annuels par Expérience et par Région",
    ""
]

sub_t1 = df_flow[df_flow["season_or_month"] == "Annuel"]
cols_t1 = ["experiment", "region", "n_cells", "P_mm", "Qs_mm", "Qsb_mm", "TotalRunoff_mm", "ET_mm", "coeff_TotalRunoff_over_P", "Delta_S_total_mm", "Delta_GWS_mm", "water_balance_check_P_minus_ET_minus_Q_minus_DS_mm", "diff_TotalRunoff_vs_upstream_cb_mm", "diff_ET_vs_upstream_cb_mm"]
rep_lines.append(df_to_markdown_simple(sub_t1[cols_t1]))

rep_lines.extend([
    "",
    "### 1.2 Contrastes Annuels C1, C2, C3, C4 de Partition des Écoulements",
    ""
])
sub_t2 = df_contrasts_flow[df_contrasts_flow["season_or_month"] == "Annuel"]
cols_t2 = ["contrast_id", "contrast_name", "region", "delta_P_mm", "delta_Qs_mm", "delta_Qsb_mm", "delta_TotalRunoff_mm", "delta_ET_mm", "delta_Delta_S_total_mm", "delta_Delta_GWS_mm", "delta_coeff_TotalRunoff_over_P"]
rep_lines.append(df_to_markdown_simple(sub_t2[cols_t2]))

rep_lines.extend([
    "",
    "---",
    "",
    "## 2. Événements de Pluie et Réponse Hydrologique (2018)",
    "",
    "### 2.1 Synthèse des Événements et Ruissellement Cumulé J0→J+5",
    ""
])
cols_t3 = ["basin", "event_id", "start_date", "end_date", "duration_days", "P_event_mm", "experiment", "stock_total_eve_mm", "Qs_cum_j0_j5_mm", "Qsb_cum_j0_j5_mm", "TotalRunoff_cum_j0_j5_mm", "runoff_coeff_Total"]
rep_lines.append(df_to_markdown_simple(df_events[cols_t3]))

rep_lines.extend([
    "",
    "### 2.2 Régression Linéaire : Δ(Qs+Qsb) vs ΔStock veille (C2 et C3)",
    ""
])
sub_t4 = df_reg[df_reg["record_type"] == "summary_regression"]
cols_t4 = ["basin", "contrast_id", "contrast_name", "n_events", "delta_stock_total_eve_mm", "delta_TotalRunoff_cum_j0_j5_mm", "slope", "intercept", "pearson_r", "r_squared", "p_value"]
rep_lines.append(df_to_markdown_simple(sub_t4[cols_t4]))

rep_lines.extend([
    "",
    "---",
    "",
    "## 3. Débit et Métriques aux Stations (2018)",
    "",
    "### 3.1 Performance KGE 2012, Composantes, Biais et Débit de Pointe",
    ""
])
cols_t5 = ["station", "experiment", "status", "n_days", "kge_2012", "r", "beta", "gamma", "nse", "volume_bias_m3s", "rel_volume_bias_pct", "peak_sim_m3s", "peak_sim_date", "peak_bias_m3s", "peak_timing_days", "nic_contrast_id", "nic_reference_run", "nic_kge_2012", "nic_bootstrap_mean", "nic_bootstrap_ci_low", "nic_bootstrap_ci_high"]
rep_lines.append(df_to_markdown_simple(df_sf_metrics[cols_t5]))

rep_lines.extend([
    "",
    "### 3.2 Comparaison Annuelle et Mensuelle : Δ Débit Exutoire vs Δ(Qs+Qsb) Bassin (C2 et C3)",
    ""
])
cols_t6 = ["station", "contrast_id", "time_scale", "season_or_month", "delta_streamflow_volume_m3", "delta_streamflow_depth_mm", "delta_TotalRunoff_volume_m3", "delta_TotalRunoff_depth_mm", "ratio_streamflow_over_runoff"]
rep_lines.append(df_to_markdown_simple(df_sf_comp[cols_t6]))

rep_lines.extend([
    "",
    "---",
    "",
    "## 4. Liste des Fichiers Produits",
    "",
    "### Tables CSV :",
    "- `paper1/tables/A2_flow_partition_runs.csv`",
    "- `paper1/tables/A2_flow_partition_contrasts.csv`",
    "- `paper1/tables/A2_rainfall_events_runoff.csv`",
    "- `paper1/tables/A2_rainfall_events_contrasts_regression.csv`",
    "- `paper1/tables/A2_streamflow_metrics_stations.csv`",
    "- `paper1/tables/A2_streamflow_vs_runoff_contrasts.csv`",
    "",
    "### Figures PNG :",
    "- `paper1/figures/A2_streamflow_hydrographs_2018.png`",
    "- `paper1/figures/A2_flow_partition_bars.png`",
    "- `paper1/figures/A2_rainfall_events_scatter.png`",
    "",
    "### Scripts :",
    "- `scripts/paper1/step_a2_soil_to_streamflow.py`",
    "- `paper1/scripts/step_a2_soil_to_streamflow.py`",
    ""
])

with open(REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_lines))

with open(ROOT_REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_lines))

print(f"  [OK] Rapports {REPORT_PATH} et {ROOT_REPORT_PATH} générés avec succès !")
os.system("cp scripts/paper1/step_a2_soil_to_streamflow.py paper1/scripts/step_a2_soil_to_streamflow.py")
print("  [OK] Script copié dans paper1/scripts/")
print("=" * 80)
