#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Intercomparaison des produits de precipitations pour l'annee 2018 :
  - GPM IMERG V07B Final (forcage utilise par Noah-MP, TotalPrecip_tavg / Rainf_f_tavg)
  - MSWEP v2.8 (Multi-Source Weighted-Ensemble Precipitation, 0.10 deg)
  - ERA5 (Reanalyse ECMWF, total precipitation 0.25 deg)

Bassins versants etudies (reseau D8 HyMAP valide) :
  1. Lalla Chafia (Bouregreg amont) : 133 mailles, 3 333.35 km2 (outlet 75, 71)
  2. Sidi Jabeur (Grou) : 121 mailles, 3 130.55 km2 (outlet 71, 71)
  3. Dar El Hamra (Zloul / Sebou) : 26 mailles, 654.75 km2 (outlet 75, 112)

Objectif scientifique :
  Tester l'hypothese d'Augusto Getirana sur le forcage de precipitation :
  determiner si les sous-estimations majeures des crues de 2018 (notamment mars
  et novembre) proviennent d'un deficit de pluie dans IMERG ou des processus internes
  de generation de ruissellement et d'infiltration dans Noah-MP.

Sorties generees :
  - CSV journalier : plots/sebou_bouregreg/tables/daily_precip_comparison_2018.csv
  - CSV de synthese (annuel, mensuel, evenements) : plots/sebou_bouregreg/tables/summary_precip_comparison_2018.csv
  - Figure comparative des crues : plots/sebou_bouregreg/figures/forcing_runoff/events_2018_precip_intercomparison.png (.pdf)
