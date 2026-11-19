#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
generate_multistation_figures.py
Generates the complete set of publication-ready scientific figures (F1A, F1B, F2, F3, F4, F5, F6)
in English for the Noah-MP 4.0.1 / HyMAP-2 multi-station hydrological evaluation (2018).
Produces both high-resolution 300-DPI PNGs and vector PDFs.
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
import matplotlib.gridspec as gridspec
from matplotlib.ticker import AutoMinorLocator

REPO_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = os.path.join(REPO_ROOT, "experiments/NorthMor/opl_hydrology_sensitivity")
POSTPROC_DIR = os.path.join(SENS_DIR, "postproc")
ROUTING_DIR = os.path.join(SENS_DIR, "routing")
TABLES_DIR = os.path.join(POSTPROC_DIR, "tables")
FIG_DIR = os.path.join(POSTPROC_DIR, "multistation/figures")
FIG_MAIN_DIR = os.path.join(POSTPROC_DIR, "figures")
ARTIFACT_DIR = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/8bcb0dc0-2d9f-4159-9391-a47e04a3c44e"
LEGACY_ARTIFACT_DIR = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/f3772236-acd2-402d-bb10-a9a2613cf75f"

os.makedirs(FIG_DIR, exist_ok=True)
os.makedirs(FIG_MAIN_DIR, exist_ok=True)
os.makedirs(ARTIFACT_DIR, exist_ok=True)

# Data paths
STREAMFLOW_CSV = os.path.join(TABLES_DIR, "streamflow_all_stations_2018.csv")
FLUXES_DAILY_CSV = os.path.join(TABLES_DIR, "catchment_fluxes_multistation_daily_2018.csv")
METRICS_CSV = os.path.join(TABLES_DIR, "table_multistation_metrics_2018.csv")
LOWFLOWS_CSV = os.path.join(TABLES_DIR, "table_multistation_lowflows_2018.csv")
FLOODS_CSV = os.path.join(TABLES_DIR, "table_multistation_floods_2018.csv")
PRECIP_COMP_CSV = os.path.join(REPO_ROOT, "experiments/NorthMor/routing/plots/sebou_bouregreg/tables/daily_precip_comparison_2018.csv")
OBS_MONTHLY_CSV = os.path.join(REPO_ROOT, "data/streamflow_clean/obs_monthly.csv")

# Homogeneous color palette across all figures
SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM (Ref)", "#1f77b4", "-"),
    ("OL_R2_SIMTOP", "SIMTOP", "#ff7f0e", "-"),
    ("OL_R3_SCHAAKE96", "Schaake96", "#2ca02c", "-"),
    ("OL_R4_BATS", "BATS", "#9467bd", "-")
]

COLOR_OBS = "#111111"
COLOR_PRECIP = "#4292c6"

# Matplotlib global parameters
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['axes.edgecolor'] = '#333333'
plt.rcParams['axes.linewidth'] = 0.8
plt.rcParams['xtick.direction'] = 'out'
plt.rcParams['ytick.direction'] = 'out'

def save_fig(fig, base_name):
    """Saves figure in both PNG (300 DPI) and vector PDF to multi-station, main figures, and artifact directories."""
    for ext in [".png", ".pdf"]:
        p_multi = os.path.join(FIG_DIR, base_name + ext)
        p_main = os.path.join(FIG_MAIN_DIR, base_name + ext)
        p_art = os.path.join(ARTIFACT_DIR, base_name + ext)

        dpi_val = 300 if ext == ".png" else None
        fig.savefig(p_multi, dpi=dpi_val, bbox_inches='tight')
        fig.savefig(p_main, dpi=dpi_val, bbox_inches='tight')
        if os.path.exists(ARTIFACT_DIR):
            fig.savefig(p_art, dpi=dpi_val, bbox_inches='tight')
        p_leg = os.path.join(LEGACY_ARTIFACT_DIR, base_name + ext)
        if os.path.exists(LEGACY_ARTIFACT_DIR):
            try:
                fig.savefig(p_leg, dpi=dpi_val, bbox_inches='tight')
            except Exception:
                pass
    print(f"  -> Saved: {base_name}.png and .pdf")
    plt.close(fig)

# =============================================================================
# F1A — Daily Streamflow Hydrographs (Bouregreg Basin)
# =============================================================================
def plot_f1a(df_q):
    print("Generating F1A — Daily streamflow hydrographs (Bouregreg Basin)...")
    df_q['date_dt'] = pd.to_datetime(df_q['date'])

    fig, axes = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
    stations_bouregreg = [
        ('b_l_chafia', '(a) Lalla Chafia — Upper Bouregreg (3,333 km²)', 335.0),
        ('b_s_jabeur', '(b) Sidi Jabeur — Oued Grou (3,131 km²)', 395.0),
        ('b_a_loudah', '(c) Ain Loudah — Tiflet Sub-basin (696 km²)*', 35.0),
        ('b_s_cherif', '(d) S.M. Cherif — Cherif Sub-basin (648 km²)*', 68.0)
    ]

    for ax, (sid, st_name, y_lim_max) in zip(axes, stations_bouregreg):
        sub = df_q[df_q['station_id'] == sid].sort_values('date_dt')

        # Observed discharge
        ax.plot(sub['date_dt'].values, sub['q_obs_m3s'].values, color=COLOR_OBS, lw=2.2, label='ABH Observed', zorder=5)

        # Simulated discharges
        for exp_id, label, color, ls in SCHEMES:
            ax.plot(sub['date_dt'].values, sub[f'q_sim_{exp_id}'].values, color=color, lw=1.3, ls=ls, label=label, alpha=0.9, zorder=3)

        ax.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
        ax.set_title(st_name, fontsize=10.5, fontweight='bold', loc='left', pad=4)
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.set_ylim(0, y_lim_max)
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    axes[3].set_xlabel('Date (2018)', fontsize=10.5, fontweight='bold', labelpad=6)
    axes[3].xaxis.set_major_locator(mdates.MonthLocator())
    axes[3].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    axes[3].set_xlim(pd.to_datetime('2018-01-01'), pd.to_datetime('2018-12-31'))

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=5, frameon=True, framealpha=0.95, fontsize=10)

    fig.text(0.08, 0.015,
             '* Note: Recorded streamflow at Ain Loudah and S.M. Cherif in 2018 are identical duplicate records in the ABH database (r = 1.000); both sub-basins are retained with caveats.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F1A — Daily Streamflow Hydrographs : Bouregreg Basin (2018)', fontsize=13, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.94, bottom=0.065, hspace=0.24)
    save_fig(fig, "f1a_hydrographs_bouregreg_daily_2018_en")

