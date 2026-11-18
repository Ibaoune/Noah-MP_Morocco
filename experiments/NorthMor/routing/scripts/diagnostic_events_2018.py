#!/usr/bin/env python3
"""
Diagnostic cible sur les evenements hydrologiques de 2018 pour 3 bassins amont :
- Lalla Chafia (Bouregreg, grille D8 HyMAP : 3 333.35 km2)
- Sidi Jabeur (Bouregreg, grille D8 HyMAP : 3 130.55 km2)
- Dar El Hamra (Sebou, grille D8 HyMAP : 654.75 km2)

Les superficies et cellules sont extraites directement du referentiel LDT corrigee.

Evenements etudies :
1. Evenement 05-09 mars 2018 (pic pluie 06-08 mars)
2. Evenement 23-27 avril 2018 (pic pluie 24-26 avril)
3. Evenements de novembre 2018 :
   3a. Crue d'automne / debut novembre (28 oct - 03 nov 2018)
   3b. Episodes pluvieux mi/fin novembre (18 - 25 nov 2018)

Auteur : M. El Aabaribaoune / Antigravity
"""

import os
import sys
import datetime
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Import du module de diagnostic pour extraire les superficies LDT
sys.path.insert(0, os.path.dirname(__file__))
import diagnostic_lalla_chafia_flux as diag

