#!/usr/bin/env python3
"""
fig_09.py
---------
Figure 9: Streamflow simulations under HyMAP-2 (linres=0) at Lalla Chafia and Sidi Jabeur (2018).
Panels:
  (a) Daily hydrograph at Lalla Chafia (Sebou, 5,502 km²) on logarithmic scale,
      with KGE and NIC insets (95% bootstrap CI).
  (b) Daily hydrograph at Sidi Jabeur (Oum Er Rbia, 16,339 km²) on logarithmic scale,
      with KGE and NIC insets (95% bootstrap CI).

Outputs:
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
DAILY_CSV = os.path.join(BASE_DIR, "paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
METRICS_CSV = os.path.join(BASE_DIR, "paper1/tables/streamflow_metrics.csv")
NIC_CSV = os.path.join(BASE_DIR, "paper1/tables/streamflow_nic.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_09.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_09_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_daily = pd.read_csv(DAILY_CSV)
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_daily.to_csv(OUT_CSV, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # ── 2. Setup Figure ────────────────────────────────────────────────────────
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 11), sharex=True)
    fig.subplots_adjust(hspace=0.22, left=0.07, right=0.95, top=0.92, bottom=0.08)
    
    dates = df_daily['date'].to_numpy()
    
    # Color standards:
    # Obs: Black
    # OPL: #1f77b4
    # OL_DAIC: #56B4E9
    # ENS_OPL: #009E73
    # DA_nocdf: #D55E00
    # DA_cdf: #CC79A7
    c_obs = '#000000'
    colors = {
        'OPL': '#1f77b4',
        'OL_DAIC': '#56B4E9',
        'ENS_OPL': '#009E73',
        'DA_nocdf': '#D55E00',
        'DA_cdf': '#CC79A7'
    }
    
    # ── Panel (a): Lalla Chafia ────────────────────────────────────────────────
    ax1.plot(dates, df_daily['obs_lalla_chafia'].to_numpy(), color=c_obs, lw=2.2, label='Observed (In Situ)', zorder=6)
    ax1.plot(dates, df_daily['OPL_lalla_chafia'].to_numpy(), color=colors['OPL'], lw=1.5, ls='-', label='OPL (Baseline)')
    ax1.plot(dates, df_daily['OL_DAIC_lalla_chafia'].to_numpy(), color=colors['OL_DAIC'], lw=1.5, ls='-', label='OL-DAIC (Unperturbed)')
    ax1.plot(dates, df_daily['ENS_OPL_lalla_chafia'].to_numpy(), color=colors['ENS_OPL'], lw=1.8, ls='-', label='ENS-OL (Ensemble Mean)')
    ax1.plot(dates, df_daily['DA_nocdf_lalla_chafia'].to_numpy(), color=colors['DA_nocdf'], lw=2.0, ls='--', label='DA-NoCDF (Runoff surge)')
    ax1.plot(dates, df_daily['DA_cdf_lalla_chafia'].to_numpy(), color=colors['DA_cdf'], lw=1.8, ls='-.', label='DA-CDF (Rescaled)')
    
    ax1.set_yscale('log')
    ax1.set_ylim(0.04, 300)
    ax1.set_ylabel("Streamflow ($m^3 / s$) [Log Scale]", fontsize=11)
    ax1.set_title("(a) Sebou at Lalla Chafia (Upstream Area: 5,502 km²) — Daily Hydrographs 2018", fontsize=12, fontweight='bold', pad=8)
    ax1.grid(True, which='both', linestyle=':', alpha=0.5)
    ax1.legend(loc='lower left', fontsize=8.5, ncol=3, framealpha=0.95)
    
    # Inset Text Box for Metrics
    inset_text_a = (
        "Evaluation Metrics (Annual 2018):\n"
        "  • OPL:      KGE = +0.125,  NSE = +0.169\n"
        "  • OL_DAIC:  KGE = +0.120,  NSE = +0.231\n"
        "  • ENS_OPL:  KGE = +0.014,  NSE = +0.174\n"
        "  • DA_cdf:   KGE = -0.022,  NSE = +0.200\n"
        "  • DA_nocdf: KGE = -1.795,  NSE = -2.339\n"
        "  ────────\n"
        "  • NIC (DA_nocdf vs ENS): -1.836 [-2.65, -1.02]\n"
        "  • NIC (ENS vs OL_DAIC):  -0.120 [-0.24, +0.00]"
    )
    ax1.text(0.72, 0.95, inset_text_a, transform=ax1.transAxes, fontsize=8.2,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F9FA', edgecolor='#CCCCCC', alpha=0.92))
             
    # ── Panel (b): Sidi Jabeur ─────────────────────────────────────────────────
    ax2.plot(dates, df_daily['obs_sidi_jabeur'].to_numpy(), color=c_obs, lw=2.2, label='Observed (In Situ)', zorder=6)
    ax2.plot(dates, df_daily['OPL_sidi_jabeur'].to_numpy(), color=colors['OPL'], lw=1.5, ls='-', label='OPL (Baseline)')
    ax2.plot(dates, df_daily['OL_DAIC_sidi_jabeur'].to_numpy(), color=colors['OL_DAIC'], lw=1.5, ls='-', label='OL-DAIC (Unperturbed)')
    ax2.plot(dates, df_daily['ENS_OPL_sidi_jabeur'].to_numpy(), color=colors['ENS_OPL'], lw=1.8, ls='-', label='ENS-OL (Ensemble Mean)')
    ax2.plot(dates, df_daily['DA_nocdf_sidi_jabeur'].to_numpy(), color=colors['DA_nocdf'], lw=2.0, ls='--', label='DA-NoCDF')
    ax2.plot(dates, df_daily['DA_cdf_sidi_jabeur'].to_numpy(), color=colors['DA_cdf'], lw=1.8, ls='-.', label='DA-CDF')
    
    ax2.set_yscale('log')
    ax2.set_ylim(0.2, 500)
    ax2.set_ylabel("Streamflow ($m^3 / s$) [Log Scale]", fontsize=11)
    ax2.set_title("(b) Oum Er Rbia at Sidi Jabeur (Upstream Area: 16,339 km²) — Daily Hydrographs 2018", fontsize=12, fontweight='bold', pad=8)
    ax2.grid(True, which='both', linestyle=':', alpha=0.5)
    
    # Inset Text Box for Metrics
    inset_text_b = (
        "Evaluation Metrics (Annual 2018):\n"
        "  • OPL:      KGE = -0.036,  NSE = +0.054\n"
        "  • OL_DAIC:  KGE = +0.059,  NSE = +0.131\n"
        "  • ENS_OPL:  KGE = +0.081,  NSE = +0.154\n"
        "  • DA_cdf:   KGE = +0.039,  NSE = +0.148\n"
        "  • DA_nocdf: KGE = -0.221,  NSE = +0.032\n"
        "  ────────\n"
        "  • NIC (DA_nocdf vs ENS): -0.329 [-0.64, -0.02]\n"
        "  • NIC (ENS vs OL_DAIC):  +0.024 [-0.00, +0.05]"
    )
    ax2.text(0.72, 0.95, inset_text_b, transform=ax2.transAxes, fontsize=8.2,
             verticalalignment='top', bbox=dict(boxstyle='round,pad=0.5', facecolor='#F8F9FA', edgecolor='#CCCCCC', alpha=0.92))
             
    # Date formatting
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    fig.autofmt_xdate(rotation=0, ha='center')
    
    fig.suptitle("Figure 9 — Daily Streamflow Hydrographs and KGE/NIC Performance under HyMAP-2 linres=0 (2018)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
