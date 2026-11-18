#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic des flux moyens et des debits du bassin versant amont de Lalla Chafia
(Annee 2018 detaillee et extension interannuelle 2016–2020).
Pour repondre aux recommandations scientifiques d'Augusto Getirana.

Variables analysees :
  1. Precipitation moyenne du bassin (Rainf_f_tavg pluie liquide, Snowf_tavg neige, mm/day)
  2. Ruissellement de surface moyen du bassin (Qs_tavg, mm/day)
  3. Ruissellement souterrain moyen du bassin (Qsb_tavg, mm/day)
  4. Debit d'apport total amont au reseau (Qin = Qs + Qsb, m3/s)
  5. Debits a l'exutoire de Lalla Chafia (cellule row=75, col=71) :
     - Observations ABH (data/streamflow_clean/obs_daily.csv)
     - OPL historique linres=1 (output/OPL_2016_2020_corrigee)
     - OPL recent linres=0 (output/OPL_linres0_2016_2020)

Periode d'analyse :
  2016–2020 : 1 827 jours calendaires, dont 1 826 jours communs valides avec
  observations ABH (seule la journee du 06/01/2018 est manquante).

Produits generes :
  - CSV journalier complet 2016–2020 : plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2016_2020.csv
  - CSV journalier 2018 : plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv
  - CSV stats annuelles et estivales : plots/sebou_bouregreg/tables/lalla_chafia_annual_summer_stats_2016_2020.csv
  - Figure de synthese interannuelle 2016–2020 : plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2016_2020_synthesis.png (.pdf)
  - Figure detaillee 3-panneaux 2018 : plots/sebou_bouregreg/figures/streamflow/lalla_chafia_2018_fluxes_and_streamflow.png (.pdf)
"""

import os
import sys
import time
import glob
import shutil
import datetime
import argparse
import multiprocessing as mp
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

STATIONS_CONFIG = {
    'b_l_chafia': {
        'name': 'Lalla Chafia',
        'basin': 'Bouregreg',
        'river': 'Bouregreg',
        'cell': (75, 71),  # (row, col) 0-indexed in NetCDF
        'lat_ldt': 33.7750,
        'lon_ldt': -6.4250,
        'area_km2_official': 3341.6,
        'prefix': 'lalla_chafia',
        'obs_type': 'daily',
    },
    'b_s_jabeur': {
        'name': 'Sidi Jabeur',
        'basin': 'Bouregreg',
        'river': 'Grou',
        'cell': (71, 71),  # (row, col) 0-indexed in NetCDF
        'lat_ldt': 33.5750,
        'lon_ldt': -6.4250,
        'area_km2_official': 3138.5,
        'prefix': 'sidi_jabeur',
        'obs_type': 'daily',
    },
    'dar_el_hamra': {
        'name': 'Dar El Hamra',
        'basin': 'Sebou',
        'river': 'Zloul',
        'cell': (75, 112),  # (row, col) 0-indexed in NetCDF
        'lat_ldt': 33.7750,
        'lon_ldt': -4.3750,
        'area_km2_official': 670.0,
        'prefix': 'dar_el_hamra',
        'obs_type': 'monthly',
    },
}

def parse_args():
    parser = argparse.ArgumentParser(description="Diagnostic des flux journaliers amont et debits OPL (2016–2020).")
    parser.add_argument("--station", default="b_l_chafia", choices=list(STATIONS_CONFIG.keys()),
                        help="Identifiant de la station a analyser (defaut: b_l_chafia).")
    parser.add_argument("--start-year", type=int, default=2016, help="Annee de debut (defaut: 2016).")
    parser.add_argument("--end-year", type=int, default=2020, help="Annee de fin (defaut: 2020).")
    parser.add_argument("--base-dir", default=None, help="Racine de routing (par defaut detecte automatiquement).")
    parser.add_argument("--artifact-dir", default="/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e",
                        help="Repertoire d'artefacts pour affichage UI.")
    parser.add_argument("--no-plot-2018", action="store_true", help="Ne pas regenerer la figure detaillee 2018.")
    return parser.parse_args()

def get_catchment_cells(ldt_path, outlet_row=75, outlet_col=71):
    """Delimite le bassin versant amont d'une station (cellule outlet_row, outlet_col) depuis le reseau LDT."""
    ds_ldt = nc.Dataset(ldt_path)
    flow_x = ds_ldt['HYMAP_flow_direction_x'][:]
    flow_y = ds_ldt['HYMAP_flow_direction_y'][:]
    area = ds_ldt['HYMAP_grid_area'][:].filled(0.0)
    R, C = flow_x.shape
    ds_ldt.close()

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

    cat = sorted(list(vis))
    cat_rows = np.array([r for r, c in cat], dtype=np.int32)
    cat_cols = np.array([c for r, c in cat], dtype=np.int32)
    cat_areas = area[cat_rows, cat_cols]
    tot_area_m2 = float(np.sum(cat_areas))
    return cat, cat_rows, cat_cols, cat_areas, tot_area_m2

