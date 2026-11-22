#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3_et_evaluation_corrected_2018.py
Évaluation de l'évapotranspiration (ET) 2018 contre WaPOR v3 (référence principale)
et GLEAM v4.3a (secondaire) pour la Partie A3.

Inclut :
  - OPL, OL_DAIC, ENS_OPL, ENS_corr, DA_nocdf, DA_cdf, DA_nocdf_nowilt, DA_corr
  - Stratifications : Domaine, Sebou, Bouregreg, Texture, Saisons (Annual, MAM, JJA)
  - Direction de changement (delta |biais| et fraction des mailles qui se rapprochent)
    pour les 5 différences propres de A1.

Sorties :
  - paper1/tables/et_evaluation_corrected_2018.csv
  - paper1/tables/et_direction_of_change_corrected_2018.csv
"""

import os
import glob
import re
import time
import numpy as np
import pandas as pd
import netCDF4 as nc
import tifffile
from scipy import stats
from multiprocessing import Pool

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Grilles, Masques et Stratifications
# -------------------------------------------------------------
print(">>> Chargement des masques géographiques et texturaux...")
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = ds_in.variables["LANDMASK"][:] == 1.0  # (121, 181)
    texture_181 = ds_in.variables["TEXTURE"][:]          # (16, 121, 181)
    dom_texture_181 = np.argmax(texture_181, axis=0) + 1  # 1 to 16
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

# Bassins Sebou et Bouregreg depuis lis_input_corrigee.d01.nc
hymap_input_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
with nc.Dataset(hymap_input_path) as ds_hm:
    hymap_basin = ds_hm.variables["HYMAP_basin"][:]  # (120, 180)
    lat_180 = ds_hm.variables["lat"][:, 0]
    lon_180 = ds_hm.variables["lon"][0, :]

basin_181 = np.full((121, 181), -9999.0, dtype=np.float32)
for j in range(121):
    j_180 = np.clip(int(np.round((lat_181[j] - lat_180[0]) / 0.05)), 0, 119)
    for i in range(181):
        i_180 = np.clip(int(np.round((lon_181[i] - lon_180[0]) / 0.05)), 0, 179)
        basin_181[j, i] = hymap_basin[j_180, i_180]

mask_domain = landmask_181
mask_sebou = (basin_181 == 155.0) & landmask_181
mask_bouregreg = (basin_181 == 150.0) & landmask_181

# Grille GLEAM Maroc (0.10 deg, 60 x 90)
gleam_file_2018 = os.path.join(BASE_DIR, "data/validation/evapotranspiration/GLEAM/raw/E_2018_GLEAM_v4.3a.nc")
with nc.Dataset(gleam_file_2018) as ds_g:
    g_lat_all = ds_g.variables["lat"][:]
    g_lon_all = ds_g.variables["lon"][:]

lat_idx_g = np.where((g_lat_all >= 30.0) & (g_lat_all <= 36.0))[0]
lon_idx_g = np.where((g_lon_all >= -10.0) & (g_lon_all <= -1.0))[0]
gleam_lats = g_lat_all[lat_idx_g]  # descending 35.95 to 30.05 (60)
gleam_lons = g_lon_all[lon_idx_g]  # ascending -9.95 to -1.05 (90)

def regrid_to_gleam(grid_181, mask_weights=None):
    out_grid = np.full((60, 90), np.nan, dtype=np.float32)
    weights = landmask_181 if mask_weights is None else (landmask_181 & mask_weights)
    
    for j, lat_c in enumerate(gleam_lats):
        r_idx = np.where((lat_181 >= lat_c - 0.05 - 1e-4) & (lat_181 <= lat_c + 0.05 + 1e-4))[0]
        for i, lon_c in enumerate(gleam_lons):
            c_idx = np.where((lon_181 >= lon_c - 0.05 - 1e-4) & (lon_181 <= lon_c + 0.05 + 1e-4))[0]
            sub_w = weights[np.ix_(r_idx, c_idx)]
            if np.any(sub_w):
                sub_data = grid_181[np.ix_(r_idx, c_idx)]
                out_grid[j, i] = np.mean(sub_data[sub_w])
    return out_grid

mask_g_domain = ~np.isnan(regrid_to_gleam(np.where(mask_domain, 1.0, np.nan)))
mask_g_sebou = ~np.isnan(regrid_to_gleam(np.where(mask_sebou, 1.0, np.nan)))
mask_g_bouregreg = ~np.isnan(regrid_to_gleam(np.where(mask_bouregreg, 1.0, np.nan)))

# Texture dominante sur grille GLEAM
tex_g = np.full((60, 90), 0, dtype=np.int32)
for j, lat_c in enumerate(gleam_lats):
    r_idx = np.where((lat_181 >= lat_c - 0.05 - 1e-4) & (lat_181 <= lat_c + 0.05 + 1e-4))[0]
    for i, lon_c in enumerate(gleam_lons):
        c_idx = np.where((lon_181 >= lon_c - 0.05 - 1e-4) & (lon_181 <= lon_c + 0.05 + 1e-4))[0]
        sub_w = mask_domain[np.ix_(r_idx, c_idx)]
        if np.any(sub_w):
            sub_tex = dom_texture_181[np.ix_(r_idx, c_idx)][sub_w]
            vals, counts = np.unique(sub_tex, return_counts=True)
            tex_g[j, i] = vals[np.argmax(counts)]

TEXTURE_NAMES = {
    1: "Sand", 2: "Loamy Sand", 3: "Sandy Loam", 4: "Silt Loam", 5: "Silt",
    6: "Loam", 7: "Sandy Clay Loam", 8: "Silty Clay Loam", 9: "Clay Loam",
    10: "Sandy Clay", 11: "Silty Clay", 12: "Clay"
}

# -------------------------------------------------------------
# 2. Chargement des Observations GLEAM et WaPOR
# -------------------------------------------------------------
print(">>> Chargement des observations GLEAM v4.3a...")
def load_gleam_year(year):
    fpath = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/GLEAM/raw/E_{year}_GLEAM_v4.3a.nc")
    with nc.Dataset(fpath) as ds:
        e_raw = ds.variables["E"][:, lat_idx_g, lon_idx_g]
    leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    days_in_month = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    monthly_et = []
    d_start = 0
    for m, nd in enumerate(days_in_month):
        d_end = d_start + nd
        sub_e = e_raw[d_start:d_end, :, :]
        sub_e = np.where(sub_e < -900, np.nan, sub_e)
        m_mean = np.nanmean(sub_e, axis=0)
        m_tot = m_mean * nd
        monthly_et.append(m_tot)
        d_start = d_end
    
    monthly_et = np.array(monthly_et, dtype=np.float32)
    annual_et = np.sum(monthly_et, axis=0)
    return monthly_et, annual_et

gleam_monthly_2018, gleam_annual_2018 = load_gleam_year(2018)

print(">>> Chargement et agrégation de WaPOR v3 AETI 2018...")
wapor_file_2018 = os.path.join(BASE_DIR, "data/validation/evapotranspiration/WaPOR/WaPOR_v3_AETI/WaPOR_v3_AETI_2018.tif")
wapor_raw_2018 = tifffile.imread(wapor_file_2018)
w_h, w_w = wapor_raw_2018.shape
lon_0_w = -7.500932622398005
lat_0_w = 36.02244289319281
d_w = 0.002245788210298804

wapor_annual_on_gleam_2018 = np.full((60, 90), np.nan, dtype=np.float32)
for j, lat_c in enumerate(gleam_lats):
    lat_top = lat_c + 0.05
    lat_bot = lat_c - 0.05
    r0 = int(np.clip(np.floor((lat_0_w - lat_top) / d_w), 0, w_h))
    r1 = int(np.clip(np.ceil((lat_0_w - lat_bot) / d_w), 0, w_h))
    if r0 >= r1: continue
    for i, lon_c in enumerate(gleam_lons):
        lon_left = lon_c - 0.05
        lon_right = lon_c + 0.05
        c0 = int(np.clip(np.floor((lon_left - lon_0_w) / d_w), 0, w_w))
        c1 = int(np.clip(np.ceil((lon_right - lon_0_w) / d_w), 0, w_w))
        if c0 >= c1: continue
        block = wapor_raw_2018[r0:r1, c0:c1]
        valid = (block >= 0) & (block < 5000)
        if np.sum(valid) > 50:
            wapor_annual_on_gleam_2018[j, i] = np.mean(block[valid])

mask_g_wapor_coverage = ~np.isnan(wapor_annual_on_gleam_2018) & mask_g_domain
print(f"Mailles de couverture commune WaPOR v3 sur domaine: {np.sum(mask_g_wapor_coverage)}")

# -------------------------------------------------------------
# 3. Chargement et Agrégation des Simulations Noah-MP
# -------------------------------------------------------------
print(">>> Chargement des simulations Noah-MP 2018...")

EXP_CONFIGS = {
    "OPL": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": False
    },
    "OL_DAIC": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": False
    },
    "ENS_OPL": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    },
    "ENS_corr": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    },
    "DA_nocdf": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    },
    "DA_cdf": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    },
    "DA_nocdf_nowilt": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    },
    "DA_corr": {
        "pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"),
        "is_ensemble": True
    }
}

days_in_month_2018 = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

def read_month_et(flist, ndays):
    daily_sums = np.zeros((121, 181), dtype=np.float64)
    for f in flist:
        with nc.Dataset(f, "r") as ds:
            evap = ds.variables["Evap_tavg"][:]
            if evap.ndim == 3:
                evap = evap[0]
            evap_clean = np.where((evap < -900) | np.isnan(evap), 0.0, evap) * 86400.0
            daily_sums += evap_clean
    m_rate = daily_sums / len(flist)
    return (m_rate * ndays).astype(np.float32)

sim_monthly_2018 = {}
sim_annual_2018 = {}

for exp_name, cfg in EXP_CONFIGS.items():
    t0 = time.time()
    files = sorted(glob.glob(cfg["pattern"], recursive=True))
    files = [f for f in files if "LIS_HIST_" in f and not f.endswith("0000.d01.nc.tmp")]
    
    month_data = {m: [] for m in range(1, 13)}
    for f in files:
        fname = os.path.basename(f)
        m = re.search(r"LIS_HIST_(\d{4})(\d{2})(\d{2})", fname)
        if not m: continue
        f_y, f_m, f_d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ts = pd.Timestamp(year=f_y, month=f_m, day=f_d) - pd.Timedelta(days=1)
        if ts.year == 2018:
            month_data[ts.month].append(f)
            
    m_et_181 = []
    for m in range(1, 13):
        flist = month_data[m]
        if not flist:
            raise FileNotFoundError(f"Missing history files for {exp_name} month {m}")
        m_et_181.append(read_month_et(flist, days_in_month_2018[m - 1]))
        
    m_et_181 = np.array(m_et_181)
    monthly_et_g = np.array([regrid_to_gleam(m_et_181[m]) for m in range(12)])
    annual_et_g = np.sum(monthly_et_g, axis=0)
    
    sim_monthly_2018[exp_name] = monthly_et_g
    sim_annual_2018[exp_name] = annual_et_g
    mean_dom = np.nanmean(annual_et_g[mask_g_domain])
    print(f"  {exp_name:16s} ET chargée en {time.time()-t0:.1f} s | Moyenne domaine: {mean_dom:.1f} mm/an")

# -------------------------------------------------------------
# 4. Calcul des Métriques et Évaluations Statistiques
# -------------------------------------------------------------
print("\n>>> Calcul des métriques statistiques et stratifications...")

def compute_metrics(obs_arr, sim_arr, mask):
    o = obs_arr[mask]
    s = sim_arr[mask]
    valid = ~np.isnan(o) & ~np.isnan(s)
    o, s = o[valid], s[valid]
    if len(o) < 5:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, len(o)
    
    obs_mean = float(np.mean(o))
    sim_mean = float(np.mean(s))
    bias = float(np.mean(s - o))
    rel_bias = float((bias / obs_mean) * 100.0) if obs_mean != 0 else np.nan
    rmsd = float(np.sqrt(np.mean((s - o) ** 2)))
    ubrmsd = float(np.sqrt(max(0.0, rmsd ** 2 - bias ** 2)))
    r, _ = stats.pearsonr(o, s) if len(o) > 2 and np.std(o) > 0 and np.std(s) > 0 else (np.nan, np.nan)
    return obs_mean, sim_mean, bias, rel_bias, rmsd, ubrmsd, float(r), int(len(o))

strata_geo = {
    "Domain": mask_g_domain,
    "Sebou": mask_g_sebou,
    "Bouregreg": mask_g_bouregreg
}

valid_textures = [t for t in [1, 3, 4, 6, 7, 9, 12] if np.any((tex_g == t) & mask_g_domain)]

eval_rows = []

# Pour chaque expérience (WaPOR en premier, GLEAM en second comme requis)
for ref_name, ref_monthly, ref_annual in [
    ("WaPOR_v3", None, wapor_annual_on_gleam_2018),
    ("GLEAM_v4.3a", gleam_monthly_2018, gleam_annual_2018)
]:
    for exp_name in EXP_CONFIGS.keys():
        sim_m = sim_monthly_2018[exp_name]
        sim_a = sim_annual_2018[exp_name]
        
        # 1. Strates géographiques (Domain, Sebou, Bouregreg)
        for s_name, s_mask in strata_geo.items():
            mask_eval = (s_mask & mask_g_wapor_coverage) if ref_name == "WaPOR_v3" else s_mask
            
            # Annuel
            o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(ref_annual, sim_a, mask_eval)
            eval_rows.append({
                "experiment": exp_name,
                "period": "2018",
                "reference": ref_name,
                "stratum_type": "Geographic",
                "stratum": s_name,
                "season": "Annual",
                "n_cells": n_pts,
                "et_obs_mean_mm": round(o_m, 2) if not np.isnan(o_m) else np.nan,
                "et_sim_mean_mm": round(s_m, 2) if not np.isnan(s_m) else np.nan,
                "bias_mm": round(b, 2) if not np.isnan(b) else np.nan,
                "rel_bias_pct": round(rb, 2) if not np.isnan(rb) else np.nan,
                "rmsd_mm": round(rmse, 2) if not np.isnan(rmse) else np.nan,
                "ubrmsd_mm": round(ub_rmse, 2) if not np.isnan(ub_rmse) else np.nan,
                "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan
            })
            
            # Saisonnier MAM et JJA (disponible pour GLEAM)
            if ref_monthly is not None:
                for seas, m_idx in [("MAM", [2, 3, 4]), ("JJA", [5, 6, 7])]:
                    o_seas = np.sum(ref_monthly[m_idx], axis=0)
                    s_seas = np.sum(sim_m[m_idx], axis=0)
                    o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(o_seas, s_seas, mask_eval)
                    eval_rows.append({
                        "experiment": exp_name,
                        "period": "2018",
                        "reference": ref_name,
                        "stratum_type": "Geographic",
                        "stratum": s_name,
                        "season": seas,
                        "n_cells": n_pts,
                        "et_obs_mean_mm": round(o_m, 2) if not np.isnan(o_m) else np.nan,
                        "et_sim_mean_mm": round(s_m, 2) if not np.isnan(s_m) else np.nan,
                        "bias_mm": round(b, 2) if not np.isnan(b) else np.nan,
                        "rel_bias_pct": round(rb, 2) if not np.isnan(rb) else np.nan,
                        "rmsd_mm": round(rmse, 2) if not np.isnan(rmse) else np.nan,
                        "ubrmsd_mm": round(ub_rmse, 2) if not np.isnan(ub_rmse) else np.nan,
                        "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan
                    })

        # 2. Strates par texture (Annual)
        for t_id in valid_textures:
            t_name = f"Texture_{t_id}_{TEXTURE_NAMES.get(t_id, 'Class')}"
            t_mask = (tex_g == t_id) & mask_g_domain
            mask_eval = (t_mask & mask_g_wapor_coverage) if ref_name == "WaPOR_v3" else t_mask
            
            o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(ref_annual, sim_a, mask_eval)
            if n_pts >= 5:
                eval_rows.append({
                    "experiment": exp_name,
                    "period": "2018",
                    "reference": ref_name,
                    "stratum_type": "Texture",
                    "stratum": t_name,
                    "season": "Annual",
                    "n_cells": n_pts,
                    "et_obs_mean_mm": round(o_m, 2) if not np.isnan(o_m) else np.nan,
                    "et_sim_mean_mm": round(s_m, 2) if not np.isnan(s_m) else np.nan,
                    "bias_mm": round(b, 2) if not np.isnan(b) else np.nan,
                    "rel_bias_pct": round(rb, 2) if not np.isnan(rb) else np.nan,
                    "rmsd_mm": round(rmse, 2) if not np.isnan(rmse) else np.nan,
                    "ubrmsd_mm": round(ub_rmse, 2) if not np.isnan(ub_rmse) else np.nan,
                    "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan
                })

df_eval = pd.DataFrame(eval_rows)
out_eval = os.path.join(TABLES_DIR, "et_evaluation_corrected_2018.csv")
df_eval.to_csv(out_eval, index=False)
print(f"\n[OK] Table sauvegardée : {out_eval} ({len(df_eval)} lignes)")

# -------------------------------------------------------------
# 5. Direction de Changement pour les 5 Paires Propres de A1
# -------------------------------------------------------------
print("\n>>> Analyse de la direction de changement pour les 5 paires propres...")

CLEAN_PAIRS = [
    ("ENS_corr", "OL_DAIC", "ENS_corr vs OL_DAIC (Effet residuel ensemble corrige)"),
    ("ENS_OPL", "OL_DAIC", "ENS_OPL vs OL_DAIC (Effet ensemble production)"),
    ("DA_corr", "ENS_corr", "DA_corr vs ENS_corr (Effet observations systeme corrige)"),
    ("DA_nocdf", "ENS_OPL", "DA_nocdf vs ENS_OPL (Effet observations systeme production)"),
    ("DA_nocdf_nowilt", "DA_nocdf", "DA_nocdf_nowilt vs DA_nocdf (Effet filtre fletrissement)")
]

dir_rows = []

for ref_name, ref_annual in [
    ("WaPOR_v3", wapor_annual_on_gleam_2018),
    ("GLEAM_v4.3a", gleam_annual_2018)
]:
    for exp_x, exp_y, pair_desc in CLEAN_PAIRS:
        sim_x = sim_annual_2018[exp_x]
        sim_y = sim_annual_2018[exp_y]
        
        # Strates géographiques
        for s_name, s_mask in strata_geo.items():
            mask_eval = (s_mask & mask_g_wapor_coverage) if ref_name == "WaPOR_v3" else s_mask
            o = ref_annual[mask_eval]
            sx = sim_x[mask_eval]
            sy = sim_y[mask_eval]
            valid = ~np.isnan(o) & ~np.isnan(sx) & ~np.isnan(sy)
            o, sx, sy = o[valid], sx[valid], sy[valid]
            
            if len(o) >= 5:
                mean_diff = float(np.mean(sx - sy))
                bias_x = float(np.mean(sx - o))
                bias_y = float(np.mean(sy - o))
                delta_abs_bias = abs(bias_x) - abs(bias_y)  # < 0: amélioration (rapprochement)
                dist_x = np.abs(sx - o)
                dist_y = np.abs(sy - o)
                frac_closer = float(np.mean(dist_x < dist_y) * 100.0)
                direction = "Rapprochement" if delta_abs_bias < 0 else "Éloignement"
                
                dir_rows.append({
                    "pair": f"{exp_x} - {exp_y}",
                    "pair_description": pair_desc,
                    "reference": ref_name,
                    "stratum_type": "Geographic",
                    "stratum": s_name,
                    "season": "Annual",
                    "n_cells": len(o),
                    "mean_diff_mm": round(mean_diff, 2),
                    "bias_x_mm": round(bias_x, 2),
                    "bias_y_mm": round(bias_y, 2),
                    "delta_abs_bias_mm": round(delta_abs_bias, 2),
                    "frac_closer_pct": round(frac_closer, 2),
                    "direction": direction
                })

        # Strates texturales
        for t_id in valid_textures:
            t_name = f"Texture_{t_id}_{TEXTURE_NAMES.get(t_id, 'Class')}"
            t_mask = (tex_g == t_id) & mask_g_domain
            mask_eval = (t_mask & mask_g_wapor_coverage) if ref_name == "WaPOR_v3" else t_mask
            
            o = ref_annual[mask_eval]
            sx = sim_x[mask_eval]
            sy = sim_y[mask_eval]
            valid = ~np.isnan(o) & ~np.isnan(sx) & ~np.isnan(sy)
            o, sx, sy = o[valid], sx[valid], sy[valid]
            
            if len(o) >= 5:
                mean_diff = float(np.mean(sx - sy))
                bias_x = float(np.mean(sx - o))
                bias_y = float(np.mean(sy - o))
                delta_abs_bias = abs(bias_x) - abs(bias_y)
                dist_x = np.abs(sx - o)
                dist_y = np.abs(sy - o)
                frac_closer = float(np.mean(dist_x < dist_y) * 100.0)
                direction = "Rapprochement" if delta_abs_bias < 0 else "Éloignement"
                
                dir_rows.append({
                    "pair": f"{exp_x} - {exp_y}",
                    "pair_description": pair_desc,
                    "reference": ref_name,
                    "stratum_type": "Texture",
                    "stratum": t_name,
                    "season": "Annual",
                    "n_cells": len(o),
                    "mean_diff_mm": round(mean_diff, 2),
                    "bias_x_mm": round(bias_x, 2),
                    "bias_y_mm": round(bias_y, 2),
                    "delta_abs_bias_mm": round(delta_abs_bias, 2),
                    "frac_closer_pct": round(frac_closer, 2),
                    "direction": direction
                })

df_dir = pd.DataFrame(dir_rows)
out_dir = os.path.join(TABLES_DIR, "et_direction_of_change_corrected_2018.csv")
df_dir.to_csv(out_dir, index=False)
print(f"[OK] Table sauvegardée : {out_dir} ({len(df_dir)} lignes)")
