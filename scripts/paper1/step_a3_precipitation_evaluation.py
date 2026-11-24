#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Étape A3 — Précipitations (H5).
Pas de nouveau run, pas de téléchargement, pas d'interprétation.
Message final : AUCUN chiffre, seulement la liste des fichiers et le hash du commit.

1. Stations (ABH_stations_plusziz_and_abhbc.csv, 2001–2014) :
   - doublons station-date identiques -> garder une valeur ;
   - doublons conflictuels -> exclure la date pour cette station ;
   - valeurs > 300 mm/j -> exclure ;
   - écrire les comptes de chaque exclusion par station ;
   - garder les stations avec >= 80 % de jours valides en 2001–2014 ;
   - ajouter bassin (masques A2b) et altitude (lis_input).
2. Produits :
   - IMERG V07B (demi-horaire -> journalier UTC ; jour "absent" si < 48 fichiers) ;
   - MERRA-2 PRECTOTCORR journalier (jour "absent" si incomplet) ;
   - Comparaison station <-> pixel qui la contient ;
   - Tester le décalage de jour (-1, 0, +1) par corrélation journalière et garder le meilleur, en le reportant.
3. Métriques (par station, puis agrégées par bassin, par classe d'altitude et par saison) :
   - rapport de cumul produit/station ;
   - fréquence de jours >= 1 mm ;
   - intensité moyenne des jours pluvieux ;
   - POD/FAR/CSI pour >= 1, >= 10 et >= 30 mm ;
   - quantiles 95 et 99 des jours pluvieux ;
   - rapport sur les 1 % de jours les plus forts ;
   - Bassins avec >= 2 stations (dont Lalla Chafia et Sidi Jabeur) : moyenne des stations vs moyenne de bassin du produit, en journalier et en cumuls 10 jours.
4. 2018 (descriptif, sans référence) :
   - pluie de bassin journalière IMERG, MERRA-2 et forçage LIS (ENS_corr) pour Lalla Chafia et Sidi Jabeur, du 15 février au 15 mai ;
   - cumuls des épisodes de mars et d'avril pour chaque produit.
5. Sorties :
   - A3_*.csv, figures depuis les CSV, REPORT_A3.md (tableaux seulement).
"""

import os
import glob
import re
import time
import multiprocessing as mp
from collections import OrderedDict
import netCDF4 as nc
import numpy as np
import pandas as pd
import h5py
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
CACHE_DIR = os.path.join(BASE_DIR, "paper1/cache")
REPORT_PATH = os.path.join(BASE_DIR, "paper1/REPORT_A3.md")
ROOT_REPORT_PATH = os.path.join(BASE_DIR, "REPORT_A3.md")

os.makedirs(TABLES_DIR, exist_ok=True)
os.makedirs(FIGURES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

# Sources de donnees
STATIONS_CSV = os.path.expanduser("~/lustre/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/SCRIPTS/paper_dataset_precip/data/raw/stations/ABH_stations_plusziz_and_abhbc.csv")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
LIS_INPUT_FILE = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
IMERG_DIR = os.path.join(BASE_DIR, "data/forcing/IMERG/raw")
MERRA2_FLX_DIR = os.path.join(BASE_DIR, "data/forcing/MERRA2/M2T1NXFLX")
MERRA2_ALT_DIR = os.path.join(BASE_DIR, "data/forcing/MERRA2/MERRA2_400")
ENS_CORR_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL")

P0, P1 = pd.Timestamp("2001-01-01"), pd.Timestamp("2014-12-31")
TOTAL_DAYS_EVAL = (P1 - P0).days + 1 # 5113 jours

print("=" * 80)
print("Step A3 — Evaluation des Precipitations (H5)")
print(f"Periode d evaluation stations : {P0:%Y-%m-%d} -> {P1:%Y-%m-%d} ({TOTAL_DAYS_EVAL} jours)")
print("=" * 80)

# ==============================================================================
# 1. Grille LIS, Modeles Numeriques de Terrain et Masques des Bassins Versants
# ==============================================================================
print("\n>>> [1/7] Chargement de la topographie lis_input et delimitation des bassins HyMAP...")

with nc.Dataset(LIS_INPUT_FILE) as ds:
    grid_elev = ds["ELEVATION"][:].squeeze() # shape (121, 181)
    grid_lat = ds["lat"][:].squeeze()
    grid_lon = ds["lon"][:].squeeze()

with nc.Dataset(LDT_FILE) as ds:
    hymap_flow_x = ds["HYMAP_flow_direction_x"][:]
    hymap_flow_y = ds["HYMAP_flow_direction_y"][:]
    hymap_glat = ds["lat"][:]
    hymap_glon = ds["lon"][:]
    hymap_area = ds["HYMAP_grid_area"][:].filled(0.0) # (120, 180)
    dx_hymap, dy_hymap = float(ds.DX), float(ds.DY)

R_hy, C_hy = hymap_flow_x.shape
down_r = np.full((R_hy, C_hy), -1, dtype=int)
down_c = np.full((R_hy, C_hy), -1, dtype=int)
for c in range(C_hy):
    for r in range(R_hy):
        if not np.ma.is_masked(hymap_flow_x[r, c]) and hymap_flow_x[r, c] != -9999.0:
            vx, vy = int(round(hymap_flow_x[r, c])), int(round(hymap_flow_y[r, c]))
            if 1 <= vx <= C_hy and 1 <= vy <= R_hy:
                down_c[r, c], down_r[r, c] = vx - 1, vy - 1

parents = {}
for r in range(R_hy):
    for c in range(C_hy):
        pr, pc = down_r[r, c], down_c[r, c]
        if pr >= 0 and pc >= 0:
            parents.setdefault((pr, pc), []).append((r, c))

def get_catchment_cells(orow, ocol):
    vis = set([(orow, ocol)])
    q = [(orow, ocol)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis

cells_lc = get_catchment_cells(75, 71)
cells_sj = get_catchment_cells(71, 71)
cells_az = get_catchment_cells(75, 108)

catchments = OrderedDict([
    ("Lalla Chafia", cells_lc),
    ("Sidi Jabeur", cells_sj),
    ("Sebou amont", cells_az),
])

print(f"  Mailles HyMAP D8 : Lalla Chafia={len(cells_lc)}, Sidi Jabeur={len(cells_sj)}, Sebou amont={len(cells_az)}")

weights_181 = {}
for cname, ccells in catchments.items():
    w181 = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        a = hymap_area[r, c]
        w181[r, c] += 0.25 * a
        w181[r, c+1] += 0.25 * a
        w181[r+1, c] += 0.25 * a
        w181[r+1, c+1] += 0.25 * a
    weights_181[cname] = w181 / np.sum(w181)

# ==============================================================================
# 2. Nettoyage et Filtrage des Stations (2001–2014)
# ==============================================================================
print("\n>>> [2/7] Nettoyage et contrôle des pluviomètres ABH (2001–2014)...")

df_raw_all = pd.read_csv(STATIONS_CSV, dtype=str)
df_raw_all["Date"] = pd.to_datetime(df_raw_all["Date"], errors="coerce")
df_raw_all["Precipitation"] = pd.to_numeric(df_raw_all["Precipitation"], errors="coerce")
df_raw_all["Longitude"] = pd.to_numeric(df_raw_all["Longitude"], errors="coerce")
df_raw_all["Latitude"] = pd.to_numeric(df_raw_all["Latitude"], errors="coerce")

df_sub = df_raw_all[(df_raw_all["Date"] >= P0) & (df_raw_all["Date"] <= P1)].copy()

stations_list = sorted(df_sub["Station"].unique())
stations_metadata = []
clean_station_series = {}

for st in stations_list:
    grp = df_sub[df_sub["Station"] == st].copy()
    n_raw_records = len(grp)
    lon_st = float(grp["Longitude"].iloc[0])
    lat_st = float(grp["Latitude"].iloc[0])
    
    date_counts = grp.groupby("Date")["Precipitation"].count()
    date_nuniques = grp.groupby("Date")["Precipitation"].nunique()
    
    conflict_dates = set(date_nuniques[date_nuniques > 1].index)
    n_conflict_dates = len(conflict_dates)
    
    identical_dup_dates = set(date_nuniques[(date_nuniques == 1) & (date_counts > 1)].index)
    n_identical_dup_kept = len(identical_dup_dates)
    
    grp_noconflict = grp[~grp["Date"].isin(conflict_dates)].drop_duplicates(subset=["Date", "Precipitation"])
    grp_single_date = grp_noconflict.drop_duplicates(subset=["Date"]).copy()
    
    gt300_mask = grp_single_date["Precipitation"] > 300.0
    n_gt300 = int(gt300_mask.sum())
    
    grp_valid = grp_single_date[~gt300_mask & (grp_single_date["Precipitation"] >= 0.0)].copy()
    n_valid_days = len(grp_valid)
    pct_valid_days = round(100.0 * n_valid_days / TOTAL_DAYS_EVAL, 2)
    is_selected_ge80 = (pct_valid_days >= 80.0)
    
    hymap_lat0, hymap_lon0 = float(hymap_glat[0, 0]), float(hymap_glon[0, 0])
    hy_r = int(np.floor((lat_st - (hymap_lat0 - dy_hymap/2)) / dy_hymap))
    hy_c = int(np.floor((lon_st - (hymap_lon0 - dx_hymap/2)) / dx_hymap))
    
    in_domain = (30.0 <= lat_st <= 36.0) and (-10.0 <= lon_st <= -1.0)
    
    if (hy_r, hy_c) in cells_lc:
        basin_name = "Lalla Chafia"
    elif (hy_r, hy_c) in cells_sj:
        basin_name = "Sidi Jabeur"
    elif (hy_r, hy_c) in cells_az:
        basin_name = "Sebou amont"
    elif in_domain:
        basin_name = "Domaine complet"
    else:
        basin_name = "Hors domaine"
        
    if in_domain:
        lis_r = int(np.round((lat_st - 30.0) / 0.05))
        lis_c = int(np.round((lon_st - (-10.0)) / 0.05))
        lis_r = max(0, min(120, lis_r))
        lis_c = max(0, min(180, lis_c))
        
        # Si la maille directe est masquee (mer/ocean cotiere), chercher la maille terre valide la plus proche
        if np.ma.is_masked(grid_elev[lis_r, lis_c]) or np.isnan(grid_elev[lis_r, lis_c]):
            best_d = 1e9
            best_elev = None
            for dr in range(-6, 7):
                for dc in range(-6, 7):
                    rr, cc = lis_r + dr, lis_c + dc
                    if 0 <= rr < 121 and 0 <= cc < 181:
                        if not np.ma.is_masked(grid_elev[rr, cc]) and not np.isnan(grid_elev[rr, cc]):
                            d = dr*dr + dc*dc
                            if d < best_d:
                                best_d = d
                                best_elev = float(grid_elev[rr, cc])
            elev_val = best_elev
        else:
            elev_val = float(grid_elev[lis_r, lis_c])

        if elev_val is not None and not np.isnan(elev_val):
            elev_str = f"{elev_val:.1f}"
            if elev_val < 500.0:
                elev_class = "< 500 m"
            elif elev_val < 1000.0:
                elev_class = "500-1000 m"
            elif elev_val < 1500.0:
                elev_class = "1000-1500 m"
            else:
                elev_class = ">= 1500 m"
        else:
            elev_val = np.nan
            elev_str = "absent"
            elev_class = "Hors domaine"
    else:
        elev_val = np.nan
        elev_str = "absent"
        elev_class = "Hors domaine"
        
    stations_metadata.append({
        "station": st,
        "longitude": round(lon_st, 5),
        "latitude": round(lat_st, 5),
        "total_days_eval": TOTAL_DAYS_EVAL,
        "n_raw_records": n_raw_records,
        "n_dup_identical_kept": n_identical_dup_kept,
        "n_conflict_dates_excluded": n_conflict_dates,
        "n_gt300_excluded": n_gt300,
        "n_valid_days": n_valid_days,
        "pct_valid_days": pct_valid_days,
        "selected_ge80": "oui" if is_selected_ge80 else "non",
        "basin_a2b": basin_name,
        "elevation_lis_m": elev_str,
        "elevation_class": elev_class,
    })
    
    if is_selected_ge80:
        ser = grp_valid.set_index("Date")["Precipitation"].sort_index()
        clean_station_series[st] = ser

df_stations_meta = pd.DataFrame(stations_metadata)
out_meta_csv = os.path.join(TABLES_DIR, "A3_stations_clean_metadata.csv")
df_stations_meta.to_csv(out_meta_csv, index=False)
print(f"  [OK] Table des métadonnées stations enregistrée : {out_meta_csv} ({len(df_stations_meta)} stations)")

selected_stations = [r["station"] for r in stations_metadata if r["selected_ge80"] == "oui"]
print(f"  Stations sélectionnées (>= 80% valide) : {len(selected_stations)} / {len(stations_metadata)}")

selected_meta = df_stations_meta[df_stations_meta["selected_ge80"] == "oui"].set_index("station")
st_imerg_idx = {}
st_merra_idx = {}

for st in selected_stations:
    lon_s = selected_meta.loc[st, "longitude"]
    lat_s = selected_meta.loc[st, "latitude"]
    i_lon = int(round((lon_s - -179.95) / 0.1))
    i_lat = int(round((lat_s - -89.95) / 0.1))
    st_imerg_idx[st] = (i_lon, i_lat)
    
    m_lon = int(round((lon_s - -180.0) / 0.625))
    m_lat = int(round((lat_s - -90.0) / 0.5))
    st_merra_idx[st] = (m_lon, m_lat)

basin_imerg_weights = {}
basin_merra_weights = {}

for bname, ccells in catchments.items():
    tot_a = sum(hymap_area[r, c] for r, c in ccells)
    
    w_im = {}
    for r, c in ccells:
        glat_val = hymap_glat[r, c]
        glon_val = hymap_glon[r, c]
        i_l = int(round((glon_val - -179.95) / 0.1))
        i_t = int(round((glat_val - -89.95) / 0.1))
        w_im[(i_l, i_t)] = w_im.get((i_l, i_t), 0.0) + (hymap_area[r, c] / tot_a)
    basin_imerg_weights[bname] = w_im
    
    w_me = {}
    for r, c in ccells:
        glat_val = hymap_glat[r, c]
        glon_val = hymap_glon[r, c]
        m_l = int(round((glon_val - -180.0) / 0.625))
        m_t = int(round((glat_val - -90.0) / 0.5))
        w_me[(m_l, m_t)] = w_me.get((m_l, m_t), 0.0) + (hymap_area[r, c] / tot_a)
    basin_merra_weights[bname] = w_me

# ==============================================================================
# 3. Extraction IMERG V07B et MERRA-2 PRECTOTCORR
# ==============================================================================
print("\n>>> [3/7] Extraction et accumulation journaliere des produits IMERG et MERRA-2...")

merra_cache_file = os.path.join(CACHE_DIR, "merra2_daily_stations_and_basins_2001_2014.npz")
all_eval_dates = pd.date_range(P0, P1).strftime("%Y-%m-%d").tolist()

if os.path.exists(merra_cache_file):
    print("  Chargement du cache MERRA-2 journalier...")
    merra_data = np.load(merra_cache_file, allow_pickle=True)
    merra_station_daily = merra_data["station_daily"].item()
    merra_basin_daily = merra_data["basin_daily"].item()
else:
    print("  Extraction de MERRA-2 PRECTOTCORR depuis les archives...")
    merra_files = glob.glob(os.path.join(MERRA2_FLX_DIR, "MERRA2_*.nc4"))
    merra_dict = {}
    for f in merra_files:
        m = re.search(r"\.(\d{8})\.nc4$", f)
        if m:
            merra_dict[m.group(1)] = f
            
    if len(merra_dict) < len(all_eval_dates):
        for f in glob.glob(os.path.join(MERRA2_ALT_DIR, "**/*.nc4"), recursive=True):
            m = re.search(r"\.(\d{8})\.nc4$", f)
            if m and m.group(1) not in merra_dict:
                merra_dict[m.group(1)] = f

    merra_station_daily = {st: np.full(len(all_eval_dates), np.nan, dtype=np.float32) for st in selected_stations}
    merra_basin_daily = {b: np.full(len(all_eval_dates), np.nan, dtype=np.float32) for b in catchments}
    
    def extract_single_day_merra(args):
        idx_d, d_str = args
        ymd = d_str.replace("-", "")
        fp = merra_dict.get(ymd)
        if fp is None or not os.path.exists(fp):
            return idx_d, None, None
        try:
            with nc.Dataset(fp) as ds:
                if "PRECTOTCORR" not in ds.variables:
                    return idx_d, None, None
                p_var = ds["PRECTOTCORR"]
                if p_var.shape[0] < 24:
                    return idx_d, None, None
                slice_p = p_var[:, 215:260, 250:300]
                p_day_box = np.sum(slice_p, axis=0) * 3600.0
                
                st_vals = {}
                for st in selected_stations:
                    ml, mt = st_merra_idx[st]
                    st_vals[st] = p_day_box[mt - 215, ml - 250]
                    
                b_vals = {}
                for bname, w_dict in basin_merra_weights.items():
                    bv = 0.0
                    for (ml, mt), w in w_dict.items():
                        bv += p_day_box[mt - 215, ml - 250] * w
                    b_vals[bname] = bv
                return idx_d, st_vals, b_vals
        except Exception:
            return idx_d, None, None

    t0 = time.time()
    task_args = list(enumerate(all_eval_dates))
    n_done_m = 0
    with mp.Pool(28) as pool:
        for idx_d, st_v, b_v in pool.imap_unordered(extract_single_day_merra, task_args, chunksize=64):
            n_done_m += 1
            if n_done_m % 1000 == 0 or n_done_m == len(all_eval_dates):
                print(f"    [MERRA-2] {n_done_m}/{len(all_eval_dates)} jours traités ({100.0*n_done_m/len(all_eval_dates):.1f}%)", flush=True)
            if st_v is not None:
                for st in selected_stations:
                    merra_station_daily[st][idx_d] = st_v[st]
                for bname in catchments:
                    merra_basin_daily[bname][idx_d] = b_v[bname]
            
    print(f"  [OK] Extraction MERRA-2 terminee en {time.time()-t0:.1f} s")
    np.savez_compressed(merra_cache_file, station_daily=merra_station_daily, basin_daily=merra_basin_daily)

imerg_cache_file = os.path.join(CACHE_DIR, "imerg_daily_stations_and_basins_2001_2014.npz")

if os.path.exists(imerg_cache_file):
    print("  Chargement du cache IMERG journalier...")
    imerg_data = np.load(imerg_cache_file, allow_pickle=True)
    imerg_station_daily = imerg_data["station_daily"].item()
    imerg_basin_daily = imerg_data["basin_daily"].item()
else:
    print("  Extraction parallèle de IMERG V07B (28 workers)...")
    imerg_station_daily = {st: np.full(len(all_eval_dates), np.nan, dtype=np.float32) for st in selected_stations}
    imerg_basin_daily = {b: np.full(len(all_eval_dates), np.nan, dtype=np.float32) for b in catchments}
    
    months_keys = sorted(list(set(d[:7].replace("-", "") for d in all_eval_dates)))
    month_file_map = {}
    for ym in months_keys:
        d_dir = os.path.join(IMERG_DIR, ym)
        if os.path.exists(d_dir):
            flist = sorted(glob.glob(os.path.join(d_dir, "3B-HHR.MS.MRG.3IMERG.*.V07B.HDF5")))
            by_day = {}
            for f in flist:
                fn = os.path.basename(f)
                d_day = fn[21:29]
                by_day.setdefault(d_day, []).append(f)
            month_file_map[ym] = by_day
        else:
            month_file_map[ym] = {}
            
    def extract_single_day_imerg(args):
        idx_d, d_str = args
        ymd = d_str.replace("-", "")
        ym = ymd[:6]
        day_files = month_file_map.get(ym, {}).get(ymd, [])
        if len(day_files) != 48:
            return idx_d, None, None
            
        daily_sum = np.zeros((200, 180), dtype=np.float32)
        try:
            for f in day_files:
                with h5py.File(f, "r") as hf:
                    p = hf["Grid/precipitation"][0, 1600:1800, 1100:1280]
                    daily_sum += np.where(p >= 0, p * 0.5, 0.0)
                    
            st_vals = {}
            for st in selected_stations:
                il, it = st_imerg_idx[st]
                st_vals[st] = daily_sum[il - 1600, it - 1100]
                
            b_vals = {}
            for bname, w_dict in basin_imerg_weights.items():
                bv = 0.0
                for (il, it), w in w_dict.items():
                    bv += daily_sum[il - 1600, it - 1100] * w
                b_vals[bname] = bv
                
            return idx_d, st_vals, b_vals
        except Exception:
            return idx_d, None, None

    t0 = time.time()
    task_args = list(enumerate(all_eval_dates))
    n_done_im = 0
    with mp.Pool(28) as pool:
        for idx_d, st_v, b_v in pool.imap_unordered(extract_single_day_imerg, task_args, chunksize=16):
            n_done_im += 1
            if n_done_im % 500 == 0 or n_done_im == len(all_eval_dates):
                elapsed = time.time() - t0
                pct = 100.0 * n_done_im / len(all_eval_dates)
                rate = n_done_im / elapsed if elapsed > 0 else 0
                eta = (len(all_eval_dates) - n_done_im) / rate if rate > 0 else 0
                print(f"    [IMERG] {n_done_im}/{len(all_eval_dates)} jours traités ({pct:.1f}%) - {rate:.1f} j/s - ETA: {eta:.0f}s", flush=True)
            if st_v is not None:
                for st in selected_stations:
                    imerg_station_daily[st][idx_d] = st_v[st]
                for bname in catchments:
                    imerg_basin_daily[bname][idx_d] = b_v[bname]
                    
    print(f"  [OK] Extraction IMERG terminee en {time.time()-t0:.1f} s")
    np.savez_compressed(imerg_cache_file, station_daily=imerg_station_daily, basin_daily=imerg_basin_daily)

# ==============================================================================
# 4. Test du Décalage de Jour (-1, 0, +1) et Gel du Meilleur Décalage
# ==============================================================================
print("\n>>> [4/7] Test du décalage temporel (-1, 0, +1 jour) par corrélation journalière...")

dates_idx = pd.DatetimeIndex(all_eval_dates)
lag_testing_records = []

optimal_lag_by_product = {}

for prod_name, prod_dict in [("IMERG", imerg_station_daily), ("MERRA-2", merra_station_daily)]:
    corr_lags = {-1: [], 0: [], 1: []}
    
    for st in selected_stations:
        obs_ser = clean_station_series[st]
        prod_ser = pd.Series(prod_dict[st], index=dates_idx)
        
        row_rec = {"product": prod_name, "station": st}
        r_by_lag = {}
        
        for lag in [-1, 0, 1]:
            shifted_prod = prod_ser.shift(-lag)
            combined = pd.DataFrame({"obs": obs_ser, "prod": shifted_prod}).dropna()
            
            if len(combined) >= 30 and combined["obs"].std() > 0 and combined["prod"].std() > 0:
                r_val = float(combined["obs"].corr(combined["prod"]))
            else:
                r_val = np.nan
            r_by_lag[lag] = r_val
            corr_lags[lag].append(r_val)
            row_rec[f"corr_lag_{lag}"] = round(r_val, 4) if pd.notnull(r_val) else "N/A"
            
        best_lag = max(r_by_lag.keys(), key=lambda l: (r_by_lag[l] if pd.notnull(r_by_lag[l]) else -999))
        row_rec["best_lag"] = best_lag
        row_rec["best_corr"] = round(r_by_lag[best_lag], 4) if pd.notnull(r_by_lag[best_lag]) else "N/A"
        lag_testing_records.append(row_rec)
        
    mean_corr = {l: np.nanmean(corr_lags[l]) for l in [-1, 0, 1]}
    best_prod_lag = max(mean_corr.keys(), key=lambda l: mean_corr[l])
    optimal_lag_by_product[prod_name] = best_prod_lag
    print(f"  Produit {prod_name} : r(lag -1)={mean_corr[-1]:.4f}, r(lag 0)={mean_corr[0]:.4f}, r(lag +1)={mean_corr[1]:.4f} -> Meilleur décalage retenu = {best_prod_lag:+d} jour")

df_lag_test = pd.DataFrame(lag_testing_records)
out_lag_csv = os.path.join(TABLES_DIR, "A3_lag_correlation_testing.csv")
df_lag_test.to_csv(out_lag_csv, index=False)
print(f"  [OK] Table de test des décalages enregistrée : {out_lag_csv} ({len(df_lag_test)} lignes)")

# ==============================================================================
# 5. Calcul des Métriques Pluviométriques Détaillées et Agrégation
# ==============================================================================
print("\n>>> [5/7] Calcul des métriques statistiques et des scores de contingence (POD, FAR, CSI)...")

def compute_metrics_vector(obs_arr, prod_arr):
    n_days = len(obs_arr)
    if n_days == 0:
        return {}
        
    sum_obs = float(np.sum(obs_arr))
    sum_prod = float(np.sum(prod_arr))
    ratio_cumul = round(sum_prod / sum_obs, 4) if sum_obs > 0 else np.nan
    
    n_ge1_obs = int(np.sum(obs_arr >= 1.0))
    n_ge1_prod = int(np.sum(prod_arr >= 1.0))
    freq_ge1_obs = round(n_ge1_obs / n_days, 4)
    freq_ge1_prod = round(n_ge1_prod / n_days, 4)
    
    int_obs = round(float(np.mean(obs_arr[obs_arr >= 1.0])), 2) if n_ge1_obs > 0 else np.nan
    int_prod = round(float(np.mean(prod_arr[prod_arr >= 1.0])), 2) if n_ge1_prod > 0 else np.nan
    
    contingency = {}
    for th in [1.0, 10.0, 30.0]:
        th_int = int(th)
        b_obs = (obs_arr >= th)
        b_prod = (prod_arr >= th)
        hits = int(np.sum(b_obs & b_prod))
        false_alarms = int(np.sum(~b_obs & b_prod))
        misses = int(np.sum(b_obs & ~b_prod))
        
        pod = round(hits / (hits + misses), 4) if (hits + misses) > 0 else np.nan
        far = round(false_alarms / (hits + false_alarms), 4) if (hits + false_alarms) > 0 else np.nan
        csi = round(hits / (hits + false_alarms + misses), 4) if (hits + false_alarms + misses) > 0 else np.nan
        
        contingency[f"POD_ge_{th_int}mm"] = pod
        contingency[f"FAR_ge_{th_int}mm"] = far
        contingency[f"CSI_ge_{th_int}mm"] = csi
        
    rainy_obs = obs_arr[obs_arr >= 1.0]
    rainy_prod = prod_arr[prod_arr >= 1.0]
    
    q95_obs = round(float(np.percentile(rainy_obs, 95)), 2) if len(rainy_obs) >= 20 else np.nan
    q95_prod = round(float(np.percentile(rainy_prod, 95)), 2) if len(rainy_prod) >= 20 else np.nan
    q99_obs = round(float(np.percentile(rainy_obs, 99)), 2) if len(rainy_obs) >= 50 else np.nan
    q99_prod = round(float(np.percentile(rainy_prod, 99)), 2) if len(rainy_prod) >= 50 else np.nan
    
    n_top1pct = max(1, int(round(0.01 * n_days)))
    top_obs_idx = np.argsort(obs_arr)[-n_top1pct:]
    sum_top_obs = float(np.sum(obs_arr[top_obs_idx]))
    sum_top_prod = float(np.sum(prod_arr[top_obs_idx]))
    ratio_top1pct = round(sum_top_prod / sum_top_obs, 4) if sum_top_obs > 0 else np.nan
    
    r_val = round(float(np.corrcoef(obs_arr, prod_arr)[0, 1]), 4) if np.std(obs_arr) > 0 and np.std(prod_arr) > 0 else np.nan
    
    res = {
        "n_common_valid_days": n_days,
        "sum_obs_mm": round(sum_obs, 1),
        "sum_prod_mm": round(sum_prod, 1),
        "ratio_cumul_prod_over_obs": ratio_cumul,
        "corr_journaliere": r_val,
        "freq_ge_1mm_obs": freq_ge1_obs,
        "freq_ge_1mm_prod": freq_ge1_prod,
        "intensite_moyenne_pluvieuse_obs": int_obs,
        "intensite_moyenne_pluvieuse_prod": int_prod,
        "Q95_pluvieux_obs_mm": q95_obs,
        "Q95_pluvieux_prod_mm": q95_prod,
        "Q99_pluvieux_obs_mm": q99_obs,
        "Q99_pluvieux_prod_mm": q99_prod,
        "ratio_cumul_top1pct_jours": ratio_top1pct,
    }
    res.update(contingency)
    return res

station_metrics_records = []

season_months = {
    "Annuel": list(range(1, 13)),
    "JF+D": [1, 2, 12],
    "MAM": [3, 4, 5],
    "JJA": [6, 7, 8],
    "SON": [9, 10, 11]
}

for prod_name, prod_dict in [("IMERG", imerg_station_daily), ("MERRA-2", merra_station_daily)]:
    best_lag = optimal_lag_by_product[prod_name]
    
    for st in selected_stations:
        obs_ser = clean_station_series[st]
        prod_ser = pd.Series(prod_dict[st], index=dates_idx).shift(-best_lag)
        
        meta = selected_meta.loc[st]
        basin = meta["basin_a2b"]
        elev_c = meta["elevation_class"]
        elev_m = meta["elevation_lis_m"]
        
        df_pair = pd.DataFrame({"obs": obs_ser, "prod": prod_ser}).dropna()
        df_pair["month"] = df_pair.index.month
        
        for sname, mlist in season_months.items():
            sub_season = df_pair[df_pair["month"].isin(mlist)]
            if len(sub_season) >= 15:
                mets = compute_metrics_vector(sub_season["obs"].values, sub_season["prod"].values)
            else:
                mets = {k: "N/A" for k in [
                    "n_common_valid_days", "sum_obs_mm", "sum_prod_mm", "ratio_cumul_prod_over_obs",
                    "corr_journaliere", "freq_ge_1mm_obs", "freq_ge_1mm_prod", "intensite_moyenne_pluvieuse_obs",
                    "intensite_moyenne_pluvieuse_prod", "Q95_pluvieux_obs_mm", "Q95_pluvieux_prod_mm",
                    "Q99_pluvieux_obs_mm", "Q99_pluvieux_prod_mm", "ratio_cumul_top1pct_jours",
                    "POD_ge_1mm", "FAR_ge_1mm", "CSI_ge_1mm",
                    "POD_ge_10mm", "FAR_ge_10mm", "CSI_ge_10mm",
                    "POD_ge_30mm", "FAR_ge_30mm", "CSI_ge_30mm"
                ]}
            rec = {
                "product": prod_name,
                "applied_lag_days": best_lag,
                "station": st,
                "season": sname,
                "basin_a2b": basin,
                "elevation_class": elev_c,
                "elevation_lis_m": elev_m,
                "longitude": meta["longitude"],
                "latitude": meta["latitude"],
            }
            rec.update(mets)
            station_metrics_records.append(rec)

df_station_metrics = pd.DataFrame(station_metrics_records)
out_st_metrics_csv = os.path.join(TABLES_DIR, "A3_precipitation_metrics_stations.csv")
df_station_metrics.to_csv(out_st_metrics_csv, index=False)
print(f"  [OK] Table des métriques par station enregistrée : {out_st_metrics_csv} ({len(df_station_metrics)} lignes)")

# Aggregation des metriques par bassin, par classe d altitude et par saison
print("  Agrégation des métriques par groupe...")
agg_records = []
metrics_numeric_cols = [
    "ratio_cumul_prod_over_obs", "corr_journaliere", "freq_ge_1mm_obs", "freq_ge_1mm_prod",
    "intensite_moyenne_pluvieuse_obs", "intensite_moyenne_pluvieuse_prod",
    "Q95_pluvieux_obs_mm", "Q95_pluvieux_prod_mm", "Q99_pluvieux_obs_mm", "Q99_pluvieux_prod_mm",
    "ratio_cumul_top1pct_jours",
    "POD_ge_1mm", "FAR_ge_1mm", "CSI_ge_1mm",
    "POD_ge_10mm", "FAR_ge_10mm", "CSI_ge_10mm",
    "POD_ge_30mm", "FAR_ge_30mm", "CSI_ge_30mm"
]

df_st_num = df_station_metrics.copy()
for col in metrics_numeric_cols:
    df_st_num[col] = pd.to_numeric(df_st_num[col], errors="coerce")

for prod_name in ["IMERG", "MERRA-2"]:
    sub_prod = df_st_num[df_st_num["product"] == prod_name]
    best_lag = optimal_lag_by_product[prod_name]
    
    for sname in ["Annuel", "JF+D", "MAM", "JJA", "SON"]:
        sub_s = sub_prod[sub_prod["season"] == sname]
        
        # 1. Domaine complet LIS (toutes stations in_domain)
        sub_dom = sub_s[sub_s["basin_a2b"] != "Hors domaine"]
        rec = {
            "product": prod_name, "applied_lag_days": best_lag, "aggregation_type": "basin",
            "group_name": "Domaine complet", "season": sname, "n_stations": len(sub_dom)
        }
        for col in metrics_numeric_cols:
            rec[f"{col}_mean"] = round(float(sub_dom[col].mean()), 4) if sub_dom[col].count() > 0 else "N/A"
            rec[f"{col}_median"] = round(float(sub_dom[col].median()), 4) if sub_dom[col].count() > 0 else "N/A"
        agg_records.append(rec)
        
        # 2. Bassins specifiques A2b
        for bname in ["Lalla Chafia", "Sidi Jabeur", "Sebou amont"]:
            sub_b = sub_s[sub_s["basin_a2b"] == bname]
            rec = {
                "product": prod_name, "applied_lag_days": best_lag, "aggregation_type": "basin",
                "group_name": bname, "season": sname, "n_stations": len(sub_b)
            }
            for col in metrics_numeric_cols:
                rec[f"{col}_mean"] = round(float(sub_b[col].mean()), 4) if sub_b[col].count() > 0 else "N/A"
                rec[f"{col}_median"] = round(float(sub_b[col].median()), 4) if sub_b[col].count() > 0 else "N/A"
            agg_records.append(rec)
            
        # 3. Classes d altitude
        for e_class in ["< 500 m", "500-1000 m", "1000-1500 m", ">= 1500 m"]:
            sub_e = sub_s[sub_s["elevation_class"] == e_class]
            rec = {
                "product": prod_name, "applied_lag_days": best_lag, "aggregation_type": "elevation_class",
                "group_name": e_class, "season": sname, "n_stations": len(sub_e)
            }
            for col in metrics_numeric_cols:
                rec[f"{col}_mean"] = round(float(sub_e[col].mean()), 4) if sub_e[col].count() > 0 else "N/A"
                rec[f"{col}_median"] = round(float(sub_e[col].median()), 4) if sub_e[col].count() > 0 else "N/A"
            agg_records.append(rec)

df_agg_metrics = pd.DataFrame(agg_records)
out_agg_metrics_csv = os.path.join(TABLES_DIR, "A3_precipitation_metrics_aggregated.csv")
df_agg_metrics.to_csv(out_agg_metrics_csv, index=False)
print(f"  [OK] Table des métriques agrégées enregistrée : {out_agg_metrics_csv} ({len(df_agg_metrics)} lignes)")

# ==============================================================================
# 6. Bassins Versants (>= 2 stations) : Moyenne Stations vs Moyenne de Bassin
# ==============================================================================
print("\n>>> [6/7] Analyse de bassin (Lalla Chafia, Sidi Jabeur, Sebou amont) : stations vs produit...")

catchment_comparison_records = []

for bname, ccells in catchments.items():
    st_in_b = [s for s in selected_stations if df_stations_meta.loc[df_stations_meta["station"]==s, "basin_a2b"].values[0] == bname]
    if len(st_in_b) < 2:
        continue
        
    st_df = pd.DataFrame({s: clean_station_series[s] for s in st_in_b})
    st_mean_daily = st_df.mean(axis=1)
    
    for prod_name, prod_basin_dict in [("IMERG", imerg_basin_daily), ("MERRA-2", merra_basin_daily)]:
        best_lag = optimal_lag_by_product[prod_name]
        prod_ser = pd.Series(prod_basin_dict[bname], index=dates_idx).shift(-best_lag)
        
        pair_daily = pd.DataFrame({"obs": st_mean_daily, "prod": prod_ser}).dropna()
        
        mets_daily = compute_metrics_vector(pair_daily["obs"].values, pair_daily["prod"].values)
        bias_d = round(float(np.mean(pair_daily["prod"] - pair_daily["obs"])), 3)
        rmse_d = round(float(np.sqrt(np.mean((pair_daily["prod"] - pair_daily["obs"])**2))), 3)
        
        catchment_comparison_records.append({
            "basin": bname,
            "product": prod_name,
            "applied_lag_days": best_lag,
            "time_scale": "journalier",
            "n_stations_in_basin": len(st_in_b),
            "stations_list": "; ".join(st_in_b),
            "n_periods": len(pair_daily),
            "sum_stations_mean_mm": mets_daily["sum_obs_mm"],
            "sum_basin_product_mm": mets_daily["sum_prod_mm"],
            "ratio_cumul_prod_over_stations": mets_daily["ratio_cumul_prod_over_obs"],
            "bias_mean_mm": bias_d,
            "rmse_mm": rmse_d,
            "corr": mets_daily["corr_journaliere"],
            "POD_ge_1mm": mets_daily["POD_ge_1mm"],
            "FAR_ge_1mm": mets_daily["FAR_ge_1mm"],
            "CSI_ge_1mm": mets_daily["CSI_ge_1mm"],
            "POD_ge_10mm": mets_daily["POD_ge_10mm"],
            "FAR_ge_10mm": mets_daily["FAR_ge_10mm"],
            "CSI_ge_10mm": mets_daily["CSI_ge_10mm"],
            "POD_ge_30mm": mets_daily["POD_ge_30mm"],
            "FAR_ge_30mm": mets_daily["FAR_ge_30mm"],
            "CSI_ge_30mm": mets_daily["CSI_ge_30mm"],
        })
        
        pair_daily["block10"] = np.arange(len(pair_daily)) // 10
        pair_10d = pair_daily.groupby("block10")[["obs", "prod"]].sum()
        counts_10d = pair_daily.groupby("block10")["obs"].count()
        pair_10d = pair_10d[counts_10d == 10]
        
        sum_10d_obs = float(pair_10d["obs"].sum())
        sum_10d_prod = float(pair_10d["prod"].sum())
        ratio_10d = round(sum_10d_prod / sum_10d_obs, 4) if sum_10d_obs > 0 else np.nan
        bias_10d = round(float(np.mean(pair_10d["prod"] - pair_10d["obs"])), 3)
        rmse_10d = round(float(np.sqrt(np.mean((pair_10d["prod"] - pair_10d["obs"])**2))), 3)
        r_10d = round(float(pair_10d["obs"].corr(pair_10d["prod"])), 4) if len(pair_10d) > 2 else np.nan
        
        catchment_comparison_records.append({
            "basin": bname,
            "product": prod_name,
            "applied_lag_days": best_lag,
            "time_scale": "cumul_10_jours",
            "n_stations_in_basin": len(st_in_b),
            "stations_list": "; ".join(st_in_b),
            "n_periods": len(pair_10d),
            "sum_stations_mean_mm": round(sum_10d_obs, 1),
            "sum_basin_product_mm": round(sum_10d_prod, 1),
            "ratio_cumul_prod_over_stations": ratio_10d,
            "bias_mean_mm": bias_10d,
            "rmse_mm": rmse_10d,
            "corr": r_10d,
            "POD_ge_1mm": "N/A", "FAR_ge_1mm": "N/A", "CSI_ge_1mm": "N/A",
            "POD_ge_10mm": "N/A", "FAR_ge_10mm": "N/A", "CSI_ge_10mm": "N/A",
            "POD_ge_30mm": "N/A", "FAR_ge_30mm": "N/A", "CSI_ge_30mm": "N/A",
        })

df_catchment_comp = pd.DataFrame(catchment_comparison_records)
out_catchment_csv = os.path.join(TABLES_DIR, "A3_catchment_stations_vs_basin_products.csv")
df_catchment_comp.to_csv(out_catchment_csv, index=False)
print(f"  [OK] Table de comparaison de bassin enregistrée : {out_catchment_csv} ({len(df_catchment_comp)} lignes)")

# ==============================================================================
# 7. Année 2018 (15 février au 15 mai) : IMERG, MERRA-2 et Forçage LIS (ENS_corr)
# ==============================================================================
print("\n>>> [7/7] Analyse de la saison hydrologique 2018 (15 février - 15 mai)...")

dates_2018_hydro = pd.date_range("2018-02-15", "2018-05-15").strftime("%Y-%m-%d").tolist()
forcing_2018_cache = os.path.join(CACHE_DIR, "forcing_2018_hydro_season_basins.npz")

if os.path.exists(forcing_2018_cache):
    print("  Chargement du cache forçages 2018...")
    d2018 = np.load(forcing_2018_cache, allow_pickle=True)
    p_imerg_2018 = d2018["imerg"].item()
    p_merra_2018 = d2018["merra"].item()
    p_lis_2018 = d2018["lis"].item()
else:
    print("  Extraction des forçages 2018 pour Lalla Chafia et Sidi Jabeur...")
    p_imerg_2018 = {b: np.full(len(dates_2018_hydro), np.nan, dtype=np.float32) for b in ["Lalla Chafia", "Sidi Jabeur"]}
    p_merra_2018 = {b: np.full(len(dates_2018_hydro), np.nan, dtype=np.float32) for b in ["Lalla Chafia", "Sidi Jabeur"]}
    p_lis_2018 = {b: np.full(len(dates_2018_hydro), np.nan, dtype=np.float32) for b in ["Lalla Chafia", "Sidi Jabeur"]}
    
    for idx_d, d_str in enumerate(dates_2018_hydro):
        ymd = d_str.replace("-", "")
        ym = ymd[:6]
        flist = sorted(glob.glob(os.path.join(IMERG_DIR, ym, f"3B-HHR.MS.MRG.3IMERG.{ymd}-S*.V07B.HDF5")))
        if len(flist) == 48:
            daily_box = np.zeros((200, 180), dtype=np.float32)
            for f in flist:
                with h5py.File(f, "r") as hf:
                    p = hf["Grid/precipitation"][0, 1600:1800, 1100:1280]
                    daily_box += np.where(p >= 0, p * 0.5, 0.0)
            for bname in ["Lalla Chafia", "Sidi Jabeur"]:
                bv = sum(daily_box[il - 1600, it - 1100] * w for (il, it), w in basin_imerg_weights[bname].items())
                p_imerg_2018[bname][idx_d] = bv
                
    for idx_d, d_str in enumerate(dates_2018_hydro):
        ymd = d_str.replace("-", "")
        m_files = glob.glob(os.path.join(MERRA2_FLX_DIR, f"MERRA2_*.{ymd}.nc4"))
        if not m_files:
            m_files = glob.glob(os.path.join(MERRA2_ALT_DIR, f"**/*.{ymd}.nc4"), recursive=True)
        if m_files and os.path.exists(m_files[0]):
            with nc.Dataset(m_files[0]) as ds:
                p_var = ds["PRECTOTCORR"]
                if p_var.shape[0] >= 24:
                    slice_p = p_var[:, 215:260, 250:300]
                    p_day_box = np.sum(slice_p, axis=0) * 3600.0
                    for bname in ["Lalla Chafia", "Sidi Jabeur"]:
                        bv = sum(p_day_box[mt - 215, ml - 250] * w for (ml, mt), w in basin_merra_weights[bname].items())
                        p_merra_2018[bname][idx_d] = bv
                        
    for idx_d, d_str in enumerate(dates_2018_hydro):
        dt_curr = pd.to_datetime(d_str)
        dt_next = dt_curr + pd.Timedelta(days=1)
        ymd_next = dt_next.strftime("%Y%m%d")
        ym_next = ymd_next[:6]
        f_lis = os.path.join(ENS_CORR_DIR, ym_next, f"LIS_HIST_{ymd_next}0000.d01.nc")
        if os.path.exists(f_lis):
            with nc.Dataset(f_lis) as ds:
                p_lis_grid = ds["TotalPrecip_tavg"][:].squeeze() * 86400.0
                for bname in ["Lalla Chafia", "Sidi Jabeur"]:
                    p_lis_2018[bname][idx_d] = float(np.sum(p_lis_grid * weights_181[bname]))
                    
    np.savez_compressed(forcing_2018_cache, imerg=p_imerg_2018, merra=p_merra_2018, lis=p_lis_2018)
    print("  [OK] Extraction forçages 2018 terminée et sauvegardée dans le cache.")

episodes = OrderedDict([
    ("Episode début Mars", ("2018-03-01", "2018-03-10")),
    ("Episode mi-Mars", ("2018-03-15", "2018-03-20")),
    ("Episode fin Avril", ("2018-04-20", "2018-04-26")),
    ("Total Mois de Mars", ("2018-03-01", "2018-03-31")),
    ("Total Mois d Avril", ("2018-04-01", "2018-04-30")),
    ("Total Période (15 fév - 15 mai)", ("2018-02-15", "2018-05-15")),
])

forcing_comp_records = []
dt_2018_series = pd.to_datetime(dates_2018_hydro)

for bname in ["Lalla Chafia", "Sidi Jabeur"]:
    ser_im = pd.Series(p_imerg_2018[bname], index=dt_2018_series)
    ser_me = pd.Series(p_merra_2018[bname], index=dt_2018_series)
    ser_lis = pd.Series(p_lis_2018[bname], index=dt_2018_series)
    
    for ep_name, (d_start, d_end) in episodes.items():
        sub_im = ser_im.loc[d_start:d_end]
        sub_me = ser_me.loc[d_start:d_end]
        sub_lis = ser_lis.loc[d_start:d_end]
        
        cum_im = round(float(sub_im.sum()), 2)
        cum_me = round(float(sub_me.sum()), 2)
        cum_lis = round(float(sub_lis.sum()), 2)
        
        ratio_im_lis = round(cum_im / cum_lis, 4) if cum_lis > 0 else np.nan
        ratio_me_lis = round(cum_me / cum_lis, 4) if cum_lis > 0 else np.nan
        ratio_im_me = round(cum_im / cum_me, 4) if cum_me > 0 else np.nan
        
        forcing_comp_records.append({
            "basin": bname,
            "period_or_episode": ep_name,
            "start_date": d_start,
            "end_date": d_end,
            "duration_days": (pd.to_datetime(d_end) - pd.to_datetime(d_start)).days + 1,
            "P_IMERG_V07B_mm": cum_im,
            "P_MERRA2_PRECTOTCORR_mm": cum_me,
            "P_LIS_ENS_corr_mm": cum_lis,
            "ratio_IMERG_over_LIS": ratio_im_lis,
            "ratio_MERRA2_over_LIS": ratio_me_lis,
            "ratio_IMERG_over_MERRA2": ratio_im_me,
        })

df_forcing_2018 = pd.DataFrame(forcing_comp_records)
out_forcing_2018_csv = os.path.join(TABLES_DIR, "A3_2018_basin_forcing_comparison.csv")
df_forcing_2018.to_csv(out_forcing_2018_csv, index=False)
print(f"  [OK] Table comparatif forçage 2018 enregistrée : {out_forcing_2018_csv} ({len(df_forcing_2018)} lignes)")

# ==============================================================================
# 8. Generation des Figures (Graphiques Publication-Quality)
# ==============================================================================
print("\n>>> Génération des figures cartographiques et diagnostiques...")

# Figure 1 : Carte des stations, classes d altitude et bassins
fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
cmap_topo = plt.cm.terrain
im = ax.imshow(grid_elev, extent=[-10.0, -1.0, 30.0, 36.0], origin="lower", cmap=cmap_topo, alpha=0.65, vmin=0, vmax=3000)
cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
cbar.set_label("Altitude MNT LIS (m)", fontsize=11)

for bname, ccells in catchments.items():
    color_b = "blue" if bname == "Lalla Chafia" else ("darkgreen" if bname == "Sidi Jabeur" else "purple")
    b_lons = [hymap_glon[r, c] for r, c in ccells]
    b_lats = [hymap_glat[r, c] for r, c in ccells]
    ax.scatter(b_lons, b_lats, s=1.5, color=color_b, alpha=0.3, label=f"Bassin {bname}")

st_in_dom = df_stations_meta[(df_stations_meta["selected_ge80"] == "oui") & (df_stations_meta["basin_a2b"] != "Hors domaine")]
st_out_dom = df_stations_meta[(df_stations_meta["selected_ge80"] == "oui") & (df_stations_meta["basin_a2b"] == "Hors domaine")]

sc = ax.scatter(st_in_dom["longitude"].values, st_in_dom["latitude"].values, c=pd.to_numeric(st_in_dom["elevation_lis_m"]).values,
                cmap="autumn_r", edgecolors="black", linewidths=0.5, s=40, zorder=5, label="Stations sélectionnées (>= 80%)")
ax.scatter(st_out_dom["longitude"].values, st_out_dom["latitude"].values, color="red", marker="x", s=35, zorder=5, label="Stations hors domaine")

ax.set_xlim(-10.2, -0.8)
ax.set_ylim(29.8, 36.2)
ax.set_xlabel("Longitude (°E)", fontsize=11)
ax.set_ylabel("Latitude (°N)", fontsize=11)
ax.set_title("Pluviomètres ABH Sélectionnés (2001–2014), Topographie et Bassins Versants", fontsize=12, fontweight="bold")
ax.grid(True, linestyle="--", alpha=0.4)
ax.legend(loc="lower left", fontsize=9, framealpha=0.9)
plt.tight_layout()
fig1_path = os.path.join(FIGURES_DIR, "A3_stations_map_elevation_basins.png")
fig.savefig(fig1_path)
plt.close(fig)
print(f"  [OK] Figure 1 enregistrée : {fig1_path}")

# Figure 2 : Décalage temporel (-1, 0, +1) et corrélations
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5), dpi=300)
for p_idx, prod_name in enumerate(["IMERG", "MERRA-2"]):
    ax = ax1 if p_idx == 0 else ax2
    sub_l = df_lag_test[df_lag_test["product"] == prod_name]
    lags = [-1, 0, 1]
    box_data = [pd.to_numeric(sub_l[f"corr_lag_{l}"], errors="coerce").dropna().values for l in lags]
    bp = ax.boxplot(box_data, labels=[f"Lag {l:+d} j" for l in lags], patch_artist=True,
                    boxprops=dict(facecolor="lightblue" if p_idx==0 else "lightgreen", alpha=0.7),
                    medianprops=dict(color="red", linewidth=2))
    ax.set_ylabel("Corrélation journalière de Pearson (r)", fontsize=11)
    ax.set_title(f"Sensibilité au Décalage Temporel — {prod_name}", fontsize=12, fontweight="bold")
    ax.grid(True, linestyle="--", alpha=0.4)
    best_l = optimal_lag_by_product[prod_name]
    ax.text(0.05, 0.05, f"Décalage optimal retenu : {best_l:+d} j", transform=ax.transAxes,
            fontsize=10, fontweight="bold", bbox=dict(boxstyle="round", facecolor="white", alpha=0.8))

plt.tight_layout()
fig2_path = os.path.join(FIGURES_DIR, "A3_lag_correlation_summary.png")
fig.savefig(fig2_path)
plt.close(fig)
print(f"  [OK] Figure 2 enregistrée : {fig2_path}")

# Figure 3 : Métriques par classe d altitude et bassin
fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
sub_elev = df_agg_metrics[(df_agg_metrics["aggregation_type"] == "elevation_class") & (df_agg_metrics["season"] == "Annuel")]
e_classes = ["< 500 m", "500-1000 m", "1000-1500 m", ">= 1500 m"]
x_pos = np.arange(len(e_classes))
w_bar = 0.35

for p_idx, prod_name in enumerate(["IMERG", "MERRA-2"]):
    vals = [float(sub_elev[(sub_elev["product"] == prod_name) & (sub_elev["group_name"] == ec)]["ratio_cumul_prod_over_obs_median"].values[0]) for ec in e_classes]
    ax1.bar(x_pos + (p_idx - 0.5)*w_bar, vals, width=w_bar, label=prod_name,
            color="#2b5c8f" if p_idx==0 else "#d95f02", alpha=0.85)
ax1.axhline(1.0, color="gray", linestyle="--")
ax1.set_xticks(x_pos)
ax1.set_xticklabels(e_classes)
ax1.set_ylabel("Rapport médian Produit / Station", fontsize=10)
ax1.set_title("Rapport de Cumul Annuel par Classe d'Altitude", fontsize=11, fontweight="bold")
ax1.legend(loc="upper left")
ax1.grid(True, linestyle="--", alpha=0.3)

for p_idx, prod_name in enumerate(["IMERG", "MERRA-2"]):
    pod_vals = [float(sub_elev[(sub_elev["product"] == prod_name) & (sub_elev["group_name"] == ec)]["POD_ge_1mm_median"].values[0]) for ec in e_classes]
    far_vals = [float(sub_elev[(sub_elev["product"] == prod_name) & (sub_elev["group_name"] == ec)]["FAR_ge_1mm_median"].values[0]) for ec in e_classes]
    ax2.plot(e_classes, pod_vals, marker="o", linewidth=2, label=f"POD {prod_name}", color="#2b5c8f" if p_idx==0 else "#d95f02")
    ax2.plot(e_classes, far_vals, marker="s", linestyle="--", linewidth=1.5, label=f"FAR {prod_name}", color="#2b5c8f" if p_idx==0 else "#d95f02", alpha=0.7)
ax2.set_ylabel("Score médian", fontsize=10)
ax2.set_title("Scores de Détection (POD) et Fausses Alertes (FAR) >= 1 mm", fontsize=11, fontweight="bold")
ax2.legend(loc="center right", fontsize=9)
ax2.grid(True, linestyle="--", alpha=0.3)

for p_idx, prod_name in enumerate(["IMERG", "MERRA-2"]):
    int_p = [float(sub_elev[(sub_elev["product"] == prod_name) & (sub_elev["group_name"] == ec)]["intensite_moyenne_pluvieuse_prod_median"].values[0]) for ec in e_classes]
    ax3.bar(x_pos + (p_idx - 0.5)*w_bar, int_p, width=w_bar, label=f"Intensité {prod_name}",
            color="#2b5c8f" if p_idx==0 else "#d95f02", alpha=0.85)
int_obs_vals = [float(sub_elev[(sub_elev["product"] == "IMERG") & (sub_elev["group_name"] == ec)]["intensite_moyenne_pluvieuse_obs_median"].values[0]) for ec in e_classes]
ax3.scatter(x_pos, int_obs_vals, color="black", s=60, zorder=5, label="Observation Station")
ax3.set_xticks(x_pos)
ax3.set_xticklabels(e_classes)
ax3.set_ylabel("Intensité moyenne (mm/jour pluvieux)", fontsize=10)
ax3.set_title("Intensité Moyenne des Jours Pluvieux (>= 1 mm)", fontsize=11, fontweight="bold")
ax3.legend(loc="upper left")
ax3.grid(True, linestyle="--", alpha=0.3)

for p_idx, prod_name in enumerate(["IMERG", "MERRA-2"]):
    q99_p = [float(sub_elev[(sub_elev["product"] == prod_name) & (sub_elev["group_name"] == ec)]["Q99_pluvieux_prod_mm_median"].values[0]) for ec in e_classes]
    ax4.bar(x_pos + (p_idx - 0.5)*w_bar, q99_p, width=w_bar, label=f"Q99 {prod_name}",
            color="#2b5c8f" if p_idx==0 else "#d95f02", alpha=0.85)
q99_obs_vals = [float(sub_elev[(sub_elev["product"] == "IMERG") & (sub_elev["group_name"] == ec)]["Q99_pluvieux_obs_mm_median"].values[0]) for ec in e_classes]
ax4.scatter(x_pos, q99_obs_vals, color="black", s=60, zorder=5, label="Observation Station")
ax4.set_xticks(x_pos)
ax4.set_xticklabels(e_classes)
ax4.set_ylabel("Quantile 99 (mm/jour)", fontsize=10)
ax4.set_title("Événements Extrêmes : Quantile 99 des Jours Pluvieux", fontsize=11, fontweight="bold")
ax4.legend(loc="upper left")
ax4.grid(True, linestyle="--", alpha=0.3)

plt.tight_layout()
fig3_path = os.path.join(FIGURES_DIR, "A3_metrics_by_basin_and_elevation.png")
fig.savefig(fig3_path)
plt.close(fig)
print(f"  [OK] Figure 3 enregistrée : {fig3_path}")

# Figure 4 : Saison hydrologique 2018 (15 fév - 15 mai)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(13, 8), dpi=300, sharex=True)
dt_plot = pd.to_datetime(dates_2018_hydro)

ax1.plot(dt_plot, p_lis_2018["Lalla Chafia"], label="LIS Forçage (ENS_corr)", color="black", linewidth=1.8)
ax1.plot(dt_plot, p_imerg_2018["Lalla Chafia"], label="IMERG V07B (brut)", color="#1f78b4", linewidth=1.4, alpha=0.85)
ax1.plot(dt_plot, p_merra_2018["Lalla Chafia"], label="MERRA-2 PRECTOTCORR", color="#e31a1c", linewidth=1.4, alpha=0.85)
ax1.set_ylabel("Pluie de bassin (mm/j)", fontsize=11)
ax1.set_title("Comparaison des Forçages Pluviométriques de Bassin — Lalla Chafia (15 fév - 15 mai 2018)", fontsize=11, fontweight="bold")
ax1.grid(True, linestyle="--", alpha=0.4)
ax1.legend(loc="upper left", fontsize=10)

ax2.plot(dt_plot, p_lis_2018["Sidi Jabeur"], label="LIS Forçage (ENS_corr)", color="black", linewidth=1.8)
ax2.plot(dt_plot, p_imerg_2018["Sidi Jabeur"], label="IMERG V07B (brut)", color="#1f78b4", linewidth=1.4, alpha=0.85)
ax2.plot(dt_plot, p_merra_2018["Sidi Jabeur"], label="MERRA-2 PRECTOTCORR", color="#e31a1c", linewidth=1.4, alpha=0.85)
ax2.set_ylabel("Pluie de bassin (mm/j)", fontsize=11)
ax2.set_xlabel("Date (2018)", fontsize=11)
ax2.set_title("Comparaison des Forçages Pluviométriques de Bassin — Sidi Jabeur (15 fév - 15 mai 2018)", fontsize=11, fontweight="bold")
ax2.grid(True, linestyle="--", alpha=0.4)
ax2.legend(loc="upper left", fontsize=10)

plt.tight_layout()
fig4_path = os.path.join(FIGURES_DIR, "A3_2018_hydro_season_forcing_comparison.png")
fig.savefig(fig4_path)
plt.close(fig)
print(f"  [OK] Figure 4 enregistrée : {fig4_path}")

# ==============================================================================
# 9. Generation du Rapport REPORT_A3.md (Tableaux Seulement, Pas d Interprétation)
# ==============================================================================
print("\n>>> Génération de REPORT_A3.md...")

rep_lines = [
    "# Rapport d'Étape A3 — Évaluation des Précipitations (H5)",
    "",
    "Ce rapport présente strictement les tableaux de résultats générés par script depuis les données in-situ ABH et les produits satellitaires/réanalyses IMERG V07B et MERRA-2 PRECTOTCORR.",
    "Conformément aux instructions, aucun chiffre n'est tapé à la main et le rapport ne comporte aucune phrase d'interprétation.",
    "",
    "## 1. Synthèse du Filtrage des Pluviomètres ABH (2001–2014)",
    "",
    f"- Période totale d'évaluation : 2001-01-01 au 2014-12-31 ({TOTAL_DAYS_EVAL} jours calendaires).",
    f"- Critère d'inclusion : >= 80 % de jours valides sur 2001–2014.",
    f"- Total stations brutes analysées : {len(df_stations_meta)}.",
    f"- Total stations retenues (>= 80 %) : {len(selected_stations)} (dont {len(st_in_dom)} dans le domaine LIS et {len(st_out_dom)} hors domaine).",
    "",
    "### 1.1 Synthèse par Bassin et par Classe d'Altitude",
    "",
    "| Groupe | Type de regroupement | Nombre total de stations | Stations >= 80 % valides | % de stations sélectionnées |",
    "| --- | --- | --- | --- | --- |",
]

for bname in ["Domaine complet", "Lalla Chafia", "Sidi Jabeur", "Sebou amont", "Hors domaine"]:
    tot_b = len(df_stations_meta[df_stations_meta["basin_a2b"] == bname])
    sel_b = len(df_stations_meta[(df_stations_meta["basin_a2b"] == bname) & (df_stations_meta["selected_ge80"] == "oui")])
    pct_b = round(100.0 * sel_b / tot_b, 1) if tot_b > 0 else 0.0
    rep_lines.append(f"| {bname} | Bassin A2b | {tot_b} | {sel_b} | {pct_b} % |")

for ec in ["< 500 m", "500-1000 m", "1000-1500 m", ">= 1500 m", "Hors domaine"]:
    tot_e = len(df_stations_meta[df_stations_meta["elevation_class"] == ec])
    sel_e = len(df_stations_meta[(df_stations_meta["elevation_class"] == ec) & (df_stations_meta["selected_ge80"] == "oui")])
    pct_e = round(100.0 * sel_e / tot_e, 1) if tot_e > 0 else 0.0
    rep_lines.append(f"| {ec} | Classe d'altitude | {tot_e} | {sel_e} | {pct_e} % |")

rep_lines.extend([
    "",
    "---",
    "",
    "## 2. Test du Décalage Temporel (-1, 0, +1 jour) par Corrélation Journalière",
    "",
    "| Produit | Décalage testé | Corrélation moyenne (r) | Corrélation médiane (r) | Décalage retenu |",
    "| --- | --- | --- | --- | --- |",
])

for prod_name in ["IMERG", "MERRA-2"]:
    sub_l = df_lag_test[df_lag_test["product"] == prod_name]
    best_l = optimal_lag_by_product[prod_name]
    for lag in [-1, 0, 1]:
        c_mean = round(float(pd.to_numeric(sub_l[f"corr_lag_{lag}"], errors="coerce").mean()), 4)
        c_med = round(float(pd.to_numeric(sub_l[f"corr_lag_{lag}"], errors="coerce").median()), 4)
        is_ret = "OUI" if lag == best_l else "non"
        rep_lines.append(f"| {prod_name} | {lag:+d} jour | {c_mean} | {c_med} | {is_ret} |")

rep_lines.extend([
    "",
    "---",
    "",
    "## 3. Métriques Pluviométriques Agrégées par Bassin, Classe d'Altitude et Saison",
    "",
    "| Produit | Type | Groupe | Saison | N_stations | Ratio cumul Prod/Obs (médian) | Corr journalière (médiane) | Freq >= 1mm Obs | Freq >= 1mm Prod | Int pluvieuse Obs | Int pluvieuse Prod | POD >= 1mm | FAR >= 1mm | CSI >= 1mm | POD >= 10mm | FAR >= 10mm | CSI >= 10mm | POD >= 30mm | FAR >= 30mm | CSI >= 30mm | Q95 pluvieux Obs | Q95 pluvieux Prod | Q99 pluvieux Obs | Q99 pluvieux Prod | Ratio Top 1% |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
])

for _, r in df_agg_metrics.iterrows():
    rep_lines.append(
        f"| {r['product']} | {r['aggregation_type']} | {r['group_name']} | {r['season']} | {r['n_stations']} | "
        f"{r['ratio_cumul_prod_over_obs_median']} | {r['corr_journaliere_median']} | "
        f"{r['freq_ge_1mm_obs_median']} | {r['freq_ge_1mm_prod_median']} | "
        f"{r['intensite_moyenne_pluvieuse_obs_median']} | {r['intensite_moyenne_pluvieuse_prod_median']} | "
        f"{r['POD_ge_1mm_median']} | {r['FAR_ge_1mm_median']} | {r['CSI_ge_1mm_median']} | "
        f"{r['POD_ge_10mm_median']} | {r['FAR_ge_10mm_median']} | {r['CSI_ge_10mm_median']} | "
        f"{r['POD_ge_30mm_median']} | {r['FAR_ge_30mm_median']} | {r['CSI_ge_30mm_median']} | "
        f"{r['Q95_pluvieux_obs_mm_median']} | {r['Q95_pluvieux_prod_mm_median']} | "
        f"{r['Q99_pluvieux_obs_mm_median']} | {r['Q99_pluvieux_prod_mm_median']} | "
        f"{r['ratio_cumul_top1pct_jours_median']} |"
    )

rep_lines.extend([
    "",
    "---",
    "",
    "## 4. Comparaison à l'Échelle des Bassins (>= 2 stations) : Moyenne Stations vs Moyenne de Bassin",
    "",
    "| Bassin | Produit | Décalage | Échelle de temps | N_stations | Cumul stations (mm) | Cumul produit bassin (mm) | Ratio Produit/Stations | Biais moyen (mm) | RMSE (mm) | Corrélation | POD >= 1mm | FAR >= 1mm | CSI >= 1mm | POD >= 10mm | FAR >= 10mm | CSI >= 10mm | POD >= 30mm | FAR >= 30mm | CSI >= 30mm |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
])

for _, r in df_catchment_comp.iterrows():
    rep_lines.append(
        f"| {r['basin']} | {r['product']} | {r['applied_lag_days']} j | {r['time_scale']} | {r['n_stations_in_basin']} | "
        f"{r['sum_stations_mean_mm']} | {r['sum_basin_product_mm']} | {r['ratio_cumul_prod_over_stations']} | "
        f"{r['bias_mean_mm']} | {r['rmse_mm']} | {r['corr']} | "
        f"{r['POD_ge_1mm']} | {r['FAR_ge_1mm']} | {r['CSI_ge_1mm']} | "
        f"{r['POD_ge_10mm']} | {r['FAR_ge_10mm']} | {r['CSI_ge_10mm']} | "
        f"{r['POD_ge_30mm']} | {r['FAR_ge_30mm']} | {r['CSI_ge_30mm']} |"
    )

rep_lines.extend([
    "",
    "---",
    "",
    "## 5. Saison Hydrologique 2018 (15 février - 15 mai) : IMERG, MERRA-2 et Forçage LIS (ENS_corr)",
    "",
    "| Bassin | Période ou Épisode | Date début | Date fin | Durée (j) | P IMERG V07B (mm) | P MERRA-2 PRECTOTCORR (mm) | P LIS ENS_corr (mm) | Ratio IMERG / LIS | Ratio MERRA-2 / LIS | Ratio IMERG / MERRA-2 |",
    "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
])

for _, r in df_forcing_2018.iterrows():
    rep_lines.append(
        f"| {r['basin']} | {r['period_or_episode']} | {r['start_date']} | {r['end_date']} | {r['duration_days']} | "
        f"{r['P_IMERG_V07B_mm']} | {r['P_MERRA2_PRECTOTCORR_mm']} | {r['P_LIS_ENS_corr_mm']} | "
        f"{r['ratio_IMERG_over_LIS']} | {r['ratio_MERRA2_over_LIS']} | {r['ratio_IMERG_over_MERRA2']} |"
    )

rep_lines.extend([
    "",
    "---",
    "",
    "## 6. Liste des Fichiers Produits",
    "",
    "### Tables CSV :",
    "- `paper1/tables/A3_stations_clean_metadata.csv`",
    "- `paper1/tables/A3_lag_correlation_testing.csv`",
    "- `paper1/tables/A3_precipitation_metrics_stations.csv`",
    "- `paper1/tables/A3_precipitation_metrics_aggregated.csv`",
    "- `paper1/tables/A3_catchment_stations_vs_basin_products.csv`",
    "- `paper1/tables/A3_2018_basin_forcing_comparison.csv`",
    "",
    "### Figures PNG :",
    "- `paper1/figures/A3_stations_map_elevation_basins.png`",
    "- `paper1/figures/A3_lag_correlation_summary.png`",
    "- `paper1/figures/A3_metrics_by_basin_and_elevation.png`",
    "- `paper1/figures/A3_2018_hydro_season_forcing_comparison.png`",
    "",
    "### Scripts :",
    "- `scripts/paper1/step_a3_precipitation_evaluation.py`",
    "- `paper1/scripts/step_a3_precipitation_evaluation.py`",
])

report_text = "\n".join(rep_lines) + "\n"
with open(REPORT_PATH, "w", encoding="utf-8") as fh:
    fh.write(report_text)
with open(ROOT_REPORT_PATH, "w", encoding="utf-8") as fh:
    fh.write(report_text)

print(f"  [OK] Rapports {REPORT_PATH} et {ROOT_REPORT_PATH} générés avec succès !")
print("=" * 80)
print("Étape A3 terminée avec succès.")
print("=" * 80)
