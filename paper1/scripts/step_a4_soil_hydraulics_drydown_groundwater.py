#!/usr/bin/env python3
"""
step_a4_soil_hydraulics_drydown_groundwater.py

Step A4 — Hydraulique du sol, assèchement, nappe (H2).
Aucun chiffre tapé à la main, tout est extrait par script depuis les données et le code.
"""

import os
import sys
import glob
import time
import datetime
import multiprocessing as mp
from collections import OrderedDict

import numpy as np
import pandas as pd
import netCDF4 as nc
from scipy.optimize import curve_fit
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
SCRIPTS_DIR = os.path.join(BASE_DIR, "paper1/scripts")
REPORT_FILE_1 = os.path.join(BASE_DIR, "REPORT_A4.md")
REPORT_FILE_2 = os.path.join(BASE_DIR, "paper1/REPORT_A4.md")

CACHE_FILE_UNCENSORED = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/daily_cache_uncensored_2016_2020.npz"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
SOILPARM_PATH = os.path.join(BASE_DIR, "data/land_params/noahmp401_parms/SOILPARM.TBL")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")

EXP_ENS_CORR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL")
EXP_OL_DAIC = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL")
EXP_DA_CORR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL")

USDA_TEXTURE_NAMES = {
    1: "Sand",
    2: "Loamy Sand",
    3: "Sandy Loam",
    4: "Silt Loam",
    5: "Silt",
    6: "Loam",
    7: "Sandy Clay Loam",
    8: "Silty Clay Loam",
    9: "Clay Loam",
    10: "Sandy Clay",
    11: "Silty Clay",
    12: "Clay",
    13: "Organic Material",
    14: "Water",
    15: "Bedrock",
    16: "Other (land-ice)",
    17: "Playa",
    18: "Lava",
    19: "White Sand"
}

def get_season(dt):
    m = dt.month
    if m in [12, 1, 2]:
        return "DJF"
    elif m in [3, 4, 5]:
        return "MAM"
    elif m in [6, 7, 8]:
        return "JJA"
    else:
        return "SON"

def exp_decay(t, theta_res, delta_theta, tau):
    return theta_res + delta_theta * np.exp(-t / tau)

def fit_single_drydown(t_obs, sm_obs, min_obs=3):
    if len(t_obs) < min_obs:
        return None
    ss_tot = float(np.sum((sm_obs - np.mean(sm_obs))**2))
    if ss_tot < 1e-7:
        return None
    lb = [0.001, 0.001, 0.5]
    ub = [0.55, 0.50, 60.0]
    p0 = [
        max(lb[0], min(ub[0], float(np.min(sm_obs)))),
        max(lb[1], min(ub[1], float(np.max(sm_obs) - np.min(sm_obs)))),
        5.0
    ]
    try:
        popt, _ = curve_fit(exp_decay, t_obs, sm_obs, p0=p0, bounds=(lb, ub), maxfev=400)
        theta_res, delta_theta, tau = float(popt[0]), float(popt[1]), float(popt[2])
        pred = exp_decay(t_obs, *popt)
        ss_res = float(np.sum((sm_obs - pred)**2))
        r2 = 1.0 - (ss_res / ss_tot)
        if r2 >= 0.7 and delta_theta > 0.002 and (0.5 <= tau <= 60.0):
            return {
                "theta_res": theta_res,
                "delta_theta": delta_theta,
                "tau": tau,
                "r2": float(r2)
            }
        return None
    except Exception:
        return None

def process_pixel_episodes_2018(args):
    r, c, p_series, smap_series, ens_series, ol_series, stype, stype_name, basin_name, lat_val, lon_val, dates_list = args
    results = []
    n_days = len(p_series)
    i = 0
    while i < n_days - 4:
        if p_series[i] >= 5.0 and p_series[i] < 500.0:
            k = i + 1
            while k < n_days and (0.0 <= p_series[k] < 1.0):
                k += 1
            dry_len = k - (i + 1)
            if dry_len >= 4:
                t_idx = np.arange(1, dry_len + 1)
                smap_win = smap_series[i + 1 : k]
                ens_win = ens_series[i + 1 : k]
                ol_win = ol_series[i + 1 : k]
                v_smap = np.isfinite(smap_win)
                n_smap = int(np.sum(v_smap))
                if n_smap >= 3:
                    t_obs = t_idx[v_smap]
                    smap_obs = smap_win[v_smap]
                    ens_obs = ens_win[v_smap]
                    ol_obs = ol_win[v_smap]
                    
                    fit_smap = fit_single_drydown(t_obs, smap_obs, min_obs=3)
                    fit_ens = fit_single_drydown(t_obs, ens_obs, min_obs=3)
                    fit_ol = fit_single_drydown(t_obs, ol_obs, min_obs=3)
                    
                    start_date = dates_list[i + 1]
                    season = get_season(start_date)
                    
                    tau_smap = fit_smap["tau"] if fit_smap else np.nan
                    dth_smap = fit_smap["delta_theta"] if fit_smap else np.nan
                    th_inf_smap = fit_smap["theta_res"] if fit_smap else np.nan
                    r2_smap = fit_smap["r2"] if fit_smap else np.nan
                    
                    tau_ens = fit_ens["tau"] if fit_ens else np.nan
                    dth_ens = fit_ens["delta_theta"] if fit_ens else np.nan
                    th_inf_ens = fit_ens["theta_res"] if fit_ens else np.nan
                    r2_ens = fit_ens["r2"] if fit_ens else np.nan
                    
                    tau_ol = fit_ol["tau"] if fit_ol else np.nan
                    dth_ol = fit_ol["delta_theta"] if fit_ol else np.nan
                    th_inf_ol = fit_ol["theta_res"] if fit_ol else np.nan
                    r2_ol = fit_ol["r2"] if fit_ol else np.nan
                    
                    ratio_ens = (tau_ens / tau_smap) if (np.isfinite(tau_smap) and np.isfinite(tau_ens)) else np.nan
                    ratio_ol = (tau_ol / tau_smap) if (np.isfinite(tau_smap) and np.isfinite(tau_ol)) else np.nan
                    
                    results.append({
                        "pixel_row": r,
                        "pixel_col": c,
                        "lat": lat_val,
                        "lon": lon_val,
                        "soil_texture_id": stype,
                        "soil_texture_name": stype_name,
                        "basin": basin_name,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "dry_len_days": dry_len,
                        "season": season,
                        "n_obs_smap": n_smap,
                        "tau_smap": tau_smap,
                        "delta_theta_smap": dth_smap,
                        "theta_inf_smap": th_inf_smap,
                        "r2_smap": r2_smap,
                        "tau_ens_corr": tau_ens,
                        "delta_theta_ens_corr": dth_ens,
                        "theta_inf_ens_corr": th_inf_ens,
                        "r2_ens_corr": r2_ens,
                        "tau_ol_daic": tau_ol,
                        "delta_theta_ol_daic": dth_ol,
                        "theta_inf_ol_daic": th_inf_ol,
                        "r2_ol_daic": r2_ol,
                        "ratio_tau_ens_over_smap": ratio_ens,
                        "ratio_tau_ol_over_smap": ratio_ol
                    })
                i = k
            else:
                i += 1
        else:
            i += 1
    return results

