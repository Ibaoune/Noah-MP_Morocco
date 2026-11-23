#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fig_09.py
---------
Figure 9 : Évaluation des simulations de débit HyMAP-2 (linres=0) à Lalla Chafia et Sidi Jabeur en 2018.
Panels :
  (a) Hydrogrammes journaliers à Lalla Chafia (Sebou, 5 502 km²) en échelle semi-logarithmique,
      avec cartouche des métriques (KGE, NSE, NIC) généré dynamiquement depuis les CSV.
  (b) Hydrogrammes journaliers à Sidi Jabeur (Oum Er Rbia, 16 339 km²) en échelle semi-logarithmique,
      avec cartouche des métriques (KGE, NSE, NIC) généré dynamiquement depuis les CSV.

Expériences tracées :
  - Observé (In Situ)
  - OPL (Baseline)
  - OL_DAIC (Condition initiale DAIC)
  - ENS_OPL (Ensemble production)
  - ENS_corr (Ensemble corrigé)
  - DA_nocdf (Production sans CDF)
  - DA_cdf (Production CDF matching)
  - DA_corr (Assimilation corrigée)

Outputs :
  paper1/figures/fig_09.png (200 dpi)
  paper1/figures/fig_09_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
FIGURES_DIR = os.path.join(BASE_DIR, "paper1/figures")
os.makedirs(FIGURES_DIR, exist_ok=True)

