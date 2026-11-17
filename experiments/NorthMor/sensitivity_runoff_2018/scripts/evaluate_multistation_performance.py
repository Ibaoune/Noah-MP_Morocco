#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate_multistation_performance.py
Calcule l'ensemble des métriques hydrologiques multi-stations sur 2018 pour les 4 schémas OPL :
- Métriques journalières (Bouregreg) : NSE, KGE, PBIAS, r, biais des crues, métriques d'étiage.
- Métriques mensuelles (Bouregreg + Sebou) : NSE_m, KGE_m, PBIAS_m, r_m.
- Diagnostic des étiages (Juin-Septembre 122 jours) : jours <=0.1 et <=0.5 m3/s, séquence d'assec max.
- Biais des pics et volumes d'événements.
Sorties :
  - postproc/tables/streamflow_all_stations_2018.csv
  - postproc/tables/table_multistation_metrics_2018.csv
  - postproc/tables/table_multistation_metrics_2018.md
  - postproc/tables/table_multistation_lowflows_2018.csv
  - postproc/tables/table_multistation_floods_2018.csv
"""

import os
import sys
import datetime
import numpy as np
import pandas as pd

REPO_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = os.path.join(REPO_ROOT, "experiments/NorthMor/opl_hydrology_sensitivity")
ROUTING_DIR = os.path.join(SENS_DIR, "routing")
POSTPROC_DIR = os.path.join(SENS_DIR, "postproc")
INVENTORY_CSV = os.path.join(POSTPROC_DIR, "tables/station_inventory_2018.csv")
OBS_DAILY_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/obs_daily.csv")
OBS_MONTHLY_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/obs_monthly.csv")

OUT_STREAMFLOW_CSV = os.path.join(POSTPROC_DIR, "tables/streamflow_all_stations_2018.csv")
OUT_METRICS_CSV = os.path.join(POSTPROC_DIR, "tables/table_multistation_metrics_2018.csv")
OUT_METRICS_MD = os.path.join(POSTPROC_DIR, "tables/table_multistation_metrics_2018.md")
OUT_LOWFLOWS_CSV = os.path.join(POSTPROC_DIR, "tables/table_multistation_lowflows_2018.csv")
OUT_FLOODS_CSV = os.path.join(POSTPROC_DIR, "tables/table_multistation_floods_2018.csv")

SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM (Réf)"),
    ("OL_R2_SIMTOP", "SIMTOP"),
    ("OL_R3_SCHAAKE96", "Schaake96"),
    ("OL_R4_BATS", "BATS")
]

def calc_kge(sim, obs):
    mask = ~np.isnan(sim) & ~np.isnan(obs)
    s = sim[mask]
    o = obs[mask]
    if len(s) < 3 or np.std(o) == 0:
        return np.nan, np.nan, np.nan, np.nan
    r = np.corrcoef(s, o)[0, 1]
    alpha = np.std(s) / np.std(o)
    beta = np.mean(s) / np.mean(o) if np.mean(o) != 0 else np.nan
    kge = 1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)
    return kge, r, alpha, beta

def calc_nse(sim, obs):
    mask = ~np.isnan(sim) & ~np.isnan(obs)
    s = sim[mask]
    o = obs[mask]
    if len(s) < 3 or np.var(o) == 0:
        return np.nan
    return 1.0 - (np.sum((s - o)**2) / np.sum((o - np.mean(o))**2))

def calc_pbias(sim, obs):
    mask = ~np.isnan(sim) & ~np.isnan(obs)
    s = sim[mask]
    o = obs[mask]
    if len(s) == 0 or np.sum(o) == 0:
        return np.nan
    return 100.0 * np.sum(s - o) / np.sum(o)

def max_consecutive_zeros(series, threshold=0.0):
    max_streak = 0
    curr_streak = 0
    for val in series:
        if pd.isna(val):
            curr_streak = 0
        elif val <= threshold:
            curr_streak += 1
            if curr_streak > max_streak:
                max_streak = curr_streak
        else:
            curr_streak = 0
    return max_streak

def main():
    print("[1/5] Chargement inventaire et observations...")
    df_inv = pd.read_csv(INVENTORY_CSV)
    df_ret = df_inv[df_inv['statut_2018'] != 'Exclue'].copy()
    retained_sids = list(df_ret['station_id'])

    # Observations journalières 2018
    df_d = pd.read_csv(OBS_DAILY_CSV)
    df_d['date'] = pd.to_datetime(df_d['date'])
    df_d_2018 = df_d[df_d['date'].dt.year == 2018].copy()
    df_d_2018['date_str'] = df_d_2018['date'].dt.strftime('%Y-%m-%d')

    # Observations mensuelles 2018
    df_m = pd.read_csv(OBS_MONTHLY_CSV)
    df_m_2018 = df_m[df_m['annee'] == 2018].copy()

    # Débits simulés journaliers des 4 schémas
    print("[2/5] Chargement des débits simulés HyMAP-2...")
    sim_dfs = {}
    for exp_id, exp_label in SCHEMES:
        p = os.path.join(ROUTING_DIR, "outputs", exp_id, "streamflow_daily_stations.csv")
        df_sim = pd.read_csv(p)
        df_sim['date_str'] = pd.to_datetime(df_sim['date']).dt.strftime('%Y-%m-%d')
        df_sim_2018 = df_sim[(df_sim['date_str'] >= '2018-01-01') & (df_sim['date_str'] <= '2018-12-31')].copy()
        sim_dfs[exp_id] = df_sim_2018.set_index('date_str')

    # Dates 2018
    dates_2018 = [datetime.date(2018, 1, 1) + datetime.timedelta(days=i) for i in range(365)]
    dates_str = [d.strftime('%Y-%m-%d') for d in dates_2018]

    # Construction du tableau unifié des débits
    print("[3/5] Construction du fichier unifié streamflow_all_stations_2018.csv...")
    records_streamflow = []
    
    # Pour chaque station retenue
    for sid in retained_sids:
        sinfo = df_ret[df_ret['station_id'] == sid].iloc[0]
        pas = sinfo['pas_temps']
        
        # Obs journalières si dispo
        sub_obs_d = df_d_2018[df_d_2018['station_id'] == sid].set_index('date_str') if pas == 'journalier' else None
        # Obs mensuelles si dispo
        sub_obs_m = df_m_2018[df_m_2018['station_id'] == sid].set_index('mois') if pas == 'mensuel' else None

        for d in dates_2018:
            d_str = d.strftime('%Y-%m-%d')
            q_obs = np.nan
            if pas == 'journalier' and sub_obs_d is not None and d_str in sub_obs_d.index:
                val = sub_obs_d.loc[d_str, 'q_m3s']
                if pd.notna(val):
                    q_obs = float(val)

            rec = {
                'date': d_str,
                'annee': d.year,
                'mois': d.month,
                'jour': d.day,
                'station_id': sid,
                'nom': sinfo['nom'],
                'bassin': sinfo['bassin'],
                'sous_bassin': sinfo['sous_bassin'],
                'pas_temps': pas,
                'q_obs_m3s': q_obs
            }
            for exp_id, exp_label in SCHEMES:
                rec[f'q_sim_{exp_id}'] = float(sim_dfs[exp_id].loc[d_str, sid])
            records_streamflow.append(rec)

    df_all_streamflow = pd.DataFrame(records_streamflow)
    os.makedirs(os.path.dirname(OUT_STREAMFLOW_CSV), exist_ok=True)
    df_all_streamflow.to_csv(OUT_STREAMFLOW_CSV, index=False)
    print("Fichier unifié sauvegardé :", OUT_STREAMFLOW_CSV, "(", len(df_all_streamflow), "lignes)")

    # 4. Calcul des métriques multi-stations
    print("[4/5] Calcul des métriques journalières et mensuelles...")
    metrics_records = []
    lowflow_records = []
    
    # Table mensuelle pour Sebou et comparaison mensuelle
    df_all_streamflow['month_dt'] = df_all_streamflow['mois']

    for sid in retained_sids:
        sinfo = df_ret[df_ret['station_id'] == sid].iloc[0]
        sub_st = df_all_streamflow[df_all_streamflow['station_id'] == sid].copy()
        pas = sinfo['pas_temps']
        
        # Agréger mensuel pour les simulations
        monthly_sim = sub_st.groupby('mois')[[f'q_sim_{exp_id}' for exp_id, _ in SCHEMES]].mean()
        
        # Obs mensuelles réelles
        if pas == 'mensuel':
            sub_m = df_m_2018[df_m_2018['station_id'] == sid].set_index('mois')
            obs_m_arr = np.array([sub_m.loc[m, 'q_m3s'] if m in sub_m.index else np.nan for m in range(1, 13)])
        else:
            # Pour Bouregreg, moyenne mensuelle des obs journalières
            obs_m_arr = sub_st.groupby('mois')['q_obs_m3s'].mean().values

        # Référence SIMGM pour les deltas
        nse_ref_d, kge_ref_d = np.nan, np.nan
        nse_ref_m, kge_ref_m = np.nan, np.nan

        # Calculer d'abord SIMGM pour avoir les références
        for exp_id, exp_label in SCHEMES:
            q_sim_daily = sub_st[f'q_sim_{exp_id}'].values
            q_obs_daily = sub_st['q_obs_m3s'].values
            
            # Métriques journalières (si station journalière)
            if pas == 'journalier':
                nse_d = calc_nse(q_sim_daily, q_obs_daily)
                kge_d, r_d, alpha_d, beta_d = calc_kge(q_sim_daily, q_obs_daily)
                pbias_d = calc_pbias(q_sim_daily, q_obs_daily)
            else:
                nse_d, kge_d, r_d, alpha_d, beta_d, pbias_d = np.nan, np.nan, np.nan, np.nan, np.nan, np.nan

            # Métriques mensuelles (pour toutes les stations)
            q_sim_monthly = monthly_sim[f'q_sim_{exp_id}'].values
            nse_m = calc_nse(q_sim_monthly, obs_m_arr)
            kge_m, r_m, alpha_m, beta_m = calc_kge(q_sim_monthly, obs_m_arr)
            pbias_m = calc_pbias(q_sim_monthly, obs_m_arr)

            if exp_id == 'OL_R1_SIMGM':
                nse_ref_d, kge_ref_d = nse_d, kge_d
                nse_ref_m, kge_ref_m = nse_m, kge_m

            # Écarts vs SIMGM
            delta_nse_d = nse_d - nse_ref_d if pd.notna(nse_d) and pd.notna(nse_ref_d) else np.nan
            delta_kge_d = kge_d - kge_ref_d if pd.notna(kge_d) and pd.notna(kge_ref_d) else np.nan
            delta_nse_m = nse_m - nse_ref_m if pd.notna(nse_m) and pd.notna(nse_ref_m) else np.nan
            delta_kge_m = kge_m - kge_ref_m if pd.notna(kge_m) and pd.notna(kge_ref_m) else np.nan

            metrics_records.append({
                'station_id': sid,
                'nom': sinfo['nom'],
                'bassin': sinfo['bassin'],
                'sous_bassin': sinfo['sous_bassin'],
                'statut_2018': sinfo['statut_2018'],
                'pas_temps': pas,
                'aire_d8_km2': sinfo['aire_d8_km2'],
                'experiment': exp_id,
                'formulation': exp_label,
                # Métriques journalières
                'NSE_daily': round(nse_d, 3) if pd.notna(nse_d) else np.nan,
                'KGE_daily': round(kge_d, 3) if pd.notna(kge_d) else np.nan,
                'PBIAS_daily_pct': round(pbias_d, 1) if pd.notna(pbias_d) else np.nan,
                'r_daily': round(r_d, 3) if pd.notna(r_d) else np.nan,
                'delta_NSE_daily': round(delta_nse_d, 3) if pd.notna(delta_nse_d) else np.nan,
                'delta_KGE_daily': round(delta_kge_d, 3) if pd.notna(delta_kge_d) else np.nan,
                # Métriques mensuelles
                'NSE_monthly': round(nse_m, 3) if pd.notna(nse_m) else np.nan,
                'KGE_monthly': round(kge_m, 3) if pd.notna(kge_m) else np.nan,
                'PBIAS_monthly_pct': round(pbias_m, 1) if pd.notna(pbias_m) else np.nan,
                'r_monthly': round(r_m, 3) if pd.notna(r_m) else np.nan,
                'delta_NSE_monthly': round(delta_nse_m, 3) if pd.notna(delta_nse_m) else np.nan,
                'delta_KGE_monthly': round(delta_kge_m, 3) if pd.notna(delta_kge_m) else np.nan,
                # Débits moyens
                'q_mean_obs_m3s': round(float(np.nanmean(obs_m_arr)), 3) if len(obs_m_arr) > 0 else np.nan,
                'q_mean_sim_m3s': round(float(np.mean(q_sim_monthly)), 3),
                'q_max_sim_m3s': round(float(np.max(q_sim_daily)), 2),
                'q_max_obs_m3s': round(float(np.nanmax(q_obs_daily)), 2) if pas == 'journalier' else round(float(np.nanmax(obs_m_arr)), 2)
            })

        # Diagnostic d'étiage (Juin - Septembre 2018 : 122 jours)
        sub_summer = sub_st[(sub_st['mois'] >= 6) & (sub_st['mois'] <= 9)].copy()
        n_days_summer = len(sub_summer)
        q_obs_sum = sub_summer['q_obs_m3s'].values
        
        # Métriques d'étiage observées
        q_obs_sum_valid = q_obs_sum[~np.isnan(q_obs_sum)]
        obs_mean_sum = float(np.mean(q_obs_sum_valid)) if len(q_obs_sum_valid) > 0 else np.nan
        obs_med_sum = float(np.median(q_obs_sum_valid)) if len(q_obs_sum_valid) > 0 else np.nan
        obs_days_le_01 = int(np.sum(q_obs_sum_valid <= 0.1)) if len(q_obs_sum_valid) > 0 else np.nan
        obs_days_le_05 = int(np.sum(q_obs_sum_valid <= 0.5)) if len(q_obs_sum_valid) > 0 else np.nan
        obs_days_zero = int(np.sum(q_obs_sum_valid == 0.0)) if len(q_obs_sum_valid) > 0 else np.nan
        obs_max_dry_spell = max_consecutive_zeros(sub_summer['q_obs_m3s'].values, threshold=0.0) if pas == 'journalier' else np.nan

        for exp_id, exp_label in SCHEMES:
            q_sim_sum = sub_summer[f'q_sim_{exp_id}'].values
            sim_mean_sum = float(np.mean(q_sim_sum))
            sim_med_sum = float(np.median(q_sim_sum))
            sim_days_le_01 = int(np.sum(q_sim_sum <= 0.1))
            sim_days_le_05 = int(np.sum(q_sim_sum <= 0.5))
            sim_days_zero = int(np.sum(q_sim_sum == 0.0))
            sim_max_dry_spell = max_consecutive_zeros(q_sim_sum, threshold=0.0)

            lowflow_records.append({
                'station_id': sid,
                'nom': sinfo['nom'],
                'bassin': sinfo['bassin'],
                'pas_temps': pas,
                'experiment': exp_id,
                'formulation': exp_label,
                'periode': 'Juin–Sept 2018 (122 j)',
                'q_mean_obs_m3s': round(obs_mean_sum, 3) if pd.notna(obs_mean_sum) else np.nan,
                'q_mean_sim_m3s': round(sim_mean_sum, 3),
                'q_median_obs_m3s': round(obs_med_sum, 3) if pd.notna(obs_med_sum) else np.nan,
                'q_median_sim_m3s': round(sim_med_sum, 3),
                'n_days_le_01_obs': obs_days_le_01,
                'n_days_le_01_sim': sim_days_le_01,
                'n_days_le_05_obs': obs_days_le_05,
                'n_days_le_05_sim': sim_days_le_05,
                'n_days_zero_obs': obs_days_zero,
                'n_days_zero_sim': sim_days_zero,
                'max_dry_spell_obs_days': obs_max_dry_spell,
                'max_dry_spell_sim_days': sim_max_dry_spell,
                'biais_q_mean_sum_pct': round((sim_mean_sum - obs_mean_sum) / obs_mean_sum * 100.0, 1) if pd.notna(obs_mean_sum) and obs_mean_sum > 0 else np.nan
            })

    df_metrics = pd.DataFrame(metrics_records)
    df_metrics.to_csv(OUT_METRICS_CSV, index=False)
    print("Table de métriques sauvegardée :", OUT_METRICS_CSV)

    df_lowflow = pd.DataFrame(lowflow_records)
    df_lowflow.to_csv(OUT_LOWFLOWS_CSV, index=False)
    print("Table d'étiage sauvegardée :", OUT_LOWFLOWS_CSV)

    # 5. Diagnostic des crues (événements principaux)
    print("[5/5] Diagnostic des événements de crue...")
    events = [
        {'id': 'mars_2018', 'nom': 'Crue 05–15 mars 2018', 'start': '2018-03-05', 'end': '2018-03-15'},
        {'id': 'avril_2018', 'nom': 'Crue 22–30 avril 2018', 'start': '2018-04-22', 'end': '2018-04-30'},
        {'id': 'nov_2018', 'nom': 'Crue 15–28 nov 2018', 'start': '2018-11-15', 'end': '2018-11-28'}
    ]
    
    flood_records = []
    # Pour les stations journalières
    daily_sids = [sid for sid in retained_sids if df_ret[df_ret['station_id'] == sid].iloc[0]['pas_temps'] == 'journalier']
    
    for ev in events:
        sub_ev = df_all_streamflow[(df_all_streamflow['date'] >= ev['start']) & (df_all_streamflow['date'] <= ev['end'])]
        for sid in daily_sids:
            sub_st_ev = sub_ev[sub_ev['station_id'] == sid]
            q_obs_arr = sub_st_ev['q_obs_m3s'].values
            q_obs_arr_v = q_obs_arr[~np.isnan(q_obs_arr)]
            q_peak_obs = float(np.max(q_obs_arr_v)) if len(q_obs_arr_v) > 0 else np.nan
            vol_obs_hm3 = float(np.sum(q_obs_arr_v) * 86400.0 / 1e6) if len(q_obs_arr_v) > 0 else np.nan

            for exp_id, exp_label in SCHEMES:
                q_sim_arr = sub_st_ev[f'q_sim_{exp_id}'].values
                q_peak_sim = float(np.max(q_sim_arr))
                vol_sim_hm3 = float(np.sum(q_sim_arr) * 86400.0 / 1e6)

                bias_peak_pct = round((q_peak_sim - q_peak_obs) / q_peak_obs * 100.0, 1) if pd.notna(q_peak_obs) and q_peak_obs > 0 else np.nan
                bias_vol_pct = round((vol_sim_hm3 - vol_obs_hm3) / vol_obs_hm3 * 100.0, 1) if pd.notna(vol_obs_hm3) and vol_obs_hm3 > 0 else np.nan

                flood_records.append({
                    'evenement': ev['nom'],
                    'debut': ev['start'],
                    'fin': ev['end'],
                    'station_id': sid,
                    'nom': sub_st_ev.iloc[0]['nom'],
                    'bassin': sub_st_ev.iloc[0]['bassin'],
                    'experiment': exp_id,
                    'formulation': exp_label,
                    'q_peak_obs_m3s': round(q_peak_obs, 2),
                    'q_peak_sim_m3s': round(q_peak_sim, 2),
                    'biais_pic_pct': bias_peak_pct,
                    'vol_obs_hm3': round(vol_obs_hm3, 2),
                    'vol_sim_hm3': round(vol_sim_hm3, 2),
                    'biais_vol_pct': bias_vol_pct
                })

    df_floods = pd.DataFrame(flood_records)
    df_floods.to_csv(OUT_FLOODS_CSV, index=False)
    print("Table des crues sauvegardée :", OUT_FLOODS_CSV)

    # Sauvegarde Markdown de synthèse
    with open(OUT_METRICS_MD, 'w', encoding='utf-8') as f:
        f.write("# Évaluation des Performances Multi-Stations — Année 2018\n\n")
        f.write("Ce document présente la comparaison des 4 formulations OPL (SIMGM, SIMTOP, Schaake96, BATS) "
                "sur l'ensemble des 10 stations hydrométriques ABH exploitables.\n\n")
        
        f.write("## 1. Synthèse Globale des Performances par Station\n\n")
        cols_disp = ['nom', 'bassin', 'pas_temps', 'formulation', 'NSE_daily', 'KGE_daily', 'delta_NSE_daily', 
                     'NSE_monthly', 'KGE_monthly', 'PBIAS_monthly_pct', 'r_monthly']
        f.write("| " + " | ".join(cols_disp) + " |\n")
        f.write("| " + " | ".join(['---'] * len(cols_disp)) + " |\n")
        for _, r in df_metrics.sort_values(by=['bassin', 'nom', 'experiment']).iterrows():
            vals = [str(r[c]) if not isinstance(r[c], float) else f"{r[c]:.2f}" for c in cols_disp]
            f.write("| " + " | ".join(vals) + " |\n")
        f.write("\n---\n\n")

        f.write("## 2. Diagnostic d'Étiage Estival (Juin–Septembre 2018, 122 jours)\n\n")
        disp_lf = ['nom', 'bassin', 'formulation', 'q_mean_obs_m3s', 'q_mean_sim_m3s', 'n_days_le_01_obs', 
                   'n_days_le_01_sim', 'n_days_zero_obs', 'n_days_zero_sim', 'max_dry_spell_obs_days', 'max_dry_spell_sim_days']
        f.write("| " + " | ".join(disp_lf) + " |\n")
        f.write("| " + " | ".join(['---'] * len(disp_lf)) + " |\n")
        for _, r in df_lowflow.sort_values(by=['bassin', 'nom', 'experiment']).iterrows():
            vals = [str(r[c]) if not isinstance(r[c], float) else f"{r[c]:.2f}" for c in disp_lf]
            f.write("| " + " | ".join(vals) + " |\n")
        f.write("\n\n")

    print("Markdown de synthèse généré :", OUT_METRICS_MD)

if __name__ == '__main__':
    main()