def process_pixel_episodes_2016_2020(args):
    r, c, p_series, smap_series, opl_series, stype, stype_name, basin_name, lat_val, lon_val, dates_list = args
    results = []
    n_days = len(p_series)
    i = 0
    while i < n_days - 4:
        if p_series[i] >= 5.0 and p_series[i] < 500.0:
            k = i + 1
            while k < n_days and (0.0 <= p_series[k] < 1.0):
                k += 1
            dry_len = k - (i + 1)
            if dry_len >= 4:
                t_idx = np.arange(1, dry_len + 1)
                smap_win = smap_series[i + 1 : k]
                opl_win = opl_series[i + 1 : k]
                v_smap = np.isfinite(smap_win)
                n_smap = int(np.sum(v_smap))
                if n_smap >= 3:
                    t_obs = t_idx[v_smap]
                    smap_obs = smap_win[v_smap]
                    opl_obs = opl_win[v_smap]
                    
                    fit_smap = fit_single_drydown(t_obs, smap_obs, min_obs=3)
                    fit_opl = fit_single_drydown(t_obs, opl_obs, min_obs=3)
                    
                    start_date = dates_list[i + 1]
                    season = get_season(start_date)
                    
                    tau_smap = fit_smap["tau"] if fit_smap else np.nan
                    dth_smap = fit_smap["delta_theta"] if fit_smap else np.nan
                    th_inf_smap = fit_smap["theta_res"] if fit_smap else np.nan
                    r2_smap = fit_smap["r2"] if fit_smap else np.nan
                    
                    tau_opl = fit_opl["tau"] if fit_opl else np.nan
                    dth_opl = fit_opl["delta_theta"] if fit_opl else np.nan
                    th_inf_opl = fit_opl["theta_res"] if fit_opl else np.nan
                    r2_opl = fit_opl["r2"] if fit_opl else np.nan
                    
                    ratio_opl = (tau_opl / tau_smap) if (np.isfinite(tau_smap) and np.isfinite(tau_opl)) else np.nan
                    
                    results.append({
                        "pixel_row": r,
                        "pixel_col": c,
                        "lat": lat_val,
                        "lon": lon_val,
                        "soil_texture_id": stype,
                        "soil_texture_name": stype_name,
                        "basin": basin_name,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "dry_len_days": dry_len,
                        "season": season,
                        "n_obs_smap": n_smap,
                        "tau_smap": tau_smap,
                        "delta_theta_smap": dth_smap,
                        "theta_inf_smap": th_inf_smap,
                        "r2_smap": r2_smap,
                        "tau_opl": tau_opl,
                        "delta_theta_opl": dth_opl,
                        "theta_inf_opl": th_inf_opl,
                        "r2_opl": r2_opl,
                        "ratio_tau_opl_over_smap": ratio_opl
                    })
                i = k
            else:
                i += 1
        else:
            i += 1
    return results

def compute_quantiles(arr):
    v = arr[np.isfinite(arr)]
    if len(v) == 0:
        return np.nan, np.nan, np.nan
    return float(np.median(v)), float(np.percentile(v, 25)), float(np.percentile(v, 75))

