#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step8_et_evaluation_2017.py
---------------------------
Partie B3 : Évaluation de l'évapotranspiration (ET) 2017 contre GLEAM v4.3a
(et documentation de l'absence de données WaPOR v3 en 2017).

Expériences 2017 :
  - OPL, OL_DAIC, ENS_OPL, DA_nocdf, DA_nocdf_nowilt
Stratifications :
  - Géographique : Domaine, Sebou, Bouregreg
  - Textures : 7 classes principales (Sand, Sandy Loam, Silt Loam, Loam, Sandy Clay Loam, Clay Loam, Clay)
  - Saisons : Annual, MAM, JJA

Sortie :
  - paper1/tables/et_evaluation_2017.csv
"""

import os
import glob
import numpy as np
import pandas as pd
import netCDF4 as nc
from scipy import stats

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
CACHE_DIR = os.path.join(BASE_DIR, "paper1/tables/cache_et_2017")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# 1. Grilles, Masques et Stratifications
print(">>> Chargement des masques géographiques et texturaux...")
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = ds_in.variables["LANDMASK"][:] == 1.0  # (121, 181)
    texture_181 = ds_in.variables["TEXTURE"][:]          # (16, 121, 181)
    dom_texture_181 = np.argmax(texture_181, axis=0) + 1  # 1 to 16
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

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
gleam_file_2017 = os.path.join(BASE_DIR, "data/validation/evapotranspiration/GLEAM/raw/E_2017_GLEAM_v4.3a.nc")
with nc.Dataset(gleam_file_2017) as ds_g:
    g_lat_all = ds_g.variables["lat"][:]
    g_lon_all = ds_g.variables["lon"][:]

lat_idx_g = np.where((g_lat_all >= 30.0) & (g_lat_all <= 36.0))[0]
lon_idx_g = np.where((g_lon_all >= -10.0) & (g_lon_all <= -1.0))[0]
gleam_lats = g_lat_all[lat_idx_g]  # 60
gleam_lons = g_lon_all[lon_idx_g]  # 90

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

# 2. Chargement GLEAM 2017
print(">>> Chargement des observations GLEAM v4.3a 2017...")
with nc.Dataset(gleam_file_2017) as ds:
    e_raw = ds.variables["E"][:, lat_idx_g, lon_idx_g]
days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

gleam_monthly_2017 = []
d_start = 0
for m, nd in enumerate(days_in_month):
    d_end = d_start + nd
    sub_e = e_raw[d_start:d_end, :, :]
    sub_e = np.where(sub_e < -900, np.nan, sub_e)
    m_mean = np.nanmean(sub_e, axis=0)
    m_tot = m_mean * nd
    gleam_monthly_2017.append(m_tot)
    d_start = d_end

gleam_monthly_2017 = np.array(gleam_monthly_2017, dtype=np.float32)
gleam_annual_2017 = np.sum(gleam_monthly_2017, axis=0)

# 3. Modèles LIS 2017
MODELS_2017 = {
    "OPL": {
        "style": "hierarchical",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output")
    },
    "OL_DAIC": {
        "style": "flat",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/OL_DAIC_2017/output")
    },
    "ENS_OPL": {
        "style": "flat",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/ENS_OPL_2017/output")
    },
    "DA_nocdf": {
        "style": "hierarchical",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output")
    },
    "DA_nocdf_nowilt": {
        "style": "flat",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/output")
    }
}

def load_simulated_et_2017(exp_name, cfg):
    cache_f = os.path.join(CACHE_DIR, f"et_sim_gleam_grid_{exp_name}_2017.npz")
    if os.path.exists(cache_f):
        data = np.load(cache_f)
        print(f"  [{exp_name}] Chargé depuis le cache.")
        return data["monthly"], data["annual"]

    print(f"  [{exp_name}] Calcul du cumul mensuel et regridding sur grille GLEAM...")
    monthly_g = []
    for m in range(1, 13):
        m_str = f"2017-{m:02d}"
        ym = f"2017{m:02d}"
        if cfg["style"] == "hierarchical":
            p = os.path.join(cfg["dir"], f"{m_str}/SURFACEMODEL/{ym}/LIS_HIST_*.nc")
        else:
            p = os.path.join(cfg["dir"], f"SURFACEMODEL/{ym}/LIS_HIST_*.nc")
        files = sorted(glob.glob(p))
        if not files:
            raise FileNotFoundError(f"Aucun fichier trouvé pour {exp_name} {m_str}: {p}")

        m_tot_181 = np.zeros((121, 181), dtype=np.float32)
        for fn in files:
            with nc.Dataset(fn) as ds:
                evap = ds.variables["Evap_tavg"][:].squeeze() * 86400.0  # mm/jour
                m_tot_181 += evap

        g_m = regrid_to_gleam(m_tot_181)
        monthly_g.append(g_m)

    monthly_g = np.array(monthly_g, dtype=np.float32)
    annual_g = np.sum(monthly_g, axis=0)
    np.savez_compressed(cache_f, monthly=monthly_g, annual=annual_g)
    print(f"  [{exp_name}] Terminé et mis en cache.")
    return monthly_g, annual_g

def compute_metrics(o_grid, s_grid, mask):
    valid = mask & ~np.isnan(o_grid) & ~np.isnan(s_grid)
    n = int(np.sum(valid))
    if n < 5:
        return np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, np.nan, n
    o = o_grid[valid]
    s = s_grid[valid]
    o_m = float(np.mean(o))
    s_m = float(np.mean(s))
    bias = s_m - o_m
    rel_bias = (bias / o_m * 100.0) if abs(o_m) > 1e-6 else np.nan
    rmse = float(np.sqrt(np.mean((s - o)**2)))
    ub_rmse = float(np.sqrt(max(0.0, rmse**2 - bias**2)))
    r_val, _ = stats.pearsonr(s, o) if np.std(s) > 1e-6 and np.std(o) > 1e-6 else (np.nan, np.nan)
    return o_m, s_m, bias, rel_bias, rmse, ub_rmse, float(r_val), n

def main():
    print("================================================================================")
    print("  EVALUATION DE L'EVAPOTRANSPIRATION (ET) 2017 (PARTIE B3)")
    print("================================================================================")

    sim_et_2017 = {}
    for exp_name, cfg in MODELS_2017.items():
        sim_et_2017[exp_name] = load_simulated_et_2017(exp_name, cfg)

    GEOG_STRATA = [
        ("Domaine", mask_g_domain),
        ("Sebou", mask_g_sebou),
        ("Bouregreg", mask_g_bouregreg)
    ]
    valid_textures = [1, 3, 4, 6, 7, 9, 12]

    eval_rows = []

    for exp_name, (sim_m, sim_a) in sim_et_2017.items():
        print(f"\n>>> Évaluation pour {exp_name}...")

        # 1. Évaluation contre GLEAM v4.3a
        # 1.1 Strates Géographiques
        for s_name, s_mask in GEOG_STRATA:
            mask_eval = s_mask & mask_g_domain
            # Annuel
            o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(gleam_annual_2017, sim_a, mask_eval)
            eval_rows.append({
                "experiment": exp_name,
                "period": "2017",
                "reference": "GLEAM_v4.3a",
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
                "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan,
                "note": "OK"
            })

            # Saisonnier MAM et JJA
            for seas, m_idx in [("MAM", [2, 3, 4]), ("JJA", [5, 6, 7])]:
                o_seas = np.sum(gleam_monthly_2017[m_idx], axis=0)
                s_seas = np.sum(sim_m[m_idx], axis=0)
                o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(o_seas, s_seas, mask_eval)
                eval_rows.append({
                    "experiment": exp_name,
                    "period": "2017",
                    "reference": "GLEAM_v4.3a",
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
                    "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan,
                    "note": "OK"
                })

        # 1.2 Strates par texture
        for t_id in valid_textures:
            t_name = f"Texture_{t_id}_{TEXTURE_NAMES.get(t_id, 'Class')}"
            t_mask = (tex_g == t_id) & mask_g_domain
            o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(gleam_annual_2017, sim_a, t_mask)
            if n_pts >= 5:
                eval_rows.append({
                    "experiment": exp_name,
                    "period": "2017",
                    "reference": "GLEAM_v4.3a",
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
                    "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan,
                    "note": "OK"
                })

        # 2. Entrée pour WaPOR v3 (Documentation explicite de données manquantes)
        for s_name, s_mask in GEOG_STRATA:
            eval_rows.append({
                "experiment": exp_name,
                "period": "2017",
                "reference": "WaPOR_v3",
                "stratum_type": "Geographic",
                "stratum": s_name,
                "season": "Annual",
                "n_cells": 0,
                "et_obs_mean_mm": np.nan,
                "et_sim_mean_mm": np.nan,
                "bias_mm": np.nan,
                "rel_bias_pct": np.nan,
                "rmsd_mm": np.nan,
                "ubrmsd_mm": np.nan,
                "r_spatial": np.nan,
                "note": "DONNEE_MANQUANTE : Produit WaPOR v3 AETI non disponible pour l'annee 2017 dans data/validation/evapotranspiration/WaPOR/"
            })

    df_eval = pd.DataFrame(eval_rows)
    out_csv = os.path.join(TABLES_DIR, "et_evaluation_2017.csv")
    df_eval.to_csv(out_csv, index=False)
    print(f"\n[OK] Table sauvegardée avec succès : {out_csv} ({len(df_eval)} lignes).")
    print(df_eval[(df_eval["reference"] == "GLEAM_v4.3a") & (df_eval["stratum"] == "Domaine") & (df_eval["season"] == "Annual")][["experiment", "et_obs_mean_mm", "et_sim_mean_mm", "bias_mm", "rmsd_mm", "r_spatial"]])

if __name__ == "__main__":
    main()
