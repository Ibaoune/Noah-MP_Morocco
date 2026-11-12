#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evaluation systematique des evenements de crue (2016–2020) pour Lalla Chafia et Sidi Jabeur.
Analyse comparative des hydrogrammes ABH et des simulations HyMAP-2 (linres=1 et linres=0),
avec partitionnement des flux amont Noah-MP (P, Qs, Qsb, Qin_HyMAP).

Methode de selection et de separation explicite des crues :
  1. Identification de 24 fenetres regionales communes aux bassins du Bouregreg (Lalla Chafia)
     et du Grou (Sidi Jabeur) sur 2016–2020. Ces fenetres communes permettent une comparaison
     rigoureuse et synchronisee de la reponse hydrologique des deux bassins versants amont.
  2. Chaque fenetre est testee pour verifier si le seuil de crue ABH est atteint
     (seuil de pointe >= 25 m3/s a Lalla Chafia, >= 30 m3/s a Sidi Jabeur).
  3. Definition d'une fenetre hydrologique [t_start, t_end] incluant :
     - 1 a 2 jours calmes avant la montee de crue (integration de la pluie declenchante),
     - L'integralite de la crue et des pics secondaires,
     - La recession complete jusqu'au retour vers le debit de base (< 10 m3/s).
  4. Les 24 fenetres sont strictement disjointes (Crue_2016_11_Nov bornee au 30/11 pour eviter
     tout chevauchement avec Crue_2016_12_Dec1 demarrant le 01/12).

Distinctions et precisions physiques fondamentales :
  - Surface des bassins et mailles D8 :
    * Lalla Chafia (133 mailles D8) : surfaces variables de 1.17 a 75.41 km2 (moyenne 25.06 km2) ;
      somme exacte HYMAP_grid_area = 3 333 348 864 m2 = 3 333.35 km2.
    * Sidi Jabeur (121 mailles D8) : surfaces variables de 0.14 a 77.07 km2 (moyenne 25.87 km2) ;
      somme exacte HYMAP_grid_area = 3 130 554 112 m2 = 3 130.55 km2.
  - Volume entrant HyMAP (Qin_HyMAP) : Construit par sommation spatiale des flux de ruissellement
    bruts de surface Qs et de subsurface Qsb generes par Noah-MP sur chaque maille amont, convertis
    en m3/s : Qin_HyMAP = sum((Qs + Qsb) * maille_m2) / 1000. Son integration temporelle est
    mathematiquement identique au volume lame d'eau (Qs + Qsb) [mm] * Surface_bassin [km2] * 1e-3.
  - Distinction essentielle : Ce Qin_HyMAP (flux lateral entrant dans le reseau hydrographique)
    est distinct du QIN vertical etudie dans le diagnostic estival SIMGM (echange net sol-nappe).
  - Role du routage HyMAP et conservation de masse : Sur une fenetre fermee [t_start, t_end],
    une similitude entre volume entrant V_qin et volume sortant V_sim (V_qin ~= V_sim) reflete
    le bilan de masse a l'echelle de l'evenement (Delta_S_HyMAP ~= 0 entre etats non inondes).
    Elle ne demontre pas une absence d'effet du routage : HyMAP redistribue le flux dans le temps
    (ecretement de pointe, amortissement en plaine d'inondation, deceleration et traine de recession).
  - Nature des volumes observes ABH : V_obs integre le debit total enregistre a la station
    (incluant le debit de base continu Qbase) ; il ne s'agit pas d'un ruissellement rapide isole.
  - Sens physique des bilans : Pour expliquer un deficit de debit simule (Qsim << Qobs), une
    sous-estimation de l'ET ou des pertes fluviales accrues conduirait au resultat inverse (une
    sous-estimation d'ET laisserait plus d'eau disponible pour le debit, et des pertes fluviales
    reduiraient encore le debit simule). Les hypotheses physiques coherentes reposent donc sur
    une sous-estimation de la pluie d'orage IMERG, une surestimation de l'ET reelle, une retention
    profonde excessive, ou des processus de ruissellement rapide non resolus a 10 km.
  - Traitement des observations manquantes : Si une donnee ABH est manquante dans une fenetre
    (ex. 06/01/2018 a Lalla Chafia), elle n'est pas remplacee artificiellement ni interpolee ;
    les volumes bruts et les indicateurs de completude sont conserves, mais les ratios de volumes
    sont rendus non evaluables (NaN) et classes de facon neutre en 'Observation incomplete',
    excluant cet enregistrement des statistiques agregees de performance volumique.

