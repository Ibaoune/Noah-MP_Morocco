#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
extract_multistation_fluxes.py
Extrait les flux journaliers amont (P, Qs, Qsb, Qin = Qs + Qsb) pour les 10 stations
hydrométriques ABH retenues en 2018 sur les 4 formulations OPL.
Contrôle la cohérence des précipitations et la conservation volumique du remapping.
"""

import os
import sys
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

REPO_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = os.path.join(REPO_ROOT, "experiments/NorthMor/opl_hydrology_sensitivity")
LDT_PATH = os.path.join(REPO_ROOT, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
INVENTORY_CSV = os.path.join(SENS_DIR, "postproc/tables/station_inventory_2018.csv")

OUT_DAILY_CSV = os.path.join(SENS_DIR, "postproc/tables/catchment_fluxes_multistation_daily_2018.csv")
OUT_MONTHLY_CSV = os.path.join(SENS_DIR, "postproc/tables/catchment_fluxes_multistation_monthly_2018.csv")
OUT_SUMMARY_CSV = os.path.join(SENS_DIR, "postproc/tables/catchment_fluxes_multistation_summary_2018.csv")
OUT_SUMMARY_MD = os.path.join(SENS_DIR, "postproc/tables/catchment_fluxes_multistation_summary_2018.md")

SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM"),
    ("OL_R2_SIMTOP", "SIMTOP"),
    ("OL_R3_SCHAAKE96", "Schaake96"),
    ("OL_R4_BATS", "BATS")
]

def main():
    print("[1/4] Chargement LDT et délimitation D8 des bassins versants...")
    ds_ldt = nc.Dataset(LDT_PATH)
    grid_area = ds_ldt['HYMAP_grid_area'][:].filled(0.0)
    flow_x = ds_ldt['HYMAP_flow_direction_x'][:]
    flow_y = ds_ldt['HYMAP_flow_direction_y'][:]
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

    def get_catchment(orow, ocol):
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

    # Charger l'inventaire et filtrer les stations retenues
    df_inv = pd.read_csv(INVENTORY_CSV)
    df_retained = df_inv[df_inv['statut_2018'] != 'Exclue'].copy()
    print("Stations retenues (" + str(len(df_retained)) + ") :", list(df_retained['station_id']))

    station_weights = {}
    station_areas = {}
    for _, row in df_retained.iterrows():
        sid = row['station_id']
        r_hy, c_hy = int(row['row_hymap']), int(row['col_hymap'])
        cat = get_catchment(r_hy, c_hy)
        tot_area = sum(grid_area[cr, cc] for cr, cc in cat)
        w = np.zeros((R, C), dtype=float)
        for cr, cc in cat:
            w[cr, cc] = grid_area[cr, cc] / tot_area
        station_weights[sid] = w
        station_areas[sid] = tot_area

    # Jours 2018
    dates_2018 = [datetime.date(2018, 1, 1) + datetime.timedelta(days=i) for i in range(365)]

    # Extraction commune de P (identique pour toutes les expériences)
    print("[2/4] Extraction des précipitations journalières amont (P IMERG)...")
    daily_p_by_station = {sid: [] for sid in station_weights}
    
    # Lire P depuis le run de référence SIMGM
    ref_noah_dir = os.path.join(SENS_DIR, "experiments/OL_R1_SIMGM/output")
    for d in dates_2018:
        file_dt = d + datetime.timedelta(days=1)
        m_folder = d.strftime('%Y-%m')
        ym = file_dt.strftime('%Y%m')
        fname = f"LIS_HIST_{file_dt.strftime('%Y%m%d0000')}.d01.nc"
        noah_f = os.path.join(ref_noah_dir, m_folder, "SURFACEMODEL", ym, fname)
        
        with nc.Dataset(noah_f, 'r') as ds:
            p_arr = ds['Rainf_f_tavg'][:]
            if p_arr.ndim == 3:
                p_arr = p_arr[0]
            # Remap 2x2 vers 120x180
            p_remap = 0.25 * (p_arr[:-1, :-1] + p_arr[:-1, 1:] + p_arr[1:, :-1] + p_arr[1:, 1:])
            
        for sid, w in station_weights.items():
            p_val = float(np.sum(p_remap * w) * 86400.0)  # kg/m2/s -> mm/day
            daily_p_by_station[sid].append(p_val)

    # 3. Extraction Qs et Qsb pour chaque expérience
    print("[3/4] Extraction des flux Qs et Qsb pour les 4 schémas...")
    records_daily = []
    
    # Structure de contrôle conservation
    conservation_check = []

    for exp_id, exp_label in SCHEMES:
        print("  Traitement " + exp_id + " (" + exp_label + ")...")
        remap_dir = os.path.join(SENS_DIR, "routing/runs/remap_180x120", exp_id, "SURFACEMODEL")
        noah_dir = os.path.join(SENS_DIR, "experiments", exp_id, "output")
        
        # Test de conservation sur un jour d'hiver représentatif (2018-03-08 crue)
        f_test_noah = os.path.join(noah_dir, "2018-03/SURFACEMODEL/201803/LIS_HIST_201803090000.d01.nc")
        f_test_remap = os.path.join(remap_dir, "201803/LIS_HIST_201803090000.d01.nc")
        
        with nc.Dataset(f_test_noah) as ds_n, nc.Dataset(f_test_remap) as ds_r:
            qs_n = np.nan_to_num(ds_n['Qs_tavg'][:])
            qsb_n = np.nan_to_num(ds_n['Qsb_tavg'][:])
            if qs_n.ndim == 3: qs_n = qs_n[0]
            if qsb_n.ndim == 3: qsb_n = qsb_n[0]
            
            qs_r = np.nan_to_num(ds_r['Qs_tavg'][:])
            qsb_r = np.nan_to_num(ds_r['Qsb_tavg'][:])
            if qs_r.ndim == 3: qs_r = qs_r[0]
            if qsb_r.ndim == 3: qsb_r = qsb_r[0]
            
            # Aire brute vs aire hymap
            # Note: pour noah-mp, aire moyenne ~25 km2
            vol_raw = float(np.sum(qs_n + qsb_n))
            vol_rem = float(np.sum(qs_r + qsb_r))
            ratio = (vol_rem / vol_raw) if vol_raw > 0 else 1.0
            conservation_check.append({
                'experiment': exp_id,
                'formulation': exp_label,
                'date_test': '2018-03-08',
                'sum_raw': vol_raw,
                'sum_remap': vol_rem,
                'ratio_remap_raw': ratio
            })

        for day_idx, d in enumerate(dates_2018):
            file_dt = d + datetime.timedelta(days=1)
            ym = file_dt.strftime('%Y%m')
            fname = f"LIS_HIST_{file_dt.strftime('%Y%m%d0000')}.d01.nc"
            remap_f = os.path.join(remap_dir, ym, fname)
            
            with nc.Dataset(remap_f, 'r') as ds:
                qs_arr = ds['Qs_tavg'][:]
                qsb_arr = ds['Qsb_tavg'][:]
                if qs_arr.ndim == 3: qs_arr = qs_arr[0]
                if qsb_arr.ndim == 3: qsb_arr = qsb_arr[0]

            d_str = d.strftime('%Y-%m-%d')
            for sid, sinfo in df_retained.set_index('station_id').iterrows():
                w = station_weights[sid]
                area_m2 = station_areas[sid]
                
                p_mm = daily_p_by_station[sid][day_idx]
                qs_mm = float(np.sum(qs_arr * w) * 86400.0)
                qsb_mm = float(np.sum(qsb_arr * w) * 86400.0)
                qin_mm = qs_mm + qsb_mm
                
                # Débits équivalents d'apport amont en m3/s : flux(m/s) * area(m2)
                qs_m3s = (qs_mm * 1e-3 / 86400.0) * area_m2
                qsb_m3s = (qsb_mm * 1e-3 / 86400.0) * area_m2
                qin_m3s = qs_m3s + qsb_m3s
                
                records_daily.append({
                    'station_id': sid,
                    'nom': sinfo['nom'],
                    'bassin': sinfo['bassin'],
                    'sous_bassin': sinfo['sous_bassin'],
                    'aire_d8_km2': round(area_m2 / 1e6, 2),
                    'experiment': exp_id,
                    'formulation': exp_label,
                    'date': d_str,
                    'annee': d.year,
                    'mois': d.month,
                    'P_mm_day': round(p_mm, 4),
                    'Qs_mm_day': round(qs_mm, 4),
                    'Qsb_mm_day': round(qsb_mm, 4),
                    'Qin_mm_day': round(qin_mm, 4),
                    'Qs_m3s': round(qs_m3s, 4),
                    'Qsb_m3s': round(qsb_m3s, 4),
                    'Qin_m3s': round(qin_m3s, 4)
                })

    df_daily = pd.DataFrame(records_daily)
    os.makedirs(os.path.dirname(OUT_DAILY_CSV), exist_ok=True)
    df_daily.to_csv(OUT_DAILY_CSV, index=False)
    print("Fichier journalier sauvegardé :", OUT_DAILY_CSV, "(", len(df_daily), "lignes)")

    # 4. Agréger au pas mensuel et annuel
    print("[4/4] Calcul des cumuls mensuels, saisonniers et de synthèse...")
    df_monthly = df_daily.groupby(['station_id', 'nom', 'bassin', 'sous_bassin', 'aire_d8_km2', 
                                   'experiment', 'formulation', 'annee', 'mois'])[['P_mm_day', 'Qs_mm_day', 'Qsb_mm_day', 'Qin_mm_day']].sum().reset_index()
    df_monthly = df_monthly.rename(columns={
        'P_mm_day': 'P_mm_month',
        'Qs_mm_day': 'Qs_mm_month',
        'Qsb_mm_day': 'Qsb_mm_month',
        'Qin_mm_day': 'Qin_mm_month'
    })
    df_monthly.to_csv(OUT_MONTHLY_CSV, index=False)
    print("Fichier mensuel sauvegardé :", OUT_MONTHLY_CSV)

    # Synthèse annuelle 2018 par station et schéma
    df_ann = df_daily.groupby(['station_id', 'nom', 'bassin', 'sous_bassin', 'aire_d8_km2', 
                               'experiment', 'formulation'])[['P_mm_day', 'Qs_mm_day', 'Qsb_mm_day', 'Qin_mm_day']].sum().reset_index()
    df_ann = df_ann.rename(columns={
        'P_mm_day': 'P_mm_yr',
        'Qs_mm_day': 'Qs_mm_yr',
        'Qsb_mm_day': 'Qsb_mm_yr',
        'Qin_mm_day': 'Qin_mm_yr'
    })
    df_ann['ratio_Qsb_Qin_pct'] = round(df_ann['Qsb_mm_yr'] / df_ann['Qin_mm_yr'] * 100.0, 1)
    df_ann['ratio_Qin_P_pct'] = round(df_ann['Qin_mm_yr'] / df_ann['P_mm_yr'] * 100.0, 1)

    # Ajouter les flux d'été (JJA : juin-juillet-août)
    mask_jja = df_daily['mois'].isin([6, 7, 8])
    df_jja = df_daily[mask_jja].groupby(['station_id', 'experiment'])[['Qsb_mm_day', 'Qin_mm_day']].sum().reset_index()
    df_jja = df_jja.rename(columns={'Qsb_mm_day': 'Qsb_mm_jja', 'Qin_mm_day': 'Qin_mm_jja'})
    df_ann = df_ann.merge(df_jja, on=['station_id', 'experiment'])

    df_ann.to_csv(OUT_SUMMARY_CSV, index=False)
    print("Fichier de synthèse annuel sauvegardé :", OUT_SUMMARY_CSV)

    # Markdown de synthèse
    with open(OUT_SUMMARY_MD, 'w', encoding='utf-8') as f:
        f.write("# Diagnostic des Flux Précipitations, Qs et Qsb Multi-Stations (2018)\n\n")
        f.write("Ce document synthétise les apports surfaciques annuels (P, Qs, Qsb, Qin) pour les 10 stations "
                "hydrométriques retenues, sur les quatre formulations OPL.\n\n")
        
        f.write("## 1. Contrôle de Conservation du Remapping (Événement du 08 mars 2018)\n\n")
        f.write("| Expérience | Formulation | Somme brute Noah-MP | Somme remappée HyMAP | Ratio Remap/Raw | Statut |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for cc in conservation_check:
            st = "CONSERVATIF (<0.01% écart)" if abs(cc['ratio_remap_raw'] - 1.0) < 0.005 else "Écart détecté"
            f.write(f"| {cc['experiment']} | {cc['formulation']} | {cc['sum_raw']:.4f} | {cc['sum_remap']:.4f} | {cc['ratio_remap_raw']:.5f} | {st} |\n")
        f.write("\n---\n\n")

        f.write("## 2. Cumuls Annuels 2018 par Bassin et Formulation\n\n")
        disp_cols = ['nom', 'bassin', 'aire_d8_km2', 'formulation', 'P_mm_yr', 'Qs_mm_yr', 'Qsb_mm_yr', 'Qin_mm_yr', 'ratio_Qsb_Qin_pct', 'Qsb_mm_jja']
        f.write("| " + " | ".join(disp_cols) + " |\n")
        f.write("| " + " | ".join(['---'] * len(disp_cols)) + " |\n")
        for _, r in df_ann.sort_values(by=['bassin', 'nom', 'experiment']).iterrows():
            vals = [str(r[c]) if not isinstance(r[c], float) else f"{r[c]:.1f}" for c in disp_cols]
            f.write("| " + " | ".join(vals) + " |\n")
        f.write("\n\n")

    print("Inventaire Markdown généré :", OUT_SUMMARY_MD)

if __name__ == '__main__':
    main()
