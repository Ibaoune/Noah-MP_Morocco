#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Verification approfondie des debits simules par DA_nocdf a Lalla Chafia (Lot 2b).
Objectif : determiner et documenter factuellement si la surestimation de debit
a Lalla Chafia (35.90 m3/s simule vs 9.74 m3/s observe) provient du routage,
du remapping ou de la production de ruissellement sous-surfacique (Qsb) par Noah-MP.

Sorties produites :
  - paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv
  - paper1/tables/monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv
  - paper1/tables/water_balance_upstream_catchments_2018.csv
  - paper1/tables/da_nocdf_annual_runoff_catchment_2016_2020.csv
  - paper1/tables/remap_runoff_check_lalla_chafia_2018.csv
  - paper1/tables/top20_cells_qsb_difference.csv
  - paper1/figures/fig_control_daily_streamflow_log.png (.pdf)
  - paper1/figures/fig_map_qsb_difference_da_minus_ens.png (.pdf)
"""

import os
import sys
import glob
import datetime
import numpy as np
import pandas as pd
import netCDF4 as nc
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
LIS_INPUT_181 = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
CACHE_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/routing/cache_streamflow_2018")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)

# 1. Delimitation du bassin amont HyMAP D8
def get_catchment_cells(ldt_path, outlet_row, outlet_col):
    with nc.Dataset(ldt_path) as ds:
        flow_x = ds['HYMAP_flow_direction_x'][:]
        flow_y = ds['HYMAP_flow_direction_y'][:]
        area = ds['HYMAP_grid_area'][:].filled(0.0)
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
                if (pr, pc) not in parents:
                    parents[(pr, pc)] = []
                parents[(pr, pc)].append((r, c))

    vis = set([(outlet_row, outlet_col)])
    q = [(outlet_row, outlet_col)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis, area

print(">>> 1. Delimitation des bassins versants amont...")
cells_lalla, area_180 = get_catchment_cells(LDT_FILE, 75, 71)
cells_jabeur, _ = get_catchment_cells(LDT_FILE, 71, 71)
area_lalla_km2 = sum(area_180[r, c] for r, c in cells_lalla) / 1e6
area_jabeur_km2 = sum(area_180[r, c] for r, c in cells_jabeur) / 1e6

print(f"  Lalla Chafia : {len(cells_lalla)} mailles, Superficie = {area_lalla_km2:.2f} km2 (Table = 3341.60 km2)")
print(f"  Sidi Jabeur  : {len(cells_jabeur)} mailles, Superficie = {area_jabeur_km2:.2f} km2 (Table = 3138.52 km2)")

# Masque booleen 180x120
mask_lalla_180 = np.zeros((120, 180), dtype=bool)
for r, c in cells_lalla:
    mask_lalla_180[r, c] = True

mask_jabeur_180 = np.zeros((120, 180), dtype=bool)
for r, c in cells_jabeur:
    mask_jabeur_180[r, c] = True

# Poids pour la projection 181x121
weights_lalla_181 = np.zeros((121, 181), dtype=float)
for r, c in cells_lalla:
    weights_lalla_181[r, c] += 0.25
    weights_lalla_181[r, c+1] += 0.25
    weights_lalla_181[r+1, c] += 0.25
    weights_lalla_181[r+1, c+1] += 0.25

weights_jabeur_181 = np.zeros((121, 181), dtype=float)
for r, c in cells_jabeur:
    weights_jabeur_181[r, c] += 0.25
    weights_jabeur_181[r, c+1] += 0.25
    weights_jabeur_181[r+1, c] += 0.25
    weights_jabeur_181[r+1, c+1] += 0.25

# 2. Séries journalières et mensuelles 2018
print("\n>>> 2. Assemblage des debits journaliers et mensuels 2018...")
df_obs = pd.read_csv(os.path.join(BASE_DIR, "data/streamflow_clean/obs_daily.csv"))
df_obs["year"] = pd.to_datetime(df_obs["date"]).dt.year
obs_2018 = df_obs[df_obs["year"] == 2018]
obs_lalla = obs_2018[obs_2018["station_id"] == "b_l_chafia"].set_index("date")["q_m3s"]
obs_jabeur = obs_2018[obs_2018["station_id"] == "b_s_jabeur"].set_index("date")["q_m3s"]

exps = ["OPL", "OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]
daily_dict = {"date": pd.date_range("2018-01-01", "2018-12-31").strftime("%Y-%m-%d")}
df_daily = pd.DataFrame(daily_dict)

df_daily["obs_lalla_chafia"] = df_daily["date"].map(obs_lalla)
df_daily["obs_sidi_jabeur"] = df_daily["date"].map(obs_jabeur)

for exp in exps:
    cache_f = os.path.join(CACHE_DIR, f"streamflow_2018_{exp}.csv")
    df_c = pd.read_csv(cache_f).set_index("date")
    df_daily[f"{exp}_lalla_chafia"] = df_daily["date"].map(df_c["b_l_chafia"])
    df_daily[f"{exp}_sidi_jabeur"] = df_daily["date"].map(df_c["b_s_jabeur"])

out_daily_csv = os.path.join(TABLES_DIR, "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
df_daily.to_csv(out_daily_csv, index=False)
print(f"  [OK] CSV journalier sauve : {out_daily_csv}")

# Calcul mensuel
df_daily["year_month"] = pd.to_datetime(df_daily["date"]).dt.strftime("%Y-%m")
m_records = []
for ym, grp in df_daily.groupby("year_month"):
    for st_id, st_name in [("lalla_chafia", "Lalla Chafia"), ("sidi_jabeur", "Sidi Jabeur")]:
        rec = {"station": st_name, "station_id": st_id, "year_month": ym}
        rec["obs"] = grp[f"obs_{st_id}"].mean()
        for exp in exps:
            rec[exp] = grp[f"{exp}_{st_id}"].mean()
        m_records.append(rec)

df_monthly = pd.DataFrame(m_records)
out_monthly_csv = os.path.join(TABLES_DIR, "monthly_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
df_monthly.to_csv(out_monthly_csv, index=False)
print(f"  [OK] CSV mensuel sauve : {out_monthly_csv}")

# Figure de controle echelle log
print("\n>>> 3. Generation de la figure de controle (echelle log)...")
fig, axes = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
dates_dt = pd.to_datetime(df_daily["date"]).dt.to_pydatetime()

colors = {
    "obs": "black", "OPL": "#1f77b4", "OL_DAIC": "#2ca02c",
    "ENS_OPL": "#ff7f0e", "DA_nocdf": "#d62728", "DA_cdf": "#9467bd",
    "DA_nocdf_nowilt": "#8c564b"
}

for ax, st_id, st_name in zip(axes, ["lalla_chafia", "sidi_jabeur"], ["Lalla Chafia (Bouregreg)", "Sidi Jabeur (Grou)"]):
    ax.plot(dates_dt, np.asarray(df_daily[f"obs_{st_id}"]), label="Observed (ABH)", color=colors["obs"], linewidth=1.8, zorder=5)
    ax.plot(dates_dt, np.asarray(df_daily[f"OPL_{st_id}"]), label="OPL (linres=0)", color=colors["OPL"], linewidth=1.2, alpha=0.85)
    ax.plot(dates_dt, np.asarray(df_daily[f"OL_DAIC_{st_id}"]), label="OL_DAIC (linres=0)", color=colors["OL_DAIC"], linewidth=1.2, alpha=0.85)
    ax.plot(dates_dt, np.asarray(df_daily[f"ENS_OPL_{st_id}"]), label="ENS_OPL (linres=0, 20m)", color=colors["ENS_OPL"], linewidth=1.2, alpha=0.85)
    ax.plot(dates_dt, np.asarray(df_daily[f"DA_nocdf_{st_id}"]), label="DA_nocdf (linres=0)", color=colors["DA_nocdf"], linewidth=1.6, zorder=4)
    ax.plot(dates_dt, np.asarray(df_daily[f"DA_cdf_{st_id}"]), label="DA_cdf (linres=0)", color=colors["DA_cdf"], linewidth=1.2, alpha=0.85)
    ax.plot(dates_dt, np.asarray(df_daily[f"DA_nocdf_nowilt_{st_id}"]), label="DA_nocdf_nowilt (linres=0)", color=colors["DA_nocdf_nowilt"], linestyle="--", linewidth=1.2, alpha=0.85)
    
    ax.set_yscale("log")
    ax.set_ylim(0.01, 400)
    ax.set_ylabel("Daily Streamflow [m³/s] (log scale)", fontsize=11)
    ax.set_title(f"2018 Daily Hydrograph Control — {st_name}", fontsize=12, fontweight="bold")
    ax.grid(True, which="both", linestyle=":", alpha=0.6)
    ax.legend(loc="upper left", ncol=4, fontsize=9, framealpha=0.9)

axes[1].set_xlabel("Date (2018)", fontsize=11)
axes[1].xaxis.set_major_locator(mdates.MonthLocator())
axes[1].xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
plt.tight_layout()

fig_png = os.path.join(FIGURES_DIR, "fig_control_daily_streamflow_log.png")
fig_pdf = os.path.join(FIGURES_DIR, "fig_control_daily_streamflow_log.pdf")
plt.savefig(fig_png, dpi=300)
plt.savefig(fig_pdf)
plt.close()
print(f"  [OK] Figure de controle sauvee : {fig_png} et {fig_pdf}")

# 4. Bilan mensuel sur le bassin amont reel de chaque station
print("\n>>> 4. Calcul du bilan mensuel sur les bassins versants amont...")
# Epaisseurs et masque
dz = np.array([0.1, 0.3, 0.6, 1.0])

# Repertoires des simulations
RUN_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018"),
}

# Fonction extraction flux sur mailles amont (remapped 180x120)
def extract_catchment_monthly_fluxes(exp_key, basin_mask_180, area_weights_180):
    remap_dir = os.path.join(BASE_DIR, f"experiments/NorthMor/routing/runoff_remap_180x120")
    if exp_key == "OPL":
        sub_dir = os.path.join(remap_dir, "OPL_noirr_2016_2020/SURFACEMODEL")
    elif exp_key == "DA_nocdf":
        sub_dir = os.path.join(remap_dir, "DA_nocdf_noirr_2016_2020/SURFACEMODEL")
    elif exp_key == "DA_cdf":
        sub_dir = os.path.join(remap_dir, "DA_cdf_noirr_2016_2020/SURFACEMODEL")
    else:
        sub_dir = os.path.join(remap_dir, f"{exp_key}/SURFACEMODEL")

    tot_area = np.sum(area_weights_180[basin_mask_180])
    w = area_weights_180 / tot_area

    months_data = []
    for m in range(1, 13):
        ym = f"2018{m:02d}"
        files = sorted(glob.glob(os.path.join(sub_dir, f"{ym}/*.d01.nc")))
        # Note : le premier jour du mois m+1 contient le flux du dernier jour de m
        m_next = f"2018{m+1:02d}" if m < 12 else "201901"
        f_last = os.path.join(sub_dir, f"{m_next}/LIS_HIST_{m_next}010000.d01.nc")
        if os.path.exists(f_last) and f_last not in files:
            files.append(f_last)

        qs_sum = 0.0
        qsb_sum = 0.0
        for f in files:
            fname = os.path.basename(f)
            if not fname.startswith("LIS_HIST_"):
                continue
            with nc.Dataset(f) as ds:
                qs = np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb = np.squeeze(ds["Qsb_tavg"][:]) * 86400.0
                qs_sum += float(np.sum(qs[basin_mask_180] * w[basin_mask_180]))
                qsb_sum += float(np.sum(qsb[basin_mask_180] * w[basin_mask_180]))
        months_data.append((qs_sum, qsb_sum))
    return months_data

# Lecture P et ET sur grille native 181x121 projetee
def extract_native_monthly_p_et(exp_key, weights_181):
    w_norm = weights_181 / np.sum(weights_181)
    exp_dir = RUN_DIRS[exp_key]
    
    months_p_et = []
    for m in range(1, 13):
        m_label = f"2018-{m:02d}"
        ym = f"2018{m:02d}"
        # Recherche fichiers
        if exp_key in ["OPL", "DA_nocdf", "DA_cdf"]:
            f_dir = os.path.join(exp_dir, f"output/{m_label}/SURFACEMODEL/{ym}")
        else:
            f_dir = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}")
        
        files = sorted(glob.glob(os.path.join(f_dir, "LIS_HIST_*.d01.nc")))
        m_next = f"2018{m+1:02d}" if m < 12 else "201901"
        if exp_key in ["OPL", "DA_nocdf", "DA_cdf"]:
            m_next_label = f"2018-{m+1:02d}" if m < 12 else "2019-01"
            f_last = os.path.join(exp_dir, f"output/{m_next_label}/SURFACEMODEL/{m_next}/LIS_HIST_{m_next}010000.d01.nc")
        else:
            f_last = os.path.join(exp_dir, f"output/SURFACEMODEL/{m_next}/LIS_HIST_{m_next}010000.d01.nc")
            if not os.path.exists(f_last) and m == 5:
                # Fichier 31 mai dans hang
                f_last = os.path.join(exp_dir, f"output/_partial_201806_hang/SURFACEMODEL_{m_next}/LIS_HIST_{m_next}010000.d01.nc")

        if os.path.exists(f_last) and f_last not in files:
            files.append(f_last)

        p_sum, et_sum = 0.0, 0.0
        for f in files:
            with nc.Dataset(f) as ds:
                p_val = ds["TotalPrecip_tavg"][:].squeeze() * 86400.0 if "TotalPrecip_tavg" in ds.variables else np.zeros((121, 181))
                et_val = ds["Evap_tavg"][:].squeeze() * 86400.0
                p_sum += float(np.sum(p_val * w_norm))
                et_sum += float(np.sum(et_val * w_norm))
        months_p_et.append((p_sum, et_sum))
    return months_p_et

# Extraction des increments EnKF par couche pour DA_nocdf et DA_nocdf_nowilt
def extract_catchment_enkf_increments(exp_key, weights_181):
    w_norm = weights_181 / np.sum(weights_181)
    exp_dir = RUN_DIRS[exp_key]
    
    monthly_incrs = []
    for m in range(1, 13):
        m_label = f"2018-{m:02d}"
        ym = f"2018{m:02d}"
        if exp_key == "DA_nocdf":
            pat = os.path.join(exp_dir, f"output/{m_label}/EnKF/{ym}/LIS_DA_EnKF_*_incr.a01.d01.nc")
        else:
            pat = os.path.join(exp_dir, f"output/EnKF/{ym}/LIS_DA_EnKF_*_incr.a01.d01.nc")
        flist = sorted(glob.glob(pat))
        
        i1_m, i2_m, i3_m, i4_m = 0.0, 0.0, 0.0, 0.0
        for f in flist:
            with nc.Dataset(f) as ds:
                i1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
                i2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
                i3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
                i4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
                i1_m += float(np.sum(i1 * w_norm)) * dz[0] * 1000.0
                i2_m += float(np.sum(i2 * w_norm)) * dz[1] * 1000.0
                i3_m += float(np.sum(i3 * w_norm)) * dz[2] * 1000.0
                i4_m += float(np.sum(i4 * w_norm)) * dz[3] * 1000.0
        tot_m = i1_m + i2_m + i3_m + i4_m
        monthly_incrs.append((i1_m, i2_m, i3_m, i4_m, tot_m))
    return monthly_incrs

out_wb_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")

def run_step4():
    print("  Calcul en cours...")
    wb_records = []
    for st_id, st_name, bmask_180, w_181 in [
        ("b_l_chafia", "Lalla Chafia", mask_lalla_180, weights_lalla_181),
        ("b_s_jabeur", "Sidi Jabeur", mask_jabeur_180, weights_jabeur_181)
    ]:
        print(f"  Calcul du bilan sur le bassin de {st_name}...")
        for exp in exps:
            runoff_data = extract_catchment_monthly_fluxes(exp, bmask_180, area_180)
            p_et_data = extract_native_monthly_p_et(exp, w_181)
            if "DA" in exp:
                incrs = extract_catchment_enkf_increments(exp if exp != "DA_cdf" else "DA_nocdf", w_181)
            else:
                incrs = [(0.0, 0.0, 0.0, 0.0, 0.0)] * 12
    
            for m in range(12):
                ym = f"2018-{m+1:02d}"
                qs, qsb = runoff_data[m]
                p, et = p_et_data[m]
                i1, i2, i3, i4, itot = incrs[m]
                wb_records.append({
                    "station": st_name,
                    "station_id": st_id,
                    "experiment": exp,
                    "year_month": ym,
                    "P_mm": p,
                    "ET_mm": et,
                    "Qs_mm": qs,
                    "Qsb_mm": qsb,
                    "TotalRunoff_mm": qs + qsb,
                    "Incr_Layer1_mm": i1,
                    "Incr_Layer2_mm": i2,
                    "Incr_Layer3_mm": i3,
                    "Incr_Layer4_mm": i4,
                    "Incr_Total_mm": itot
                })
    
        
    df_wb = pd.DataFrame(wb_records)
    df_wb.to_csv(out_wb_csv, index=False)
    print(f"  [OK] Bilan mensuel amont sauve : {out_wb_csv}")

if os.path.exists(out_wb_csv):
    print(f"  [CACHE] Bilan mensuel amont existe déjà : {out_wb_csv}")
else:
    run_step4()

# 5. Qs + Qsb annuel de DA_nocdf sur Lalla Chafia pour 2016-2020
print("\n>>> 5. Calcul de Qs + Qsb annuel de DA_nocdf (2016-2020)...")
out_ann_csv = os.path.join(TABLES_DIR, "da_nocdf_annual_runoff_catchment_2016_2020.csv")

def run_step5():
    years = [2016, 2017, 2018, 2019, 2020]
    annual_records = []
    
    remap_da_dir = os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL")
    tot_area_lalla = sum(area_180[r, c] for r, c in cells_lalla)
    tot_area_jabeur = sum(area_180[r, c] for r, c in cells_jabeur)
    w_lalla = area_180 / tot_area_lalla
    w_jabeur = area_180 / tot_area_jabeur
    
    for yr in years:
        # Fichiers de l'annee
        yr_files = sorted(glob.glob(os.path.join(remap_da_dir, f"{yr}*/*.d01.nc")))
        # Premier jour annee suivante
        f_next = os.path.join(remap_da_dir, f"{yr+1}01/LIS_HIST_{yr+1}01010000.d01.nc")
        if os.path.exists(f_next):
            yr_files.append(f_next)
        
        qs_lalla, qsb_lalla = 0.0, 0.0
        qs_jabeur, qsb_jabeur = 0.0, 0.0
        for f in yr_files:
            fname = os.path.basename(f)
            if not fname.startswith("LIS_HIST_"):
                continue
            with nc.Dataset(f) as ds:
                qs = np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb = np.squeeze(ds["Qsb_tavg"][:]) * 86400.0
                qs_lalla += float(np.sum(qs[mask_lalla_180] * w_lalla[mask_lalla_180]))
                qsb_lalla += float(np.sum(qsb[mask_lalla_180] * w_lalla[mask_lalla_180]))
                qs_jabeur += float(np.sum(qs[mask_jabeur_180] * w_jabeur[mask_jabeur_180]))
                qsb_jabeur += float(np.sum(qsb[mask_jabeur_180] * w_jabeur[mask_jabeur_180]))
    
        # Conversion en hm3 et debit moyen m3/s
        n_days = 366 if yr in [2016, 2020] else 365
        vol_lalla_hm3 = (qs_lalla + qsb_lalla) * (tot_area_lalla / 1e6) / 1000.0
        q_lalla_m3s = vol_lalla_hm3 * 1e6 / (n_days * 86400.0)
    
        vol_jabeur_hm3 = (qs_jabeur + qsb_jabeur) * (tot_area_jabeur / 1e6) / 1000.0
        q_jabeur_m3s = vol_jabeur_hm3 * 1e6 / (n_days * 86400.0)
    
        annual_records.append({
            "station": "Lalla Chafia",
            "station_id": "b_l_chafia",
            "year": yr,
            "n_days": n_days,
            "area_km2": area_lalla_km2,
            "Qs_mm": qs_lalla,
            "Qsb_mm": qsb_lalla,
            "TotalRunoff_mm": qs_lalla + qsb_lalla,
            "TotalRunoff_hm3": vol_lalla_hm3,
            "Q_mean_m3s_equivalent": q_lalla_m3s
        })
        annual_records.append({
            "station": "Sidi Jabeur",
            "station_id": "b_s_jabeur",
            "year": yr,
            "n_days": n_days,
            "area_km2": area_jabeur_km2,
            "Qs_mm": qs_jabeur,
            "Qsb_mm": qsb_jabeur,
            "TotalRunoff_mm": qs_jabeur + qsb_jabeur,
            "TotalRunoff_hm3": vol_jabeur_hm3,
            "Q_mean_m3s_equivalent": q_jabeur_m3s
        })
    
        
    df_ann = pd.DataFrame(annual_records)
    df_ann.to_csv(out_ann_csv, index=False)
    print(f"  [OK] Bilan multi-annuel DA_nocdf sauve : {out_ann_csv}")

if os.path.exists(out_ann_csv):
    print(f"  [CACHE] Bilan multi-annuel DA_nocdf existe déjà : {out_ann_csv}")
else:
    run_step5()

# 6. Contrôle du ruissellement remappé vs natif sur Lalla Chafia en 2018
print("\n>>> 6. Contrôle du ruissellement remappé vs natif sur Lalla Chafia (2018)...")
out_remap_check_csv = os.path.join(TABLES_DIR, "remap_runoff_check_lalla_chafia_2018.csv")

def run_step6():
    remap_check_records = []
    
    for exp in ["DA_nocdf", "ENS_OPL"]:
        # 1. Lu dans remappé 180x120
        if exp == "DA_nocdf":
            r_dir = os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL")
        else:
            r_dir = os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL")
        
        files_remap = sorted(glob.glob(os.path.join(r_dir, "2018*/*.d01.nc")))
        f_next = os.path.join(r_dir, "201901/LIS_HIST_201901010000.d01.nc")
        if os.path.exists(f_next):
            files_remap.append(f_next)
        
        qs_remap, qsb_remap = 0.0, 0.0
        for f in files_remap:
            fname = os.path.basename(f)
            if not fname.startswith("LIS_HIST_"):
                continue
            with nc.Dataset(f) as ds:
                qs = np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb = np.squeeze(ds["Qsb_tavg"][:]) * 86400.0
                qs_remap += float(np.sum(qs[mask_lalla_180] * w_lalla[mask_lalla_180]))
                qsb_remap += float(np.sum(qsb[mask_lalla_180] * w_lalla[mask_lalla_180]))
    
        # 2. Lu dans natif 181x121 projeté
        w_nat = weights_lalla_181 / np.sum(weights_lalla_181)
        exp_dir = RUN_DIRS[exp]
        
        qs_nat, qsb_nat = 0.0, 0.0
        for m in range(1, 13):
            m_label = f"2018-{m:02d}"
            ym = f"2018{m:02d}"
            if exp == "DA_nocdf":
                f_dir = os.path.join(exp_dir, f"output/{m_label}/SURFACEMODEL/{ym}")
            else:
                f_dir = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}")
            files_nat = sorted(glob.glob(os.path.join(f_dir, "LIS_HIST_*.d01.nc")))
            m_next = f"2018{m+1:02d}" if m < 12 else "201901"
            if exp == "DA_nocdf":
                m_next_label = f"2018-{m+1:02d}" if m < 12 else "2019-01"
                f_last = os.path.join(exp_dir, f"output/{m_next_label}/SURFACEMODEL/{m_next}/LIS_HIST_{m_next}010000.d01.nc")
            else:
                f_last = os.path.join(exp_dir, f"output/SURFACEMODEL/{m_next}/LIS_HIST_{m_next}010000.d01.nc")
                if not os.path.exists(f_last) and m == 5:
                    f_last = os.path.join(exp_dir, f"output/_partial_201806_hang/SURFACEMODEL_{m_next}/LIS_HIST_{m_next}010000.d01.nc")
    
            if os.path.exists(f_last) and f_last not in files_nat:
                files_nat.append(f_last)
    
            for f in files_nat:
                with nc.Dataset(f) as ds:
                    qs = ds["Qs_tavg"][:].squeeze() * 86400.0
                    qsb = ds["Qsb_tavg"][:].squeeze() * 86400.0
                    qs_nat += float(np.sum(qs * w_nat))
                    qsb_nat += float(np.sum(qsb * w_nat))
    
        tot_remap = qs_remap + qsb_remap
        tot_nat = qs_nat + qsb_nat
        diff_mm = tot_remap - tot_nat
        diff_pct = (diff_mm / tot_nat) * 100.0
    
        remap_check_records.append({
            "experiment": exp,
            "station": "Lalla Chafia",
            "catchment_area_km2": area_lalla_km2,
            "Qs_native_mm": qs_nat,
            "Qsb_native_mm": qsb_nat,
            "TotalRunoff_native_mm": tot_nat,
            "Qs_remapped_mm": qs_remap,
            "Qsb_remapped_mm": qsb_remap,
            "TotalRunoff_remapped_mm": tot_remap,
            "difference_mm": diff_mm,
            "difference_pct": diff_pct
        })
    
        
    df_remap_check = pd.DataFrame(remap_check_records)
    df_remap_check.to_csv(out_remap_check_csv, index=False)
    print(f"  [OK] Contrôle du remapping sauvé : {out_remap_check_csv}")

if os.path.exists(out_remap_check_csv):
    print(f"  [CACHE] Contrôle remapping existe déjà : {out_remap_check_csv}")
else:
    run_step6()

# 7. Carte de différence Qsb 2018 DA_nocdf - ENS_OPL et Top 20 mailles
print("\n>>> 7. Calcul de la carte de difference Qsb annuel (DA_nocdf - ENS_OPL) et Top 20 mailles...")
# Chargement Qsb annuel 180x120 pour DA_nocdf et ENS_OPL
qsb_ann_da = np.zeros((120, 180), dtype=float)
qsb_ann_ens = np.zeros((120, 180), dtype=float)

# DA_nocdf
da_dir = os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL")
files_da = sorted(glob.glob(os.path.join(da_dir, "2018*/*.d01.nc")))
f_next_da = os.path.join(da_dir, "201901/LIS_HIST_201901010000.d01.nc")
if os.path.exists(f_next_da):
    files_da.append(f_next_da)
for f in files_da:
    if os.path.basename(f).startswith("LIS_HIST_"):
        with nc.Dataset(f) as ds:
            qsb_ann_da += np.squeeze(ds["Qsb_tavg"][:]) * 86400.0

# ENS_OPL
ens_dir = os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL")
files_ens = sorted(glob.glob(os.path.join(ens_dir, "2018*/*.d01.nc")))
f_next_ens = os.path.join(ens_dir, "201901/LIS_HIST_201901010000.d01.nc")
if os.path.exists(f_next_ens):
    files_ens.append(f_next_ens)
for f in files_ens:
    if os.path.basename(f).startswith("LIS_HIST_"):
        with nc.Dataset(f) as ds:
            qsb_ann_ens += np.squeeze(ds["Qsb_tavg"][:]) * 86400.0

diff_qsb = qsb_ann_da - qsb_ann_ens

# Coordonnées et texture
with nc.Dataset(LDT_FILE) as ds:
    lats_180 = ds["lat"][:]
    lons_180 = ds["lon"][:]
    basin_hymap = ds["HYMAP_basin"][:]
    texture_raw = ds["TEXTURE"][:]  # (16, 120, 180)
    dom_mask = ds["DOMAINMASK"][:] == 1.0

# Texture dominante
tex_idx = np.argmax(texture_raw, axis=0) + 1  # 1-indexed

USDA_NAMES = {
    1: "Sand", 2: "Loamy Sand", 3: "Sandy Loam", 4: "Silt Loam", 5: "Silt",
    6: "Loam", 7: "Sandy Clay Loam", 8: "Silty Clay Loam", 9: "Clay Loam",
    10: "Sandy Clay", 11: "Silty Clay", 12: "Clay", 13: "Organic Material",
    14: "Water", 15: "Bedrock", 16: "Other"
}

# Extraction des Top 20 mailles où diff_qsb est la plus forte
top_indices = np.argsort(diff_qsb.ravel())[::-1]
top20_records = []
rank = 1
for idx in top_indices:
    r, c = np.unravel_index(idx, (120, 180))
    if not dom_mask[r, c]:
        continue
    t_id = int(tex_idx[r, c])
    t_name = USDA_NAMES.get(t_id, f"Class {t_id}")
    in_bouregreg = bool(basin_hymap[r, c] == 150.0)
    in_sebou = bool(basin_hymap[r, c] == 155.0)
    in_lalla = bool(mask_lalla_180[r, c])
    in_jabeur = bool(mask_jabeur_180[r, c])

    top20_records.append({
        "rank": rank,
        "row_180": r,
        "col_180": c,
        "lon": float(lons_180[r, c]),
        "lat": float(lats_180[r, c]),
        "texture_id": t_id,
        "texture_name": t_name,
        "qsb_da_nocdf_mm": float(qsb_ann_da[r, c]),
        "qsb_ens_opl_mm": float(qsb_ann_ens[r, c]),
        "diff_qsb_mm": float(diff_qsb[r, c]),
        "inside_lalla_chafia": in_lalla,
        "inside_sidi_jabeur": in_jabeur,
        "inside_bouregreg": in_bouregreg,
        "inside_sebou": in_sebou
    })
    rank += 1
    if len(top20_records) >= 20:
        break

df_top20 = pd.DataFrame(top20_records)
out_top20_csv = os.path.join(TABLES_DIR, "top20_cells_qsb_difference.csv")
df_top20.to_csv(out_top20_csv, index=False)
print(f"  [OK] Table Top 20 mailles sauvee : {out_top20_csv}")

# Carte matplotlib
fig, ax = plt.subplots(figsize=(12, 8))
masked_diff = np.ma.masked_where(~dom_mask, diff_qsb)
lon_mesh = lons_180
lat_mesh = lats_180

cmap = plt.cm.RdYlBu_r
levels = np.linspace(-50, 600, 27)
cf = ax.contourf(lon_mesh, lat_mesh, masked_diff, levels=levels, cmap=cmap, extend="both")
cb = plt.colorbar(cf, ax=ax, orientation="vertical", pad=0.02, shrink=0.85)
cb.set_label("2018 Subsurface Runoff Difference (DA_nocdf − ENS_OPL) [mm/year]", fontsize=10)

# Contours des bassins
# Bassin Sebou (ID 155) et Bouregreg (ID 150)
ax.contour(lon_mesh, lat_mesh, basin_hymap == 155.0, levels=[0.5], colors=["#1f77b4"], linewidths=[1.2], linestyles=["--"])
ax.contour(lon_mesh, lat_mesh, basin_hymap == 150.0, levels=[0.5], colors=["#2ca02c"], linewidths=[1.2], linestyles=["--"])

# Contours amont exacts Lalla Chafia et Sidi Jabeur
ax.contour(lon_mesh, lat_mesh, mask_lalla_180, levels=[0.5], colors=["black"], linewidths=[2.0])
ax.contour(lon_mesh, lat_mesh, mask_jabeur_180, levels=[0.5], colors=["purple"], linewidths=[1.8])

# Positions des stations
ax.plot(lons_180[75, 71], lats_180[75, 71], marker="^", markersize=9, color="black", markeredgecolor="white", label="Lalla Chafia outlet")
ax.plot(lons_180[71], lats_180[71], marker="v", markersize=9, color="purple", markeredgecolor="white", label="Sidi Jabeur outlet")

# Légende personnalisée
from matplotlib.lines import Line2D
custom_lines = [
    Line2D([0], [0], color="black", lw=2, label="Lalla Chafia Upstream Catchment (D8)"),
    Line2D([0], [0], color="purple", lw=1.8, label="Sidi Jabeur Upstream Catchment (D8)"),
    Line2D([0], [0], color="#2ca02c", lw=1.2, linestyle="--", label="Bouregreg Basin Outline (ID 150)"),
    Line2D([0], [0], color="#1f77b4", lw=1.2, linestyle="--", label="Sebou Basin Outline (ID 155)"),
    Line2D([0], [0], marker="^", color="w", markerfacecolor="black", markersize=8, label="Lalla Chafia Outlet"),
    Line2D([0], [0], marker="v", color="w", markerfacecolor="purple", markersize=8, label="Sidi Jabeur Outlet"),
]
ax.legend(handles=custom_lines, loc="lower right", framealpha=0.9, fontsize=9)

ax.set_title("2018 Annual Subsurface Runoff Difference (DA_nocdf − ENS_OPL)\nwith HyMAP Upstream Catchment Delineation", fontsize=12, fontweight="bold")
ax.set_xlabel("Longitude [°E]", fontsize=10)
ax.set_ylabel("Latitude [°N]", fontsize=10)
ax.grid(True, linestyle=":", alpha=0.5)

map_png = os.path.join(FIGURES_DIR, "fig_map_qsb_difference_da_minus_ens.png")
map_pdf = os.path.join(FIGURES_DIR, "fig_map_qsb_difference_da_minus_ens.pdf")
plt.tight_layout()
plt.savefig(map_png, dpi=300)
plt.savefig(map_pdf)
plt.close()
print(f"  [OK] Carte sauvee : {map_png} et {map_pdf}")

print("\n>>> Toutes les verifications ont ete executees avec succes !")