"""

import os
import sys
import shutil
import argparse
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.ticker import AutoMinorLocator

BASINS_CONFIG = {
    'b_l_chafia': {
        'name': 'Lalla Chafia',
        'basin': 'Bouregreg amont',
        'cell': (75, 71),
        'csv_imerg': 'experiments/NorthMor/routing/plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv',
        'color': '#1f77b4'
    },
    'b_s_jabeur': {
        'name': 'Sidi Jabeur',
        'basin': 'Grou (Bouregreg)',
        'cell': (71, 71),
        'csv_imerg': 'experiments/NorthMor/routing/plots/sebou_bouregreg/tables/sidi_jabeur_fluxes_2016_2020.csv',
        'color': '#2ca02c'
    },
    'dar_el_hamra': {
        'name': 'Dar El Hamra',
        'basin': 'Zloul (Sebou)',
        'cell': (75, 112),
        'csv_imerg': 'experiments/NorthMor/routing/plots/sebou_bouregreg/tables/dar_el_hamra_fluxes_daily_2018.csv',
        'color': '#d62728'
    }
}

EVENTS_CONFIG = [
    {
        'id': 'event_mar',
        'name': 'Crue 05–09 mars 2018',
        'short_title': '05–09 mars 2018\n(Fin d\'hiver)',
        'start': '2018-03-05',
        'end': '2018-03-09'
    },
    {
        'id': 'event_apr',
        'name': 'Crue 23–27 avril 2018',
        'short_title': '23–27 avril 2018\n(Orages de printemps)',
        'start': '2018-04-23',
        'end': '2018-04-27'
    },
    {
        'id': 'event_oct_nov',
        'name': 'Crue 28 oct – 03 nov 2018',
        'short_title': '28 oct – 03 nov 2018\n(1ère crue d\'automne)',
        'start': '2018-10-28',
        'end': '2018-11-03'
    },
    {
        'id': 'event_nov',
        'name': 'Crue 18–25 nov 2018',
        'short_title': '18–25 nov 2018\n(Grande crue d\'automne)',
        'start': '2018-11-18',
        'end': '2018-11-25'
    }
]

def parse_args():
    parser = argparse.ArgumentParser(description="Intercomparaison precipitations IMERG vs MSWEP vs ERA5 (2018).")
    parser.add_argument("--year", type=int, default=2018, help="Annee d'analyse (defaut: 2018).")
    parser.add_argument("--ldt-path", default="experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc",
                        help="Chemin vers le fichier LDT HyMAP.")
    parser.add_argument("--mswep-path",
                        default="/srv/lustre01/project/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/mswep/all_Mor/mswep_1979_2020.nc",
                        help="Chemin vers le fichier NetCDF MSWEP.")
    parser.add_argument("--era5-path",
                        default="/srv/lustre01/project/climat-um6p-st-iwri-7ksifkvwkuy/shared/TEAM/data/ERA5/from_khadija/era5_total_precipitation.nc",
                        help="Chemin vers le fichier NetCDF ERA5.")
    parser.add_argument("--artifact-dir",
                        default="/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e",
                        help="Repertoire d'artefacts pour affichage UI.")
    parser.add_argument("--out-tables-dir",
                        default="experiments/NorthMor/routing/plots/sebou_bouregreg/tables",
                        help="Dossier de sortie pour les tableaux CSV.")
    parser.add_argument("--out-figs-dir",
                        default="experiments/NorthMor/routing/plots/sebou_bouregreg/figures/forcing_runoff",
                        help="Dossier de sortie pour les figures PNG/PDF.")
    return parser.parse_args()

def delineate_catchment(flow_x, flow_y, area, outlet_row, outlet_col):
    """Delimite le bassin versant amont D8 a partir du reseau hydrographique HyMAP."""
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

    cat = sorted(list(vis))
    cat_rows = np.array([r for r, c in cat], dtype=np.int32)
    cat_cols = np.array([c for r, c in cat], dtype=np.int32)
    cat_areas = area[cat_rows, cat_cols]
    tot_area_m2 = float(np.sum(cat_areas))
    return cat_rows, cat_cols, cat_areas, tot_area_m2

def compute_bilinear_weights(lat_src, lon_src, lat_h, lon_h, cat_rows, cat_cols, cat_areas, tot_area):
    """
    Calcule les poids d'interpolation bilineaire projetes sur les mailles HyMAP
    puis ponderes par leurs aires respectives.
    Partition d'unite exacte : somme des poids = 1.0.
    """
    node_weights = {}
    lat_is_asc = (lat_src[1] > lat_src[0])
    
    for r, c, a in zip(cat_rows, cat_cols, cat_areas):
        clat = lat_h[r, c]
        clon = lon_h[r, c]
        
        if lat_is_asc:
            j = np.searchsorted(lat_src, clat) - 1
            j = max(0, min(j, len(lat_src) - 2))
            dj = (clat - lat_src[j]) / (lat_src[j+1] - lat_src[j])
        else:
            j = np.searchsorted(-lat_src, -clat) - 1
            j = max(0, min(j, len(lat_src) - 2))
            dj = (clat - lat_src[j]) / (lat_src[j+1] - lat_src[j])
            
        i = np.searchsorted(lon_src, clon) - 1
        i = max(0, min(i, len(lon_src) - 2))
        di = (clon - lon_src[i]) / (lon_src[i+1] - lon_src[i])
        
        w_cell = a / tot_area
        w00 = (1.0 - dj) * (1.0 - di) * w_cell
        w01 = (1.0 - dj) * di * w_cell
        w10 = dj * (1.0 - di) * w_cell
        w11 = dj * di * w_cell
        
        for node, w in [((j, i), w00), ((j, i+1), w01), ((j+1, i), w10), ((j+1, i+1), w11)]:
            node_weights[node] = node_weights.get(node, 0.0) + w
            
    # Verification de la partition d'unite
    sum_w = sum(node_weights.values())
    assert abs(sum_w - 1.0) < 1e-6, f"Erreur de normalisation spatiale : somme={sum_w}"
    return node_weights

def extract_weighted_series(ds_var, time_indices, node_weights, scale_factor=1.0):
    """Extrait la serie temporelle journaliere ponderee a partir des poids precalcules."""
    nodes = list(node_weights.keys())
    j_min = min(n[0] for n in nodes)
    j_max = max(n[0] for n in nodes)
    i_min = min(n[1] for n in nodes)
    i_max = max(n[1] for n in nodes)
    
    t_start, t_end = time_indices[0], time_indices[-1] + 1
    sub_data = ds_var[t_start:t_end, j_min:j_max+1, i_min:i_max+1]
    
    res = np.zeros(len(time_indices), dtype=np.float64)
    for (j, i), w in node_weights.items():
        res += w * sub_data[:, j - j_min, i - i_min]
    return res * scale_factor

def main():
    args = parse_args()
    print("================================================================================")
    print(" INTERCOMPARAISON PRECIPITATIONS 2018 : IMERG (Noah-MP) vs MSWEP v2 vs ERA5")
    print("================================================================================")
    
    os.makedirs(args.out_tables_dir, exist_ok=True)
    os.makedirs(args.out_figs_dir, exist_ok=True)
    
    # 1. Chargement de la geometrie LDT
    print(f"Chargement du reseau LDT : {args.ldt_path}")
    ds_ldt = nc.Dataset(args.ldt_path)
    flow_x = ds_ldt['HYMAP_flow_direction_x'][:]
    flow_y = ds_ldt['HYMAP_flow_direction_y'][:]
    area = ds_ldt['HYMAP_grid_area'][:].filled(0.0)
    lat_h = ds_ldt['lat'][:]
    lon_h = ds_ldt['lon'][:]
    ds_ldt.close()
    
    # Delimitation des 3 bassins
    catchments = {}
    for code, binfo in BASINS_CONFIG.items():
        orow, ocol = binfo['cell']
        c_rows, c_cols, c_areas, tot_area_m2 = delineate_catchment(flow_x, flow_y, area, orow, ocol)
        catchments[code] = {
            'rows': c_rows,
            'cols': c_cols,
            'areas': c_areas,
            'tot_area_m2': tot_area_m2,
            'area_km2': tot_area_m2 / 1e6,
            'n_cells': len(c_rows)
        }
        print(f"  - {binfo['name']:<15} : {len(c_rows)} mailles HyMAP, {tot_area_m2/1e6:8.2f} km2 (outlet [{orow}, {ocol}])")

    # 2. Ouverture des produits en lecture seule
    print(f"\nOuverture de MSWEP : {args.mswep_path}")
    ds_m = nc.Dataset(args.mswep_path, 'r')
    lon_m = ds_m.variables['lon'][:]
    lat_m = ds_m.variables['lat'][:]
    tm = ds_m.variables['time']
    dates_m = nc.num2date(tm[:], units=tm.units, calendar=tm.calendar)
    dates_m_dt = pd.to_datetime([f"{d.year:04d}-{d.month:02d}-{d.day:02d}" for d in dates_m])
    idx_m_2018 = np.where(dates_m_dt.year == args.year)[0]
    dates_2018 = dates_m_dt[idx_m_2018]
    print(f"  MSWEP : {len(idx_m_2018)} pas de temps en {args.year} ({dates_2018[0].date()} a {dates_2018[-1].date()})")

    print(f"\nOuverture d'ERA5 : {args.era5_path}")
    ds_e = nc.Dataset(args.era5_path, 'r')
    lon_e = ds_e.variables['longitude'][:]
    lat_e = ds_e.variables['latitude'][:]
    te = ds_e.variables['valid_time']
    dates_e = nc.num2date(te[:], units=te.units, calendar=te.calendar)
    dates_e_dt = pd.to_datetime([f"{d.year:04d}-{d.month:02d}-{d.day:02d}" for d in dates_e])
    idx_e_2018 = np.where(dates_e_dt.year == args.year)[0]
    print(f"  ERA5  : {len(idx_e_2018)} pas de temps en {args.year} ({dates_e_dt[idx_e_2018[0]].date()} a {dates_e_dt[idx_e_2018[-1]].date()})")

    # 3. Extraction spatio-temporelle pour chaque bassin
    basin_data = {}
    daily_records = []

    for code, binfo in BASINS_CONFIG.items():
        cat = catchments[code]
        print(f"\nExtraction spatiale pour {binfo['name']} ({cat['area_km2']:.1f} km2)...")
        
        # Poids spatiaux bilineaires
        w_mswep = compute_bilinear_weights(lat_m, lon_m, lat_h, lon_h, cat['rows'], cat['cols'], cat['areas'], cat['tot_area_m2'])
        w_era5 = compute_bilinear_weights(lat_e, lon_e, lat_h, lon_h, cat['rows'], cat['cols'], cat['areas'], cat['tot_area_m2'])
        print(f"  Poids spatiaux : {len(w_mswep)} mailles MSWEP (somme={sum(w_mswep.values()):.4f}), {len(w_era5)} mailles ERA5 (somme={sum(w_era5.values()):.4f})")

        # Extraction MSWEP (unite mm/d)
        mswep_arr = extract_weighted_series(ds_m.variables['precipitation'], idx_m_2018, w_mswep, scale_factor=1.0)
        s_mswep = pd.Series(mswep_arr, index=dates_2018)

        # Extraction ERA5 (unite m -> mm/d avec conversion 24000.0)
        era5_arr = extract_weighted_series(ds_e.variables['tp'], idx_e_2018, w_era5, scale_factor=24000.0)
        s_era5 = pd.Series(era5_arr, index=dates_2018)

        # Lecture IMERG depuis les tables existantes
        df_im = pd.read_csv(binfo['csv_imerg'])
        if 'year' in df_im.columns:
            df_im = df_im[df_im['year'] == args.year].reset_index(drop=True)
        df_im['date'] = pd.to_datetime(df_im['date'])
        s_imerg = df_im.set_index('date')['precip_mm_d']
        s_imerg = s_imerg.reindex(dates_2018).fillna(0.0)

        basin_data[code] = {
            'info': binfo,
            'area_km2': cat['area_km2'],
            'imerg': s_imerg,
            'mswep': s_mswep,
            'era5': s_era5
        }

        # Ajout au registre journalier
        for dt in dates_2018:
            p_im = float(s_imerg.loc[dt])
            p_ms = float(s_mswep.loc[dt])
            p_er = float(s_era5.loc[dt])
            daily_records.append({
                'date': dt.strftime('%Y-%m-%d'),
                'day_of_year': int(dt.dayofyear),
                'basin_id': code,
                'basin_name': binfo['name'],
                'area_km2': round(cat['area_km2'], 2),
                'precip_imerg_mm_d': round(p_im, 4),
                'precip_mswep_mm_d': round(p_ms, 4),
                'precip_era5_mm_d': round(p_er, 4),
                'diff_imerg_mswep_mm_d': round(p_im - p_ms, 4),
                'diff_imerg_era5_mm_d': round(p_im - p_er, 4)
            })

    ds_m.close()
    ds_e.close()

    # 4. Enregistrement du CSV journalier 2018
    df_daily = pd.DataFrame(daily_records)
    csv_daily_path = os.path.join(args.out_tables_dir, "daily_precip_comparison_2018.csv")
    df_daily.to_csv(csv_daily_path, index=False)
    print(f"\n[OK] CSV journalier enregistre : {csv_daily_path} ({len(df_daily)} lignes)")

    # 5. Calcul de la synthese annuelle, mensuelle et evenementielle
    summary_rows = []

    for code, bdata in basin_data.items():
        name = bdata['info']['name']
        area_km2 = bdata['area_km2']
        im_s = bdata['imerg']
        ms_s = bdata['mswep']
        er_s = bdata['era5']

        # A. Annuel 2018
        tot_im = float(im_s.sum())
        tot_ms = float(ms_s.sum())
        tot_er = float(er_s.sum())
        diff_ms = tot_im - tot_ms
        diff_er = tot_im - tot_er
        rel_ms = (diff_ms / tot_ms * 100.0) if tot_ms > 0 else np.nan
        rel_er = (diff_er / tot_er * 100.0) if tot_er > 0 else np.nan
        corr_ms = float(im_s.corr(ms_s))
        corr_er = float(im_s.corr(er_s))
        dt_peak_im = im_s.idxmax()
        peak_im = float(im_s.max())
        dt_peak_ms = ms_s.idxmax()
        peak_ms = float(ms_s.max())
        dt_peak_er = er_s.idxmax()
        peak_er = float(er_s.max())

        summary_rows.append({
            'scale': 'annual',
            'basin_id': code,
            'basin_name': name,
            'area_km2': round(area_km2, 2),
            'period': '2018_annual',
            'start_date': '2018-01-01',
            'end_date': '2018-12-31',
            'cumul_imerg_mm': round(tot_im, 2),
            'cumul_mswep_mm': round(tot_ms, 2),
            'cumul_era5_mm': round(tot_er, 2),
            'diff_imerg_mswep_mm': round(diff_ms, 2),
            'rel_diff_mswep_pct': round(rel_ms, 2),
            'diff_imerg_era5_mm': round(diff_er, 2),
            'rel_diff_era5_pct': round(rel_er, 2),
            'corr_imerg_mswep': round(corr_ms, 3),
            'corr_imerg_era5': round(corr_er, 3),
            'peak_imerg_mm_d': round(peak_im, 2),
            'date_peak_imerg': dt_peak_im.strftime('%Y-%m-%d'),
            'peak_mswep_mm_d': round(peak_ms, 2),
            'date_peak_mswep': dt_peak_ms.strftime('%Y-%m-%d'),
            'lag_peak_mswep_d': int((dt_peak_im - dt_peak_ms).days),
            'peak_era5_mm_d': round(peak_er, 2),
            'date_peak_era5': dt_peak_er.strftime('%Y-%m-%d'),
            'lag_peak_era5_d': int((dt_peak_im - dt_peak_er).days)
        })

        # B. Mensuel (12 mois)
        for m in range(1, 13):
            sub_im = im_s[im_s.index.month == m]
            sub_ms = ms_s[ms_s.index.month == m]
            sub_er = er_s[er_s.index.month == m]

            m_im = float(sub_im.sum())
            m_ms = float(sub_ms.sum())
            m_er = float(sub_er.sum())
            m_diff_ms = m_im - m_ms
            m_diff_er = m_im - m_er
            m_rel_ms = (m_diff_ms / m_ms * 100.0) if m_ms > 0 else np.nan
            m_rel_er = (m_diff_er / m_er * 100.0) if m_er > 0 else np.nan
            m_corr_ms = float(sub_im.corr(sub_ms)) if sub_im.std() > 0 and sub_ms.std() > 0 else np.nan
            m_corr_er = float(sub_im.corr(sub_er)) if sub_im.std() > 0 and sub_er.std() > 0 else np.nan

            p_im_max = float(sub_im.max())
            dt_im_max = sub_im.idxmax()
            p_ms_max = float(sub_ms.max())
            dt_ms_max = sub_ms.idxmax()
            p_er_max = float(sub_er.max())
            dt_er_max = sub_er.idxmax()

            summary_rows.append({
                'scale': 'monthly',
                'basin_id': code,
                'basin_name': name,
                'area_km2': round(area_km2, 2),
                'period': f'2018-{m:02d}',
                'start_date': f'2018-{m:02d}-01',
                'end_date': f"2018-{m:02d}-{sub_im.index[-1].day:02d}",
                'cumul_imerg_mm': round(m_im, 2),
                'cumul_mswep_mm': round(m_ms, 2),
                'cumul_era5_mm': round(m_er, 2),
                'diff_imerg_mswep_mm': round(m_diff_ms, 2),
                'rel_diff_mswep_pct': round(m_rel_ms, 2),
                'diff_imerg_era5_mm': round(m_diff_er, 2),
                'rel_diff_era5_pct': round(m_rel_er, 2),
                'corr_imerg_mswep': round(m_corr_ms, 3) if not np.isnan(m_corr_ms) else np.nan,
                'corr_imerg_era5': round(m_corr_er, 3) if not np.isnan(m_corr_er) else np.nan,
                'peak_imerg_mm_d': round(p_im_max, 2),
                'date_peak_imerg': dt_im_max.strftime('%Y-%m-%d'),
                'peak_mswep_mm_d': round(p_ms_max, 2),
                'date_peak_mswep': dt_ms_max.strftime('%Y-%m-%d'),
                'lag_peak_mswep_d': int((dt_im_max - dt_ms_max).days),
                'peak_era5_mm_d': round(p_er_max, 2),
                'date_peak_era5': dt_er_max.strftime('%Y-%m-%d'),
                'lag_peak_era5_d': int((dt_im_max - dt_er_max).days)
            })

        # C. Evenements cibles (4 evenements)
        for ev in EVENTS_CONFIG:
            ev_im = im_s.loc[ev['start']:ev['end']]
            ev_ms = ms_s.loc[ev['start']:ev['end']]
            ev_er = er_s.loc[ev['start']:ev['end']]

            c_im = float(ev_im.sum())
            c_ms = float(ev_ms.sum())
            c_er = float(ev_er.sum())
            c_diff_ms = c_im - c_ms
            c_diff_er = c_im - c_er
            c_rel_ms = (c_diff_ms / c_ms * 100.0) if c_ms > 0 else np.nan
            c_rel_er = (c_diff_er / c_er * 100.0) if c_er > 0 else np.nan
            c_corr_ms = float(ev_im.corr(ev_ms)) if ev_im.std() > 0 and ev_ms.std() > 0 else np.nan
            c_corr_er = float(ev_im.corr(ev_er)) if ev_im.std() > 0 and ev_er.std() > 0 else np.nan

            pk_im = float(ev_im.max())
            dt_pk_im = ev_im.idxmax()
            pk_ms = float(ev_ms.max())
            dt_pk_ms = ev_ms.idxmax()
            pk_er = float(ev_er.max())
            dt_pk_er = ev_er.idxmax()

            summary_rows.append({
                'scale': 'event',
                'basin_id': code,
                'basin_name': name,
                'area_km2': round(area_km2, 2),
                'period': ev['id'],
                'start_date': ev['start'],
                'end_date': ev['end'],
                'cumul_imerg_mm': round(c_im, 2),
                'cumul_mswep_mm': round(c_ms, 2),
                'cumul_era5_mm': round(c_er, 2),
                'diff_imerg_mswep_mm': round(c_diff_ms, 2),
                'rel_diff_mswep_pct': round(c_rel_ms, 2),
                'diff_imerg_era5_mm': round(c_diff_er, 2),
                'rel_diff_era5_pct': round(c_rel_er, 2),
                'corr_imerg_mswep': round(c_corr_ms, 3) if not np.isnan(c_corr_ms) else np.nan,
                'corr_imerg_era5': round(c_corr_er, 3) if not np.isnan(c_corr_er) else np.nan,
                'peak_imerg_mm_d': round(pk_im, 2),
                'date_peak_imerg': dt_pk_im.strftime('%Y-%m-%d'),
                'peak_mswep_mm_d': round(pk_ms, 2),
                'date_peak_mswep': dt_pk_ms.strftime('%Y-%m-%d'),
                'lag_peak_mswep_d': int((dt_pk_im - dt_pk_ms).days),
                'peak_era5_mm_d': round(pk_er, 2),
                'date_peak_era5': dt_pk_er.strftime('%Y-%m-%d'),
                'lag_peak_era5_d': int((dt_pk_im - dt_pk_er).days)
            })

    df_summary = pd.DataFrame(summary_rows)
    csv_summary_path = os.path.join(args.out_tables_dir, "summary_precip_comparison_2018.csv")
    df_summary.to_csv(csv_summary_path, index=False)
    print(f"[OK] CSV de synthese enregistre : {csv_summary_path} ({len(df_summary)} lignes)")

    # 6. Production de la figure comparative multi-panneaux
    print("\nGeneration de la figure comparative multi-panneaux (3 bassins x 4 evenements)...")
    plt.rcParams.update({
        'font.sans-serif': 'DejaVu Sans',
        'font.family': 'sans-serif',
        'font.size': 9,
        'axes.labelsize': 9.5,
        'axes.titlesize': 10,
        'xtick.labelsize': 8.5,
        'ytick.labelsize': 8.5,
        'legend.fontsize': 8,
        'figure.titlesize': 12,
        'axes.grid': True,
        'grid.alpha': 0.35,
        'grid.linestyle': '--'
    })

    fig, axes = plt.subplots(3, 4, figsize=(18, 10.5), sharey='row')
    fig.subplots_adjust(top=0.91, bottom=0.08, left=0.06, right=0.97, hspace=0.32, wspace=0.18)

    c_imerg = '#08519c'   # Bleu soutenu
    c_mswep = '#d94701'   # Orange sombre / corail
    c_era5  = '#238b45'   # Vert foret

    basin_order = ['b_l_chafia', 'b_s_jabeur', 'dar_el_hamra']

    for row_idx, b_code in enumerate(basin_order):
        bdata = basin_data[b_code]
        bname = bdata['info']['name']
        b_area = bdata['area_km2']
        
        # Trouver le maximum absolu pour cette ligne parmi tous les evenements et produits
        row_max = 0.0
        for ev in EVENTS_CONFIG:
            d_s = (pd.to_datetime(ev['start']) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            d_e = (pd.to_datetime(ev['end']) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            m_val = max(bdata['imerg'].loc[d_s:d_e].max(),
                        bdata['mswep'].loc[d_s:d_e].max(),
                        bdata['era5'].loc[d_s:d_e].max())
            if m_val > row_max:
                row_max = m_val
        y_top = row_max * 1.25
        
        for col_idx, ev in enumerate(EVENTS_CONFIG):
            ax = axes[row_idx, col_idx]
            
            # Sous-series de l'evenement
            # On elargit de 1 jour avant et apres pour bien voir l'amorce et la decrue
            d_start_plot = (pd.to_datetime(ev['start']) - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            d_end_plot = (pd.to_datetime(ev['end']) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')
            
            sub_im = bdata['imerg'].loc[d_start_plot:d_end_plot]
            sub_ms = bdata['mswep'].loc[d_start_plot:d_end_plot]
            sub_er = bdata['era5'].loc[d_start_plot:d_end_plot]
            
            # Traces de courbes
            ax.plot(sub_im.index.to_pydatetime(), sub_im.values, color=c_imerg, linewidth=2.0, marker='o', markersize=4.5,
                    label='IMERG (Noah-MP)', zorder=4)
            ax.plot(sub_ms.index.to_pydatetime(), sub_ms.values, color=c_mswep, linewidth=1.7, marker='s', markersize=4.0,
                    linestyle='--', label='MSWEP v2.8', zorder=3)
            ax.plot(sub_er.index.to_pydatetime(), sub_er.values, color=c_era5, linewidth=1.7, marker='^', markersize=4.0,
                    linestyle='-.', label='ERA5', zorder=2)
            
            # Mise en evidence de la fenetre officielle de l'evenement
            ax.axvspan(pd.to_datetime(ev['start']), pd.to_datetime(ev['end']), color='#e0e0e0', alpha=0.35, zorder=1)
            
            # Cumuls sur la fenetre exacte
            cum_im = bdata['imerg'].loc[ev['start']:ev['end']].sum()
            cum_ms = bdata['mswep'].loc[ev['start']:ev['end']].sum()
            cum_er = bdata['era5'].loc[ev['start']:ev['end']].sum()
            
            # Boite d'annotation des cumuls
            txt_box = f"Cumuls :\nIMERG: {cum_im:.1f} mm\nMSWEP: {cum_ms:.1f} mm\nERA5  : {cum_er:.1f} mm"
            ax.text(0.96, 0.94, txt_box, transform=ax.transAxes, verticalalignment='top', horizontalalignment='right',
                    fontsize=7.8, family='monospace', bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.88, edgecolor='#cccccc'))
            
            # Format des axes temporels
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=1 if (pd.to_datetime(ev['end']) - pd.to_datetime(ev['start'])).days <= 6 else 2))
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, ha='right')
            ax.set_ylim(bottom=0, top=y_top)
            
            # Titre de colonne en haut
            if row_idx == 0:
                ax.set_title(ev['short_title'], fontweight='bold', pad=10)
            
            # Label d'ordonnee pour la premiere colonne
            if col_idx == 0:
                ax.set_ylabel(f"{bname}\n({b_area:.0f} km²)\nPrécip. (mm/j)", fontweight='bold')
                
            # Legende seulement sur le panneau superieur gauche
            if row_idx == 0 and col_idx == 0:
                ax.legend(loc='upper left', framealpha=0.9, edgecolor='#cccccc')

    fig.suptitle("Intercomparaison des événements pluvieux majeurs de 2018 : Forçage IMERG (Noah-MP) vs MSWEP v2 vs ERA5\n"
                 "Évaluation de l'hypothèse de sous-estimation du forçage de précipitation",
                 fontweight='bold', y=0.98)

    fig_png = os.path.join(args.out_figs_dir, "events_2018_precip_intercomparison.png")
    fig_pdf = os.path.join(args.out_figs_dir, "events_2018_precip_intercomparison.pdf")
    plt.savefig(fig_png, dpi=300)
    plt.savefig(fig_pdf)
    plt.close()
    print(f"[OK] Figure PNG sauvegardee : {fig_png}")
    print(f"[OK] Figure PDF sauvegardee : {fig_pdf}")

    # Copie vers l'espace d'artefacts pour affichage UI
    if os.path.exists(args.artifact_dir):
        art_png = os.path.join(args.artifact_dir, "events_2018_precip_intercomparison.png")
        shutil.copy2(fig_png, art_png)
        print(f"[OK] Copie vers artefacts : {art_png}")

    print("\nSynthese comparative des cumuls annuels 2018 :")
    for code in basin_order:
        bdata = basin_data[code]
        im_tot = bdata['imerg'].sum()
        ms_tot = bdata['mswep'].sum()
        er_tot = bdata['era5'].sum()
        print(f"  {bdata['info']['name']:<15} : IMERG = {im_tot:6.1f} mm | MSWEP = {ms_tot:6.1f} mm (écart {im_tot-ms_tot:+5.1f} mm, {(im_tot-ms_tot)/ms_tot*100:+.1f}%) | ERA5 = {er_tot:6.1f} mm (écart {im_tot-er_tot:+5.1f} mm, {(im_tot-er_tot)/er_tot*100:+.1f}%)")

if __name__ == '__main__':
    main()