# =============================================================================
# F1B — Monthly Streamflow Hydrographs (Sebou Basin Continuum)
# =============================================================================
def plot_f1b(df_q):
    print("Generating F1B — Monthly streamflow hydrographs (Sebou Basin Continuum)...")
    df_obs_m = pd.read_csv(OBS_MONTHLY_CSV)
    sub_obs_2018 = df_obs_m[df_obs_m['annee'] == 2018]

    df_q['date_dt'] = pd.to_datetime(df_q['date'])
    df_q['month'] = df_q['date_dt'].dt.month

    st_sebou = [
        ('ain_timedrine', '(a) Ain Timedrine (4,387 km²)', 30.0),
        ('azzaba', '(b) Azzaba (4,640 km²)', 48.0),
        ('pont_de_mdez', '(c) Pont de Mdez (3,425 km²)', 18.0),
        ('ait_khabbach', '(d) Ait Khabbach (1,240 km²)*', 4.6),
        ('dar_el_hamra', '(e) Dar El Hamra (670 km²)', 14.0),
        ('pont_ait_aissa', '(f) Pont Ait Aissa (205 km²)**', 1.65)
    ]

    fig, axes = plt.subplots(3, 2, figsize=(16, 12.5), sharex=True)
    axes = axes.flatten()
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    for ax, (sid, st_name, y_lim_max) in zip(axes, st_sebou):
        obs_st = sub_obs_2018[sub_obs_2018['station_id'] == sid].sort_values('mois')
        ax.plot(obs_st['mois'].values, obs_st['q_m3s'].values,
                color=COLOR_OBS, lw=2.2, marker='o', ms=4.5, label='ABH Observed (Monthly)', zorder=5)

        sub_q_st = df_q[df_q['station_id'] == sid]
        for exp_id, label, color, ls in SCHEMES:
            m_sim = sub_q_st.groupby('month')[f'q_sim_{exp_id}'].mean()
            ax.plot(m_sim.index.values, m_sim.values,
                    color=color, lw=1.4, ls=ls, marker='s', ms=3.5, label=label, alpha=0.9, zorder=3)

        ax.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
        ax.set_title(st_name, fontsize=10.5, fontweight='bold', loc='left', pad=4)
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.set_xticks(months)
        ax.set_xticklabels(month_names)
        ax.set_ylim(0, y_lim_max)
        ax.yaxis.set_minor_locator(AutoMinorLocator(2))

    axes[4].set_xlabel('Month (2018)', fontsize=10, fontweight='bold', labelpad=6)
    axes[5].set_xlabel('Month (2018)', fontsize=10, fontweight='bold', labelpad=6)

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=5, frameon=True, framealpha=0.95, fontsize=10)

    fig.text(0.08, 0.015,
             '* Ait Khabbach is influenced by seasonal agricultural groundwater pumping in the Guigou plain and karstic recharge.\n'
             '** Pont Ait Aissa has high grid-scale area discrepancy (+23.8%) due to small basin size.\n'
             'Note: Stations form a hydrologically nested continuum: Pont Ait Aissa ⊂ Ait Khabbach ⊂ Pont de Mdez ⊂ Ain Timedrine ⊂ Azzaba.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F1B — Monthly Streamflow Hydrographs : Sebou Basin Continuum (2018)', fontsize=13, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.94, bottom=0.085, hspace=0.25, wspace=0.18)
    save_fig(fig, "f1b_hydrographs_sebou_monthly_2018_en")

