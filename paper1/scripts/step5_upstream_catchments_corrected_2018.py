#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5_upstream_catchments_corrected_2018.py
Ajoute ENS_corr_2018 et DA_corr_2018 aux bilans hydriques des bassins amont
(Lalla Chafia et Sidi Jabeur) et aux diagnostics d'innovations/incréments (Partie A5).

Met à jour :
  - paper1/tables/water_balance_upstream_catchments_annual_summary_2018.csv
  - paper1/tables/water_balance_upstream_catchments_2018.csv
  - paper1/tables/lalla_chafia_innovations_and_increments.csv
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
print(">>> Délimitation des bassins amont D8...")
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

# Mapping des 16030 tuiles vers (121, 181)
f_sample = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/restart/LIS_RST_NOAHMP401_201801010000.d01.nc")
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
        if smc.shape[1] == 320600:
            smc = smc.reshape(4, 16030, 20).mean(axis=2)
            wa = wa.reshape(16030, 20).mean(axis=1)
            can = can.reshape(16030, 20).mean(axis=1)
            sn = sn.reshape(16030, 20).mean(axis=1)
        tot_mm = np.sum(smc * dz[:, None], axis=0) * 1000.0 + wa + can + sn
        stock_2d = np.full((121, 181), np.nan)
        stock_2d[tile_r, tile_c] = tot_mm
        return stock_2d

monthly_P = {cid: [] for cid in catchments}
opl_dir = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020")
for m in range(1, 13):
    m_lbl = f"2018-{m:02d}"
    opl_files = sorted(glob.glob(os.path.join(opl_dir, f"output/{m_lbl}/SURFACEMODEL/*/LIS_HIST_*.d01.nc")))
    p_grids = np.zeros((121, 181))
    for f in opl_files:
        with nc.Dataset(f) as ds:
            p_grids += ds["TotalPrecip_tavg"][:].squeeze() * 86400.0
    for cid in catchments:
        monthly_P[cid].append(float(np.sum(p_grids * weights_181[cid])))

NEW_EXPS = {
    "ENS_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_corr_2018/SURFACEMODEL"),
        "is_da": False
    },
    "DA_corr": {
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018"),
        "remap_dir": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_corr_2018/SURFACEMODEL"),
        "is_da": True
    }
}

rst_init = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/restarts/surf/LIS_RST_NOAHMP401_201801010000.d01.nc")