DAILY_CSV = os.path.join(TABLES_DIR, "daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
METRICS_CSV = os.path.join(TABLES_DIR, "streamflow_metrics_corrected_2018.csv")
NIC_CSV = os.path.join(TABLES_DIR, "streamflow_nic_corrected_2018.csv")

OUT_FIG = os.path.join(FIGURES_DIR, "fig_09.png")
OUT_CSV = os.path.join(FIGURES_DIR, "fig_09_data.csv")

def format_metrics_box(df_m, df_nic, sid):
    # Filter for Annual daily metrics
    sub_m = df_m[(df_m['station_id'] == sid) & (df_m['timestep'] == 'journalier') & (df_m['season'] == 'Annual')].set_index('experiment')
    sub_nic = df_nic[(df_nic['station_id'] == sid) & (df_nic['timestep'] == 'journalier') & (df_nic['season'] == 'Annual')].set_index('pair')

    def get_kge_nse(exp):
        if exp in sub_m.index:
            r = sub_m.loc[exp]
            return f"KGE = {r['kge_2012']:+.3f}, NSE = {r['nse']:+.3f}"
        return "N/A"

    def get_nic(pair):
        if pair in sub_nic.index:
            r = sub_nic.loc[pair]
            return f"{r['nic']:+.3f} [{r['nic_ci95_low']:+.2f}, {r['nic_ci95_high']:+.2f}]"
        return "N/A"

    lines = [
        "Métriques d'évaluation (Journalier 2018) :",
        f"  • OPL :       {get_kge_nse('OPL')}",
        f"  • OL_DAIC :   {get_kge_nse('OL_DAIC')}",
        f"  • ENS_OPL :   {get_kge_nse('ENS_OPL')}",
        f"  • ENS_corr :  {get_kge_nse('ENS_corr')}",
        f"  • DA_cdf :    {get_kge_nse('DA_cdf')}",
        f"  • DA_nocdf :  {get_kge_nse('DA_nocdf')}",
        f"  • DA_corr :   {get_kge_nse('DA_corr')}",
        "  ────────────────────────",
        f"  • NIC (DA_corr vs ENS_corr) : {get_nic('DA_corr vs ENS_corr')}",
        f"  • NIC (ENS_corr vs OL_DAIC) : {get_nic('ENS_corr vs OL_DAIC')}",
        f"  • NIC (DA_nocdf vs ENS_OPL) : {get_nic('DA_nocdf vs ENS_OPL')}",
        f"  • NIC (ENS_OPL vs OL_DAIC)  : {get_nic('ENS_OPL vs OL_DAIC')}"
    ]
    return "\n".join(lines)

def main():
    print("=== GÉNÉRATION FIG. 09 : HYDROGRAMMES ET DÉBITS 2018 ===")
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_daily = pd.read_csv(DAILY_CSV)
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily.to_csv(OUT_CSV, index=False)
    print(f"[OK] Données tracées exportées dans : {OUT_CSV}")

    df_metrics = pd.read_csv(METRICS_CSV)
    df_nic = pd.read_csv(NIC_CSV)

    # ── 2. Setup Figure ────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(17, 12), sharex=True)
    fig.subplots_adjust(hspace=0.22, left=0.07, right=0.95, top=0.92, bottom=0.08)

    dates = df_daily['date'].to_numpy()

    # Color palette
    colors = {
        'obs': '#000000',
        'OPL': '#7F7F7F',           # Gris
        'OL_DAIC': '#56B4E9',       # Bleu clair
        'ENS_OPL': '#E69F00',       # Orange/ocre
        'ENS_corr': '#009E73',      # Vert
        'DA_nocdf': '#D55E00',      # Rouge vermillon
        'DA_cdf': '#CC79A7',        # Rose violacé
        'DA_corr': '#0072B2'        # Bleu foncé
    }

    # ── Panel (a): Lalla Chafia ────────────────────────────────────────────────
    ax1.plot(dates, df_daily['obs_lalla_chafia'].to_numpy(), color=colors['obs'], lw=2.4, label='Observed (In Situ)', zorder=10)
    ax1.plot(dates, df_daily['OPL_lalla_chafia'].to_numpy(), color=colors['OPL'], lw=1.3, ls=':', label='OPL (Baseline)')
    ax1.plot(dates, df_daily['OL_DAIC_lalla_chafia'].to_numpy(), color=colors['OL_DAIC'], lw=1.4, ls='-', label='OL-DAIC (Unperturbed)')
    ax1.plot(dates, df_daily['ENS_OPL_lalla_chafia'].to_numpy(), color=colors['ENS_OPL'], lw=1.6, ls='--', label='ENS-OPL (Production)')
    ax1.plot(dates, df_daily['ENS_corr_lalla_chafia'].to_numpy(), color=colors['ENS_corr'], lw=1.8, ls='-', label='ENS-corr (Corrigé)')
    ax1.plot(dates, df_daily['DA_cdf_lalla_chafia'].to_numpy(), color=colors['DA_cdf'], lw=1.6, ls='-.', label='DA-CDF (CDF matching)')
    ax1.plot(dates, df_daily['DA_nocdf_lalla_chafia'].to_numpy(), color=colors['DA_nocdf'], lw=1.8, ls='--', label='DA-NoCDF (Runoff surge)')
    ax1.plot(dates, df_daily['DA_corr_lalla_chafia'].to_numpy(), color=colors['DA_corr'], lw=2.0, ls='-', label='DA-corr (Corrigé)')

    ax1.set_yscale('log')
    ax1.set_ylim(0.04, 350)
    ax1.set_ylabel("Débit ($m^3/s$) [Échelle Log]", fontsize=11, fontweight='bold')
    ax1.set_title("(a) Sebou à Lalla Chafia (Bassin amont : 5 502 km²) — Hydrogrammes journaliers 2018",
                  fontsize=12, fontweight='bold', pad=8)
    ax1.grid(True, which='both', linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.2, ncol=4, framealpha=0.92)

    # Inset Text Box (Metrics loaded from CSV)
    box_a = format_metrics_box(df_metrics, df_nic, 'b_l_chafia')
    ax1.text(0.68, 0.95, box_a, transform=ax1.transAxes, fontsize=8.0,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F9FA', edgecolor='#CCCCCC', alpha=0.92))

    # ── Panel (b): Sidi Jabeur ─────────────────────────────────────────────────
    ax2.plot(dates, df_daily['obs_sidi_jabeur'].to_numpy(), color=colors['obs'], lw=2.4, label='Observed (In Situ)', zorder=10)
    ax2.plot(dates, df_daily['OPL_sidi_jabeur'].to_numpy(), color=colors['OPL'], lw=1.3, ls=':', label='OPL (Baseline)')
    ax2.plot(dates, df_daily['OL_DAIC_sidi_jabeur'].to_numpy(), color=colors['OL_DAIC'], lw=1.4, ls='-', label='OL-DAIC (Unperturbed)')
    ax2.plot(dates, df_daily['ENS_OPL_sidi_jabeur'].to_numpy(), color=colors['ENS_OPL'], lw=1.6, ls='--', label='ENS-OPL (Production)')
    ax2.plot(dates, df_daily['ENS_corr_sidi_jabeur'].to_numpy(), color=colors['ENS_corr'], lw=1.8, ls='-', label='ENS-corr (Corrigé)')
    ax2.plot(dates, df_daily['DA_cdf_sidi_jabeur'].to_numpy(), color=colors['DA_cdf'], lw=1.6, ls='-.', label='DA-CDF (CDF matching)')
    ax2.plot(dates, df_daily['DA_nocdf_sidi_jabeur'].to_numpy(), color=colors['DA_nocdf'], lw=1.8, ls='--', label='DA-NoCDF')
    ax2.plot(dates, df_daily['DA_corr_sidi_jabeur'].to_numpy(), color=colors['DA_corr'], lw=2.0, ls='-', label='DA-corr (Corrigé)')

    ax2.set_yscale('log')
    ax2.set_ylim(0.2, 500)
    ax2.set_ylabel("Débit ($m^3/s$) [Échelle Log]", fontsize=11, fontweight='bold')
    ax2.set_title("(b) Oum Er Rbia à Sidi Jabeur (Bassin amont : 16 339 km²) — Hydrogrammes journaliers 2018",
                  fontsize=12, fontweight='bold', pad=8)
    ax2.grid(True, which='both', linestyle=':', alpha=0.5)

    # Inset Text Box (Metrics loaded from CSV)
    box_b = format_metrics_box(df_metrics, df_nic, 'b_s_jabeur')
    ax2.text(0.68, 0.95, box_b, transform=ax2.transAxes, fontsize=8.0,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F9FA', edgecolor='#CCCCCC', alpha=0.92))

    # Format date axis
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
    ax2.set_xlabel("Mois de l'année 2018", fontsize=11, fontweight='bold')

    plt.suptitle("Figure 9 : Évaluation des Simulations de Débit HyMAP-2 (linres=0) — Impact de l'Ensemble et de la DA Corrigée",
                 fontsize=15, fontweight='bold', y=0.97)

    plt.savefig(OUT_FIG, dpi=200)
    plt.close()
    print(f"[OK] Figure 9 sauvegardée dans : {OUT_FIG}")

if __name__ == '__main__':
    main()