def main():
    print("=" * 80)
    print("STEP A4: HYDRAULIQUE DU SOL, ASSÈCHEMENT, NAPPE (H2)")
    print("=" * 80)

    # ---------------------------------------------------------
    # 1. PARAMÈTRES STATIQUES ET MASQUES DE BASSINS
    # ---------------------------------------------------------
    print("\n>>> [1/7] Chargement des paramètres statiques et masques...")
    with nc.Dataset(LIS_INPUT) as ds:
        landmask = ds.variables["LANDMASK"][:].squeeze().astype(bool)
        texture_3d = ds.variables["TEXTURE"][:]
        soiltype = np.argmax(texture_3d, axis=0) + 1
        lat_grid = ds.variables["lat"][:]
        lon_grid = ds.variables["lon"][:]

    n_land = int(np.sum(landmask))
    print(f"  Pixels terrestres: {n_land}")

    # HyMAP catchments
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

    weights_181 = {}
    basin_grid = np.full((121, 181), "Autre", dtype=object)

    for name, cells in catchments.items():
        w = np.zeros((121, 180), dtype=float)
        tot = sum(area_180[r, c] for r, c in cells)
        for r, c in cells:
            w[r, c] = area_180[r, c] / tot
        w_pad = np.pad(w, ((0, 0), (0, 1)), mode='constant', constant_values=0.0)
        weights_181[name] = w_pad
        for r, c in cells:
            basin_grid[r, c] = name

    print("  Bassins HyMAP délimités avec succès.")

    # ---------------------------------------------------------
    # 2. PARAMÈTRES DU SOL RÉELLEMENT LUS PAR LE RUN (SOILPARM.TBL)
    # ---------------------------------------------------------
    print("\n>>> [2/7] Lecture de SOILPARM.TBL (STAS) et calcul des seuils SMAP...")
    soil_params = {}
    with open(SOILPARM_PATH, "r") as f:
        in_stas = False
        for line in f:
            if "STAS" in line and not "STAS-RUC" in line:
                in_stas = True
                continue
            if "STAS-RUC" in line:
                break
            if in_stas and line.strip() and line.strip()[0].isdigit():
                parts = [p.strip().strip("'") for p in line.split(",") if p.strip()]
                if len(parts) == 12:
                    tid = int(parts[0])
                    soil_params[tid] = {
                        "texture_id": tid,
                        "texture_name": parts[11],
                        "BEXP": float(parts[1]),
                        "SMCMAX": float(parts[4]),
                        "SMCREF": float(parts[5]),
                        "SMCWLT": float(parts[9]),
                        "DKSAT": float(parts[7]),
                        "PSISAT": float(parts[6]),
                    }

    # Load SMAP uncensored 2018
    print(f"  Chargement du cache SMAP non censuré depuis {CACHE_FILE_UNCENSORED}...")
    cache_data = np.load(CACHE_FILE_UNCENSORED)
    smap_uncens_daily = cache_data["smap_uncensored_daily"] # (1827, 121, 181)
    dates_str_all = cache_data["dates_str"]
    idx_2018 = [i for i, d in enumerate(dates_str_all) if d.startswith("2018")]
    smap_2018 = smap_uncens_daily[idx_2018] # (365, 121, 181)

    soil_thresh_rows = []
    for tid in range(1, 13):
        p = soil_params[tid]
        tmask = landmask & (soiltype == tid)
        n_pix = int(np.sum(tmask))
        if n_pix == 0:
            soil_thresh_rows.append({
                "texture_id": tid,
                "texture_name": p["texture_name"],
                "BEXP": p["BEXP"],
                "SMCMAX": p["SMCMAX"],
                "SMCREF": p["SMCREF"],
                "SMCWLT": p["SMCWLT"],
                "DKSAT": p["DKSAT"],
                "PSISAT": p["PSISAT"],
                "domain_pixel_count": 0,
                "domain_pixel_fraction_pct": 0.0,
                "smap_retrievals_total_2018": "absent",
                "smap_fraction_below_smcwlt_pct": "absent",
                "smap_fraction_below_smcwlt_plus_002_pct": "absent",
                "smap_fraction_above_smcmax_pct": "absent",
                "evidence": "data/land_params/noahmp401_parms/SOILPARM.TBL:STAS"
            })
            continue

        obs_t = smap_2018[:, tmask]
        obs_v = obs_t[np.isfinite(obs_t)]
        n_tot = len(obs_v)
        f_wlt = round(float((obs_v < p["SMCWLT"]).sum() / n_tot * 100.0), 2) if n_tot > 0 else 0.0
        f_wlt_plus = round(float((obs_v < (p["SMCWLT"] + 0.02)).sum() / n_tot * 100.0), 2) if n_tot > 0 else 0.0
        f_max = round(float((obs_v > p["SMCMAX"]).sum() / n_tot * 100.0), 2) if n_tot > 0 else 0.0

        soil_thresh_rows.append({
            "texture_id": tid,
            "texture_name": p["texture_name"],
            "BEXP": p["BEXP"],
            "SMCMAX": p["SMCMAX"],
            "SMCREF": p["SMCREF"],
            "SMCWLT": p["SMCWLT"],
            "DKSAT": p["DKSAT"],
            "PSISAT": p["PSISAT"],
            "domain_pixel_count": n_pix,
            "domain_pixel_fraction_pct": round(n_pix / n_land * 100.0, 2),
            "smap_retrievals_total_2018": n_tot,
            "smap_fraction_below_smcwlt_pct": f_wlt,
            "smap_fraction_below_smcwlt_plus_002_pct": f_wlt_plus,
            "smap_fraction_above_smcmax_pct": f_max,
            "evidence": "data/land_params/noahmp401_parms/SOILPARM.TBL:STAS"
        })

    df_soil_thresh = pd.DataFrame(soil_thresh_rows)
    out_soil_thresh = os.path.join(TABLES_DIR, "A4_soil_parameters_and_smap_thresholds.csv")
    df_soil_thresh.to_csv(out_soil_thresh, index=False)
    print(f"  [OK] Table {out_soil_thresh} sauvegardée ({len(df_soil_thresh)} lignes).")

    # ---------------------------------------------------------
    # 3. EXTRACTION DES SORTIES MODÈLE 2018
    # ---------------------------------------------------------
    print("\n>>> [3/7] Extraction des sorties journalières modèle 2018...")
    def get_run_files(exp_path):
        f_2018 = sorted(glob.glob(os.path.join(exp_path, "2018*/LIS_HIST_*.d01.nc")))
        f_2019 = sorted(glob.glob(os.path.join(exp_path, "201901/LIS_HIST_201901010000.d01.nc")))
        return f_2018 + f_2019

    files_ens = get_run_files(EXP_ENS_CORR)
    files_ol = get_run_files(EXP_OL_DAIC)
    files_da = get_run_files(EXP_DA_CORR)

    print(f"  ENS_corr: {len(files_ens)} fichiers")
    print(f"  OL_DAIC:  {len(files_ol)} fichiers")
    print(f"  DA_corr:  {len(files_da)} fichiers")

    sim_dates = [datetime.date(2018, 1, 1) + datetime.timedelta(days=d) for d in range(365)]

    p_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    sm1_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    sm4_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    gws_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    wtd_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    qsb_ens_2018 = np.zeros((365, 121, 181), dtype=np.float32)

    sm1_ol_2018 = np.zeros((365, 121, 181), dtype=np.float32)

    sm4_da_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    gws_da_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    wtd_da_2018 = np.zeros((365, 121, 181), dtype=np.float32)
    qsb_da_2018 = np.zeros((365, 121, 181), dtype=np.float32)

    t0 = time.time()
    for d_idx, (f_ens, f_ol, f_da) in enumerate(zip(files_ens, files_ol, files_da)):
        with nc.Dataset(f_ens) as ds:
            p_ens_2018[d_idx] = ds["TotalPrecip_tavg"][:] * 86400.0 # kg/m2/s -> mm/day
            sm1_ens_2018[d_idx] = ds["SoilMoist_tavg"][0]
            sm4_ens_2018[d_idx] = ds["SoilMoist_tavg"][3]
            gws_ens_2018[d_idx] = ds["GWS_tavg"][:]
            wtd_ens_2018[d_idx] = ds["WaterTableD_tavg"][:]
            qsb_ens_2018[d_idx] = ds["Qsb_tavg"][:] * 86400.0 # kg/m2/s -> mm/day

        with nc.Dataset(f_ol) as ds:
            sm1_ol_2018[d_idx] = ds["SoilMoist_tavg"][0]

        with nc.Dataset(f_da) as ds:
            sm4_da_2018[d_idx] = ds["SoilMoist_tavg"][3]
            gws_da_2018[d_idx] = ds["GWS_tavg"][:]
            wtd_da_2018[d_idx] = ds["WaterTableD_tavg"][:]
            qsb_da_2018[d_idx] = ds["Qsb_tavg"][:] * 86400.0

    print(f"  Extraction 2018 terminée en {time.time() - t0:.1f} s.")

    # ---------------------------------------------------------
    # 4. BILAN MENSUEL DE LA NAPPE 2018 (LALLA CHAFIA & SIDI JABEUR)
    # ---------------------------------------------------------
    print("\n>>> [4/7] Calcul de la dynamique de nappe mensuelle 2018...")
    months_2018 = [f"2018-{m:02d}" for m in range(1, 13)]
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    month_slices = []
    curr = 0
    for dim in days_in_month:
        month_slices.append(slice(curr, curr + dim))
        curr += dim

    gw_rows = []
    stations_gw = ["Lalla Chafia", "Sidi Jabeur"]
    runs_gw = [
        ("ENS_corr", sm4_ens_2018, gws_ens_2018, wtd_ens_2018, qsb_ens_2018, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL"),
        ("DA_corr", sm4_da_2018, gws_da_2018, wtd_da_2018, qsb_da_2018, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL")
    ]

    for st_name in stations_gw:
        w_st = weights_181[st_name]
        for run_name, sm4_arr, gws_arr, wtd_arr, qsb_arr, ev_path in runs_gw:
            for m_idx, (ym, sl, dim) in enumerate(zip(months_2018, month_slices, days_in_month)):
                gws_m = float(np.sum(np.mean(gws_arr[sl], axis=0) * w_st))
                wtd_m = float(np.sum(np.mean(wtd_arr[sl], axis=0) * w_st))
                sm4_m = float(np.sum(np.mean(sm4_arr[sl], axis=0) * w_st))
                qsb_m = float(np.sum(np.sum(qsb_arr[sl], axis=0) * w_st))
                rech_m = "absent"

                gw_rows.append({
                    "station": st_name,
                    "experiment": run_name,
                    "year_month": ym,
                    "GWS_mm": round(gws_m, 2),
                    "WaterTableD_m": round(wtd_m, 3),
                    "SoilMoist_layer4_m3m3": round(sm4_m, 4),
                    "Qsb_mm_month": round(qsb_m, 2),
                    "recharge": rech_m,
                    "evidence": f"{ev_path}/{ym.replace('-', '')}/LIS_HIST_*.d01.nc"
                })

    df_gw = pd.DataFrame(gw_rows)
    out_gw = os.path.join(TABLES_DIR, "A4_groundwater_monthly_2018.csv")
    df_gw.to_csv(out_gw, index=False)
    print(f"  [OK] Table {out_gw} sauvegardée ({len(df_gw)} lignes).")

    # Code diff SIMGM table
    diff_rows = [
        {
            "model_component": "Noah-MP 4.0.1 / SIMGM",
            "file": "src/lisf/lis/surfacemodels/land/noahmp.4.0.1/phys/module_sf_noahmplsm_401.F90",
            "lines": "6584-6590",
            "code_statement": "IF(OPT_RUN == 1) CALL GROUNDWATER (...) RUNSUB = QDIS",
            "physical_meaning": "Activation schéma SIMGM nappe et drainage de baseflow"
        },
        {
            "model_component": "Noah-MP 4.0.1 / SIMGM",
            "file": "src/lisf/lis/surfacemodels/land/noahmp.4.0.1/phys/module_sf_noahmplsm_401.F90",
            "lines": "8448-8454",
            "code_statement": "QIN = - KA * (WH_ZWT-WH) / ((ZWT-ZNODE(IWT))*1.E3)",
            "physical_meaning": "Flux de recharge Darcy entre le bas du sol et la nappe phréatique"
        },
        {
            "model_component": "Noah-MP 4.0.1 / SIMGM",
            "file": "src/lisf/lis/surfacemodels/land/noahmp.4.0.1/phys/module_sf_noahmplsm_401.F90",
            "lines": "8458",
            "code_statement": "IF(IWT.EQ.NSOIL) WA = WA + (QIN - QDIS) * DT",
            "physical_meaning": "Stock aquifère WA alimenté par QIN lorsque la nappe est sous la couche 4"
        },
        {
            "model_component": "Noah-MP 4.0.1 / SIMGM",
            "file": "src/lisf/lis/surfacemodels/land/noahmp.4.0.1/phys/module_sf_noahmplsm_401.F90",
            "lines": "8460",
            "code_statement": "MLIQ(NSOIL) = MLIQ(NSOIL) - QIN * DT",
            "physical_meaning": "L'eau entrant dans la nappe (QIN) est prélevée directement dans la couche 4"
        },
        {
            "model_component": "Noah-MP 4.0.1 / SIMGM",
            "file": "src/lisf/lis/surfacemodels/land/noahmp.4.0.1/phys/module_sf_noahmplsm_401.F90",
            "lines": "8506-8515",
            "code_statement": "MLIQ(IZ) = MLIQ(IZ) + XS; WA = WA - XS; WT = WT - XS",
            "physical_meaning": "Remontée capillaire / rééquilibrage de déficit puisé dans la nappe WA"
        }
    ]
    df_diff = pd.DataFrame(diff_rows)
    out_diff = os.path.join(TABLES_DIR, "A4_groundwater_code_diff.csv")
    df_diff.to_csv(out_diff, index=False)
    print(f"  [OK] Table {out_diff} sauvegardée.")

    # ---------------------------------------------------------
    # 5. AJUSTEMENT EXPONENTIEL DU DRYDOWN 2018 (SMAP, ENS_corr, OL_DAIC)
    # ---------------------------------------------------------
    print("\n>>> [5/7] Ajustement exponentiel du drydown 2018...")
    pixel_args_2018 = []
    for r in range(121):
        for c in range(181):
            if not landmask[r, c]:
                continue
            st = int(soiltype[r, c])
            st_name = USDA_TEXTURE_NAMES.get(st, f"Texture_{st}")
            b_name = basin_grid[r, c]
            lat_v = float(lat_grid[r, c])
            lon_v = float(lon_grid[r, c])

            p_s = p_ens_2018[:, r, c]
            smap_s = smap_2018[:, r, c]
            ens_s = sm1_ens_2018[:, r, c]
            ol_s = sm1_ol_2018[:, r, c]

            pixel_args_2018.append((
                r, c, p_s, smap_s, ens_s, ol_s, st, st_name, b_name, lat_v, lon_v, sim_dates
            ))

    t0 = time.time()
    n_workers = min(16, max(1, mp.cpu_count() - 2))
    print(f"  Lancement du traitement parallèle 2018 sur {n_workers} cœurs ({len(pixel_args_2018)} pixels)...")
    with mp.Pool(n_workers) as pool:
        res_nested = pool.map(process_pixel_episodes_2018, pixel_args_2018)

    all_episodes_2018 = [ep for sub in res_nested for ep in sub]
    print(f"  {len(all_episodes_2018)} épisodes identifiés en {time.time() - t0:.1f} s.")

    df_ep_2018 = pd.DataFrame(all_episodes_2018)
    float_cols = [c for c in df_ep_2018.columns if df_ep_2018[c].dtype == "float64"]
    df_ep_2018[float_cols] = df_ep_2018[float_cols].round(4)
    out_ep_2018 = os.path.join(TABLES_DIR, "A4_drydown_episodes_2018.csv")
    df_ep_2018.to_csv(out_ep_2018, index=False)
    print(f"  [OK] Table {out_ep_2018} sauvegardée.")

    # Agrégations 2018
    agg_rows_2018 = []

    def compute_agg_metrics(df_sub, agg_type, cat_name):
        n_tot_ep = len(df_sub)
        sub_smap = df_sub[df_sub["r2_smap"] >= 0.7]
        n_smap = len(sub_smap)
        t_smap_med, t_smap_q25, t_smap_q75 = compute_quantiles(sub_smap["tau_smap"].values)
        d_smap_med, d_smap_q25, d_smap_q75 = compute_quantiles(sub_smap["delta_theta_smap"].values)

        sub_ens = df_sub[df_sub["r2_ens_corr"] >= 0.7]
        n_ens = len(sub_ens)
        t_ens_med, t_ens_q25, t_ens_q75 = compute_quantiles(sub_ens["tau_ens_corr"].values)
        d_ens_med, d_ens_q25, d_ens_q75 = compute_quantiles(sub_ens["delta_theta_ens_corr"].values)

        sub_ol = df_sub[df_sub["r2_ol_daic"] >= 0.7]
        n_ol = len(sub_ol)
        t_ol_med, t_ol_q25, t_ol_q75 = compute_quantiles(sub_ol["tau_ol_daic"].values)
        d_ol_med, d_ol_q25, d_ol_q75 = compute_quantiles(sub_ol["delta_theta_ol_daic"].values)

        sub_paired_ens = df_sub[(df_sub["r2_smap"] >= 0.7) & (df_sub["r2_ens_corr"] >= 0.7)]
        n_paired_ens = len(sub_paired_ens)
        r_ens_med, r_ens_q25, r_ens_q75 = compute_quantiles(sub_paired_ens["ratio_tau_ens_over_smap"].values)

        sub_paired_ol = df_sub[(df_sub["r2_smap"] >= 0.7) & (df_sub["r2_ol_daic"] >= 0.7)]
        n_paired_ol = len(sub_paired_ol)
        r_ol_med, r_ol_q25, r_ol_q75 = compute_quantiles(sub_paired_ol["ratio_tau_ol_over_smap"].values)

        return {
            "aggregation_type": agg_type,
            "category": cat_name,
            "n_episodes_evaluated": n_tot_ep,
            "n_episodes_smap_r2_07": n_smap,
            "tau_smap_median": round(t_smap_med, 2) if np.isfinite(t_smap_med) else "absent",
            "tau_smap_q25": round(t_smap_q25, 2) if np.isfinite(t_smap_q25) else "absent",
            "tau_smap_q75": round(t_smap_q75, 2) if np.isfinite(t_smap_q75) else "absent",
            "delta_theta_smap_median": round(d_smap_med, 4) if np.isfinite(d_smap_med) else "absent",
            "delta_theta_smap_q25": round(d_smap_q25, 4) if np.isfinite(d_smap_q25) else "absent",
            "delta_theta_smap_q75": round(d_smap_q75, 4) if np.isfinite(d_smap_q75) else "absent",
            "n_episodes_ens_corr_r2_07": n_ens,
            "tau_ens_corr_median": round(t_ens_med, 2) if np.isfinite(t_ens_med) else "absent",
            "tau_ens_corr_q25": round(t_ens_q25, 2) if np.isfinite(t_ens_q25) else "absent",
            "tau_ens_corr_q75": round(t_ens_q75, 2) if np.isfinite(t_ens_q75) else "absent",
            "delta_theta_ens_corr_median": round(d_ens_med, 4) if np.isfinite(d_ens_med) else "absent",
            "delta_theta_ens_corr_q25": round(d_ens_q25, 4) if np.isfinite(d_ens_q25) else "absent",
            "delta_theta_ens_corr_q75": round(d_ens_q75, 4) if np.isfinite(d_ens_q75) else "absent",
            "n_episodes_ol_daic_r2_07": n_ol,
            "tau_ol_daic_median": round(t_ol_med, 2) if np.isfinite(t_ol_med) else "absent",
            "tau_ol_daic_q25": round(t_ol_q25, 2) if np.isfinite(t_ol_q25) else "absent",
            "tau_ol_daic_q75": round(t_ol_q75, 2) if np.isfinite(t_ol_q75) else "absent",
            "delta_theta_ol_daic_median": round(d_ol_med, 4) if np.isfinite(d_ol_med) else "absent",
            "delta_theta_ol_daic_q25": round(d_ol_q25, 4) if np.isfinite(d_ol_q25) else "absent",
            "delta_theta_ol_daic_q75": round(d_ol_q75, 4) if np.isfinite(d_ol_q75) else "absent",
            "n_paired_ens_smap": n_paired_ens,
            "ratio_tau_ens_over_smap_median": round(r_ens_med, 2) if np.isfinite(r_ens_med) else "absent",
            "ratio_tau_ens_over_smap_q25": round(r_ens_q25, 2) if np.isfinite(r_ens_q25) else "absent",
            "ratio_tau_ens_over_smap_q75": round(r_ens_q75, 2) if np.isfinite(r_ens_q75) else "absent",
            "n_paired_ol_smap": n_paired_ol,
            "ratio_tau_ol_over_smap_median": round(r_ol_med, 2) if np.isfinite(r_ol_med) else "absent",
            "ratio_tau_ol_over_smap_q25": round(r_ol_q25, 2) if np.isfinite(r_ol_q25) else "absent",
            "ratio_tau_ol_over_smap_q75": round(r_ol_q75, 2) if np.isfinite(r_ol_q75) else "absent"
        }

    agg_rows_2018.append(compute_agg_metrics(df_ep_2018, "Domaine", "Domaine complet"))
    for tid in sorted(df_ep_2018["soil_texture_id"].unique()):
        sub_t = df_ep_2018[df_ep_2018["soil_texture_id"] == tid]
        tname = USDA_TEXTURE_NAMES.get(tid, f"Texture_{tid}")
        agg_rows_2018.append(compute_agg_metrics(sub_t, "Texture de sol", f"{tid} - {tname}"))
    for s_name in ["DJF", "MAM", "JJA", "SON"]:
        sub_s = df_ep_2018[df_ep_2018["season"] == s_name]
        agg_rows_2018.append(compute_agg_metrics(sub_s, "Saison", s_name))
    for b_name in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
        sub_b = df_ep_2018[df_ep_2018["basin"] == b_name]
        agg_rows_2018.append(compute_agg_metrics(sub_b, "Bassin versant", b_name))

    df_agg_2018 = pd.DataFrame(agg_rows_2018)
    out_agg_2018 = os.path.join(TABLES_DIR, "A4_drydown_aggregated_metrics_2018.csv")
    df_agg_2018.to_csv(out_agg_2018, index=False)
    print(f"  [OK] Table {out_agg_2018} sauvegardée ({len(df_agg_2018)} catégories).")

    # ---------------------------------------------------------
    # 6. PRODUCTION 2016–2020 (OPL vs SMAP NON CENSURÉ)
    # ---------------------------------------------------------
    print("\n>>> [6/7] Traitement du drydown sur la production multi-annuelle 2016–2020...")
    precip_all = cache_data["precip_daily"] # (1827, 121, 181)
    ol_all = cache_data["ol_daily"] # (1827, 121, 181)
    dates_list_all = [datetime.datetime.strptime(d[:10], "%Y-%m-%d").date() for d in dates_str_all]

    pixel_args_prod = []
    for r in range(121):
        for c in range(181):
            if not landmask[r, c]:
                continue
            st = int(soiltype[r, c])
            st_name = USDA_TEXTURE_NAMES.get(st, f"Texture_{st}")
            b_name = basin_grid[r, c]
            lat_v = float(lat_grid[r, c])
            lon_v = float(lon_grid[r, c])

            p_s = precip_all[:, r, c]
            smap_s = smap_uncens_daily[:, r, c]
            opl_s = ol_all[:, r, c]

            pixel_args_prod.append((
                r, c, p_s, smap_s, opl_s, st, st_name, b_name, lat_v, lon_v, dates_list_all
            ))

    t0 = time.time()
    print(f"  Lancement du traitement parallèle 2016–2020 sur {n_workers} cœurs...")
    with mp.Pool(n_workers) as pool:
        res_nested_prod = pool.map(process_pixel_episodes_2016_2020, pixel_args_prod)

    all_episodes_prod = [ep for sub in res_nested_prod for ep in sub]
    print(f"  {len(all_episodes_prod)} épisodes identifiés pour 2016–2020 en {time.time() - t0:.1f} s.")

    df_ep_prod = pd.DataFrame(all_episodes_prod)

    agg_rows_prod = []
    def compute_agg_metrics_prod(df_sub, agg_type, cat_name):
        n_tot_ep = len(df_sub)
        sub_smap = df_sub[df_sub["r2_smap"] >= 0.7]
        n_smap = len(sub_smap)
        t_smap_med, t_smap_q25, t_smap_q75 = compute_quantiles(sub_smap["tau_smap"].values)
        d_smap_med, d_smap_q25, d_smap_q75 = compute_quantiles(sub_smap["delta_theta_smap"].values)

        sub_opl = df_sub[df_sub["r2_opl"] >= 0.7]
        n_opl = len(sub_opl)
        t_opl_med, t_opl_q25, t_opl_q75 = compute_quantiles(sub_opl["tau_opl"].values)
        d_opl_med, d_opl_q25, d_opl_q75 = compute_quantiles(sub_opl["delta_theta_opl"].values)

        sub_paired = df_sub[(df_sub["r2_smap"] >= 0.7) & (df_sub["r2_opl"] >= 0.7)]
        n_paired = len(sub_paired)
        r_opl_med, r_opl_q25, r_opl_q75 = compute_quantiles(sub_paired["ratio_tau_opl_over_smap"].values)

        return {
            "aggregation_type": agg_type,
            "category": cat_name,
            "n_episodes_evaluated": n_tot_ep,
            "n_episodes_smap_r2_07": n_smap,
            "tau_smap_median": round(t_smap_med, 2) if np.isfinite(t_smap_med) else "absent",
            "tau_smap_q25": round(t_smap_q25, 2) if np.isfinite(t_smap_q25) else "absent",
            "tau_smap_q75": round(t_smap_q75, 2) if np.isfinite(t_smap_q75) else "absent",
            "delta_theta_smap_median": round(d_smap_med, 4) if np.isfinite(d_smap_med) else "absent",
            "delta_theta_smap_q25": round(d_smap_q25, 4) if np.isfinite(d_smap_q25) else "absent",
            "delta_theta_smap_q75": round(d_smap_q75, 4) if np.isfinite(d_smap_q75) else "absent",
            "n_episodes_opl_r2_07": n_opl,
            "tau_opl_median": round(t_opl_med, 2) if np.isfinite(t_opl_med) else "absent",
            "tau_opl_q25": round(t_opl_q25, 2) if np.isfinite(t_opl_q25) else "absent",
            "tau_opl_q75": round(t_opl_q75, 2) if np.isfinite(t_opl_q75) else "absent",
            "delta_theta_opl_median": round(d_opl_med, 4) if np.isfinite(d_opl_med) else "absent",
            "delta_theta_opl_q25": round(d_opl_q25, 4) if np.isfinite(d_opl_q25) else "absent",
            "delta_theta_opl_q75": round(d_opl_q75, 4) if np.isfinite(d_opl_q75) else "absent",
            "n_paired_opl_smap": n_paired,
            "ratio_tau_opl_over_smap_median": round(r_opl_med, 2) if np.isfinite(r_opl_med) else "absent",
            "ratio_tau_opl_over_smap_q25": round(r_opl_q25, 2) if np.isfinite(r_opl_q25) else "absent",
            "ratio_tau_opl_over_smap_q75": round(r_opl_q75, 2) if np.isfinite(r_opl_q75) else "absent"
        }

    agg_rows_prod.append(compute_agg_metrics_prod(df_ep_prod, "Domaine", "Domaine complet"))
    for tid in sorted(df_ep_prod["soil_texture_id"].unique()):
        sub_t = df_ep_prod[df_ep_prod["soil_texture_id"] == tid]
        tname = USDA_TEXTURE_NAMES.get(tid, f"Texture_{tid}")
        agg_rows_prod.append(compute_agg_metrics_prod(sub_t, "Texture de sol", f"{tid} - {tname}"))
    for s_name in ["DJF", "MAM", "JJA", "SON"]:
        sub_s = df_ep_prod[df_ep_prod["season"] == s_name]
        agg_rows_prod.append(compute_agg_metrics_prod(sub_s, "Saison", s_name))
    for b_name in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
        sub_b = df_ep_prod[df_ep_prod["basin"] == b_name]
        agg_rows_prod.append(compute_agg_metrics_prod(sub_b, "Bassin versant", b_name))

    df_agg_prod = pd.DataFrame(agg_rows_prod)
    out_agg_prod = os.path.join(TABLES_DIR, "A4_drydown_aggregated_metrics_2016_2020.csv")
    df_agg_prod.to_csv(out_agg_prod, index=False)
    print(f"  [OK] Table {out_agg_prod} sauvegardée ({len(df_agg_prod)} catégories).")

    # ---------------------------------------------------------
    # 7. FIGURES SCIENTIFIQUES DEPUIS LES CSV
    # ---------------------------------------------------------
    print("\n>>> [7/7] Génération des figures scientifiques...")

    # Figure 1: SMAP vs Soil limits
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    sub_th = df_soil_thresh[df_soil_thresh["domain_pixel_count"] > 0].copy()
    x = np.arange(len(sub_th))
    width = 0.28
    rects1 = ax.bar(x - width, sub_th["smap_fraction_below_smcwlt_pct"], width, label="< SMCWLT", color="#d62728", alpha=0.85)
    rects2 = ax.bar(x, sub_th["smap_fraction_below_smcwlt_plus_002_pct"], width, label="< SMCWLT + 0.02 m³/m³ (Censure LIS)", color="#ff7f0e", alpha=0.85)
    rects3 = ax.bar(x + width, sub_th["smap_fraction_above_smcmax_pct"], width, label="> SMCMAX", color="#1f77b4", alpha=0.85)

    ax.set_ylabel("Fraction des observations SMAP 2018 (%)", fontsize=11, fontweight="bold")
    ax.set_title("Observations SMAP 2018 face aux limites physiques du sol de Noah-MP (SOILPARM.TBL)", fontsize=12, fontweight="bold", pad=12)
    ax.set_xticks(x)
    ax.set_xticklabels([f"{r.texture_id}\n{r.texture_name}" for _, r in sub_th.iterrows()], fontsize=9)
    ax.legend(frameon=True, fontsize=10)
    ax.grid(True, linestyle="--", alpha=0.5, axis="y")
    plt.tight_layout()
    fig1_path = os.path.join(FIGURES_DIR, "A4_smap_retrievals_vs_soil_limits.png")
    fig.savefig(fig1_path)
    plt.close(fig)
    print(f"  [OK] Figure {fig1_path} créée.")

    # Figure 2: Tau distributions by texture (2018)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5.5), dpi=300)
    df_t = df_agg_2018[df_agg_2018["aggregation_type"] == "Texture de sol"].copy()
    xt = np.arange(len(df_t))
    w = 0.25

    y_smap = df_t["tau_smap_median"].astype(float).values
    err_smap = [y_smap - df_t["tau_smap_q25"].astype(float).values, df_t["tau_smap_q75"].astype(float).values - y_smap]
    y_ens = df_t["tau_ens_corr_median"].astype(float).values
    err_ens = [y_ens - df_t["tau_ens_corr_q25"].astype(float).values, df_t["tau_ens_corr_q75"].astype(float).values - y_ens]
    y_ol = df_t["tau_ol_daic_median"].astype(float).values
    err_ol = [y_ol - df_t["tau_ol_daic_q25"].astype(float).values, df_t["tau_ol_daic_q75"].astype(float).values - y_ol]

    ax1.bar(xt - w, y_smap, w, yerr=err_smap, capsize=3, label="SMAP natif (R²≥0.7)", color="#2ca02c", alpha=0.85)
    ax1.bar(xt, y_ens, w, yerr=err_ens, capsize=3, label="ENS_corr (R²≥0.7)", color="#1f77b4", alpha=0.85)
    ax1.bar(xt + w, y_ol, w, yerr=err_ol, capsize=3, label="OL_DAIC (R²≥0.7)", color="#ff7f0e", alpha=0.85)
    ax1.set_ylabel("Constante de temps de séchage τ (jours) [Médiane et IQR]", fontsize=10, fontweight="bold")
    ax1.set_title("Dynamique de ressuyage τ par texture de sol (2018)", fontsize=11, fontweight="bold")
    ax1.set_xticks(xt)
    ax1.set_xticklabels([c.replace(" - ", "\n") for c in df_t["category"]], fontsize=8)
    ax1.legend(frameon=True, fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.4, axis="y")

    r_ens = df_t["ratio_tau_ens_over_smap_median"].astype(float).values
    r_ens_err = [r_ens - df_t["ratio_tau_ens_over_smap_q25"].astype(float).values, df_t["ratio_tau_ens_over_smap_q75"].astype(float).values - r_ens]
    r_ol = df_t["ratio_tau_ol_over_smap_median"].astype(float).values
    r_ol_err = [r_ol - df_t["ratio_tau_ol_over_smap_q25"].astype(float).values, df_t["ratio_tau_ol_over_smap_q75"].astype(float).values - r_ol]

    ax2.bar(xt - w/2, r_ens, w, yerr=r_ens_err, capsize=3, label="τ(ENS_corr) / τ(SMAP)", color="#1f77b4", alpha=0.85)
    ax2.bar(xt + w/2, r_ol, w, yerr=r_ol_err, capsize=3, label="τ(OL_DAIC) / τ(SMAP)", color="#ff7f0e", alpha=0.85)
    ax2.axhline(1.0, color="black", linestyle="--", linewidth=1.2, label="Parité modèle / SMAP (ratio=1)")
    ax2.set_ylabel("Rapport τ_modèle / τ_SMAP [Médiane et IQR]", fontsize=10, fontweight="bold")
    ax2.set_title("Rapport de vitesse d'assèchement (modèle vs satellite)", fontsize=11, fontweight="bold")
    ax2.set_xticks(xt)
    ax2.set_xticklabels([c.replace(" - ", "\n") for c in df_t["category"]], fontsize=8)
    ax2.legend(frameon=True, fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.4, axis="y")

    plt.tight_layout()
    fig2_path = os.path.join(FIGURES_DIR, "A4_drydown_tau_distribution_by_texture.png")
    fig.savefig(fig2_path)
    plt.close(fig)
    print(f"  [OK] Figure {fig2_path} créée.")

    # Figure 3: Drydown across seasons and basins
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    df_s = df_agg_2018[df_agg_2018["aggregation_type"] == "Saison"].copy()
    xs = np.arange(len(df_s))
    ax1.bar(xs - w/2, df_s["ratio_tau_ens_over_smap_median"].astype(float), w, label="τ(ENS_corr) / τ(SMAP)", color="#1f77b4", alpha=0.85)
    ax1.bar(xs + w/2, df_s["ratio_tau_ol_over_smap_median"].astype(float), w, label="τ(OL_DAIC) / τ(SMAP)", color="#ff7f0e", alpha=0.85)
    ax1.axhline(1.0, color="black", linestyle="--", linewidth=1.2)
    ax1.set_ylabel("Rapport médian τ_modèle / τ_SMAP", fontsize=10, fontweight="bold")
    ax1.set_title("Rapport τ_modèle / τ_SMAP par saison (2018)", fontsize=11, fontweight="bold")
    ax1.set_xticks(xs)
    ax1.set_xticklabels(df_s["category"], fontsize=10)
    ax1.legend(frameon=True, fontsize=9)
    ax1.grid(True, linestyle="--", alpha=0.4, axis="y")

    df_b = df_agg_2018[df_agg_2018["aggregation_type"].isin(["Domaine", "Bassin versant"])].copy()
    xb = np.arange(len(df_b))
    ax2.bar(xb - w/2, df_b["ratio_tau_ens_over_smap_median"].astype(float), w, label="τ(ENS_corr) / τ(SMAP)", color="#1f77b4", alpha=0.85)
    ax2.bar(xb + w/2, df_b["ratio_tau_ol_over_smap_median"].astype(float), w, label="τ(OL_DAIC) / τ(SMAP)", color="#ff7f0e", alpha=0.85)
    ax2.axhline(1.0, color="black", linestyle="--", linewidth=1.2)
    ax2.set_ylabel("Rapport médian τ_modèle / τ_SMAP", fontsize=10, fontweight="bold")
    ax2.set_title("Rapport τ_modèle / τ_SMAP par région / bassin (2018)", fontsize=11, fontweight="bold")
    ax2.set_xticks(xb)
    ax2.set_xticklabels(df_b["category"], fontsize=9)
    ax2.legend(frameon=True, fontsize=9)
    ax2.grid(True, linestyle="--", alpha=0.4, axis="y")

    plt.tight_layout()
    fig3_path = os.path.join(FIGURES_DIR, "A4_drydown_tau_seasonal_and_basins.png")
    fig.savefig(fig3_path)
    plt.close(fig)
    print(f"  [OK] Figure {fig3_path} créée.")

    # Figure 4: Groundwater dynamics 2018
    fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=300, sharex=True)
    m_labels = [f"{m:02d}" for m in range(1, 13)]

    for row_idx, st_name in enumerate(["Lalla Chafia", "Sidi Jabeur"]):
        df_st_ens = df_gw[(df_gw["station"] == st_name) & (df_gw["experiment"] == "ENS_corr")]
        df_st_da = df_gw[(df_gw["station"] == st_name) & (df_gw["experiment"] == "DA_corr")]

        # GWS & WaterTableD
        ax_gws = axes[row_idx, 0]
        ax_wtd = ax_gws.twinx()
        l1 = ax_gws.plot(m_labels, df_st_ens["GWS_mm"], color="#1f77b4", marker="o", label="GWS ENS_corr (mm)")
        l2 = ax_gws.plot(m_labels, df_st_da["GWS_mm"], color="#1f77b4", linestyle="--", marker="s", label="GWS DA_corr (mm)")
        l3 = ax_wtd.plot(m_labels, df_st_ens["WaterTableD_m"], color="#d62728", marker="^", label="WTD ENS_corr (m)")
        l4 = ax_wtd.plot(m_labels, df_st_da["WaterTableD_m"], color="#d62728", linestyle="--", marker="v", label="WTD DA_corr (m)")
        ax_gws.set_ylabel("GWS (mm)", color="#1f77b4", fontsize=10, fontweight="bold")
        ax_wtd.set_ylabel("Profondeur nappe (m)", color="#d62728", fontsize=10, fontweight="bold")
        ax_gws.set_title(f"{st_name} — Nappe phréatique (GWS et WTD, 2018)", fontsize=11, fontweight="bold")
        lines = l1 + l2 + l3 + l4
        labels = [l.get_label() for l in lines]
        ax_gws.legend(lines, labels, loc="upper left", fontsize=8, frameon=True)
        ax_gws.grid(True, linestyle="--", alpha=0.4)

        # SoilMoist Layer 4 & Qsb
        ax_sm4 = axes[row_idx, 1]
        ax_qsb = ax_sm4.twinx()
        l5 = ax_sm4.plot(m_labels, df_st_ens["SoilMoist_layer4_m3m3"], color="#2ca02c", marker="o", label="θ_couche4 ENS_corr (m³/m³)")
        l6 = ax_sm4.plot(m_labels, df_st_da["SoilMoist_layer4_m3m3"], color="#2ca02c", linestyle="--", marker="s", label="θ_couche4 DA_corr (m³/m³)")
        l7 = ax_qsb.plot(m_labels, df_st_ens["Qsb_mm_month"], color="#9467bd", marker="^", label="Qsb ENS_corr (mm/mois)")
        l8 = ax_qsb.plot(m_labels, df_st_da["Qsb_mm_month"], color="#9467bd", linestyle="--", marker="v", label="Qsb DA_corr (mm/mois)")
        ax_sm4.set_ylabel("θ couche 4 (m³/m³)", color="#2ca02c", fontsize=10, fontweight="bold")
        ax_qsb.set_ylabel("Qsb (mm/mois)", color="#9467bd", fontsize=10, fontweight="bold")
        ax_sm4.set_title(f"{st_name} — Humidité couche 4 et écoulement souterrain Qsb (2018)", fontsize=11, fontweight="bold")
        lines_b = l5 + l6 + l7 + l8
        labels_b = [l.get_label() for l in lines_b]
        ax_sm4.legend(lines_b, labels_b, loc="upper left", fontsize=8, frameon=True)
        ax_sm4.grid(True, linestyle="--", alpha=0.4)

    axes[1, 0].set_xlabel("Mois (2018)", fontsize=10, fontweight="bold")
    axes[1, 1].set_xlabel("Mois (2018)", fontsize=10, fontweight="bold")

    plt.tight_layout()
    fig4_path = os.path.join(FIGURES_DIR, "A4_groundwater_dynamics_2018.png")
    fig.savefig(fig4_path)
    plt.close(fig)
    print(f"  [OK] Figure {fig4_path} créée.")

    # ---------------------------------------------------------
    # 8. GÉNÉRATION DU RAPPORT MARKDOWN (TABLEAUX SEULEMENT)
    # ---------------------------------------------------------
    print("\n>>> [8/8] Génération de REPORT_A4.md (tableaux uniquement)...")

    md_lines = [
        "# REPORT_A4 — Hydraulique du sol, assèchement et nappe (H2)\n\n",
        "## Table 1 : Paramètres du sol utilisés et distribution des observations SMAP 2018 face aux limites physiques\n\n",
        df_soil_thresh.to_markdown(index=False),
        "\n\n## Table 2 : Assèchement après la pluie (2018) — Métriques agrégées (Texture, Saison, Bassin)\n\n",
        df_agg_2018.to_markdown(index=False),
        "\n\n## Table 3 : Assèchement après la pluie (Production 2016–2020) — Métriques agrégées (OPL vs SMAP)\n\n",
        df_agg_prod.to_markdown(index=False),
        "\n\n## Table 4 : Dynamique mensuelle de la nappe (2018) — Lalla Chafia et Sidi Jabeur (ENS_corr et DA_corr)\n\n",
        df_gw.to_markdown(index=False),
        "\n\n## Table 5 : Traçabilité du code source — Source de l'eau entrant dans la nappe phréatique (Noah-MP 4.0.1 / SIMGM)\n\n",
        df_diff.to_markdown(index=False),
        "\n"
    ]

    report_content = "".join(md_lines)
    for rpath in [REPORT_FILE_1, REPORT_FILE_2]:
        with open(rpath, "w") as f:
            f.write(report_content)
        print(f"  [OK] Rapport {rpath} écrit.")

    print("\n" + "=" * 80)
    print("STEP A4 TERMINÉ AVEC SUCCÈS")
    print("=" * 80)

if __name__ == "__main__":
    main()
