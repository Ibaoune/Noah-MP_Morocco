#!/usr/bin/env python3
"""
c2_evaluate_et.py
Évaluation rigoureuse de l'évapotranspiration (ET) simulée par Noah-MP contre GLEAM v4.3a et WaPOR (RQ3).
Génère:
  - paper1/tables/et_evaluation.csv
  - paper1/tables/et_evaluation_by_texture.csv
  - paper1/tables/et_direction_of_change.csv
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

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# -------------------------------------------------------------
# 1. Grilles, Masques et Stratifications
# -------------------------------------------------------------
print(">>> Chargement des masques géographiques et texturaux...")
lis_input_path = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
ds_in = nc.Dataset(lis_input_path)
landmask_181 = ds_in.variables["LANDMASK"][:] == 1.0  # (121, 181)
texture_181 = ds_in.variables["TEXTURE"][:]          # (16, 121, 181)
dom_texture_181 = np.argmax(texture_181, axis=0) + 1  # 1 to 16
lat_181 = ds_in.variables["lat"][:, 0]
lon_181 = ds_in.variables["lon"][0, :]
ds_in.close()

# Bassins Sebou et Bouregreg depuis lis_input_corrigee.d01.nc
hymap_input_path = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
ds_hm = nc.Dataset(hymap_input_path)
hymap_basin = ds_hm.variables["HYMAP_basin"][:]  # (120, 180)
lat_180 = ds_hm.variables["lat"][:, 0]
lon_180 = ds_hm.variables["lon"][0, :]
ds_hm.close()

# Remap basin from 180x120 to 181x121
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
ds_g = nc.Dataset(gleam_file_2018)
g_lat_all = ds_g.variables["lat"][:]
g_lon_all = ds_g.variables["lon"][:]
ds_g.close()

lat_idx_g = np.where((g_lat_all >= 30.0) & (g_lat_all <= 36.0))[0]
lon_idx_g = np.where((g_lon_all >= -10.0) & (g_lon_all <= -1.0))[0]
gleam_lats = g_lat_all[lat_idx_g]  # descending 35.95 to 30.05 (60)
gleam_lons = g_lon_all[lon_idx_g]  # ascending -9.95 to -1.05 (90)

# Fonction d'agrégation conservative 181x121 -> 60x90 GLEAM
def regrid_to_gleam(grid_181, mask_weights=None):
    """
    Agrège un champ (121, 181) vers la grille GLEAM (60, 90) par moyenne des mailles
    terrestres contenues dans chaque boîte de 0.10° x 0.10°.
    """
    out_grid = np.full((60, 90), np.nan, dtype=np.float32)
    weights = landmask_181 if mask_weights is None else (landmask_181 & mask_weights)
    
    for j, lat_c in enumerate(gleam_lats):
        # lat_c is center, box spans [lat_c - 0.05, lat_c + 0.05]
        r_idx = np.where((lat_181 >= lat_c - 0.05 - 1e-4) & (lat_181 <= lat_c + 0.05 + 1e-4))[0]
        for i, lon_c in enumerate(gleam_lons):
            c_idx = np.where((lon_181 >= lon_c - 0.05 - 1e-4) & (lon_181 <= lon_c + 0.05 + 1e-4))[0]
            sub_w = weights[np.ix_(r_idx, c_idx)]
            if np.any(sub_w):
                sub_data = grid_181[np.ix_(r_idx, c_idx)]
                out_grid[j, i] = np.mean(sub_data[sub_w])
    return out_grid

# Masques agrégés sur grille GLEAM
mask_g_domain = ~np.isnan(regrid_to_gleam(np.where(mask_domain, 1.0, np.nan)))
mask_g_sebou = ~np.isnan(regrid_to_gleam(np.where(mask_sebou, 1.0, np.nan)))
mask_g_bouregreg = ~np.isnan(regrid_to_gleam(np.where(mask_bouregreg, 1.0, np.nan)))

# Texture dominante agrégée sur grille GLEAM
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

# Noms de texture USDA
TEXTURE_NAMES = {
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
    13: "Organic material"
}

# -------------------------------------------------------------
# 2. Chargement des Observations GLEAM et WaPOR
# -------------------------------------------------------------
print(">>> Chargement et traitement des observations GLEAM v4.3a...")
def load_gleam_year(year):
    fpath = os.path.join(BASE_DIR, f"data/validation/evapotranspiration/GLEAM/raw/E_{year}_GLEAM_v4.3a.nc")
    ds = nc.Dataset(fpath)
    # E: (time, lat, lon) in mm/day
    e_raw = ds.variables["E"][:, lat_idx_g, lon_idx_g]
    # Dates
    n_days = len(e_raw)
    ds.close()
    
    # Days per month
    leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    days_in_month = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    # Monthly total ET (mm/month)
    monthly_et = []
    d_start = 0
    for m, nd in enumerate(days_in_month):
        d_end = d_start + nd
        # mean daily rate * nd
        sub_e = e_raw[d_start:d_end, :, :]
        # masked / fill values
        sub_e = np.where(sub_e < -900, np.nan, sub_e)
        m_mean = np.nanmean(sub_e, axis=0)
        m_tot = m_mean * nd
        monthly_et.append(m_tot)
        d_start = d_end
    
    monthly_et = np.array(monthly_et, dtype=np.float32) # (12, 60, 90)
    annual_et = np.sum(monthly_et, axis=0)              # (60, 90)
    return monthly_et, annual_et

gleam_monthly_2018, gleam_annual_2018 = load_gleam_year(2018)

# Chargement WaPOR v3 (2018, annuel)
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

# Masque de couverture commune WaPOR v3 (recouvrement partiel nord Maroc)
mask_g_wapor_coverage = ~np.isnan(wapor_annual_on_gleam_2018) & mask_g_domain
print(f"Mailles de couverture commune WaPOR v3 sur domaine: {np.sum(mask_g_wapor_coverage)}")

# -------------------------------------------------------------
# 3. Chargement et Agrégation des Sorties Noah-MP
# -------------------------------------------------------------
print(">>> Chargement des simulations Noah-MP...")

def load_noahmp_monthly_et(exp_name, year):
    """
    Extrait les 12 grilles mensuelles d'ET (mm/mois) pour une expérience et une année donnée.
    """
    if exp_name == "OPL":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/{year}-*/**/LIS_HIST_*.d01.nc")
    elif exp_name == "DA_nocdf":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/{year}-*/**/LIS_HIST_*.d01.nc")
    elif exp_name == "DA_cdf":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output/{year}-*/**/LIS_HIST_*.d01.nc")
    elif exp_name == "OL_DAIC":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_{year}/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc")
    elif exp_name == "ENS_OPL":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_{year}/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc")
    elif exp_name == "DA_nocdf_nowilt":
        src_pattern = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_{year}/output/SURFACEMODEL/**/LIS_HIST_*.d01.nc")
    else:
        raise ValueError(f"Expérience inconnue: {exp_name}")
    
    files = sorted(glob.glob(src_pattern, recursive=True))
    # Exclude boundary/restart files
    files = [f for f in files if "LIS_HIST_" in f and not f.endswith("0000.d01.nc.tmp")]
    
    # Grouper par mois calendaire réel de simulation
    # Rappel: t_sim = t_file - 1 jour
    month_data = {m: [] for m in range(1, 13)}
    
    for f in files:
        fname = os.path.basename(f)
        m = re.search(r"LIS_HIST_(\d{4})(\d{2})(\d{2})", fname)
        if not m: continue
        f_y, f_m, f_d = int(m.group(1)), int(m.group(2)), int(m.group(3))
        # Date simulée = f_date - 1 day
        ts = pd.Timestamp(year=f_y, month=f_m, day=f_d) - pd.Timedelta(days=1)
        if ts.year == year:
            month_data[ts.month].append(f)
            
    leap = (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0))
    days_in_month = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    monthly_et_181 = []
    for m in range(1, 13):
        flist = month_data[m]
        if not flist:
            print(f"Warning: Aucun fichier pour {exp_name} {year}-{m:02d}!")
            monthly_et_181.append(np.full((121, 181), np.nan, dtype=np.float32))
            continue
        
        # Moyenne quotidienne du mois (kg/m2/s * 86400 = mm/jour)
        daily_sums = np.zeros((121, 181), dtype=np.float64)
        for f in flist:
            ds = nc.Dataset(f, "r")
            evap = ds.variables["Evap_tavg"][:]
            if evap.ndim == 3: evap = evap[0]
            ds.close()
            evap_clean = np.where((evap < -900) | np.isnan(evap), 0.0, evap) * 86400.0
            daily_sums += evap_clean
            
        m_rate = daily_sums / len(flist)
        # Total mensuel physique = taux journalier moyen * nombre de jours civils
        m_total = m_rate * days_in_month[m - 1]
        monthly_et_181.append(m_total.astype(np.float32))
        
    monthly_et_181 = np.array(monthly_et_181) # (12, 121, 181)
    
    # Agrégation conservative vers la grille GLEAM (60, 90)
    monthly_et_g = np.array([regrid_to_gleam(monthly_et_181[m]) for m in range(12)])
    annual_et_g = np.sum(monthly_et_g, axis=0)
    
    return monthly_et_g, annual_et_g

# Charger les 6 simulations 2018
exp_list_2018 = ["OPL", "OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]
sim_monthly_2018 = {}
sim_annual_2018 = {}

for exp in exp_list_2018:
    t0 = time.time()
    m_et, a_et = load_noahmp_monthly_et(exp, 2018)
    sim_monthly_2018[exp] = m_et
    sim_annual_2018[exp] = a_et
    mean_dom = np.nanmean(a_et[mask_g_domain])
    print(f"  {exp:16s} 2018 ET chargée en {time.time()-t0:.1f} s | Moyenne domaine: {mean_dom:.1f} mm/an")

# -------------------------------------------------------------
# 4. Calcul des Métriques et Évaluations Statistiques
# -------------------------------------------------------------
print("\n>>> Calcul des métriques statistiques et stratifications...")

def compute_metrics(obs_arr, sim_arr, mask):
    """
    Calcule Biais (mm et %), RMSD, ubRMSD, et Corrélation spatio-temporelle / spatiale.
    obs_arr et sim_arr ont la même forme: soit 2D (annuel), soit 3D (saisonnier / mensuel).
    """
    if obs_arr.ndim == 2:
        o = obs_arr[mask]
        s = sim_arr[mask]
        valid = ~np.isnan(o) & ~np.isnan(s)
        o, s = o[valid], s[valid]
        if len(o) < 5:
            return np.nan, np.nan, np.nan, np.nan, np.nan, len(o), np.nan, np.nan
        
        obs_mean = float(np.mean(o))
        sim_mean = float(np.mean(s))
        bias = float(np.mean(s - o))
        rel_bias = float((bias / obs_mean) * 100.0) if obs_mean != 0 else np.nan
        rmsd = float(np.sqrt(np.mean((s - o) ** 2)))
        ubrmsd = float(np.sqrt(max(0.0, rmsd ** 2 - bias ** 2)))
        r, _ = stats.pearsonr(o, s) if len(o) > 2 and np.std(o) > 0 and np.std(s) > 0 else (np.nan, np.nan)
        return obs_mean, sim_mean, bias, rel_bias, rmsd, ubrmsd, float(r), int(len(o))
        
    elif obs_arr.ndim == 3:
        # 3D: (months, lat, lon)
        # Vectorisation sur l'ensemble des mois et mailles valides
        n_m = obs_arr.shape[0]
        o_list, s_list = [], []
        for m in range(n_m):
            sub_o = obs_arr[m][mask]
            sub_s = sim_arr[m][mask]
            valid = ~np.isnan(sub_o) & ~np.isnan(sub_s)
            o_list.append(sub_o[valid])
            s_list.append(sub_s[valid])
            
        o = np.concatenate(o_list)
        s = np.concatenate(s_list)
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

# Définition des strates géographiques
strata_geo = {
    "Domain": mask_g_domain,
    "Sebou": mask_g_sebou,
    "Bouregreg": mask_g_bouregreg
}

# Définition des saisons (indices mensuels 0-indexed)
seasons_idx = {
    "Annual": list(range(12)),
    "MAM": [2, 3, 4],  # March, April, May
    "JJA": [5, 6, 7]   # June, July, August
}

# -------------------------------------------------------------
# TABLE 1 : et_evaluation.csv
# -------------------------------------------------------------
eval_rows = []

# Évaluation 2018 contre GLEAM v4.3a
for exp in exp_list_2018:
    sim_m = sim_monthly_2018[exp]
    sim_a = sim_annual_2018[exp]
    
    for s_name, s_mask in strata_geo.items():
        # Annuel (somme mm/an)
        o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
            gleam_annual_2018, sim_a, s_mask
        )
        eval_rows.append({
            "experiment": exp,
            "period": "2018",
            "reference": "GLEAM_v4.3a",
            "stratum": s_name,
            "season": "Annual",
            "n_obs": n_pts,
            "et_obs_mean_mm": round(o_m, 2),
            "et_sim_mean_mm": round(s_m, 2),
            "bias_mm": round(b, 2),
            "rel_bias_pct": round(rb, 2),
            "rmsd_mm": round(rmse, 2),
            "ubrmsd_mm": round(ub_rmse, 2),
            "r_monthly": round(r_val, 4)
        })
        
        # Saisonnier MAM et JJA (somme saisonnière en mm)
        for seas, m_indices in [("MAM", [2, 3, 4]), ("JJA", [5, 6, 7])]:
            g_seas = np.sum(gleam_monthly_2018[m_indices], axis=0)
            sim_seas = np.sum(sim_m[m_indices], axis=0)
            o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
                g_seas, sim_seas, s_mask
            )
            eval_rows.append({
                "experiment": exp,
                "period": "2018",
                "reference": "GLEAM_v4.3a",
                "stratum": s_name,
                "season": seas,
                "n_obs": n_pts,
                "et_obs_mean_mm": round(o_m, 2),
                "et_sim_mean_mm": round(s_m, 2),
                "bias_mm": round(b, 2),
                "rel_bias_pct": round(rb, 2),
                "rmsd_mm": round(rmse, 2),
                "ubrmsd_mm": round(ub_rmse, 2),
                "r_monthly": round(r_val, 4)
            })

# Évaluation 2018 contre WaPOR v3 AETI (Annuel uniquement, sur emprise commune)
for exp in exp_list_2018:
    sim_a = sim_annual_2018[exp]
    for s_name, s_mask in strata_geo.items():
        w_mask = s_mask & mask_g_wapor_coverage
        o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
            wapor_annual_on_gleam_2018, sim_a, w_mask
        )
        eval_rows.append({
            "experiment": exp,
            "period": "2018",
            "reference": "WaPOR_v3",
            "stratum": s_name,
            "season": "Annual",
            "n_obs": n_pts,
            "et_obs_mean_mm": round(o_m, 2) if not np.isnan(o_m) else np.nan,
            "et_sim_mean_mm": round(s_m, 2) if not np.isnan(s_m) else np.nan,
            "bias_mm": round(b, 2) if not np.isnan(b) else np.nan,
            "rel_bias_pct": round(rb, 2) if not np.isnan(rb) else np.nan,
            "rmsd_mm": round(rmse, 2) if not np.isnan(rmse) else np.nan,
            "ubrmsd_mm": round(ub_rmse, 2) if not np.isnan(ub_rmse) else np.nan,
            "r_monthly": round(r_val, 4) if not np.isnan(r_val) else np.nan
        })

# Incertitude de Référence : Écart GLEAM - WaPOR (2018 Annuel)
for s_name, s_mask in strata_geo.items():
    w_mask = s_mask & mask_g_wapor_coverage
    o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
        wapor_annual_on_gleam_2018, gleam_annual_2018, w_mask
    )
    eval_rows.append({
        "experiment": "GLEAM_v4.3a",
        "period": "2018",
        "reference": "WaPOR_v3",
        "stratum": s_name,
        "season": "Annual",
        "n_obs": n_pts,
        "et_obs_mean_mm": round(o_m, 2),
        "et_sim_mean_mm": round(s_m, 2),
        "bias_mm": round(b, 2),
        "rel_bias_pct": round(rb, 2),
        "rmsd_mm": round(rmse, 2),
        "ubrmsd_mm": round(ub_rmse, 2),
        "r_monthly": round(r_val, 4)
    })

# Évaluation Multi-annuelle 2016-2020 (OPL, DA_nocdf, DA_cdf) contre GLEAM v4.3a
print(">>> Évaluation 2016-2020 de production contre GLEAM...")
multiyear_exps = ["OPL", "DA_nocdf", "DA_cdf"]
years_5y = [2016, 2017, 2018, 2019, 2020]

# Charger GLEAM 2016-2020
gleam_5y_annual = []
for y in years_5y:
    _, a_et = load_gleam_year(y)
    gleam_5y_annual.append(a_et)
gleam_5y_mean = np.mean(gleam_5y_annual, axis=0) # (60, 90) mm/an

for exp in multiyear_exps:
    sim_5y_annual = []
    for y in years_5y:
        _, a_et = load_noahmp_monthly_et(exp, y)
        sim_5y_annual.append(a_et)
    sim_5y_mean = np.mean(sim_5y_annual, axis=0)
    
    for s_name, s_mask in strata_geo.items():
        o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
            gleam_5y_mean, sim_5y_mean, s_mask
        )
        eval_rows.append({
            "experiment": exp,
            "period": "2016-2020",
            "reference": "GLEAM_v4.3a",
            "stratum": s_name,
            "season": "Annual",
            "n_obs": n_pts,
            "et_obs_mean_mm": round(o_m, 2),
            "et_sim_mean_mm": round(s_m, 2),
            "bias_mm": round(b, 2),
            "rel_bias_pct": round(rb, 2),
            "rmsd_mm": round(rmse, 2),
            "ubrmsd_mm": round(ub_rmse, 2),
            "r_monthly": round(r_val, 4)
        })

df_eval = pd.DataFrame(eval_rows)
out_eval_path = os.path.join(TABLES_DIR, "et_evaluation.csv")
df_eval.to_csv(out_eval_path, index=False)
print(f"Table 1 sauvegardée : {out_eval_path} ({len(df_eval)} lignes)")

# -------------------------------------------------------------
# TABLE 2 : et_evaluation_by_texture.csv
# -------------------------------------------------------------
print(">>> Calcul de l'évaluation stratifiée par classe texturale...")
tex_rows = []

# Classes texturales représentées
valid_textures = [t for t in [1, 3, 4, 6, 7, 9, 12] if np.any((tex_g == t) & mask_g_domain)]

for exp in exp_list_2018:
    sim_a = sim_annual_2018[exp]
    for t_id in valid_textures:
        t_name = TEXTURE_NAMES.get(t_id, f"Class_{t_id}")
        t_mask = (tex_g == t_id) & mask_g_domain
        
        # Contre GLEAM 2018
        o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
            gleam_annual_2018, sim_a, t_mask
        )
        tex_rows.append({
            "experiment": exp,
            "period": "2018",
            "reference": "GLEAM_v4.3a",
            "texture_id": t_id,
            "texture_name": t_name,
            "n_cells": n_pts,
            "et_obs_mean_mm": round(o_m, 2),
            "et_sim_mean_mm": round(s_m, 2),
            "bias_mm": round(b, 2),
            "rel_bias_pct": round(rb, 2),
            "rmsd_mm": round(rmse, 2),
            "ubrmsd_mm": round(ub_rmse, 2),
            "r_spatial": round(r_val, 4)
        })
        
        # Contre WaPOR v3 2018
        w_t_mask = t_mask & mask_g_wapor_coverage
        o_m, s_m, b, rb, rmse, ub_rmse, r_val, n_pts = compute_metrics(
            wapor_annual_on_gleam_2018, sim_a, w_t_mask
        )
        if n_pts > 0:
            tex_rows.append({
                "experiment": exp,
                "period": "2018",
                "reference": "WaPOR_v3",
                "texture_id": t_id,
                "texture_name": t_name,
                "n_cells": n_pts,
                "et_obs_mean_mm": round(o_m, 2) if not np.isnan(o_m) else np.nan,
                "et_sim_mean_mm": round(s_m, 2) if not np.isnan(s_m) else np.nan,
                "bias_mm": round(b, 2) if not np.isnan(b) else np.nan,
                "rel_bias_pct": round(rb, 2) if not np.isnan(rb) else np.nan,
                "rmsd_mm": round(rmse, 2) if not np.isnan(rmse) else np.nan,
                "ubrmsd_mm": round(ub_rmse, 2) if not np.isnan(ub_rmse) else np.nan,
                "r_spatial": round(r_val, 4) if not np.isnan(r_val) else np.nan
            })

df_tex = pd.DataFrame(tex_rows)
out_tex_path = os.path.join(TABLES_DIR, "et_evaluation_by_texture.csv")
df_tex.to_csv(out_tex_path, index=False)
print(f"Table 2 sauvegardée : {out_tex_path} ({len(df_tex)} lignes)")

# -------------------------------------------------------------
# TABLE 3 : et_direction_of_change.csv
# -------------------------------------------------------------
print(">>> Analyse de la direction de changement (rapprochement vs éloignement)...")
dir_rows = []

pairs_to_test = [
    ("DA_nocdf", "ENS_OPL", "DA_nocdf vs ENS_OPL (Effet des observations)"),
    ("ENS_OPL", "OL_DAIC", "ENS_OPL vs OL_DAIC (Effet de l'ensemble)"),
    ("DA_nocdf_nowilt", "DA_nocdf", "DA_nocdf_nowilt vs DA_nocdf (Effet du filtre flétrissement)")
]

for exp_x, exp_y, pair_label in pairs_to_test:
    sim_x_a = sim_annual_2018[exp_x]
    sim_y_a = sim_annual_2018[exp_y]
    
    # 1. Contre GLEAM v4.3a
    for s_name, s_mask in strata_geo.items():
        o = gleam_annual_2018[s_mask]
        sx = sim_x_a[s_mask]
        sy = sim_y_a[s_mask]
        valid = ~np.isnan(o) & ~np.isnan(sx) & ~np.isnan(sy)
        o, sx, sy = o[valid], sx[valid], sy[valid]
        
        diff = sx - sy
        mean_diff = float(np.mean(diff))
        
        # Biais absolus
        bias_x = float(np.mean(sx - o))
        bias_y = float(np.mean(sy - o))
        delta_abs_bias = abs(bias_x) - abs(bias_y)  # < 0 signifie réduction d'erreur (rapprochement)
        
        # Fraction des mailles qui se rapprochent
        dist_x = np.abs(sx - o)
        dist_y = np.abs(sy - o)
        frac_closer = float(np.mean(dist_x < dist_y) * 100.0)
        
        direction = "Rapprochement" if delta_abs_bias < 0 else "Éloignement"
        
        dir_rows.append({
            "pair": f"{exp_x} - {exp_y}",
            "pair_description": pair_label,
            "reference": "GLEAM_v4.3a",
            "period": "2018",
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

    # 2. Contre WaPOR v3 AETI
    for s_name, s_mask in strata_geo.items():
        w_mask = s_mask & mask_g_wapor_coverage
        o = wapor_annual_on_gleam_2018[w_mask]
        sx = sim_x_a[w_mask]
        sy = sim_y_a[w_mask]
        valid = ~np.isnan(o) & ~np.isnan(sx) & ~np.isnan(sy)
        o, sx, sy = o[valid], sx[valid], sy[valid]
        
        if len(o) > 5:
            diff = sx - sy
            mean_diff = float(np.mean(diff))
            bias_x = float(np.mean(sx - o))
            bias_y = float(np.mean(sy - o))
            delta_abs_bias = abs(bias_x) - abs(bias_y)
            dist_x = np.abs(sx - o)
            dist_y = np.abs(sy - o)
            frac_closer = float(np.mean(dist_x < dist_y) * 100.0)
            direction = "Rapprochement" if delta_abs_bias < 0 else "Éloignement"
            
            dir_rows.append({
                "pair": f"{exp_x} - {exp_y}",
                "pair_description": pair_label,
                "reference": "WaPOR_v3",
                "period": "2018",
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

df_dir = pd.DataFrame(dir_rows)
out_dir_path = os.path.join(TABLES_DIR, "et_direction_of_change.csv")
df_dir.to_csv(out_dir_path, index=False)
print(f"Table 3 sauvegardée : {out_dir_path} ({len(df_dir)} lignes)")
print("\n>>> Traitement C2 (ET Evaluation) achevé avec succès !")
