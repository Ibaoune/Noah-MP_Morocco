#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcul du bilan hydrique complet mensuel 2018 sur les bassins versants amont
de Lalla Chafia et Sidi Jabeur pour les 6 experiences :
OPL, OL_DAIC, ENS_OPL, DA_nocdf, DA_cdf, DA_nocdf_nowilt.

Stock S calcule rigoureusement a partir des restarts mensuels :
  S = sum_{l=1}^4 SMC_l * dz_l * 1000 + WA + CANWAT + SNEQV
  (avec moyenne d'ensemble pour les ensembles).

Controle de validite :
  Residu annuel de OL_DAIC et OPL < 1 mm/an.
"""

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# 1. Delimitation HyMAP D8
with nc.Dataset(LDT_FILE) as ds:
    area_180 = ds["HYMAP_grid_area"][:].filled(0.0)
    flow_x = ds["HYMAP_flow_direction_x"][:]
    flow_y = ds["HYMAP_flow_direction_y"][:]

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

cells_lalla = get_catchment(75, 71)
cells_jabeur = get_catchment(71, 71)

catchments = {
    "b_l_chafia": ("Lalla Chafia", cells_lalla),
    "b_s_jabeur": ("Sidi Jabeur", cells_jabeur)
}

masks_180 = {}
weights_180 = {}
weights_181 = {}

for cid, (cname, ccells) in catchments.items():
    m180 = np.zeros((120, 180), dtype=bool)
    for r, c in ccells:
        m180[r, c] = True
    masks_180[cid] = m180
    
    tot_area = sum(area_180[r, c] for r, c in ccells)
    w180 = np.zeros((120, 180), dtype=float)
    for r, c in ccells:
        w180[r, c] = area_180[r, c] / tot_area
    weights_180[cid] = w180

    w181 = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w181[r, c] += 0.25 * area_180[r, c]
        w181[r, c+1] += 0.25 * area_180[r, c]
        w181[r+1, c] += 0.25 * area_180[r, c]
        w181[r+1, c+1] += 0.25 * area_180[r, c]
    weights_181[cid] = w181 / np.sum(w181)

dz = np.array([0.1, 0.3, 0.6, 1.0])

# Repertoires des simulations
EXP_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018")
}

REMAP_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"),
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OL_DAIC_2018/SURFACEMODEL"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_cdf_noirr_2016_2020/SURFACEMODEL"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_nowilt_2018/SURFACEMODEL")
}

# Mapping des 16030 tuiles vers (121, 181)
f_sample = os.path.join(EXP_DIRS["OL_DAIC"], "restart/LIS_RST_NOAHMP401_201801010000.d01.nc")
with nc.Dataset(f_sample) as ds:
    lat_tile = ds['lat'][:]
    lon_tile = ds['lon'][:]
    tile_c = np.round((lon_tile - (-10.0)) / 0.05).astype(int)
    tile_r = np.round((lat_tile - 30.0) / 0.05).astype(int)

def read_restart_stock(fp):
    with nc.Dataset(fp) as ds:
        smc = ds['SMC'][:]
        wa = ds['WA'][:]
        can = ds['CANWAT'][:]
        sn = ds['SNEQV'][:]
        if smc.shape[1] == 320600: # ensemble (4, 320600)
            smc = smc.reshape(4, 16030, 20).mean(axis=2)
            wa = wa.reshape(16030, 20).mean(axis=1)
            can = can.reshape(16030, 20).mean(axis=1)
            sn = sn.reshape(16030, 20).mean(axis=1)
        tot_mm = np.sum(smc * dz[:, None], axis=0) * 1000.0 + wa + can + sn
        stock_2d = np.full((121, 181), np.nan)
        stock_2d[tile_r, tile_c] = tot_mm
        return stock_2d

# Restarts mensuels pour chaque experience (0 a 12 -> 13 restarts)
print("Identification des restarts pour chaque experience...")
exp_restarts = {}

# OPL
rst_opl = [os.path.join(EXP_DIRS["OPL"], "output/2017-12/SURFACEMODEL/201801/LIS_RST_NOAHMP401_201801010000.d01.nc")]
for m in range(1, 12):
    m_lbl = f"2018-{m:02d}"
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["OPL"], f"output/{m_lbl}/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_opl.append(f[-1])
rst_opl.append(os.path.join(EXP_DIRS["OPL"], "output/2018-12/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["OPL"] = rst_opl

# OL_DAIC
rst_ol = [os.path.join(EXP_DIRS["OL_DAIC"], "restart/LIS_RST_NOAHMP401_201801010000.d01.nc")]
for m in range(1, 12):
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["OL_DAIC"], f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_ol.append(f[-1])
rst_ol.append(os.path.join(EXP_DIRS["OL_DAIC"], "output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["OL_DAIC"] = rst_ol

# ENS_OPL
rst_ens_init = os.path.join(EXP_DIRS["DA_nocdf"], "restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc")
rst_ens = [rst_ens_init]
for m in range(1, 12):
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["ENS_OPL"], f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_ens.append(f[-1])
rst_ens.append(os.path.join(EXP_DIRS["ENS_OPL"], "output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["ENS_OPL"] = rst_ens

# DA_nocdf
rst_da_nocdf = [os.path.join(EXP_DIRS["DA_nocdf"], "restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc")]
for m in range(1, 12):
    m_lbl = f"2018-{m:02d}"
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["DA_nocdf"], f"output/{m_lbl}/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_da_nocdf.append(f[-1])
rst_da_nocdf.append(os.path.join(EXP_DIRS["DA_nocdf"], "output/2018-12/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["DA_nocdf"] = rst_da_nocdf

# DA_cdf
rst_da_cdf = [os.path.join(EXP_DIRS["DA_cdf"], "restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc")]
for m in range(1, 12):
    m_lbl = f"2018-{m:02d}"
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["DA_cdf"], f"output/{m_lbl}/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_da_cdf.append(f[-1])
rst_da_cdf.append(os.path.join(EXP_DIRS["DA_cdf"], "output/2018-12/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["DA_cdf"] = rst_da_cdf

# DA_nocdf_nowilt
rst_nowilt = [rst_ens_init]
for m in range(1, 12):
    ym = f"2018{m:02d}"
    f = sorted(glob.glob(os.path.join(EXP_DIRS["DA_nocdf_nowilt"], f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
    rst_nowilt.append(f[-1])
rst_nowilt.append(os.path.join(EXP_DIRS["DA_nocdf_nowilt"], "output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
exp_restarts["DA_nocdf_nowilt"] = rst_nowilt

for exp, flist in exp_restarts.items():
    print(f"  {exp}: {len(flist)} restarts (all exist: {all(os.path.exists(f) for f in flist)})")

# Lecture des stocks
print("\nLecture des grilles de stockage S (SMC+WA+CANWAT+SNEQV) pour toutes les experiences...")
exp_stocks = {}
for exp, flist in exp_restarts.items():
    print(f"  Lecture des restarts de {exp}...")
    exp_stocks[exp] = [read_restart_stock(f) for f in flist]

# Fonction extraction des increments EnKF par mois
def get_enkf_increments(exp, year, month, w181):
    if exp not in ["DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    
    ym = f"{year}{month:02d}"
    m_label = f"{year}-{month:02d}"
    exp_dir = EXP_DIRS[exp]
    
    if exp in ["DA_nocdf_nowilt"]:
        files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/LIS_DA_EnKF_*_incr.*.nc")))
    else:
        files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_label}/EnKF/{ym}/LIS_DA_EnKF_*_incr.*.nc")))

    i1, i2, i3, i4 = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            v1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
            v2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
            v3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
            v4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
            i1 += float(np.sum(v1 * w181)) * dz[0] * 1000.0
            i2 += float(np.sum(v2 * w181)) * dz[1] * 1000.0
            i3 += float(np.sum(v3 * w181)) * dz[2] * 1000.0
            i4 += float(np.sum(v4 * w181)) * dz[3] * 1000.0
    return (i1, i2, i3, i4, i1 + i2 + i3 + i4)

# Precalcul de P mensuel (identique a toutes les experiences, lu depuis OPL)
monthly_P = {cid: [] for cid in catchments}
for m in range(1, 13):
    m_lbl = f"2018-{m:02d}"
    opl_files = sorted(glob.glob(os.path.join(EXP_DIRS["OPL"], f"output/{m_lbl}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    p_grids = np.zeros((121, 181))
    for f in opl_files:
        with nc.Dataset(f) as ds:
            p_grids += ds["TotalPrecip_tavg"][:].squeeze() * 86400.0
    for cid in catchments:
        monthly_P[cid].append(float(np.sum(p_grids * weights_181[cid])))

# Calcul complet du bilan mensuel
print("\nCalcul du bilan hydrique mensuel 2018 sur chaque bassin...")
exps = ["OPL", "OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]
records = []

for m in range(1, 13):
    ym_str = f"2018-{m:02d}"
    ym = f"2018{m:02d}"
    print(f"  Traitement du mois {ym_str}...")

    for exp in exps:
        # Fichiers remappes pour Qs et Qsb
        r_dir = REMAP_DIRS[exp]
        remap_files = sorted(glob.glob(os.path.join(r_dir, f"{ym}/*.d01.nc")))
        if m < 12:
            f_next = os.path.join(r_dir, f"2018{m+1:02d}/LIS_HIST_2018{m+1:02d}010000.d01.nc")
        else:
            f_next = os.path.join(r_dir, "201901/LIS_HIST_201901010000.d01.nc")
        if os.path.exists(f_next):
            remap_files.append(f_next)
        remap_files = [f for f in remap_files if not os.path.basename(f).startswith(f"LIS_HIST_{ym}010000")]

        qs_grid = np.zeros((120, 180))
        qsb_grid = np.zeros((120, 180))
        for f in remap_files:
            with nc.Dataset(f) as ds:
                qs_grid += np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb_grid += np.squeeze(ds["Qsb_tavg"][:]) * 86400.0

        # Fichiers natifs pour ET
        exp_dir = EXP_DIRS[exp]
        if exp in ["OPL", "DA_nocdf", "DA_cdf"]:
            nat_files = sorted(glob.glob(os.path.join(exp_dir, f"output/{ym_str}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
        else:
            if m < 12:
                nat_files = sorted(glob.glob(os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")))[1:]
                f_nat_next = sorted(glob.glob(os.path.join(exp_dir, f"output/SURFACEMODEL/2018{m+1:02d}/LIS_HIST_*.d01.nc")))[0]
                nat_files.append(f_nat_next)
            else:
                nat_files = sorted(glob.glob(os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_HIST_*.d01.nc")))[1:]
                f_nat_next = os.path.join(exp_dir, "output/SURFACEMODEL/201901/LIS_HIST_201901010000.d01.nc")
                nat_files.append(f_nat_next)

        et_grid = np.zeros((121, 181))
        for f in nat_files:
            with nc.Dataset(f) as ds:
                et_grid += ds["Evap_tavg"][:].squeeze() * 86400.0

        # Delta S a partir des restarts
        ds_grid = exp_stocks[exp][m] - exp_stocks[exp][m-1]

        for cid, (cname, _) in catchments.items():
            w180 = weights_180[cid]
            w181 = weights_181[cid]

            p_val = monthly_P[cid][m-1]
            et_val = float(np.sum(et_grid * w181))
            qs_val = float(np.sum(qs_grid * w180))
            qsb_val = float(np.sum(qsb_grid * w180))
            delta_s_val = float(np.nansum(ds_grid * w181))

            i1, i2, i3, i4, itot = get_enkf_increments(exp, 2018, m, w181)

            residual = p_val - et_val - (qs_val + qsb_val) + itot - delta_s_val

            records.append({
                "station": cname,
                "station_id": cid,
                "experiment": exp,
                "year_month": ym_str,
                "P_mm": round(p_val, 4),
                "ET_mm": round(et_val, 4),
                "Qs_mm": round(qs_val, 4),
                "Qsb_mm": round(qsb_val, 4),
                "TotalRunoff_mm": round(qs_val + qsb_val, 4),
                "Delta_S_mm": round(delta_s_val, 4),
                "Incr_Layer1_mm": round(i1, 4),
                "Incr_Layer2_mm": round(i2, 4),
                "Incr_Layer3_mm": round(i3, 4),
                "Incr_Layer4_mm": round(i4, 4),
                "Incr_Total_mm": round(itot, 4),
                "WaterBalance_Residual_mm": round(residual, 4)
            })

df = pd.DataFrame(records)

# Ajout de la colonne Delta_R = R_exp - R_OL_DAIC
print("\nCalcul de Delta_R = R_exp - R_OL_DAIC...")
# Extraire les residus de OL_DAIC pour chaque (station_id, year_month)
ol_res = df[df["experiment"] == "OL_DAIC"].set_index(["station_id", "year_month"])["WaterBalance_Residual_mm"].to_dict()

def calc_delta_r(row):
    r_ol = ol_res.get((row["station_id"], row["year_month"]), 0.0)
    return round(row["WaterBalance_Residual_mm"] - r_ol, 4)

df["Delta_R_vs_OL_DAIC_mm"] = df.apply(calc_delta_r, axis=1)

out_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")
df.to_csv(out_csv, index=False)
print(f"[OK] Table de bilan hydrique generee : {out_csv} ({len(df)} lignes)")

# Synthese annuelle et controle de validite
print("\n================ CONTROLE DE VALIDITE ANNUEL ================")
summary = []
for st_id in ["b_l_chafia", "b_s_jabeur"]:
    sub = df[df["station_id"] == st_id]
    st_name = sub["station"].iloc[0]
    print(f"\n--- {st_name} ({st_id}) ---")
    for exp in exps:
        esub = sub[sub["experiment"] == exp]
        ann_P = esub["P_mm"].sum()
        ann_ET = esub["ET_mm"].sum()
        ann_Q = esub["TotalRunoff_mm"].sum()
        ann_dS = esub["Delta_S_mm"].sum()
        ann_Incr = esub["Incr_Total_mm"].sum()
        ann_R = esub["WaterBalance_Residual_mm"].sum()
        ann_dR = esub["Delta_R_vs_OL_DAIC_mm"].sum()
        
        valid = "VALID (< 1 mm)" if abs(ann_R) < 1.0 else "NON-VALID"
        print(f"  {exp:15s}: P={ann_P:6.1f} ET={ann_ET:6.1f} Q={ann_Q:6.1f} dS={ann_dS:6.1f} Incr={ann_Incr:6.1f} => R={ann_R:+6.2f} mm/an | dR={ann_dR:+6.2f} mm/an [{valid}]")
        summary.append({
            "station": st_name,
            "experiment": exp,
            "P_mm": round(ann_P, 2),
            "ET_mm": round(ann_ET, 2),
            "TotalRunoff_mm": round(ann_Q, 2),
            "Delta_S_mm": round(ann_dS, 2),
            "Incr_Total_mm": round(ann_Incr, 2),
            "WaterBalance_Residual_mm": round(ann_R, 2),
            "Delta_R_vs_OL_DAIC_mm": round(ann_dR, 2),
            "valid_closure_lt_1mm": abs(ann_R) < 1.0
        })

df_sum = pd.DataFrame(summary)
out_sum_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_annual_summary_2018.csv")
df_sum.to_csv(out_sum_csv, index=False)
print(f"\n[OK] Synthese annuelle sauvee : {out_sum_csv}")
