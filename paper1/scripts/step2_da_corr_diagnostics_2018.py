#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step2_da_corr_diagnostics_2018.py
Analyse des diagnostics d'assimilation pour DA_corr_2018 (Partie A2) :
- Nombre d'observations assimilées par mois (DA_corr vs DA_nocdf vs DA_nocdf_nowilt)
- Spread de theta1 : écart-type calculé à partir des membres (restarts mensuelles)
  et étendue / 3.735 (fichiers EnKF spread quotidiens)
- Innovations normalisées : moyenne et variance, par mois et par texture
- Incréments par couche, par mois et par texture

Sortie : paper1/tables/da_corr_diagnostics_2018.csv
"""

import os
import glob
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
PARAM_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# Charger masque domaine et textures
with nc.Dataset(PARAM_NC) as ds:
    landmask = ds.variables["LANDMASK"][:].squeeze() > 0.5
    texture_grid = ds.variables["TEXTURE"][:]
dom_texture = np.argmax(texture_grid, axis=0) + 1  # 1..16
dom_texture_tiles = dom_texture[landmask]

TEXTURE_NAMES = {
    1: "Sand", 2: "Loamy Sand", 3: "Sandy Loam", 4: "Silt Loam", 5: "Silt",
    6: "Loam", 7: "Sandy Clay Loam", 8: "Silty Clay Loam", 9: "Clay Loam",
    10: "Sandy Clay", 11: "Silty Clay", 12: "Clay"
}

LAYER_DEPTHS = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)  # m

DIR_DA_CORR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output")
DIR_DA_NOCDF = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output")
DIR_DA_NOWILT = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output")

print(">>> Analyse des diagnostics EnKF 2018...")

records = []
target_textures = [0] + sorted(list(np.unique(dom_texture_tiles)))

for m in range(1, 13):
    ym = f"2018{m:02d}"
    m_str = f"2018-{m:02d}"
    print(f"\n--- Traitement du mois {m_str} ---")

    # --- A. Fichiers EnKF ---
    # DA_corr
    inv_corr_files = sorted(glob.glob(os.path.join(DIR_DA_CORR, f"EnKF/{ym}/*_innov.*.nc")))
    inc_corr_files = sorted(glob.glob(os.path.join(DIR_DA_CORR, f"EnKF/{ym}/*_incr.*.nc")))
    sp_corr_files = sorted(glob.glob(os.path.join(DIR_DA_CORR, f"EnKF/{ym}/*_spread.*.nc")))

    # DA_nocdf
    p_inv_nocdf = os.path.join(DIR_DA_NOCDF, f"{m_str}/EnKF/{ym}/*_innov.*.nc")
    inv_nocdf_files = sorted(glob.glob(p_inv_nocdf))
    if not inv_nocdf_files:
        inv_nocdf_files = sorted(glob.glob(os.path.join(DIR_DA_NOCDF, f"EnKF/{ym}/*_innov.*.nc")))

    # DA_nowilt
    inv_nowilt_files = sorted(glob.glob(os.path.join(DIR_DA_NOWILT, f"EnKF/{ym}/*_innov.*.nc")))

    # Count observations by texture for DA_corr, DA_nocdf, DA_nowilt
    obs_counts = {
        "corr": {t: 0 for t in target_textures},
        "nocdf": {t: 0 for t in target_textures},
        "nowilt": {t: 0 for t in target_textures}
    }

    # DA_corr innovations and norm innovations
    norm_innovs_corr = {t: [] for t in target_textures}

    for f_inv in inv_corr_files:
        with nc.Dataset(f_inv) as ds:
            d = ds["innov_01"][:].squeeze()
            sig_f = ds["forecast_sigma_01"][:].squeeze()
            valid = (d != -9999.0) & (~np.isnan(d)) & landmask
            if np.sum(valid) > 0:
                d_v = d[valid]
                sig_v = sig_f[valid]
                n_v = d_v / np.sqrt(sig_v**2 + 0.04**2)
                
                obs_counts["corr"][0] += len(d_v)
                norm_innovs_corr[0].extend(n_v)
                
                tex_v = dom_texture[valid]
                for tid in np.unique(tex_v):
                    if tid in obs_counts["corr"]:
                        mask_t = (tex_v == tid)
                        obs_counts["corr"][tid] += int(np.sum(mask_t))
                        norm_innovs_corr[tid].extend(n_v[mask_t])

    for f_inv in inv_nocdf_files:
        with nc.Dataset(f_inv) as ds:
            d = ds["innov_01"][:].squeeze()
            valid = (d != -9999.0) & (~np.isnan(d)) & landmask
            if np.sum(valid) > 0:
                obs_counts["nocdf"][0] += int(np.sum(valid))
                tex_v = dom_texture[valid]
                for tid in np.unique(tex_v):
                    if tid in obs_counts["nocdf"]:
                        obs_counts["nocdf"][tid] += int(np.sum(tex_v == tid))

    for f_inv in inv_nowilt_files:
        with nc.Dataset(f_inv) as ds:
            d = ds["innov_01"][:].squeeze()
            valid = (d != -9999.0) & (~np.isnan(d)) & landmask
            if np.sum(valid) > 0:
                obs_counts["nowilt"][0] += int(np.sum(valid))
                tex_v = dom_texture[valid]
                for tid in np.unique(tex_v):
                    if tid in obs_counts["nowilt"]:
                        obs_counts["nowilt"][tid] += int(np.sum(tex_v == tid))

    print(f"  Obs assimilées : DA_corr={obs_counts['corr'][0]}, DA_nocdf={obs_counts['nocdf'][0]}, DA_nowilt={obs_counts['nowilt'][0]}")

    # --- B. Incréments d'analyse DA_corr ---
    sum_incr_layer = [np.zeros((121, 181), dtype=np.float64) for _ in range(4)]
    for f_inc in inc_corr_files:
        with nc.Dataset(f_inc) as ds:
            for k in range(4):
                var = ds[f"anlys_incr_Soil Moisture Layer {k+1}_01"][:].squeeze()
                valid_inc = (var != -9999.0) & (~np.isnan(var)) & landmask
                sum_incr_layer[k][valid_inc] += var[valid_inc]

    # --- C. Spread theta_1 ---
    # 1. Depuis restart mensuelle DA_corr (écart-type des membres)
    if m == 12:
        rst_pattern = os.path.join(DIR_DA_CORR, "SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc")
    else:
        rst_pattern = os.path.join(DIR_DA_CORR, f"SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.d01.nc")
    r_files = sorted(glob.glob(rst_pattern))
    if not r_files:
        raise FileNotFoundError(f"Restart introuvable : {rst_pattern}")
    rst_file = r_files[-1]

    with nc.Dataset(rst_file) as ds:
        smc = ds.variables["SMC"][:]
        smc1 = smc[0, :].reshape(16030, 20)
        std_members_tiles = np.std(smc1, axis=1, ddof=1)

    # 2. Depuis EnKF spread files (range / 3.735)
    spread_tippett_steps = []
    for f_sp in sp_corr_files:
        with nc.Dataset(f_sp) as ds:
            sp1 = ds["ensspread_Soil Moisture Layer 1_01"][:].squeeze()
            valid_sp = (sp1 != -9999.0) & (~np.isnan(sp1)) & landmask
            if np.sum(valid_sp) > 0:
                spread_tippett_steps.append(sp1 / 3.735)

    if spread_tippett_steps:
        mean_tippett_grid = np.mean(spread_tippett_steps, axis=0)
    else:
        mean_tippett_grid = None

    # --- Assemble records for each texture class ---
    for tid in target_textures:
        if tid == 0:
            t_name = "Domain_All"
            mask_2d = landmask
            mask_tiles = np.ones(16030, dtype=bool)
        else:
            t_name = f"Texture_{tid}_{TEXTURE_NAMES.get(tid, 'Unknown')}"
            mask_2d = landmask & (dom_texture == tid)
            mask_tiles = (dom_texture_tiles == tid)

        n_cells = int(np.sum(mask_2d))
        if n_cells == 0:
            continue

        n_corr = obs_counts["corr"][tid]
        n_nocdf = obs_counts["nocdf"][tid]
        n_nowilt = obs_counts["nowilt"][tid]

        arr_norm = np.array(norm_innovs_corr[tid])
        if len(arr_norm) > 0:
            mean_ninv = float(np.mean(arr_norm))
            var_ninv = float(np.var(arr_norm))
        else:
            mean_ninv = np.nan
            var_ninv = np.nan

        sp_members = float(np.mean(std_members_tiles[mask_tiles]))

        if mean_tippett_grid is not None:
            sp_tippett = float(np.mean(mean_tippett_grid[mask_2d]))
        else:
            sp_tippett = np.nan

        inc_m3m3 = [float(np.mean(sum_incr_layer[k][mask_2d])) for k in range(4)]
        inc_mm = [inc_m3m3[k] * LAYER_DEPTHS[k] * 1000.0 for k in range(4)]
        inc_tot_mm = sum(inc_mm)

        records.append({
            "month": m_str,
            "texture_id": tid,
            "texture_name": t_name,
            "n_cells": n_cells,
            "n_obs_DA_corr": n_corr,
            "n_obs_DA_nocdf": n_nocdf,
            "n_obs_DA_nowilt": n_nowilt,
            "spread_theta1_members_std": round(sp_members, 5),
            "spread_theta1_tippett": round(sp_tippett, 5) if not np.isnan(sp_tippett) else np.nan,
            "spread_method": "restarts: sample std across 20 members (ddof=1); EnKF spread: range / 3.735 (Tippett)",
            "mean_norm_innov": round(mean_ninv, 4) if not np.isnan(mean_ninv) else np.nan,
            "var_norm_innov": round(var_ninv, 4) if not np.isnan(var_ninv) else np.nan,
            "incr_layer1_mm": round(inc_mm[0], 4),
            "incr_layer2_mm": round(inc_mm[1], 4),
            "incr_layer3_mm": round(inc_mm[2], 4),
            "incr_layer4_mm": round(inc_mm[3], 4),
            "incr_total_mm": round(inc_tot_mm, 4),
            "incr_layer1_m3m3": round(inc_m3m3[0], 6),
            "incr_layer2_m3m3": round(inc_m3m3[1], 6),
            "incr_layer3_m3m3": round(inc_m3m3[2], 6),
            "incr_layer4_m3m3": round(inc_m3m3[3], 6)
        })

df = pd.DataFrame(records)

# --- Add ANNUAL Summary rows for each texture ---
annual_records = []
for tid in target_textures:
    df_t = df[df["texture_id"] == tid]
    if len(df_t) == 0:
        continue
    row0 = df_t.iloc[0]
    
    ann_n_corr = int(df_t["n_obs_DA_corr"].sum())
    ann_n_nocdf = int(df_t["n_obs_DA_nocdf"].sum())
    ann_n_nowilt = int(df_t["n_obs_DA_nowilt"].sum())
    
    ann_sp_members = float(df_t["spread_theta1_members_std"].mean())
    ann_sp_tippett = float(df_t["spread_theta1_tippett"].mean())
    
    ann_inc1 = float(df_t["incr_layer1_mm"].sum())
    ann_inc2 = float(df_t["incr_layer2_mm"].sum())
    ann_inc3 = float(df_t["incr_layer3_mm"].sum())
    ann_inc4 = float(df_t["incr_layer4_mm"].sum())
    ann_inctot = float(df_t["incr_total_mm"].sum())
    
    ann_inc1_m3 = float(df_t["incr_layer1_m3m3"].sum())
    ann_inc2_m3 = float(df_t["incr_layer2_m3m3"].sum())
    ann_inc3_m3 = float(df_t["incr_layer3_m3m3"].sum())
    ann_inc4_m3 = float(df_t["incr_layer4_m3m3"].sum())

    weights = df_t["n_obs_DA_corr"]
    if weights.sum() > 0:
        ann_mean_ninv = float(np.average(df_t["mean_norm_innov"], weights=weights))
        ann_var_ninv = float(np.average(df_t["var_norm_innov"], weights=weights) + np.average((df_t["mean_norm_innov"] - ann_mean_ninv)**2, weights=weights))
    else:
        ann_mean_ninv = np.nan
        ann_var_ninv = np.nan

    annual_records.append({
        "month": "ANNUAL",
        "texture_id": tid,
        "texture_name": row0["texture_name"],
        "n_cells": row0["n_cells"],
        "n_obs_DA_corr": ann_n_corr,
        "n_obs_DA_nocdf": ann_n_nocdf,
        "n_obs_DA_nowilt": ann_n_nowilt,
        "spread_theta1_members_std": round(ann_sp_members, 5),
        "spread_theta1_tippett": round(ann_sp_tippett, 5),
        "spread_method": row0["spread_method"],
        "mean_norm_innov": round(ann_mean_ninv, 4) if not np.isnan(ann_mean_ninv) else np.nan,
        "var_norm_innov": round(ann_var_ninv, 4) if not np.isnan(ann_var_ninv) else np.nan,
        "incr_layer1_mm": round(ann_inc1, 4),
        "incr_layer2_mm": round(ann_inc2, 4),
        "incr_layer3_mm": round(ann_inc3, 4),
        "incr_layer4_mm": round(ann_inc4, 4),
        "incr_total_mm": round(ann_inctot, 4),
        "incr_layer1_m3m3": round(ann_inc1_m3, 6),
        "incr_layer2_m3m3": round(ann_inc2_m3, 6),
        "incr_layer3_m3m3": round(ann_inc3_m3, 6),
        "incr_layer4_m3m3": round(ann_inc4_m3, 6)
    })

df_all = pd.concat([df, pd.DataFrame(annual_records)], ignore_index=True)
out_csv = os.path.join(TABLES_DIR, "da_corr_diagnostics_2018.csv")
df_all.to_csv(out_csv, index=False)
print(f"\n>>> [OK] Table générée avec succès : {out_csv}")
print(f"    Nombre total de lignes : {len(df_all)}")