# =============================================================================
# F2 — Precipitation and Flood Event Response
# =============================================================================
def plot_f2(df_q, df_flux):
    print("Generating F2 — Precipitation and flood event response...")
    df_q['date_dt'] = pd.to_datetime(df_q['date'])
    df_flux['date_dt'] = pd.to_datetime(df_flux['date'])
    df_precip_comp = pd.read_csv(PRECIP_COMP_CSV)
    df_precip_comp['date_dt'] = pd.to_datetime(df_precip_comp['date'])

    fig, axes = plt.subplots(2, 2, figsize=(16, 11.5))

    # Helper function for event panels
    def plot_event_panel(ax, sid, d_start, d_end, title, q_ylim_max, p_ylim_max):
        sub_q = df_q[(df_q['station_id'] == sid) & (df_q['date_dt'] >= d_start) & (df_q['date_dt'] <= d_end)]
        sub_p = df_flux[(df_flux['station_id'] == sid) & (df_flux['experiment'] == 'OL_R1_SIMGM') & (df_flux['date_dt'] >= d_start) & (df_flux['date_dt'] <= d_end)]

        ax_p = ax.twinx()
        ax_p.bar(sub_p['date_dt'].values, sub_p['P_mm_day'].values, color=COLOR_PRECIP, alpha=0.35, width=0.6, label='Catchment Precip. (IMERG)', zorder=1)
        ax_p.set_ylabel('Precipitation (mm/day)', color='#08519c', fontsize=9, fontweight='bold')
        ax_p.set_ylim(0, p_ylim_max)
        ax_p.invert_yaxis()
        ax_p.grid(False)

        ax.plot(sub_q['date_dt'].values, sub_q['q_obs_m3s'].values, color=COLOR_OBS, lw=2.2, marker='o', ms=3.5, label='ABH Observed', zorder=5)
        for exp_id, label, color, ls in SCHEMES:
            ax.plot(sub_q['date_dt'].values, sub_q[f'q_sim_{exp_id}'].values, color=color, lw=1.4, ls=ls, label=label, zorder=4)

        ax.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
        ax.set_title(title, fontsize=10.5, fontweight='bold', loc='left', pad=4)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.set_ylim(0, q_ylim_max)
        ax.set_zorder(ax_p.get_zorder() + 1)
        ax.patch.set_visible(False)
        return ax, ax_p

    # Panel A: March 2018 Flood — Lalla Chafia
    ax1, ax1_p = plot_event_panel(axes[0, 0], 'b_l_chafia', '2018-03-01', '2018-03-20', '(a) March 2018 Flood Event — Lalla Chafia (Bouregreg)', q_ylim_max=340.0, p_ylim_max=125.0)

    # Panel B: March 2018 Flash Flood — Sidi Jabeur
    ax2, ax2_p = plot_event_panel(axes[0, 1], 'b_s_jabeur', '2018-03-01', '2018-03-20', '(b) March 2018 Flash Flood Event — Sidi Jabeur (Grou)', q_ylim_max=400.0, p_ylim_max=125.0)

    # Panel C: November 2018 Flood — Lalla Chafia
    ax3, ax3_p = plot_event_panel(axes[1, 0], 'b_l_chafia', '2018-11-15', '2018-11-30', '(c) November 2018 Flood Event — Lalla Chafia (Bouregreg)', q_ylim_max=56.0, p_ylim_max=95.0)

    # Panel D: Precipitation Products Comparison
    ax4 = axes[1, 1]
    sub_pc = df_precip_comp[(df_precip_comp['basin_id'] == 'b_l_chafia') & (df_precip_comp['date_dt'] >= '2018-03-01') & (df_precip_comp['date_dt'] <= '2018-03-20')]
    w = 0.25
    ax4.bar((sub_pc['date_dt'] - pd.Timedelta(days=0.25)).values, sub_pc['precip_imerg_mm_d'].values, width=w, color='#1f77b4', label='IMERG V07B (Forcing used)', alpha=0.85)
    ax4.bar(sub_pc['date_dt'].values, sub_pc['precip_mswep_mm_d'].values, width=w, color='#2ca02c', label='MSWEP v2.8', alpha=0.85)
    ax4.bar((sub_pc['date_dt'] + pd.Timedelta(days=0.25)).values, sub_pc['precip_era5_mm_d'].values, width=w, color='#ff7f0e', label='ERA5-Land', alpha=0.85)
    ax4.set_ylabel('Catchment Precipitation (mm/day)', fontsize=9.5, fontweight='bold')
    ax4.set_title('(d) Multi-Source Precipitation Comparison — Lalla Chafia (01–20 March 2018)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax4.grid(axis='y', linestyle=':', alpha=0.5)
    ax4.set_ylim(0, 48.0)
    ax4.legend(loc='upper right', fontsize=8.5, frameon=True, framealpha=0.9)

    # Common legend for streamflow and precip
    handles_q, labels_q = ax1.get_legend_handles_labels()
    handles_p, labels_p = ax1_p.get_legend_handles_labels()
    all_handles = handles_q + handles_p
    all_labels = labels_q + labels_p
    fig.legend(all_handles, all_labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=6, frameon=True, framealpha=0.95, fontsize=9.5)

    fig.text(0.08, 0.015,
             'Note: Precipitation comparisons represent catchment-averaged consistency diagnostics across satellite and reanalysis products, not in-situ gauge validation.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F2 — Precipitation Forcing and Flood Event Hydrodynamics (2018)', fontsize=13, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.94, bottom=0.065, hspace=0.24, wspace=0.20)
    save_fig(fig, "f2_precip_and_flood_response_2018_en")

# =============================================================================
# F3 — Daily Precipitation, Qs, Qsb and Routed Discharge
# =============================================================================
def plot_f3(df_flux, df_q):
    print("Generating F3 — Daily precipitation, Qs, Qsb and routed discharge...")
    df_flux['date_dt'] = pd.to_datetime(df_flux['date'])
    df_q['date_dt'] = pd.to_datetime(df_q['date'])

    fig, axes = plt.subplots(4, 2, figsize=(16, 14), sharex=True)

    # Column titles
    axes[0, 0].set_title('Lalla Chafia — Upper Bouregreg (3,333 km²)', fontsize=11.5, fontweight='bold', pad=12)
    axes[0, 1].set_title('Sidi Jabeur — Oued Grou (3,131 km²)', fontsize=11.5, fontweight='bold', pad=12)

    # 1. Row 1: Precipitation (IMERG V07B)
    for col_idx, sid in enumerate(['b_l_chafia', 'b_s_jabeur']):
        ax = axes[0, col_idx]
        sub_p = df_flux[(df_flux['station_id'] == sid) & (df_flux['experiment'] == 'OL_R1_SIMGM')].sort_values('date_dt')
        ax.bar(sub_p['date_dt'].values, sub_p['P_mm_day'].values, color=COLOR_PRECIP, width=0.8, alpha=0.75)
        ax.set_ylabel('Precipitation (mm/day)', fontsize=9, fontweight='bold')
        ax.set_ylim(0, 70.0)
        ax.invert_yaxis()
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.text(0.02, 0.12, 'Daily Precipitation (IMERG)', transform=ax.transAxes, fontsize=8.5, fontweight='bold', color='#08519c')

    # 2. Row 2: Surface Runoff Qs (Noah-MP)
    for col_idx, sid in enumerate(['b_l_chafia', 'b_s_jabeur']):
        ax = axes[1, col_idx]
        for exp_id, label, color, ls in SCHEMES:
            sub_f = df_flux[(df_flux['station_id'] == sid) & (df_flux['experiment'] == exp_id)].sort_values('date_dt')
            ax.plot(sub_f['date_dt'].values, sub_f['Qs_mm_day'].values, color=color, lw=1.2, ls=ls, label=label, alpha=0.9)
        ax.set_ylabel('Surface Runoff Qs (mm/day)', fontsize=9, fontweight='bold')
        ax.set_ylim(0, 15.0)  # Shared scale ensures direct physical comparability
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.text(0.02, 0.88, 'Surface Runoff (Qs Noah-MP)', transform=ax.transAxes, fontsize=8.5, fontweight='bold', color='#333333')

    # 3. Row 3: Subsurface Drainage Qsb (Noah-MP)
    for col_idx, (sid, y_lim_qsb) in enumerate([('b_l_chafia', 1.65), ('b_s_jabeur', 0.55)]):
        ax = axes[2, col_idx]
        for exp_id, label, color, ls in SCHEMES:
            sub_f = df_flux[(df_flux['station_id'] == sid) & (df_flux['experiment'] == exp_id)].sort_values('date_dt')
            ax.plot(sub_f['date_dt'].values, sub_f['Qsb_mm_day'].values, color=color, lw=1.3, ls=ls, label=label, alpha=0.9)
        ax.set_ylabel('Drainage Qsb (mm/day)', fontsize=9, fontweight='bold')
        ax.set_ylim(0, y_lim_qsb)
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.text(0.02, 0.88, 'Deep Subsurface Drainage (Qsb Noah-MP)', transform=ax.transAxes, fontsize=8.5, fontweight='bold', color='#333333')

    # 4. Row 4: Routed Discharge (HyMAP-2) vs Observed
    for col_idx, (sid, y_lim_q) in enumerate([('b_l_chafia', 335.0), ('b_s_jabeur', 395.0)]):
        ax = axes[3, col_idx]
        sub_q = df_q[df_q['station_id'] == sid].sort_values('date_dt')
        ax.plot(sub_q['date_dt'].values, sub_q['q_obs_m3s'].values, color=COLOR_OBS, lw=2.2, label='ABH Observed', zorder=5)
        for exp_id, label, color, ls in SCHEMES:
            ax.plot(sub_q['date_dt'].values, sub_q[f'q_sim_{exp_id}'].values, color=color, lw=1.3, ls=ls, label=label, alpha=0.9, zorder=3)
        ax.set_ylabel('Routed Discharge (m³/s)', fontsize=9, fontweight='bold')
        ax.set_ylim(0, y_lim_q)
        ax.grid(axis='y', linestyle=':', alpha=0.5)
        ax.text(0.02, 0.88, 'Routed Streamflow (HyMAP-2 vs Observed)', transform=ax.transAxes, fontsize=8.5, fontweight='bold', color='#333333')
        ax.set_xlabel('Date (2018)', fontsize=10, fontweight='bold', labelpad=6)
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        ax.set_xlim(pd.to_datetime('2018-01-01'), pd.to_datetime('2018-12-31'))

    handles, labels = axes[3, 0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=5, frameon=True, framealpha=0.95, fontsize=10)

    fig.text(0.08, 0.015,
             'Note: Noah-MP subsurface drainage Qsb represents deep soil drainage into the unconfined aquifer / baseflow reservoir; it is an internal land-surface flux and not an in-situ streamflow measurement.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F3 — Daily Catchment Fluxes (Precipitation, Qs, Qsb) and Routed Discharge (2018)', fontsize=13, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.935, bottom=0.065, hspace=0.22, wspace=0.18)
    save_fig(fig, "f3_daily_qs_qsb_hydrographs_2018_en")

# =============================================================================
# F4 — Summer Low-flow and Intermittency Diagnostic
# =============================================================================
def plot_f4(df_q, df_low=None):
    print("Generating F4 — Summer Streamflow and Zero-Flow Occurrence (June–September 2018)...")
    df_q['date_dt'] = pd.to_datetime(df_q['date'])
    sub_sum = df_q[(df_q['date_dt'] >= '2018-06-01') & (df_q['date_dt'] <= '2018-09-30')].copy()

    fig = plt.figure(figsize=(15, 9.2))
    gs = fig.add_gridspec(2, 2, height_ratios=[2.3, 1.05], hspace=0.32, wspace=0.18)

    # -------------------------------------------------------------------------
    # Panel A: Sidi Jabeur (Broken Y-axis)
    # -------------------------------------------------------------------------
    gs_a = gs[0, 0].subgridspec(2, 1, height_ratios=[1, 3.2], hspace=0.08)
    ax_top = fig.add_subplot(gs_a[0])
    ax_bot = fig.add_subplot(gs_a[1], sharex=ax_top)

    sub_sj = sub_sum[sub_sum['station_id'] == 'b_s_jabeur'].sort_values('date_dt')

    for ax_cur in [ax_top, ax_bot]:
        ax_cur.plot(sub_sj['date_dt'].values, sub_sj['q_obs_m3s'].values,
                    color=COLOR_OBS, lw=2.0, label='Observed (ABH)', zorder=5)
        for exp_id, label, color, ls in SCHEMES:
            ax_cur.plot(sub_sj['date_dt'].values, sub_sj[f'q_sim_{exp_id}'].values,
                        color=color, lw=1.35, ls=ls, label=label, alpha=0.9, zorder=3)
        ax_cur.grid(axis='y', linestyle=':', alpha=0.5)

    # Spines and broken axis limits
    ax_top.set_ylim(8.0, 62.0)
    ax_top.set_yticks([20, 40, 60])
    ax_bot.set_ylim(-0.15, 7.5)
    ax_bot.set_yticks([0, 1, 2, 3, 4, 5, 6, 7])
    ax_top.spines['bottom'].set_visible(False)
    ax_bot.spines['top'].set_visible(False)
    ax_top.tick_params(bottom=False, labelbottom=False)

    # Broken axis diagonal cut marks
    d = 0.5
    kwargs = dict(marker=[(-1, -d), (1, d)], markersize=9, linestyle="none", color='k', mec='k', mew=1, clip_on=False)
    ax_top.plot([0, 1], [0, 0], transform=ax_top.transAxes, **kwargs)
    ax_bot.plot([0, 1], [1, 1], transform=ax_bot.transAxes, **kwargs)

    ax_top.set_title('(a) Sidi Jabeur (Oued Grou)', fontsize=11, fontweight='bold', loc='left', pad=6)
    ax_bot.set_ylabel('Streamflow (m³/s)', fontsize=10, fontweight='bold')
    ax_bot.yaxis.set_label_coords(-0.09, 0.65)
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    # Annotate peak on upper axis: placed with ample clearance in whitespace to the left
    ax_top.annotate('Observed peak: 50.1 m³/s (17 Sep)',
                    xy=(pd.to_datetime('2018-09-17'), 50.1),
                    xytext=(-175, -28), textcoords='offset points',
                    arrowprops=dict(arrowstyle="->", color='#333333', lw=1.0),
                    fontsize=8.5, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="#888888", lw=0.8, alpha=0.95))

    # Discreet signaling of the 47 consecutive zero-flow days
    d_start = pd.to_datetime('2018-07-18')
    d_end = pd.to_datetime('2018-09-02')

    # Subtle shaded vertical band for the zero-flow window
    ax_bot.axvspan(d_start, d_end, color='#f2f4f7', alpha=0.85, zorder=1)

    # Discreet callout in the clear space below simulated curves (Schaake96 is >= 1.2 m3/s)
    ax_bot.annotate('Observed zero flow: 18 Jul – 2 Sep\n(47 consecutive days)',
                    xy=(pd.to_datetime('2018-08-10'), 0.0),
                    xytext=(pd.to_datetime('2018-08-10'), 0.62),
                    ha='center', va='center',
                    arrowprops=dict(arrowstyle="->", color='#444444', lw=0.9),
                    fontsize=8, fontweight='bold', color='#222222',
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="#7f8c8d", lw=0.8, alpha=0.95),
                    zorder=7)

    # -------------------------------------------------------------------------
    # Panel B: Lalla Chafia
    # -------------------------------------------------------------------------
    ax_b = fig.add_subplot(gs[0, 1])
    sub_lc = sub_sum[sub_sum['station_id'] == 'b_l_chafia'].sort_values('date_dt')

    ax_b.plot(sub_lc['date_dt'].values, sub_lc['q_obs_m3s'].values,
              color=COLOR_OBS, lw=2.0, label='Observed (ABH)', zorder=5)
    for exp_id, label, color, ls in SCHEMES:
        ax_b.plot(sub_lc['date_dt'].values, sub_lc[f'q_sim_{exp_id}'].values,
                  color=color, lw=1.35, ls=ls, label=label, alpha=0.9, zorder=3)

    ax_b.set_ylabel('Streamflow (m³/s)', fontsize=10, fontweight='bold')
    ax_b.set_title('(b) Lalla Chafia (Upper Bouregreg)', fontsize=11, fontweight='bold', loc='left', pad=6)
    ax_b.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    ax_b.grid(axis='y', linestyle=':', alpha=0.5)
    ax_b.set_ylim(-0.15, 14.5)

    # -------------------------------------------------------------------------
    # Global Legend (Top)
    # -------------------------------------------------------------------------
    handles_a, labels_a = ax_b.get_legend_handles_labels()
    fig.legend(handles_a, labels_a, loc='upper center', bbox_to_anchor=(0.5, 0.985),
               ncol=5, frameon=True, framealpha=0.95, fontsize=9.5)

    # -------------------------------------------------------------------------
    # Bottom Tables: Sidi Jabeur (left) & Lalla Chafia (right)
    # -------------------------------------------------------------------------
    def create_summary_table(ax_tbl, sub_st, st_title):
        ax_tbl.axis('off')

        col_labels = ['Series', 'Days with\nQ = 0 m³/s', 'Days with\nQ ≤ 0.1 m³/s', 'Median streamflow\n(Q50) [m³/s]']

        rows = []
        # Observed
        q_obs = sub_st['q_obs_m3s'].values
        d_zero_obs = int(np.sum(q_obs == 0))
        d_01_obs = int(np.sum(q_obs <= 0.1))
        med_obs = np.median(q_obs)
        rows.append(['Observed (ABH)', f"{d_zero_obs}", f"{d_01_obs}", f"{med_obs:.2f}"])

        # Schemes
        for exp_id, label, _, _ in SCHEMES:
            q_sim = sub_st[f'q_sim_{exp_id}'].values
            d_zero_sim = int(np.sum(q_sim == 0))
            d_01_sim = int(np.sum(q_sim <= 0.1))
            med_sim = np.median(q_sim)
            rows.append([label, f"{d_zero_sim}", f"{d_01_sim}", f"{med_sim:.2f}"])

        table = ax_tbl.table(cellText=rows, colLabels=col_labels, loc='center', cellLoc='center',
                             colWidths=[0.28, 0.22, 0.22, 0.28])
        table.auto_set_font_size(False)
        table.set_fontsize(8.5)
        table.scale(1.0, 1.45)

        # Style header and rows
        for (r, c), cell in table.get_celld().items():
            cell.set_edgecolor('#d0d0d0')
            if r == 0:
                cell.set_facecolor('#eaecef')
                cell.set_text_props(weight='bold', color='#111111')
            else:
                if c == 0:
                    cell.set_text_props(weight='bold' if r == 1 else 'normal', ha='left')
                    cell.set_facecolor('#f8f9fa' if r == 1 else '#ffffff')
                else:
                    cell.set_text_props(weight='bold' if r == 1 else 'normal')
                    cell.set_facecolor('#f8f9fa' if r == 1 else '#ffffff')

        ax_tbl.set_title(st_title, fontsize=10, fontweight='bold', pad=8, loc='center')

    ax_tbl_sj = fig.add_subplot(gs[1, 0])
    create_summary_table(ax_tbl_sj, sub_sj, 'Summary Metrics — Sidi Jabeur (June–September 2018, 122 days)')

    ax_tbl_lc = fig.add_subplot(gs[1, 1])
    create_summary_table(ax_tbl_lc, sub_lc, 'Summary Metrics — Lalla Chafia (June–September 2018, 122 days)')

    fig.suptitle('F4 — Summer Streamflow and Zero-Flow Occurrence (June–September 2018)',
                 fontsize=12.5, fontweight='bold', y=1.015)

    save_fig(fig, "f4_lowflow_diagnostic_summer2018_en")

