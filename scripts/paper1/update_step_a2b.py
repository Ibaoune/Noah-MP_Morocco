#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Step A2b — Corrections du bilan A2.
- Bilan annuel : Delta S sol et Delta GWS calculés depuis les restarts au 2018-01-01 et 2019-01-01.
- État initial lu dans experiment_definitions_2018.csv (colonne initial_state).
- Résidu = P - ET - Qs - Qsb - Delta_S_sol - Delta_GWS.
- Contrôle domaine : retrouver les résidus validés de water_balance_corrected_2018_annual.csv (écart en colonne).
- Mensuel/saisonnier : stock depuis moyennes journalières, nommé DeltaS_from_daily_means, résidu non calculé ("N/A").
- Bassins : mêmes masques/poids que calc_catchment_water_balance.py (écart à water_balance_upstream_catchments_2018.csv ≈ 0).
- Régénérer uniquement A2_flow_partition_runs.csv, A2_flow_partition_contrasts.csv, A2_flow_partition_bars.png, REPORT_A2.md.
- Ajouter A2_peak_timing.csv : 3 plus grands pics (date, valeur) et pluie de bassin ENS_corr des 10 jours précédant chaque pic.
"""

import os
import glob
from collections import OrderedDict
import netCDF4 as nc
import numpy as np
import pandas as pd
from scipy.signal import find_peaks
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A2.md")
ROOT_REPORT_PATH = os.path.join(BASE_DIR, "REPORT_A2.md")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
DEFS_FILE = os.path.join(TABLES_DIR, "experiment_definitions_2018.csv")
WB_ANNUAL_CTRL = os.path.join(TABLES_DIR, "water_balance_corrected_2018_annual.csv")
WB_UPSTREAM_CTRL = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

print("=" * 80)
print("Step A2b — Corrections du bilan A2")
print("=" * 80)

# 1. Delimitation HyMAP D8 et calcul des poids
print("\n>>> [1/6] Chargement de la grille et des poids des bassins...")
with nc.Dataset(LDT_FILE) as ds:
    flow_x = ds["HYMAP_flow_direction_x"][:]
    flow_y = ds["HYMAP_flow_direction_y"][:]
    area_180 = ds["HYMAP_grid_area"][:].filled(0.0)

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

catchments = OrderedDict([
    ("Lalla Chafia", cells_lc),
    ("Sidi Jabeur", cells_sj),
    ("Sebou amont", cells_az),
])

weights_180 = {}
weights_181 = {}

for cname, ccells in catchments.items():
    tot_area = sum(area_180[r, c] for r, c in ccells)
    w180 = np.zeros((120, 180), dtype=float)
    for r, c in ccells:
        w180[r, c] = area_180[r, c] / tot_area
    weights_180[cname] = w180
    
    w181 = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        a = area_180[r, c]
        w181[r, c] += 0.25 * a
        w181[r, c+1] += 0.25 * a
        w181[r+1, c] += 0.25 * a
        w181[r+1, c+1] += 0.25 * a
    weights_181[cname] = w181 / np.sum(w181)

# Mapping tuiles LIS vers (121, 181)
f_sample = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc")
with nc.Dataset(f_sample) as ds:
    lat_tile = ds["lat"][:]
    lon_tile = ds["lon"][:]
    tile_c = np.round((lon_tile - (-10.0)) / 0.05).astype(int)
    tile_r = np.round((lat_tile - 30.0) / 0.05).astype(int)

# Masque domaine complet (16030 tuiles)
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = (ds_in.variables["LANDMASK"][:] == 1.0)

# 2. Lecture des restarts initiaux et finaux pour le bilan annuel
print("\n>>> [2/6] Extraction des restarts au 2018-01-01 et 2019-01-01...")
df_defs = pd.read_csv(DEFS_FILE)

EXP_RUNS = ["OL_DAIC", "ENS_OPL", "ENS_corr", "DA_nocdf", "DA_nocdf_nowilt", "DA_corr"]

END_RESTARTS = {
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
    "ENS_corr": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-12/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
    "DA_corr": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"),
}

def read_restart_fields(fp):
    with nc.Dataset(fp) as ds:
        smc = ds.variables["SMC"][:]
        wa = ds.variables["WA"][:]
        can = ds.variables["CANWAT"][:]
        sn = ds.variables["SNEQV"][:]
        
        if smc.ndim == 3: # (4, ntiles, nens)
            smc_m = np.mean(smc, axis=2)
            wa_m = np.mean(wa, axis=1)
            can_m = np.mean(can, axis=1)
            sn_m = np.mean(sn, axis=1)
        elif smc.ndim == 2 and smc.shape[1] == 320600:
            smc_m = np.mean(smc.reshape(4, 16030, 20), axis=2)
            wa_m = np.mean(wa.reshape(16030, 20), axis=1)
            can_m = np.mean(can.reshape(16030, 20), axis=1)
            sn_m = np.mean(sn.reshape(16030, 20), axis=1)
        else:
            smc_m, wa_m, can_m, sn_m = smc, wa, can, sn
            
        smc_layers_mm = smc_m * dz[:, None] * 1000.0 # shape (4, 16030)
        smc_tot_mm = np.sum(smc_layers_mm, axis=0) # shape (16030,)
        tot_tile_mm = smc_tot_mm + wa_m + can_m + sn_m
        other_tile_mm = can_m + sn_m
        
        # Mapping 2D
        grid_smc_layers = np.full((4, 121, 181), np.nan)
        grid_smc_tot = np.full((121, 181), np.nan)
        grid_wa = np.full((121, 181), np.nan)
        grid_other = np.full((121, 181), np.nan)
        grid_tot = np.full((121, 181), np.nan)
        
        for l in range(4):
            grid_smc_layers[l, tile_r, tile_c] = smc_layers_mm[l]
        grid_smc_tot[tile_r, tile_c] = smc_tot_mm
        grid_wa[tile_r, tile_c] = wa_m
        grid_other[tile_r, tile_c] = other_tile_mm
        grid_tot[tile_r, tile_c] = tot_tile_mm
        
        return {
            "smc_layers": smc_layers_mm, "smc_tot": smc_tot_mm, "wa": wa_m, "other": other_tile_mm, "tot": tot_tile_mm,
            "grid_smc_layers": grid_smc_layers, "grid_smc_tot": grid_smc_tot,
            "grid_wa": grid_wa, "grid_other": grid_other, "grid_tot": grid_tot
        }

annual_restart_deltas = {}
for exp in EXP_RUNS:
    init_fp = df_defs[df_defs["experiment"] == exp]["initial_state"].values[0]
    end_fp = END_RESTARTS[exp]
    
    rst_start = read_restart_fields(init_fp)
    rst_end = read_restart_fields(end_fp)
    
    annual_restart_deltas[exp] = {
        # Domaine
        "dom_d_smc_l": [float(np.mean(rst_end["smc_layers"][l] - rst_start["smc_layers"][l])) for l in range(4)],
        "dom_d_smc_tot": float(np.mean(rst_end["smc_tot"] - rst_start["smc_tot"])),
        "dom_d_wa": float(np.mean(rst_end["wa"] - rst_start["wa"])),
        "dom_d_other": float(np.mean(rst_end["other"] - rst_start["other"])),
        "dom_d_tot": float(np.mean(rst_end["tot"] - rst_start["tot"])),
        # 2D grids
        "grid_d_smc_l": rst_end["grid_smc_layers"] - rst_start["grid_smc_layers"],
        "grid_d_smc_tot": rst_end["grid_smc_tot"] - rst_start["grid_smc_tot"],
        "grid_d_wa": rst_end["grid_wa"] - rst_start["grid_wa"],
        "grid_d_other": rst_end["grid_other"] - rst_start["grid_other"],
        "grid_d_tot": rst_end["grid_tot"] - rst_start["grid_tot"]
    }

# 3. Chargement des tables validées de contrôle
df_ann_ctrl = pd.read_csv(WB_ANNUAL_CTRL)
dom_ctrl_dict = {}
for _, r in df_ann_ctrl[df_ann_ctrl["period"] == "ANNUAL"].iterrows():
    dom_ctrl_dict[r["experiment"]] = {
        "P": float(r["P_mm"]), "ET": float(r["ET_mm"]),
        "Qs": float(r["Qs_mm"]), "Qsb": float(r["Qsb_mm"]), "TotalRunoff": float(r["TotalRunoff_mm"]),
        "Delta_S": float(r["Delta_S_mm"]), "Residual": float(r["WaterBalance_Residual_mm"])
    }

df_cb_ctrl = pd.read_csv(WB_UPSTREAM_CTRL)
cb_ctrl_dict = {}
for _, r in df_cb_ctrl.iterrows():
    key = (r["station"], r["experiment"], r["year_month"])
    cb_ctrl_dict[key] = {
        "P": float(r["P_mm"]), "ET": float(r["ET_mm"]),
        "Qs": float(r["Qs_mm"]), "Qsb": float(r["Qsb_mm"]), "TotalRunoff": float(r["TotalRunoff_mm"]),
        "Delta_S": float(r["Delta_S_mm"]), "Residual": float(r["WaterBalance_Residual_mm"])
    }

for st in ["Lalla Chafia", "Sidi Jabeur"]:
    for exp in df_cb_ctrl["experiment"].unique():
        sub = df_cb_ctrl[(df_cb_ctrl["station"] == st) & (df_cb_ctrl["experiment"] == exp)].copy()
        sub["month"] = pd.to_datetime(sub["year_month"] + "-01").dt.month
        cb_ctrl_dict[(st, exp, "Annuel")] = {
            "P": float(sub["P_mm"].sum()), "ET": float(sub["ET_mm"].sum()),
            "Qs": float(sub["Qs_mm"].sum()), "Qsb": float(sub["Qsb_mm"].sum()),
            "TotalRunoff": float(sub["TotalRunoff_mm"].sum()),
            "Delta_S": float(sub["Delta_S_mm"].sum()), "Residual": float(sub["WaterBalance_Residual_mm"].sum())
        }
        for sname, months in [("JF+D_2018", [1, 2, 12]), ("MAM", [3, 4, 5]), ("JJA", [6, 7, 8]), ("SON", [9, 10, 11])]:
            sub_s = sub[sub["month"].isin(months)]
            cb_ctrl_dict[(st, exp, sname)] = {
                "P": float(sub_s["P_mm"].sum()), "ET": float(sub_s["ET_mm"].sum()),
                "Qs": float(sub_s["Qs_mm"].sum()), "Qsb": float(sub_s["Qsb_mm"].sum()),
                "TotalRunoff": float(sub_s["TotalRunoff_mm"].sum()),
                "Delta_S": float(sub_s["Delta_S_mm"].sum()), "Residual": float(sub_s["WaterBalance_Residual_mm"].sum())
            }

# 4. Chargement des sorties journalières et calcul des bilans
print("\n>>> [3/6] Chargement des flux journaliers et calcul des bilans...")

RUN_CONFIGS = OrderedDict([
    ("OL_DAIC", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OL_DAIC_2018/SURFACEMODEL"),
        "has_p": False, "has_gws": False
    }),
    ("ENS_OPL", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL"),
        "has_p": True, "has_gws": True
    }),
    ("ENS_corr", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_corr_2018/SURFACEMODEL"),
        "has_p": True, "has_gws": True
    }),
    ("DA_nocdf", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL"),
        "has_p": True, "has_gws": True
    }),
    ("DA_nocdf_nowilt", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_nowilt_2018/SURFACEMODEL"),
        "has_p": True, "has_gws": True
    }),
    ("DA_corr", {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_corr_2018/SURFACEMODEL"),
        "has_p": True, "has_gws": True
    }),
])

# Forçage OPL pour P de OL_DAIC
opl_dir = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")

# Lecture des 365 fichiers journaliers pour chaque run
def get_daily_files_365(exp_dir, is_hierarchical=False):
    if is_hierarchical:
        files = sorted(glob.glob(os.path.join(exp_dir, "output/2018-*/**/LIS_HIST_*.d01.nc"), recursive=True))
    else:
        files = sorted(glob.glob(os.path.join(exp_dir, "output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), recursive=True))
    day_files = []
    for f in files:
        fn = os.path.basename(f)
        if not fn.startswith("LIS_HIST_") or fn.endswith(".tmp"): continue
        ymd = fn[9:17]
        if "20180102" <= ymd <= "20190101":
            day_files.append((ymd, f))
    day_files = sorted(day_files, key=lambda x: x[0])
    return day_files

daily_fluxes = {}
dates_list = []

# Précipitation non perturbée OPL
opl_day_files = get_daily_files_365(opl_dir, is_hierarchical=True)
opl_p_arr = np.zeros((365, 121, 181), dtype=np.float32)
for idx, (ymd, f) in enumerate(opl_day_files):
    with nc.Dataset(f) as ds:
        opl_p_arr[idx] = np.where(ds["TotalPrecip_tavg"][:] > -900, ds["TotalPrecip_tavg"][:].squeeze(), 0.0) * 86400.0

for exp, cfg in RUN_CONFIGS.items():
    is_h = (exp == "DA_nocdf")
    day_files = get_daily_files_365(cfg["dir"], is_hierarchical=is_h)
    if not dates_list:
        for ymd, _ in day_files:
            dt = pd.to_datetime(ymd) - pd.Timedelta(days=1)
            dates_list.append(dt.strftime("%Y-%m-%d"))
            
    p_arr = np.zeros((365, 121, 181), dtype=np.float32)
    et_arr = np.zeros((365, 121, 181), dtype=np.float32)
    qs_nat = np.zeros((365, 121, 181), dtype=np.float32)
    qsb_nat = np.zeros((365, 121, 181), dtype=np.float32)
    sm_arr = np.zeros((365, 4, 121, 181), dtype=np.float32)
    
    for idx, (ymd, f) in enumerate(day_files):
        with nc.Dataset(f) as ds:
            if cfg["has_p"]:
                p_arr[idx] = np.where(ds["TotalPrecip_tavg"][:] > -900, ds["TotalPrecip_tavg"][:].squeeze(), 0.0) * 86400.0
            else:
                p_arr[idx] = opl_p_arr[idx]
            et_arr[idx] = np.where(ds["Evap_tavg"][:] > -900, ds["Evap_tavg"][:].squeeze(), 0.0) * 86400.0
            qs_nat[idx] = np.where(ds["Qs_tavg"][:] > -900, ds["Qs_tavg"][:].squeeze(), 0.0) * 86400.0
            qsb_nat[idx] = np.where(ds["Qsb_tavg"][:] > -900, ds["Qsb_tavg"][:].squeeze(), 0.0) * 86400.0
            sm_arr[idx] = ds["SoilMoist_tavg"][:].squeeze()
            
    # Remapped 180x120 files for catchments Qs and Qsb
    remap_day_files = sorted(glob.glob(os.path.join(cfg["remap_dir"], "**/*.d01.nc"), recursive=True))
    remap_365 = []
    for f in remap_day_files:
        fn = os.path.basename(f)
        if not fn.startswith("LIS_HIST_") or fn.endswith(".tmp"): continue
        ymd = fn[9:17]
        if "20180102" <= ymd <= "20190101":
            remap_365.append((ymd, f))
    remap_365 = sorted(remap_365, key=lambda x: x[0])
    
    qs_remap = np.zeros((365, 120, 180), dtype=np.float32)
    qsb_remap = np.zeros((365, 120, 180), dtype=np.float32)
    for idx, (ymd, f) in enumerate(remap_365):
        with nc.Dataset(f) as ds:
            qs_remap[idx] = np.where(ds["Qs_tavg"][:] > -900, ds["Qs_tavg"][:].squeeze(), 0.0) * 86400.0
            qsb_remap[idx] = np.where(ds["Qsb_tavg"][:] > -900, ds["Qsb_tavg"][:].squeeze(), 0.0) * 86400.0
            
    daily_fluxes[exp] = {
        "P": p_arr, "ET": et_arr, "Qs_nat": qs_nat, "Qsb_nat": qsb_nat, "SM": sm_arr,
        "Qs_remap": qs_remap, "Qsb_remap": qsb_remap, "has_p": cfg["has_p"]
    }
    print(f"  Exp {exp} chargée : P={np.mean(np.sum(p_arr, axis=0)[landmask_181]):.2f} mm")

# 5. Construction de la table A2_flow_partition_runs.csv
print("\n>>> [4/6] Construction de A2_flow_partition_runs.csv...")

TIME_PERIODS = OrderedDict()
TIME_PERIODS["Annuel"] = ("annual", list(range(365)))
for sname, months in [("JF+D_2018", [1, 2, 12]), ("MAM", [3, 4, 5]), ("JJA", [6, 7, 8]), ("SON", [9, 10, 11])]:
    smask = [pd.to_datetime(d).month in months for d in dates_list]
    TIME_PERIODS[sname] = ("seasonal", [i for i, b in enumerate(smask) if b])

for m in range(1, 13):
    mmask = [pd.to_datetime(d).month == m for d in dates_list]
    TIME_PERIODS[f"2018-{m:02d}"] = ("monthly", [i for i, b in enumerate(mmask) if b])

flow_records = []

for exp in EXP_RUNS:
    exp_d = daily_fluxes[exp]
    rst_d = annual_restart_deltas[exp]
    
    for pname, (ptype, pindices) in TIME_PERIODS.items():
        is_annual = (pname == "Annuel")
        first_d = pindices[0]
        last_d = pindices[-1]
        
        # Sommes de flux
        p_sum_181 = np.sum(exp_d["P"][pindices], axis=0)
        et_sum_181 = np.sum(exp_d["ET"][pindices], axis=0)
        qs_sum_nat = np.sum(exp_d["Qs_nat"][pindices], axis=0)
        qsb_sum_nat = np.sum(exp_d["Qsb_nat"][pindices], axis=0)
        qs_sum_rem = np.sum(exp_d["Qs_remap"][pindices], axis=0)
        qsb_sum_rem = np.sum(exp_d["Qsb_remap"][pindices], axis=0)
        
        # Variations journalières de stock (pour mensuel/saisonnier)
        sm_start = exp_d["SM"][first_d - 1] if first_d > 0 else exp_d["SM"][0] # approximation journalière
        sm_end = exp_d["SM"][last_d]
        d_sm_daily_l = [(sm_end[l] - sm_start[l]) * dz[l] * 1000.0 for l in range(4)]
        d_sm_daily_tot = sum(d_sm_daily_l)
        
        # Boucle sur les 4 régions
        regions_list = ["Domaine complet", "Lalla Chafia", "Sidi Jabeur", "Sebou amont"]
        
        for rname in regions_list:
            if rname == "Domaine complet":
                n_cells = 16030
                p_val = float(np.mean(p_sum_181[landmask_181]))
                et_val = float(np.mean(et_sum_181[landmask_181]))
                qs_val = float(np.mean(qs_sum_nat[landmask_181]))
                qsb_val = float(np.mean(qsb_sum_nat[landmask_181]))
                qtot_val = qs_val + qsb_val
                
                if is_annual:
                    dsl1 = rst_d["dom_d_smc_l"][0]
                    dsl2 = rst_d["dom_d_smc_l"][1]
                    dsl3 = rst_d["dom_d_smc_l"][2]
                    dsl4 = rst_d["dom_d_smc_l"][3]
                    ds_sol = rst_d["dom_d_smc_tot"]
                    dgws = rst_d["dom_d_wa"]
                    ds_tot = rst_d["dom_d_tot"]
                    ds_daily = "N/A"
                    res_val = round(p_val - et_val - qtot_val - ds_tot, 4)
                    
                    # Contrôle domaine
                    ctrl_res = dom_ctrl_dict[exp]["Residual"]
                    diff_res = round(res_val - ctrl_res, 4)
                else:
                    dsl1 = float(np.mean(d_sm_daily_l[0][landmask_181]))
                    dsl2 = float(np.mean(d_sm_daily_l[1][landmask_181]))
                    dsl3 = float(np.mean(d_sm_daily_l[2][landmask_181]))
                    dsl4 = float(np.mean(d_sm_daily_l[3][landmask_181]))
                    ds_sol = "N/A"
                    dgws = "N/A"
                    ds_tot = "N/A"
                    ds_daily = round(float(np.mean(d_sm_daily_tot[landmask_181])), 2)
                    res_val = "N/A"
                    ctrl_res = "N/A"
                    diff_res = "N/A"
                    
                c_q_str = "absent"
                c_et_str = "absent"
                diff_q = "absent"
                diff_et = "absent"
                
            else: # Bassins : Lalla Chafia, Sidi Jabeur, Sebou amont
                w180 = weights_180[rname]
                w181 = weights_181[rname]
                n_cells = len(catchments[rname])
                
                p_val = float(np.sum(p_sum_181 * w181))
                et_val = float(np.sum(et_sum_181 * w181))
                qs_val = float(np.sum(qs_sum_rem * w180))
                qsb_val = float(np.sum(qsb_sum_rem * w180))
                qtot_val = qs_val + qsb_val
                
                if is_annual:
                    dsl1 = float(np.nansum(rst_d["grid_d_smc_l"][0] * w181))
                    dsl2 = float(np.nansum(rst_d["grid_d_smc_l"][1] * w181))
                    dsl3 = float(np.nansum(rst_d["grid_d_smc_l"][2] * w181))
                    dsl4 = float(np.nansum(rst_d["grid_d_smc_l"][3] * w181))
                    ds_sol = float(np.nansum(rst_d["grid_d_smc_tot"] * w181))
                    dgws = float(np.nansum(rst_d["grid_d_wa"] * w181))
                    ds_tot = float(np.nansum(rst_d["grid_d_tot"] * w181))
                    ds_daily = "N/A"
                    res_val = round(p_val - et_val - qtot_val - ds_tot, 4)
                else:
                    dsl1 = float(np.sum(d_sm_daily_l[0] * w181))
                    dsl2 = float(np.sum(d_sm_daily_l[1] * w181))
                    dsl3 = float(np.sum(d_sm_daily_l[2] * w181))
                    dsl4 = float(np.sum(d_sm_daily_l[3] * w181))
                    ds_sol = "N/A"
                    dgws = "N/A"
                    ds_tot = "N/A"
                    ds_daily = round(float(np.sum(d_sm_daily_tot * w181)), 2)
                    res_val = "N/A"
                    
                ctrl_res = "N/A"
                diff_res = "N/A"
                
                # Contrôle bassins
                ctrl_key = (rname, exp, pname)
                if ctrl_key in cb_ctrl_dict:
                    c_q = cb_ctrl_dict[ctrl_key]["TotalRunoff"]
                    c_et = cb_ctrl_dict[ctrl_key]["ET"]
                    c_q_str = round(c_q, 4)
                    c_et_str = round(c_et, 4)
                    diff_q = round(qtot_val - c_q, 4)
                    diff_et = round(et_val - c_et, 4)
                else:
                    c_q_str = "absent"
                    c_et_str = "absent"
                    diff_q = "absent"
                    diff_et = "absent"
                    
            coeff_qs = round(qs_val / p_val, 4) if p_val > 1e-6 else np.nan
            coeff_qsb = round(qsb_val / p_val, 4) if p_val > 1e-6 else np.nan
            coeff_qtot = round(qtot_val / p_val, 4) if p_val > 1e-6 else np.nan
            
            p_display = round(p_val, 2) if (exp_d["has_p"] or is_annual) else "absent (non sorti)"
            
            flow_records.append({
                "period": "2018",
                "experiment": exp,
                "region": rname,
                "time_scale": ptype,
                "season_or_month": pname,
                "n_cells": n_cells,
                "P_mm": p_display,
                "Qs_mm": round(qs_val, 2),
                "Qsb_mm": round(qsb_val, 2),
                "TotalRunoff_mm": round(qtot_val, 2),
                "ET_mm": round(et_val, 2),
                "coeff_Qs_over_P": coeff_qs,
                "coeff_Qsb_over_P": coeff_qsb,
                "coeff_TotalRunoff_over_P": coeff_qtot,
                "Delta_S_L1_mm": round(dsl1, 2) if dsl1 != "N/A" else "N/A",
                "Delta_S_L2_mm": round(dsl2, 2) if dsl2 != "N/A" else "N/A",
                "Delta_S_L3_mm": round(dsl3, 2) if dsl3 != "N/A" else "N/A",
                "Delta_S_L4_mm": round(dsl4, 2) if dsl4 != "N/A" else "N/A",
                "Delta_S_sol_mm": round(ds_sol, 2) if ds_sol != "N/A" else "N/A",
                "Delta_GWS_mm": round(dgws, 2) if dgws != "N/A" else "N/A",
                "Delta_S_total_mm": round(ds_tot, 2) if ds_tot != "N/A" else "N/A",
                "DeltaS_from_daily_means": ds_daily,
                "Recharge_mm": "absent",
                "WaterBalance_Residual_mm": res_val,
                "ctrl_validated_domain_residual_mm": ctrl_res,
                "diff_validated_domain_residual_mm": diff_res,
                "ctrl_TotalRunoff_upstream_cb_mm": c_q_str,
                "ctrl_ET_upstream_cb_mm": c_et_str,
                "diff_TotalRunoff_vs_upstream_cb_mm": diff_q,
                "diff_ET_vs_upstream_cb_mm": diff_et,
            })

df_flow = pd.DataFrame(flow_records)
out_csv_flow = os.path.join(TABLES_DIR, "A2_flow_partition_runs.csv")
df_flow.to_csv(out_csv_flow, index=False)
print(f"  [OK] Table {out_csv_flow} régénérée ({len(df_flow)} lignes)")

# 6. Contrastes C1, C2, C3, C4
print("\n>>> [5/6] Construction de A2_flow_partition_contrasts.csv...")

CONTRASTS = [
    ("C1", "ENS_OPL − OL_DAIC", "ENS_OPL", "OL_DAIC"),
    ("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"),
    ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr"),
    ("C4", "DA_nocdf_nowilt − DA_nocdf", "DA_nocdf_nowilt", "DA_nocdf"),
]

contrasts_flow_records = []
for cid, cname, run_a, run_b in CONTRASTS:
    for pname, (ptype, _) in TIME_PERIODS.items():
        is_ann = (pname == "Annuel")
        for rname in ["Domaine complet", "Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
            row_a = df_flow[(df_flow["experiment"] == run_a) & (df_flow["season_or_month"] == pname) & (df_flow["region"] == rname)].iloc[0]
            row_b = df_flow[(df_flow["experiment"] == run_b) & (df_flow["season_or_month"] == pname) & (df_flow["region"] == rname)].iloc[0]
            
            d_qs = round(float(row_a["Qs_mm"]) - float(row_b["Qs_mm"]), 2)
            d_qsb = round(float(row_a["Qsb_mm"]) - float(row_b["Qsb_mm"]), 2)
            d_qtot = round(float(row_a["TotalRunoff_mm"]) - float(row_b["TotalRunoff_mm"]), 2)
            d_et = round(float(row_a["ET_mm"]) - float(row_b["ET_mm"]), 2)
            
            if is_ann:
                d_ds_sol = round(float(row_a["Delta_S_sol_mm"]) - float(row_b["Delta_S_sol_mm"]), 2)
                d_dgws = round(float(row_a["Delta_GWS_mm"]) - float(row_b["Delta_GWS_mm"]), 2)
                d_dstot = round(float(row_a["Delta_S_total_mm"]) - float(row_b["Delta_S_total_mm"]), 2)
                d_ds_daily = "N/A"
            else:
                d_ds_sol = "N/A"
                d_dgws = "N/A"
                d_dstot = "N/A"
                d_ds_daily = round(float(row_a["DeltaS_from_daily_means"]) - float(row_b["DeltaS_from_daily_means"]), 2)
                
            if str(row_a["P_mm"]).startswith("absent") or str(row_b["P_mm"]).startswith("absent"):
                d_p = "absent"
                d_c_qs = "absent"
                d_c_qsb = "absent"
                d_c_qtot = "absent"
            else:
                d_p = round(float(row_a["P_mm"]) - float(row_b["P_mm"]), 2)
                d_c_qs = round(float(row_a["coeff_Qs_over_P"]) - float(row_b["coeff_Qs_over_P"]), 4) if pd.notnull(row_a["coeff_Qs_over_P"]) and pd.notnull(row_b["coeff_Qs_over_P"]) else np.nan
                d_c_qsb = round(float(row_a["coeff_Qsb_over_P"]) - float(row_b["coeff_Qsb_over_P"]), 4) if pd.notnull(row_a["coeff_Qsb_over_P"]) and pd.notnull(row_b["coeff_Qsb_over_P"]) else np.nan
                d_c_qtot = round(float(row_a["coeff_TotalRunoff_over_P"]) - float(row_b["coeff_TotalRunoff_over_P"]), 4) if pd.notnull(row_a["coeff_TotalRunoff_over_P"]) and pd.notnull(row_b["coeff_TotalRunoff_over_P"]) else np.nan
                
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
                "delta_Delta_S_sol_mm": d_ds_sol,
                "delta_Delta_GWS_mm": d_dgws,
                "delta_Delta_S_total_mm": d_dstot,
                "delta_DeltaS_from_daily_means": d_ds_daily,
                "delta_coeff_Qs_over_P": d_c_qs,
                "delta_coeff_Qsb_over_P": d_c_qsb,
                "delta_coeff_TotalRunoff_over_P": d_c_qtot,
            })

df_contrasts_flow = pd.DataFrame(contrasts_flow_records)
out_csv_c_flow = os.path.join(TABLES_DIR, "A2_flow_partition_contrasts.csv")
df_contrasts_flow.to_csv(out_csv_c_flow, index=False)
print(f"  [OK] Table {out_csv_c_flow} régénérée ({len(df_contrasts_flow)} lignes)")

# 7. Génération de A2_peak_timing.csv
print("\n>>> [6/6] Construction de A2_peak_timing.csv...")

df_sf = pd.read_csv(os.path.join(TABLES_DIR, "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv"))
p_ens_corr = daily_fluxes["ENS_corr"]["P"] # shape (365, 121, 181)

peak_records = []

for st_col, st_name in [("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]:
    w181 = weights_181[st_name]
    basin_p_series = np.sum(p_ens_corr * w181, axis=(1, 2)) # shape (365,)
    
    # 1. Observé
    obs_series = df_sf[f"obs_{st_col}"].values
    valid_mask = ~np.isnan(obs_series)
    obs_clean = np.where(valid_mask, obs_series, 0.0)
    
    # Pics distincts (distance minimale = 5 jours)
    p_indices, _ = find_peaks(obs_clean, distance=5)
    top_indices = p_indices[np.argsort(obs_clean[p_indices])[-3:][::-1]]
    
    for rank, idx in enumerate(top_indices, 1):
        dt_str = df_sf.loc[idx, "date"]
        pk_val = float(obs_clean[idx])
        
        # 10 jours précédant le pic (J-10 à J-1)
        precip_prec = [round(float(basin_p_series[idx - k]), 2) if (idx - k) >= 0 else 0.0 for k in range(10, 0, -1)]
        cum_10d = round(sum(precip_prec), 2)
        j0_prec = round(float(basin_p_series[idx]), 2)
        cum_11d = round(cum_10d + j0_prec, 2)
        
        peak_records.append({
            "station": st_name,
            "series_type": "observed",
            "experiment": "OBS",
            "peak_rank": rank,
            "peak_date": dt_str,
            "peak_flow_m3s": round(pk_val, 2),
            "precip_basin_j_minus_10_mm": precip_prec[0],
            "precip_basin_j_minus_9_mm": precip_prec[1],
            "precip_basin_j_minus_8_mm": precip_prec[2],
            "precip_basin_j_minus_7_mm": precip_prec[3],
            "precip_basin_j_minus_6_mm": precip_prec[4],
            "precip_basin_j_minus_5_mm": precip_prec[5],
            "precip_basin_j_minus_4_mm": precip_prec[6],
            "precip_basin_j_minus_3_mm": precip_prec[7],
            "precip_basin_j_minus_2_mm": precip_prec[8],
            "precip_basin_j_minus_1_mm": precip_prec[9],
            "precip_basin_j0_mm": j0_prec,
            "precip_basin_cum_10d_prior_mm": cum_10d,
            "precip_basin_cum_11d_inc_j0_mm": cum_11d
        })
        
    # 2. Simulations
    sf_runs_all = ["OL_DAIC", "ENS_OPL", "ENS_corr", "DA_nocdf", "DA_nocdf_nowilt", "DA_corr", "OPL", "DA_cdf"]
    for exp in sf_runs_all:
        col = f"{exp}_{st_col}"
        if col not in df_sf.columns:
            continue
        sim_series = df_sf[col].values
        p_indices, _ = find_peaks(sim_series, distance=5)
        top_indices = p_indices[np.argsort(sim_series[p_indices])[-3:][::-1]]
        
        for rank, idx in enumerate(top_indices, 1):
            dt_str = df_sf.loc[idx, "date"]
            pk_val = float(sim_series[idx])
            
            precip_prec = [round(float(basin_p_series[idx - k]), 2) if (idx - k) >= 0 else 0.0 for k in range(10, 0, -1)]
            cum_10d = round(sum(precip_prec), 2)
            j0_prec = round(float(basin_p_series[idx]), 2)
            cum_11d = round(cum_10d + j0_prec, 2)
            
            peak_records.append({
                "station": st_name,
                "series_type": "simulated",
                "experiment": exp,
                "peak_rank": rank,
                "peak_date": dt_str,
                "peak_flow_m3s": round(pk_val, 2),
                "precip_basin_j_minus_10_mm": precip_prec[0],
                "precip_basin_j_minus_9_mm": precip_prec[1],
                "precip_basin_j_minus_8_mm": precip_prec[2],
                "precip_basin_j_minus_7_mm": precip_prec[3],
                "precip_basin_j_minus_6_mm": precip_prec[4],
                "precip_basin_j_minus_5_mm": precip_prec[5],
                "precip_basin_j_minus_4_mm": precip_prec[6],
                "precip_basin_j_minus_3_mm": precip_prec[7],
                "precip_basin_j_minus_2_mm": precip_prec[8],
                "precip_basin_j_minus_1_mm": precip_prec[9],
                "precip_basin_j0_mm": j0_prec,
                "precip_basin_cum_10d_prior_mm": cum_10d,
                "precip_basin_cum_11d_inc_j0_mm": cum_11d
            })

df_peaks = pd.DataFrame(peak_records)
out_csv_peaks = os.path.join(TABLES_DIR, "A2_peak_timing.csv")
df_peaks.to_csv(out_csv_peaks, index=False)
print(f"  [OK] Table {out_csv_peaks} enregistrée ({len(df_peaks)} lignes)")

# 8. Régénération de la figure des barres
print("\n>>> Régénération de A2_flow_partition_bars.png...")
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
        vals = [float(sub_b[sub_b["contrast_id"] == cid][comp].values[0]) for cid in ["C1", "C2", "C3", "C4"]]
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

# 9. Régénération de REPORT_A2.md
print("\n>>> Régénération de REPORT_A2.md...")
def df_to_markdown_simple(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

rep_lines = [
    "# Rapport d'Étape A2 — Du sol au débit (H6/H7)",
    "",
    "Ce rapport présente strictement les tableaux générés par script depuis les sorties brutes et les tables de l'étape A2 (mis à jour en étape A2b).",
    "Conformément aux consignes, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.",
    "",
    "## 1. Partition Annuelle des Écoulements et Bilan Hydrique (2018)",
    "",
    "### 1.1 Totaux Annuels par Expérience et par Région",
    ""
]

sub_t1 = df_flow[df_flow["season_or_month"] == "Annuel"]
cols_t1 = ["experiment", "region", "n_cells", "P_mm", "Qs_mm", "Qsb_mm", "TotalRunoff_mm", "ET_mm", "coeff_TotalRunoff_over_P", "Delta_S_sol_mm", "Delta_GWS_mm", "Delta_S_total_mm", "WaterBalance_Residual_mm", "ctrl_validated_domain_residual_mm", "diff_validated_domain_residual_mm", "ctrl_TotalRunoff_upstream_cb_mm", "diff_TotalRunoff_vs_upstream_cb_mm", "ctrl_ET_upstream_cb_mm", "diff_ET_vs_upstream_cb_mm"]
rep_lines.append(df_to_markdown_simple(sub_t1[cols_t1]))

rep_lines.extend([
    "",
    "### 1.2 Contrastes Annuels C1, C2, C3, C4 de Partition des Écoulements",
    ""
])
sub_t2 = df_contrasts_flow[df_contrasts_flow["season_or_month"] == "Annuel"]
cols_t2 = ["contrast_id", "contrast_name", "region", "delta_P_mm", "delta_Qs_mm", "delta_Qsb_mm", "delta_TotalRunoff_mm", "delta_ET_mm", "delta_Delta_S_sol_mm", "delta_Delta_GWS_mm", "delta_Delta_S_total_mm", "delta_coeff_TotalRunoff_over_P"]
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
df_events = pd.read_csv(os.path.join(TABLES_DIR, "A2_rainfall_events_runoff.csv"))
cols_t3 = ["basin", "event_id", "start_date", "end_date", "duration_days", "P_event_mm", "experiment", "stock_total_eve_mm", "Qs_cum_j0_j5_mm", "Qsb_cum_j0_j5_mm", "TotalRunoff_cum_j0_j5_mm", "runoff_coeff_Total"]
rep_lines.append(df_to_markdown_simple(df_events[cols_t3]))

rep_lines.extend([
    "",
    "### 2.2 Régression Linéaire : Δ(Qs+Qsb) vs ΔStock veille (C2 et C3)",
    ""
])
df_reg = pd.read_csv(os.path.join(TABLES_DIR, "A2_rainfall_events_contrasts_regression.csv"))
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
df_sf_metrics = pd.read_csv(os.path.join(TABLES_DIR, "A2_streamflow_metrics_stations.csv"))
cols_t5 = ["station", "experiment", "status", "n_days", "kge_2012", "r", "beta", "gamma", "nse", "volume_bias_m3s", "rel_volume_bias_pct", "peak_sim_m3s", "peak_sim_date", "peak_bias_m3s", "peak_timing_days", "nic_contrast_id", "nic_reference_run", "nic_kge_2012", "nic_bootstrap_mean", "nic_bootstrap_ci_low", "nic_bootstrap_ci_high"]
rep_lines.append(df_to_markdown_simple(df_sf_metrics[cols_t5]))

rep_lines.extend([
    "",
    "### 3.2 Comparaison Annuelle et Mensuelle : Δ Débit Exutoire vs Δ(Qs+Qsb) Bassin (C2 et C3)",
    ""
])
df_sf_comp = pd.read_csv(os.path.join(TABLES_DIR, "A2_streamflow_vs_runoff_contrasts.csv"))
cols_t6 = ["station", "contrast_id", "time_scale", "season_or_month", "delta_streamflow_volume_m3", "delta_streamflow_depth_mm", "delta_TotalRunoff_volume_m3", "delta_TotalRunoff_depth_mm", "ratio_streamflow_over_runoff"]
rep_lines.append(df_to_markdown_simple(df_sf_comp[cols_t6]))

rep_lines.extend([
    "",
    "### 3.3 Timing et Ampleur des 3 Plus Grands Pics de Débit (Observés et Simulés)",
    ""
])
cols_t7 = ["station", "series_type", "experiment", "peak_rank", "peak_date", "peak_flow_m3s", "precip_basin_j_minus_3_mm", "precip_basin_j_minus_2_mm", "precip_basin_j_minus_1_mm", "precip_basin_j0_mm", "precip_basin_cum_10d_prior_mm", "precip_basin_cum_11d_inc_j0_mm"]
rep_lines.append(df_to_markdown_simple(df_peaks[cols_t7]))

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
    "- `paper1/tables/A2_peak_timing.csv`",
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
print("=" * 80)