new_stocks = {}
for exp, cfg in NEW_EXPS.items():
    print(f"Extraction restarts pour {exp}...")
    rst_files = [rst_init]
    exp_dir = cfg["dir"]
    for m in range(1, 12):
        ym = f"2018{m:02d}"
        f = sorted(glob.glob(os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}/LIS_RST_NOAHMP401_*.nc")))
        rst_files.append(f[-1])
    rst_files.append(os.path.join(exp_dir, "output/SURFACEMODEL/201901/LIS_RST_NOAHMP401_201901010000.d01.nc"))
    new_stocks[exp] = [read_restart_stock(f) for f in rst_files]

def get_da_corr_increments(month, w181):
    ym = f"2018{month:02d}"
    exp_dir = NEW_EXPS["DA_corr"]["dir"]
    files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/LIS_DA_EnKF_*_incr.*.nc")))
    i1, i2, i3, i4 = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            v1 = np.where(ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze())
            v2 = np.where(ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze())
            v3 = np.where(ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze())
            v4 = np.where(ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze())
            i1 += float(np.sum(v1 * w181)) * dz[0] * 1000.0
            i2 += float(np.sum(v2 * w181)) * dz[1] * 1000.0
            i3 += float(np.sum(v3 * w181)) * dz[2] * 1000.0
            i4 += float(np.sum(v4 * w181)) * dz[3] * 1000.0
    return (i1, i2, i3, i4, i1 + i2 + i3 + i4)

print("\n>>> Calcul du bilan mensuel sur les bassins pour ENS_corr et DA_corr...")
new_records = []

for m in range(1, 13):
    ym_str = f"2018-{m:02d}"
    ym = f"2018{m:02d}"

    for exp, cfg in NEW_EXPS.items():
        r_dir = cfg["remap_dir"]
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

        exp_dir = cfg["dir"]
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

        ds_grid = new_stocks[exp][m] - new_stocks[exp][m-1]

        for cid, (cname, ccells) in catchments.items():
            p_val = monthly_P[cid][m-1]
            et_val = float(np.sum(et_grid * weights_181[cid]))
            qs_val = float(np.sum(qs_grid * weights_180[cid]))
            qsb_val = float(np.sum(qsb_grid * weights_180[cid]))
            ds_val = float(np.nansum(ds_grid * weights_181[cid]))

            if cfg["is_da"]:
                i1, i2, i3, i4, itot = get_da_corr_increments(m, weights_181[cid])
            else:
                i1, i2, i3, i4, itot = 0.0, 0.0, 0.0, 0.0, 0.0

            q_tot = qs_val + qsb_val
            residual = p_val - et_val - q_tot + itot - ds_val

            new_records.append({
                "station": cname,
                "station_id": cid,
                "experiment": exp,
                "year_month": ym_str,
                "P_mm": round(p_val, 4),
                "ET_mm": round(et_val, 4),
                "Qs_mm": round(qs_val, 4),
                "Qsb_mm": round(qsb_val, 4),
                "TotalRunoff_mm": round(q_tot, 4),
                "Delta_S_mm": round(ds_val, 4),
                "Incr_Layer1_mm": round(i1, 4),
                "Incr_Layer2_mm": round(i2, 4),
                "Incr_Layer3_mm": round(i3, 4),
                "Incr_Layer4_mm": round(i4, 4),
                "Incr_Total_mm": round(itot, 4),
                "WaterBalance_Residual_mm": round(residual, 4)
            })

df_new_monthly = pd.DataFrame(new_records)

wb_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")
df_old_wb = pd.read_csv(wb_csv)
df_old_wb = df_old_wb[~df_old_wb["experiment"].isin(["ENS_corr", "DA_corr"])]
df_full_wb = pd.concat([df_old_wb, df_new_monthly], ignore_index=True)

# Recalculer Delta_R_vs_OL_DAIC_mm
ol_res = df_full_wb[df_full_wb["experiment"] == "OL_DAIC"].set_index(["station_id", "year_month"])["WaterBalance_Residual_mm"].to_dict()
df_full_wb["Delta_R_vs_OL_DAIC_mm"] = df_full_wb.apply(lambda r: round(r["WaterBalance_Residual_mm"] - ol_res.get((r["station_id"], r["year_month"]), 0.0), 4), axis=1)

df_full_wb.to_csv(wb_csv, index=False)
print(f"[OK] Table mensuelle mise a jour : {wb_csv} ({len(df_full_wb)} lignes)")

print("Mise a jour du resume annuel...")
ann_records = []
ol_residuals_ann = {}
for cid, (cname, _) in catchments.items():
    df_ol = df_full_wb[(df_full_wb["station"] == cname) & (df_full_wb["experiment"] == "OL_DAIC")]
    ol_residuals_ann[cname] = float(df_ol["WaterBalance_Residual_mm"].sum())

for (cname, exp), group in df_full_wb.groupby(["station", "experiment"]):
    p_tot = float(group["P_mm"].sum())
    et_tot = float(group["ET_mm"].sum())
    q_tot = float(group["TotalRunoff_mm"].sum())
    ds_tot = float(group["Delta_S_mm"].sum())
    inc_tot = float(group["Incr_Total_mm"].sum())
    r_tot = float(group["WaterBalance_Residual_mm"].sum())
    delta_r = round(r_tot - ol_residuals_ann[cname], 2)
    valid_closure = abs(r_tot) < 1.0

    ann_records.append({
        "station": cname,
        "experiment": exp,
        "P_mm": round(p_tot, 2),
        "ET_mm": round(et_tot, 2),
        "TotalRunoff_mm": round(q_tot, 2),
        "Delta_S_mm": round(ds_tot, 2),
        "Incr_Total_mm": round(inc_tot, 2),
        "WaterBalance_Residual_mm": round(r_tot, 2),
        "Delta_R_vs_OL_DAIC_mm": delta_r,
        "valid_closure_lt_1mm": valid_closure
    })

df_ann_sum = pd.DataFrame(ann_records).sort_values(["station", "experiment"]).reset_index(drop=True)
ann_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_annual_summary_2018.csv")
df_ann_sum.to_csv(ann_csv, index=False)
print(f"[OK] Table annuelle mise a jour : {ann_csv} ({len(df_ann_sum)} lignes)")

# 4. Mettre à jour lalla_chafia_innovations_and_increments.csv avec DA_corr 2018
print("\n>>> Mise a jour de lalla_chafia_innovations_and_increments.csv avec DA_corr...")
DIR_DA_CORR_ENKF = os.path.join(NEW_EXPS["DA_corr"]["dir"], "output/EnKF")
w_lc = weights_181["b_l_chafia"]
m_lc = w_lc > 0.0
w_lc_norm = w_lc / np.sum(w_lc[m_lc])

corr_innov_records = []
all_innov_lc_2018 = []
i1_vol_ann, i2_vol_ann, i3_vol_ann, i4_vol_ann = 0.0, 0.0, 0.0, 0.0
n_obs_ann = 0

for m in range(1, 13):
    ym = f"2018{m:02d}"
    inv_files = sorted(glob.glob(os.path.join(DIR_DA_CORR_ENKF, f"{ym}/*_innov.*.nc")))
    inc_files = sorted(glob.glob(os.path.join(DIR_DA_CORR_ENKF, f"{ym}/*_incr.*.nc")))

    m_innovs = []
    n_obs_m = 0
    for f in inv_files:
        with nc.Dataset(f) as ds:
            d = ds["innov_01"][:].squeeze()
            valid = (d != -9999.0) & (~np.isnan(d)) & m_lc
            if np.sum(valid) > 0:
                n_obs_m += int(np.sum(valid))
                m_innovs.extend(d[valid])

    i1_m, i2_m, i3_m, i4_m = 0.0, 0.0, 0.0, 0.0
    for f in inc_files:
        with nc.Dataset(f) as ds:
            v1 = np.where(ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze())
            v2 = np.where(ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze())
            v3 = np.where(ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze())
            v4 = np.where(ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze())
            i1_m += float(np.sum(v1 * w_lc_norm))
            i2_m += float(np.sum(v2 * w_lc_norm))
            i3_m += float(np.sum(v3 * w_lc_norm))
            i4_m += float(np.sum(v4 * w_lc_norm))

    mean_inv_m = float(np.mean(m_innovs)) if len(m_innovs) > 0 else np.nan
    all_innov_lc_2018.extend(m_innovs)
    n_obs_ann += n_obs_m
    i1_vol_ann += i1_m
    i2_vol_ann += i2_m
    i3_vol_ann += i3_m
    i4_vol_ann += i4_m

    corr_innov_records.append({
        "target": "Lalla Chafia",
        "experiment": "DA_corr",
        "period_type": "monthly_2018",
        "period": f"2018-{m:02d}",
        "n_obs_assimilated": n_obs_m,
        "mean_innovation_m3m3": round(mean_inv_m, 6) if not np.isnan(mean_inv_m) else np.nan,
        "incr_layer1_m3m3": round(i1_m, 6),
        "incr_layer2_m3m3": round(i2_m, 6),
        "incr_layer3_m3m3": round(i3_m, 6),
        "incr_layer4_m3m3": round(i4_m, 6),
        "incr_layer1_mm": round(i1_m * dz[0] * 1000.0, 4),
        "incr_layer2_mm": round(i2_m * dz[1] * 1000.0, 4),
        "incr_layer3_mm": round(i3_m * dz[2] * 1000.0, 4),
        "incr_layer4_mm": round(i4_m * dz[3] * 1000.0, 4),
        "incr_total_mm": round((i1_m*dz[0] + i2_m*dz[1] + i3_m*dz[2] + i4_m*dz[3]) * 1000.0, 4)
    })

mean_inv_ann = float(np.mean(all_innov_lc_2018)) if len(all_innov_lc_2018) > 0 else np.nan
corr_innov_records.append({
    "target": "Lalla Chafia",
    "experiment": "DA_corr",
    "period_type": "annual_2016_2020",
    "period": "2018",
    "n_obs_assimilated": n_obs_ann,
    "mean_innovation_m3m3": round(mean_inv_ann, 6) if not np.isnan(mean_inv_ann) else np.nan,
    "incr_layer1_m3m3": round(i1_vol_ann, 6),
    "incr_layer2_m3m3": round(i2_vol_ann, 6),
    "incr_layer3_m3m3": round(i3_vol_ann, 6),
    "incr_layer4_m3m3": round(i4_vol_ann, 6),
    "incr_layer1_mm": round(i1_vol_ann * dz[0] * 1000.0, 4),
    "incr_layer2_mm": round(i2_vol_ann * dz[1] * 1000.0, 4),
    "incr_layer3_mm": round(i3_vol_ann * dz[2] * 1000.0, 4),
    "incr_layer4_mm": round(i4_vol_ann * dz[3] * 1000.0, 4),
    "incr_total_mm": round((i1_vol_ann*dz[0] + i2_vol_ann*dz[1] + i3_vol_ann*dz[2] + i4_vol_ann*dz[3]) * 1000.0, 4)
})

lc_csv = os.path.join(TABLES_DIR, "lalla_chafia_innovations_and_increments.csv")
df_old_lc = pd.read_csv(lc_csv)
df_old_lc = df_old_lc[df_old_lc["experiment"] != "DA_corr"]
df_full_lc = pd.concat([df_old_lc, pd.DataFrame(corr_innov_records)], ignore_index=True)
df_full_lc.to_csv(lc_csv, index=False)
print(f"[OK] Table lalla_chafia mise a jour : {lc_csv} ({len(df_full_lc)} lignes)")