# =============================================================================
# F5 — Temporal Continuity and Transition Checks
# =============================================================================
def plot_f5(df_q):
    print("Generating F5 — Temporal continuity and transition checks...")
    df_q['date_dt'] = pd.to_datetime(df_q['date'])

    fig, axes = plt.subplots(3, 1, figsize=(15, 12))

    # Panel A: Transition 2017 -> 2018 at Lalla Chafia
    ax1 = axes[0]
    sub1 = df_q[(df_q['station_id'] == 'b_l_chafia') & (df_q['date_dt'] >= '2017-11-01') & (df_q['date_dt'] <= '2018-02-01')].sort_values('date_dt')
    for exp_id, label, color, ls in SCHEMES:
        ax1.plot(sub1['date_dt'].values, sub1[f'q_sim_{exp_id}'].values, color=color, lw=1.4, ls=ls, label=label, alpha=0.9)
    line_bnd = ax1.axvline(pd.to_datetime('2017-12-31'), color='#d95f02', ls='--', lw=1.3, label='Year Boundary (31 Dec 2017)')
    ax1.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
    ax1.set_title('(a) Temporal Continuity Across 2017–2018 Year Boundary — Lalla Chafia (Bouregreg)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax1.grid(axis='y', linestyle=':', alpha=0.5)
    ax1.set_ylim(0, 78.0)

    # Panel B: Recession Continuity at End of 2018 at Lalla Chafia
    ax2 = axes[1]
    sub2 = df_q[(df_q['station_id'] == 'b_l_chafia') & (df_q['date_dt'] >= '2018-11-01') & (df_q['date_dt'] <= '2018-12-31')].sort_values('date_dt')
    for exp_id, label, color, ls in SCHEMES:
        ax2.plot(sub2['date_dt'].values, sub2[f'q_sim_{exp_id}'].values, color=color, lw=1.4, ls=ls, label=label, alpha=0.9)
    ax2.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
    ax2.set_title('(b) Streamflow Recession Continuity at End of 2018 — Lalla Chafia (Bouregreg)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax2.grid(axis='y', linestyle=':', alpha=0.5)
    ax2.set_ylim(0, 75.0)
    ax2.text(0.98, 0.88, 'Smooth baseflow stabilization (~3.8 m³/s) with no abrupt drop to zero', transform=ax2.transAxes,
             fontsize=8.5, ha='right', style='italic', color='#1b7837', bbox=dict(boxstyle="round,pad=0.25", fc="#f7fcf5", ec="#1b7837", lw=0.8))

    # Panel C: Transition 2017 -> 2018 at Sidi Jabeur
    ax3 = axes[2]
    sub3 = df_q[(df_q['station_id'] == 'b_s_jabeur') & (df_q['date_dt'] >= '2017-11-01') & (df_q['date_dt'] <= '2018-02-01')].sort_values('date_dt')
    for exp_id, label, color, ls in SCHEMES:
        ax3.plot(sub3['date_dt'].values, sub3[f'q_sim_{exp_id}'].values, color=color, lw=1.4, ls=ls, label=label, alpha=0.9)
    ax3.axvline(pd.to_datetime('2017-12-31'), color='#d95f02', ls='--', lw=1.3)
    ax3.set_ylabel('Streamflow (m³/s)', fontsize=9.5, fontweight='bold')
    ax3.set_title('(c) Temporal Continuity Across 2017–2018 Year Boundary — Sidi Jabeur (Oued Grou)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax3.set_xlabel('Simulation Date', fontsize=10, fontweight='bold', labelpad=6)
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%d %b %Y'))
    ax3.grid(axis='y', linestyle=':', alpha=0.5)
    ax3.set_ylim(0, 66.0)

    # Global legend at top
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=5, frameon=True, framealpha=0.95, fontsize=10)

    fig.text(0.08, 0.015,
             'Note: Verified temporal continuity across 2017–2018 confirms absence of restart or remapping discontinuities in production simulations. The legacy single-day artifact was retrospectively linked to prototype test scripts.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F5 — Verification of Temporal Continuity and Absence of Simulation Discontinuities (2017–2018)', fontsize=13, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.94, bottom=0.065, hspace=0.26)
    save_fig(fig, "f5_discontinuity_and_continuity_check_en")

# =============================================================================
# F6 — Multi-Station Performance Synthesis
# =============================================================================
def plot_f6(df_metrics):
    print("Generating F6 — Multi-station performance synthesis (horizontal grouped bars)...")
    fig, axes = plt.subplots(2, 2, figsize=(16, 12.5))

    st_order = [
        'b_l_chafia',
        'b_s_jabeur',
        'b_a_loudah',
        'ain_timedrine',
        'pont_de_mdez',
        'dar_el_hamra',
        'azzaba',
        'ait_khabbach'
    ]

    st_labels = [
        'Lalla Chafia [Daily]',
        'Sidi Jabeur [Daily]',
        'Ain Loudah* [Daily]',
        'Ain Timedrine [Monthly]',
        'Pont de Mdez [Monthly]',
        'Dar El Hamra [Monthly]',
        'Azzaba [Monthly]',
        'Ait Khabbach** [Monthly]'
    ]

    df_sub = df_metrics[df_metrics['station_id'].isin(st_order)].copy()
    y_pos = np.arange(len(st_order))
    bar_height = 0.20

    # 1. Subplot A: Kling-Gupta Efficiency (KGE)
    ax1 = axes[0, 0]
    for idx, (exp_id, label, color, _) in enumerate(SCHEMES):
        kge_vals = []
        for sid in st_order:
            row = df_sub[(df_sub['station_id'] == sid) & (df_sub['experiment'] == exp_id)].iloc[0]
            val = row['KGE_daily'] if pd.notna(row['KGE_daily']) else row['KGE_monthly']
            kge_vals.append(val)
        ax1.barh(y_pos + (idx - 1.5)*bar_height, kge_vals, bar_height, label=label, color=color, alpha=0.85)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(st_labels, fontsize=9.5, fontweight='bold')
    ax1.invert_yaxis()
    ax1.axvline(0, color='#333333', lw=1.0)
    ax1.axhline(2.5, color='#888888', ls='--', lw=0.9)  # Separator Bouregreg / Sebou
    ax1.text(0.02, 0.96, 'Bouregreg Basin (Daily)', transform=ax1.transAxes, fontsize=8.5, fontweight='bold', color='#1f77b4')
    ax1.text(0.02, 0.58, 'Sebou Basin (Monthly)', transform=ax1.transAxes, fontsize=8.5, fontweight='bold', color='#2ca02c')
    ax1.set_xlabel('Kling-Gupta Efficiency (KGE)', fontsize=9.5, fontweight='bold')
    ax1.set_title('(a) Kling-Gupta Efficiency (KGE)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax1.grid(axis='x', linestyle=':', alpha=0.5)
    ax1.set_xlim(-1.6, 1.0)  # Accommodates BATS at Ait Khabbach (-1.444) without clipping

    # 2. Subplot B: Delta KGE relative to SIMGM Reference
    ax2 = axes[0, 1]
    schemes_comp = [("OL_R2_SIMTOP", "SIMTOP", "#ff7f0e"),
                    ("OL_R3_SCHAAKE96", "Schaake96", "#2ca02c"),
                    ("OL_R4_BATS", "BATS", "#9467bd")]
    bar_h3 = 0.25
    for idx, (exp_id, label, color) in enumerate(schemes_comp):
        delta_vals = []
        for sid in st_order:
            row = df_sub[(df_sub['station_id'] == sid) & (df_sub['experiment'] == exp_id)].iloc[0]
            val = row['delta_KGE_daily'] if pd.notna(row['delta_KGE_daily']) else row['delta_KGE_monthly']
            delta_vals.append(val)
        ax2.barh(y_pos + (idx - 1)*bar_h3, delta_vals, bar_h3, label=f'Δ KGE ({label} - SIMGM)', color=color, alpha=0.85)

    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(st_labels, fontsize=9.5, fontweight='bold')
    ax2.invert_yaxis()
    ax2.axvline(0, color='#333333', lw=1.0)
    ax2.axhline(2.5, color='#888888', ls='--', lw=0.9)
    ax2.text(0.02, 0.96, 'Bouregreg Basin (Daily)', transform=ax2.transAxes, fontsize=8.5, fontweight='bold', color='#1f77b4')
    ax2.text(0.02, 0.58, 'Sebou Basin (Monthly)', transform=ax2.transAxes, fontsize=8.5, fontweight='bold', color='#2ca02c')
    ax2.set_xlabel('KGE Gain Relative to SIMGM (Δ KGE)', fontsize=9.5, fontweight='bold')
    ax2.set_title('(b) Performance Gain Relative to Baseline SIMGM (Δ KGE)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax2.grid(axis='x', linestyle=':', alpha=0.5)
    ax2.set_xlim(-1.5, 1.0)

    # 3. Subplot C: Percent Volume Bias (PBIAS %)
    ax3 = axes[1, 0]
    for idx, (exp_id, label, color, _) in enumerate(SCHEMES):
        pbias_vals = []
        for sid in st_order:
            row = df_sub[(df_sub['station_id'] == sid) & (df_sub['experiment'] == exp_id)].iloc[0]
            pbias_vals.append(row['PBIAS_monthly_pct'])
        rects = ax3.barh(y_pos + (idx - 1.5)*bar_height, pbias_vals, bar_height, label=label, color=color, alpha=0.85)
        # Annotate extreme positive PBIAS for Ait Khabbach BATS (+220%)
        if exp_id == 'OL_R4_BATS':
            for r, sid, val in zip(rects, st_order, pbias_vals):
                if sid == 'ait_khabbach' and val > 150:
                    ax3.annotate(f'+{val:.0f}%', xy=(val, r.get_y() + r.get_height()/2),
                                 xytext=(4, 0), textcoords='offset points', va='center', fontsize=7.5, fontweight='bold', color='#6a3d9a')

    ax3.set_yticks(y_pos)
    ax3.set_yticklabels(st_labels, fontsize=9.5, fontweight='bold')
    ax3.invert_yaxis()
    ax3.axvline(0, color='#333333', lw=1.0)
    ax3.axhline(2.5, color='#888888', ls='--', lw=0.9)
    ax3.axvspan(-15, 15, color='#e0f3db', alpha=0.5, label='Target Bias (±15%)')
    ax3.text(0.02, 0.96, 'Bouregreg Basin (Daily)', transform=ax3.transAxes, fontsize=8.5, fontweight='bold', color='#1f77b4')
    ax3.text(0.02, 0.58, 'Sebou Basin (Monthly)', transform=ax3.transAxes, fontsize=8.5, fontweight='bold', color='#2ca02c')
    ax3.set_xlabel('Percent Volume Bias PBIAS (%)', fontsize=9.5, fontweight='bold')
    ax3.set_title('(c) Annual Volume Relative Bias (PBIAS %)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax3.grid(axis='x', linestyle=':', alpha=0.5)
    ax3.set_xlim(-100, 240)  # Accommodates BATS at Ait Khabbach (+220%) without clipping

    # 4. Subplot D: Pearson Correlation Coefficient (r)
    ax4 = axes[1, 1]
    for idx, (exp_id, label, color, _) in enumerate(SCHEMES):
        r_vals = []
        for sid in st_order:
            row = df_sub[(df_sub['station_id'] == sid) & (df_sub['experiment'] == exp_id)].iloc[0]
            val = row['r_daily'] if pd.notna(row['r_daily']) else row['r_monthly']
            r_vals.append(val)
        ax4.barh(y_pos + (idx - 1.5)*bar_height, r_vals, bar_height, label=label, color=color, alpha=0.85)

    ax4.set_yticks(y_pos)
    ax4.set_yticklabels(st_labels, fontsize=9.5, fontweight='bold')
    ax4.invert_yaxis()
    ax4.axvline(0, color='#333333', lw=1.0)
    ax4.axhline(2.5, color='#888888', ls='--', lw=0.9)
    ax4.text(0.02, 0.96, 'Bouregreg Basin (Daily)', transform=ax4.transAxes, fontsize=8.5, fontweight='bold', color='#1f77b4')
    ax4.text(0.02, 0.58, 'Sebou Basin (Monthly)', transform=ax4.transAxes, fontsize=8.5, fontweight='bold', color='#2ca02c')
    ax4.set_xlabel('Pearson Correlation Coefficient (r)', fontsize=9.5, fontweight='bold')
    ax4.set_title('(d) Hydrograph Phasing & Temporal Correlation (r)', fontsize=10.5, fontweight='bold', loc='left', pad=4)
    ax4.grid(axis='x', linestyle=':', alpha=0.5)
    ax4.set_xlim(0, 1.05)

    # Shared global legend at top
    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 0.985), ncol=4, frameon=True, framealpha=0.95, fontsize=10)

    fig.text(0.08, 0.015,
             '* Ain Loudah: duplicate observation record with S.M. Cherif in ABH archives.\n'
             '** Ait Khabbach: influenced by intensive seasonal agricultural groundwater pumping in the Guigou plain and karstic recharge.\n'
             'Note: Bouregreg metrics evaluated at daily time step; Sebou metrics evaluated at monthly time step due to data availability.',
             fontsize=8.5, style='italic', color='#444444')

    fig.suptitle('F6 — Multi-Station Hydrological Performance Synthesis (2018) : SIMGM vs SIMTOP vs Schaake96 vs BATS', fontsize=12.5, fontweight='bold', y=1.01)
    plt.subplots_adjust(top=0.935, bottom=0.08, hspace=0.24, wspace=0.22)
    save_fig(fig, "f6_multistation_synthesis_performance_en")

# =============================================================================
# Contact Sheet Generator
# =============================================================================
def generate_contact_sheet():
    print("Generating contact sheet plate assembling all 7 figures...")
    import matplotlib.image as mpimg

    fig_names = [
        ("f1a_hydrographs_bouregreg_daily_2018_en.png", "F1A — Daily Streamflow Hydrographs : Bouregreg Basin"),
        ("f1b_hydrographs_sebou_monthly_2018_en.png", "F1B — Monthly Streamflow Hydrographs : Sebou Basin"),
        ("f2_precip_and_flood_response_2018_en.png", "F2 — Precipitation Forcing & Flood Hydrodynamics"),
        ("f3_daily_qs_qsb_hydrographs_2018_en.png", "F3 — Catchment Fluxes (P, Qs, Qsb) & Routed Streamflow"),
        ("f4_lowflow_diagnostic_summer2018_en.png", "F4 — Summer Streamflow and Zero-Flow Occurrence"),
        ("f5_discontinuity_and_continuity_check_en.png", "F5 — Temporal Continuity & Transition Checks"),
        ("f6_multistation_synthesis_performance_en.png", "F6 — Multi-Station Performance Synthesis")
    ]

    fig, axes = plt.subplots(4, 2, figsize=(20, 26))
    axes = axes.flatten()

    for idx, (fname, title) in enumerate(fig_names):
        fpath = os.path.join(FIG_DIR, fname)
        img = mpimg.imread(fpath)
        axes[idx].imshow(img)
        axes[idx].set_title(title, fontsize=11, fontweight='bold', pad=6)
        axes[idx].axis('off')

    # Last slot (axes[7]) for summary info box
    ax_info = axes[7]
    ax_info.axis('off')
    summary_text = (
        "Noah-MP 4.0.1 / HyMAP-2 Multi-Station Evaluation Suite (2018)\n"
        "─────────────────────────────────────────────────────────────\n\n"
        "• Suite Scope: 4 Noah-MP Runoff Formulations\n"
        "  - SIMGM (Baseline Reference)\n"
        "  - SIMTOP (Runoff option 2)\n"
        "  - Schaake96 (Runoff option 3)\n"
        "  - BATS (Runoff option 4)\n\n"
        "• Hydrological Basins Evaluated:\n"
        "  - Bouregreg Basin (Daily, 4 stations: Lalla Chafia, Sidi Jabeur,\n"
        "    Ain Loudah*, S.M. Cherif*)\n"
        "  - Sebou Basin Continuum (Monthly, 6 nested stations:\n"
        "    Ain Timedrine, Azzaba, Pont de Mdez, Ait Khabbach*,\n"
        "    Dar El Hamra, Pont Ait Aissa*)\n\n"
        "• Key Addressed Diagnostics:\n"
        "  - Simulation continuity verified across year boundaries (F5)\n"
        "  - Baseflow (Qsb) dominance & zero-flow intermittency (F3, F4)\n"
        "  - Storm hydrodynamics vs multi-source precipitation (F2)\n"
        "  - Comparative performance metrics & bias distribution (F6)\n\n"
        "All figures rendered at 300 DPI (PNG) with vector PDF counterparts.\n"
        "Repository: Noah-MP_Morocco / experiments/NorthMor/opl_hydrology_sensitivity"
    )
    ax_info.text(0.08, 0.50, summary_text, transform=ax_info.transAxes, fontsize=10.5,
                 va='center', family='monospace', bbox=dict(boxstyle="round,pad=0.8", fc="#f8f9fa", ec="#cccccc", lw=1.2))

    fig.suptitle('Noah-MP–HyMAP-2 Multi-Station Diagnostic Suite (2018) — Overview Plate', fontsize=16, fontweight='bold', y=0.995)
    plt.tight_layout()
    plt.subplots_adjust(top=0.97, bottom=0.02)
    save_fig(fig, "multistation_figures_contact_sheet")

def main():
    import sys
    print("Loading post-processing tables...")
    df_q = pd.read_csv(STREAMFLOW_CSV)
    df_flux = pd.read_csv(FLUXES_DAILY_CSV)
    df_metrics = pd.read_csv(METRICS_CSV)
    df_low = pd.read_csv(LOWFLOWS_CSV)

    if len(sys.argv) > 1 and sys.argv[1] == "--f4-only":
        print("Executing only plot_f4 as requested...")
        plot_f4(df_q, df_low)
        print("\nFigure F4 generated successfully!")
        return

    plot_f1a(df_q)
    plot_f1b(df_q)
    plot_f2(df_q, df_flux)
    plot_f3(df_flux, df_q)
    plot_f4(df_q, df_low)
    plot_f5(df_q)
    plot_f6(df_metrics)
    generate_contact_sheet()
    print("\nAll figures F1A, F1B, F2, F3, F4, F5, F6 and Contact Sheet generated successfully!")

if __name__ == '__main__':
    main()