Classification multidimensionnelle :
  - Diagnostic de volume (Rv = Vsim_lr0 / Vobs)
  - Diagnostic d'amplitude de pointe (Rq = Qpeak_lr0 / Qpeak_obs)
  - Diagnostic de synchronisme (Delta_t = t_peak_lr0 - t_peak_obs)
  - Diagnostic principal hierarchise : Priorite absolue aux deficits de volume majeurs (Rv < 0.40).
"""

import os
import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Repertoires de travail
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TABLES_DIR = os.path.join(BASE_DIR, "plots", "sebou_bouregreg", "tables")
PLOTS_DIR = os.path.join(BASE_DIR, "plots", "sebou_bouregreg")
ARTIFACT_DIR = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e"

STATIONS = {
    'lalla_chafia': {
        'name': 'Lalla Chafia',
        'basin': 'Bouregreg',
        'river': 'Bouregreg',
        'n_cells_d8': 133,
        'area_km2': 3333.35,  # 133 mailles D8 (moyenne 25.06 km2/maille, somme exacte = 3333.35 km2)
        'flood_threshold_m3s': 25.0,
        'csv_path': os.path.join(TABLES_DIR, 'lalla_chafia_fluxes_2016_2020.csv'),
    },
    'sidi_jabeur': {
        'name': 'Sidi Jabeur',
        'basin': 'Bouregreg',
        'river': 'Grou',
        'n_cells_d8': 121,
        'area_km2': 3130.55,  # 121 mailles D8 (moyenne 25.87 km2/maille, somme exacte = 3130.55 km2)
        'flood_threshold_m3s': 30.0,
        'csv_path': os.path.join(TABLES_DIR, 'sidi_jabeur_fluxes_2016_2020.csv'),
    }
}

# Liste des 24 fenetres regionales communes 2016-2020 (strictement disjointes)
COMMON_EVENTS = [
    # 2016
    ("Crue_2016_01_Jan", "2016-01-05", "2016-01-16", "2016-01-24", "Episode hivernal precoce 2016"),
    ("Crue_2016_02_Fev", "2016-02-23", "2016-02-28", "2016-03-03", "Petite crue de fin fevrier 2016"),
    ("Crue_2016_03_Mar", "2016-03-20", "2016-03-24", "2016-03-31", "Crue printaniere mars 2016 (Grou)"),
    ("Crue_2016_05_Mai", "2016-05-06", "2016-05-10", "2016-05-16", "Crue orageuse de mai 2016"),
    ("Crue_2016_11_Nov", "2016-11-21", "2016-11-28", "2016-11-30", "Premiere vague automnale 2016"),
    ("Crue_2016_12_Dec1", "2016-12-01", "2016-12-06", "2016-12-11", "Deuxieme vague decembre 2016"),
    ("Crue_2016_12_Dec2", "2016-12-14", "2016-12-17", "2016-12-23", "Troisieme vague decembre 2016"),
    # 2017
    ("Crue_2017_01_Jan", "2017-01-22", "2017-01-28", "2017-02-03", "Crue hivernale janvier 2017"),
    ("Crue_2017_02_Fev", "2017-02-18", "2017-02-24", "2017-03-03", "Crue majeure de fevrier 2017"),
    ("Crue_2017_04_Avr", "2017-04-21", "2017-04-25", "2017-04-30", "Crue printaniere avril 2017"),
    ("Crue_2017_12_Dec", "2017-11-28", "2017-12-01", "2017-12-07", "Crue automnale debut decembre 2017"),
    # 2018 (Annee record)
    ("Crue_2018_01_Jan", "2018-01-05", "2018-01-09", "2018-01-16", "Crue hivernale debut janvier 2018"),
    ("Crue_2018_02_Fev", "2018-01-31", "2018-02-06", "2018-02-14", "Crue saturee debut fevrier 2018"),
    ("Crue_2018_03_Mar", "2018-02-28", "2018-03-08", "2018-03-22", "Crue majeure de mars 2018"),
    ("Crue_2018_04_Avr1", "2018-04-10", "2018-04-15", "2018-04-20", "Premiere vague printaniere avril 2018"),
    ("Crue_2018_04_Avr2", "2018-04-21", "2018-04-25", "2018-05-02", "Deuxieme vague printaniere avril 2018"),
    ("Crue_2018_05_Mai", "2018-05-05", "2018-05-09", "2018-05-15", "Crue tardive mai 2018"),
    ("Crue_2018_10_Oct", "2018-10-25", "2018-10-29", "2018-11-05", "Crue automnale fin octobre / debut nov 2018"),
    ("Crue_2018_11_Nov", "2018-11-18", "2018-11-24", "2018-12-01", "Crue automnale fin novembre 2018"),
    # 2019
    ("Crue_2019_04_Avr", "2019-03-29", "2019-04-01", "2019-04-06", "Petite crue de printemps 2019"),
    ("Crue_2019_12_Dec", "2019-12-14", "2019-12-18", "2019-12-24", "Crue hivernale decembre 2019"),
    # 2020
    ("Crue_2020_03_Mar", "2020-03-20", "2020-03-25", "2020-03-31", "Crue de debut de printemps 2020"),
    ("Crue_2020_04_Avr", "2020-04-19", "2020-04-25", "2020-05-01", "Crue printaniere avril 2020"),
    ("Crue_2020_05_Mai", "2020-05-10", "2020-05-16", "2020-05-22", "Crue tardive mai 2020 (Grou)"),
]

def analyze_flood_events():
    """Analyse systematique des 24 fenetres regionales pour Lalla Chafia et Sidi Jabeur."""
    dfs = {}
    for stn_key, stn_cfg in STATIONS.items():
        if not os.path.exists(stn_cfg['csv_path']):
            raise FileNotFoundError(f"Fichier introuvable : {stn_cfg['csv_path']}")
        df = pd.read_csv(stn_cfg['csv_path'], parse_dates=['date'])
        dfs[stn_key] = df

    records = []

    for ev_id, (ev_name, start_date_str, peak_ref_str, end_date_str, desc) in enumerate(COMMON_EVENTS, 1):
        d_start = pd.to_datetime(start_date_str)
        d_end = pd.to_datetime(end_date_str)
        duration_days = (d_end - d_start).days + 1

        for stn_key, stn_cfg in STATIONS.items():
            df_full = dfs[stn_key]
            sub = df_full[(df_full['date'] >= d_start) & (df_full['date'] <= d_end)].copy()

            if len(sub) == 0:
                continue

            area_km2 = stn_cfg['area_km2']
            thresh_m3s = stn_cfg['flood_threshold_m3s']
            conv_mm_to_hm3 = area_km2 * 1e-3  # mm -> hm3
            conv_m3s_d_to_hm3 = 86400.0 / 1e6 # 0.0864

            # 1. Completude des observations ABH
            n_days_total = duration_days
            n_obs_valid = int(sub['q_obs_m3s'].notna().sum())
            is_obs_complete = bool(n_obs_valid == n_days_total)
            obs_completeness_pct = round(n_obs_valid / n_days_total * 100.0, 1)

            # 2. Pic observe ABH (inclut debit de base)
            peak_obs_val = float(sub['q_obs_m3s'].max()) if n_obs_valid > 0 else np.nan
            peak_obs_idx = sub['q_obs_m3s'].idxmax() if n_obs_valid > 0 else None
            peak_obs_date = sub.loc[peak_obs_idx, 'date'] if peak_obs_idx is not None else pd.NaT
            is_thresh_met = bool(peak_obs_val >= thresh_m3s) if not np.isnan(peak_obs_val) else False

            # 3. Pic simule linres=0
            peak_lr0_val = float(sub['q_sim_linres0_m3s'].max())
            peak_lr0_idx = sub['q_sim_linres0_m3s'].idxmax()
            peak_lr0_date = sub.loc[peak_lr0_idx, 'date']
            lag_lr0 = int((peak_lr0_date - peak_obs_date).days) if pd.notna(peak_obs_date) else np.nan
            ratio_peak_lr0 = peak_lr0_val / peak_obs_val if (not np.isnan(peak_obs_val) and peak_obs_val > 0) else np.nan

            # 4. Pic simule linres=1
            peak_h1_val = float(sub['q_sim_hist_m3s'].max())
            peak_h1_idx = sub['q_sim_hist_m3s'].idxmax()
            peak_h1_date = sub.loc[peak_h1_idx, 'date']
            lag_h1 = int((peak_h1_date - peak_obs_date).days) if pd.notna(peak_obs_date) else np.nan
            ratio_peak_h1 = peak_h1_val / peak_obs_val if (not np.isnan(peak_obs_val) and peak_obs_val > 0) else np.nan

            # 5. Flux amont Noah-MP
            p_cum_mm = float(sub['precip_mm_d'].sum())
            qs_cum_mm = float(sub['qs_mm_d'].sum())
            qsb_cum_mm = float(sub['qsb_mm_d'].sum())
            qtot_noah_mm = float(sub['qtot_runoff_mm_d'].sum())
            qs_ratio_pct = (qs_cum_mm / qtot_noah_mm * 100.0) if qtot_noah_mm > 0 else np.nan

            # 6. Volumes ecoules (hm3 et mm)
            # v_obs_hm3 somme uniquement les jours valides sans inventer de valeur
            v_obs_hm3 = float((sub['q_obs_m3s'].dropna() * conv_m3s_d_to_hm3).sum()) if n_obs_valid > 0 else np.nan
            v_lr0_hm3 = float((sub['q_sim_linres0_m3s'] * conv_m3s_d_to_hm3).sum())
            v_h1_hm3 = float((sub['q_sim_hist_m3s'] * conv_m3s_d_to_hm3).sum())
            v_qin_noah_hm3 = float((sub['qin_m3s'] * conv_m3s_d_to_hm3).sum())

            v_obs_mm = v_obs_hm3 / conv_mm_to_hm3 if not np.isnan(v_obs_hm3) else np.nan
            v_lr0_mm = v_lr0_hm3 / conv_mm_to_hm3
            v_h1_mm = v_h1_hm3 / conv_mm_to_hm3
            v_qin_noah_mm = v_qin_noah_hm3 / conv_mm_to_hm3

            # Ratios volumiques : non evaluables (NaN) lorsque les observations sont incompletes
            # afin de ne pas fausser l'evaluation en comparant un volume simule sur N jours a un volume observe partiel
            if is_obs_complete and not np.isnan(v_obs_hm3) and v_obs_hm3 > 0:
                ratio_vol_lr0 = v_lr0_hm3 / v_obs_hm3
                ratio_vol_h1 = v_h1_hm3 / v_obs_hm3
                ratio_vol_qin = v_qin_noah_hm3 / v_obs_hm3
                cr_obs = (v_obs_mm / p_cum_mm * 100.0) if (p_cum_mm > 0 and not np.isnan(v_obs_mm)) else np.nan
                ratio_vol_status = 'Complet'
            else:
                ratio_vol_lr0 = np.nan
                ratio_vol_h1 = np.nan
                ratio_vol_qin = np.nan
                cr_obs = np.nan
                ratio_vol_status = f'Non evaluable (obs incomplete: {n_obs_valid}/{n_days_total} j)'

            cr_noah = (qtot_noah_mm / p_cum_mm * 100.0) if p_cum_mm > 0 else np.nan

            # 7. Diagnostics separes (evalue sur linres=0)
            # A. Diagnostic de volume
            if not is_obs_complete:
                diag_volume = "Observation incomplete"
            elif np.isnan(ratio_vol_lr0):
                diag_volume = "Non calculable (obs manquante)"
            elif ratio_vol_lr0 < 0.40:
                diag_volume = "Deficit volumique majeur (Rv < 0.40)"
            elif ratio_vol_lr0 < 0.65:
                diag_volume = "Deficit volumique modere (0.40 <= Rv < 0.65)"
            elif ratio_vol_lr0 <= 1.35:
                diag_volume = "Volume satisfaisant (0.65 <= Rv <= 1.35)"
            else:
                diag_volume = "Surestimation volumique (Rv > 1.35)"

            # B. Diagnostic d'amplitude de pointe
            if np.isnan(ratio_peak_lr0):
                diag_peak = "Non calculable"
            elif ratio_peak_lr0 < 0.40:
                diag_peak = "Ecrasement severe pointe (Rq < 0.40)"
            elif ratio_peak_lr0 < 0.70:
                diag_peak = "Sous-estimation moderee pointe (0.40 <= Rq < 0.70)"
            elif ratio_peak_lr0 <= 1.30:
                diag_peak = "Pointe bien restituee (0.70 <= Rq <= 1.30)"
            else:
                diag_peak = "Surestimation pointe (Rq > 1.30)"

            # C. Diagnostic de synchronisme (timing)
            if np.isnan(lag_lr0):
                diag_timing = "Non calculable"
            elif lag_lr0 == 0:
                diag_timing = "Synchrone (0 j)"
            elif lag_lr0 == 1:
                diag_timing = "Leger retard (+1 j)"
            elif lag_lr0 == -1:
                diag_timing = "Legere avance (-1 j)"
            elif lag_lr0 >= 2:
                diag_timing = f"Retard prononce (+{lag_lr0} j)"
            else:
                diag_timing = f"Avance prononcee ({lag_lr0} j)"

            # D. Diagnostic principal hierarchise (priorite absolue au deficit volumique)
            if not is_obs_complete:
                primary_diag = "Observation incomplete"
            elif ratio_vol_lr0 < 0.40:
                primary_diag = "Deficit de volume majeur"
            elif ratio_vol_lr0 >= 0.65 and ratio_peak_lr0 < 0.45:
                primary_diag = "Ecrasement pointe / amortissement dynamique"
            elif ratio_peak_lr0 > 1.30 or ratio_vol_lr0 > 1.35:
                primary_diag = "Surestimation pointe/volume"
            elif abs(lag_lr0) >= 2:
                primary_diag = "Erreur de synchronisme (timing)"
            elif ratio_vol_lr0 >= 0.60 and ratio_peak_lr0 >= 0.45:
                primary_diag = "Bien reproduite (volume & dynamique)"
            else:
                primary_diag = "Sous-estimation moderee mixte"

            rec = {
                'event_code': f"{ev_name}_{stn_key[:2].upper()}",
                'event_name': ev_name,
                'station_key': stn_key,
                'station_name': stn_cfg['name'],
                'basin': stn_cfg['basin'],
                'area_km2': area_km2,
                'n_cells_d8': stn_cfg['n_cells_d8'],
                'start_date': start_date_str,
                'end_date': end_date_str,
                'duration_days': duration_days,
                'n_obs_valid_days': n_obs_valid,
                'is_obs_complete': is_obs_complete,
                'obs_completeness_pct': obs_completeness_pct,
                'flood_threshold_m3s': thresh_m3s,
                'is_threshold_met': is_thresh_met,
                'p_cum_mm': round(p_cum_mm, 1),
                'q_obs_peak_m3s': round(peak_obs_val, 1) if not np.isnan(peak_obs_val) else np.nan,
                'date_peak_obs': peak_obs_date.strftime('%Y-%m-%d') if pd.notna(peak_obs_date) else 'N/A',
                'q_lr0_peak_m3s': round(peak_lr0_val, 1),
                'date_peak_lr0': peak_lr0_date.strftime('%Y-%m-%d'),
                'lag_lr0_days': lag_lr0 if not np.isnan(lag_lr0) else np.nan,
                'ratio_peak_lr0': round(ratio_peak_lr0, 2) if not np.isnan(ratio_peak_lr0) else np.nan,
                'q_h1_peak_m3s': round(peak_h1_val, 1),
                'date_peak_h1': peak_h1_date.strftime('%Y-%m-%d'),
                'lag_h1_days': lag_h1 if not np.isnan(lag_h1) else np.nan,
                'ratio_peak_h1': round(ratio_peak_h1, 2) if not np.isnan(ratio_peak_h1) else np.nan,
                'v_obs_hm3': round(v_obs_hm3, 2) if not np.isnan(v_obs_hm3) else np.nan,
                'v_obs_mm': round(v_obs_mm, 2) if not np.isnan(v_obs_mm) else np.nan,
                'v_lr0_hm3': round(v_lr0_hm3, 2),
                'v_lr0_mm': round(v_lr0_mm, 2),
                'ratio_vol_lr0': round(ratio_vol_lr0, 2) if not np.isnan(ratio_vol_lr0) else np.nan,
                'ratio_vol_status': ratio_vol_status,
                'v_h1_hm3': round(v_h1_hm3, 2),
                'v_h1_mm': round(v_h1_mm, 2),
                'ratio_vol_h1': round(ratio_vol_h1, 2) if not np.isnan(ratio_vol_h1) else np.nan,
                'v_qin_noah_hm3': round(v_qin_noah_hm3, 2),
                'v_qin_noah_mm': round(v_qin_noah_mm, 2),
                'ratio_vol_qin': round(ratio_vol_qin, 2) if not np.isnan(ratio_vol_qin) else np.nan,
                'qs_cum_mm': round(qs_cum_mm, 2),
                'qsb_cum_mm': round(qsb_cum_mm, 2),
                'qtot_noah_mm': round(qtot_noah_mm, 2),
                'qs_ratio_pct': round(qs_ratio_pct, 1),
                'cr_obs_pct': round(cr_obs, 1) if not np.isnan(cr_obs) else np.nan,
                'cr_noah_pct': round(cr_noah, 1),
                'diag_volume': diag_volume,
                'diag_peak': diag_peak,
                'diag_timing': diag_timing,
                'primary_diagnosis': primary_diag,
                'description': desc
            }
            records.append(rec)

    df_res = pd.DataFrame(records)
    out_csv = os.path.join(TABLES_DIR, "flood_events_synthesis_2016_2020.csv")
    df_res.to_csv(out_csv, index=False)
    print(f"[OK] Table de synthese des crues sauvegardee ({len(df_res)} lignes) : {out_csv}")
    return df_res, dfs

def plot_representative_events(dfs, df_res):
    """Genere une figure multi-panneaux (4 evenements x 2 stations) des hydrogrammes representatifs."""
    selected_events = [
        ("Crue_2017_02_Fev", "Fevrier 2017 : Deficit volumique majeur", "2017-02-18", "2017-03-03"),
        ("Crue_2018_03_Mar", "Mars 2018 : Crue majeure fortement sous-estimee", "2018-02-28", "2018-03-22"),
        ("Crue_2018_04_Avr2", "Avril 2018 : Contraste Lalla Chafia vs Sidi Jabeur", "2018-04-20", "2018-05-02"),
        ("Crue_2018_11_Nov", "Novembre 2018 : Reponse aux impulsions automnales", "2018-11-18", "2018-12-01"),
    ]

    stations_order = [('lalla_chafia', 'Lalla Chafia (Bouregreg)'),
                      ('sidi_jabeur', 'Sidi Jabeur (Grou)')]

    fig, axes = plt.subplots(nrows=4, ncols=2, figsize=(16, 14), sharey='row')
    plt.subplots_adjust(hspace=0.35, wspace=0.12, top=0.93, bottom=0.06, left=0.07, right=0.92)

    # Palette de couleurs
    c_obs = '#111111'     # Noir profond
    c_lr0 = '#d62728'     # Rouge vif (linres=0)
    c_h1  = '#1f77b4'     # Bleu royal (linres=1)
    c_p   = '#4682b4'     # Bleu acier (pluie)

    for row_idx, (ev_name, ev_title, d_start_str, d_end_str) in enumerate(selected_events):
        d_start = pd.to_datetime(d_start_str)
        d_end = pd.to_datetime(d_end_str)

        # Trouver le max de debit sur la ligne pour aligner les echelles
        max_q_row = 0.0
        max_p_row = 0.0
        for stn_key, stn_label in stations_order:
            df_stn = dfs[stn_key]
            sub = df_stn[(df_stn['date'] >= d_start) & (df_stn['date'] <= d_end)]
            max_q_row = max(max_q_row, sub['q_obs_m3s'].max(), sub['q_sim_linres0_m3s'].max(), sub['q_sim_hist_m3s'].max())
            max_p_row = max(max_p_row, sub['precip_mm_d'].max())

        for col_idx, (stn_key, stn_label) in enumerate(stations_order):
            ax = axes[row_idx, col_idx]
            df_stn = dfs[stn_key]
            sub = df_stn[(df_stn['date'] >= d_start) & (df_stn['date'] <= d_end)].copy()

            # Recuperer les metriques dans df_res
            row_res = df_res[(df_res['event_name'] == ev_name) & (df_res['station_key'] == stn_key)]
            if len(row_res) > 0:
                res = row_res.iloc[0]
                q_obs_pk = res['q_obs_peak_m3s']
                q_lr0_pk = res['q_lr0_peak_m3s']
                q_h1_pk  = res['q_h1_peak_m3s']
                rv_lr0   = res['ratio_vol_lr0']
                rq_lr0   = res['ratio_peak_lr0']
                lag_lr0  = res['lag_lr0_days']
                p_cum    = res['p_cum_mm']
                diag     = res['primary_diagnosis']
            else:
                q_obs_pk, q_lr0_pk, q_h1_pk, rv_lr0, rq_lr0, lag_lr0, p_cum, diag = [0]*8

            # Axe jumeau pour la pluie (hyetogramme inverse en haut)
            ax_p = ax.twinx()
            ax_p.bar(sub['date'].values, sub['precip_mm_d'].values, width=0.6, color=c_p, alpha=0.25, label='Precip IMERG (mm/j)')
            ax_p.set_ylim(max_p_row * 3.5, 0)  # Inversion de l'axe de pluie
            if col_idx == 1:
                ax_p.set_ylabel('Pluie (mm/j)', color=c_p, fontsize=9)
                ax_p.tick_params(axis='y', labelcolor=c_p, labelsize=8)
            else:
                ax_p.set_yticks([])

            # Hydrogrammes
            l_obs = ax.plot(sub['date'].values, sub['q_obs_m3s'].values, color=c_obs, lw=2.2, label='Obs ABH (inclut Qbase)', zorder=4)
            l_lr0 = ax.plot(sub['date'].values, sub['q_sim_linres0_m3s'].values, color=c_lr0, lw=2.0, label='HyMAP linres=0 (recommandé)', zorder=3)
            l_h1  = ax.plot(sub['date'].values, sub['q_sim_hist_m3s'].values, color=c_h1, lw=1.6, ls='--', label='HyMAP linres=1 (historique)', zorder=2)

            # Marquer les pics
            pk_obs_row = sub.loc[sub['q_obs_m3s'].idxmax()]
            pk_lr0_row = sub.loc[sub['q_sim_linres0_m3s'].idxmax()]
            ax.scatter([pk_obs_row['date']], [pk_obs_row['q_obs_m3s']], color=c_obs, s=35, zorder=5)
            ax.scatter([pk_lr0_row['date']], [pk_lr0_row['q_sim_linres0_m3s']], color=c_lr0, s=35, zorder=5)

            # Echelles et limites
            ax.set_ylim(0, max_q_row * 1.15)
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%d/%m'))
            ax.grid(True, linestyle=':', alpha=0.6)

            if col_idx == 0:
                ax.set_ylabel(f"{ev_title.split(':')[0]}\nDébit ($m^3/s$)", fontsize=10, fontweight='bold')

            # Titre du panneau
            ax.set_title(f"{stn_label} — {ev_title.split(':')[0]} ({d_start.strftime('%d/%m')}–{d_end.strftime('%d/%m/%Y')})",
                         fontsize=10.5, pad=6)

            # Boite de texte synthetique avec metriques
            info_text = (f"Obs: {q_obs_pk:.1f} m³/s | P: {p_cum:.1f} mm\n"
                         f"lr0: {q_lr0_pk:.1f} m³/s (Rq={rq_lr0:.2f})\n"
                         f"Rv={rv_lr0:.2f} | Lag={lag_lr0:+d}j\n"
                         f"{diag}")
            ax.text(0.02, 0.95, info_text, transform=ax.transAxes, verticalalignment='top',
                    fontsize=8.5, bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.85, edgecolor='#cccccc'))

            # Legende unique sur le premier panneau
            if row_idx == 0 and col_idx == 0:
                lines = l_obs + l_lr0 + l_h1
                labels = [l.get_label() for l in lines] + ['Précip IMERG (droite)']
                ax.legend(lines + [plt.Rectangle((0,0),1,1, color=c_p, alpha=0.4)], labels,
                          loc='upper right', fontsize=8, framealpha=0.9)

    fig.suptitle("Diagnostic événementiel comparatif Noah-MP / HyMAP-2 (2016–2020)\n"
                 "Hydrogrammes observés ABH (incluant débit de base) vs simulations linres=0 et linres=1",
                 fontsize=13, fontweight='bold', y=0.98)

    out_fig = os.path.join(PLOTS_DIR, "flood_events_representative_hydrographs.png")
    plt.savefig(out_fig, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"[OK] Figure des hydrogrammes representatifs sauvegardee : {out_fig}")

    # Copie vers l'artefact IDE pour consultation UI
    artifact_fig = os.path.join(ARTIFACT_DIR, "flood_events_representative_hydrographs.png")
    os.system(f"cp {out_fig} {artifact_fig}")
    print(f"[OK] Figure copiee vers les artefacts IDE : {artifact_fig}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Diagnostic evenementiel des crues 2016-2020")
    parser.add_argument('--plot', action='store_true', help="Regenerer la figure des hydrogrammes representatifs")
    args = parser.parse_args()

    df_res, dfs = analyze_flood_events()
    if args.plot:
        plot_representative_events(dfs, df_res)

    print("\n" + "=" * 105)
    print("RESUME SYNTHETIQUE DES CRUES (2016–2020) :")
    print("=" * 105)
    cols = ['event_name', 'station_name', 'is_threshold_met', 'is_obs_complete', 'p_cum_mm',
            'q_obs_peak_m3s', 'q_lr0_peak_m3s', 'ratio_peak_lr0', 'v_obs_hm3', 'v_lr0_hm3',
            'ratio_vol_lr0', 'lag_lr0_days', 'primary_diagnosis']
    print(df_res[cols].to_string(index=False))

    # Statistiques agregees de performance volumique excluant explicitement les observations incompletes
    print("\n" + "=" * 105)
    print("STATISTIQUES AGREGEES DE PERFORMANCE VOLUMIQUE (linres=0, observations completes uniquement) :")
    print("=" * 105)
    df_complete = df_res[df_res['is_obs_complete']].copy()
    n_incomp = len(df_res) - len(df_complete)
    print(f"Enregistrements totaux : {len(df_res)} | Observations incompletes exclues : {n_incomp}")

    for stn_key in ['lalla_chafia', 'sidi_jabeur']:
        sub = df_complete[df_complete['station_key'] == stn_key]
        sub_thresh = sub[sub['is_threshold_met']]
        stn_name = sub['station_name'].iloc[0]
        print(f"\n--- {stn_name} ({stn_key}) ---")
        print(f"  Nombre de fenetres au seuil de crue : {len(sub_thresh)} / {len(sub)}")
        print(f"  Ratio volumique median Rv (lr0/obs) : {sub_thresh['ratio_vol_lr0'].median():.2f}")
        print(f"  Ratio volumique moyen  Rv (lr0/obs) : {sub_thresh['ratio_vol_lr0'].mean():.2f}")
        print(f"  Deficits de volume majeurs (Rv < 0.40) : {(sub_thresh['ratio_vol_lr0'] < 0.40).sum()} / {len(sub_thresh)} ({(sub_thresh['ratio_vol_lr0'] < 0.40).mean()*100:.1f}%)")
