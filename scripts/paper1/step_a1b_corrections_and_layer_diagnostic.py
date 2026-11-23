#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape A1b : Corrections A1 + diagnostic par couche (2018).
Règles : Aucun nouveau run, pas de téléchargement, pas d'interprétation.
Chiffres générés par script depuis les sorties, "absent" si donnée manquante.
"""

import os
import re
import glob
import time
from collections import OrderedDict
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A1b.md")

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
print("Étape A1b : Corrections A1 + Diagnostic par couche (2018)")
print("=" * 80)

# 1. Grilles, Masques et Classes d'occupation du sol
print("\n>>> [1/6] Chargement des grilles et masques...")
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
with nc.Dataset(lis_input_path) as ds_in:
    landmask_181 = (ds_in.variables["LANDMASK"][:] == 1.0)
    landcover_20 = ds_in.variables["LANDCOVER"][:]
    dom_lc_181 = np.argmax(landcover_20, axis=0) + 1
    lat_181 = ds_in.variables["lat"][:, 0]
    lon_181 = ds_in.variables["lon"][0, :]

ldt_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
with nc.Dataset(ldt_path) as ds_ldt:
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]

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
cells_azzaba = get_catchment(75, 108)

def make_mask_121(ccells):
    w = np.zeros((121, 181), dtype=bool)
    for r, c in ccells:
        w[r, c] = True
        w[r, c+1] = True
        w[r+1, c] = True
        w[r+1, c+1] = True
    return w & landmask_181

mask_dom_veg = landmask_181 & (dom_lc_181 != 13) & (dom_lc_181 != 16)

REGIONS = OrderedDict([
    ("Domaine complet", landmask_181),
    ("Domaine hors classes 13 et 16", mask_dom_veg),
    ("Lalla Chafia", make_mask_121(cells_lalla)),
    ("Sidi Jabeur", make_mask_121(cells_jabeur)),
    ("Sebou amont", make_mask_121(cells_azzaba)),
])

for rname, rmask in REGIONS.items():
    print(f"  Région {rname} : {int(np.count_nonzero(rmask))} mailles valides")

LANDCOVER_NAMES = {
    1: "Evergreen Needleleaf Forest", 2: "Evergreen Broadleaf Forest", 3: "Deciduous Needleleaf Forest",
    4: "Deciduous Broadleaf Forest", 5: "Mixed Forest", 6: "Closed Shrublands", 7: "Open Shrublands",
    8: "Woody Savannas", 9: "Savannas", 10: "Grasslands", 11: "Permanent Wetlands", 12: "Croplands",
    13: "Urban and Built-Up", 14: "Cropland/Natural Vegetation Mosaic", 15: "Snow and Ice",
    16: "Barren or Sparsely Vegetated", 17: "Water",
}

LANDCOVER_MASKS = OrderedDict()
dom_lc_on_land = np.where(landmask_181, dom_lc_181, 0)
unique_lc = np.unique(dom_lc_on_land[dom_lc_on_land > 0])
for lc_id in unique_lc:
    cname = LANDCOVER_NAMES.get(lc_id, f"Classe_{lc_id}")
    mask_c = (dom_lc_on_land == lc_id)
    n_pix = int(np.count_nonzero(mask_c))
    label = f"Classe {lc_id} - {cname}"
    LANDCOVER_MASKS[label] = mask_c

all_strats = []
for rname, rmask in REGIONS.items():
    all_strats.append(("region", rname, rmask))
for lc_label, lc_mask in LANDCOVER_MASKS.items():
    all_strats.append(("landcover", lc_label, lc_mask))

# 2. MODIS LAI 2018
print("\n>>> [2/6] Agrégation de MODIS LAI sur la grille LIS (2018)...")
def load_modis_lai_year(year):
    pattern = os.path.join(BASE_DIR, f"data/observations_archive/MODIS_LAI/processed/{year}/MCD15A2H.006_LAI_*.nc4")
    flist = sorted(glob.glob(pattern))
    if not flist:
        print(f"  [ATTENTION] Aucun fichier MODIS LAI pour {year}")
        return None
    month_grids = {m: [] for m in range(1, 13)}
    r_start, r_end = 28794, 30246
    c_start, c_end = 40794, 42966
    for f in flist:
        fname = os.path.basename(f)
        m = re.search(r"LAI_(\d{4})(\d{3})", fname)
        if not m: continue
        f_yr, f_doy = int(m.group(1)), int(m.group(2))
        center_date = pd.Timestamp(year=f_yr, month=1, day=1) + pd.Timedelta(days=f_doy - 1 + 3)
        target_month = center_date.month
        with nc.Dataset(f, "r") as ds:
            v = ds.variables["Lai_500m"]
            v.set_auto_mask(False)
            sub = v[r_start:r_end, c_start:c_end]
        sub_valid = np.where((sub <= 100) & (sub >= 0), sub * 0.1, np.nan)
        blocks = sub_valid.reshape(121, 12, 181, 12).swapaxes(1, 2).reshape(121, 181, 144)
        val_cnt = np.count_nonzero(~np.isnan(blocks), axis=-1)
        grid_mean = np.nanmean(blocks, axis=-1)
        grid_mean[val_cnt == 0] = np.nan
        month_grids[target_month].append(grid_mean)
    monthly_lai = []
    for m in range(1, 13):
        grids = month_grids[m]
        if grids:
            stacked = np.stack(grids, axis=0)
            monthly_lai.append(np.nanmean(stacked, axis=0))
        else:
            monthly_lai.append(np.full((121, 181), np.nan, dtype=np.float32))
    return np.array(monthly_lai, dtype=np.float32)

modis_lai_2018 = load_modis_lai_year(2018)
modis_lai_annual_2018 = np.nanmean(modis_lai_2018, axis=0)
print(f"  MODIS LAI 2018 annuel moyen (terre) : {np.nanmean(modis_lai_annual_2018[landmask_181]):.4f} m2/m2")

# 3. Simulations Noah-MP 2018 (avec SoilMoist 4 couches)
print("\n>>> [3/6] Chargement des simulations Noah-MP 2018 avec SoilMoist 4 couches...")
RUNS_2018 = OrderedDict([
    ("OL_DAIC", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": False, "substitut": "ENS_corr"}),
    ("ENS_OPL", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}),
    ("ENS_corr", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}),
    ("DA_nocdf", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}),
    ("DA_nocdf_nowilt", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}),
    ("DA_corr", {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}),
])

def load_exp_2018_full(exp_name, pattern, read_lai=True):
    t0 = time.time()
    files = sorted(glob.glob(pattern, recursive=True))
    files = [f for f in files if "LIS_HIST_" in f and not f.endswith(".tmp")]
    month_files = {m: [] for m in range(1, 13)}
    for f in files:
        fname = os.path.basename(f)
        m = re.search(r"LIS_HIST_(\d{4})(\d{2})(\d{2})", fname)
        if not m: continue
        f_y, f_m, f_d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ts = pd.Timestamp(year=f_y, month=f_m, day=f_d) - pd.Timedelta(days=1)
        if ts.year == 2018:
            month_files[ts.month].append(f)
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly_esoil, monthly_tveg, monthly_ecanop, monthly_lai, monthly_sm = [], [], [], [], []
    for m in range(1, 13):
        flist = month_files[m]
        n_days = len(flist)
        nd_expected = days_in_month[m - 1]
        if n_days == 0:
            raise FileNotFoundError(f"Fichiers manquants pour {exp_name} en 2018 mois {m}")
        sum_es = np.zeros((121, 181), dtype=np.float64)
        sum_tv = np.zeros((121, 181), dtype=np.float64)
        sum_ec = np.zeros((121, 181), dtype=np.float64)
        sum_l = np.zeros((121, 181), dtype=np.float64)
        sum_sm = np.zeros((4, 121, 181), dtype=np.float64)
        has_l = False
        for f in flist:
            with nc.Dataset(f, "r") as ds:
                es = ds.variables["ESoil_tavg"][:]
                if es.ndim == 3: es = es[0]
                sum_es += np.where((es < -900) | np.isnan(es), 0.0, es) * 86400.0
                tv = ds.variables["TVeg_tavg"][:]
                if tv.ndim == 3: tv = tv[0]
                sum_tv += np.where((tv < -900) | np.isnan(tv), 0.0, tv) * 86400.0
                ec = ds.variables["ECanop_tavg"][:]
                if ec.ndim == 3: ec = ec[0]
                sum_ec += np.where((ec < -900) | np.isnan(ec), 0.0, ec) * 86400.0
                if read_lai and "LAI_tavg" in ds.variables:
                    has_l = True
                    lv = ds.variables["LAI_tavg"][:]
                    if lv.ndim == 3: lv = lv[0]
                    sum_l += np.where((lv < -900) | np.isnan(lv), 0.0, lv)
                sm = ds.variables["SoilMoist_tavg"][:]
                if sm.ndim == 4: sm = sm[0]
                sum_sm += np.where((sm < -900) | np.isnan(sm), 0.0, sm)
        factor = (nd_expected / n_days)
        monthly_esoil.append((sum_es * factor).astype(np.float32))
        monthly_tveg.append((sum_tv * factor).astype(np.float32))
        monthly_ecanop.append((sum_ec * factor).astype(np.float32))
        monthly_sm.append((sum_sm / n_days).astype(np.float32))
        if has_l:
            monthly_lai.append((sum_l / n_days).astype(np.float32))
        else:
            monthly_lai.append(None)
    monthly_esoil = np.array(monthly_esoil, dtype=np.float32)
    monthly_tveg = np.array(monthly_tveg, dtype=np.float32)
    monthly_ecanop = np.array(monthly_ecanop, dtype=np.float32)
    monthly_sm = np.array(monthly_sm, dtype=np.float32) # shape (12, 4, 121, 181)
    monthly_lai = np.array(monthly_lai, dtype=np.float32) if not any(x is None for x in monthly_lai) else None
    t1 = time.time()
    print(f"  Exp {exp_name} (2018) chargée en {t1-t0:.2f} s. ESoil: {np.nanmean(np.sum(monthly_esoil, axis=0)[landmask_181]):.1f} mm, SM L1: {np.nanmean(monthly_sm[:, 0, landmask_181]):.3f} m3/m3")
    return {"monthly_esoil": monthly_esoil, "monthly_tveg": monthly_tveg, "monthly_ecanop": monthly_ecanop, "monthly_lai": monthly_lai, "monthly_sm": monthly_sm}

data_2018 = {}
for exp_name, cfg in RUNS_2018.items():
    data_2018[exp_name] = load_exp_2018_full(exp_name, cfg["pattern"], read_lai=cfg["has_lai"])

data_2018["OL_DAIC"]["monthly_lai"] = data_2018["ENS_corr"]["monthly_lai"]

# 4. Figure de contrôle MODIS vs ENS_corr (Annuel 2018)
print("\n>>> [4/6] Génération de la figure de contrôle LAI MODIS vs ENS_corr...")
ens_corr_lai_annual = np.mean(data_2018["ENS_corr"]["monthly_lai"], axis=0)
m_modis_plot = np.where(landmask_181, modis_lai_annual_2018, np.nan)
m_ens_plot = np.where(landmask_181, ens_corr_lai_annual, np.nan)

v_max = 3.5
fig, axes = plt.subplots(1, 2, figsize=(13, 6), dpi=300)
lon_grid, lat_grid = np.meshgrid(lon_181, lat_181)

im0 = axes[0].pcolormesh(lon_grid, lat_grid, m_modis_plot, cmap="YlGn", vmin=0.0, vmax=v_max, shading="auto")
axes[0].set_title("(a) MODIS LAI annuel 2018 (MCD15A2H.006)\nagrégé sur la grille LIS 5 km", fontsize=11, fontweight="bold")
axes[0].set_xlabel("Longitude (°)", fontsize=10)
axes[0].set_ylabel("Latitude (°)", fontsize=10)
axes[0].set_aspect("equal")

im1 = axes[1].pcolormesh(lon_grid, lat_grid, m_ens_plot, cmap="YlGn", vmin=0.0, vmax=v_max, shading="auto")
axes[1].set_title("(b) Noah-MP ENS_corr LAI annuel 2018\n(moyenne d'ensemble)", fontsize=11, fontweight="bold")
axes[1].set_xlabel("Longitude (°)", fontsize=10)
axes[1].set_ylabel("Latitude (°)", fontsize=10)
axes[1].set_aspect("equal")

cbar_ax = fig.add_axes([0.25, 0.08, 0.50, 0.03])
cbar = fig.colorbar(im1, cax=cbar_ax, orientation="horizontal")
cbar.set_label("LAI ($m^2/m^2$)", fontsize=10, fontweight="bold")

plt.subplots_adjust(bottom=0.20, top=0.90, wspace=0.25)
out_fig_ctrl = os.path.join(FIGURES_DIR, "A1b_lai_control_modis_vs_ens_corr_2018.png")
plt.savefig(out_fig_ctrl)
plt.close()
print(f"  [OK] Figure de contrôle enregistrée : {out_fig_ctrl}")

# Saisons avec JF+D_2018
SEASONS_MONTHS = OrderedDict([
    ("JF+D_2018", [0, 1, 11]),
    ("MAM", [2, 3, 4]),
    ("JJA", [5, 6, 7]),
    ("SON", [8, 9, 10]),
    ("Annuel", list(range(12))),
])

# 5. Diagnostic par couche pour C1, C2, C3, C4 (2018)
print("\n>>> [5/6] Calcul du diagnostic par couche pour C1, C2, C3, C4...")
CONTRASTS = [
    ("C1", "ENS_OPL − OL_DAIC", "ENS_OPL", "OL_DAIC"),
    ("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"),
    ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr"),
    ("C4", "DA_nocdf_nowilt − DA_nocdf", "DA_nocdf_nowilt", "DA_nocdf"),
]

# Épaisseurs des couches Noah-MP en mm (dz = [0.1, 0.3, 0.6, 1.0] m)
DZ_MM = [100.0, 300.0, 600.0, 1000.0]

diag_records = []
for cid, cname, run_a, run_b in CONTRASTS:
    sm_a = data_2018[run_a]["monthly_sm"] # shape (12, 4, 121, 181)
    sm_b = data_2018[run_b]["monthly_sm"]
    for s_label, s_months in SEASONS_MONTHS.items():
        # Moyenne temporelle saisonnière
        mean_sm_a = np.mean(sm_a[s_months], axis=0) # shape (4, 121, 181)
        mean_sm_b = np.mean(sm_b[s_months], axis=0)
        delta_sm = mean_sm_a - mean_sm_b # shape (4, 121, 181)
        for r_name, r_mask in REGIONS.items():
            n_cells = int(np.count_nonzero(r_mask))
            d_theta_L = [float(np.mean(delta_sm[l][r_mask])) for l in range(4)]
            d_stock_L = [d_theta_L[l] * DZ_MM[l] for l in range(4)]
            d_stock_tot = sum(d_stock_L)
            diag_records.append({
                "period": "2018",
                "contrast_id": cid,
                "contrast_name": cname,
                "season": s_label,
                "region": r_name,
                "n_cells": n_cells,
                "delta_theta_L1_m3m3": round(d_theta_L[0], 5),
                "delta_theta_L2_m3m3": round(d_theta_L[1], 5),
                "delta_theta_L3_m3m3": round(d_theta_L[2], 5),
                "delta_theta_L4_m3m3": round(d_theta_L[3], 5),
                "delta_stock_L1_mm": round(d_stock_L[0], 2),
                "delta_stock_L2_mm": round(d_stock_L[1], 2),
                "delta_stock_L3_mm": round(d_stock_L[2], 2),
                "delta_stock_L4_mm": round(d_stock_L[3], 2),
                "delta_stock_total_mm": round(d_stock_tot, 2),
                "delta_BTRAN": "absent",
            })

df_diag = pd.DataFrame(diag_records)
out_csv_diag = os.path.join(TABLES_DIR, "A1b_soil_moisture_layers_diagnostic.csv")
df_diag.to_csv(out_csv_diag, index=False)
print(f"  [OK] Table {out_csv_diag} enregistrée ({len(df_diag)} lignes)")

# 6. Corrélations spatiales pour C3 (MAM et JJA)
print("\n>>> [6/6] Calcul des corrélations spatiales pour C3 (MAM et JJA)...")
def calc_spatial_corr(x, y):
    valid = ~np.isnan(x) & ~np.isnan(y)
    xv = x[valid]
    yv = y[valid]
    if len(xv) < 3 or np.std(xv) < 1e-9 or np.std(yv) < 1e-9:
        return np.nan
    r = np.corrcoef(xv, yv)[0, 1]
    return round(float(r), 4)

corr_records = []
for s_label in ["MAM", "JJA"]:
    s_months = SEASONS_MONTHS[s_label]
    d_tveg = np.sum(data_2018["DA_corr"]["monthly_tveg"][s_months], axis=0) - np.sum(data_2018["ENS_corr"]["monthly_tveg"][s_months], axis=0)
    d_lai = np.mean(data_2018["DA_corr"]["monthly_lai"][s_months], axis=0) - np.mean(data_2018["ENS_corr"]["monthly_lai"][s_months], axis=0)
    d_sm = np.mean(data_2018["DA_corr"]["monthly_sm"][s_months], axis=0) - np.mean(data_2018["ENS_corr"]["monthly_sm"][s_months], axis=0)
    for r_name, r_mask in REGIONS.items():
        n_cells = int(np.count_nonzero(r_mask))
        x_tv = d_tveg[r_mask]
        x_l = d_lai[r_mask]
        corr_L1 = calc_spatial_corr(x_tv, d_sm[0][r_mask])
        corr_L2 = calc_spatial_corr(x_tv, d_sm[1][r_mask])
        corr_L3 = calc_spatial_corr(x_tv, d_sm[2][r_mask])
        corr_L4 = calc_spatial_corr(x_tv, d_sm[3][r_mask])
        corr_lai = calc_spatial_corr(x_tv, x_l)
        corr_records.append({
            "period": "2018",
            "contrast_id": "C3",
            "contrast_name": "DA_corr − ENS_corr",
            "season": s_label,
            "region": r_name,
            "n_cells": n_cells,
            "corr_delta_tveg_vs_delta_theta_L1": corr_L1,
            "corr_delta_tveg_vs_delta_theta_L2": corr_L2,
            "corr_delta_tveg_vs_delta_theta_L3": corr_L3,
            "corr_delta_tveg_vs_delta_theta_L4": corr_L4,
            "corr_delta_tveg_vs_delta_lai": corr_lai,
        })

df_corr = pd.DataFrame(corr_records)
out_csv_corr = os.path.join(TABLES_DIR, "A1b_c3_spatial_correlations.csv")
df_corr.to_csv(out_csv_corr, index=False)
print(f"  [OK] Table {out_csv_corr} enregistrée ({len(df_corr)} lignes)")

# 7. Régénération des tables de partitionnement et de comparaison avec corrections (b, d, e)
print("\n>>> Régénération des tables de partitionnement et WaPOR avec les corrections...")

# 7.1 Partitioning levels (2018)
part_levels_records = []
for exp_name in RUNS_2018.keys():
    es_m = data_2018[exp_name]["monthly_esoil"]
    tv_m = data_2018[exp_name]["monthly_tveg"]
    ec_m = data_2018[exp_name]["monthly_ecanop"]
    for s_label, s_months in SEASONS_MONTHS.items():
        es_s = np.sum(es_m[s_months], axis=0)
        tv_s = np.sum(tv_m[s_months], axis=0)
        ec_s = np.sum(ec_m[s_months], axis=0)
        et_s = es_s + tv_s + ec_s
        for stype, sname, smask in all_strats:
            es_val = float(np.mean(es_s[smask]))
            tv_val = float(np.mean(tv_s[smask]))
            ec_val = float(np.mean(ec_s[smask]))
            et_val = float(np.mean(et_s[smask]))
            part_levels_records.append({
                "period": "2018",
                "experiment": exp_name,
                "season": s_label,
                "stratification_type": stype,
                "region_or_class": sname,
                "n_cells": int(np.count_nonzero(smask)),
                "ESoil_mm": round(es_val, 2),
                "TVeg_mm": round(tv_val, 2),
                "ECanop_mm": round(ec_val, 2),
                "ET_total_mm": round(et_val, 2),
                "fraction_ESoil": round(es_val / et_val if et_val > 1e-6 else 0.0, 4),
                "fraction_TVeg": round(tv_val / et_val if et_val > 1e-6 else 0.0, 4),
                "fraction_ECanop": round(ec_val / et_val if et_val > 1e-6 else 0.0, 4),
            })

df_part_levels = pd.DataFrame(part_levels_records)
df_part_levels.to_csv(os.path.join(TABLES_DIR, "A1b_et_partitioning_levels.csv"), index=False)
df_part_levels.to_csv(os.path.join(TABLES_DIR, "A1_et_partitioning_levels.csv"), index=False)
print("  [OK] Table A1b_et_partitioning_levels.csv enregistrée")

# 7.2 Partitioning contrasts (2018)
part_contrasts_records = []
for cid, cname, run_a, run_b in CONTRASTS:
    for s_label, s_months in SEASONS_MONTHS.items():
        es_diff = np.sum(data_2018[run_a]["monthly_esoil"][s_months], axis=0) - np.sum(data_2018[run_b]["monthly_esoil"][s_months], axis=0)
        tv_diff = np.sum(data_2018[run_a]["monthly_tveg"][s_months], axis=0) - np.sum(data_2018[run_b]["monthly_tveg"][s_months], axis=0)
        ec_diff = np.sum(data_2018[run_a]["monthly_ecanop"][s_months], axis=0) - np.sum(data_2018[run_b]["monthly_ecanop"][s_months], axis=0)
        et_diff = es_diff + tv_diff + ec_diff
        for stype, sname, smask in all_strats:
            part_contrasts_records.append({
                "period": "2018",
                "contrast_id": cid,
                "contrast_name": cname,
                "season": s_label,
                "stratification_type": stype,
                "region_or_class": sname,
                "n_cells": int(np.count_nonzero(smask)),
                "delta_ESoil_mm": round(float(np.mean(es_diff[smask])), 2),
                "delta_TVeg_mm": round(float(np.mean(tv_diff[smask])), 2),
                "delta_ECanop_mm": round(float(np.mean(ec_diff[smask])), 2),
                "delta_ET_total_mm": round(float(np.mean(et_diff[smask])), 2),
            })

df_part_contrasts = pd.DataFrame(part_contrasts_records)
df_part_contrasts.to_csv(os.path.join(TABLES_DIR, "A1b_et_partitioning_contrasts.csv"), index=False)
df_part_contrasts.to_csv(os.path.join(TABLES_DIR, "A1_et_partitioning_contrasts.csv"), index=False)
print("  [OK] Table A1b_et_partitioning_contrasts.csv enregistrée")

# 7.3 WaPOR Comparison avec ratio_T_over_ETcomb = sum(T)/sum(E+T)
import tifffile
def aggregate_wapor(filepath):
    if not os.path.exists(filepath): return None, None
    raw_img = tifffile.imread(filepath).astype(np.float32)
    h_w, w_w = raw_img.shape
    lat_max_w, lon_0_w, d_w = 36.02, -7.50, 0.0022457882102988038
    agg_grid = np.full((121, 181), np.nan, dtype=np.float32)
    cov_mask = np.zeros((121, 181), dtype=bool)
    for j in range(121):
        lat_c = lat_181[j]
        r0 = int(np.floor((lat_max_w - (lat_c + 0.025)) / d_w))
        r1 = int(np.ceil((lat_max_w - (lat_c - 0.025)) / d_w))
        if r0 < 0 or r1 > h_w or r0 >= r1: continue
        for i in range(181):
            lon_c = lon_181[i]
            c0 = int(np.floor(((lon_c - 0.025) - lon_0_w) / d_w))
            c1 = int(np.ceil(((lon_c + 0.025) - lon_0_w) / d_w))
            if c0 < 0 or c1 > w_w or c0 >= c1: continue
            block = raw_img[r0:r1, c0:c1]
            n_tot = (r1 - r0) * (c1 - c0)
            valid = ~np.isnan(block) & (block >= 0) & (block < 10000)
            if np.count_nonzero(valid) / n_tot >= 0.80:
                cov_mask[j, i] = True
                agg_grid[j, i] = np.mean(block[valid])
    return agg_grid, cov_mask

f_e_18 = os.path.join(BASE_DIR, "data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_2018.tif")
f_t_18 = os.path.join(BASE_DIR, "data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_2018.tif")
w_e_18, m_e_18 = aggregate_wapor(f_e_18)
w_t_18, m_t_18 = aggregate_wapor(f_t_18)
w_mask_18 = (m_e_18 & m_t_18) if (m_e_18 is not None and m_t_18 is not None) else None
print(f"  WaPOR v3 2018 valid mask (>=80%) : {int(np.count_nonzero(w_mask_18))} mailles")

wapor_comp_records = []
for exp_name in RUNS_2018.keys():
    mod_es = np.sum(data_2018[exp_name]["monthly_esoil"], axis=0)
    mod_tv = np.sum(data_2018[exp_name]["monthly_tveg"], axis=0)
    mod_ec = np.sum(data_2018[exp_name]["monthly_ecanop"], axis=0)
    for stype, sname, smask in all_strats:
        valid_cells = smask & landmask_181 & w_mask_18
        n_valid = int(np.count_nonzero(valid_cells))
        if n_valid == 0:
            wapor_comp_records.append({
                "period": "2018", "experiment": exp_name, "season": "Annuel", "stratification_type": stype, "region_or_class": sname,
                "n_cells_valid": 0, "status": "absent (hors emprise WaPOR v3)",
                "ESoil_model_mm": "absent", "E_wapor_mm": "absent", "bias_E_mm": "absent", "abs_bias_E_mm": "absent",
                "TVeg_model_mm": "absent", "T_wapor_mm": "absent", "bias_T_mm": "absent", "abs_bias_T_mm": "absent",
                "ETcomb_model_mm": "absent", "ETcomb_wapor_mm": "absent", "bias_ETcomb_mm": "absent", "abs_bias_ETcomb_mm": "absent",
                "ECanop_model_mm": "absent", "I_wapor_mm": "absent", "bias_ECanop_mm": "absent", "abs_bias_ECanop_mm": "absent",
                "AETI_total_model_mm": "absent", "AETI_total_wapor_mm": "absent", "bias_AETI_mm": "absent",
                "ratio_T_over_ETcomb_model": "absent", "ratio_T_over_ETcomb_wapor": "absent", "monthly_correlation": "absent"
            })
            continue
        m_e, m_t, m_c = mod_es[valid_cells], mod_tv[valid_cells], mod_ec[valid_cells]
        m_comb = m_e + m_t
        wp_e, wp_t = w_e_18[valid_cells], w_t_18[valid_cells]
        wp_comb = wp_e + wp_t
        # Correction 1b : Ratio des moyennes = sum(T) / sum(E+T)
        ratio_mod = float(np.sum(m_t) / np.sum(m_comb)) if np.sum(m_comb) > 1e-6 else np.nan
        ratio_wap = float(np.sum(wp_t) / np.sum(wp_comb)) if np.sum(wp_comb) > 1e-6 else np.nan
        wapor_comp_records.append({
            "period": "2018", "experiment": exp_name, "season": "Annuel", "stratification_type": stype, "region_or_class": sname,
            "n_cells_valid": n_valid, "status": "calcule",
            "ESoil_model_mm": round(float(np.mean(m_e)), 2), "E_wapor_mm": round(float(np.mean(wp_e)), 2),
            "bias_E_mm": round(float(np.mean(m_e - wp_e)), 2), "abs_bias_E_mm": round(float(np.mean(np.abs(m_e - wp_e))), 2),
            "TVeg_model_mm": round(float(np.mean(m_t)), 2), "T_wapor_mm": round(float(np.mean(wp_t)), 2),
            "bias_T_mm": round(float(np.mean(m_t - wp_t)), 2), "abs_bias_T_mm": round(float(np.mean(np.abs(m_t - wp_t))), 2),
            "ETcomb_model_mm": round(float(np.mean(m_comb)), 2), "ETcomb_wapor_mm": round(float(np.mean(wp_comb)), 2),
            "bias_ETcomb_mm": round(float(np.mean(m_comb - wp_comb)), 2), "abs_bias_ETcomb_mm": round(float(np.mean(np.abs(m_comb - wp_comb))), 2),
            "ECanop_model_mm": round(float(np.mean(m_c)), 2), "I_wapor_mm": "absent", "bias_ECanop_mm": "absent", "abs_bias_ECanop_mm": "absent",
            "AETI_total_model_mm": round(float(np.mean(m_e + m_t + m_c)), 2), "AETI_total_wapor_mm": "absent", "bias_AETI_mm": "absent",
            "ratio_T_over_ETcomb_model": round(ratio_mod, 4),
            "ratio_T_over_ETcomb_wapor": round(ratio_wap, 4),
            "monthly_correlation": "absent (WaPOR v3 mensuel non archive)"
        })
    for s_miss in ["JF+D_2018", "MAM", "JJA", "SON"]:
        wapor_comp_records.append({
            "period": "2018", "experiment": exp_name, "season": s_miss, "stratification_type": "region", "region_or_class": "Domaine complet",
            "n_cells_valid": 0, "status": "absent (WaPOR v3 dekadaire/mensuel non archive sur disque)",
            "ESoil_model_mm": "absent", "E_wapor_mm": "absent", "bias_E_mm": "absent", "abs_bias_E_mm": "absent",
            "TVeg_model_mm": "absent", "T_wapor_mm": "absent", "bias_T_mm": "absent", "abs_bias_T_mm": "absent",
            "ETcomb_model_mm": "absent", "ETcomb_wapor_mm": "absent", "bias_ETcomb_mm": "absent", "abs_bias_ETcomb_mm": "absent",
            "ECanop_model_mm": "absent", "I_wapor_mm": "absent", "bias_ECanop_mm": "absent", "abs_bias_ECanop_mm": "absent",
            "AETI_total_model_mm": "absent", "AETI_total_wapor_mm": "absent", "bias_AETI_mm": "absent",
            "ratio_T_over_ETcomb_model": "absent", "ratio_T_over_ETcomb_wapor": "absent", "monthly_correlation": "absent"
        })

df_wapor_comp = pd.DataFrame(wapor_comp_records)
df_wapor_comp.to_csv(os.path.join(TABLES_DIR, "A1b_wapor_et_comparison.csv"), index=False)
df_wapor_comp.to_csv(os.path.join(TABLES_DIR, "A1_wapor_et_comparison.csv"), index=False)
print("  [OK] Table A1b_wapor_et_comparison.csv enregistrée (avec ratio des moyennes)")

# 7.4 WaPOR Direction of Change avec "Domaine hors classes 13 et 16"
w_comb_18 = w_e_18 + w_t_18
doc_records = []
contrasts_doc = [("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"), ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr")]

for cid, clabel, run_da, run_ens in contrasts_doc:
    es_da, tv_da = np.sum(data_2018[run_da]["monthly_esoil"], axis=0), np.sum(data_2018[run_da]["monthly_tveg"], axis=0)
    es_ens, tv_ens = np.sum(data_2018[run_ens]["monthly_esoil"], axis=0), np.sum(data_2018[run_ens]["monthly_tveg"], axis=0)
    components = [("E (ESoil vs WaPOR E)", es_da, es_ens, w_e_18), ("T (TVeg vs WaPOR T)", tv_da, tv_ens, w_t_18), ("E+T (ESoil+TVeg vs WaPOR E+T)", es_da + tv_da, es_ens + tv_ens, w_comb_18)]
    for comp_name, m_da, m_ens, m_wap in components:
        for stype, sname, smask in all_strats:
            vcells = smask & landmask_181 & w_mask_18
            n_val = int(np.count_nonzero(vcells))
            if n_val == 0: continue
            bias_da = np.abs(m_da[vcells] - m_wap[vcells])
            bias_ens = np.abs(m_ens[vcells] - m_wap[vcells])
            d_abs = float(np.mean(bias_da - bias_ens))
            closer = (bias_da < (bias_ens - 1e-6))
            farther = (bias_da > (bias_ens + 1e-6))
            neutral = (~closer & ~farther)
            doc_records.append({
                "period": "2018", "contrast_id": cid, "contrast_name": clabel, "component": comp_name,
                "stratification_type": stype, "region_or_class": sname, "n_cells_valid": n_val,
                "delta_abs_bias_mm": round(d_abs, 2), "pct_cells_closer": round(float(np.count_nonzero(closer) / n_val * 100.0), 2),
                "pct_cells_farther": round(float(np.count_nonzero(farther) / n_val * 100.0), 2), "pct_cells_neutral": round(float(np.count_nonzero(neutral) / n_val * 100.0), 2)
            })

df_doc = pd.DataFrame(doc_records)
df_doc.to_csv(os.path.join(TABLES_DIR, "A1b_wapor_direction_of_change.csv"), index=False)
df_doc.to_csv(os.path.join(TABLES_DIR, "A1_wapor_direction_of_change.csv"), index=False)
print("  [OK] Table A1b_wapor_direction_of_change.csv enregistrée")

# 7.5 LAI Model vs MODIS (avec Domaine hors 13 et 16)
lai_records = []
for exp_name in RUNS_2018.keys():
    mod_lai = data_2018[exp_name]["monthly_lai"]
    subst = RUNS_2018[exp_name]["substitut"]
    for stype, sname, smask in all_strats:
        m_mean_model = [float(np.mean(mod_lai[m][smask])) for m in range(12)]
        m_mean_modis = [float(np.nanmean(modis_lai_2018[m][smask])) for m in range(12)]
        ann_model = float(np.mean(m_mean_model))
        ann_modis = float(np.mean(m_mean_modis))
        bias_ann = ann_model - ann_modis
        valid_corr = ~np.isnan(m_mean_model) & ~np.isnan(m_mean_modis)
        r_val = np.corrcoef(np.array(m_mean_model)[valid_corr], np.array(m_mean_modis)[valid_corr])[0, 1] if np.count_nonzero(valid_corr) > 2 else np.nan
        peak_mod = int(np.argmax(m_mean_model)) + 1
        peak_obs = int(np.nanargmax(m_mean_modis)) + 1
        rec = {
            "period": "2018", "experiment": exp_name, "substitut": subst, "stratification_type": stype, "region_or_class": sname,
            "lai_model_annual_mean": round(ann_model, 4), "lai_modis_annual_mean": round(ann_modis, 4), "bias_annual": round(bias_ann, 4),
            "monthly_correlation": round(float(r_val), 4) if not np.isnan(r_val) else np.nan, "peak_month_model": peak_mod, "peak_month_modis": peak_obs
        }
        for m in range(1, 13):
            rec[f"lai_model_m{m:02d}"] = round(m_mean_model[m-1], 4)
            rec[f"lai_modis_m{m:02d}"] = round(m_mean_modis[m-1], 4)
        lai_records.append(rec)

df_lai_upd = pd.DataFrame(lai_records)
df_lai_upd.to_csv(os.path.join(TABLES_DIR, "A1b_lai_model_vs_modis.csv"), index=False)
df_lai_upd.to_csv(os.path.join(TABLES_DIR, "A1_lai_model_vs_modis.csv"), index=False)
print("  [OK] Table A1b_lai_model_vs_modis.csv enregistrée")

# 7.6 Delta LAI Assimilation (avec Domaine hors 13 et 16)
delta_lai_records = []
contrasts_lai = [("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"), ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr")]
for cid, clabel, run_da, run_ens in contrasts_lai:
    lai_da = data_2018[run_da]["monthly_lai"]
    lai_ens = data_2018[run_ens]["monthly_lai"]
    diff_lai = lai_da - lai_ens
    for stype, sname, smask in all_strats:
        m_diff = [float(np.mean(diff_lai[m][smask])) for m in range(12)]
        ann_diff = float(np.mean(m_diff))
        rec = {"period": "2018", "contrast": clabel, "stratification_type": stype, "region_or_class": sname, "delta_lai_annual_mean": round(ann_diff, 4)}
        for m in range(1, 13):
            rec[f"delta_lai_m{m:02d}"] = round(m_diff[m-1], 4)
        delta_lai_records.append(rec)

df_delta_lai_upd = pd.DataFrame(delta_lai_records)
df_delta_lai_upd.to_csv(os.path.join(TABLES_DIR, "A1b_delta_lai_assimilation.csv"), index=False)
df_delta_lai_upd.to_csv(os.path.join(TABLES_DIR, "A1_delta_lai_assimilation.csv"), index=False)
print("  [OK] Table A1b_delta_lai_assimilation.csv enregistrée")

# 8. GÉNÉRATION DU RAPPORT FACTUEL REPORT_A1b.md (Tableaux seulement)
print("\n>>> Génération de REPORT_A1b.md (tableaux uniquement)...")

rep_b_lines = [
    "# Rapport d'Étape A1b — Diagnostic par Couche et Corrections A1 (2018)",
    "",
    "Ce rapport présente strictement les tableaux générés par script depuis les sorties brutes et les tables de l'étape A1b.",
    "Conformément aux consignes, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.",
    "",
    "## 1. Diagnostic par Couche d'Humidité du Sol (2018)",
    "",
    "Épaisseurs des couches : L1 = 100 mm (0–0,1 m), L2 = 300 mm (0,1–0,4 m), L3 = 600 mm (0,4–1,0 m), L4 = 1 000 mm (1,0–2,0 m).",
    "Stock d'eau : $\\Delta\\text{Stock}_k = \\Delta\\theta_k \\times \\Delta z_k$. $\\Delta\\text{BTRAN}$ est noté `absent` car non archivé en sortie.",
    "",
    "### 1.1 Contrastes Annuels C1, C2, C3, C4 par Couche (Domaine et Bassins)",
    ""
]

sub_d1 = df_diag[(df_diag["season"] == "Annuel")]
cols_d1 = ["contrast_id", "contrast_name", "region", "n_cells", "delta_theta_L1_m3m3", "delta_theta_L2_m3m3", "delta_theta_L3_m3m3", "delta_theta_L4_m3m3", "delta_stock_total_mm", "delta_BTRAN"]
rep_b_lines.append(df_to_markdown_simple(sub_d1[cols_d1]))

rep_b_lines.extend([
    "",
    "### 1.2 Contrastes Saisonniers par Couche pour C2 et C3 (Domaine complet et Domaine hors 13/16)",
    ""
])
sub_d2 = df_diag[(df_diag["contrast_id"].isin(["C2", "C3"])) & (df_diag["region"].isin(["Domaine complet", "Domaine hors classes 13 et 16"]))]
cols_d2 = ["contrast_id", "season", "region", "delta_stock_L1_mm", "delta_stock_L2_mm", "delta_stock_L3_mm", "delta_stock_L4_mm", "delta_stock_total_mm"]
rep_b_lines.append(df_to_markdown_simple(sub_d2[cols_d2]))

rep_b_lines.extend([
    "",
    "---",
    "",
    "## 2. Corrélations Spatiales pour C3 (MAM et JJA 2018)",
    "",
    "Corrélations de Pearson spatiales sur les mailles de chaque région entre $\\Delta\\text{TVeg}$ et $\\Delta\\theta$ de chaque couche, et entre $\\Delta\\text{TVeg}$ et $\\Delta\\text{LAI}$.",
    ""
])
cols_c = ["season", "region", "n_cells", "corr_delta_tveg_vs_delta_theta_L1", "corr_delta_tveg_vs_delta_theta_L2", "corr_delta_tveg_vs_delta_theta_L3", "corr_delta_tveg_vs_delta_theta_L4", "corr_delta_tveg_vs_delta_lai"]
rep_b_lines.append(df_to_markdown_simple(df_corr[cols_c]))

rep_b_lines.extend([
    "",
    "---",
    "",
    "## 3. Synthèse des Tables Mises à Jour avec Corrections",
    "",
    "### 3.1 Comparaison Annuelle contre WaPOR v3 (ratio des moyennes = somme T / somme (E+T))",
    ""
])
sub_w = df_wapor_comp[(df_wapor_comp["season"] == "Annuel") & (df_wapor_comp["stratification_type"] == "region")]
cols_w = ["experiment", "region_or_class", "n_cells_valid", "ESoil_model_mm", "E_wapor_mm", "bias_E_mm", "TVeg_model_mm", "T_wapor_mm", "bias_T_mm", "ratio_T_over_ETcomb_model", "ratio_T_over_ETcomb_wapor"]
rep_b_lines.append(df_to_markdown_simple(sub_w[cols_w]))

rep_b_lines.extend([
    "",
    "### 3.2 Direction de Changement pour C2 et C3 contre WaPOR v3",
    ""
])
sub_doc_reg = df_doc[(df_doc["stratification_type"] == "region")]
cols_doc = ["contrast_id", "contrast_name", "component", "region_or_class", "n_cells_valid", "delta_abs_bias_mm", "pct_cells_closer", "pct_cells_farther", "pct_cells_neutral"]
rep_b_lines.append(df_to_markdown_simple(sub_doc_reg[cols_doc]))

rep_b_lines.extend([
    "",
    "### 3.3 Partition Annuelle de l'ET en 2018 (avec Domaine hors classes 13 et 16)",
    ""
])
sub_p = df_part_levels[(df_part_levels["season"] == "Annuel") & (df_part_levels["stratification_type"] == "region")]
cols_p = ["experiment", "region_or_class", "ESoil_mm", "TVeg_mm", "ECanop_mm", "ET_total_mm", "fraction_TVeg", "fraction_ESoil", "fraction_ECanop"]
rep_b_lines.append(df_to_markdown_simple(sub_p[cols_p]))

rep_b_lines.extend([
    "",
    "---",
    "",
    "## 4. Liste des Fichiers Produits",
    "",
    "### Tables CSV :",
    "- `paper1/tables/A1b_soil_moisture_layers_diagnostic.csv`",
    "- `paper1/tables/A1b_c3_spatial_correlations.csv`",
    "- `paper1/tables/A1b_lai_model_vs_modis.csv`",
    "- `paper1/tables/A1b_delta_lai_assimilation.csv`",
    "- `paper1/tables/A1b_et_partitioning_levels.csv`",
    "- `paper1/tables/A1b_et_partitioning_contrasts.csv`",
    "- `paper1/tables/A1b_wapor_et_comparison.csv`",
    "- `paper1/tables/A1b_wapor_direction_of_change.csv`",
    "",
    "### Figures PNG :",
    "- `paper1/figures/A1b_lai_control_modis_vs_ens_corr_2018.png`",
    "",
    "### Scripts :",
    "- `scripts/paper1/step_a1b_corrections_and_layer_diagnostic.py`",
    "- `paper1/scripts/step_a1b_corrections_and_layer_diagnostic.py`",
    ""
])

with open(REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_b_lines))

print(f"  [OK] Rapport {REPORT_PATH} généré avec succès !")
os.system("cp scripts/paper1/step_a1b_corrections_and_layer_diagnostic.py paper1/scripts/step_a1b_corrections_and_layer_diagnostic.py")
print("  [OK] Script copié dans paper1/scripts/")
print("=" * 80)
