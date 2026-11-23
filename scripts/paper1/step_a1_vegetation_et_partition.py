#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step_a1_vegetation_et_partition.py
Étape A1 : Végétation et partition de l ET (H1).
"""
import os, sys, glob, re, time
import numpy as np
import pandas as pd
import netCDF4 as nc
import tifffile
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
SCRIPTS_DIR = os.path.join(BASE_DIR, "paper1/scripts")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A1.md")
os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(SCRIPTS_DIR, exist_ok=True)

print("=" * 80)
print("Étape A1 : Végétation et partition de l ET (H1)")
print("=" * 80)

def df_to_markdown_simple(df):
    headers = list(df.columns)
    lines = []
    lines.append("| " + " | ".join(str(h) for h in headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[h]) for h in headers) + " |")
    return "\n".join(lines)

# 1. Grilles, Masques et Classes d occupation du sol
print("\n>>> [1/5] Chargement des grilles et masques...")
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

REGIONS = {
    "Domaine complet": landmask_181,
    "Lalla Chafia": make_mask_121(cells_lalla),
    "Sidi Jabeur": make_mask_121(cells_jabeur),
    "Sebou amont": make_mask_121(cells_azzaba),
}

for rname, rmask in REGIONS.items():
    print(f"  Région {rname} : {np.count_nonzero(rmask)} mailles valides")

LANDCOVER_NAMES = {
    1: "Evergreen Needleleaf Forest",
    2: "Evergreen Broadleaf Forest",
    3: "Deciduous Needleleaf Forest",
    4: "Deciduous Broadleaf Forest",
    5: "Mixed Forests",
    6: "Closed Shrublands",
    7: "Open Shrublands",
    8: "Woody Savannas",
    9: "Savannas",
    10: "Grasslands",
    11: "Permanent Wetlands",
    12: "Croplands",
    13: "Urban and Built-Up",
    14: "Cropland/Natural Vegetation Mosaic",
    15: "Snow and Ice",
    16: "Barren or Sparsely Vegetated",
    17: "Water",
}

LANDCOVER_MASKS = {}
dom_lc_on_land = np.where(landmask_181, dom_lc_181, 0)
unique_lc = np.unique(dom_lc_on_land[dom_lc_on_land > 0])
for lc_id in unique_lc:
    cname = LANDCOVER_NAMES.get(lc_id, f"Classe_{lc_id}")
    mask_c = (dom_lc_on_land == lc_id)
    n_pix = np.count_nonzero(mask_c)
    label = f"Classe {lc_id} - {cname}"
    LANDCOVER_MASKS[label] = mask_c
    print(f"  {label} : {n_pix} mailles ({n_pix / np.count_nonzero(landmask_181) * 100:.2f} %)")

# 2. MODIS LAI
print("\n>>> [2/5] Agrégation de MODIS LAI sur la grille LIS (2018 et 2016-2020)...")
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
modis_lai_2016_2020_list = []
for yr in range(2016, 2021):
    m_yr = load_modis_lai_year(yr)
    if m_yr is not None:
        modis_lai_2016_2020_list.append(m_yr)
modis_lai_2016_2020 = np.nanmean(np.stack(modis_lai_2016_2020_list, axis=0), axis=0)
print(f"  MODIS LAI 2018 chargé. Moyenne domaine : {np.nanmean(modis_lai_2018[:, landmask_181]):.4f} m2/m2")

# 3. Simulations Noah-MP
print("\n>>> [3/5] Chargement des simulations Noah-MP...")
RUNS_2018 = {
    "OL_DAIC": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": False, "substitut": "ENS_corr"},
    "ENS_OPL": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "ENS_corr": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "DA_nocdf": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-*/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "DA_nocdf_nowilt": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "DA_corr": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}
}
RUNS_PROD = {
    "OPL": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "DA_nocdf": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"},
    "DA_cdf": {"pattern": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output/**/LIS_HIST_*.d01.nc"), "has_lai": True, "substitut": "aucun"}
}

def load_exp_year_data(exp_name, pattern, target_year=2018, read_lai=True):
    t0 = time.time()
    files = sorted(glob.glob(pattern, recursive=True))
    files = [f for f in files if "LIS_HIST_" in f and not f.endswith("0000.d01.nc.tmp")]
    month_files = {m: [] for m in range(1, 13)}
    for f in files:
        fname = os.path.basename(f)
        m = re.search(r"LIS_HIST_(\d{4})(\d{2})(\d{2})", fname)
        if not m: continue
        f_y, f_m, f_d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        ts = pd.Timestamp(year=f_y, month=f_m, day=f_d) - pd.Timedelta(days=1)
        if ts.year == target_year:
            month_files[ts.month].append(f)
    days_in_month = [31, 29 if (target_year % 4 == 0 and (target_year % 100 != 0 or target_year % 400 == 0)) else 28,
                     31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    monthly_esoil, monthly_tveg, monthly_ecanop, monthly_lai = [], [], [], []
    for m in range(1, 13):
        flist = month_files[m]
        n_days = len(flist)
        nd_expected = days_in_month[m - 1]
        if n_days == 0:
            raise FileNotFoundError(f"Missing history files for {exp_name} year {target_year} month {m}")
        sum_es = np.zeros((121, 181), dtype=np.float64)
        sum_tv = np.zeros((121, 181), dtype=np.float64)
        sum_ec = np.zeros((121, 181), dtype=np.float64)
        sum_l = np.zeros((121, 181), dtype=np.float64)
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
        factor = (nd_expected / n_days)
        monthly_esoil.append((sum_es * factor).astype(np.float32))
        monthly_tveg.append((sum_tv * factor).astype(np.float32))
        monthly_ecanop.append((sum_ec * factor).astype(np.float32))
        if has_l:
            monthly_lai.append((sum_l / n_days).astype(np.float32))
        else:
            monthly_lai.append(None)
    monthly_esoil = np.array(monthly_esoil, dtype=np.float32)
    monthly_tveg = np.array(monthly_tveg, dtype=np.float32)
    monthly_ecanop = np.array(monthly_ecanop, dtype=np.float32)
    monthly_lai = np.array(monthly_lai, dtype=np.float32) if not any(x is None for x in monthly_lai) else None
    t1 = time.time()
    print(f"  Exp {exp_name} ({target_year}) : {t1-t0:.2f} s. ESoil: {np.nanmean(np.sum(monthly_esoil, axis=0)[landmask_181]):.1f} mm")
    return {"monthly_esoil": monthly_esoil, "monthly_tveg": monthly_tveg, "monthly_ecanop": monthly_ecanop, "monthly_lai": monthly_lai}

data_2018 = {}
for exp_name, cfg in RUNS_2018.items():
    data_2018[exp_name] = load_exp_year_data(exp_name, cfg["pattern"], target_year=2018, read_lai=cfg["has_lai"])

data_2018["OL_DAIC"]["monthly_lai"] = data_2018["ENS_corr"]["monthly_lai"]

data_prod = {}
for exp_name, cfg in RUNS_PROD.items():
    print(f"  Chargement production {exp_name} (2016-2020)...")
    years_data = [load_exp_year_data(f"{exp_name}_{yr}", cfg["pattern"], target_year=yr, read_lai=True) for yr in range(2016, 2021)]
    m_esoil_prod = np.mean([yd["monthly_esoil"] for yd in years_data], axis=0)
    m_tveg_prod  = np.mean([yd["monthly_tveg"] for yd in years_data], axis=0)
    m_ecanop_prod = np.mean([yd["monthly_ecanop"] for yd in years_data], axis=0)
    m_lai_prod   = np.mean([yd["monthly_lai"] for yd in years_data], axis=0)
    data_prod[exp_name] = {
        "monthly_esoil": m_esoil_prod, "monthly_tveg": m_tveg_prod, "monthly_ecanop": m_ecanop_prod, "monthly_lai": m_lai_prod,
        "by_year": {yr: yd for yr, yd in zip(range(2016, 2021), years_data)}
    }

# 4. PARTIE 1 : LAI Modèle vs MODIS
print("\n>>> [4/5] Traitement Partie 1 : LAI Modèle vs MODIS...")
lai_records = []
all_strats = []
for rname, rmask in REGIONS.items():
    all_strats.append(("region", rname, rmask))
for cname, cmask in LANDCOVER_MASKS.items():
    all_strats.append(("landcover", cname, cmask))

def process_lai_comparison(exp_name, period_label, substitut_label, mod_m_lai, obs_m_lai):
    for stype, sname, smask in all_strats:
        valid_cells = smask & landmask_181 & ~np.isnan(obs_m_lai[0])
        n_valid = int(np.count_nonzero(valid_cells))
        if n_valid == 0: continue
        mod_12 = [float(np.nanmean(mod_m_lai[m][valid_cells])) for m in range(12)]
        obs_12 = [float(np.nanmean(obs_m_lai[m][valid_cells])) for m in range(12)]
        mod_ann, obs_ann = float(np.mean(mod_12)), float(np.mean(obs_12))
        bias_ann = mod_ann - obs_ann
        r_val = stats.pearsonr(mod_12, obs_12)[0] if (np.std(mod_12) > 1e-7 and np.std(obs_12) > 1e-7) else np.nan
        peak_mod = int(np.argmax(mod_12) + 1)
        peak_obs = int(np.argmax(obs_12) + 1)
        rec = {
            "period": period_label, "experiment": exp_name, "substitut": substitut_label,
            "stratification_type": stype, "region_or_class": sname, "n_cells_valid": n_valid,
            "lai_model_annual_mean": round(mod_ann, 4), "lai_modis_annual_mean": round(obs_ann, 4),
            "bias_annual": round(bias_ann, 4), "monthly_correlation": round(r_val, 4) if not np.isnan(r_val) else "absent",
            "peak_month_model": peak_mod, "peak_month_modis": peak_obs
        }
        for m in range(12):
            rec[f"lai_model_m{m+1:02d}"] = round(mod_12[m], 4)
            rec[f"lai_modis_m{m+1:02d}"] = round(obs_12[m], 4)
        lai_records.append(rec)

for exp_name, cfg in RUNS_2018.items():
    process_lai_comparison(exp_name, "2018", cfg["substitut"], data_2018[exp_name]["monthly_lai"], modis_lai_2018)

for exp_name in ["OPL", "DA_nocdf", "DA_cdf"]:
    process_lai_comparison(exp_name, "2016–2020", "aucun", data_prod[exp_name]["monthly_lai"], modis_lai_2016_2020)

df_lai = pd.DataFrame(lai_records)
out_csv_lai = os.path.join(TABLES_DIR, "A1_lai_model_vs_modis.csv")
df_lai.to_csv(out_csv_lai, index=False)
print(f"  [OK] Table A1_lai_model_vs_modis.csv enregistrée ({len(df_lai)} lignes)")

print("  Génération carte de biais annuel 2018 (ENS_corr − MODIS)...")
ens_corr_ann_lai = np.mean(data_2018["ENS_corr"]["monthly_lai"], axis=0)
modis_ann_lai_2018 = np.mean(modis_lai_2018, axis=0)
bias_lai_map_2018_masked = np.where(landmask_181, ens_corr_ann_lai - modis_ann_lai_2018, np.nan)

fig, ax = plt.subplots(figsize=(8, 6), dpi=300)
lon_mesh, lat_mesh = np.meshgrid(lon_181, lat_181)
c = ax.pcolormesh(lon_mesh, lat_mesh, bias_lai_map_2018_masked, cmap="coolwarm", vmin=-1.5, vmax=1.5, shading="auto")
cbar = plt.colorbar(c, ax=ax, orientation="vertical", pad=0.03, shrink=0.85)
cbar.set_label("Biais annuel LAI (ENS_corr − MODIS) [m²/m²]", fontsize=11)
ax.set_title("Carte du biais annuel LAI 2018 (ENS_corr − MODIS)", fontsize=13, fontweight="bold", pad=10)
ax.set_xlabel("Longitude (°E)", fontsize=11)
ax.set_ylabel("Latitude (°N)", fontsize=11)
ax.set_xlim(-10.1, -0.9)
ax.set_ylim(29.9, 36.1)
ax.grid(True, linestyle="--", alpha=0.5)
plt.tight_layout()
out_fig_lai_bias = os.path.join(FIGURES_DIR, "A1_lai_bias_map_2018.png")
plt.savefig(out_fig_lai_bias)
plt.close()
print(f"  [OK] Figure {out_fig_lai_bias} enregistrée")

# 5. PARTIE 2 : Delta LAI dû à l assimilation
print("\n>>> Traitement Partie 2 : ΔLAI dû à l assimilation...")
delta_lai_records = []
contrasts_lai = [
    ("DA_nocdf − ENS_OPL", data_2018["DA_nocdf"]["monthly_lai"] - data_2018["ENS_OPL"]["monthly_lai"]),
    ("DA_corr − ENS_corr", data_2018["DA_corr"]["monthly_lai"] - data_2018["ENS_corr"]["monthly_lai"])
]
for c_label, diff_grid in contrasts_lai:
    for stype, sname, smask in all_strats:
        valid_cells = smask & landmask_181
        n_valid = int(np.count_nonzero(valid_cells))
        if n_valid == 0: continue
        d_12 = [float(np.nanmean(diff_grid[m][valid_cells])) for m in range(12)]
        rec = {
            "period": "2018", "contrast": c_label, "stratification_type": stype, "region_or_class": sname,
            "n_cells_valid": n_valid, "delta_lai_annual_mean": round(float(np.mean(d_12)), 5)
        }
        for m in range(12):
            rec[f"delta_lai_m{m+1:02d}"] = round(d_12[m], 5)
        delta_lai_records.append(rec)

df_delta_lai = pd.DataFrame(delta_lai_records)
out_csv_delta_lai = os.path.join(TABLES_DIR, "A1_delta_lai_assimilation.csv")
df_delta_lai.to_csv(out_csv_delta_lai, index=False)
print(f"  [OK] Table A1_delta_lai_assimilation.csv enregistrée ({len(df_delta_lai)} lignes)")

fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300, sharey=True)
months = list(range(1, 13))
month_labels = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
region_colors = {"Domaine complet": "#1f77b4", "Lalla Chafia": "#ff7f0e", "Sidi Jabeur": "#2ca02c", "Sebou amont": "#d62728"}

for idx, (c_label, _) in enumerate(contrasts_lai):
    ax = axes[idx]
    sub_df = df_delta_lai[(df_delta_lai["contrast"] == c_label) & (df_delta_lai["stratification_type"] == "region")]
    for _, row in sub_df.iterrows():
        rname = row["region_or_class"]
        vals = [row[f"delta_lai_m{m:02d}"] for m in months]
        ax.plot(months, vals, marker="o", label=rname, color=region_colors.get(rname, "black"), linewidth=1.8)
    ax.axhline(0, color="grey", linestyle="--", linewidth=1.0)
    ax.set_title(c_label, fontsize=12, fontweight="bold")
    ax.set_xlabel("Mois de l année 2018", fontsize=11)
    ax.set_xticks(months)
    ax.set_xticklabels(month_labels)
    ax.grid(True, linestyle=":", alpha=0.6)
    if idx == 0:
        ax.set_ylabel("ΔLAI (modèle avec DA − contrôle) [m²/m²]", fontsize=11)
        ax.legend(frameon=True, fontsize=9)

plt.suptitle("Cycle mensuel du ΔLAI dû à l assimilation en 2018", fontsize=13, fontweight="bold", y=0.98)
plt.tight_layout()
out_fig_delta_lai = os.path.join(FIGURES_DIR, "A1_delta_lai_monthly.png")
plt.savefig(out_fig_delta_lai)
plt.close()
print(f"  [OK] Figure {out_fig_delta_lai} enregistrée")

# 6. PARTIE 3 : Partition de l ET et Contrastes C1, C2, C3, C4
print("\n>>> Traitement Partie 3 : Partition de l ET et Contrastes...")
SEASONS = {"DJF": [11, 0, 1], "MAM": [2, 3, 4], "JJA": [5, 6, 7], "SON": [8, 9, 10], "Annuel": list(range(12))}

def aggregate_seasonal(m_flux_12):
    return {sname: np.sum([m_flux_12[idx] for idx in m_indices], axis=0) for sname, m_indices in SEASONS.items()}

et_levels_records = []
def record_levels(exp_name, period_label, exp_data):
    s_es = aggregate_seasonal(exp_data["monthly_esoil"])
    s_tv = aggregate_seasonal(exp_data["monthly_tveg"])
    s_ec = aggregate_seasonal(exp_data["monthly_ecanop"])
    for sname in ["DJF", "MAM", "JJA", "SON", "Annuel"]:
        grid_es, grid_tv, grid_ec = s_es[sname], s_tv[sname], s_ec[sname]
        grid_et = grid_es + grid_tv + grid_ec
        for stype, rname, rmask in all_strats:
            vcells = rmask & landmask_181
            n_val = int(np.count_nonzero(vcells))
            if n_val == 0: continue
            es_val, tv_val, ec_val, et_val = float(np.mean(grid_es[vcells])), float(np.mean(grid_tv[vcells])), float(np.mean(grid_ec[vcells])), float(np.mean(grid_et[vcells]))
            et_levels_records.append({
                "period": period_label, "experiment": exp_name, "season": sname, "stratification_type": stype, "region_or_class": rname,
                "n_cells_valid": n_val, "ESoil_mm": round(es_val, 2), "TVeg_mm": round(tv_val, 2), "ECanop_mm": round(ec_val, 2), "ET_total_mm": round(et_val, 2),
                "fraction_TVeg": round(tv_val / et_val, 4) if et_val > 1e-6 else "absent",
                "fraction_ESoil": round(es_val / et_val, 4) if et_val > 1e-6 else "absent",
                "fraction_ECanop": round(ec_val / et_val, 4) if et_val > 1e-6 else "absent"
            })

for exp_name in RUNS_2018.keys():
    record_levels(exp_name, "2018", data_2018[exp_name])
for exp_name in ["OPL", "DA_nocdf", "DA_cdf"]:
    record_levels(exp_name, "2016–2020", data_prod[exp_name])

df_et_levels = pd.DataFrame(et_levels_records)
out_csv_et_levels = os.path.join(TABLES_DIR, "A1_et_partitioning_levels.csv")
df_et_levels.to_csv(out_csv_et_levels, index=False)
print(f"  [OK] Table A1_et_partitioning_levels.csv enregistrée ({len(df_et_levels)} lignes)")

CONTRASTS = [
    ("C1", "ENS_OPL − OL_DAIC", "ENS_OPL", "OL_DAIC"),
    ("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"),
    ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr"),
    ("C4", "DA_nocdf_nowilt − DA_nocdf", "DA_nocdf_nowilt", "DA_nocdf")
]

et_contrasts_records = []
for cid, clabel, run_a, run_b in CONTRASTS:
    d_es = aggregate_seasonal(data_2018[run_a]["monthly_esoil"] - data_2018[run_b]["monthly_esoil"])
    d_tv = aggregate_seasonal(data_2018[run_a]["monthly_tveg"] - data_2018[run_b]["monthly_tveg"])
    d_ec = aggregate_seasonal(data_2018[run_a]["monthly_ecanop"] - data_2018[run_b]["monthly_ecanop"])
    for sname in ["DJF", "MAM", "JJA", "SON", "Annuel"]:
        grid_des, grid_dtv, grid_dec = d_es[sname], d_tv[sname], d_ec[sname]
        grid_det = grid_des + grid_dtv + grid_dec
        for stype, rname, rmask in all_strats:
            vcells = rmask & landmask_181
            n_val = int(np.count_nonzero(vcells))
            if n_val == 0: continue
            des_val, dtv_val, dec_val, det_val = float(np.mean(grid_des[vcells])), float(np.mean(grid_dtv[vcells])), float(np.mean(grid_dec[vcells])), float(np.mean(grid_det[vcells]))
            et_contrasts_records.append({
                "period": "2018", "contrast_id": cid, "contrast_name": clabel, "season": sname, "stratification_type": stype, "region_or_class": rname,
                "n_cells_valid": n_val, "delta_ESoil_mm": round(des_val, 2), "delta_TVeg_mm": round(dtv_val, 2), "delta_ECanop_mm": round(dec_val, 2), "delta_ET_total_mm": round(det_val, 2)
            })

df_et_contrasts = pd.DataFrame(et_contrasts_records)
out_csv_et_contrasts = os.path.join(TABLES_DIR, "A1_et_partitioning_contrasts.csv")
df_et_contrasts.to_csv(out_csv_et_contrasts, index=False)
print(f"  [OK] Table A1_et_partitioning_contrasts.csv enregistrée ({len(df_et_contrasts)} lignes)")

fig, ax = plt.subplots(figsize=(12, 6), dpi=300)
reg_order = ["Domaine complet", "Lalla Chafia", "Sidi Jabeur", "Sebou amont"]
c_order = ["C1", "C2", "C3", "C4"]
c_labels = {"C1": "C1 (ENS_OPL − OL_DAIC)", "C2": "C2 (DA_nocdf − ENS_OPL)", "C3": "C3 (DA_corr − ENS_corr)", "C4": "C4 (DA_nocdf_nowilt − DA_nocdf)"}
n_groups, n_contrasts = len(reg_order), len(c_order)
bar_width = 0.18
x = np.arange(n_groups)

for i, cid in enumerate(c_order):
    sub = df_et_contrasts[(df_et_contrasts["contrast_id"] == cid) & (df_et_contrasts["season"] == "Annuel") & (df_et_contrasts["stratification_type"] == "region")]
    sub = sub.set_index("region_or_class").reindex(reg_order)
    pos = x + (i - (n_contrasts - 1) / 2.0) * bar_width
    vals = sub["delta_ET_total_mm"].values
    bars = ax.bar(pos, vals, width=bar_width * 0.88, label=c_labels[cid], alpha=0.88)
    for rect, val in zip(bars, vals):
        h = rect.get_height()
        va = "bottom" if h >= 0 else "top"
        ax.annotate(f"{val:+.1f}", xy=(rect.get_x() + rect.get_width() / 2, h), xytext=(0, 3 if h >= 0 else -3), textcoords="offset points", ha="center", va=va, fontsize=8)

ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
ax.set_xticks(x)
ax.set_xticklabels(reg_order, fontsize=11)
ax.set_ylabel("ΔET annuel total (mm/an)", fontsize=11)
ax.set_title("Décomposition des contrastes annuels 2018 (C1, C2, C3, C4)", fontsize=13, fontweight="bold", pad=12)
ax.legend(frameon=True, fontsize=10, loc="upper right")
ax.grid(True, linestyle=":", alpha=0.5, axis="y")
plt.tight_layout()
out_fig_et_contrasts = os.path.join(FIGURES_DIR, "A1_et_partitioning_contrasts.png")
plt.savefig(out_fig_et_contrasts)
plt.close()
print(f"  [OK] Figure {out_fig_et_contrasts} enregistrée")

# 7. PARTIE 4 : WaPOR v3 (2018-2020)
print("\n>>> Traitement Partie 4 : Évaluation contre WaPOR v3...")
lon_0_w = -7.500932622398005
lat_0_w = 36.02244289319281
d_w = 0.002245788210298804

def aggregate_wapor(tif_path):
    if not os.path.exists(tif_path): return None, None
    raw_img = tifffile.imread(tif_path)
    w_h, w_w = raw_img.shape
    agg_grid = np.full((121, 181), np.nan, dtype=np.float32)
    cov_mask = np.zeros((121, 181), dtype=bool)
    for j in range(121):
        lat_c = lat_181[j]
        r0 = int(np.floor((lat_0_w - (lat_c + 0.025)) / d_w))
        r1 = int(np.ceil((lat_0_w - (lat_c - 0.025)) / d_w))
        if r0 < 0 or r1 > w_h or r0 >= r1: continue
        for i in range(181):
            if not landmask_181[j, i]: continue
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

wapor_annual = {}
for yr in [2018, 2019, 2020]:
    f_e = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/WaPOR/WaPOR_v3_E/WaPOR_v3_E_{yr}.tif")
    f_t = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/WaPOR/WaPOR_v3_T/WaPOR_v3_T_{yr}.tif")
    g_e, m_e = aggregate_wapor(f_e)
    g_t, m_t = aggregate_wapor(f_t)
    wapor_annual[yr] = {"E": g_e, "T": g_t, "valid_mask": (m_e & m_t) if (m_e is not None and m_t is not None) else None}
    cnt = np.count_nonzero(wapor_annual[yr]["valid_mask"])
    print(f"  WaPOR v3 {yr} : {cnt} mailles retenues (>= 80%)")

wapor_comparison_records = []
def evaluate_wapor(exp_name, period_label, mod_es, mod_tv, mod_ec, w_e, w_t, w_mask):
    for stype, sname, smask in all_strats:
        valid_cells = smask & landmask_181 & w_mask
        n_valid = int(np.count_nonzero(valid_cells))
        if n_valid == 0:
            wapor_comparison_records.append({
                "period": period_label, "experiment": exp_name, "season": "Annuel", "stratification_type": stype, "region_or_class": sname,
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
        wp_e, wp_t = w_e[valid_cells], w_t[valid_cells]
        wp_comb = wp_e + wp_t
        wapor_comparison_records.append({
            "period": period_label, "experiment": exp_name, "season": "Annuel", "stratification_type": stype, "region_or_class": sname,
            "n_cells_valid": n_valid, "status": "calcule",
            "ESoil_model_mm": round(float(np.mean(m_e)), 2), "E_wapor_mm": round(float(np.mean(wp_e)), 2),
            "bias_E_mm": round(float(np.mean(m_e - wp_e)), 2), "abs_bias_E_mm": round(float(np.mean(np.abs(m_e - wp_e))), 2),
            "TVeg_model_mm": round(float(np.mean(m_t)), 2), "T_wapor_mm": round(float(np.mean(wp_t)), 2),
            "bias_T_mm": round(float(np.mean(m_t - wp_t)), 2), "abs_bias_T_mm": round(float(np.mean(np.abs(m_t - wp_t))), 2),
            "ETcomb_model_mm": round(float(np.mean(m_comb)), 2), "ETcomb_wapor_mm": round(float(np.mean(wp_comb)), 2),
            "bias_ETcomb_mm": round(float(np.mean(m_comb - wp_comb)), 2), "abs_bias_ETcomb_mm": round(float(np.mean(np.abs(m_comb - wp_comb))), 2),
            "ECanop_model_mm": round(float(np.mean(m_c)), 2), "I_wapor_mm": "absent", "bias_ECanop_mm": "absent", "abs_bias_ECanop_mm": "absent",
            "AETI_total_model_mm": round(float(np.mean(m_e + m_t + m_c)), 2), "AETI_total_wapor_mm": "absent", "bias_AETI_mm": "absent",
            "ratio_T_over_ETcomb_model": round(float(np.mean(m_t / np.where(m_comb > 1e-6, m_comb, np.nan))), 4),
            "ratio_T_over_ETcomb_wapor": round(float(np.mean(wp_t / np.where(wp_comb > 1e-6, wp_comb, np.nan))), 4),
            "monthly_correlation": "absent (WaPOR v3 mensuel non archive)"
        })
    for s_miss in ["DJF", "MAM", "JJA", "SON"]:
        wapor_comparison_records.append({
            "period": period_label, "experiment": exp_name, "season": s_miss, "stratification_type": "region", "region_or_class": "Domaine complet",
            "n_cells_valid": 0, "status": "absent (WaPOR v3 dekadaire/mensuel non archive sur disque)",
            "ESoil_model_mm": "absent", "E_wapor_mm": "absent", "bias_E_mm": "absent", "abs_bias_E_mm": "absent",
            "TVeg_model_mm": "absent", "T_wapor_mm": "absent", "bias_T_mm": "absent", "abs_bias_T_mm": "absent",
            "ETcomb_model_mm": "absent", "ETcomb_wapor_mm": "absent", "bias_ETcomb_mm": "absent", "abs_bias_ETcomb_mm": "absent",
            "ECanop_model_mm": "absent", "I_wapor_mm": "absent", "bias_ECanop_mm": "absent", "abs_bias_ECanop_mm": "absent",
            "AETI_total_model_mm": "absent", "AETI_total_wapor_mm": "absent", "bias_AETI_mm": "absent",
            "ratio_T_over_ETcomb_model": "absent", "ratio_T_over_ETcomb_wapor": "absent", "monthly_correlation": "absent"
        })

for exp_name in RUNS_2018.keys():
    evaluate_wapor(exp_name, "2018", np.sum(data_2018[exp_name]["monthly_esoil"], axis=0),
                   np.sum(data_2018[exp_name]["monthly_tveg"], axis=0), np.sum(data_2018[exp_name]["monthly_ecanop"], axis=0),
                   wapor_annual[2018]["E"], wapor_annual[2018]["T"], wapor_annual[2018]["valid_mask"])

for exp_name in ["OPL", "DA_nocdf", "DA_cdf"]:
    es_18_20 = np.mean([np.sum(data_prod[exp_name]["by_year"][yr]["monthly_esoil"], axis=0) for yr in [2018, 2019, 2020]], axis=0)
    tv_18_20 = np.mean([np.sum(data_prod[exp_name]["by_year"][yr]["monthly_tveg"], axis=0) for yr in [2018, 2019, 2020]], axis=0)
    ec_18_20 = np.mean([np.sum(data_prod[exp_name]["by_year"][yr]["monthly_ecanop"], axis=0) for yr in [2018, 2019, 2020]], axis=0)
    we_18_20 = np.mean([wapor_annual[yr]["E"] for yr in [2018, 2019, 2020]], axis=0)
    wt_18_20 = np.mean([wapor_annual[yr]["T"] for yr in [2018, 2019, 2020]], axis=0)
    wmask_18_20 = wapor_annual[2018]["valid_mask"] & wapor_annual[2019]["valid_mask"] & wapor_annual[2020]["valid_mask"]
    evaluate_wapor(exp_name, "2018–2020", es_18_20, tv_18_20, ec_18_20, we_18_20, wt_18_20, wmask_18_20)

df_wapor_comp = pd.DataFrame(wapor_comparison_records)
out_csv_wapor_comp = os.path.join(TABLES_DIR, "A1_wapor_et_comparison.csv")
df_wapor_comp.to_csv(out_csv_wapor_comp, index=False)
print(f"  [OK] Table A1_wapor_et_comparison.csv enregistrée ({len(df_wapor_comp)} lignes)")

print("  Calcul direction de changement pour C2 et C3 contre WaPOR v3...")
doc_records = []
contrasts_doc = [("C2", "DA_nocdf − ENS_OPL", "DA_nocdf", "ENS_OPL"), ("C3", "DA_corr − ENS_corr", "DA_corr", "ENS_corr")]
w_e_18 = wapor_annual[2018]["E"]
w_t_18 = wapor_annual[2018]["T"]
w_comb_18 = w_e_18 + w_t_18
w_mask_18 = wapor_annual[2018]["valid_mask"]

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
out_csv_doc = os.path.join(TABLES_DIR, "A1_wapor_direction_of_change.csv")
df_doc.to_csv(out_csv_doc, index=False)
print(f"  [OK] Table A1_wapor_direction_of_change.csv enregistrée ({len(df_doc)} lignes)")

fig, axes = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
ax1 = axes[0]
sub_doc_dom = df_doc[(df_doc["stratification_type"] == "region") & (df_doc["region_or_class"] == "Domaine complet")]
x_pos, width = np.arange(3), 0.35
c2_vals = sub_doc_dom[sub_doc_dom["contrast_id"] == "C2"]["delta_abs_bias_mm"].values
c3_vals = sub_doc_dom[sub_doc_dom["contrast_id"] == "C3"]["delta_abs_bias_mm"].values
comp_labels = ["E (ESoil)", "T (TVeg)", "E+T combiné"]
ax1.bar(x_pos - width/2, c2_vals, width, label="C2 (DA_nocdf − ENS_OPL)", color="#1f77b4", alpha=0.85)
ax1.bar(x_pos + width/2, c3_vals, width, label="C3 (DA_corr − ENS_corr)", color="#2ca02c", alpha=0.85)
ax1.axhline(0, color="black", linestyle="--", linewidth=0.8)
ax1.set_xticks(x_pos)
ax1.set_xticklabels(comp_labels, fontsize=10)
ax1.set_ylabel("Δ|biais| moyen (mm/an) [négatif = amélioration]", fontsize=10)
ax1.set_title("Variation du biais absolu moyen (Domaine)", fontsize=11, fontweight="bold")
ax1.legend(frameon=True, fontsize=9)
ax1.grid(True, linestyle=":", alpha=0.5, axis="y")

ax2 = axes[1]
c2_pct = sub_doc_dom[sub_doc_dom["contrast_id"] == "C2"]["pct_cells_closer"].values
c3_pct = sub_doc_dom[sub_doc_dom["contrast_id"] == "C3"]["pct_cells_closer"].values
ax2.bar(x_pos - width/2, c2_pct, width, label="C2 (DA_nocdf − ENS_OPL)", color="#1f77b4", alpha=0.85)
ax2.bar(x_pos + width/2, c3_pct, width, label="C3 (DA_corr − ENS_corr)", color="#2ca02c", alpha=0.85)
ax2.axhline(50, color="red", linestyle=":", linewidth=1.0, label="Seuil de parité (50 %)")
ax2.set_xticks(x_pos)
ax2.set_xticklabels(comp_labels, fontsize=10)
ax2.set_ylabel("% de mailles se rapprochant de WaPOR v3", fontsize=10)
ax2.set_title("Pourcentage de mailles avec réduction du biais (Domaine)", fontsize=11, fontweight="bold")
ax2.set_ylim(0, 100)
ax2.legend(frameon=True, fontsize=9)
ax2.grid(True, linestyle=":", alpha=0.5, axis="y")
plt.suptitle("Impact de l assimilation sur l accord avec WaPOR v3 en 2018", fontsize=13, fontweight="bold", y=0.98)
plt.tight_layout()
out_fig_wapor = os.path.join(FIGURES_DIR, "A1_wapor_direction_of_change.png")
plt.savefig(out_fig_wapor)
plt.close()
print(f"  [OK] Figure {out_fig_wapor} enregistrée")

# 8. GÉNÉRATION DU RAPPORT REPORT_A1.md
print("\n>>> Génération du rapport factuel REPORT_A1.md...")
cnt_lc = np.count_nonzero(REGIONS["Lalla Chafia"])
cnt_sj = np.count_nonzero(REGIONS["Sidi Jabeur"])
cnt_sa = np.count_nonzero(REGIONS["Sebou amont"])
cnt_wp = np.count_nonzero(wapor_annual[2018]["valid_mask"])
n_land = np.count_nonzero(landmask_181)

rep_lines = [
    "# Rapport d Étape A1 — Végétation et partition de l ET (H1)",
    "",
    "Ce rapport présente les résultats quantitatifs de l étape A1, sans interprétation subjective ni spéculation.",
    "Tous les chiffres sont issus des scripts de post-traitement sur les sorties de simulation LIS et les observations MODIS LAI et WaPOR v3.",
    "",
    "## 1. Méthodes d Agrégation et Données",
    "",
    "### 1.1 Grille et Masques",
    "- **Grille LIS NorthMor** : 121 rangées × 181 colonnes (résolution 0,05°, domaine 30,0°N à 36,0°N, 10,0°O à 1,0°O).",
    f"- **Nombre total de mailles terrestres (LANDMASK=1)** : {n_land} mailles.",
    f"- **Bassin de Lalla Chafia** : {cnt_lc} mailles.",
    f"- **Bassin de Sidi Jabeur** : {cnt_sj} mailles.",
    f"- **Bassin de Sebou amont** : {cnt_sa} mailles.",
    "",
    "### 1.2 Occupation du Sol (MODIS-IGBP NCEP-modified)",
    "Classes dominantes présentes sur le domaine terrestre :",
]
for lc_id in unique_lc:
    cname = LANDCOVER_NAMES.get(lc_id, f"Classe_{lc_id}")
    label = f"Classe {lc_id} - {cname}"
    n_pix = np.count_nonzero(LANDCOVER_MASKS[label])
    pct = n_pix / np.count_nonzero(landmask_181) * 100.0
    rep_lines.append(f"- **{label}** : {n_pix} mailles ({pct:.2f} %)")

rep_lines.extend([
    "",
    "### 1.3 MODIS LAI (MCD15A2H.006)",
    "- **Résolution native** : ~500 m (1/240°).",
    "- **Agrégation spatiale** : blocs de 12 × 12 pixels sur chaque maille 5 km LIS (moyenne des pixels valides avec QC <= 100, facteur d échelle 0,1).",
    "- **Agrégation temporelle** : composites 8 jours groupés par mois civil (selon la date centrale du composite) pour chaque mois de 2018 (46 fichiers) et de 2016–2020.",
    "- **Règle pour OL_DAIC** : la variable `LAI_tavg` n a pas été demandée en sortie (fichier MODEL_OUTPUT_LIST hourly). Selon l instruction, les valeurs de `ENS_corr` sont utilisées comme substitut factuel et explicitement indiquées par la mention `substitut=ENS_corr`.",
    "",
    "### 1.4 WaPOR v3 (2018–2020)",
    "- **Résolution native** : ~250 m (0,002246°).",
    "- **Emprise archivée** : Longitudes -7,50° à -2,99° ; Latitudes 32,00° à 36,02° (Nord du Maroc).",
    f"- **Règle de rétention** : moyenne des pixels 250 m valides dans la maille LIS 5 km, cellule retenue uniquement si la couverture de pixels valides est ≥ 80 %.",
    f"- **Nombre de cellules retenues sur la grille LIS (couverture ≥ 80 %)** : {cnt_wp} mailles.",
    "- **Disponibilité temporelle** : rasters annuels (2018, 2019, 2020) pour AETI, E, T, NPP. Les fichiers dékadaires et mensuels ne sont pas archivés sur disque.",
    "- **Interception et AETI** : la composante interception (I) de WaPOR v3 n étant pas disponible sur disque, ECanop et AETI total ne sont pas comparés et portent la mention `absent`.",
    "- **Métriques mensuelles/saisonnières** : en l absence de fichiers dékadaires ou mensuels sur disque, ces métriques portent la mention `absent (WaPOR v3 dékadaire non archivé sur disque)`.",
    "",
    "---",
    "",
    "## 2. Tableaux Récapitulatifs Factuels",
    "",
    "### 2.1 Synthèse LAI Modèle vs MODIS en 2018 (Domaine et Bassins)",
    ""
])

sub_t1 = df_lai[(df_lai["period"] == "2018") & (df_lai["stratification_type"] == "region")]
cols_t1 = ["experiment", "substitut", "region_or_class", "lai_model_annual_mean", "lai_modis_annual_mean", "bias_annual", "monthly_correlation", "peak_month_model", "peak_month_modis"]
rep_lines.append(df_to_markdown_simple(sub_t1[cols_t1]))

rep_lines.extend(["", "### 2.2 ΔLAI dû à l Assimilation en 2018 (Domaine et Bassins)", ""])
sub_t2 = df_delta_lai[(df_delta_lai["period"] == "2018") & (df_delta_lai["stratification_type"] == "region")]
cols_t2 = ["contrast", "region_or_class", "delta_lai_annual_mean", "delta_lai_m01", "delta_lai_m04", "delta_lai_m07", "delta_lai_m10"]
rep_lines.append(df_to_markdown_simple(sub_t2[cols_t2]))

rep_lines.extend(["", "### 2.3 Partition Annuelle de l ET en 2018 (Domaine et Bassins)", ""])
sub_t3 = df_et_levels[(df_et_levels["period"] == "2018") & (df_et_levels["season"] == "Annuel") & (df_et_levels["stratification_type"] == "region")]
cols_t3 = ["experiment", "region_or_class", "ESoil_mm", "TVeg_mm", "ECanop_mm", "ET_total_mm", "fraction_TVeg", "fraction_ESoil", "fraction_ECanop"]
rep_lines.append(df_to_markdown_simple(sub_t3[cols_t3]))

rep_lines.extend(["", "### 2.4 Contrastes Annuels C1, C2, C3, C4 Décomposés par Composante (2018)", ""])
sub_t4 = df_et_contrasts[(df_et_contrasts["season"] == "Annuel") & (df_et_contrasts["stratification_type"] == "region")]
cols_t4 = ["contrast_id", "contrast_name", "region_or_class", "delta_ESoil_mm", "delta_TVeg_mm", "delta_ECanop_mm", "delta_ET_total_mm"]
rep_lines.append(df_to_markdown_simple(sub_t4[cols_t4]))

rep_lines.extend(["", "### 2.5 Comparaison Annuelle contre WaPOR v3 en 2018 (Domaine et Bassins)", ""])
sub_t5 = df_wapor_comp[(df_wapor_comp["period"] == "2018") & (df_wapor_comp["season"] == "Annuel") & (df_wapor_comp["stratification_type"] == "region")]
cols_t5 = ["experiment", "region_or_class", "n_cells_valid", "ESoil_model_mm", "E_wapor_mm", "bias_E_mm", "TVeg_model_mm", "T_wapor_mm", "bias_T_mm", "ETcomb_model_mm", "ETcomb_wapor_mm", "bias_ETcomb_mm", "ratio_T_over_ETcomb_model", "ratio_T_over_ETcomb_wapor"]
rep_lines.append(df_to_markdown_simple(sub_t5[cols_t5]))

rep_lines.extend(["", "### 2.6 Direction de Changement pour C2 et C3 contre WaPOR v3 en 2018", ""])
sub_t6 = df_doc[(df_doc["stratification_type"] == "region")]
cols_t6 = ["contrast_id", "contrast_name", "component", "region_or_class", "n_cells_valid", "delta_abs_bias_mm", "pct_cells_closer", "pct_cells_farther", "pct_cells_neutral"]
rep_lines.append(df_to_markdown_simple(sub_t6[cols_t6]))

rep_lines.extend([
    "", "---", "", "## 3. Liste des Fichiers Produits", "",
    "### Tables CSV :",
    "- `paper1/tables/A1_lai_model_vs_modis.csv`",
    "- `paper1/tables/A1_delta_lai_assimilation.csv`",
    "- `paper1/tables/A1_et_partitioning_levels.csv`",
    "- `paper1/tables/A1_et_partitioning_contrasts.csv`",
    "- `paper1/tables/A1_wapor_et_comparison.csv`",
    "- `paper1/tables/A1_wapor_direction_of_change.csv`",
    "", "### Figures PNG :",
    "- `paper1/figures/A1_lai_bias_map_2018.png`",
    "- `paper1/figures/A1_delta_lai_monthly.png`",
    "- `paper1/figures/A1_et_partitioning_contrasts.png`",
    "- `paper1/figures/A1_wapor_direction_of_change.png`",
    "", "### Scripts :",
    "- `scripts/paper1/step_a1_vegetation_et_partition.py`",
    "- `paper1/scripts/step_a1_vegetation_et_partition.py`",
    ""
])

with open(REPORT_PATH, "w", encoding="utf-8") as f_rep:
    f_rep.write("\n".join(rep_lines))

print(f"  [OK] Rapport {REPORT_PATH} généré")
os.system("cp scripts/paper1/step_a1_vegetation_et_partition.py paper1/scripts/step_a1_vegetation_et_partition.py")
print("  [OK] Script copié dans paper1/scripts/")
print("=" * 80)
