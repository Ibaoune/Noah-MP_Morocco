#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_opl_physics_et_sm_wb_2018.py
Évaluation des contraintes physiques indépendantes (ET/GLEAM, SMAP, Bilan Hydrique)
pour les 4 configurations OPL Noah-MP 4.0.1 (SIMGM, SIMTOP, Schaake96, BATS) sur 2018.
"""

import sys
import os

print("=== TOP OF SCRIPT EXECUTED ===", flush=True)

# Configuration de l'environnement Lustre pour immunité totale aux erreurs NFS
lustre_pkg = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/.local_lustre/lib/python3.8/site-packages"
pylib = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/pylib38"
pylib_dyn = pylib + "/lib-dynload"

for mod_name, mod in list(sys.modules.items()):
    if hasattr(mod, '__path__') and mod.__path__:
        mod.__path__ = [p.replace('/srv/software/easybuild/software/Anaconda3/2020.11/lib/python3.8', pylib) for p in mod.__path__]

sys.path = [lustre_pkg, pylib, pylib_dyn]

import datetime
import glob
import shutil
import pickle
import netCDF4 as nc
import numpy as np
import pandas as pd
import scipy.stats as stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = f"{BASE_DIR}/experiments/NorthMor/opl_hydrology_sensitivity"
LDT_PATH = f"{BASE_DIR}/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"
LIS_INPUT_NORTHMOR = f"{BASE_DIR}/data/lis_input/lis_input_NorthMor_5km.nc"
GLEAM_V4_PATH = f"{BASE_DIR}/data/validation/evapotranspiration/GLEAM/raw/E_2018_GLEAM_v4.3a.nc"
GLEAM_V3_PATH = f"{BASE_DIR}/data/validation/evapotranspiration/GLEAM/E_2018_GLEAM_v3.7a.nc"
SMAP_DIR = f"{BASE_DIR}/data/observations/SMAP_SPL3SMP_E"
POSTPROC_DIR = f"{SENS_DIR}/postproc"
ARTIFACT_DIR = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/f3772236-acd2-402d-bb10-a9a2613cf75f"

SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM (Réf)", "#1f77b4"),
    ("OL_R2_SIMTOP", "SIMTOP", "#2ca02c"),
    ("OL_R3_SCHAAKE96", "Schaake96", "#ff7f0e"),
    ("OL_R4_BATS", "BATS", "#d62728")
]

STATIONS = {
    'b_l_chafia': {'name': 'Lalla Chafia', 'basin': 'Bouregreg', 'row': 75, 'col': 71,
                   'lat_min': 33.0, 'lat_max': 33.8, 'lon_min': -6.3, 'lon_max': -5.3},
    'b_s_jabeur': {'name': 'Sidi Jabeur', 'basin': 'Grou / Bouregreg', 'row': 71, 'col': 71,
                   'lat_min': 33.2, 'lat_max': 33.9, 'lon_min': -6.8, 'lon_max': -5.9}
}

SOIL_THICKNESS_MM = np.array([100.0, 300.0, 600.0, 1000.0], dtype=np.float64)

def get_catchment_cells(ldt_path, outlet_row, outlet_col):
    with nc.Dataset(ldt_path) as ds:
        flow_x = ds['HYMAP_flow_direction_x'][:]
        flow_y = ds['HYMAP_flow_direction_y'][:]
        area = ds['HYMAP_grid_area'][:].filled(0.0)
        lat_grid = ds['lat'][:]
        lon_grid = ds['lon'][:]
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
    return vis, area, lat_grid, lon_grid

def main():
    print("=" * 80)
    print(" EVALUATION PHYSIQUE INDEPENDANTE DES 4 SCHEMAS OPL (2018)")
    print(" ET (GLEAM), HUMIDITE DU SOL (SMAP) ET BILAN HYDRIQUE")
    print("=" * 80)

    # 1. Extraction des masques de bassin
    print("\n[1/5] Extraction des cellules de bassin amont D8...")
    st_cells = {}
    st_weights = {}
    st_areas_km2 = {}
    
    with nc.Dataset(LDT_PATH) as ds:
        area_grid = ds['HYMAP_grid_area'][:].filled(0.0)
        lat_hymap = ds['lat'][:]
        lon_hymap = ds['lon'][:]
        
    for sid, meta in STATIONS.items():
        cells, _, _, _ = get_catchment_cells(LDT_PATH, meta['row'], meta['col'])
        st_cells[sid] = cells
        tot_area = sum([area_grid[r, c] for r, c in cells])
        w = np.zeros(area_grid.shape, dtype=float)
        for r, c in cells:
            w[r, c] = area_grid[r, c] / tot_area
        st_weights[sid] = w
        st_areas_km2[sid] = tot_area / 1e6
        print(f"  -> {meta['name']} : {len(cells)} cellules, Aire D8 = {st_areas_km2[sid]:.2f} km²")

    # Mapping des 16030 tuiles continentales vers la grille (121, 181)
    with nc.Dataset(LIS_INPUT_NORTHMOR) as ds:
        landmask_16030 = ds.variables['LANDMASK'][:].squeeze()
    land_idx = np.where(landmask_16030 == 1)
    
    # 2. Extraction des flux Noah-MP quotidiens pour 2018 (P, ET, Qs, Qsb, SM_layer1)
    print("\n[2/5] Extraction des séries journalières Noah-MP (P, ET, Qs, Qsb, SM superficiel)...")
    dates_2018 = [datetime.date(2018, 1, 1) + datetime.timedelta(days=i) for i in range(365)]
    
    cache_path = f"{POSTPROC_DIR}/tables/noah_daily_cache_2018.pkl"
    if os.path.exists(cache_path):
        print(f"  [CACHE] Chargement immédiat des séries Noah-MP depuis {cache_path}")
        with open(cache_path, 'rb') as f:
            noah_daily = pickle.load(f)
    else:
        noah_daily = {exp_id: {sid: {'P': [], 'ET': [], 'Qs': [], 'Qsb': [], 'SM_top': []} 
                               for sid in STATIONS} for exp_id, _, _ in SCHEMES}
        
        for exp_id, label, color in SCHEMES:
            noah_dir = f"{SENS_DIR}/experiments/{exp_id}/output"
            remap_dir = f"{SENS_DIR}/routing/runs/remap_180x120/{exp_id}/SURFACEMODEL"
            print(f"  -> Traitement de {exp_id} ({label})...")
            
            for d in dates_2018:
                file_dt = d + datetime.timedelta(days=1)
                m_folder = d.strftime('%Y-%m')
                ym = file_dt.strftime('%Y%m')
                fname = f"LIS_HIST_{file_dt.strftime('%Y%m%d0000')}.d01.nc"
                
                noah_f = f"{noah_dir}/{m_folder}/SURFACEMODEL/{ym}/{fname}"
                remap_f = f"{remap_dir}/{ym}/{fname}"
                
                with nc.Dataset(noah_f, 'r') as ds:
                    p_arr = ds['Rainf_f_tavg'][:]
                    if p_arr.ndim == 3: p_arr = p_arr[0]
                    p_remap = 0.25 * (p_arr[:-1, :-1] + p_arr[:-1, 1:] + p_arr[1:, :-1] + p_arr[1:, 1:])
                    
                    et_arr = ds['Evap_tavg'][:]
                    if et_arr.ndim == 3: et_arr = et_arr[0]
                    et_remap = 0.25 * (et_arr[:-1, :-1] + et_arr[:-1, 1:] + et_arr[1:, :-1] + et_arr[1:, 1:])
                    
                    sm_arr = ds['SoilMoist_tavg'][:]
                    if sm_arr.ndim == 4: sm_arr = sm_arr[0, 0]
                    elif sm_arr.ndim == 3: sm_arr = sm_arr[0]
                    sm_remap = 0.25 * (sm_arr[:-1, :-1] + sm_arr[:-1, 1:] + sm_arr[1:, :-1] + sm_arr[1:, 1:])
                    
                with nc.Dataset(remap_f, 'r') as ds:
                    qs_arr = ds['Qs_tavg'][:]
                    qsb_arr = ds['Qsb_tavg'][:]
                    if qs_arr.ndim == 3: qs_arr = qs_arr[0]
                    if qsb_arr.ndim == 3: qsb_arr = qsb_arr[0]
                    
                for sid in STATIONS:
                    w = st_weights[sid]
                    p_val = float(np.sum(p_remap * w) * 86400.0)
                    et_val = float(np.sum(et_remap * w) * 86400.0)
                    qs_val = float(np.sum(qs_arr * w) * 86400.0)
                    qsb_val = float(np.sum(qsb_arr * w) * 86400.0)
                    sm_val = float(np.sum(sm_remap * w))
                    
                    noah_daily[exp_id][sid]['P'].append(p_val)
                    noah_daily[exp_id][sid]['ET'].append(et_val)
                    noah_daily[exp_id][sid]['Qs'].append(qs_val)
                    noah_daily[exp_id][sid]['Qsb'].append(qsb_val)
                    noah_daily[exp_id][sid]['SM_top'].append(sm_val)

        os.makedirs(f"{POSTPROC_DIR}/tables", exist_ok=True)
        with open(cache_path, 'wb') as f:
            pickle.dump(noah_daily, f)
        print(f"  [CACHE] Séries Noah-MP sauvegardées dans {cache_path}")

    # 3. Extraction et Bilan Hydrique depuis les Restart Files
    print("\n[3/5] Calcul du bilan hydrique et des variations de stockage (restarts 20180101 -> 20190101)...")
    wb_results = []
    
    for exp_id, label, color in SCHEMES:
        rst_init = f"{SENS_DIR}/experiments/{exp_id}/restarts/LIS_RST_NOAHMP401_201801010000.d01.nc"
        rst_final = f"{SENS_DIR}/experiments/{exp_id}/restarts/LIS_RST_NOAHMP401_201901010000.d01.nc"
        
        with nc.Dataset(rst_init) as ds_i, nc.Dataset(rst_final) as ds_f:
            smc_i = ds_i.variables['SMC'][:] # (4, 16030)
            smc_f = ds_f.variables['SMC'][:]
            
            # Stock sol sur 4 couches (mm)
            soil_stock_i = np.sum(smc_i * SOIL_THICKNESS_MM[:, None], axis=0) # (16030,)
            soil_stock_f = np.sum(smc_f * SOIL_THICKNESS_MM[:, None], axis=0)
            delta_soil_16030 = soil_stock_f - soil_stock_i # (16030,)
            
            # Reconstruction sur la grille 2D (121, 181)
            delta_soil_2d = np.zeros((121, 181), dtype=float)
            delta_soil_2d[land_idx] = delta_soil_16030
            delta_soil_remap = 0.25 * (delta_soil_2d[:-1, :-1] + delta_soil_2d[:-1, 1:] + 
                                       delta_soil_2d[1:, :-1] + delta_soil_2d[1:, 1:])
            
            # Nappe / Aquifère WA (uniquement SIMGM)
            has_wa = ('WA' in ds_i.variables and 'WA' in ds_f.variables)
            if has_wa and exp_id == 'OL_R1_SIMGM':
                wa_i = ds_i.variables['WA'][:]
                wa_f = ds_f.variables['WA'][:]
                delta_wa_16030 = wa_f - wa_i
                delta_wa_2d = np.zeros((121, 181), dtype=float)
                delta_wa_2d[land_idx] = delta_wa_16030
                delta_wa_remap = 0.25 * (delta_wa_2d[:-1, :-1] + delta_wa_2d[:-1, 1:] + 
                                         delta_wa_2d[1:, :-1] + delta_wa_2d[1:, 1:])
            else:
                delta_wa_remap = np.zeros(area_grid.shape, dtype=float)
                
            # Canopée CANWAT et Neige SNEQV
            can_i = ds_i.variables['CANWAT'][:]
            can_f = ds_f.variables['CANWAT'][:]
            sn_i = ds_i.variables['SNEQV'][:]
            sn_f = ds_f.variables['SNEQV'][:]
            delta_surf_16030 = (can_f - can_i) + (sn_f - sn_i)
            delta_surf_2d = np.zeros((121, 181), dtype=float)
            delta_surf_2d[land_idx] = delta_surf_16030
            delta_surf_remap = 0.25 * (delta_surf_2d[:-1, :-1] + delta_surf_2d[:-1, 1:] + 
                                       delta_surf_2d[1:, :-1] + delta_surf_2d[1:, 1:])

        for sid, meta in STATIONS.items():
            w = st_weights[sid]
            p_tot = float(np.sum(noah_daily[exp_id][sid]['P']))
            et_tot = float(np.sum(noah_daily[exp_id][sid]['ET']))
            qs_tot = float(np.sum(noah_daily[exp_id][sid]['Qs']))
            qsb_tot = float(np.sum(noah_daily[exp_id][sid]['Qsb']))
            q_tot = qs_tot + qsb_tot
            
            d_soil = float(np.sum(delta_soil_remap * w))
            d_gw = float(np.sum(delta_wa_remap * w))
            d_surf = float(np.sum(delta_surf_remap * w))
            d_storage = d_soil + d_gw + d_surf
            
            # Fermeture du bilan : Residu = P - ET - Q - Delta_S
            residual = p_tot - et_tot - q_tot - d_storage
            closure_err_pct = (residual / p_tot) * 100.0 if p_tot > 0 else 0.0
            
            wb_results.append({
                'Station': meta['name'],
                'Station_ID': sid,
                'Superficie_D8_km2': st_areas_km2[sid],
                'Formulation': label,
                'Expérience': exp_id,
                'P_annuel_mm': round(p_tot, 1),
                'ET_annuel_mm': round(et_tot, 1),
                'Qs_annuel_mm': round(qs_tot, 1),
                'Qsb_annuel_mm': round(qsb_tot, 1),
                'Q_tot_annuel_mm': round(q_tot, 1),
                'Part_Qs_pct': round((qs_tot / q_tot) * 100.0, 1) if q_tot > 0 else 0.0,
                'Part_Qsb_pct': round((qsb_tot / q_tot) * 100.0, 1) if q_tot > 0 else 0.0,
                'Coeff_Ecoulement_pct': round((q_tot / p_tot) * 100.0, 1),
                'Delta_S_soil_mm': round(d_soil, 2),
                'Delta_S_gw_mm': round(d_gw, 2),
                'Delta_S_surf_mm': round(d_surf, 3),
                'Delta_S_total_mm': round(d_storage, 2),
                'Residu_Bilan_mm': round(residual, 2),
                'Erreur_Fermeture_pct': round(closure_err_pct, 2)
            })

    df_wb = pd.DataFrame(wb_results)
    csv_wb = f"{POSTPROC_DIR}/tables/table_water_balance_2018.csv"
    md_wb = f"{POSTPROC_DIR}/tables/table_water_balance_2018.md"
    df_wb.to_csv(csv_wb, index=False)
    
    # Écriture du Markdown du bilan hydrique
    header = "| " + " | ".join(df_wb.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df_wb.columns)) + " |"
    rows = ["| " + " | ".join(str(val) for val in row) + " |" for row in df_wb.values]
    with open(md_wb, "w") as f:
        f.write("\n".join([header, sep] + rows) + "\n")
    print(f"  [OK] Table Bilan Hydrique exportée : {csv_wb}")

    # 4. Evaluation ET vs GLEAM v4.3a
    print("\n[4/5] Extraction et comparaison ET avec le benchmark GLEAM v4.3a...")
    with nc.Dataset(GLEAM_V4_PATH) as ds:
        gl_lat = ds.variables['lat'][:]
        gl_lon = ds.variables['lon'][:]
        # Découpe sur le Maroc (lat 29.5 à 36.5, lon -10.5 à -0.5)
        # gl_lat: [-89.95 .. 89.95], step 0.1
        lat_mask = (gl_lat >= 29.5) & (gl_lat <= 36.5)
        lon_mask = (gl_lon >= -10.5) & (gl_lon <= -0.5)
        ilat_min, ilat_max = np.where(lat_mask)[0][0], np.where(lat_mask)[0][-1] + 1
        ilon_min, ilon_max = np.where(lon_mask)[0][0], np.where(lon_mask)[0][-1] + 1
        
        e_morocco = ds.variables['E'][:, ilat_min:ilat_max, ilon_min:ilon_max] # (365, nlat, nlon)
        sub_lat = gl_lat[ilat_min:ilat_max]
        sub_lon = gl_lon[ilon_min:ilon_max]

    gleam_daily = {}
    for sid, meta in STATIONS.items():
        cells = st_cells[sid]
        tot_area = sum([area_grid[r, c] for r, c in cells])
        g_series = np.zeros(365, dtype=float)
        for r, c in cells:
            clat = lat_hymap[r, c]
            clon = lon_hymap[r, c]
            i_la = int(np.argmin(np.abs(sub_lat - clat)))
            i_lo = int(np.argmin(np.abs(sub_lon - clon)))
            g_series += e_morocco[:, i_la, i_lo] * (area_grid[r, c] / tot_area)
        gleam_daily[sid] = g_series
        print(f"  -> GLEAM v4.3a Annuel {meta['name']} : {np.sum(g_series):.1f} mm/an")

    # 5. Extraction et comparaison SMAP SPL3SMP_E 2018 (AM)
    print("\n[5/5] Extraction et comparaison Humidité du sol avec SMAP SPL3SMP_E (2018)...")
    smap_daily = {sid: np.full(365, np.nan, dtype=float) for sid in STATIONS}
    
    # Repérage des coordonnées des cellules EASE-Grid dans la boîte [329:412, 1816:1880]
    smap_files_2018 = sorted(glob.glob(f"{SMAP_DIR}/raw/*2018*.h5") + glob.glob(f"{SMAP_DIR}/**/SMAP_L3_SM_P_E_2018*.h5", recursive=True))
    master_lat = np.full((83, 64), np.nan)
    master_lon = np.full((83, 64), np.nan)
    for f in smap_files_2018[:10]:
        try:
            with nc.Dataset(f) as ds:
                g = ds.groups['Soil_Moisture_Retrieval_Data_AM']
                lp = g.variables['latitude'][329:412, 1816:1880]
                lop = g.variables['longitude'][329:412, 1816:1880]
                v = (lp > -90)
                master_lat[v] = lp[v]
                master_lon[v] = lop[v]
        except Exception:
            continue
        if np.sum(np.isnan(master_lat)) == 0:
            break

    # Masque des pixels SMAP couvrant chaque bassin
    smap_basin_mask = {}
    for sid, meta in STATIONS.items():
        m = (master_lat >= meta['lat_min']) & (master_lat <= meta['lat_max']) & \
            (master_lon >= meta['lon_min']) & (master_lon <= meta['lon_max'])
        smap_basin_mask[sid] = m
        print(f"  -> Masque SMAP {meta['name']} : {np.sum(m)} pixels EASE-Grid")

    # Parcours des jours 2018 pour SMAP
    for day_idx, d in enumerate(dates_2018):
        ymd = d.strftime('%Y%m%d')
        pattern1 = f"{SMAP_DIR}/raw/SMAP_L3_SM_P_E_{ymd}_*.h5"
        pattern2 = f"{SMAP_DIR}/{d.strftime('%Y.%m.%d')}/SMAP_L3_SM_P_E_{ymd}_*.h5"
        f_list = glob.glob(pattern1) + glob.glob(pattern2)
        if not f_list:
            continue
        try:
            with nc.Dataset(f_list[0]) as ds:
                if 'Soil_Moisture_Retrieval_Data_AM' in ds.groups:
                    g = ds.groups['Soil_Moisture_Retrieval_Data_AM']
                    sm_patch = g.variables['soil_moisture'][329:412, 1816:1880]
                    flag_patch = g.variables['retrieval_qual_flag'][329:412, 1816:1880]
                    
                    # Filtre qualité : bit0 == 0 (qualité recommandée) et valeurs physiques [0, 0.6]
                    valid = ((flag_patch & 1) == 0) & (sm_patch > 0.0) & (sm_patch <= 0.6)
                    
                    for sid in STATIONS:
                        m = smap_basin_mask[sid] & valid
                        if np.sum(m) >= 2:
                            smap_daily[sid][day_idx] = float(np.mean(sm_patch[m]))
        except Exception:
            pass

    for sid in STATIONS:
        n_valid = np.sum(~np.isnan(smap_daily[sid]))
        print(f"  -> SMAP valid days {STATIONS[sid]['name']} : {n_valid}/365")

    # Calcul des métriques de performance ET et SMAP
    et_smap_results = []
    
    for sid, meta in STATIONS.items():
        g_et = gleam_daily[sid]
        s_obs = smap_daily[sid]
        valid_smap = ~np.isnan(s_obs)
        
        # SMAP anomalie saisonnière (retrait de la moyenne mobile 30j)
        s_obs_series = pd.Series(s_obs)
        s_obs_clim = s_obs_series.rolling(31, center=True, min_periods=5).mean()
        s_obs_anom = (s_obs_series - s_obs_clim).values
        
        for exp_id, label, color in SCHEMES:
            m_et = np.array(noah_daily[exp_id][sid]['ET'])
            m_sm = np.array(noah_daily[exp_id][sid]['SM_top'])
            
            # --- Métriques ET vs GLEAM ---
            et_ann_mod = float(np.sum(m_et))
            et_ann_gl = float(np.sum(g_et))
            et_bias_daily = float(np.mean(m_et - g_et))
            et_rmsd_daily = float(np.sqrt(np.mean((m_et - g_et)**2)))
            et_r_daily, _ = stats.pearsonr(m_et, g_et)
            
            # Cycle mensuel ET
            df_m = pd.DataFrame({'month': pd.to_datetime(dates_2018).month, 'mod': m_et, 'gl': g_et})
            m_cycle = df_m.groupby('month')[['mod', 'gl']].mean()
            et_r_monthly, _ = stats.pearsonr(m_cycle['mod'], m_cycle['gl'])
            
            # --- Métriques SMAP sur masque commun ---
            sm_mod_valid = m_sm[valid_smap]
            sm_obs_valid = s_obs[valid_smap]
            
            sm_mean_mod = float(np.mean(sm_mod_valid))
            sm_mean_obs = float(np.mean(sm_obs_valid))
            sm_bias = float(np.mean(sm_mod_valid - sm_obs_valid))
            sm_rmsd = float(np.sqrt(np.mean((sm_mod_valid - sm_obs_valid)**2)))
            sm_ubrmsd = float(np.sqrt(max(0.0, sm_rmsd**2 - sm_bias**2)))
            sm_r, _ = stats.pearsonr(sm_mod_valid, sm_obs_valid)
            
            # SM anomalie
            m_sm_series = pd.Series(m_sm)
            m_sm_clim = m_sm_series.rolling(31, center=True, min_periods=5).mean()
            m_sm_anom = (m_sm_series - m_sm_clim).values
            sm_anom_mod = m_sm_anom[valid_smap]
            sm_anom_obs = s_obs_anom[valid_smap]
            val_anom = ~np.isnan(sm_anom_mod) & ~np.isnan(sm_anom_obs)
            sm_r_anom, _ = stats.pearsonr(sm_anom_mod[val_anom], sm_anom_obs[val_anom])
            
            et_smap_results.append({
                'Station': meta['name'],
                'Station_ID': sid,
                'Formulation': label,
                'Expérience': exp_id,
                'ET_Annuel_Sim_mm': round(et_ann_mod, 1),
                'ET_Annuel_GLEAM_mm': round(et_ann_gl, 1),
                'ET_Biais_mm_an': round(et_ann_mod - et_ann_gl, 1),
                'ET_Biais_pct': round(((et_ann_mod - et_ann_gl) / et_ann_gl) * 100.0, 1),
                'ET_RMSD_mm_j': round(et_rmsd_daily, 3),
                'ET_R_journalier': round(et_r_daily, 3),
                'ET_R_mensuel': round(et_r_monthly, 3),
                'SM_Moyen_Sim_m3m3': round(sm_mean_mod, 3),
                'SM_Moyen_SMAP_m3m3': round(sm_mean_obs, 3),
                'SM_Biais_m3m3': round(sm_bias, 3),
                'SM_RMSD_m3m3': round(sm_rmsd, 3),
                'SM_ubRMSD_m3m3': round(sm_ubrmsd, 3),
                'SM_R_temporel': round(sm_r, 3),
                'SM_R_anomalie': round(sm_r_anom, 3),
                'SM_Jours_Valides': int(np.sum(valid_smap))
            })

    df_et_sm = pd.DataFrame(et_smap_results)
    csv_et_sm = f"{POSTPROC_DIR}/tables/table_et_smap_evaluation_2018.csv"
    md_et_sm = f"{POSTPROC_DIR}/tables/table_et_smap_evaluation_2018.md"
    df_et_sm.to_csv(csv_et_sm, index=False)
    
    header = "| " + " | ".join(df_et_sm.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(df_et_sm.columns)) + " |"
    rows = ["| " + " | ".join(str(val) for val in row) + " |" for row in df_et_sm.values]
    with open(md_et_sm, "w") as f:
        f.write("\n".join([header, sep] + rows) + "\n")
    print(f"  [OK] Table ET & SMAP exportée : {csv_et_sm}")

    # =========================================================================
    # 6. FIGURES DE SYNTHESE
    # =========================================================================
    print("\n[6/6] Génération des figures scientifiques ET et SMAP...")
    
    # -------------------------------------------------------------------------
    # FIGURE 5 : Évapotranspiration (Cycle mensuel & Cumul annuel vs GLEAM)
    # -------------------------------------------------------------------------
    fig5, axes = plt.subplots(2, 2, figsize=(14, 10))
    month_names = ['Jan', 'Fév', 'Mar', 'Avr', 'Mai', 'Juin', 'Juil', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc']
    
    for idx, (sid, meta) in enumerate(STATIONS.items()):
        ax_m = axes[idx, 0]
        ax_b = axes[idx, 1]
        
        # Cycle mensuel moyen
        df_gl = pd.DataFrame({'date': dates_2018, 'ET': gleam_daily[sid]})
        df_gl['month'] = pd.to_datetime(df_gl['date']).dt.month
        gl_m = df_gl.groupby('month')['ET'].mean()
        
        ax_m.plot(range(1, 13), gl_m.values, 'k--', linewidth=2.5, marker='s', markersize=6, label='GLEAM v4.3a (Obs)', zorder=5)
        
        annual_bars = [np.sum(gleam_daily[sid])]
        bar_labels = ['GLEAM v4.3a']
        bar_colors = ['#333333']
        
        for exp_id, label, color in SCHEMES:
            df_mod = pd.DataFrame({'date': dates_2018, 'ET': noah_daily[exp_id][sid]['ET']})
            df_mod['month'] = pd.to_datetime(df_mod['date']).dt.month
            mod_m = df_mod.groupby('month')['ET'].mean()
            ax_m.plot(range(1, 13), mod_m.values, color=color, linewidth=2.0, marker='o', markersize=4, label=f"Noah-MP {label}")
            
            annual_bars.append(np.sum(noah_daily[exp_id][sid]['ET']))
            bar_labels.append(label)
            bar_colors.append(color)
            
        ax_m.set_xticks(range(1, 13))
        ax_m.set_xticklabels(month_names)
        ax_m.set_ylabel("Évapotranspiration (mm/jour)", fontsize=10.5)
        ax_m.set_title(f"Cycle mensuel moyen d'ET (2018) — {meta['name']} ({meta['basin']})", fontsize=11, weight='bold')
        ax_m.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax_m.legend(loc='upper right', fontsize=9, framealpha=0.9)
            
        # Cumul annuel (Barres)
        x_pos = np.arange(len(annual_bars))
        rects = ax_b.bar(x_pos, annual_bars, color=bar_colors, alpha=0.85, edgecolor='black', width=0.55)
        ax_b.set_xticks(x_pos)
        ax_b.set_xticklabels(bar_labels, rotation=15, ha='right', fontsize=9.5)
        ax_b.set_ylabel("ET Cumulée Annuelle (mm/an)", fontsize=10.5)
        ax_b.set_title(f"Bilan Annuel d'ET vs GLEAM (2018) — {meta['name']}", fontsize=11, weight='bold')
        ax_b.grid(True, linestyle=":", alpha=0.5, axis='y')
        
        # Ajout des valeurs au-dessus des barres
        for r in rects:
            h = r.get_height()
            ax_b.annotate(f"{h:.1f}",
                          xy=(r.get_x() + r.get_width() / 2, h),
                          xytext=(0, 3), textcoords="offset points",
                          ha='center', va='bottom', fontsize=9, weight='bold')

    plt.tight_layout()
    fig5_png = f"{POSTPROC_DIR}/figures/fig5_et_monthly_comparison_gleam_wapor.png"
    fig5_pdf = f"{POSTPROC_DIR}/figures/fig5_et_monthly_comparison_gleam_wapor.pdf"
    plt.savefig(fig5_png, dpi=300)
    plt.savefig(fig5_pdf)
    plt.close()
    print(f"  -> Figure 5 sauvegardée : {fig5_png}")

    # -------------------------------------------------------------------------
    # FIGURE 6 : Humidité du sol superficielle (0-10 cm) vs SMAP (0-5 cm)
    # -------------------------------------------------------------------------
    fig6, axes = plt.subplots(2, 2, figsize=(15, 10))
    dates_dt = [datetime.datetime(d.year, d.month, d.day) for d in dates_2018]
    
    for idx, (sid, meta) in enumerate(STATIONS.items()):
        ax_t = axes[idx, 0]
        ax_s = axes[idx, 1]
        
        s_obs = smap_daily[sid]
        valid_smap = ~np.isnan(s_obs)
        valid_dates = [dates_dt[i] for i in range(365) if valid_smap[i]]
        valid_smap_vals = s_obs[valid_smap]
        
        # Séries temporelles
        ax_t.scatter(valid_dates, valid_smap_vals, color='black', s=22, alpha=0.85, label='SMAP SPL3SMP_E (0–5 cm)', zorder=5)
        
        for exp_id, label, color in SCHEMES:
            m_sm = np.array(noah_daily[exp_id][sid]['SM_top'])
            ax_t.plot(dates_dt, m_sm, color=color, linewidth=1.5, alpha=0.9, label=f"Noah-MP {label} (0–10 cm)")
            
            # Scatter plot
            sm_mod_valid = m_sm[valid_smap]
            ax_s.scatter(valid_smap_vals, sm_mod_valid, color=color, alpha=0.6, s=16, label=f"{label}")
            
        ax_t.set_ylabel("Humidité volumique (m³/m³)", fontsize=10.5)
        ax_t.set_title(f"Dynamique temporelle de l'humidité de surface (2018) — {meta['name']}", fontsize=11, weight='bold')
        ax_t.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
        ax_t.xaxis.set_major_locator(mdates.MonthLocator())
        ax_t.set_ylim(0.0, 0.45)
        ax_t.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax_t.legend(loc='upper right', fontsize=8.5, framealpha=0.9)
            
        # Scatter 1:1
        ax_s.plot([0.0, 0.45], [0.0, 0.45], 'k--', linewidth=1.5, label='Ligne 1:1')
        ax_s.set_xlim(0.0, 0.45)
        ax_s.set_ylim(0.0, 0.45)
        ax_s.set_xlabel("Humidité observée SMAP (m³/m³)", fontsize=10.5)
        ax_s.set_ylabel("Humidité simulée Noah-MP (m³/m³)", fontsize=10.5)
        ax_s.set_title(f"Corrélation directe Modèle vs SMAP (2018) — {meta['name']}", fontsize=11, weight='bold')
        ax_s.grid(True, linestyle=":", alpha=0.6)
        if idx == 0:
            ax_s.legend(loc='lower right', fontsize=8.5, framealpha=0.9)

    plt.tight_layout()
    fig6_png = f"{POSTPROC_DIR}/figures/fig6_surface_soil_moisture_smap_comparison.png"
    fig6_pdf = f"{POSTPROC_DIR}/figures/fig6_surface_soil_moisture_smap_comparison.pdf"
    plt.savefig(fig6_png, dpi=300)
    plt.savefig(fig6_pdf)
    plt.close()
    print(f"  -> Figure 6 sauvegardée : {fig6_png}")

    # Copie vers l'espace d'artefacts pour affichage utilisateur
    os.makedirs(ARTIFACT_DIR, exist_ok=True)
    for f in [fig5_png, fig6_png, csv_et_sm, md_et_sm, csv_wb, md_wb]:
        shutil.copy2(f, ARTIFACT_DIR)
    print(f"[OK] Fichiers et figures copiés vers l'espace d'artefacts : {ARTIFACT_DIR}")
    print("\n[SUCCÈS GLOBAL] Diagnostic physique indépendant (ET, SMAP, Bilan) terminé avec succès.")

if __name__ == '__main__':
    main()