def main():
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    routing_dir = os.path.join(base_dir, "experiments/NorthMor/routing")
    ldt_path = os.path.join(routing_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    tbl_dir = os.path.join(routing_dir, "plots/sebou_bouregreg/tables")
    fig_dir = os.path.join(routing_dir, "plots/sebou_bouregreg/figures/forcing_runoff")
    os.makedirs(tbl_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)

    # 1. Recuperation dynamique des superficies et cellules depuis le LDT
    station_meta = [
        ('b_l_chafia', 'Lalla Chafia', 'Bouregreg', 75, 71, True, '#1f77b4'),
        ('b_s_jabeur', 'Sidi Jabeur', 'Bouregreg', 71, 71, True, '#2ca02c'),
        ('dar_el_hamra', 'Dar El Hamra', 'Sebou (Zloul)', 75, 112, False, '#d95f02')
    ]

    # 2. Chargement des series journalieres 2018
    f_lc = os.path.join(tbl_dir, "lalla_chafia_fluxes_2016_2020.csv")
    f_sj = os.path.join(tbl_dir, "sidi_jabeur_fluxes_2016_2020.csv")
    f_deh = os.path.join(tbl_dir, "dar_el_hamra_fluxes_daily_2018.csv")

    df_lc_18 = pd.read_csv(f_lc).set_index('date')
    df_sj_18 = pd.read_csv(f_sj).set_index('date')
    df_deh_18 = pd.read_csv(f_deh).set_index('date')

    df_lc_18 = df_lc_18[df_lc_18.index.str.startswith('2018')].copy()
    df_sj_18 = df_sj_18[df_sj_18.index.str.startswith('2018')].copy()
    df_deh_18 = df_deh_18[df_deh_18.index.str.startswith('2018')].copy()

    stations = []
    dfs_dict = {'b_l_chafia': df_lc_18, 'b_s_jabeur': df_sj_18, 'dar_el_hamra': df_deh_18}

    for st_id, name, basin, r, c, has_daily, color in station_meta:
        cat, cat_rows, cat_cols, cat_areas, tot_area_m2 = diag.get_catchment_cells(ldt_path, r, c)
        area_km2 = float(tot_area_m2 / 1e6)
        print(f"Bassin {name} ({st_id}) : {len(cat)} cellules LDT, superficie D8 = {area_km2:.2f} km2")
        stations.append({
            'id': st_id,
            'name': name,
            'basin': basin,
            'row': r,
            'col': c,
            'n_cells': len(cat),
            'area_km2': round(area_km2, 2),
            'df': dfs_dict[st_id],
            'has_daily_obs': has_daily,
            'color': color
        })

    events = [
        {
            'id': 'ev1_mar',
            'name': 'Mars 2018 (05–09 mars)',
            'short': '05–09 Mar 2018',
            'start': '2018-03-05',
            'end': '2018-03-09',
            'n_days': 5,
            'month': '2018-03'
        },
        {
            'id': 'ev2_apr',
            'name': 'Avril 2018 (23–27 avril)',
            'short': '23–27 Avr 2018',
            'start': '2018-04-23',
            'end': '2018-04-27',
            'n_days': 5,
            'month': '2018-04'
        },
        {
            'id': 'ev3a_nov_early',
            'name': 'Fin Oct – Debut Nov (28 oct – 03 nov)',
            'short': '28 Oct – 03 Nov 2018',
            'start': '2018-10-28',
            'end': '2018-11-03',
            'n_days': 7,
            'month': '2018-11'
        },
        {
            'id': 'ev3b_nov_late',
            'name': 'Mi-Fin Novembre (18–25 nov)',
            'short': '18–25 Nov 2018',
            'start': '2018-11-18',
            'end': '2018-11-25',
            'n_days': 8,
            'month': '2018-11'
        }
    ]

    # Contexte mensuel valide pour Dar El Hamra
    f_deh_m = os.path.join(tbl_dir, "dar_el_hamra_fluxes_monthly_2016_2020.csv")
    df_deh_m = pd.read_csv(f_deh_m).set_index('year_month')

    # Construction du tableau evenementiel
    records = []

    for ev in events:
        for st in stations:
            df = st['df']
            sub = df.loc[ev['start']:ev['end']]

            p_cum = float(sub['precip_mm_d'].sum())
            p_max = float(sub['precip_mm_d'].max())
            p_max_date = str(sub['precip_mm_d'].idxmax())

            qs_cum = float(sub['qs_mm_d'].sum())
            qs_max = float(sub['qs_mm_d'].max())
            qsb_cum = float(sub['qsb_mm_d'].sum())
            qtot_cum = qs_cum + qsb_cum

            qs_part = (qs_cum / p_cum * 100.0) if p_cum > 0 else 0.0
            qsb_part = (qsb_cum / p_cum * 100.0) if p_cum > 0 else 0.0
            ratio_mod = (qtot_cum / p_cum * 100.0) if p_cum > 0 else 0.0

            q_lr0_max = float(sub['q_sim_linres0_m3s'].max())
            q_lr0_max_date = str(sub['q_sim_linres0_m3s'].idxmax())
            q_h1_max = float(sub['q_sim_hist_m3s'].max())
            q_lr0_mean = float(sub['q_sim_linres0_m3s'].mean())

            # Lame d'eau simulee en mm sur la fenetre
            v_sim_mm = (q_lr0_mean * ev['n_days'] * 86400.0) / (st['area_km2'] * 1e6) * 1000.0

            if st['has_daily_obs']:
                q_obs_max = float(sub['q_obs_m3s'].max())
                q_obs_max_date = str(sub['q_obs_m3s'].idxmax())
                q_obs_mean = float(sub['q_obs_m3s'].mean())
                # Lame d'eau observee calculee avec la superficie D8 rigoureuse du LDT
                v_obs_mm = (q_obs_mean * ev['n_days'] * 86400.0) / (st['area_km2'] * 1e6) * 1000.0
                ratio_obs = (v_obs_mm / p_cum * 100.0) if p_cum > 0 else 0.0
                ratio_peak_obs_sim = (q_obs_max / q_lr0_max) if q_lr0_max > 0 else np.nan

                q_obs_pic_str = f"{q_obs_max:.1f} m³/s ({q_obs_max_date[5:]})"
                v_obs_str = f"{v_obs_mm:.1f} mm"
                ratio_obs_str = f"{ratio_obs:.1f}%"
                ratio_peaks_str = f"{ratio_peak_obs_sim:.2f}"
            else:
                # Dar El Hamra : observation journaliere inexistante
                q_obs_pic_str = "N/A (obs journaliere absente)"
                v_obs_str = "N/A"
                ratio_obs_str = "N/A"
                ratio_peaks_str = "N/A"

            records.append({
                'evenement': ev['name'],
                'fenetre': f"{ev['start']} au {ev['end']}",
                'bassin': st['basin'],
                'station': st['name'],
                'superficie_d8_km2': st['area_km2'],
                'precip_cum_mm': round(p_cum, 1),
                'precip_pic_mm_d': round(p_max, 1),
                'date_pic_precip': p_max_date,
                'qs_cum_mm': round(qs_cum, 2),
                'qs_part_precip_pct': round(qs_part, 1),
                'qsb_cum_mm': round(qsb_cum, 2),
                'qsb_part_precip_pct': round(qsb_part, 1),
                'qtot_cum_mm': round(qtot_cum, 2),
                'ratio_flux_qtot_p_pct': round(ratio_mod, 1),
                'q_sim_lr0_pic_m3s': round(q_lr0_max, 2),
                'date_pic_sim_lr0': q_lr0_max_date,
                'q_sim_h1_pic_m3s': round(q_h1_max, 2),
                'q_obs_pic': q_obs_pic_str,
                'lame_ecoulee_obs_mm': v_obs_str,
                'ratio_flux_qobs_p_pct': ratio_obs_str,
                'ratio_pic_obs_sur_sim': ratio_peaks_str
            })

    df_summary = pd.DataFrame(records)
    csv_out = os.path.join(tbl_dir, "events_2018_comparison_three_basins.csv")
    df_summary.to_csv(csv_out, index=False)
    print(f"[OK] Tableau synthétique exporte : {csv_out}")

    # =========================================================================
    # FIGURE COMPARATIVE ADAPTEE ET NEUTRE
    # =========================================================================
    print("Generation de la figure comparative multi-bassins des evenements 2018...")

    fig = plt.figure(figsize=(16, 12), constrained_layout=True)
    gs = fig.add_gridspec(3, 3)

    ev_cols = [
        ('Mars 2018', '2018-03-04', '2018-03-11', '06–08 Mars 2018'),
        ('Avril 2018', '2018-04-22', '2018-04-29', '24–26 Avril 2018'),
        ('Novembre 2018', '2018-10-27', '2018-11-26', 'Episodes 28 Oct – 25 Nov')
    ]

    for col_idx, (ev_title, d_start, d_end, ev_subtitle) in enumerate(ev_cols):
        sub_lc = df_lc_18.loc[d_start:d_end]
        sub_sj = df_sj_18.loc[d_start:d_end]
        sub_deh = df_deh_18.loc[d_start:d_end]

        dates = pd.to_datetime(sub_lc.index)
        w = 0.25
        x = np.arange(len(dates))

        # 1. Panneau Superieur : Hyetogramme (Pluie moyenne sur le bassin versant)
        ax_p = fig.add_subplot(gs[0, col_idx])
        ax_p.bar(x - w, sub_lc['precip_mm_d'].values, width=w, label=f"Lalla Chafia ({stations[0]['area_km2']:.0f} km²)", color='#1f77b4', alpha=0.85)
        ax_p.bar(x, sub_sj['precip_mm_d'].values, width=w, label=f"Sidi Jabeur ({stations[1]['area_km2']:.0f} km²)", color='#2ca02c', alpha=0.85)
        ax_p.bar(x + w, sub_deh['precip_mm_d'].values, width=w, label=f"Dar El Hamra ({stations[2]['area_km2']:.0f} km²)", color='#d95f02', alpha=0.85)

        ax_p.set_title(f"Evenement : {ev_title} ({ev_subtitle})", fontsize=11, fontweight='bold', pad=6)
        if col_idx == 0:
            ax_p.set_ylabel("Precipitation IMERG\n(mm/jour)", fontsize=10, fontweight='bold')
            ax_p.legend(loc='upper right', fontsize=8, framealpha=0.9)
        ax_p.set_xticks(x[::max(1, len(x)//8)])
        ax_p.set_xticklabels([dates[i].strftime('%d/%m') for i in x[::max(1, len(x)//8)]], rotation=30, ha='right', fontsize=8)
        ax_p.grid(True, linestyle=':', alpha=0.5)

        # 2. Panneau Central : Flux de ruissellement Noah-MP (Qs et Qsb) pour les 3 bassins
        ax_f = fig.add_subplot(gs[1, col_idx])
        # Lalla Chafia
        ax_f.plot(x, sub_lc['qs_mm_d'].values, color='#1f77b4', lw=1.8, ls='-', label='Qs - Lalla Chafia')
        ax_f.plot(x, sub_lc['qsb_mm_d'].values, color='#1f77b4', lw=1.6, ls='--', alpha=0.85, label='Qsb - Lalla Chafia')
        # Sidi Jabeur
        ax_f.plot(x, sub_sj['qs_mm_d'].values, color='#2ca02c', lw=1.8, ls='-', label='Qs - Sidi Jabeur')
        ax_f.plot(x, sub_sj['qsb_mm_d'].values, color='#2ca02c', lw=1.6, ls='--', alpha=0.85, label='Qsb - Sidi Jabeur')
        # Dar El Hamra
        ax_f.plot(x, sub_deh['qs_mm_d'].values, color='#d95f02', lw=1.8, ls='-', label='Qs - Dar El Hamra')
        ax_f.plot(x, sub_deh['qsb_mm_d'].values, color='#d95f02', lw=1.6, ls='--', alpha=0.85, label='Qsb - Dar El Hamra')

        if col_idx == 0:
            ax_f.set_ylabel("Flux de ruissellement\nNoah-MP (mm/jour)", fontsize=10, fontweight='bold')
            ax_f.legend(loc='upper right', fontsize=7.5, framealpha=0.9, ncol=3)
        ax_f.set_title("Production de Ruissellement Noah-MP (Qs : continu, Qsb : tirete)", fontsize=9.5, fontweight='semibold')
        ax_f.set_xticks(x[::max(1, len(x)//8)])
        ax_f.set_xticklabels([dates[i].strftime('%d/%m') for i in x[::max(1, len(x)//8)]], rotation=30, ha='right', fontsize=8)
        ax_f.grid(True, linestyle=':', alpha=0.5)

        # 3. Panneau Inferieur : Hydrogrammes a l'exutoire (Obs vs Sim)
        ax_q = fig.add_subplot(gs[2, col_idx])
        # Lalla Chafia
        ax_q.plot(x, sub_lc['q_obs_m3s'].values, color='#1f77b4', lw=1.8, ls=':', marker='o', ms=2.5, label='Obs Lalla Chafia')
        ax_q.plot(x, sub_lc['q_sim_linres0_m3s'].values, color='#1f77b4', lw=1.8, ls='-', label='Sim Lalla Chafia (lr0)')
        # Sidi Jabeur
        ax_q.plot(x, sub_sj['q_obs_m3s'].values, color='#2ca02c', lw=1.8, ls=':', marker='s', ms=2.5, label='Obs Sidi Jabeur')
        ax_q.plot(x, sub_sj['q_sim_linres0_m3s'].values, color='#2ca02c', lw=1.8, ls='-', label='Sim Sidi Jabeur (lr0)')
        # Dar El Hamra (Simulation seule au pas journalier)
        ax_q.plot(x, sub_deh['q_sim_linres0_m3s'].values, color='#d95f02', lw=1.8, ls='-', label='Sim Dar El Hamra (lr0)')

        if col_idx == 0:
            ax_q.set_ylabel("Debit a l'exutoire\n(m³/s)", fontsize=10, fontweight='bold')
            ax_q.legend(loc='upper right', fontsize=7.5, framealpha=0.9, ncol=2)
        ax_q.set_title("Reponse Hydrologique a l'Exutoire (Simule vs Observe)", fontsize=9.5, fontweight='semibold')
        ax_q.set_xticks(x[::max(1, len(x)//8)])
        ax_q.set_xticklabels([dates[i].strftime('%d/%m') for i in x[::max(1, len(x)//8)]], rotation=30, ha='right', fontsize=8)
        ax_q.grid(True, linestyle=':', alpha=0.5)

    fig.suptitle("Diagnostic Compare des Evenements de 2018 : Forcage IMERG, Flux Noah-MP (Qs, Qsb) et Debits Exutoire\n(Bassins versants amont : Lalla Chafia, Sidi Jabeur et Dar El Hamra)", fontsize=12.5, fontweight='bold')

    png_out = os.path.join(fig_dir, "events_2018_precip_runoff_response.png")
    pdf_out = os.path.join(fig_dir, "events_2018_precip_runoff_response.pdf")
    fig.savefig(png_out, dpi=300)
    fig.savefig(pdf_out)
    plt.close(fig)
    print(f"[OK] Figure mise a jour enregistree : {png_out}")
    print(f"[OK] Figure mise a jour enregistree : {pdf_out}")

    # Copie vers l'espace d'artefacts
    artifact_path = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e/events_2018_precip_runoff_response.png"
    import shutil
    shutil.copyfile(png_out, artifact_path)
    print(f"[OK] Copie vers artefacts : {artifact_path}")

if __name__ == '__main__':
    main()
