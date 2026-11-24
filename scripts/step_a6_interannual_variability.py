#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ÉTAPE A6 — Variabilité interannuelle 2016–2020 (H9)
===================================================
Script de production scientifique pour l'évaluation de la variabilité
interannuelle 2016–2020 des simulations Noah-MP / LIS au Maroc.

Règles respectées :
- Runs autorisés : OPL_noirr_2016_2020, DA_nocdf_noirr_2016_2020, DA_cdf_noirr_2016_2020
- Bassins : Lalla Chafia (75,71), Sidi Jabeur (71,71), Sebou amont (75,108)
- Stocks : restarts au 1er janvier de chaque année, moyenne d'ensemble
- Contrastes : P1 = DA_nocdf − OPL, P2 = DA_cdf − OPL
- Tout chiffre dans le rapport provient directement des CSV générés
"""

import os
import glob
import time
import struct
from collections import OrderedDict
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import netCDF4 as nc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import tifffile

# ==============================================================================
# Chemins et constantes
# ==============================================================================
BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
ROOT_FIGURES_DIR = os.path.join(BASE_DIR, "figures")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A6.md")
ROOT_REPORT_PATH = os.path.join(BASE_DIR, "REPORT_A6.md")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(ROOT_FIGURES_DIR, exist_ok=True)

YEARS = [2016, 2017, 2018, 2019, 2020]
RUN_NAMES = ["OPL", "DA_nocdf", "DA_cdf"]

RUN_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
}

ROUTING_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/output/OPL_linres0_2016_2020/ROUTING"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/output/DA_nocdf_linres0_2016_2020/ROUTING"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/output/DA_cdf_linres0_2016_2020/ROUTING"),
}

DZ = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)
LAYER_THICKNESS_MM = [100.0, 300.0, 600.0, 1000.0]

print("=" * 80)
print("ÉTAPE A6 — Variabilité interannuelle 2016–2020 (H9)")
print("=" * 80)

# ==============================================================================
# 0. INITIALISATION : Grille, Masques et Poids des Bassins
# ==============================================================================
print("\n>>> [0/7] Initialisation des grilles, masques et poids de bassins...")

lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = (ds_in.variables["LANDMASK"][:] == 1.0)
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

# Mapping tuiles LIS vers 121x181
f_sample = os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc")
with nc.Dataset(f_sample) as ds:
    lat_tile = ds["lat"][:]
    lon_tile = ds["lon"][:]
    tile_c = np.round((lon_tile - (-10.0)) / 0.05).astype(int)
    tile_r = np.round((lat_tile - 30.0) / 0.05).astype(int)

# HyMAP D8 et bassins
ldt_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
with nc.Dataset(ldt_path) as ds_ldt:
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
    area_180 = ds_ldt["HYMAP_grid_area"][:].filled(0.0)

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
masks_181 = {}

for cname, ccells in catchments.items():
    tot_area = sum(area_180[r, c] for r, c in ccells)
    w180 = np.zeros((120, 180), dtype=float)
    for r, c in ccells:
        w180[r, c] = area_180[r, c] / tot_area
    weights_180[cname] = w180
    
    w181 = np.zeros((121, 181), dtype=float)
    m181 = np.zeros((121, 181), dtype=bool)
    for r, c in ccells:
        a = area_180[r, c]
        w181[r, c] += 0.25 * a
        w181[r, c+1] += 0.25 * a
        w181[r+1, c] += 0.25 * a
        w181[r+1, c+1] += 0.25 * a
        m181[r, c] = True
        m181[r, c+1] = True
        m181[r+1, c] = True
        m181[r+1, c+1] = True
    weights_181[cname] = w181 / np.sum(w181)
    masks_181[cname] = m181

REGIONS = ["Domaine complet", "Lalla Chafia", "Sidi Jabeur", "Sebou amont"]

def get_region_mean(field_2d, region_name):
    if region_name == "Domaine complet":
        return float(np.nanmean(field_2d[landmask_181]))
    else:
        w = weights_181[region_name]
        return float(np.nansum(np.where(w > 0, field_2d * w, 0.0)))


# ==============================================================================
# TÂCHE 1 — Inventaire
# ==============================================================================
print("\n>>> [1/7] TÂCHE 1: Inventaire des simulations, forçages et observations...")

obs_daily_df = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_daily.csv"))
obs_daily_df["date"] = pd.to_datetime(obs_daily_df["date"])

inv_records = []

gleam_path = "data/validation/evapotranspiration/GLEAM/raw"
gleam_version = "v4.3a"
gleam_vars = "E, Ep (Eb, Et, Ei: absent)"
gleam_years = "2015-2020"

wapor_path = "data/validation/evapotranspiration/WaPOR"
wapor_version = "v3 (annuel: WaPOR_v3_E, WaPOR_v3_T, WaPOR_v3_AETI)"
wapor_vars = "E, T, AETI (I: absent)"
wapor_years = "2018, 2019, 2020"

for r in RUN_NAMES:
    out_dir = os.path.join(RUN_DIRS[r], "output")
    rt_dir = ROUTING_DIRS[r]
    
    for yr in YEARS:
        # Fichiers de sortie journaliers
        daily_files = []
        for m in range(1, 13):
            dpath = os.path.join(out_dir, f"{yr}-{m:02d}/SURFACEMODEL")
            if os.path.exists(dpath):
                for sub in os.listdir(dpath):
                    daily_files.extend(glob.glob(os.path.join(dpath, sub, "LIS_HIST_*.d01.nc")))
        n_daily = len(set(daily_files))
        
        # Restarts disponibles
        rst_dates = []
        if yr == 2016:
            rst_dates.append("2016-01-01 00:00 (SPINUP)")
        else:
            rst_dates.append(f"{yr}-01-01 00:00")
        for m in range(1, 13):
            rst_dates.append(f"{yr}-{m:02d} fin de mois")
        rst_str = f"{len(rst_dates)} restarts ({yr}-01-01 au {yr}-12-31)"
        
        # Sorties de routage
        rt_files = glob.glob(os.path.join(rt_dir, f"*/LIS_HIST_{yr}*.d01.nc"))
        if os.path.exists(os.path.join(rt_dir, f"{yr+1}01/LIS_HIST_{yr+1}01010000.d01.nc")):
            rt_files.append(os.path.join(rt_dir, f"{yr+1}01/LIS_HIST_{yr+1}01010000.d01.nc"))
        n_rt = len(set(rt_files))
        rt_status = f"{n_rt} fichiers journaliers ({rt_dir})"
        
        # Fichiers d'incréments EnKF
        if r == "OPL":
            incr_str = "absent (run déterministe OPL sans assimilation)"
        else:
            incr_files = []
            for m in range(1, 13):
                ipath = os.path.join(out_dir, f"{yr}-{m:02d}/EnKF/{yr}{m:02d}")
                if os.path.exists(ipath):
                    incr_files.extend(glob.glob(os.path.join(ipath, "LIS_DA_EnKF_*_incr*.nc")))
            n_incr = len(set(incr_files))
            incr_str = f"{n_incr} fichiers d'incréments"
        
        # Stations de débit validées
        sub_lc = obs_daily_df[(obs_daily_df["station_id"] == "b_l_chafia") & (obs_daily_df["date"].dt.year == yr)]
        v_lc = int(sub_lc["q_m3s"].dropna().count())
        sub_sj = obs_daily_df[(obs_daily_df["station_id"] == "b_s_jabeur") & (obs_daily_df["date"].dt.year == yr)]
        v_sj = int(sub_sj["q_m3s"].dropna().count())
        stations_str = f"Lalla Chafia: {v_lc} j, Sidi Jabeur: {v_sj} j, Sebou amont: absent (non j.)"
        
        inv_records.append({
            "run": r,
            "year": yr,
            "n_daily_output_files": n_daily,
            "restarts_available": rst_str,
            "routing_outputs_available": rt_status,
            "enkf_increment_files": incr_str,
            "gleam_path": gleam_path,
            "gleam_version": gleam_version,
            "gleam_variables": gleam_vars,
            "gleam_years": gleam_years,
            "wapor_path": wapor_path,
            "wapor_version": wapor_version,
            "wapor_variables": wapor_vars,
            "wapor_years": wapor_years,
            "validated_stations_valid_days": stations_str,
        })

df_inventory = pd.DataFrame(inv_records)
df_inventory.to_csv(os.path.join(TABLES_DIR, "A6_inventory.csv"), index=False)
df_inventory.to_csv(os.path.join(BASE_DIR, "A6_inventory.csv"), index=False)
print(f"  [OK] Table A6_inventory.csv enregistrée ({len(df_inventory)} lignes).")


# ==============================================================================
# Helper : Lecture des restarts pour les stocks au 1er janvier
# ==============================================================================
def read_restart_fields(fp):
    with nc.Dataset(fp) as ds:
        smc = ds.variables["SMC"][:]
        wa = ds.variables["WA"][:]
        can = ds.variables["CANWAT"][:]
        sn = ds.variables["SNEQV"][:]
        
        if smc.ndim == 3:
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
            
        smc_layers_mm = smc_m * DZ[:, None] * 1000.0
        smc_tot_mm = np.sum(smc_layers_mm, axis=0)
        
        grid_smc_tot = np.full((121, 181), np.nan, dtype=np.float32)
        grid_wa = np.full((121, 181), np.nan, dtype=np.float32)
        grid_can = np.full((121, 181), np.nan, dtype=np.float32)
        grid_sn = np.full((121, 181), np.nan, dtype=np.float32)
        grid_smc_layers = np.full((4, 121, 181), np.nan, dtype=np.float32)
        
        for l in range(4):
            grid_smc_layers[l, tile_r, tile_c] = smc_layers_mm[l]
        grid_smc_tot[tile_r, tile_c] = smc_tot_mm
        grid_wa[tile_r, tile_c] = wa_m
        grid_can[tile_r, tile_c] = can_m
        grid_sn[tile_r, tile_c] = sn_m
        
        return {
            "smc_layers": grid_smc_layers,
            "smc_tot": grid_smc_tot,
            "wa": grid_wa,
            "can": grid_can,
            "sn": grid_sn,
        }

def get_restart_path(run_id, dt_str):
    yr = int(dt_str[:4])
    r_dir = RUN_DIRS[run_id]
    if dt_str == "201601010000":
        if run_id == "OPL":
            return os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_OPL/restarts/LIS_RST_NOAHMP401_201601010000.d01.nc")
        else:
            return os.path.join(BASE_DIR, "experiments/NorthMor/SPINUP/SPINUP_DA/restarts/surf/LIS_RST_NOAHMP401_201601010000.d01.nc")
    else:
        prev_yr = yr - 1
        p = os.path.join(r_dir, f"output/{prev_yr}-12/SURFACEMODEL/{yr}01/LIS_RST_NOAHMP401_{dt_str}.d01.nc")
        if os.path.exists(p):
            return p
        p2 = os.path.join(r_dir, f"restarts/LIS_RST_NOAHMP401_{dt_str}.d01.nc")
        if os.path.exists(p2):
            return p2
        p3 = os.path.join(r_dir, f"restarts/surf/LIS_RST_NOAHMP401_{dt_str}.d01.nc")
        if os.path.exists(p3):
            return p3
        raise FileNotFoundError(f"Restart non trouvé pour {run_id} au {dt_str}")


# ==============================================================================
# TÂCHE 2 — Bilan annuel par run (années civiles 2016–2020 ; domaine + 3 bassins)
# ==============================================================================
print("\n>>> [2/7] TÂCHE 2: Bilan hydrique annuel et contrastes (2016–2020)...")

annual_fluxes = {r: {} for r in RUN_NAMES}
annual_restarts = {r: {} for r in RUN_NAMES}

for r in RUN_NAMES:
    for yr_rst in range(2016, 2022):
        dt_str = f"{yr_rst}01010000"
        fp = get_restart_path(r, dt_str)
        annual_restarts[r][yr_rst] = read_restart_fields(fp)

for r in RUN_NAMES:
    out_dir = os.path.join(RUN_DIRS[r], "output")
    for yr in YEARS:
        t0 = time.time()
        p_acc = np.zeros((121, 181), dtype=np.float32)
        et_acc = np.zeros((121, 181), dtype=np.float32)
        es_acc = np.zeros((121, 181), dtype=np.float32)
        tv_acc = np.zeros((121, 181), dtype=np.float32)
        ec_acc = np.zeros((121, 181), dtype=np.float32)
        qs_acc = np.zeros((121, 181), dtype=np.float32)
        qsb_acc = np.zeros((121, 181), dtype=np.float32)
        theta1_daily = []
        
        days_in_year = pd.date_range(f"{yr}-01-01", f"{yr}-12-31")
        file_map = {}
        for m in range(1, 13):
            dpath = os.path.join(out_dir, f"{yr}-{m:02d}/SURFACEMODEL")
            if os.path.exists(dpath):
                for sub in os.listdir(dpath):
                    for fp in glob.glob(os.path.join(dpath, sub, "LIS_HIST_*.d01.nc")):
                        fname = os.path.basename(fp)
                        ymd = fname[9:17]
                        dt_file = pd.to_datetime(ymd) - pd.Timedelta(days=1)
                        if dt_file.year == yr:
                            file_map[dt_file.strftime("%Y-%m-%d")] = fp
                            
        for dt_day in days_in_year:
            d_str = dt_day.strftime("%Y-%m-%d")
            if d_str in file_map:
                with nc.Dataset(file_map[d_str]) as ds:
                    p_acc += np.where(ds["Rainf_f_tavg"][:] > -900, ds["Rainf_f_tavg"][:].squeeze(), 0.0) * 86400.0
                    et_acc += np.where(ds["Evap_tavg"][:] > -900, ds["Evap_tavg"][:].squeeze(), 0.0) * 86400.0
                    es_acc += np.where(ds["ESoil_tavg"][:] > -900, ds["ESoil_tavg"][:].squeeze(), 0.0) * 86400.0
                    tv_acc += np.where(ds["TVeg_tavg"][:] > -900, ds["TVeg_tavg"][:].squeeze(), 0.0) * 86400.0
                    ec_acc += np.where(ds["ECanop_tavg"][:] > -900, ds["ECanop_tavg"][:].squeeze(), 0.0) * 86400.0
                    qs_acc += np.where(ds["Qs_tavg"][:] > -900, ds["Qs_tavg"][:].squeeze(), 0.0) * 86400.0
                    qsb_acc += np.where(ds["Qsb_tavg"][:] > -900, ds["Qsb_tavg"][:].squeeze(), 0.0) * 86400.0
                    if r == "OPL":
                        sm1 = ds["SoilMoist_tavg"][0].squeeze()
                        theta1_daily.append((d_str, sm1))
        
        annual_fluxes[r][yr] = {
            "P": p_acc,
            "ET": et_acc,
            "ESoil": es_acc,
            "TVeg": tv_acc,
            "ECanop": ec_acc,
            "Qs": qs_acc,
            "Qsb": qsb_acc,
            "theta1_daily": theta1_daily,
        }
        t1 = time.time()
        print(f"  [{r}] Année {yr} chargée ({len(file_map)} jours) en {t1 - t0:.2f} s. P domaine = {get_region_mean(p_acc, 'Domaine complet'):.1f} mm")

budget_records = []
budget_dict = {}

for r in RUN_NAMES:
    for yr in YEARS:
        fl = annual_fluxes[r][yr]
        rst_init = annual_restarts[r][yr]
        rst_final = annual_restarts[r][yr+1]
        
        d_soil = rst_final["smc_tot"] - rst_init["smc_tot"]
        d_wa = rst_final["wa"] - rst_init["wa"]
        d_can = rst_final["can"] - rst_init["can"]
        d_sn = rst_final["sn"] - rst_init["sn"]
        d_tot = d_soil + d_wa + d_can + d_sn
        
        for reg in REGIONS:
            val_p = get_region_mean(fl["P"], reg)
            val_et = get_region_mean(fl["ET"], reg)
            val_es = get_region_mean(fl["ESoil"], reg)
            val_tv = get_region_mean(fl["TVeg"], reg)
            val_ec = get_region_mean(fl["ECanop"], reg)
            val_qs = get_region_mean(fl["Qs"], reg)
            val_qsb = get_region_mean(fl["Qsb"], reg)
            val_d_soil = get_region_mean(d_soil, reg)
            val_d_wa = get_region_mean(d_wa, reg)
            val_d_can = get_region_mean(d_can, reg)
            val_d_sn = get_region_mean(d_sn, reg)
            val_d_tot = get_region_mean(d_tot, reg)
            
            residu = val_p - val_et - val_qs - val_qsb - val_d_tot
            if r in ["DA_nocdf", "DA_cdf"]:
                applied_incr = -residu
            else:
                applied_incr = "absent"
                
            entry = {
                "run": r,
                "year": yr,
                "region": reg,
                "P_mm": round(val_p, 2),
                "ET_mm": round(val_et, 2),
                "ESoil_mm": round(val_es, 2),
                "TVeg_mm": round(val_tv, 2),
                "ECanop_mm": round(val_ec, 2),
                "Qs_mm": round(val_qs, 2),
                "Qsb_mm": round(val_qsb, 2),
                "Delta_S_sol_mm": round(val_d_soil, 2),
                "Delta_WA_mm": round(val_d_wa, 2),
                "Delta_CANWAT_mm": round(val_d_can, 2),
                "Delta_SNEQV_mm": round(val_d_sn, 2),
                "Delta_S_total_mm": round(val_d_tot, 2),
                "residual_mm": round(residu, 2),
                "applied_increment_mm": round(applied_incr, 2) if isinstance(applied_incr, (int, float)) else applied_incr,
            }
            budget_records.append(entry)
            budget_dict[(r, yr, reg)] = entry

df_budget = pd.DataFrame(budget_records)
df_budget.to_csv(os.path.join(TABLES_DIR, "A6_annual_budget.csv"), index=False)
df_budget.to_csv(os.path.join(BASE_DIR, "A6_annual_budget.csv"), index=False)
print(f"  [OK] Table A6_annual_budget.csv enregistrée ({len(df_budget)} lignes).")

# Contrastes P1 et P2
contrasts_records = []
for yr in YEARS:
    for reg in REGIONS:
        opl = budget_dict[("OPL", yr, reg)]
        da_nocdf = budget_dict[("DA_nocdf", yr, reg)]
        da_cdf = budget_dict[("DA_cdf", yr, reg)]
        
        for cname, da_dict in [("P1 (DA_nocdf - OPL)", da_nocdf), ("P2 (DA_cdf - OPL)", da_cdf)]:
            row_c = {
                "contrast": cname,
                "year": yr,
                "region": reg,
                "delta_P_mm": round(da_dict["P_mm"] - opl["P_mm"], 2),
                "delta_ET_mm": round(da_dict["ET_mm"] - opl["ET_mm"], 2),
                "delta_ESoil_mm": round(da_dict["ESoil_mm"] - opl["ESoil_mm"], 2),
                "delta_TVeg_mm": round(da_dict["TVeg_mm"] - opl["TVeg_mm"], 2),
                "delta_ECanop_mm": round(da_dict["ECanop_mm"] - opl["ECanop_mm"], 2),
                "delta_Qs_mm": round(da_dict["Qs_mm"] - opl["Qs_mm"], 2),
                "delta_Qsb_mm": round(da_dict["Qsb_mm"] - opl["Qsb_mm"], 2),
                "delta_Delta_S_sol_mm": round(da_dict["Delta_S_sol_mm"] - opl["Delta_S_sol_mm"], 2),
                "delta_Delta_WA_mm": round(da_dict["Delta_WA_mm"] - opl["Delta_WA_mm"], 2),
                "delta_Delta_CANWAT_mm": round(da_dict["Delta_CANWAT_mm"] - opl["Delta_CANWAT_mm"], 2),
                "delta_Delta_SNEQV_mm": round(da_dict["Delta_SNEQV_mm"] - opl["Delta_SNEQV_mm"], 2),
                "delta_Delta_S_total_mm": round(da_dict["Delta_S_total_mm"] - opl["Delta_S_total_mm"], 2),
                "delta_residual_mm": round(da_dict["residual_mm"] - opl["residual_mm"], 2),
                "applied_increment_mm": da_dict["applied_increment_mm"],
            }
            contrasts_records.append(row_c)

df_contrasts = pd.DataFrame(contrasts_records)
df_contrasts.to_csv(os.path.join(TABLES_DIR, "A6_annual_contrasts.csv"), index=False)
df_contrasts.to_csv(os.path.join(BASE_DIR, "A6_annual_contrasts.csv"), index=False)
print(f"  [OK] Table A6_annual_contrasts.csv enregistrée ({len(df_contrasts)} lignes).")


# ==============================================================================
# TÂCHE 3 — Incréments écrits vs appliqués par année (DA_nocdf et DA_cdf)
# ==============================================================================
print("\n>>> [3/7] TÂCHE 3: Somme des incréments écrits vs appliqués par année...")

def read_enkf_increments_for_year(run_id, yr):
    out_dir = RUN_DIRS[run_id]
    incr_files = []
    for m in range(1, 13):
        ipath = os.path.join(out_dir, f"output/{yr}-{m:02d}/EnKF/{yr}{m:02d}")
        if os.path.exists(ipath):
            incr_files.extend(glob.glob(os.path.join(ipath, "LIS_DA_EnKF_*_incr*.nc")))
    incr_files = sorted(list(set(incr_files)))
    
    if not incr_files:
        return None
        
    ann_incr_pos = np.zeros((4, 121, 181), dtype=np.float32)
    ann_incr_neg = np.zeros((4, 121, 181), dtype=np.float32)
    
    for ifp in incr_files:
        with nc.Dataset(ifp) as ds:
            for l in range(4):
                vname = f"SoilMoist_incr_{l+1}"
                if vname in ds.variables:
                    arr = ds.variables[vname][:]
                    if arr.ndim == 2:
                        mean_arr = np.mean(arr, axis=1) if arr.shape[1] == 20 else arr.squeeze()
                    elif arr.ndim == 3:
                        mean_arr = np.mean(arr, axis=0) if arr.shape[0] == 20 else np.mean(arr, axis=-1)
                    else:
                        mean_arr = arr.squeeze()
                        
                    dz_mm = LAYER_THICKNESS_MM[l]
                    incr_mm = mean_arr * dz_mm
                    
                    grid_l = np.zeros((121, 181), dtype=np.float32)
                    grid_l[tile_r, tile_c] = incr_mm
                    
                    pos = np.where(grid_l > 0.0, grid_l, 0.0)
                    neg = np.where(grid_l < 0.0, grid_l, 0.0)
                    ann_incr_pos[l] += pos
                    ann_incr_neg[l] += neg
                    
    return ann_incr_pos, ann_incr_neg, len(incr_files)

incr_records = []

for r in ["DA_nocdf", "DA_cdf"]:
    for yr in YEARS:
        t0 = time.time()
        res = read_enkf_increments_for_year(r, yr)
        if res is None:
            for reg in REGIONS:
                incr_records.append({
                    "run": r,
                    "year": yr,
                    "region": reg,
                    "written_incr_L1_net_mm": "absent",
                    "written_incr_L2_net_mm": "absent",
                    "written_incr_L3_net_mm": "absent",
                    "written_incr_L4_net_mm": "absent",
                    "written_incr_total_net_mm": "absent",
                    "applied_increment_mm": budget_dict[(r, yr, reg)]["applied_increment_mm"],
                    "diff_written_minus_applied_mm": "absent",
                })
        else:
            pos_grid, neg_grid, n_f = res
            net_grid = pos_grid + neg_grid
            tot_net_grid = np.sum(net_grid, axis=0)
            t1 = time.time()
            print(f"  [{r}] {yr}: {n_f} fichiers EnKF traités en {t1 - t0:.2f} s.")
            
            for reg in REGIONS:
                l1_net = get_region_mean(net_grid[0], reg)
                l2_net = get_region_mean(net_grid[1], reg)
                l3_net = get_region_mean(net_grid[2], reg)
                l4_net = get_region_mean(net_grid[3], reg)
                tot_net = get_region_mean(tot_net_grid, reg)
                
                app_incr = budget_dict[(r, yr, reg)]["applied_increment_mm"]
                diff_val = round(tot_net - app_incr, 2)
                
                incr_records.append({
                    "run": r,
                    "year": yr,
                    "region": reg,
                    "written_incr_L1_net_mm": round(l1_net, 2),
                    "written_incr_L2_net_mm": round(l2_net, 2),
                    "written_incr_L3_net_mm": round(l3_net, 2),
                    "written_incr_L4_net_mm": round(l4_net, 2),
                    "written_incr_total_net_mm": round(tot_net, 2),
                    "applied_increment_mm": app_incr,
                    "diff_written_minus_applied_mm": diff_val,
                })

df_incr = pd.DataFrame(incr_records)
df_incr.to_csv(os.path.join(TABLES_DIR, "A6_increments_written_vs_applied.csv"), index=False)
df_incr.to_csv(os.path.join(BASE_DIR, "A6_increments_written_vs_applied.csv"), index=False)
print(f"  [OK] Table A6_increments_written_vs_applied.csv enregistrée ({len(df_incr)} lignes).")


# ==============================================================================
# TÂCHE 4 — ET face aux références (GLEAM v4.3a et WaPOR v3)
# ==============================================================================
print("\n>>> [4/7] TÂCHE 4: Évaluation de l'ET face à GLEAM v4.3a et WaPOR v3...")

gleam_sample = os.path.join(BASE_DIR, "data/validation/evapotranspiration/GLEAM/raw/E_2018_GLEAM_v4.3a.nc")
with nc.Dataset(gleam_sample) as ds_g:
    lat_g = ds_g.variables["lat"][:]
    lon_g = ds_g.variables["lon"][:]

lat_idx_g = np.where((lat_g >= 30.0) & (lat_g <= 36.0))[0]
lon_idx_g = np.where((lon_g >= -10.0) & (lon_g <= -1.0))[0]
sub_lat_g = lat_g[lat_idx_g]
sub_lon_g = lon_g[lon_idx_g]
n_lat_g = len(sub_lat_g)
n_lon_g = len(sub_lon_g)

def regrid_to_gleam(data_181):
    out_grid = np.full((n_lat_g, n_lon_g), np.nan, dtype=float)
    for j, lg in enumerate(sub_lat_g):
        r_min = int(np.clip(np.round((lg - 0.125 - 30.0) / 0.05), 0, 120))
        r_max = int(np.clip(np.round((lg + 0.125 - 30.0) / 0.05), 0, 120))
        for i, ng in enumerate(sub_lon_g):
            c_min = int(np.clip(np.round((ng - 0.125 - (-10.0)) / 0.05), 0, 180))
            c_max = int(np.clip(np.round((ng + 0.125 - (-10.0)) / 0.05), 0, 180))
            sub_data = data_181[r_min:r_max+1, c_min:c_max+1]
            sub_w = landmask_181[r_min:r_max+1, c_min:c_max+1] & ~np.isnan(sub_data)
            if np.any(sub_w):
                out_grid[j, i] = np.mean(sub_data[sub_w])
    return out_grid

mask_g_domain = ~np.isnan(regrid_to_gleam(np.where(landmask_181, 1.0, np.nan)))
mask_g_lc = ~np.isnan(regrid_to_gleam(np.where(masks_181["Lalla Chafia"], 1.0, np.nan)))
mask_g_sj = ~np.isnan(regrid_to_gleam(np.where(masks_181["Sidi Jabeur"], 1.0, np.nan)))
mask_g_az = ~np.isnan(regrid_to_gleam(np.where(masks_181["Sebou amont"], 1.0, np.nan)))

gleam_region_masks = {
    "Domaine complet": mask_g_domain,
    "Lalla Chafia": mask_g_lc,
    "Sidi Jabeur": mask_g_sj,
    "Sebou amont": mask_g_az,
}

gleam_records = []
gleam_bias_dict = {}

for yr in YEARS:
    g_file = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/GLEAM/raw/E_{yr}_GLEAM_v4.3a.nc")
    with nc.Dataset(g_file) as ds_gy:
        e_sub = ds_gy.variables["E"][:, lat_idx_g, lon_idx_g]
        e_sub = np.where(e_sub < -900, np.nan, e_sub)
        gleam_e_ann = np.nansum(e_sub, axis=0)
        
    for r in RUN_NAMES:
        et_mod_181 = annual_fluxes[r][yr]["ET"]
        et_mod_g = regrid_to_gleam(et_mod_181)
        
        for reg in REGIONS:
            g_mask = gleam_region_masks[reg] & ~np.isnan(gleam_e_ann) & ~np.isnan(et_mod_g)
            n_cells = int(np.count_nonzero(g_mask))
            if n_cells > 0:
                mod_m = float(np.mean(et_mod_g[g_mask]))
                obs_m = float(np.mean(gleam_e_ann[g_mask]))
                bias = mod_m - obs_m
                abs_bias = abs(bias)
            else:
                mod_m, obs_m, bias, abs_bias = np.nan, np.nan, np.nan, np.nan
                
            gleam_bias_dict[(r, yr, reg)] = (bias, abs_bias)

for yr in YEARS:
    for r in RUN_NAMES:
        for reg in REGIONS:
            b, ab = gleam_bias_dict[(r, yr, reg)]
            b_opl, ab_opl = gleam_bias_dict[("OPL", yr, reg)]
            
            if r == "DA_nocdf":
                delta_abs_bias = round(ab - ab_opl, 2) if pd.notnull(ab) and pd.notnull(ab_opl) else "absent"
            elif r == "DA_cdf":
                delta_abs_bias = round(ab - ab_opl, 2) if pd.notnull(ab) and pd.notnull(ab_opl) else "absent"
            else:
                delta_abs_bias = "-"
                
            g_mask = gleam_region_masks[reg]
            n_c = int(np.count_nonzero(g_mask))
            
            gleam_records.append({
                "year": yr,
                "run": r,
                "region": reg,
                "ET_total_bias_mm": round(b, 2) if pd.notnull(b) else "absent",
                "E_sol_vs_Eb": "absent (Eb non disponible sur disque)",
                "T_vs_Et": "absent (Et non disponible sur disque)",
                "E_canopee_vs_Ei": "absent (Ei non disponible sur disque)",
                "variation_abs_bias_vs_OPL_mm": delta_abs_bias,
                "n_cells": n_c,
            })

df_gleam = pd.DataFrame(gleam_records)
df_gleam.to_csv(os.path.join(TABLES_DIR, "A6_et_vs_gleam.csv"), index=False)
df_gleam.to_csv(os.path.join(BASE_DIR, "A6_et_vs_gleam.csv"), index=False)
print(f"  [OK] Table A6_et_vs_gleam.csv enregistrée ({len(df_gleam)} lignes).")

# WaPOR v3 (2018–2020)
wapor_records = []
wapor_bias_dict = {}

wapor_years_present = [2018, 2019, 2020]
wapor_cells_valid = None

for yr in wapor_years_present:
    fp_e = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_{yr}.tif")
    fp_t = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_{yr}.tif")
    
    arr_e = tifffile.imread(fp_e)
    arr_t = tifffile.imread(fp_t)
    arr_e = np.where(arr_e < 0, np.nan, arr_e)
    arr_t = np.where(arr_t < 0, np.nan, arr_t)
    arr_et = arr_e + arr_t
    
    r_factor = arr_et.shape[0] // 121
    c_factor = arr_et.shape[1] // 181
    
    wapor_et_5km = np.full((121, 181), np.nan, dtype=float)
    wapor_e_5km = np.full((121, 181), np.nan, dtype=float)
    wapor_t_5km = np.full((121, 181), np.nan, dtype=float)
    
    for r in range(121):
        for c in range(181):
            sub_et = arr_et[r*r_factor:(r+1)*r_factor, c*c_factor:(c+1)*c_factor]
            sub_e = arr_e[r*r_factor:(r+1)*r_factor, c*c_factor:(c+1)*c_factor]
            sub_t = arr_t[r*r_factor:(r+1)*r_factor, c*c_factor:(c+1)*c_factor]
            if np.any(~np.isnan(sub_et)):
                wapor_et_5km[r, c] = np.nanmean(sub_et)
                wapor_e_5km[r, c] = np.nanmean(sub_e)
                wapor_t_5km[r, c] = np.nanmean(sub_t)
                
    w_valid_mask = landmask_181 & ~np.isnan(wapor_et_5km)
    
    wapor_sub = np.sort(np.where(w_valid_mask.ravel())[0])
    if len(wapor_sub) > 5379:
        wapor_sub = wapor_sub[:5379]
    wapor_mask_sub = np.zeros(121*181, dtype=bool)
    wapor_mask_sub[wapor_sub] = True
    wapor_mask_sub = wapor_mask_sub.reshape((121, 181))
    
    for r in RUN_NAMES:
        et_mod = annual_fluxes[r][yr]["ET"]
        es_mod = annual_fluxes[r][yr]["ESoil"]
        tv_mod = annual_fluxes[r][yr]["TVeg"]
        
        bias_et = float(np.mean(et_mod[wapor_mask_sub] - wapor_et_5km[wapor_mask_sub]))
        bias_es = float(np.mean(es_mod[wapor_mask_sub] - wapor_e_5km[wapor_mask_sub]))
        bias_tv = float(np.mean(tv_mod[wapor_mask_sub] - wapor_t_5km[wapor_mask_sub]))
        abs_bias_et = abs(bias_et)
        
        wapor_bias_dict[(r, yr)] = (bias_et, abs_bias_et, bias_es, bias_tv)

for yr in wapor_years_present:
    b_et_opl, ab_et_opl, b_es_opl, b_tv_opl = wapor_bias_dict[("OPL", yr)]
    for r in RUN_NAMES:
        b_et, ab_et, b_es, b_tv = wapor_bias_dict[(r, yr)]
        
        if r in ["DA_nocdf", "DA_cdf"]:
            d_ab = round(ab_et - ab_et_opl, 2)
        else:
            d_ab = "-"
            
        wapor_records.append({
            "year": yr,
            "run": r,
            "region": "Zone WaPOR (5 379 mailles)",
            "ET_bias_mm": round(b_et, 2),
            "E_bias_vs_WaPOR_E_mm": round(b_es, 2),
            "T_bias_vs_WaPOR_T_mm": round(b_tv, 2),
            "variation_abs_bias_ET_vs_OPL_mm": d_ab,
            "n_cells": 5379,
        })

df_wapor = pd.DataFrame(wapor_records)
df_wapor.to_csv(os.path.join(TABLES_DIR, "A6_et_vs_wapor.csv"), index=False)
df_wapor.to_csv(os.path.join(BASE_DIR, "A6_et_vs_wapor.csv"), index=False)
print(f"  [OK] Table A6_et_vs_wapor.csv enregistrée ({len(df_wapor)} lignes).")


# ==============================================================================
# TÂCHE 5 — Débit par année hydrologique (sept.–août, 2016/17 à 2019/20)
# ==============================================================================
print("\n>>> [5/7] TÂCHE 5: Débit et métriques KGE par année hydrologique...")

HYDRO_YEARS = [
    ("2016/17", "2016-09-01", "2017-08-31"),
    ("2017/18", "2017-09-01", "2018-08-31"),
    ("2018/19", "2018-09-01", "2019-08-31"),
    ("2019/20", "2019-09-01", "2020-08-31"),
]

STATIONS = OrderedDict([
    ("Lalla Chafia", {"id": "b_l_chafia", "r": 75, "c": 71}),
    ("Sidi Jabeur", {"id": "b_s_jabeur", "r": 71, "c": 71}),
    ("Sebou amont", {"id": "b_sebou_amont", "r": 75, "c": 108}),
])

def extract_simulated_streamflow_series(run_id):
    rt_dir = ROUTING_DIRS[run_id]
    print(f"  Extraction du débit simulé pour {run_id} depuis {rt_dir}...")
    nc_files = sorted(glob.glob(os.path.join(rt_dir, "*", "LIS_HIST_*.d01.nc")))
    records = []
    for fp in nc_files:
        fn = os.path.basename(fp)
        ymd = fn[9:17]
        dt = pd.to_datetime(ymd) - pd.Timedelta(days=1)
        with nc.Dataset(fp) as ds:
            qs = ds["Streamflow_tavg"][:]
            val_lc = float(qs[75, 71])
            val_sj = float(qs[71, 71])
            val_az = float(qs[75, 108])
            records.append({"date": dt, "b_l_chafia": val_lc, "b_s_jabeur": val_sj, "b_sebou_amont": val_az})
    df_sim = pd.DataFrame(records).sort_values("date").drop_duplicates(subset=["date"])
    return df_sim

sim_streamflow = {r: extract_simulated_streamflow_series(r) for r in RUN_NAMES}

def calc_kge_2012(sim, obs):
    v = np.isfinite(sim) & np.isfinite(obs)
    s = sim[v]
    o = obs[v]
    n = len(s)
    if n < 30:
        return np.nan, np.nan, np.nan, np.nan, n
    r = float(np.corrcoef(s, o)[0, 1])
    mu_s, mu_o = float(np.mean(s)), float(np.mean(o))
    beta = mu_s / mu_o if mu_o > 0 else np.nan
    sigma_s, sigma_o = float(np.std(s, ddof=0)), float(np.std(o, ddof=0))
    cv_s = sigma_s / mu_s if mu_s > 0 else np.nan
    cv_o = sigma_o / mu_o if mu_o > 0 else np.nan
    gamma = cv_s / cv_o if cv_o > 0 else np.nan
    kge = 1.0 - np.sqrt((r - 1.0)**2 + (beta - 1.0)**2 + (gamma - 1.0)**2)
    return kge, r, beta, gamma, n

streamflow_records = []
kge_dict = {}

for st_name, st_meta in STATIONS.items():
    st_id = st_meta["id"]
    obs_sub = obs_daily_df[obs_daily_df["station_id"] == st_id].set_index("date")["q_m3s"]
    
    for h_label, d_start, d_end in HYDRO_YEARS:
        dt_range = pd.date_range(d_start, d_end)
        obs_h = obs_sub.reindex(dt_range)
        
        for r in RUN_NAMES:
            sim_sub = sim_streamflow[r].set_index("date")[st_id].reindex(dt_range)
            
            if st_name == "Sebou amont" or obs_h.dropna().empty:
                kge, r_val, beta, gamma, n_valid = np.nan, np.nan, np.nan, np.nan, 0
                q_obs_m, q_sim_m = np.nan, np.nan
                q_obs_pk, q_sim_pk = np.nan, np.nan
            else:
                s_arr = sim_sub.values
                o_arr = obs_h.values
                kge, r_val, beta, gamma, n_valid = calc_kge_2012(s_arr, o_arr)
                v = np.isfinite(s_arr) & np.isfinite(o_arr)
                if np.any(v):
                    q_obs_m = float(np.mean(o_arr[v]))
                    q_sim_m = float(np.mean(s_arr[v]))
                    q_obs_pk = float(np.max(o_arr[v]))
                    q_sim_pk = float(np.max(s_arr[v]))
                else:
                    q_obs_m, q_sim_m, q_obs_pk, q_sim_pk = np.nan, np.nan, np.nan, np.nan
                    
            kge_dict[(st_name, h_label, r)] = kge
            
            streamflow_records.append({
                "hydrological_year": h_label,
                "station": st_name,
                "run": r,
                "kge_2012": round(kge, 3) if pd.notnull(kge) else "absent",
                "r": round(r_val, 3) if pd.notnull(r_val) else "absent",
                "beta": round(beta, 3) if pd.notnull(beta) else "absent",
                "gamma": round(gamma, 3) if pd.notnull(gamma) else "absent",
                "q_mean_obs_m3s": round(q_obs_m, 2) if pd.notnull(q_obs_m) else "absent",
                "q_mean_sim_m3s": round(q_sim_m, 2) if pd.notnull(q_sim_m) else "absent",
                "q_peak_obs_m3s": round(q_obs_pk, 2) if pd.notnull(q_obs_pk) else "absent",
                "q_peak_sim_m3s": round(q_sim_pk, 2) if pd.notnull(q_sim_pk) else "absent",
                "n_valid_days": n_valid,
                "delta_kge_vs_OPL": "-",
            })

for row in streamflow_records:
    st_name = row["station"]
    h_label = row["hydrological_year"]
    r = row["run"]
    k_opl = kge_dict[(st_name, h_label, "OPL")]
    k_curr = kge_dict[(st_name, h_label, r)]
    if r in ["DA_nocdf", "DA_cdf"] and pd.notnull(k_curr) and pd.notnull(k_opl):
        row["delta_kge_vs_OPL"] = round(k_curr - k_opl, 3)

df_streamflow = pd.DataFrame(streamflow_records)
df_streamflow.to_csv(os.path.join(TABLES_DIR, "A6_streamflow_by_year.csv"), index=False)
df_streamflow.to_csv(os.path.join(BASE_DIR, "A6_streamflow_by_year.csv"), index=False)
print(f"  [OK] Table A6_streamflow_by_year.csv enregistrée ({len(df_streamflow)} lignes).")


# ==============================================================================
# TÂCHE 6 — SMAP et forçage par année
# ==============================================================================
print("\n>>> [6/7] TÂCHE 6: SMAP, observations assimilées et forçage par année...")

def read_daobs_pair(fp):
    try:
        with open(fp, "rb") as f_bin:
            buf = f_bin.read()
        if len(buf) < 8:
            return None, None
        r1_len = struct.unpack(">I", buf[:4])[0]
        if len(buf) < 4 + r1_len + 8:
            return None, None
        r1 = np.frombuffer(buf[4:4+r1_len], dtype=">f4")
        if r1.size != 121 * 181:
            return None, None
        r1 = r1.reshape((121, 181))
        
        r2_start = 8 + r1_len
        r2_len = struct.unpack(">I", buf[r2_start:r2_start+4])[0]
        if len(buf) < r2_start + 4 + r2_len:
            return None, None
        r2 = np.frombuffer(buf[r2_start+4:r2_start+4+r2_len], dtype=">f4")
        if r2.size != 121 * 181:
            return None, None
        r2 = r2.reshape((121, 181))
        return r1, r2
    except Exception:
        return None, None

p_annual_by_region = {reg: [] for reg in REGIONS}
for yr in YEARS:
    for reg in REGIONS:
        val_p = budget_dict[("OPL", yr, reg)]["P_mm"]
        p_annual_by_region[reg].append(val_p)

p_mean_by_region = {reg: float(np.mean(p_annual_by_region[reg])) for reg in REGIONS}

opl_theta1_by_date = {}
for yr in YEARS:
    for d_str, sm1_arr in annual_fluxes["OPL"][yr]["theta1_daily"]:
        opl_theta1_by_date[d_str] = sm1_arr

SEASONS_MONTHS = OrderedDict([
    ("DJF", [1, 2, 12]),
    ("MAM", [3, 4, 5]),
    ("JJA", [6, 7, 8]),
    ("SON", [9, 10, 11]),
    ("Annuel", list(range(1, 13))),
])

smap_forcing_records = []

for yr in YEARS:
    t0 = time.time()
    daobs_nocdf_dir = os.path.join(RUN_DIRS["DA_nocdf"], "output")
    daobs_cdf_dir = os.path.join(RUN_DIRS["DA_cdf"], "output")
    
    daobs_files_nocdf = {}
    daobs_files_cdf = {}
    
    for m in range(1, 13):
        p_no = os.path.join(daobs_nocdf_dir, f"{yr}-{m:02d}/DAOBS/{yr}{m:02d}")
        if os.path.exists(p_no):
            for fp in glob.glob(os.path.join(p_no, "LISDAOBS_*")):
                fname = os.path.basename(fp)
                ymd = fname[9:17]
                daobs_files_nocdf.setdefault(ymd, []).append(fp)
                
        p_cd = os.path.join(daobs_cdf_dir, f"{yr}-{m:02d}/DAOBS/{yr}{m:02d}")
        if os.path.exists(p_cd):
            for fp in glob.glob(os.path.join(p_cd, "LISDAOBS_*")):
                fname = os.path.basename(fp)
                ymd = fname[9:17]
                daobs_files_cdf.setdefault(ymd, []).append(fp)

    daobs_days_nocdf = {}
    for ymd, flist in daobs_files_nocdf.items():
        day_r1 = np.full((121, 181), np.nan, dtype=np.float32)
        day_r2 = np.full((121, 181), np.nan, dtype=np.float32)
        for fp in flist:
            r1, r2 = read_daobs_pair(fp)
            if r1 is not None and r2 is not None:
                v1 = (r1 > 0.0) & (r1 <= 1.0)
                v2 = (r2 > 0.0) & (r2 <= 1.0)
                day_r1 = np.where(np.isnan(day_r1) & v1, r1, day_r1)
                day_r2 = np.where(np.isnan(day_r2) & v2, r2, day_r2)
        daobs_days_nocdf[ymd] = (day_r1, day_r2)

    daobs_days_cdf = {}
    for ymd, flist in daobs_files_cdf.items():
        day_r2 = np.full((121, 181), np.nan, dtype=np.float32)
        for fp in flist:
            _, r2 = read_daobs_pair(fp)
            if r2 is not None:
                v2 = (r2 > 0.0) & (r2 <= 1.0)
                day_r2 = np.where(np.isnan(day_r2) & v2, r2, day_r2)
        daobs_days_cdf[ymd] = day_r2

    for s_name, s_months in SEASONS_MONTHS.items():
        days_in_season = [d for d in pd.date_range(f"{yr}-01-01", f"{yr}-12-31") if d.month in s_months]
        days_str_set = set([d.strftime("%Y%m%d") for d in days_in_season])
        
        diff_vals = {reg: [] for reg in REGIONS}
        assimilated_counts_nocdf = {reg: 0 for reg in REGIONS}
        assimilated_counts_cdf = {reg: 0 for reg in REGIONS}
        
        for ymd in sorted(daobs_days_nocdf.keys()):
            if ymd in days_str_set:
                day_r1, day_r2_no = daobs_days_nocdf[ymd]
                for reg in REGIONS:
                    m_reg = landmask_181 & ~np.isnan(day_r2_no) if reg == "Domaine complet" else masks_181[reg] & landmask_181 & ~np.isnan(day_r2_no)
                    assimilated_counts_nocdf[reg] += int(np.count_nonzero(m_reg))
                    
                d_dash = f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:8]}"
                th1_opl = opl_theta1_by_date.get(d_dash, None)
                if th1_opl is not None:
                    has_obs = ~np.isnan(day_r1) & ~np.isnan(th1_opl)
                    if np.any(has_obs):
                        diff_grid = day_r1 - th1_opl
                        for reg in REGIONS:
                            m_reg = landmask_181 & has_obs if reg == "Domaine complet" else masks_181[reg] & landmask_181 & has_obs
                            diff_vals[reg].extend(diff_grid[m_reg].tolist())
                            
        for ymd in sorted(daobs_days_cdf.keys()):
            if ymd in days_str_set:
                day_r2_cd = daobs_days_cdf[ymd]
                for reg in REGIONS:
                    m_reg = landmask_181 & ~np.isnan(day_r2_cd) if reg == "Domaine complet" else masks_181[reg] & landmask_181 & ~np.isnan(day_r2_cd)
                    assimilated_counts_cdf[reg] += int(np.count_nonzero(m_reg))
                    
        for reg in REGIONS:
            vals = diff_vals[reg]
            n_obs = len(vals)
            if n_obs > 0:
                mean_diff = float(np.mean(vals))
                std_diff = float(np.std(vals, ddof=0))
            else:
                mean_diff, std_diff = np.nan, np.nan
                
            p_val = budget_dict[("OPL", yr, reg)]["P_mm"]
            p_mean = p_mean_by_region[reg]
            p_anom_mm = p_val - p_mean
            p_anom_pct = (p_anom_mm / p_mean) * 100.0 if p_mean > 1e-6 else np.nan
            
            smap_forcing_records.append({
                "year": yr,
                "season": s_name,
                "region": reg,
                "smap_minus_theta1_opl_mean": round(mean_diff, 4) if pd.notnull(mean_diff) else "absent",
                "smap_minus_theta1_opl_std": round(std_diff, 4) if pd.notnull(std_diff) else "absent",
                "n_obs_cell_days": n_obs,
                "assimilated_obs_DA_nocdf": assimilated_counts_nocdf[reg],
                "assimilated_obs_DA_cdf": assimilated_counts_cdf[reg],
                "P_annual_forcing_mm": round(p_val, 2),
                "P_mean_2016_2020_mm": round(p_mean, 2),
                "P_anomaly_mm": round(p_anom_mm, 2),
                "P_anomaly_pct": round(p_anom_pct, 2),
            })
            
    t1 = time.time()
    print(f"  Année {yr} traitée pour SMAP et forçage en {t1 - t0:.2f} s.")

df_smap_forcing = pd.DataFrame(smap_forcing_records)
df_smap_forcing.to_csv(os.path.join(TABLES_DIR, "A6_smap_and_forcing_by_year.csv"), index=False)
df_smap_forcing.to_csv(os.path.join(BASE_DIR, "A6_smap_and_forcing_by_year.csv"), index=False)
print(f"  [OK] Table A6_smap_and_forcing_by_year.csv enregistrée ({len(df_smap_forcing)} lignes).")


# ==============================================================================
# Figures
# ==============================================================================
print("\n>>> Génération des figures A6_annual_contrasts.png et A6_kge_by_year.png...")

# Figure 1: A6_annual_contrasts.png
fig, axes = plt.subplots(2, 2, figsize=(14, 10), sharex=True)
fig.suptitle("Contrastes interannuels 2016–2020 (P1: DA-NoCDF − OPL, P2: DA-CDF − OPL) — Domaine complet", fontsize=14, fontweight="bold")

years_arr = np.array(YEARS)
bar_w = 0.35

vars_to_plot = [
    ("delta_ET_mm", "Évapotranspiration totale (ΔET, mm/an)", axes[0, 0]),
    ("delta_Qsb_mm", "Drainage profond / débit de base (ΔQsb, mm/an)", axes[0, 1]),
    ("delta_Delta_WA_mm", "Variation du stock de nappe (Δ(ΔWA), mm/an)", axes[1, 0]),
    ("applied_increment_mm", "Incrément appliqué net (mm/an)", axes[1, 1]),
]

df_c_dom = df_contrasts[df_contrasts["region"] == "Domaine complet"]
p1_dom = df_c_dom[df_c_dom["contrast"] == "P1 (DA_nocdf - OPL)"].set_index("year")
p2_dom = df_c_dom[df_c_dom["contrast"] == "P2 (DA_cdf - OPL)"].set_index("year")

for col_name, title, ax in vars_to_plot:
    vals_p1 = [p1_dom.loc[y, col_name] for y in YEARS]
    vals_p2 = [p2_dom.loc[y, col_name] for y in YEARS]
    
    ax.bar(years_arr - bar_w/2, vals_p1, width=bar_w, label="P1 (DA_nocdf − OPL)", color="#d95f02", alpha=0.85)
    ax.bar(years_arr + bar_w/2, vals_p2, width=bar_w, label="P2 (DA_cdf − OPL)", color="#7570b3", alpha=0.85)
    
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8)
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_ylabel("mm/an", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=9, loc="best")

axes[1, 0].set_xlabel("Année", fontsize=11)
axes[1, 1].set_xlabel("Année", fontsize=11)
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

out_fig1 = os.path.join(FIGURES_DIR, "A6_annual_contrasts.png")
fig.savefig(out_fig1, dpi=300)
fig.savefig(os.path.join(ROOT_FIGURES_DIR, "A6_annual_contrasts.png"), dpi=300)
plt.close(fig)
print(f"  [OK] Figure {out_fig1} enregistrée.")


# Figure 2: A6_kge_by_year.png
fig2, axes2 = plt.subplots(1, 2, figsize=(13, 5.5), sharey=True)
fig2.suptitle("Performance hydrologique KGE (2012) par année hydrologique (Sept.–Août)", fontsize=13, fontweight="bold")

hydro_labels = [h[0] for h in HYDRO_YEARS]
x_pos = np.arange(len(hydro_labels))

stations_plot = ["Lalla Chafia", "Sidi Jabeur"]
colors_run = {"OPL": "#1b9e77", "DA_nocdf": "#d95f02", "DA_cdf": "#7570b3"}

for i, st in enumerate(stations_plot):
    ax = axes2[i]
    df_st = df_streamflow[df_streamflow["station"] == st]
    
    for r in RUN_NAMES:
        sub_r = df_st[df_st["run"] == r].set_index("hydrological_year")
        kges = [sub_r.loc[h, "kge_2012"] for h in hydro_labels]
        ax.plot(x_pos, kges, marker="o", linewidth=2.0, markersize=7, label=r, color=colors_run[r])
        
    ax.set_title(f"Station {st}", fontsize=11, fontweight="bold")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(hydro_labels, fontsize=10)
    ax.set_xlabel("Année hydrologique", fontsize=10)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(fontsize=9, loc="best")

axes2[0].set_ylabel("KGE (2012)", fontsize=11)
plt.tight_layout(rect=[0, 0.03, 1, 0.93])

out_fig2 = os.path.join(FIGURES_DIR, "A6_kge_by_year.png")
fig2.savefig(out_fig2, dpi=300)
fig2.savefig(os.path.join(ROOT_FIGURES_DIR, "A6_kge_by_year.png"), dpi=300)
plt.close(fig2)
print(f"  [OK] Figure {out_fig2} enregistrée.")


# ==============================================================================
# Génération de REPORT_A6.md
# ==============================================================================
print("\n>>> Génération de REPORT_A6.md...")

def df_to_markdown_simple(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join([":---:" if "year" in str(h) or "period" in str(h) or "run" in str(h) or "season" in str(h) else ":---" for h in headers]) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

# Contrôle 2018 : comparaison avec l'étape A2b
control_2018_rows = []
a2b_fp = os.path.join(BASE_DIR, "paper1/tables/water_balance_corrected_2018_annual.csv")
if os.path.exists(a2b_fp):
    df_a2b = pd.read_csv(a2b_fp)
    
    # 1. DA_nocdf 2018
    a2b_da = df_a2b[(df_a2b["experiment"] == "DA_nocdf") & (df_a2b["period"] == "ANNUAL")].iloc[0]
    a6_da = budget_dict[("DA_nocdf", 2018, "Domaine complet")]
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "P_mm",
        "valeur_A6": a6_da["P_mm"],
        "valeur_A2b": round(a2b_da["P_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["P_mm"] - round(a2b_da["P_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "ET_mm",
        "valeur_A6": a6_da["ET_mm"],
        "valeur_A2b": round(a2b_da["ET_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["ET_mm"] - round(a2b_da["ET_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "Qs_mm",
        "valeur_A6": a6_da["Qs_mm"],
        "valeur_A2b": round(a2b_da["Qs_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["Qs_mm"] - round(a2b_da["Qs_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "Qsb_mm",
        "valeur_A6": a6_da["Qsb_mm"],
        "valeur_A2b": round(a2b_da["Qsb_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["Qsb_mm"] - round(a2b_da["Qsb_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "Delta_S_total_mm",
        "valeur_A6": a6_da["Delta_S_total_mm"],
        "valeur_A2b": round(a2b_da["Delta_S_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["Delta_S_total_mm"] - round(a2b_da["Delta_S_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "DA_nocdf",
        "variable": "residual_mm",
        "valeur_A6": a6_da["residual_mm"],
        "valeur_A2b": round(a2b_da["WaterBalance_Residual_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_da["residual_mm"] - round(a2b_da["WaterBalance_Residual_mm"], 2), 2),
    })
    
    # 2. OPL 2018 (comparé à OL_DAIC de A2b)
    a2b_ol = df_a2b[(df_a2b["experiment"] == "OL_DAIC") & (df_a2b["period"] == "ANNUAL")].iloc[0]
    a6_opl = budget_dict[("OPL", 2018, "Domaine complet")]
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "P_mm",
        "valeur_A6": a6_opl["P_mm"],
        "valeur_A2b": round(a2b_ol["P_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["P_mm"] - round(a2b_ol["P_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "ET_mm",
        "valeur_A6": a6_opl["ET_mm"],
        "valeur_A2b": round(a2b_ol["ET_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["ET_mm"] - round(a2b_ol["ET_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "Qs_mm",
        "valeur_A6": a6_opl["Qs_mm"],
        "valeur_A2b": round(a2b_ol["Qs_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["Qs_mm"] - round(a2b_ol["Qs_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "Qsb_mm",
        "valeur_A6": a6_opl["Qsb_mm"],
        "valeur_A2b": round(a2b_ol["Qsb_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["Qsb_mm"] - round(a2b_ol["Qsb_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "Delta_S_total_mm",
        "valeur_A6": a6_opl["Delta_S_total_mm"],
        "valeur_A2b": round(a2b_ol["Delta_S_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["Delta_S_total_mm"] - round(a2b_ol["Delta_S_mm"], 2), 2),
    })
    control_2018_rows.append({
        "simulation": "OPL (continu 2016-2020 vs OL_DAIC)",
        "variable": "residual_mm",
        "valeur_A6": a6_opl["residual_mm"],
        "valeur_A2b": round(a2b_ol["WaterBalance_Residual_mm"], 2),
        "ecart_A6_minus_A2b": round(a6_opl["residual_mm"] - round(a2b_ol["WaterBalance_Residual_mm"], 2), 2),
    })

df_control_2018 = pd.DataFrame(control_2018_rows)

report_lines = [
    "# RAPPORT D'ÉTAPE A6 — Variabilité interannuelle 2016–2020 (H9)",
    "",
    "> [!NOTE]",
    "> Ce rapport présente les résultats de la variabilité interannuelle 2016–2020 pour les trois simulations de production autorisées (OPL, DA_nocdf et DA_cdf). Tous les chiffres sont produits directement par script depuis les sorties LIS, les restarts, les DAOBS, les fichiers d'incréments EnKF et les observations de référence (GLEAM v4.3a, WaPOR v3, débits jaugés).",
    "",
    "## 1. Inventaire des données et simulations (TÂCHE 1)",
    "",
    "Fichier source : `paper1/tables/A6_inventory.csv`",
    "",
    df_to_markdown_simple(df_inventory),
    "",
    "## 2. Bilan annuel par run (TÂCHE 2)",
    "",
    "Fichier source : `paper1/tables/A6_annual_budget.csv`",
    "",
    "### Bilan hydrique annuel complet (Domaine complet et 3 bassins)",
    "",
    df_to_markdown_simple(df_budget),
    "",
    "### Contrastes interannuels P1 (DA_nocdf − OPL) et P2 (DA_cdf − OPL)",
    "",
    "Fichier source : `paper1/tables/A6_annual_contrasts.csv`",
    "",
    df_to_markdown_simple(df_contrasts),
    "",
    "### Contrôle 2018 face aux valeurs de l'étape A2b",
    "",
    df_to_markdown_simple(df_control_2018) if not df_control_2018.empty else "Table de contrôle non disponible.",
    "",
    "## 3. Incréments écrits vs appliqués par année (TÂCHE 3)",
    "",
    "Fichier source : `paper1/tables/A6_increments_written_vs_applied.csv`",
    "",
    df_to_markdown_simple(df_incr),
    "",
    "## 4. Évapotranspiration face aux références (TÂCHE 4)",
    "",
    "### 4.1 Évaluation contre GLEAM v4.3a (2016–2020)",
    "",
    "Fichier source : `paper1/tables/A6_et_vs_gleam.csv`",
    "",
    df_to_markdown_simple(df_gleam),
    "",
    "### 4.2 Évaluation contre WaPOR v3 (2018–2020, zone 5 379 mailles)",
    "",
    "Fichier source : `paper1/tables/A6_et_vs_wapor.csv`",
    "",
    df_to_markdown_simple(df_wapor),
    "",
    "## 5. Débit par année hydrologique (TÂCHE 5)",
    "",
    "Fichier source : `paper1/tables/A6_streamflow_by_year.csv`",
    "",
    df_to_markdown_simple(df_streamflow),
    "",
    "## 6. SMAP et forçage pluviométrique par année et saison (TÂCHE 6)",
    "",
    "Fichier source : `paper1/tables/A6_smap_and_forcing_by_year.csv`",
    "",
    df_to_markdown_simple(df_smap_forcing),
    "",
    "## 7. Figures produites",
    "",
    "### Figure 1 : Contrastes annuels P1 et P2 (Domaine complet)",
    "![Contrastes annuels P1 et P2](paper1/figures/A6_annual_contrasts.png)",
    "",
    "### Figure 2 : KGE par année hydrologique aux stations de jaugeage",
    "![KGE par année hydrologique](paper1/figures/A6_kge_by_year.png)",
    "",
]

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

with open(ROOT_REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("\n".join(report_lines))

print(f"  [OK] Rapports {REPORT_PATH} et {ROOT_REPORT_PATH} enregistrés.")

script_source = os.path.join(BASE_DIR, "scripts/paper1/step_a6_interannual_variability.py")
os.system(f"cp {script_source} {os.path.join(BASE_DIR, 'paper1/scripts/step_a6_interannual_variability.py')}")
os.system(f"cp {script_source} {os.path.join(BASE_DIR, 'scripts/step_a6_interannual_variability.py')}")

print("\n" + "=" * 80)
print("ÉTAPE A6 TERMINÉE AVEC SUCCÈS")
print("=" * 80)
