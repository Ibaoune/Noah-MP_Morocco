#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_opl_hydrology_2018.py
Évaluation scientifique et sensibilité hydrologique des formulations Noah-MP 4.0.1
(SIMGM, SIMTOP, Schaake96, BATS) routées avec HyMAP-2 (linres=0) sur l'année 2018.

Stations cibles :
  - Lalla Chafia (Bouregreg, maille exutoire row=75, col=71, aire D8 = 3 333.35 km²)
  - Sidi Jabeur (Grou/Bouregreg, maille exutoire row=71, col=71, aire D8 = 3 130.55 km²)
"""

import os
import sys
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = f"{BASE_DIR}/experiments/NorthMor/opl_hydrology_sensitivity"
ROUTING_DIR = f"{SENS_DIR}/routing"
POSTPROC_DIR = f"{SENS_DIR}/postproc"
LDT_PATH = f"{BASE_DIR}/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"
OBS_CSV = f"{BASE_DIR}/data/streamflow_clean/obs_daily.csv"
PAIRING_CSV = f"{BASE_DIR}/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv"
ARTIFACT_DIR = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/f3772236-acd2-402d-bb10-a9a2613cf75f"

SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM (Réf)", "#1f77b4"),
    ("OL_R2_SIMTOP", "SIMTOP", "#ff7f0e"),
    ("OL_R3_SCHAAKE96", "Schaake96", "#2ca02c"),
    ("OL_R4_BATS", "BATS", "#9467bd")
]

STATIONS = {
    'b_l_chafia': {
        'name': 'Lalla Chafia',
        'basin': 'Bouregreg',
        'river': 'Bouregreg',
        'cell': (75, 71),
        'area_hymap_d8_km2': 3333.35,
        'area_drain_ldt_km2': 3341.60,
        'area_official_abh_km2': np.nan  # Non renseignée dans hymap_stations_pairing.csv
    },
    'b_s_jabeur': {
        'name': 'Sidi Jabeur',
        'basin': 'Bouregreg',
        'river': 'Grou',
        'cell': (71, 71),
        'area_hymap_d8_km2': 3130.55,
        'area_drain_ldt_km2': 3138.52,
        'area_official_abh_km2': np.nan  # Non renseignée dans hymap_stations_pairing.csv
    }
}

HISTORICAL_EVENTS = [
    {
        'id': 'ev1_mar',
        'name': 'Mars (05–09 mars)',
        'short': '05–09 Mar',
        'start': '2018-03-05',
        'end': '2018-03-09',
        'n_days': 5,
        'type': 'event'
    },
    {
        'id': 'ev2_apr',
        'name': 'Avril (23–27 avril)',
        'short': '23–27 Avr',
        'start': '2018-04-23',
        'end': '2018-04-27',
        'n_days': 5,
        'type': 'event'
    },
    {
        'id': 'ev3_nov_early',
        'name': 'Fin Oct – Début Nov (28 oct – 03 nov)',
        'short': '28 Oct – 03 Nov',
        'start': '2018-10-28',
        'end': '2018-11-03',
        'n_days': 7,
        'type': 'event'
    },
    {
        'id': 'ev4_nov_late',
        'name': 'Mi-Fin Novembre (18–25 nov)',
        'short': '18–25 Nov',
        'start': '2018-11-18',
        'end': '2018-11-25',
        'n_days': 8,
        'type': 'event'
    },
    {
        'id': 'm_mar',
        'name': 'Mois de Mars (01–31 mars)',
        'short': 'Mois Mars',
        'start': '2018-03-01',
        'end': '2018-03-31',
        'n_days': 31,
        'type': 'month'
    },
    {
        'id': 'm_apr',
        'name': 'Mois d\'Avril (01–30 avril)',
        'short': 'Mois Avril',
        'start': '2018-04-01',
        'end': '2018-04-30',
        'n_days': 30,
        'type': 'month'
    },
    {
        'id': 'm_nov',
        'name': 'Mois de Novembre (01–30 nov)',
        'short': 'Mois Nov',
        'start': '2018-11-01',
        'end': '2018-11-30',
        'n_days': 30,
        'type': 'month'
    }
]

def calc_kge(sim, obs):
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    std_s, std_o = np.std(s), np.std(o)
    mean_s, mean_o = np.mean(s), np.mean(o)
    if std_o == 0 or mean_o == 0:
        return np.nan
    r = np.corrcoef(s, o)[0, 1]
    alpha = std_s / std_o
    beta = mean_s / mean_o
    return 1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)

def calc_nse(sim, obs):
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    denom = np.sum((o - np.mean(o))**2)
    if denom == 0:
        return np.nan
    return 1.0 - (np.sum((s - o)**2) / denom)

def calc_pbias(sim, obs):
    valid = (~np.isnan(sim)) & (~np.isnan(obs))
    if np.sum(valid) < 5:
        return np.nan
    s, o = sim[valid], obs[valid]
    sum_o = np.sum(o)
    if sum_o == 0:
        return np.nan
    return 100.0 * np.sum(s - o) / sum_o

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

def load_observations():
    print("[1/5] Chargement des observations journalières ABH...")
    df_obs = pd.read_csv(OBS_CSV)
    df_obs['date'] = pd.to_datetime(df_obs['date'])
    df_obs['q_m3s'] = pd.to_numeric(df_obs['q_m3s'], errors='coerce')
    mask = (df_obs['date'] >= '2018-01-01') & (df_obs['date'] <= '2018-12-31')
    df_2018 = df_obs.loc[mask].copy()
    df_2018.loc[df_2018['q_m3s'] < 0, 'q_m3s'] = np.nan
    df_2018['date_str'] = df_2018['date'].dt.strftime('%Y-%m-%d')
    piv = df_2018.pivot(index='date_str', columns='station_id', values='q_m3s')
    return piv

def load_simulated_streamflows():
    print("[2/5] Chargement des débits simulés HyMAP-2 (2018)...")
    sims = {}
    for exp_id, label, color in SCHEMES:
        csv_path = f"{ROUTING_DIR}/outputs/{exp_id}/streamflow_daily_stations.csv"
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Fichier de débit extrait introuvable : {csv_path}")
        df = pd.read_csv(csv_path)
        df['date_str'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        mask = (df['date_str'] >= '2018-01-01') & (df['date_str'] <= '2018-12-31')
        sims[exp_id] = df.loc[mask].set_index('date_str')
    return sims

def extract_catchment_fluxes_corrected():
    print("[3/5] Extraction rigoureuse des flux amont (P, Qs, Qsb) pour 2018...")
    dates_2018 = [datetime.date(2018, 1, 1) + datetime.timedelta(days=i) for i in range(365)]
    
    # Pre-calcul des masques de bassin
    st_weights = {}
    st_areas_km2 = {}
    for sid, sinfo in STATIONS.items():
        vis, area_grid = get_catchment_cells(LDT_PATH, sinfo['cell'][0], sinfo['cell'][1])
        w = np.zeros_like(area_grid)
        tot_area = sum(area_grid[r, c] for r, c in vis)
        for r, c in vis:
            w[r, c] = area_grid[r, c] / tot_area
        st_weights[sid] = w
        st_areas_km2[sid] = tot_area / 1e6

    records = []
    daily_p_check = {exp_id: {sid: [] for sid in STATIONS} for exp_id, _, _ in SCHEMES}

    for exp_id, label, color in SCHEMES:
        noah_dir = f"{SENS_DIR}/experiments/{exp_id}/output"
        remap_dir = f"{SENS_DIR}/routing/runs/remap_180x120/{exp_id}/SURFACEMODEL"
        
        for d in dates_2018:
            file_dt = d + datetime.timedelta(days=1)
            # CORRECTION CRITIQUE DU CHEMIN NOAH-MP :
            # Le dossier mensuel est le mois de la date d simulée (ex: 2018-01 pour le 31 janv.)
            m_folder = d.strftime('%Y-%m')
            ym = file_dt.strftime('%Y%m')
            fname = f"LIS_HIST_{file_dt.strftime('%Y%m%d0000')}.d01.nc"
            
            noah_f = f"{noah_dir}/{m_folder}/SURFACEMODEL/{ym}/{fname}"
            remap_f = f"{remap_dir}/{ym}/{fname}"
            
            if not os.path.exists(noah_f):
                raise FileNotFoundError(f"[{exp_id}] Fichier Noah-MP manquant pour le jour {d}: {noah_f}")
            if not os.path.exists(remap_f):
                raise FileNotFoundError(f"[{exp_id}] Fichier remappé manquant pour le jour {d}: {remap_f}")
                
            # Lecture P depuis fichier Noah-MP (Rainf_f_tavg)
            with nc.Dataset(noah_f, 'r') as ds:
                p_arr = ds['Rainf_f_tavg'][:]
                if p_arr.ndim == 3: p_arr = p_arr[0]
                p_remap = 0.25 * (p_arr[:-1, :-1] + p_arr[:-1, 1:] + p_arr[1:, :-1] + p_arr[1:, 1:])
                
            # Lecture Qs et Qsb depuis fichier remappé
            with nc.Dataset(remap_f, 'r') as ds:
                qs_arr = ds['Qs_tavg'][:]
                qsb_arr = ds['Qsb_tavg'][:]
                if qs_arr.ndim == 3: qs_arr = qs_arr[0]
                if qsb_arr.ndim == 3: qsb_arr = qsb_arr[0]
                
            for sid in STATIONS:
                w = st_weights[sid]
                p_val = float(np.sum(p_remap * w) * 86400.0)
                qs_val = float(np.sum(qs_arr * w) * 86400.0)
                qsb_val = float(np.sum(qsb_arr * w) * 86400.0)
                
                daily_p_check[exp_id][sid].append(p_val)
                records.append({
                    'station_id': sid,
                    'station_name': STATIONS[sid]['name'],
                    'basin': STATIONS[sid]['basin'],
                    'area_d8_km2': st_areas_km2[sid],
                    'experiment': exp_id,
                    'formulation': label,
                    'date': d.strftime('%Y-%m-%d'),
                    'P_mm_day': p_val,
                    'Qs_mm_day': qs_val,
                    'Qsb_mm_day': qsb_val,
                    'Qin_mm_day': qs_val + qsb_val
                })

    df_fluxes = pd.DataFrame(records)
    csv_fluxes = f"{POSTPROC_DIR}/tables/catchment_fluxes_daily_2018.csv"
    df_fluxes.to_csv(csv_fluxes, index=False)
    print(f"[OK] Flux amont journaliers enregistrés : {csv_fluxes}")

    # Vérification formelle que P est rigoureusement identique entre les 4 schémas
    for sid in STATIONS:
        p_simgm = np.array(daily_p_check['OL_R1_SIMGM'][sid])
        for exp_id, label, _ in SCHEMES[1:]:
            diff = np.max(np.abs(p_simgm - np.array(daily_p_check[exp_id][sid])))
            if diff > 1e-5:
                raise ValueError(f"Incohérence de précipitation détectée entre SIMGM et {label} sur {sid}: diff={diff}")
        tot_p = np.sum(p_simgm)
        print(f"  -> Précipitation annuelle 2018 vérifiée pour {STATIONS[sid]['name']} : {tot_p:.2f} mm (Strictement identique entre les 4 schémas)")

    return df_fluxes

def compute_all_metrics_and_events(df_obs, sims, df_fluxes):
    print("[4/5] Calcul des métriques globales, mensuelles et des événements de crue...")
    
    # 1. TABLE DES ÉVÉNEMENTS HISTORIQUES ET VOLUMES MENSUELS
    event_rows = []
    summer_range = ("2018-06-01", "2018-09-30")

    for sid, sinfo in STATIONS.items():
        s_obs = df_obs[sid].copy() if sid in df_obs.columns else pd.Series(np.nan, index=df_obs.index)

        for ev in HISTORICAL_EVENTS:
            ev_dates = pd.date_range(ev['start'], ev['end']).strftime("%Y-%m-%d")
            sub_o = s_obs.reindex(ev_dates)
            v_mask_o = (~sub_o.isna()) & (sub_o >= 0)
            
            peak_o = float(sub_o[v_mask_o].max()) if v_mask_o.sum() > 0 else np.nan
            date_peak_o = str(sub_o[v_mask_o].idxmax()) if v_mask_o.sum() > 0 else "N/A"
            vol_o_mm3 = float(sub_o[v_mask_o].sum()) * 0.0864 if v_mask_o.sum() > 0 else np.nan
            # Lame d'eau écoulée obs (mm) = Vol(m3) / Aire(m2) * 1000 = Vol(Mm3)*1e6 / (Aire_km2*1e6) * 1000 = Vol_Mm3 / Aire_km2 * 1000
            lame_o_mm = (vol_o_mm3 * 1e6) / (sinfo['area_hymap_d8_km2'] * 1e6) * 1000.0 if v_mask_o.sum() > 0 else np.nan

            for exp_id, label, color in SCHEMES:
                s_sim = sims[exp_id][sid].copy()
                sub_s = s_sim.reindex(ev_dates)
                v_mask_s = (~sub_s.isna()) & (sub_s >= 0)
                
                peak_s = float(sub_s[v_mask_s].max()) if v_mask_s.sum() > 0 else np.nan
                date_peak_s = str(sub_s[v_mask_s].idxmax()) if v_mask_s.sum() > 0 else "N/A"
                vol_s_mm3 = float(sub_s[v_mask_s].sum()) * 0.0864 if v_mask_s.sum() > 0 else np.nan
                lame_s_mm = (vol_s_mm3 * 1e6) / (sinfo['area_hymap_d8_km2'] * 1e6) * 1000.0 if v_mask_s.sum() > 0 else np.nan

                peak_bias = 100.0 * (peak_s - peak_o) / peak_o if (peak_o and not np.isnan(peak_o)) else np.nan
                vol_bias = 100.0 * (vol_s_mm3 - vol_o_mm3) / vol_o_mm3 if (vol_o_mm3 and not np.isnan(vol_o_mm3)) else np.nan

                # Flux internes précip et ruissellement pendant l'événement
                sub_flux = df_fluxes[(df_fluxes['station_id'] == sid) & (df_fluxes['experiment'] == exp_id) & (df_fluxes['date'].isin(ev_dates))]
                p_ev_cum = float(sub_flux['P_mm_day'].sum())
                qs_ev_cum = float(sub_flux['Qs_mm_day'].sum())
                qsb_ev_cum = float(sub_flux['Qsb_mm_day'].sum())
                qin_ev_cum = float(sub_flux['Qin_mm_day'].sum())

                event_rows.append({
                    'Type': 'Événement de crue' if ev['type'] == 'event' else 'Volume mensuel',
                    'Fenêtre': ev['name'],
                    'Dates': f"{ev['start']} au {ev['end']}",
                    'Nb_Jours': ev['n_days'],
                    'Station': sinfo['name'],
                    'Station_ID': sid,
                    'Superficie_D8_km2': sinfo['area_hymap_d8_km2'],
                    'Formulation': label,
                    'Expérience': exp_id,
                    'P_cum_mm': round(p_ev_cum, 1),
                    'Qs_cum_mm': round(qs_ev_cum, 2),
                    'Qsb_cum_mm': round(q_sb_cum := qsb_ev_cum, 2),
                    'Qin_cum_mm': round(qin_ev_cum, 2),
                    'Ratio_Qs_sur_P_%': round(100.0 * qs_ev_cum / p_ev_cum, 1) if p_ev_cum > 0 else 0.0,
                    'Q_obs_pic_m3s': round(peak_o, 1) if not np.isnan(peak_o) else np.nan,
                    'Date_pic_obs': date_peak_o,
                    'Q_sim_pic_m3s': round(peak_s, 1),
                    'Date_pic_sim': date_peak_s,
                    'Biais_Pic_%': round(peak_bias, 1) if not np.isnan(peak_bias) else np.nan,
                    'Vol_obs_Mm3': round(vol_o_mm3, 1) if not np.isnan(vol_o_mm3) else np.nan,
                    'Vol_sim_Mm3': round(vol_s_mm3, 1),
                    'Biais_Vol_%': round(vol_bias, 1) if not np.isnan(vol_bias) else np.nan,
                    'Lame_obs_mm': round(lame_o_mm, 1) if not np.isnan(lame_o_mm) else np.nan,
                    'Lame_sim_mm': round(lame_s_mm, 1),
                })

    df_events = pd.DataFrame(event_rows)
    csv_events = f"{POSTPROC_DIR}/tables/table_events_2018_comparison.csv"
    md_events = f"{POSTPROC_DIR}/tables/table_events_2018_comparison.md"
    df_events.to_csv(csv_events, index=False)
    with open(md_events, 'w') as f:
        f.write('| ' + ' | '.join(df_events.columns) + ' |\n')
        f.write('| ' + ' | '.join(['---'] * len(df_events.columns)) + ' |\n')
        for _, row in df_events.iterrows():
            f.write('| ' + ' | '.join(str(val) for val in row) + ' |\n')
    print(f"[OK] Table événementielle exportée : {csv_events}")

    # 2. TABLE DE SYNTHÈSE GLOBALE DES PERFORMANCES 2018
    perf_rows = []
    for sid, sinfo in STATIONS.items():
        s_obs = df_obs[sid].copy()
        
        for exp_id, label, color in SCHEMES:
            s_sim = sims[exp_id][sid].copy()
            valid = (~s_obs.isna()) & (~s_sim.isna()) & (s_obs >= 0)
            n_days = int(valid.sum())
            
            kge = calc_kge(s_sim.values, s_obs.values)
            nse = calc_nse(s_sim.values, s_obs.values)
            pbias = calc_pbias(s_sim.values, s_obs.values)
            r = np.corrcoef(s_sim[valid].values, s_obs[valid].values)[0, 1] if n_days > 5 else np.nan
            mean_obs = float(s_obs[valid].mean())
            mean_sim = float(s_sim[valid].mean())

            # Bilan annuel des flux
            sub_f_ann = df_fluxes[(df_fluxes['station_id'] == sid) & (df_fluxes['experiment'] == exp_id)]
            p_ann = float(sub_f_ann['P_mm_day'].sum())
            qs_ann = float(sub_f_ann['Qs_mm_day'].sum())
            qsb_ann = float(sub_f_ann['Qsb_mm_day'].sum())
            qin_ann = qs_ann + qsb_ann

            # Bilan estival (Juin–Septembre)
            sum_idx = pd.date_range(summer_range[0], summer_range[1]).strftime("%Y-%m-%d")
            sub_o_sum = s_obs.reindex(sum_idx)
            sub_s_sum = s_sim.reindex(sum_idx)
            s_mask_sum = (~sub_o_sum.isna()) & (~sub_s_sum.isna()) & (sub_o_sum >= 0)
            
            q_sum_o = float(sub_o_sum[s_mask_sum].mean())
            q_sum_s = float(sub_s_sum[s_mask_sum].mean())
            q_sum_med_o = float(sub_o_sum[s_mask_sum].median())
            q_sum_med_s = float(sub_s_sum[s_mask_sum].median())
            sum_bias = 100.0 * (q_sum_s - q_sum_o) / q_sum_o if q_sum_o > 0 else np.nan
            
            zero_days_o = int((sub_o_sum[s_mask_sum] <= 0.1).sum())
            zero_days_s = int((sub_s_sum[s_mask_sum] <= 0.1).sum())
            low_days_o = int((sub_o_sum[s_mask_sum] <= 0.5).sum())
            low_days_s = int((sub_s_sum[s_mask_sum] <= 0.5).sum())

            sub_f_sum = sub_f_ann[sub_f_ann['date'].isin(sum_idx)]
            p_sum = float(sub_f_sum['P_mm_day'].sum())
            qs_sum = float(sub_f_sum['Qs_mm_day'].sum())
            qsb_sum = float(sub_f_sum['Qsb_mm_day'].sum())
            qin_sum = qs_sum + qsb_sum

            # Extraire les métriques d'événements clés depuis df_events
            def get_ev_val(ev_name, col):
                m = df_events[(df_events['Station_ID'] == sid) & (df_events['Expérience'] == exp_id) & (df_events['Fenêtre'] == ev_name)]
                return m[col].values[0] if len(m) > 0 else np.nan

            perf_rows.append({
                'Station': sinfo['name'],
                'Station_ID': sid,
                'Superficie_D8_km2': sinfo['area_hymap_d8_km2'],
                'Formulation': label,
                'Expérience': exp_id,
                'Jours_Valides': n_days,
                'NSE_2018': round(nse, 3),
                'KGE_2018': round(kge, 3),
                'PBIAS_2018_%': round(pbias, 1),
                'Pearson_r_2018': round(r, 3),
                'Q_moyen_obs_m3s': round(mean_obs, 2),
                'Q_moyen_sim_m3s': round(mean_sim, 2),
                # Crues événementielles
                'Crue_Mars_Pic_Sim_m3s': get_ev_val('Mars (05–09 mars)', 'Q_sim_pic_m3s'),
                'Crue_Mars_Biais_Pic_%': get_ev_val('Mars (05–09 mars)', 'Biais_Pic_%'),
                'Crue_Mars_Vol_Sim_Mm3': get_ev_val('Mars (05–09 mars)', 'Vol_sim_Mm3'),
                'Crue_Mars_Biais_Vol_%': get_ev_val('Mars (05–09 mars)', 'Biais_Vol_%'),
                'Crue_Avril_Pic_Sim_m3s': get_ev_val('Avril (23–27 avril)', 'Q_sim_pic_m3s'),
                'Crue_Avril_Biais_Pic_%': get_ev_val('Avril (23–27 avril)', 'Biais_Pic_%'),
                'Crue_Avril_Vol_Sim_Mm3': get_ev_val('Avril (23–27 avril)', 'Vol_sim_Mm3'),
                'Crue_Avril_Biais_Vol_%': get_ev_val('Avril (23–27 avril)', 'Biais_Vol_%'),
                'Crue_Nov1_Pic_Sim_m3s': get_ev_val('Fin Oct – Début Nov (28 oct – 03 nov)', 'Q_sim_pic_m3s'),
                'Crue_Nov1_Biais_Pic_%': get_ev_val('Fin Oct – Début Nov (28 oct – 03 nov)', 'Biais_Pic_%'),
                'Crue_Nov1_Vol_Sim_Mm3': get_ev_val('Fin Oct – Début Nov (28 oct – 03 nov)', 'Vol_sim_Mm3'),
                'Crue_Nov1_Biais_Vol_%': get_ev_val('Fin Oct – Début Nov (28 oct – 03 nov)', 'Biais_Vol_%'),
                'Crue_Nov2_Pic_Sim_m3s': get_ev_val('Mi-Fin Novembre (18–25 nov)', 'Q_sim_pic_m3s'),
                'Crue_Nov2_Biais_Pic_%': get_ev_val('Mi-Fin Novembre (18–25 nov)', 'Biais_Pic_%'),
                'Crue_Nov2_Vol_Sim_Mm3': get_ev_val('Mi-Fin Novembre (18–25 nov)', 'Vol_sim_Mm3'),
                'Crue_Nov2_Biais_Vol_%': get_ev_val('Mi-Fin Novembre (18–25 nov)', 'Biais_Vol_%'),
                # Volumes mensuels complets
                'Mois_Mars_Vol_Sim_Mm3': get_ev_val('Mois de Mars (01–31 mars)', 'Vol_sim_Mm3'),
                'Mois_Mars_Biais_Vol_%': get_ev_val('Mois de Mars (01–31 mars)', 'Biais_Vol_%'),
                'Mois_Avril_Vol_Sim_Mm3': get_ev_val('Mois d\'Avril (01–30 avril)', 'Vol_sim_Mm3'),
                'Mois_Avril_Biais_Vol_%': get_ev_val('Mois d\'Avril (01–30 avril)', 'Biais_Vol_%'),
                'Mois_Nov_Vol_Sim_Mm3': get_ev_val('Mois de Novembre (01–30 nov)', 'Vol_sim_Mm3'),
                'Mois_Nov_Biais_Vol_%': get_ev_val('Mois de Novembre (01–30 nov)', 'Biais_Vol_%'),
                # Étiage estival (Juin-Sept)
                'Etiage_Q_moy_obs_m3s': round(q_sum_o, 2),
                'Etiage_Q_moy_sim_m3s': round(q_sum_s, 2),
                'Etiage_Biais_%': round(sum_bias, 1),
                'Etiage_Q_med_obs_m3s': round(q_sum_med_o, 2),
                'Etiage_Q_med_sim_m3s': round(q_sum_med_s, 2),
                'Etiage_Jours_Inf_0.1_obs': zero_days_o,
                'Etiage_Jours_Inf_0.1_sim': zero_days_s,
                'Etiage_Jours_Inf_0.5_obs': low_days_o,
                'Etiage_Jours_Inf_0.5_sim': low_days_s,
                # Contributions Qs / Qsb
                'Annuel_P_mm': round(p_ann, 1),
                'Annuel_Qs_mm': round(qs_ann, 1),
                'Annuel_Qsb_mm': round(qsb_ann, 1),
                'Annuel_Part_Qs_%': round(100.0 * qs_ann / qin_ann, 1),
                'Annuel_Part_Qsb_%': round(100.0 * qsb_ann / qin_ann, 1),
                'Annuel_Coeff_Ecoulement_%': round(100.0 * qin_ann / p_ann, 1),
                'Etiage_P_mm': round(p_sum, 1),
                'Etiage_Qs_mm': round(qs_sum, 2),
                'Etiage_Qsb_mm': round(qsb_sum, 2),
                'Etiage_Part_Qs_%': round(100.0 * qs_sum / qin_sum, 1) if qin_sum > 0 else 0.0,
                'Etiage_Part_Qsb_%': round(100.0 * qsb_sum / qin_sum, 1) if qin_sum > 0 else 0.0
            })

    df_perf = pd.DataFrame(perf_rows)
    csv_perf = f"{POSTPROC_DIR}/tables/table_performance_metrics_2018.csv"
    md_perf = f"{POSTPROC_DIR}/tables/table_performance_metrics_2018.md"
    df_perf.to_csv(csv_perf, index=False)
    with open(md_perf, 'w') as f:
        f.write('| ' + ' | '.join(df_perf.columns) + ' |\n')
        f.write('| ' + ' | '.join(['---'] * len(df_perf.columns)) + ' |\n')
        for _, row in df_perf.iterrows():
            f.write('| ' + ' | '.join(str(val) for val in row) + ' |\n')
    print(f"[OK] Table de synthèse des performances exportée : {csv_perf}")
    return df_events, df_perf

def generate_all_figures(df_obs, sims, df_fluxes):
    print("[5/5] Régénération des 4 figures scientifiques comparatives...")
    os.makedirs(f"{POSTPROC_DIR}/figures", exist_ok=True)
    
    # -------------------------------------------------------------
    # FIGURE 1 : HYDROGRAMMES JOURNALIERS COMPLETS 2018
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
    dates_dt = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in df_obs.index]

    for idx, (sid, sinfo) in enumerate(STATIONS.items()):
        ax = axes[idx]
        obs_vals = df_obs[sid].values if sid in df_obs.columns else np.full(len(dates_dt), np.nan)
        ax.plot(dates_dt, obs_vals, color='black', linewidth=2.0, label='Observations ABH', zorder=5)

        for exp_id, label, color in SCHEMES:
            sim_vals = sims[exp_id].reindex(df_obs.index)[sid].values
            ax.plot(dates_dt, sim_vals, color=color, linewidth=1.3, alpha=0.85, label=label)

        title_str = (f"{sinfo['name']} ({sinfo['river']} — Bassin du {sinfo['basin']}) | "
                     f"Superficie amont HyMAP D8 = {sinfo['area_hymap_d8_km2']:.1f} km²")
        ax.set_title(title_str, fontsize=12.5, fontweight='bold')
        ax.set_ylabel("Débit Q (m³/s)", fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.4)
        ax.legend(loc='upper right', framealpha=0.9, fontsize=10)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))

    plt.xlabel("Date", fontsize=11)
    plt.tight_layout()
    fig1_png = f"{POSTPROC_DIR}/figures/fig1_hydrographs_2018_lalla_chafia_sidi_jabeur.png"
    fig1_pdf = f"{POSTPROC_DIR}/figures/fig1_hydrographs_2018_lalla_chafia_sidi_jabeur.pdf"
    plt.savefig(fig1_png, dpi=300)
    plt.savefig(fig1_pdf)
    plt.close()
    print(f"  -> Figure 1 sauvegardée : {fig1_png}")

    # -------------------------------------------------------------
    # FIGURE 2 : COMPARAISON DES 4 ÉVÉNEMENTS DE CRUE HISTORIQUES
    # -------------------------------------------------------------
    ev_list = [e for e in HISTORICAL_EVENTS if e['type'] == 'event']
    fig, axes = plt.subplots(2, 4, figsize=(20, 9), sharey='row')

    for r_idx, (sid, sinfo) in enumerate(STATIONS.items()):
        for c_idx, ev in enumerate(ev_list):
            ax = axes[r_idx, c_idx]
            ev_dates = [d.strftime("%Y-%m-%d") for d in pd.date_range(ev['start'], ev['end'])]
            ev_dt = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in ev_dates]

            obs_v = df_obs.reindex(ev_dates)[sid].values
            ax.plot(ev_dt, obs_v, color='black', linewidth=2.4, label='Obs ABH', zorder=5)

            for exp_id, label, color in SCHEMES:
                sim_v = sims[exp_id].reindex(ev_dates)[sid].values
                ax.plot(ev_dt, sim_v, color=color, linewidth=1.6, alpha=0.9, label=label)

            if r_idx == 0:
                ax.set_title(f"{ev['name']}", fontsize=11.5, fontweight='bold')
            if c_idx == 0:
                ax.set_ylabel(f"{sinfo['name']}\nQ (m³/s)", fontsize=11, fontweight='bold')
            ax.grid(True, linestyle="--", alpha=0.4)
            ax.xaxis.set_major_locator(mdates.DayLocator(interval=2 if ev['n_days'] <= 5 else 3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
            if r_idx == 0 and c_idx == 3:
                ax.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

    plt.tight_layout()
    fig2_png = f"{POSTPROC_DIR}/figures/fig2_flood_events_2018_comparison.png"
    fig2_pdf = f"{POSTPROC_DIR}/figures/fig2_flood_events_2018_comparison.pdf"
    plt.savefig(fig2_png, dpi=300)
    plt.savefig(fig2_pdf)
    plt.close()
    print(f"  -> Figure 2 sauvegardée : {fig2_png}")

    # -------------------------------------------------------------
    # FIGURE 3 : ÉTIAGE ESTIVAL (JUIN-SEPT) ET COURBES DE DÉBITS CLASSÉS
    # -------------------------------------------------------------
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    summer_dates = [d.strftime("%Y-%m-%d") for d in pd.date_range("2018-06-01", "2018-09-30")]
    summer_dt = [datetime.datetime.strptime(d, "%Y-%m-%d") for d in summer_dates]

    for idx, (sid, sinfo) in enumerate(STATIONS.items()):
        # Hydrogramme estival
        ax1 = axes[idx, 0]
        obs_v = df_obs.reindex(summer_dates)[sid].values
        ax1.plot(summer_dt, obs_v, color='black', linewidth=2.0, label='Obs ABH', zorder=5)

        for exp_id, label, color in SCHEMES:
            sim_v = sims[exp_id].reindex(summer_dates)[sid].values
            ax1.plot(summer_dt, sim_v, color=color, linewidth=1.3, alpha=0.9, label=label)

        ax1.axhline(0.1, color='red', linestyle=':', linewidth=1.2, label='Seuil tarissement (0.1 m³/s)')
        ax1.set_title(f"Hydrogramme Estival 2018 — {sinfo['name']}", fontsize=11.5, fontweight='bold')
        ax1.set_ylabel("Débit Q (m³/s)", fontsize=10.5)
        ax1.grid(True, linestyle="--", alpha=0.4)
        ax1.xaxis.set_major_locator(mdates.MonthLocator())
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        if idx == 0: ax1.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

        # Courbe des débits classés (Flow Duration Curve - FDC)
        ax2 = axes[idx, 1]
        valid_obs = obs_v[~np.isnan(obs_v)]
        obs_sorted = np.sort(valid_obs)[::-1]
        prob_obs = np.linspace(0, 100, len(obs_sorted))
        ax2.plot(prob_obs, obs_sorted, color='black', linewidth=2.2, label='Obs ABH', zorder=5)

        for exp_id, label, color in SCHEMES:
            sim_v = sims[exp_id].reindex(summer_dates)[sid].values
            sim_sorted = np.sort(sim_v)[::-1]
            prob_sim = np.linspace(0, 100, len(sim_sorted))
            ax2.plot(prob_sim, sim_sorted, color=color, linewidth=1.4, alpha=0.9, label=label)

        ax2.axhline(0.1, color='red', linestyle=':', linewidth=1.2)
        ax2.set_title(f"Courbe des Débits Classés Estivaux (FDC) — {sinfo['name']}", fontsize=11.5, fontweight='bold')
        ax2.set_ylabel("Débit Q (m³/s)", fontsize=10.5)
        ax2.set_xlabel("Fréquence au dépassement (%)", fontsize=10.5)
        ax2.set_yscale('log')
        ax2.grid(True, linestyle="--", alpha=0.4, which='both')
        if idx == 0: ax2.legend(loc='upper right', fontsize=8.5, framealpha=0.9)

    plt.tight_layout()
    fig3_png = f"{POSTPROC_DIR}/figures/fig3_summer_low_flows_2018.png"
    fig3_pdf = f"{POSTPROC_DIR}/figures/fig3_summer_low_flows_2018.pdf"
    plt.savefig(fig3_png, dpi=300)
    plt.savefig(fig3_pdf)
    plt.close()
    print(f"  -> Figure 3 sauvegardée : {fig3_png}")

    # -------------------------------------------------------------
    # FIGURE 4 : BILAN MENSUEL DES FLUX AMONT P, Qs, Qsb
    # -------------------------------------------------------------
    df_fluxes['month'] = pd.to_datetime(df_fluxes['date']).dt.to_period('M')
    m_grp = df_fluxes.groupby(['station_id', 'experiment', 'month'])[['P_mm_day', 'Qs_mm_day', 'Qsb_mm_day', 'Qin_mm_day']].sum().reset_index()

    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    for s_idx, (sid, sinfo) in enumerate(STATIONS.items()):
        sub_s = m_grp[m_grp['station_id'] == sid]
        months_str = [str(m) for m in sorted(sub_s['month'].unique())]
        x = np.arange(len(months_str))
        width = 0.2

        # Panel 1: Ruissellement de surface Qs
        ax1 = axes[s_idx, 0]
        for e_idx, (exp_id, label, color) in enumerate(SCHEMES):
            sub_e = sub_s[sub_s['experiment'] == exp_id].set_index('month')
            vals = [sub_e.loc[pd.Period(m, 'M'), 'Qs_mm_day'] if pd.Period(m, 'M') in sub_e.index else 0.0 for m in months_str]
            ax1.bar(x + (e_idx - 1.5)*width, vals, width, label=label, color=color, alpha=0.85)
        ax1.set_title(f"{sinfo['name']} — Ruissellement de Surface Qs (mm/mois)", fontsize=11, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(months_str, rotation=45)
        ax1.set_ylabel("Qs (mm)", fontsize=10)
        ax1.grid(True, linestyle="--", alpha=0.3)
        if s_idx == 0: ax1.legend(loc='upper right', fontsize=8.5)

        # Panel 2: Drainage souterrain Qsb
        ax2 = axes[s_idx, 1]
        for e_idx, (exp_id, label, color) in enumerate(SCHEMES):
            sub_e = sub_s[sub_s['experiment'] == exp_id].set_index('month')
            vals = [sub_e.loc[pd.Period(m, 'M'), 'Qsb_mm_day'] if pd.Period(m, 'M') in sub_e.index else 0.0 for m in months_str]
            ax2.bar(x + (e_idx - 1.5)*width, vals, width, label=label, color=color, alpha=0.85)
        ax2.set_title(f"{sinfo['name']} — Drainage Souterrain Qsb (mm/mois)", fontsize=11, fontweight='bold')
        ax2.set_xticks(x)
        ax2.set_xticklabels(months_str, rotation=45)
        ax2.set_ylabel("Qsb (mm)", fontsize=10)
        ax2.grid(True, linestyle="--", alpha=0.3)
        if s_idx == 0: ax2.legend(loc='upper right', fontsize=8.5)

    plt.tight_layout()
    fig4_png = f"{POSTPROC_DIR}/figures/fig4_monthly_qs_qsb_catchment_averages.png"
    fig4_pdf = f"{POSTPROC_DIR}/figures/fig4_monthly_qs_qsb_catchment_averages.pdf"
    plt.savefig(fig4_png, dpi=300)
    plt.savefig(fig4_pdf)
    plt.close()
    print(f"  -> Figure 4 sauvegardée : {fig4_png}")

    # Copie vers artefacts UI
    for f in [fig1_png, fig2_png, fig3_png, fig4_png]:
        dest = os.path.join(ARTIFACT_DIR, os.path.basename(f))
        import shutil
        shutil.copyfile(f, dest)
    print(f"[OK] Figures copiées vers l'espace d'artefacts : {ARTIFACT_DIR}")

def main():
    print("=" * 80)
    print(" OPL HYDROLOGY SENSITIVITY — POST-TRAITEMENT SCIENTIFIQUE CORRIGÉ (2018)")
    print("=" * 80)

    df_obs = load_observations()
    sims = load_simulated_streamflows()
    df_fluxes = extract_catchment_fluxes_corrected()
    df_events, df_perf = compute_all_metrics_and_events(df_obs, sims, df_fluxes)
    generate_all_figures(df_obs, sims, df_fluxes)
    print("\n[SUCCÈS] Post-traitement et figures régénérés avec succès.")

if __name__ == "__main__":
    main()