def extract_year_worker(args):
    """Fonction travailleur extrayant les flux journaliers pour une annee donnee."""
    yr, noah_base, remap_base, r_min, r_max, c_min, c_max, local_rows, local_cols, cat_areas, tot_area_m2 = args
    start = datetime.date(yr, 1, 1)
    end = datetime.date(yr, 12, 31)
    n_days = (end - start).days + 1
    recs = []

    for i in range(n_days):
        dt = start + datetime.timedelta(days=i)
        dt_str = dt.strftime('%Y-%m-%d')
        next_dt = dt + datetime.timedelta(days=1)
        fn = f"LIS_HIST_{next_dt.strftime('%Y%m%d0000')}.d01.nc"

        p_noah = os.path.join(noah_base, dt.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
        if not os.path.exists(p_noah):
            p_noah = os.path.join(noah_base, next_dt.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
            if not os.path.exists(p_noah):
                p_noah = os.path.join(noah_base, dt.strftime('%Y-%m'), 'SURFACEMODEL', dt.strftime('%Y%m'), fn)
        
        p_remap = os.path.join(remap_base, dt.strftime('%Y%m'), fn)
        if not os.path.exists(p_remap):
            p_remap = os.path.join(remap_base, next_dt.strftime('%Y%m'), fn)

        if not os.path.exists(p_noah):
            raise FileNotFoundError(f"Fichier Noah-MP manquant pour {dt_str}: {fn}")
        if not os.path.exists(p_remap):
            raise FileNotFoundError(f"Fichier ruissellement remappe manquant pour {dt_str}: {fn}")

        with nc.Dataset(p_noah) as ds_n:
            v_rf = ds_n['Rainf_f_tavg']
            rf = v_rf[0, r_min:r_max+2, c_min:c_max+2] if v_rf.ndim == 3 else v_rf[r_min:r_max+2, c_min:c_max+2]
            if 'Snowf_tavg' in ds_n.variables:
                v_sn = ds_n['Snowf_tavg']
                sn = v_sn[0, r_min:r_max+2, c_min:c_max+2] if v_sn.ndim == 3 else v_sn[r_min:r_max+2, c_min:c_max+2]
            else:
                sn = np.zeros_like(rf)

        with nc.Dataset(p_remap) as ds_r:
            v_qs = ds_r['Qs_tavg']
            qs = v_qs[0, r_min:r_max+1, c_min:c_max+1] if v_qs.ndim == 3 else v_qs[r_min:r_max+1, c_min:c_max+1]
            v_qsb = ds_r['Qsb_tavg']
            qsb = v_qsb[0, r_min:r_max+1, c_min:c_max+1] if v_qsb.ndim == 3 else v_qsb[r_min:r_max+1, c_min:c_max+1]

        # Interpolation bilineaire aux centres des mailles HyMAP (moyenne des 4 noeuds delimitant chaque maille)
        rf_rem = 0.25 * (rf[:-1, :-1] + rf[:-1, 1:] + rf[1:, :-1] + rf[1:, 1:])
        sn_rem = 0.25 * (sn[:-1, :-1] + sn[:-1, 1:] + sn[1:, :-1] + sn[1:, 1:])

        r_basin = float(np.sum(rf_rem[local_rows, local_cols] * cat_areas) / tot_area_m2 * 86400.0)
        s_basin = float(np.sum(sn_rem[local_rows, local_cols] * cat_areas) / tot_area_m2 * 86400.0)
        qs_basin = float(np.sum(qs[local_rows, local_cols] * cat_areas) / tot_area_m2 * 86400.0)
        qsb_basin = float(np.sum(qsb[local_rows, local_cols] * cat_areas) / tot_area_m2 * 86400.0)

        # Debit d'apport total amont entrant dans le reseau (m3/s)
        # (Qs + Qsb) [kg m-2 s-1] * area [m2] / 1000 [kg/m3] = m3/s
        qin_m3s = float(np.sum((qs[local_rows, local_cols] + qsb[local_rows, local_cols]) * cat_areas) / 1000.0)

        recs.append({
            'date': dt_str,
            'year': yr,
            'rain_mm_d': round(r_basin, 4),
            'snow_mm_d': round(s_basin, 4),
            'precip_mm_d': round(r_basin + s_basin, 4),
            'qs_mm_d': round(qs_basin, 5),
            'qsb_mm_d': round(qsb_basin, 5),
            'qtot_runoff_mm_d': round(qs_basin + qsb_basin, 5),
            'qin_m3s': round(qin_m3s, 4)
        })

    return recs

def compute_metrics(obs_arr, sim_arr):
    """Calcule les metriques hydrologiques standard sur des series alignees valides."""
    mask = (~np.isnan(obs_arr)) & (~np.isnan(sim_arr))
    n = int(np.sum(mask))
    if n == 0:
        return {'n': 0, 'bias': np.nan, 'rmse': np.nan, 'corr': np.nan, 'nse': np.nan}
    
    o = obs_arr[mask]
    s = sim_arr[mask]
    bias = float(np.mean(s - o))
    rmse = float(np.sqrt(np.mean((s - o)**2)))
    
    # Correlation de Pearson
    if np.std(o) > 1e-6 and np.std(s) > 1e-6:
        corr = float(np.corrcoef(o, s)[0, 1])
    else:
        corr = np.nan
        
    # Critere de Nash-Sutcliffe (NSE)
    denom = np.sum((o - np.mean(o))**2)
    if denom > 1e-6:
        nse = float(1.0 - np.sum((o - s)**2) / denom)
    else:
        nse = np.nan
        
    return {'n': n, 'bias': bias, 'rmse': rmse, 'corr': corr, 'nse': nse}

def main():
    args = parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.base_dir:
        routing_dir = os.path.abspath(args.base_dir)
    else:
        routing_dir = os.path.abspath(os.path.join(script_dir, ".."))

    project_root = os.path.abspath(os.path.join(routing_dir, "../../.."))

    st_cfg = STATIONS_CONFIG[args.station]
    st_id = args.station
    st_name = st_cfg['name']
    st_prefix = st_cfg['prefix']
    outlet_row, outlet_col = st_cfg['cell']

    print("="*85)
    print(f"DIAGNOSTIC MULTI-ANNUEL DES FLUX ET DEBITS AMONT — {st_name.upper()} ({args.start_year}–{args.end_year})")
    print("="*85)
    print(f"Racine du projet      : {project_root}")
    print(f"Repertoire routing    : {routing_dir}")
    print(f"Station               : {st_name} (ID: {st_id}, Bassin: {st_cfg['basin']}, Oued: {st_cfg['river']})")
    print(f"Periode d'etude       : {args.start_year} a {args.end_year}")

    # 1. Delimitation du bassin
    ldt_path = os.path.join(routing_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    cat_cells, cat_rows, cat_cols, cat_areas, tot_area_m2 = get_catchment_cells(ldt_path, outlet_row, outlet_col)
    tot_area_km2 = tot_area_m2 / 1e6

    print(f"\n1. Bassin versant amont {st_name} :")
    print(f"   Cellules amont     : {len(cat_cells)} mailles HyMAP")
    print(f"   Superficie totale  : {tot_area_km2:.2f} km2 ({tot_area_m2:.1f} m2)")
    print(f"   Cellule exutoire   : row={outlet_row}, col={outlet_col}")

    r_min, r_max = int(cat_rows.min()), int(cat_rows.max())
    c_min, c_max = int(cat_cols.min()), int(cat_cols.max())
    local_rows = cat_rows - r_min
    local_cols = cat_cols - c_min

    # Chemins des entrees
    noah_base = os.path.join(project_root, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output")
    remap_base = os.path.join(routing_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL")

    # Debits simules et observes
    f_hist_csv = os.path.join(routing_dir, "output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv")
    f_lr0_csv = os.path.join(routing_dir, "output/OPL_linres0_2016_2020/t_sim_daily_12stations_opl_linres0.csv")
    is_monthly = (st_cfg.get('obs_type') == 'monthly')
    if is_monthly:
        f_obs_csv = os.path.join(project_root, "data/streamflow_clean/obs_monthly.csv")
        df_obs_raw = pd.read_csv(f_obs_csv)
        sub_obs_df = df_obs_raw[(df_obs_raw['station_id'] == st_id) & (df_obs_raw['annee'] >= args.start_year) & (df_obs_raw['annee'] <= args.end_year)].copy()
        sub_obs_df['year_month'] = sub_obs_df['annee'].astype(str) + '-' + sub_obs_df['mois'].astype(str).str.zfill(2)
        obs_q_dict = dict(zip(sub_obs_df['year_month'], sub_obs_df['q_m3s']))
        obs_flag_dict = dict(zip(sub_obs_df['year_month'], sub_obs_df['flag']))
    else:
        f_obs_csv = os.path.join(project_root, "data/streamflow_clean/obs_daily.csv")
        df_obs = pd.read_csv(f_obs_csv)
        sub_obs = df_obs[df_obs['station_id'] == st_id].set_index('date')['q_m3s']

    df_hist = pd.read_csv(f_hist_csv).set_index('date')[st_id]
    df_lr0 = pd.read_csv(f_lr0_csv).set_index('date')[st_id]

    # 2. Extraction des donnees journalieres
    years = list(range(args.start_year, args.end_year + 1))
    print(f"\n2. Extraction des flux journaliers pour {len(years)} annee(s) ({args.start_year}–{args.end_year})...")
    t0 = time.time()
    worker_args = [
        (yr, noah_base, remap_base, r_min, r_max, c_min, c_max, local_rows, local_cols, cat_areas, tot_area_m2)
        for yr in years
    ]
    n_procs = min(len(years), mp.cpu_count(), 8)
    with mp.Pool(n_procs) as pool:
        results = pool.map(extract_year_worker, worker_args)

    all_recs = [r for sublist in results for r in sublist]
    df_out = pd.DataFrame(all_recs)

    # Fusion avec les debits exutoire
    df_out['q_sim_hist_m3s'] = df_out['date'].map(df_hist).round(4)
    df_out['q_sim_linres0_m3s'] = df_out['date'].map(df_lr0).round(4)
    if not is_monthly:
        df_out['q_obs_m3s'] = df_out['date'].map(sub_obs)
    else:
        df_out['q_obs_m3s'] = np.nan

    t1 = time.time()
    n_total_cal_days = len(df_out)
    print(f"   Extraction complete : {n_total_cal_days} jours calendaires extraits en {t1-t0:.2f} s.")
    if not is_monthly:
        n_valid_obs_days = int(df_out['q_obs_m3s'].notna().sum())
        n_missing_obs_days = n_total_cal_days - n_valid_obs_days
        missing_desc = f"{n_missing_obs_days} jour manquant (2018-01-06)" if n_missing_obs_days > 0 else "0 jour manquant"
        print(f"   Observations ABH    : {n_valid_obs_days} jours communs valides ({missing_desc}).")
    else:
        n_valid_months = len(obs_q_dict)
        print(f"   Observations ABH    : {n_valid_months} mois d'observations mensuelles (2016–2020).")
    # 3. Export CSV
    out_table_dir = os.path.join(routing_dir, "plots/sebou_bouregreg/tables")
    os.makedirs(out_table_dir, exist_ok=True)

    if not is_monthly:
        csv_daily_path = os.path.join(out_table_dir, f"{st_prefix}_fluxes_{args.start_year}_{args.end_year}.csv")
        df_out.to_csv(csv_daily_path, index=False)
        print(f"\n3. Tableau journalier exporte : {csv_daily_path}")

        # Si Lalla Chafia et 2018 couvert, exporter aussi lalla_chafia_fluxes_2018.csv pour compatibilite
        if st_id == 'b_l_chafia' and 2018 in years:
            df_2018 = df_out[df_out['year'] == 2018]
            csv_2018_path = os.path.join(out_table_dir, "lalla_chafia_fluxes_2018.csv")
            df_2018.to_csv(csv_2018_path, index=False)
            print(f"   Tableau journalier 2018 exporte : {csv_2018_path}")
    else:
        df_out['dt'] = pd.to_datetime(df_out['date'])
        df_out['month'] = df_out['dt'].dt.month

        monthly_recs = []
        for (yr, mo), grp in df_out.groupby(['year', 'month']):
            ym_str = f"{yr}-{mo:02d}"
            n_days_m = len(grp)
            rain_m = float(grp['rain_mm_d'].sum())
            snow_m = float(grp['snow_mm_d'].sum())
            p_m = float(grp['precip_mm_d'].sum())
            qs_m = float(grp['qs_mm_d'].sum())
            qsb_m = float(grp['qsb_mm_d'].sum())
            qtot_m = qs_m + qsb_m
            qsb_ratio_m = (qsb_m / qtot_m * 100.0) if qtot_m > 0 else np.nan
            runoff_coeff_m = (qtot_m / p_m * 100.0) if p_m > 0 else np.nan
            qin_m3s_m = float(grp['qin_m3s'].mean())
            q_h1_m = float(grp['q_sim_hist_m3s'].mean())
            q_lr0_m = float(grp['q_sim_linres0_m3s'].mean())
            q_obs_m = obs_q_dict.get(ym_str, np.nan)
            flag_m = obs_flag_dict.get(ym_str, np.nan)

            v_p_hm3 = p_m * 1e-3 * tot_area_m2 / 1e6
            v_qs_hm3 = qs_m * 1e-3 * tot_area_m2 / 1e6
            v_qsb_hm3 = qsb_m * 1e-3 * tot_area_m2 / 1e6
            v_qin_hm3 = qtot_m * 1e-3 * tot_area_m2 / 1e6
            v_h1_hm3 = q_h1_m * n_days_m * 86400.0 / 1e6
            v_lr0_hm3 = q_lr0_m * n_days_m * 86400.0 / 1e6
            v_obs_hm3 = q_obs_m * n_days_m * 86400.0 / 1e6 if not np.isnan(q_obs_m) else np.nan

            monthly_recs.append({
                'year': yr,
                'month': mo,
                'year_month': ym_str,
                'n_days': n_days_m,
                'rain_mm_month': round(rain_m, 2),
                'snow_mm_month': round(snow_m, 2),
                'precip_mm_month': round(p_m, 2),
                'qs_mm_month': round(qs_m, 2),
                'qsb_mm_month': round(qsb_m, 2),
                'qtot_runoff_mm_month': round(qtot_m, 2),
                'qsb_ratio_month_pct': round(qsb_ratio_m, 1),
                'runoff_coeff_month_pct': round(runoff_coeff_m, 1),
                'v_p_hm3': round(v_p_hm3, 2),
                'v_qs_hm3': round(v_qs_hm3, 2),
                'v_qsb_hm3': round(v_qsb_hm3, 2),
                'v_qin_hm3': round(v_qin_hm3, 2),
                'qin_mean_m3s': round(qin_m3s_m, 3),
                'q_sim_hist_m3s': round(q_h1_m, 4),
                'q_sim_linres0_m3s': round(q_lr0_m, 4),
                'q_obs_m3s': round(q_obs_m, 4) if not np.isnan(q_obs_m) else np.nan,
                'v_sim_h1_hm3': round(v_h1_hm3, 2),
                'v_sim_lr0_hm3': round(v_lr0_hm3, 2),
                'v_obs_hm3': round(v_obs_hm3, 2) if not np.isnan(v_obs_hm3) else np.nan,
                'obs_flag': flag_m
            })

        df_monthly = pd.DataFrame(monthly_recs)
        csv_monthly_path = os.path.join(out_table_dir, f"{st_prefix}_fluxes_monthly_{args.start_year}_{args.end_year}.csv")
        df_monthly.to_csv(csv_monthly_path, index=False)
        print(f"\n3. Tableau mensuel exporte ({len(df_monthly)} mois) : {csv_monthly_path}")
    # 4. Calcul des statistiques annuelles et estivales
    print("\n4. Calcul des bilans et metriques annuelles et estivales...")
    stats_records = []

    if not is_monthly:
        df_out['dt'] = pd.to_datetime(df_out['date'])
        df_idx = df_out.set_index('dt')

        for yr in years:
            sub = df_idx[df_idx['year'] == yr]
            n_days = len(sub)
            
            # Precipitations et ruissellements
            rain_ann = float(sub['rain_mm_d'].sum())
            snow_ann = float(sub['snow_mm_d'].sum())
            p_ann = float(sub['precip_mm_d'].sum())
            qs_ann = float(sub['qs_mm_d'].sum())
            qsb_ann = float(sub['qsb_mm_d'].sum())
            qtot_ann = qs_ann + qsb_ann

            v_p_hm3 = p_ann * 1e-3 * tot_area_m2 / 1e6
            v_qs_hm3 = qs_ann * 1e-3 * tot_area_m2 / 1e6
            v_qsb_hm3 = qsb_ann * 1e-3 * tot_area_m2 / 1e6
            v_qin_hm3 = qtot_ann * 1e-3 * tot_area_m2 / 1e6

            qsb_ratio_ann = (qsb_ann / qtot_ann * 100.0) if qtot_ann > 0 else np.nan
            runoff_coeff = (qtot_ann / p_ann * 100.0) if p_ann > 0 else np.nan

            # Jours communs valides d'observation
            sub_common = sub.dropna(subset=['q_obs_m3s', 'q_sim_linres0_m3s', 'q_sim_hist_m3s'])
            n_common = len(sub_common)
            
            q_obs_mean = float(sub_common['q_obs_m3s'].mean()) if n_common > 0 else np.nan
            q_lr0_mean = float(sub_common['q_sim_linres0_m3s'].mean()) if n_common > 0 else np.nan
            q_h1_mean = float(sub_common['q_sim_hist_m3s'].mean()) if n_common > 0 else np.nan

            v_obs_common_hm3 = float(sub_common['q_obs_m3s'].sum() * 86400.0 / 1e6) if n_common > 0 else np.nan
            v_lr0_common_hm3 = float(sub_common['q_sim_linres0_m3s'].sum() * 86400.0 / 1e6) if n_common > 0 else np.nan
            v_h1_common_hm3 = float(sub_common['q_sim_hist_m3s'].sum() * 86400.0 / 1e6) if n_common > 0 else np.nan

            # Metriques
            m_lr0 = compute_metrics(sub_common['q_obs_m3s'].values, sub_common['q_sim_linres0_m3s'].values)
            m_h1 = compute_metrics(sub_common['q_obs_m3s'].values, sub_common['q_sim_hist_m3s'].values)

            # Periode estivale (1er juin - 30 septembre)
            sub_sum = sub.loc[f'{yr}-06-01':f'{yr}-09-30']
            p_sum = float(sub_sum['precip_mm_d'].sum())
            qs_sum = float(sub_sum['qs_mm_d'].sum())
            qsb_sum = float(sub_sum['qsb_mm_d'].sum())
            qtot_sum = qs_sum + qsb_sum
            qsb_ratio_sum = (qsb_sum / qtot_sum * 100.0) if qtot_sum > 0 else np.nan

            sub_sum_common = sub_sum.dropna(subset=['q_obs_m3s'])
            n_sum_common = len(sub_sum_common)
            q_obs_sum_mean = float(sub_sum_common['q_obs_m3s'].mean()) if n_sum_common > 0 else np.nan
            q_lr0_sum_mean = float(sub_sum_common['q_sim_linres0_m3s'].mean()) if n_sum_common > 0 else np.nan
            q_h1_sum_mean = float(sub_sum_common['q_sim_hist_m3s'].mean()) if n_sum_common > 0 else np.nan
            qin_sum_mean = float(sub_sum['qin_m3s'].mean())

            sum_bias_lr0 = q_lr0_sum_mean - q_obs_sum_mean if not np.isnan(q_obs_sum_mean) else np.nan
            sum_bias_h1 = q_h1_sum_mean - q_obs_sum_mean if not np.isnan(q_obs_sum_mean) else np.nan

            stats_records.append({
                'year': yr,
                'n_days': n_days,
                'n_obs_valid': n_common,
                'rain_ann_mm': round(rain_ann, 2),
                'snow_ann_mm': round(snow_ann, 2),
                'p_ann_mm': round(p_ann, 2),
                'v_p_hm3': round(v_p_hm3, 2),
                'qs_ann_mm': round(qs_ann, 2),
                'v_qs_hm3': round(v_qs_hm3, 2),
                'qsb_ann_mm': round(qsb_ann, 2),
                'v_qsb_hm3': round(v_qsb_hm3, 2),
                'qtot_ann_mm': round(qtot_ann, 2),
                'v_qin_hm3': round(v_qin_hm3, 2),
                'qsb_ratio_ann_pct': round(qsb_ratio_ann, 1),
                'runoff_coeff_pct': round(runoff_coeff, 1),
                'v_obs_common_hm3': round(v_obs_common_hm3, 2),
                'q_obs_mean_m3s': round(q_obs_mean, 3),
                'v_sim_lr0_common_hm3': round(v_lr0_common_hm3, 2),
                'q_sim_lr0_mean_m3s': round(q_lr0_mean, 3),
                'v_sim_h1_common_hm3': round(v_h1_common_hm3, 2),
                'q_sim_h1_mean_m3s': round(q_h1_mean, 3),
                'bias_lr0_m3s': round(m_lr0['bias'], 3),
                'rmse_lr0_m3s': round(m_lr0['rmse'], 3),
                'corr_lr0': round(m_lr0['corr'], 3),
                'nse_lr0': round(m_lr0['nse'], 3),
                'bias_h1_m3s': round(m_h1['bias'], 3),
                'rmse_h1_m3s': round(m_h1['rmse'], 3),
                'corr_h1': round(m_h1['corr'], 3),
                'nse_h1': round(m_h1['nse'], 3),
                'summer_days_valid': n_sum_common,
                'p_sum_mm': round(p_sum, 2),
                'qs_sum_mm': round(qs_sum, 2),
                'qsb_sum_mm': round(qsb_sum, 2),
                'qsb_ratio_sum_pct': round(qsb_ratio_sum, 1),
                'qin_sum_mean_m3s': round(qin_sum_mean, 3),
                'q_obs_sum_mean_m3s': round(q_obs_sum_mean, 3),
                'q_sim_lr0_sum_mean_m3s': round(q_lr0_sum_mean, 3),
                'q_sim_h1_sum_mean_m3s': round(q_h1_sum_mean, 3),
                'summer_bias_lr0_m3s': round(sum_bias_lr0, 3),
                'summer_bias_h1_m3s': round(sum_bias_h1, 3)
            })
    else:
        for yr in years:
            sub_m = df_monthly[df_monthly['year'] == yr]
            n_months = len(sub_m)
            n_days = int(sub_m['n_days'].sum())

            rain_ann = float(sub_m['rain_mm_month'].sum())
            snow_ann = float(sub_m['snow_mm_month'].sum())
            p_ann = float(sub_m['precip_mm_month'].sum())
            qs_ann = float(sub_m['qs_mm_month'].sum())
            qsb_ann = float(sub_m['qsb_mm_month'].sum())
            qtot_ann = qs_ann + qsb_ann

            v_p_hm3 = p_ann * 1e-3 * tot_area_m2 / 1e6
            v_qs_hm3 = qs_ann * 1e-3 * tot_area_m2 / 1e6
            v_qsb_hm3 = qsb_ann * 1e-3 * tot_area_m2 / 1e6
            v_qin_hm3 = qtot_ann * 1e-3 * tot_area_m2 / 1e6

            qsb_ratio_ann = (qsb_ann / qtot_ann * 100.0) if qtot_ann > 0 else np.nan
            runoff_coeff = (qtot_ann / p_ann * 100.0) if p_ann > 0 else np.nan

            sub_common = sub_m.dropna(subset=['q_obs_m3s', 'q_sim_linres0_m3s', 'q_sim_hist_m3s'])
            n_common = len(sub_common)

            q_obs_mean = float(sub_common['q_obs_m3s'].mean()) if n_common > 0 else np.nan
            q_lr0_mean = float(sub_common['q_sim_linres0_m3s'].mean()) if n_common > 0 else np.nan
            q_h1_mean = float(sub_common['q_sim_hist_m3s'].mean()) if n_common > 0 else np.nan

            v_obs_common_hm3 = float(sub_common['v_obs_hm3'].sum()) if n_common > 0 else np.nan
            v_lr0_common_hm3 = float(sub_common['v_sim_lr0_hm3'].sum()) if n_common > 0 else np.nan
            v_h1_common_hm3 = float(sub_common['v_sim_h1_hm3'].sum()) if n_common > 0 else np.nan

            # Metriques sur les 12 debits mensuels
            m_lr0 = compute_metrics(sub_common['q_obs_m3s'].values, sub_common['q_sim_linres0_m3s'].values)
            m_h1 = compute_metrics(sub_common['q_obs_m3s'].values, sub_common['q_sim_hist_m3s'].values)

            # Periode estivale (Juin-Septembre, mois 6 a 9)
            sub_sum = sub_m[sub_m['month'].isin([6, 7, 8, 9])]
            p_sum = float(sub_sum['precip_mm_month'].sum())
            qs_sum = float(sub_sum['qs_mm_month'].sum())
            qsb_sum = float(sub_sum['qsb_mm_month'].sum())
            qtot_sum = qs_sum + qsb_sum
            qsb_ratio_sum = (qsb_sum / qtot_sum * 100.0) if qtot_sum > 0 else np.nan

            sub_sum_common = sub_sum.dropna(subset=['q_obs_m3s'])
            n_sum_common = len(sub_sum_common)
            q_obs_sum_mean = float(sub_sum_common['q_obs_m3s'].mean()) if n_sum_common > 0 else np.nan
            q_lr0_sum_mean = float(sub_sum_common['q_sim_linres0_m3s'].mean()) if n_sum_common > 0 else np.nan
            q_h1_sum_mean = float(sub_sum_common['q_sim_hist_m3s'].mean()) if n_sum_common > 0 else np.nan
            qin_sum_mean = float(sub_sum['qin_mean_m3s'].mean())

            sum_bias_lr0 = q_lr0_sum_mean - q_obs_sum_mean if not np.isnan(q_obs_sum_mean) else np.nan
            sum_bias_h1 = q_h1_sum_mean - q_obs_sum_mean if not np.isnan(q_obs_sum_mean) else np.nan

            stats_records.append({
                'year': yr,
                'n_days': n_days,
                'n_obs_valid': n_common,  # 12 mois valides
                'rain_ann_mm': round(rain_ann, 2),
                'snow_ann_mm': round(snow_ann, 2),
                'p_ann_mm': round(p_ann, 2),
                'v_p_hm3': round(v_p_hm3, 2),
                'qs_ann_mm': round(qs_ann, 2),
                'v_qs_hm3': round(v_qs_hm3, 2),
                'qsb_ann_mm': round(qsb_ann, 2),
                'v_qsb_hm3': round(v_qsb_hm3, 2),
                'qtot_ann_mm': round(qtot_ann, 2),
                'v_qin_hm3': round(v_qin_hm3, 2),
                'qsb_ratio_ann_pct': round(qsb_ratio_ann, 1),
                'runoff_coeff_pct': round(runoff_coeff, 1),
                'v_obs_common_hm3': round(v_obs_common_hm3, 2),
                'q_obs_mean_m3s': round(q_obs_mean, 3),
                'v_sim_lr0_common_hm3': round(v_lr0_common_hm3, 2),
                'q_sim_lr0_mean_m3s': round(q_lr0_mean, 3),
                'v_sim_h1_common_hm3': round(v_h1_common_hm3, 2),
                'q_sim_h1_mean_m3s': round(q_h1_mean, 3),
                'bias_lr0_m3s': round(m_lr0['bias'], 3),
                'rmse_lr0_m3s': round(m_lr0['rmse'], 3),
                'corr_lr0': round(m_lr0['corr'], 3),
                'nse_lr0': round(m_lr0['nse'], 3),
                'bias_h1_m3s': round(m_h1['bias'], 3),
                'rmse_h1_m3s': round(m_h1['rmse'], 3),
                'corr_h1': round(m_h1['corr'], 3),
                'nse_h1': round(m_h1['nse'], 3),
                'summer_days_valid': n_sum_common,  # 4 mois estivaux
                'p_sum_mm': round(p_sum, 2),
                'qs_sum_mm': round(qs_sum, 2),
                'qsb_sum_mm': round(qsb_sum, 2),
                'qsb_ratio_sum_pct': round(qsb_ratio_sum, 1),
                'qin_sum_mean_m3s': round(qin_sum_mean, 3),
                'q_obs_sum_mean_m3s': round(q_obs_sum_mean, 3),
                'q_sim_lr0_sum_mean_m3s': round(q_lr0_sum_mean, 3),
                'q_sim_h1_sum_mean_m3s': round(q_h1_sum_mean, 3),
                'summer_bias_lr0_m3s': round(sum_bias_lr0, 3),
                'summer_bias_h1_m3s': round(sum_bias_h1, 3)
            })

    df_stats = pd.DataFrame(stats_records)
    stats_csv_path = os.path.join(out_table_dir, f"{st_prefix}_annual_summer_stats_{args.start_year}_{args.end_year}.csv")
    df_stats.to_csv(stats_csv_path, index=False)
    print(f"   Tableau de statistiques exporte : {stats_csv_path}")

    # Affichage de synthese
    print("\n" + "="*85)
    print(f"SYNTHESE DES FLUX ET METRIQUES PAR ANNEE — {st_name.upper()} ({tot_area_km2:.1f} km2)")
    print("="*85)
    for _, r in df_stats.iterrows():
        yr = int(r['year'])
        flag = " [Conditions initiales distinctes]" if yr == 2016 else ""
        obs_unit_label = 'Mois valides ABH' if is_monthly else 'Jours valides ABH'
        print(f"\n--- ANNEE {yr}{flag} (Jours calendaires: {int(r['n_days'])}, {obs_unit_label}: {int(r['n_obs_valid'])}) ---")
        print(f"  Precipitations (P)    : {r['p_ann_mm']:5.1f} mm/an (Pluie: {r['rain_ann_mm']:5.1f}, Neige: {r['snow_ann_mm']:4.1f}) | {r['v_p_hm3']:6.1f} hm3")
        print(f"  Ruissellement surface : {r['qs_ann_mm']:5.1f} mm/an (Qs)    | {r['v_qs_hm3']:6.1f} hm3  [{r['qs_ann_mm']/r['p_ann_mm']*100:4.1f}% de P]")
        print(f"  Ruissellement souterr.: {r['qsb_ann_mm']:5.1f} mm/an (Qsb)   | {r['v_qsb_hm3']:6.1f} hm3  [{r['qsb_ann_mm']/r['p_ann_mm']*100:4.1f}% de P]")
        print(f"  Part Qsb annuelle     : {r['qsb_ratio_ann_pct']:4.1f}% des apports de ruissellement (Coef ecoulement: {r['runoff_coeff_pct']:4.1f}%)")
        print(f"  Volume observe ABH    : {r['v_obs_common_hm3']:6.1f} hm3 (Debit moyen: {r['q_obs_mean_m3s']:5.2f} m3/s)")
        print(f"  Volume simule linres=0: {r['v_sim_lr0_common_hm3']:6.1f} hm3 (Debit moyen: {r['q_sim_lr0_mean_m3s']:5.2f} m3/s) | Biais: {r['bias_lr0_m3s']:+5.2f} m3/s")
        print(f"  Volume simule linres=1: {r['v_sim_h1_common_hm3']:6.1f} hm3 (Debit moyen: {r['q_sim_h1_mean_m3s']:5.2f} m3/s) | Biais: {r['bias_h1_m3s']:+5.2f} m3/s")
        print(f"  Performances annuelles: linres=0 [NSE={r['nse_lr0']:+.3f}, R={r['corr_lr0']:.3f}, RMSE={r['rmse_lr0_m3s']:.2f}] vs linres=1 [NSE={r['nse_h1']:+.3f}, R={r['corr_h1']:.3f}, RMSE={r['rmse_h1_m3s']:.2f}]")
        sum_unit_label = 'mois' if is_monthly else 'jours'
        print(f"  PERIODE ESTIVALE (Juin-Septembre, {int(r['summer_days_valid'])} {sum_unit_label}) :")
        print(f"    P ete: {r['p_sum_mm']:5.1f} mm | Qs ete: {r['qs_sum_mm']:4.2f} mm | Qsb ete: {r['qsb_sum_mm']:4.2f} mm -> Part Qsb ete: {r['qsb_ratio_sum_pct']:4.1f}%")
        print(f"    Debit moyen observe: {r['q_obs_sum_mean_m3s']:4.2f} m3/s | Sim linres=0: {r['q_sim_lr0_sum_mean_m3s']:4.2f} m3/s (Biais: {r['summer_bias_lr0_m3s']:+5.2f} m3/s)")
        print(f"    Debit sim linres=1 : {r['q_sim_h1_sum_mean_m3s']:4.2f} m3/s (Biais: {r['summer_bias_h1_m3s']:+5.2f} m3/s)")

    # Moyennes 2017-2020 (synthese principale hors initialisation)
    sub_post = df_stats[df_stats['year'] >= 2017]
    print("\n" + "="*85)
    print("SYNTHESE 2017–2020 (CONDITIONS INITIALES STABILISEES)")
    print("="*85)
    print(f"Precipitation moyenne (P)    : {sub_post['p_ann_mm'].mean():.1f} mm/an ({sub_post['v_p_hm3'].mean():.1f} hm3)")
    print(f"Ruissellement surface (Qs)   : {sub_post['qs_ann_mm'].mean():.1f} mm/an ({sub_post['v_qs_hm3'].mean():.1f} hm3)")
    print(f"Ruissellement souterrain(Qsb): {sub_post['qsb_ann_mm'].mean():.1f} mm/an ({sub_post['v_qsb_hm3'].mean():.1f} hm3)")
    print(f"Part moyenne de Qsb annuelle : {sub_post['qsb_ratio_ann_pct'].mean():.1f}%")
    print(f"Part moyenne de Qsb estivale : {sub_post['qsb_ratio_sum_pct'].mean():.1f}%")
    print(f"Debit moyen observe ABH      : {sub_post['q_obs_mean_m3s'].mean():.2f} m3/s")
    print(f"Debit moyen simule linres=0  : {sub_post['q_sim_lr0_mean_m3s'].mean():.2f} m3/s (NSE moyen: {sub_post['nse_lr0'].mean():.3f}, R moyen: {sub_post['corr_lr0'].mean():.3f})")
    print(f"Debit moyen simule linres=1  : {sub_post['q_sim_h1_mean_m3s'].mean():.2f} m3/s (NSE moyen: {sub_post['nse_h1'].mean():.3f}, R moyen: {sub_post['corr_h1'].mean():.3f})")
    print(f"Biais estival moyen linres=0 : +{sub_post['summer_bias_lr0_m3s'].mean():.2f} m3/s (Obs moyen ete: {sub_post['q_obs_sum_mean_m3s'].mean():.2f} m3/s vs Sim: {sub_post['q_sim_lr0_sum_mean_m3s'].mean():.2f} m3/s)")

    # 5. Production de la figure de synthese interannuelle
    print("\n5. Generation de la figure de synthese interannuelle (2016–2020)...")
    out_fig_dir = os.path.join(routing_dir, "plots/sebou_bouregreg/figures/streamflow")
    os.makedirs(out_fig_dir, exist_ok=True)
    out_synth_png = os.path.join(out_fig_dir, f"{st_prefix}_{args.start_year}_{args.end_year}_synthesis.png")
    out_synth_pdf = os.path.join(out_fig_dir, f"{st_prefix}_{args.start_year}_{args.end_year}_synthesis.pdf")

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(13.0, 13.0), gridspec_kw={'height_ratios': [1.15, 1.15, 1.4]})
    
    yrs = df_stats['year'].values
    x = np.arange(len(yrs))
    width = 0.35

    # Palette harmonieuse et lisible
    c_p = '#1f77b4'
    c_qs = '#e6550d'
    c_qsb = '#2ca02c'
    c_obs = '#111111'
    c_lr0 = '#1f78b4'
    c_h1 = '#d62728'

    # --- PANNEAU A : FLUX ANNUELS (P, Qs, Qsb) ---
    bars_p = ax1.bar(x - width/2, df_stats['p_ann_mm'], width, label='Precipitation ($P$)', color=c_p, alpha=0.75, edgecolor='#08519c', lw=1.0)
    bars_qs = ax1.bar(x + width/2, df_stats['qs_ann_mm'], width, label='Surface Runoff ($Q_s$)', color=c_qs, alpha=0.9, edgecolor='#a63603', lw=1.0)
    bars_qsb = ax1.bar(x + width/2, df_stats['qsb_ann_mm'], width, bottom=df_stats['qs_ann_mm'], label='Subsurface Runoff ($Q_{sb}$)', color=c_qsb, alpha=0.85, edgecolor='#006d2c', lw=1.0)

    # Annotations des pourcentages de Qsb
    for i, yr in enumerate(yrs):
        qtot = df_stats.loc[i, 'qtot_ann_mm']
        qsb_pct = df_stats.loc[i, 'qsb_ratio_ann_pct']
        p_val = df_stats.loc[i, 'p_ann_mm']
        ax1.text(x[i] + width/2, qtot + 8, f"{qsb_pct:.1f}% $Q_{{sb}}$\n({qtot:.1f} mm)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#006d2c')
        ax1.text(x[i] - width/2, p_val + 8, f"{p_val:.0f} mm", ha='center', va='bottom', fontsize=8.5, color='#08519c')

    ax1.set_ylabel('Annual Amount\n(mm/year)', fontsize=11, fontweight='bold')
    ax1.set_title(f'(a) Interannual Precipitation and Annual Runoff Partitioning ({st_name} Catchment, Area = {tot_area_km2:,.0f} km²)', fontsize=12, fontweight='bold', loc='left', pad=8)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{y}\n(Init. cond. differ)" if y == 2016 else str(y) for y in yrs], fontsize=10, fontweight='semibold')
    ax1.set_ylim(0, max(df_stats['p_ann_mm']) * 1.18)
    ax1.grid(True, linestyle=':', alpha=0.5, color='#888888')
    ax1.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.5)

    # --- PANNEAU B : APPORTS ESTIVAUX (Juin-Septembre) ---
    # Titre corrige indiquant clairement que Qsb represente plus de 90 % des apports estivaux
    bars_sum_qs = ax2.bar(x, df_stats['qs_sum_mm'], width*1.1, label='Summer Surface Runoff ($Q_s$)', color=c_qs, alpha=0.9, edgecolor='#a63603', lw=1.0)
    bars_sum_qsb = ax2.bar(x, df_stats['qsb_sum_mm'], width*1.1, bottom=df_stats['qs_sum_mm'], label='Summer Subsurface Runoff ($Q_{sb}$)', color=c_qsb, alpha=0.85, edgecolor='#006d2c', lw=1.0)

    for i, yr in enumerate(yrs):
        qtot_s = df_stats.loc[i, 'qs_sum_mm'] + df_stats.loc[i, 'qsb_sum_mm']
        qsb_s_pct = df_stats.loc[i, 'qsb_ratio_sum_pct']
        ax2.text(x[i], qtot_s + 0.9, f"{qsb_s_pct:.1f}% $Q_{{sb}}$\n({qtot_s:.2f} mm)", ha='center', va='bottom', fontsize=9, fontweight='bold', color='#006d2c')

    ax2.set_ylabel('Summer Runoff\n(mm / Jun–Sep)', fontsize=11, fontweight='bold')
    min_qsb_s = df_stats['qsb_ratio_sum_pct'].min()
    if min_qsb_s >= 85.0:
        pct_floor = int(min_qsb_s // 5 * 5)
        title_b = f"(b) Summer Runoff Partitioning (June–September) — Subsurface Runoff ($Q_{{sb}}$) Represents Over {pct_floor}% of Summer Runoff Inputs"
    else:
        title_b = f"(b) Summer Runoff Partitioning (June–September) — Subsurface Runoff ($Q_{{sb}}$) Represents {min_qsb_s:.0f}–{df_stats['qsb_ratio_sum_pct'].max():.0f}% of Summer Runoff Inputs"
    ax2.set_title(title_b, fontsize=12, fontweight='bold', loc='left', pad=8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{y}\n(Init. cond. differ)" if y == 2016 else str(y) for y in yrs], fontsize=10, fontweight='semibold')
    ax2.set_ylim(0, max(df_stats['qs_sum_mm'] + df_stats['qsb_sum_mm']) * 1.25)
    ax2.grid(True, linestyle=':', alpha=0.5, color='#888888')
    ax2.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.5)

    # --- PANNEAU C : DEBITS (HYDROGRAMMES MENSUELS OU DEBITS ESTIVAUX) ---
    if not is_monthly:
        # Debits estivaux moyens pour les stations a observations journalieres
        w3 = 0.25
        bars_obs = ax3.bar(x - w3, df_stats['q_obs_sum_mean_m3s'], w3, label='Observed Streamflow (ABH)', color=c_obs, alpha=0.9, edgecolor='black', lw=1.0)
        bars_lr0 = ax3.bar(x, df_stats['q_sim_lr0_sum_mean_m3s'], w3, label='OPL Recent (HyMAP-2 linres=0)', color=c_lr0, alpha=0.9, edgecolor='#08519c', lw=1.0)
        bars_h1 = ax3.bar(x + w3, df_stats['q_sim_h1_sum_mean_m3s'], w3, label='OPL Historical (HyMAP-2 linres=1)', color=c_h1, alpha=0.75, edgecolor='#990000', lw=1.0, hatch='//')

        for i, yr in enumerate(yrs):
            q_obs_s = df_stats.loc[i, 'q_obs_sum_mean_m3s']
            q_lr0_s = df_stats.loc[i, 'q_sim_lr0_sum_mean_m3s']
            b_val = df_stats.loc[i, 'summer_bias_lr0_m3s']
            ax3.text(x[i], q_lr0_s + 0.18, f"Bias:\n+{b_val:.2f} m³/s" if b_val >= 0 else f"Bias:\n{b_val:.2f} m³/s", ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#08519c')
            ax3.text(x[i] - w3, q_obs_s + 0.18, f"{q_obs_s:.2f}", ha='center', va='bottom', fontsize=8.5, color='#111111')

        ax3.set_ylabel('Mean Summer Discharge\n(m³/s / Jun–Sep)', fontsize=11, fontweight='bold')
        ax3.set_title(f'(c) Summer Streamflow at {st_name}: Persistent Positive Bias Associated with Runoff Inputs Dominated by $Q_{{sb}}$', fontsize=12, fontweight='bold', loc='left', pad=8)
        ax3.set_xticks(x)
        ax3.set_xticklabels([f"{y}\n(Init. cond. differ)" if y == 2016 else str(y) for y in yrs], fontsize=10, fontweight='semibold')
        ax3.set_ylim(0, max(df_stats['q_sim_lr0_sum_mean_m3s']) * 1.25)
        ax3.grid(True, linestyle=':', alpha=0.5, color='#888888')
        ax3.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.5)
    else:
        # Hydrogrammes mensuels 2016–2020 pour les stations a observations mensuelles (Dar El Hamra)
        m_dates = [pd.to_datetime(f"{r['year']}-{int(r['month']):02d}-15") for _, r in df_monthly.iterrows()]

        ax3.plot(m_dates, df_monthly['q_obs_m3s'].values, color=c_obs, marker='o', markersize=4.5, lw=1.8, label='Observed Monthly Discharge (ABH)', zorder=4)
        ax3.plot(m_dates, df_monthly['q_sim_linres0_m3s'].values, color=c_lr0, marker='s', markersize=4.0, lw=1.6, label='OPL Recent (HyMAP-2 linres=0)', zorder=3)
        ax3.plot(m_dates, df_monthly['q_sim_hist_m3s'].values, color=c_h1, marker='^', markersize=4.0, lw=1.4, ls='--', alpha=0.85, label='OPL Historical (HyMAP-2 linres=1)', zorder=2)

        # Signalement des donnees suspectes (BDRE geometric decay en fev-juin 2020)
        suspect_mask = df_monthly['obs_flag'] == 'reconstruit_suspect'
        if suspect_mask.any():
            suspect_dates = [m_dates[i] for i, val in enumerate(suspect_mask) if val]
            suspect_q = df_monthly.loc[suspect_mask, 'q_obs_m3s'].values
            ax3.scatter(suspect_dates, suspect_q, color='#e6550d', edgecolors='#a63603', s=65, zorder=5, label='Observed (Reconstruit suspect, decrue geometrique BDRE)')

        # Annotations cles
        ax3.annotate('Init. conditions differ (Jan 2016):\nlinres=1 warm start (~0.37 m³/s)\nlinres=0 cold start (~0.0005 m³/s)',
                     xy=(pd.to_datetime('2016-01-15'), float(df_monthly.loc[0, 'q_sim_linres0_m3s'])),
                     xytext=(pd.to_datetime('2016-01-15'), 5.0),
                     arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=1.0),
                     fontsize=8.5, fontweight='semibold', color='#252525',
                     bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))

        idx_mar18 = df_monthly[df_monthly['year_month'] == '2018-03'].index[0]
        q_mar18_obs = float(df_monthly.loc[idx_mar18, 'q_obs_m3s'])
        q_mar18_sim = float(df_monthly.loc[idx_mar18, 'q_sim_linres0_m3s'])
        ax3.annotate(f'Peak Flood Underestimation (Mar 2018)\nObs: {q_mar18_obs:.1f} m³/s vs Sim: {q_mar18_sim:.2f} m³/s\n(Severe winter volume deficit: annual PBIAS ≈ -78%)',
                     xy=(pd.to_datetime('2018-03-15'), q_mar18_obs),
                     xytext=(pd.to_datetime('2017-02-15'), 11.2),
                     arrowprops=dict(facecolor='#111111', arrowstyle='->', lw=1.1),
                     fontsize=8.5, fontweight='semibold', color='#111111',
                     bbox=dict(boxstyle='round,pad=0.25', facecolor='#fee6ce', edgecolor='#fdae6b', lw=0.8))

        idx_jul18 = df_monthly[df_monthly['year_month'] == '2018-07'].index[0]
        q_jul18_obs = float(df_monthly.loc[idx_jul18, 'q_obs_m3s'])
        q_jul18_sim = float(df_monthly.loc[idx_jul18, 'q_sim_linres0_m3s'])
        ax3.annotate(f'Summer Low-Flow Alignment (Summer 2018)\nObs mean: 0.36 m³/s vs Sim: 0.44 m³/s\n(No persistent summer overestimation)',
                     xy=(pd.to_datetime('2018-07-15'), q_jul18_sim),
                     xytext=(pd.to_datetime('2018-05-15'), 6.5),
                     arrowprops=dict(facecolor='#08519c', arrowstyle='->', lw=1.0),
                     fontsize=8.5, fontweight='semibold', color='#08519c',
                     bbox=dict(boxstyle='round,pad=0.25', facecolor='#eff3ff', edgecolor='#bdd7e7', lw=0.8))

        ax3.set_ylabel('Monthly Mean Discharge\n(m³/s)', fontsize=11, fontweight='bold')
        ax3.set_title(f'(c) Monthly Streamflow (2016–2020) at {st_name}: Moderate Summer Bias vs Severe Winter High-Flow Deficit', fontsize=12, fontweight='bold', loc='left', pad=8)
        ax3.set_xlim(pd.to_datetime('2015-11-15'), pd.to_datetime('2021-02-15'))
        ax3.xaxis.set_major_locator(mdates.YearLocator())
        ax3.xaxis.set_minor_locator(mdates.MonthLocator())
        ax3.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))
        ax3.set_xlabel('Year', fontsize=11, fontweight='bold')
        ax3.set_ylim(-0.2, 14.5)
        ax3.grid(True, linestyle=':', alpha=0.5, color='#888888')
        ax3.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.0)

    plt.tight_layout(h_pad=2.5)
    fig.savefig(out_synth_png, dpi=300)
    fig.savefig(out_synth_pdf)
    plt.close(fig)
    print(f"   Figure de synthese PNG : {out_synth_png}")
    print(f"   Figure de synthese PDF : {out_synth_pdf}")

    if os.path.exists(args.artifact_dir):
        art_synth = os.path.join(args.artifact_dir, f"{st_prefix}_{args.start_year}_{args.end_year}_synthesis.png")
        shutil.copyfile(out_synth_png, art_synth)
        print(f"   Copie synthese vers artefacts : {art_synth}")

    # 6. Regeneration de la figure detaillee 2018 si requise
    if not is_monthly and 2018 in years and not args.no_plot_2018:
        print("\n6. Regeneration de la figure detaillee 3-panneaux pour 2018...")
        sub_2018 = df_idx[df_idx['year'] == 2018]
        dates_18 = sub_2018.index.to_pydatetime()
        p_18 = sub_2018['precip_mm_d'].values
        qs_18 = sub_2018['qs_mm_d'].values
        qsb_18 = sub_2018['qsb_mm_d'].values
        qtot_18 = qs_18 + qsb_18
        q_obs_18 = sub_2018['q_obs_m3s'].values
        q_h1_18 = sub_2018['q_sim_hist_m3s'].values
        q_lr0_18 = sub_2018['q_sim_linres0_m3s'].values

        p_ann_18 = float(sub_2018['precip_mm_d'].sum())
        p_sum_18 = float(sub_2018.loc['2018-06-01':'2018-09-30', 'precip_mm_d'].sum())

        fig18, (ax_p, ax_q, ax_s) = plt.subplots(3, 1, figsize=(13.5, 11.0), sharex=True, gridspec_kw={'height_ratios': [1.0, 1.25, 1.45]})

        # Panneau A : Precipitation
        ax_p.bar(dates_18, p_18, width=0.85, color=c_p, alpha=0.85, edgecolor='none', label='Basin-Averaged Precipitation ($P$)')
        ax_p.set_ylabel('Precipitation\n(mm/day)', fontsize=11, fontweight='bold')
        ax_p.set_ylim(0, max(p_18) * 1.18)
        ax_p.grid(True, linestyle=':', alpha=0.5, color='#888888')
        ax_p.set_title(f'(a) Basin-Averaged Daily Precipitation — {st_name} Catchment (Area = {tot_area_km2:,.0f} km²)', fontsize=12, fontweight='bold', loc='left', pad=8)
        
        # Pics de precipitations 2018 calcules dynamiquement
        dt_mar_p = sub_2018.loc['2018-03-01':'2018-03-15', 'precip_mm_d'].idxmax()
        p_mar_peak = float(sub_2018.loc[dt_mar_p, 'precip_mm_d'])
        ax_p.annotate(f"Mar {dt_mar_p.day:02d} (2018): {p_mar_peak:.1f} mm/d", xy=(dt_mar_p, p_mar_peak), xytext=(pd.to_datetime('2018-01-28'), 46),
                      arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=0.9), fontsize=9, fontweight='semibold',
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#aaaaaa', alpha=0.9))

        dt_apr_p = sub_2018.loc['2018-04-15':'2018-04-30', 'precip_mm_d'].idxmax()
        p_apr_peak = float(sub_2018.loc[dt_apr_p, 'precip_mm_d'])
        ax_p.annotate(f"Apr {dt_apr_p.day:02d} (2018): {p_apr_peak:.1f} mm/d", xy=(dt_apr_p, p_apr_peak), xytext=(pd.to_datetime('2018-03-18'), 56),
                      arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=0.9), fontsize=9, fontweight='semibold',
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#aaaaaa', alpha=0.9))

        dt_nov_p = sub_2018.loc['2018-11-10':'2018-11-25', 'precip_mm_d'].idxmax()
        p_nov_peak = float(sub_2018.loc[dt_nov_p, 'precip_mm_d'])
        ax_p.annotate(f"Nov {dt_nov_p.day:02d} (2018): {p_nov_peak:.1f} mm/d", xy=(dt_nov_p, p_nov_peak), xytext=(pd.to_datetime('2018-10-15'), 28),
                      arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=0.9), fontsize=9, fontweight='semibold',
                      bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='#aaaaaa', alpha=0.9))

        stats_p_text = f"Annual P (2018): {p_ann_18:.1f} mm/yr\nSummer P (Jun–Sep): {p_sum_18:.1f} mm"
        ax_p.text(0.985, 0.90, stats_p_text, transform=ax_p.transAxes, ha='right', va='top', fontsize=9.5,
                  bbox=dict(boxstyle='square,pad=0.4', facecolor='#f7fbff', edgecolor='#9ecae1', lw=0.8))

        # Panneau B : Ruissellements
        ax_q.plot(dates_18, qs_18, color=c_qs, lw=1.6, label='Surface Runoff ($Q_s$)', zorder=4)
        ax_q.plot(dates_18, qsb_18, color=c_qsb, lw=1.8, label='Subsurface Runoff ($Q_{sb}$)', zorder=3)
        ax_q.fill_between(dates_18, 0, qsb_18, color=c_qsb, alpha=0.15, zorder=2)
        ax_q.plot(dates_18, qtot_18, color='#756bb1', lw=1.1, ls=':', label='Total Runoff ($Q_s + Q_{sb}$)', zorder=3)
        ax_q.set_ylabel('Runoff rate\n(mm/day)', fontsize=11, fontweight='bold')
        ax_q.set_ylim(0, max(qtot_18) * 1.15)
        ax_q.grid(True, linestyle=':', alpha=0.5, color='#888888')
        ax_q.set_title('(b) Basin-Averaged Daily Runoff Partitioning (Noah-MP Open-Loop)', fontsize=12, fontweight='bold', loc='left', pad=8)
        ax_q.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.5)

        # Calcul dynamique des metriques estivales 2018 pour l'annotation
        sub_sum_18 = sub_2018.loc['2018-06-01':'2018-09-30']
        qsb_sum_mean_18 = float(sub_sum_18['qsb_mm_d'].mean())
        qs_sum_mean_18 = float(sub_sum_18['qs_mm_d'].mean())
        qtot_sum_mean_18 = qsb_sum_mean_18 + qs_sum_mean_18
        qsb_sum_pct_18 = (qsb_sum_mean_18 / qtot_sum_mean_18 * 100.0) if qtot_sum_mean_18 > 0 else 0.0
        qin_sum_mean_18 = float(sub_sum_18['qin_m3s'].mean())

        ax_q.annotate(f'Sustained Subsurface Runoff (Summer 2018)\nSummer mean $Q_{{sb}}$ = {qsb_sum_mean_18:.2f} mm/d ({qsb_sum_pct_18:.1f}% of runoff inputs)\nFeeds ~{qin_sum_mean_18:.1f} m³/s into river network',
                      xy=(pd.to_datetime('2018-07-20'), qsb_sum_mean_18), xytext=(pd.to_datetime('2018-06-15'), max(qtot_18) * 0.72),
                      arrowprops=dict(facecolor=c_qsb, arrowstyle='->', lw=1.2), fontsize=9, fontweight='semibold', color='#005a32',
                      bbox=dict(boxstyle='round,pad=0.3', facecolor='#e5f5e0', edgecolor='#74c476', lw=0.9))

        # Panneau C : Debits
        ax_s.plot(dates_18, q_obs_18, color=c_obs, lw=1.5, label='Observed Streamflow (ABH)', alpha=0.95, zorder=5)
        ax_s.plot(dates_18, q_h1_18, color=c_h1, lw=1.3, ls='--', label='OPL Historical (HyMAP-2 linres=1)', alpha=0.9, zorder=3)
        ax_s.plot(dates_18, q_lr0_18, color=c_lr0, lw=1.6, label='OPL Recent (HyMAP-2 linres=0, Job 8272794)', alpha=0.95, zorder=4)
        ax_s.set_ylabel('Streamflow\n(m³/s)', fontsize=11, fontweight='bold')
        max_q = max(float(np.nanmax(q_obs_18)), float(np.nanmax(q_lr0_18)))
        ax_s.set_ylim(0, max_q * 1.18)
        ax_s.grid(True, linestyle=':', alpha=0.5, color='#888888')
        ax_s.set_title(f'(c) Daily Streamflow at {st_name} Outlet (Row {outlet_row}, Col {outlet_col})', fontsize=12, fontweight='bold', loc='left', pad=8)
        ax_s.legend(loc='upper right', frameon=True, framealpha=0.95, facecolor='white', edgecolor='#cccccc', fontsize=9.5)

        # Annotations calculees dynamiquement et adaptees a la station
        if st_id == 'b_l_chafia':
            dt_mar_flood = sub_2018.loc['2018-03-01':'2018-03-15', 'q_obs_m3s'].idxmax()
            q_mar_obs = float(sub_2018.loc[dt_mar_flood, 'q_obs_m3s'])
            q_mar_sim = float(sub_2018.loc[dt_mar_flood, 'q_sim_linres0_m3s'])
            ax_s.annotate(f'Mar {dt_mar_flood.day:02d} (2018) Flood Peak\nUnderestimated by model\nObs: {q_mar_obs:.1f} vs Sim: {q_mar_sim:.1f} m³/s',
                          xy=(dt_mar_flood, q_mar_obs), xytext=(pd.to_datetime('2018-03-18'), 165),
                          arrowprops=dict(facecolor='#111111', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#111111',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))

            dt_apr_flood = sub_2018.loc['2018-04-20':'2018-04-30', 'q_sim_linres0_m3s'].idxmax()
            q_apr_sim = float(sub_2018.loc[dt_apr_flood, 'q_sim_linres0_m3s'])
            q_apr_obs = float(sub_2018.loc[dt_apr_flood, 'q_obs_m3s'])
            ax_s.annotate(f'Apr {dt_apr_flood.day:02d} (2018) Flood Peak\nImproved timing in linres=0\nSim: {q_apr_sim:.1f} vs Obs: {q_apr_obs:.1f} m³/s',
                          xy=(dt_apr_flood, q_apr_sim), xytext=(pd.to_datetime('2018-05-12'), 110),
                          arrowprops=dict(facecolor=c_lr0, arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#08519c',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#eff3ff', edgecolor='#bdd7e7', lw=0.8))

            q_obs_sum_18 = float(sub_sum_18['q_obs_m3s'].mean())
            q_lr0_sum_18 = float(sub_sum_18['q_sim_linres0_m3s'].mean())
            q_obs_sum_min_18 = float(sub_sum_18['q_obs_m3s'].min())
            ax_s.annotate(f'Summer Streamflow Bias (2018)\nSimulations: ~{q_lr0_sum_18:.1f} m³/s vs Observed mean: {q_obs_sum_18:.2f} m³/s\n(Obs daily lows ~{q_obs_sum_min_18:.1f} m³/s; runoff inputs dominated by $Q_{{sb}}$)',
                          xy=(pd.to_datetime('2018-08-01'), q_lr0_sum_18), xytext=(pd.to_datetime('2018-07-20'), 65),
                          arrowprops=dict(facecolor='#d95f02', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#a63603',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#fee6ce', edgecolor='#fdae6b', lw=0.8))

            sub_dec_18 = sub_2018.loc['2018-12-01':'2018-12-31']
            q_lr0_dec_end = float(sub_2018.loc['2018-12-31', 'q_sim_linres0_m3s'])
            q_obs_dec_min = float(sub_dec_18['q_obs_m3s'].min())
            q_obs_dec_max = float(sub_dec_18['q_obs_m3s'].max())
            ax_s.annotate(f'Late-Year Stabilization (Dec 2018): ~{q_lr0_dec_end:.1f} m³/s\nObserved Dec range: {q_obs_dec_min:.1f}–{q_obs_dec_max:.1f} m³/s\n(Gradual physical recession, no sudden drop to zero)',
                          xy=(pd.to_datetime('2018-12-15'), q_lr0_dec_end), xytext=(pd.to_datetime('2018-10-10'), 130),
                          arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#252525',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))
        elif st_id == 'b_s_jabeur':
            dt_mar_flood = sub_2018.loc['2018-03-01':'2018-03-15', 'q_obs_m3s'].idxmax()
            q_mar_obs = float(sub_2018.loc[dt_mar_flood, 'q_obs_m3s'])
            q_mar_sim = float(sub_2018.loc[dt_mar_flood, 'q_sim_linres0_m3s'])
            ax_s.annotate(f'Mar {dt_mar_flood.day:02d} (2018) Flash Flood\nSevere peak underestimation\nObs: {q_mar_obs:.1f} vs Sim: {q_mar_sim:.1f} m³/s',
                          xy=(dt_mar_flood, q_mar_obs), xytext=(pd.to_datetime('2018-03-16'), 305),
                          arrowprops=dict(facecolor='#111111', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#111111',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))

            dt_apr_flood = sub_2018.loc['2018-04-20':'2018-04-30', 'q_sim_linres0_m3s'].idxmax()
            q_apr_sim = float(sub_2018.loc[dt_apr_flood, 'q_sim_linres0_m3s'])
            q_apr_obs = float(sub_2018.loc[dt_apr_flood, 'q_obs_m3s'])
            q_apr_h1 = float(sub_2018.loc[dt_apr_flood, 'q_sim_hist_m3s'])
            ax_s.annotate(f'Apr {dt_apr_flood.day:02d} (2018) Flood Peak\nlinres=0 triples peak on event date ({q_apr_sim:.1f} vs {q_apr_h1:.1f} m³/s)\nSynchronous with Obs: {q_apr_obs:.1f} m³/s',
                          xy=(dt_apr_flood, q_apr_sim), xytext=(pd.to_datetime('2018-04-25'), 215), ha='center',
                          arrowprops=dict(facecolor=c_lr0, arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#08519c',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#eff3ff', edgecolor='#bdd7e7', lw=0.8))

            q_obs_sum_18 = float(sub_sum_18['q_obs_m3s'].mean())
            q_lr0_sum_18 = float(sub_sum_18['q_sim_linres0_m3s'].mean())
            n_zeros = int((sub_sum_18['q_obs_m3s'] == 0.0).sum())
            ax_s.annotate(f'Summer Flow Overestimation (2018)\nSimulations: ~{q_lr0_sum_18:.1f} m³/s vs Obs mean: {q_obs_sum_18:.2f} m³/s\n(River dries up: {n_zeros} zero-flow days in obs;\nmodel fed by continuous $Q_{{sb}}$ inputs)',
                          xy=(pd.to_datetime('2018-08-01'), q_lr0_sum_18), xytext=(pd.to_datetime('2018-07-15'), 105), ha='center',
                          arrowprops=dict(facecolor='#d95f02', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#a63603',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#fee6ce', edgecolor='#fdae6b', lw=0.8))

            sub_dec_18 = sub_2018.loc['2018-12-01':'2018-12-31']
            q_lr0_dec_end = float(sub_2018.loc['2018-12-31', 'q_sim_linres0_m3s'])
            q_obs_dec_min = float(sub_dec_18['q_obs_m3s'].min())
            q_obs_dec_max = float(sub_dec_18['q_obs_m3s'].max())
            ax_s.annotate(f'Late-Year Stabilization (Dec 2018): ~{q_lr0_dec_end:.1f} m³/s\nObserved Dec range: {q_obs_dec_min:.2f}–{q_obs_dec_max:.1f} m³/s\n(Gradual physical recession in linres=0)',
                          xy=(pd.to_datetime('2018-12-25'), q_lr0_dec_end), xytext=(pd.to_datetime('2018-11-15'), 285), ha='center',
                          arrowprops=dict(facecolor='#333333', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#252525',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))
        else:
            dt_flood = sub_2018.loc['2018-01-01':'2018-05-31', 'q_obs_m3s'].idxmax()
            q_flood_obs = float(sub_2018.loc[dt_flood, 'q_obs_m3s'])
            q_flood_sim = float(sub_2018.loc[dt_flood, 'q_sim_linres0_m3s'])
            ax_s.annotate(f'Spring Flood Peak ({dt_flood.strftime("%b %d")})\nObs: {q_flood_obs:.1f} vs Sim: {q_flood_sim:.1f} m³/s',
                          xy=(dt_flood, q_flood_obs), xytext=(dt_flood + datetime.timedelta(days=12), max_q * 0.75),
                          arrowprops=dict(facecolor='#111111', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#111111',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#f7f7f7', edgecolor='#cccccc', lw=0.8))

            q_obs_sum_18 = float(sub_sum_18['q_obs_m3s'].mean())
            q_lr0_sum_18 = float(sub_sum_18['q_sim_linres0_m3s'].mean())
            ax_s.annotate(f'Summer Streamflow (2018)\nSim: ~{q_lr0_sum_18:.1f} m³/s vs Obs: {q_obs_sum_18:.2f} m³/s',
                          xy=(pd.to_datetime('2018-08-01'), q_lr0_sum_18), xytext=(pd.to_datetime('2018-07-15'), max_q * 0.30),
                          arrowprops=dict(facecolor='#d95f02', arrowstyle='->', lw=1.1), fontsize=8.5, fontweight='semibold', color='#a63603',
                          bbox=dict(boxstyle='round,pad=0.25', facecolor='#fee6ce', edgecolor='#fdae6b', lw=0.8))

        ax_s.set_xlim(pd.to_datetime('2018-01-01'), pd.to_datetime('2018-12-31'))
        ax_s.xaxis.set_major_locator(mdates.MonthLocator())
        ax_s.xaxis.set_major_formatter(mdates.DateFormatter('%b\n%Y'))
        ax_s.xaxis.set_minor_locator(AutoMinorLocator(2))
        ax_s.set_xlabel('Date (2018)', fontsize=11, fontweight='bold')

        plt.tight_layout()
        out_png_18 = os.path.join(out_fig_dir, f"{st_prefix}_2018_fluxes_and_streamflow.png")
        out_pdf_18 = os.path.join(out_fig_dir, f"{st_prefix}_2018_fluxes_and_streamflow.pdf")
        fig18.savefig(out_png_18, dpi=300)
        fig18.savefig(out_pdf_18)
        plt.close(fig18)
        print(f"   Figure 2018 detaillee PNG : {out_png_18}")
        print(f"   Figure 2018 detaillee PDF : {out_pdf_18}")

        if os.path.exists(args.artifact_dir):
            art_png_18 = os.path.join(args.artifact_dir, f"{st_prefix}_2018_fluxes_and_streamflow.png")
            shutil.copyfile(out_png_18, art_png_18)
            print(f"   Copie 2018 detaillee vers artefacts : {art_png_18}")

    print(f"\nDiagnostic {st_name} termine avec succes.")

if __name__ == '__main__':
    main()
