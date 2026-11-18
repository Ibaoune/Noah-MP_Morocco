#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sebou_bouregreg_diagnostic.py
Diagnostic approfondi et comparatif OPL vs DA-NoCDF vs DA-CDF sur le Sebou et le Bouregreg.
Version révisée avec nuances scientifiques et ajustements des figures.
"""

import os, sys, glob, datetime, json
import numpy as np
import pandas as pd
import scipy.stats as stats
import netCDF4 as nc

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


def plot_lalla_chafia_2018_en(m_2018, fig_streamflow_dir):
    """
    Génère la figure détaillée 2018 pour Lalla Chafia en anglais (300 dpi)
    destinée à la communication avec Augusto Getirana.
    """
    dates_2018 = pd.to_datetime(m_2018['date']).dt.to_pydatetime()
    q_obs = m_2018['q_m3s'].to_numpy()
    q_opl = m_2018['q_opl'].to_numpy()
    q_nocdf = m_2018['q_nocdf'].to_numpy()
    q_cdf = m_2018['q_cdf'].to_numpy()

    # Configuration typographique
    plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
    plt.rcParams['axes.edgecolor'] = '#444444'
    plt.rcParams['axes.linewidth'] = 0.8

    # Couleurs distinctes : Obs en noir, OL en bleu, DA-NoCDF en rouge, DA-CDF en vert
    c_obs = '#111111'
    c_opl = '#1f77b4'
    c_nocdf = '#d62728'
    c_cdf = '#2ca02c'

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(13, 8.5), dpi=300,
        gridspec_kw={'height_ratios': [1.6, 1.2]}
    )

    # ----------------- Top Panel: Daily streamflow and flood peaks -----------------
    l1, = ax_top.plot(dates_2018, q_obs, color=c_obs, lw=1.6, label='Observed (ABH)', alpha=0.95, zorder=4)
    l2, = ax_top.plot(dates_2018, q_opl, color=c_opl, lw=1.3, label='Open-Loop (OL)', alpha=0.9, zorder=3)
    l3, = ax_top.plot(dates_2018, q_nocdf, color=c_nocdf, lw=1.3, ls='--', label='DA-NoCDF', alpha=0.9, zorder=3)
    l4, = ax_top.plot(dates_2018, q_cdf, color=c_cdf, lw=1.4, ls='-.', label='DA-CDF', alpha=0.95, zorder=3)

    ax_top.set_title('Daily streamflow and flood peaks', fontsize=11.5, fontweight='bold', pad=10)
    ax_top.set_ylabel('Daily streamflow (m³/s)', fontsize=10.5, fontweight='medium')
    ax_top.set_xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2018-12-31'))
    ax_top.set_ylim(-3, 215)
    ax_top.grid(True, which='major', ls=':', color='#cccccc', alpha=0.7)

    ax_top.xaxis.set_major_locator(mdates.MonthLocator())
    ax_top.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_top.tick_params(axis='both', labelsize=9.5)

    # Annotation discrète des statistiques annuelles (positionnée en été pour éviter tout chevauchement)
    stats_text = (
        "2018 Annual Statistics (Mean | Annual Peak):\n"
        f"• Observed (ABH):  {q_obs.mean():.1f} m³/s  |  {q_obs.max():.1f} m³/s (Mar 08)\n"
        f"• Open-Loop (OL):   {q_opl.mean():.1f} m³/s  |   {q_opl.max():.1f} m³/s (Apr 26)\n"
        f"• DA-NoCDF:        {q_nocdf.mean():.1f} m³/s  |  {q_nocdf.max():.1f} m³/s (Mar 17)\n"
        f"• DA-CDF:          {q_cdf.mean():.1f} m³/s  |   {q_cdf.max():.1f} m³/s (Apr 26)"
    )
    ax_top.text(
        0.51, 0.93, stats_text,
        transform=ax_top.transAxes,
        fontsize=8.5,
        verticalalignment='top',
        family='sans-serif',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#c0c0c0', alpha=0.93)
    )

    # ----------------- Bottom Panel: Low flows and seasonal recession (log scale) -----------------
    q_obs_pos = np.where(q_obs > 0.0, q_obs, np.nan)
    mask_zeros = (q_obs == 0.0)
    dates_zeros = dates_2018[mask_zeros]

    ax_bot.plot(dates_2018, q_obs_pos, color=c_obs, lw=1.6, label='Observed (ABH)', alpha=0.95, zorder=4)
    if len(dates_zeros) > 0:
        ax_bot.scatter(dates_zeros, [0.015]*len(dates_zeros), color='#e377c2', marker='|', s=45, label=f'Zero-flow days ({len(dates_zeros)} d)', zorder=5)

    ax_bot.plot(dates_2018, q_opl, color=c_opl, lw=1.3, label='Open-Loop (OL)', alpha=0.9, zorder=3)
    ax_bot.plot(dates_2018, q_nocdf, color=c_nocdf, lw=1.3, ls='--', label='DA-NoCDF', alpha=0.9, zorder=3)
    ax_bot.plot(dates_2018, q_cdf, color=c_cdf, lw=1.4, ls='-.', label='DA-CDF', alpha=0.95, zorder=3)

    ax_bot.set_yscale('log')
    ax_bot.set_xlim(pd.Timestamp('2018-01-01'), pd.Timestamp('2018-12-31'))
    ax_bot.set_ylim(0.02, 350)
    ax_bot.set_title('Low flows and seasonal recession (log scale)', fontsize=11.5, fontweight='bold', pad=10)
    ax_bot.set_ylabel('Daily streamflow [log scale] (m³/s)', fontsize=10.5, fontweight='medium')
    ax_bot.set_xlabel('Date (2018)', fontsize=10.5, fontweight='medium')

    ax_bot.grid(True, which='major', ls=':', color='#cccccc', alpha=0.7)
    ax_bot.grid(True, which='minor', ls=':', color='#ebebeb', alpha=0.4)

    ax_bot.xaxis.set_major_locator(mdates.MonthLocator())
    ax_bot.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax_bot.tick_params(axis='both', labelsize=9.5)

    # Annotation discrète des étiages (positionnée en été)
    low_flow_text = (
        "Annual Minimum Flow:\n"
        f"• Observed (ABH):  {q_obs.min():.2f} m³/s\n"
        f"• Open-Loop (OL):   {q_opl.min():.2f} m³/s\n"
        f"• DA-NoCDF:        {q_nocdf.min():.2f} m³/s\n"
        f"• DA-CDF:          {q_cdf.min():.2f} m³/s"
    )
    ax_bot.text(
        0.58, 0.93, low_flow_text,
        transform=ax_bot.transAxes,
        fontsize=8.5,
        verticalalignment='top',
        family='sans-serif',
        bbox=dict(boxstyle='round,pad=0.5', facecolor='#ffffff', edgecolor='#c0c0c0', alpha=0.93)
    )

    # Légende partagée unique en tête de figure
    fig.legend(
        [l1, l2, l3, l4],
        ['Observed (ABH)', 'Open-Loop (OL)', 'DA-NoCDF', 'DA-CDF'],
        loc='upper center',
        bbox_to_anchor=(0.5, 0.938),
        ncol=4,
        frameon=True,
        facecolor='#ffffff',
        edgecolor='#cccccc',
        fontsize=10.5
    )

    # Titre principal court
    plt.suptitle('Observed and HyMAP2-simulated streamflow at Lalla Chafia (2018)', fontsize=13.5, fontweight='bold', y=0.985)

    plt.subplots_adjust(top=0.86, bottom=0.08, hspace=0.34, left=0.08, right=0.96)

    out_fig_path = os.path.join(fig_streamflow_dir, 'lalla_chafia_streamflow_2018_en.png')
    plt.savefig(out_fig_path, dpi=300)
    plt.close(fig)
    print(f"-> Figure detaillee 2018 EN haute resolution (300 dpi) : {out_fig_path}")
    return out_fig_path


def plot_lalla_chafia_2018_linres0_comparison(clean_dir, opl_out_dir, linres0_csv, out_fig_path, table_out_path):
    """
    Génère la figure comparative 2018 à Lalla Chafia en anglais (3 panneaux, 300 dpi) :
      (a) Full-year hydrograph
      (b) Zoom sur crues mars-avril
      (c) Zoom sur étiages juin-septembre
    et sauvegarde le tableau des métriques d'évaluation dans table_out_path.
    """
    df_obs = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    sub_obs = df_obs[(df_obs["station_id"] == "b_l_chafia") & (df_obs["date"].str.startswith("2018"))][["date", "q_m3s"]].rename(columns={"q_m3s": "q_obs"})

    df_hist = pd.read_csv(os.path.join(opl_out_dir, "t7_sim_daily_12stations_corrigee.csv"))
    sub_hist = df_hist[df_hist["date"].str.startswith("2018")][["date", "b_l_chafia"]].rename(columns={"b_l_chafia": "q_hist"})

    df_lr0 = pd.read_csv(linres0_csv)
    sub_lr0 = df_lr0[df_lr0["date"].str.startswith("2018")][["date", "b_l_chafia"]].rename(columns={"b_l_chafia": "q_lr0"})

    m = pd.merge(sub_obs, sub_hist, on="date").merge(sub_lr0, on="date").dropna().sort_values("date").reset_index(drop=True)
    n_days = len(m)

    o = m["q_obs"].to_numpy()
    qh = m["q_hist"].to_numpy()
    ql = m["q_lr0"].to_numpy()

    def get_stats(s, o):
        bias = float(np.mean(s - o))
        rel_bias = float(bias / np.mean(o) * 100.0)
        rmse = float(np.sqrt(np.mean((s - o)**2)))
        r = float(np.corrcoef(o, s)[0, 1])
        nse = float(1.0 - (np.sum((o - s)**2) / np.sum((o - np.mean(o))**2)))
        alpha = float(np.std(s) / np.std(o))
        beta = float(np.mean(s) / np.mean(o))
        kge = float(1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2))
        return bias, rel_bias, rmse, r, nse, kge

    bh, rbh, rmseh, rh, nseh, kgeh = get_stats(qh, o)
    bl, rbl, rmsel, rl, nsel, kgel = get_stats(ql, o)

    summer = m[(m["date"] >= "2018-06-01") & (m["date"] <= "2018-09-30")]

    def get_date_val(df, date_str, col):
        row = df[df["date"] == date_str]
        return float(row[col].values[0]) if len(row) > 0 else np.nan

    records = [
        {
            "Simulation": "Observed (ABH)",
            "Valid_Days": n_days,
            "Annual_Mean_m3s": round(float(np.mean(o)), 2),
            "Bias_m3s": 0.0,
            "Rel_Bias_pct": 0.0,
            "RMSE_m3s": 0.0,
            "Pearson_r": 1.000,
            "NSE": 1.000,
            "KGE": 1.000,
            "Summer_Mean_m3s": round(float(summer["q_obs"].mean()), 2),
            "Annual_Max_m3s": round(float(np.max(o)), 1),
            "Annual_Max_Date": m.loc[m["q_obs"].idxmax(), "date"],
            "March07_m3s": get_date_val(m, "2018-03-07", "q_obs"),
            "March08_m3s": get_date_val(m, "2018-03-08", "q_obs"),
            "April25_m3s": get_date_val(m, "2018-04-25", "q_obs"),
            "April26_m3s": get_date_val(m, "2018-04-26", "q_obs")
        },
        {
            "Simulation": "OPL Historical (linres=1)",
            "Valid_Days": n_days,
            "Annual_Mean_m3s": round(float(np.mean(qh)), 2),
            "Bias_m3s": round(bh, 2),
            "Rel_Bias_pct": round(rbh, 1),
            "RMSE_m3s": round(rmseh, 2),
            "Pearson_r": round(rh, 3),
            "NSE": round(nseh, 3),
            "KGE": round(kgeh, 3),
            "Summer_Mean_m3s": round(float(summer["q_hist"].mean()), 2),
            "Annual_Max_m3s": round(float(np.max(qh)), 1),
            "Annual_Max_Date": m.loc[m["q_hist"].idxmax(), "date"],
            "March07_m3s": round(get_date_val(m, "2018-03-07", "q_hist"), 2),
            "March08_m3s": round(get_date_val(m, "2018-03-08", "q_hist"), 2),
            "April25_m3s": round(get_date_val(m, "2018-04-25", "q_hist"), 2),
            "April26_m3s": round(get_date_val(m, "2018-04-26", "q_hist"), 2)
        },
        {
            "Simulation": "OPL New (linres=0)",
            "Valid_Days": n_days,
            "Annual_Mean_m3s": round(float(np.mean(ql)), 2),
            "Bias_m3s": round(bl, 2),
            "Rel_Bias_pct": round(rbl, 1),
            "RMSE_m3s": round(rmsel, 2),
            "Pearson_r": round(rl, 3),
            "NSE": round(nsel, 3),
            "KGE": round(kgel, 3),
            "Summer_Mean_m3s": round(float(summer["q_lr0"].mean()), 2),
            "Annual_Max_m3s": round(float(np.max(ql)), 1),
            "Annual_Max_Date": m.loc[m["q_lr0"].idxmax(), "date"],
            "March07_m3s": round(get_date_val(m, "2018-03-07", "q_lr0"), 2),
            "March08_m3s": round(get_date_val(m, "2018-03-08", "q_lr0"), 2),
            "April25_m3s": round(get_date_val(m, "2018-04-25", "q_lr0"), 2),
            "April26_m3s": round(get_date_val(m, "2018-04-26", "q_lr0"), 2)
        }
    ]

    df_table = pd.DataFrame(records)
    df_table.to_csv(table_out_path, index=False)
    print(f"-> Table des metriques enregistree : {table_out_path}")

    dates = pd.to_datetime(m["date"]).dt.to_pydatetime()
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"
    plt.rcParams["axes.edgecolor"] = "#444444"
    plt.rcParams["axes.linewidth"] = 0.8

    c_obs = "#111111"
    c_hist = "#1f77b4"
    c_lr0 = "#d62728"

    fig, (ax1, ax2, ax3) = plt.subplots(
        3, 1, figsize=(12, 11), dpi=300,
        gridspec_kw={"height_ratios": [1.2, 1.1, 1.1]}
    )

    # Panel (a) Annual Hydrograph
    l1, = ax1.plot(dates, o, color=c_obs, lw=1.6, label="Observed (ABH)", alpha=0.95, zorder=4)
    l2, = ax1.plot(dates, qh, color=c_hist, lw=1.3, ls="--", label="HyMAP-2 Historical (linres=1, spinup restart)", alpha=0.9, zorder=3)
    l3, = ax1.plot(dates, ql, color=c_lr0, lw=1.4, ls="-", label="HyMAP-2 New (linres=0, coldstart)", alpha=0.9, zorder=3)

    ax1.set_title("(a) Full-Year 2018 Hydrograph at Lalla Chafia (Bouregreg Basin)", fontsize=11, fontweight="bold", pad=10)
    ax1.set_ylabel("Daily streamflow (m³/s)", fontsize=10, fontweight="medium")
    ax1.set_xlim(pd.Timestamp("2018-01-01"), pd.Timestamp("2018-12-31"))
    ax1.set_ylim(-3, 215)
    ax1.grid(True, which="major", ls=":", color="#cccccc", alpha=0.7)
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax1.tick_params(axis="both", labelsize=9)

    # Panel (b) March-April High Flows
    mask_ma = (m["date"] >= "2018-03-01") & (m["date"] <= "2018-04-30")
    dates_ma = pd.to_datetime(m.loc[mask_ma, "date"]).dt.to_pydatetime()

    ax2.plot(dates_ma, o[mask_ma], color=c_obs, lw=1.6, label="Observed (ABH)", alpha=0.95, zorder=4)
    ax2.plot(dates_ma, qh[mask_ma], color=c_hist, lw=1.3, ls="--", label="HyMAP-2 Historical (linres=1, spinup restart)", alpha=0.9, zorder=3)
    ax2.plot(dates_ma, ql[mask_ma], color=c_lr0, lw=1.4, ls="-", label="HyMAP-2 New (linres=0, coldstart)", alpha=0.9, zorder=3)

    ax2.set_title("(b) High-Flow Period: Flood Peaks and Hydrograph Timing (March – April 2018)", fontsize=11, fontweight="bold", pad=8)
    ax2.set_ylabel("Daily streamflow (m³/s)", fontsize=10, fontweight="medium")
    ax2.set_xlim(pd.Timestamp("2018-03-01"), pd.Timestamp("2018-04-30"))
    ax2.set_ylim(-3, 215)
    ax2.grid(True, which="major", ls=":", color="#cccccc", alpha=0.7)
    ax2.xaxis.set_major_locator(mdates.DayLocator(interval=7))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax2.tick_params(axis="both", labelsize=9)

    # Panel (c) June-Sept Low Flows
    mask_sum = (m["date"] >= "2018-06-01") & (m["date"] <= "2018-09-30")
    dates_sum = pd.to_datetime(m.loc[mask_sum, "date"]).dt.to_pydatetime()

    ax3.plot(dates_sum, o[mask_sum], color=c_obs, lw=1.6, label="Observed (ABH)", alpha=0.95, zorder=4)
    ax3.plot(dates_sum, qh[mask_sum], color=c_hist, lw=1.3, ls="--", label="HyMAP-2 Historical (linres=1, spinup restart)", alpha=0.9, zorder=3)
    ax3.plot(dates_sum, ql[mask_sum], color=c_lr0, lw=1.4, ls="-", label="HyMAP-2 New (linres=0, coldstart)", alpha=0.9, zorder=3)

    ax3.set_title("(c) Low-Flow Period: Summer Recession and Baseflow Floor (June – September 2018)", fontsize=11, fontweight="bold", pad=8)
    ax3.set_ylabel("Daily streamflow (m³/s)", fontsize=10, fontweight="medium")
    ax3.set_xlabel("Date (2018)", fontsize=10, fontweight="medium")
    ax3.set_xlim(pd.Timestamp("2018-06-01"), pd.Timestamp("2018-09-30"))
    ax3.set_ylim(-0.5, 15)
    ax3.grid(True, which="major", ls=":", color="#cccccc", alpha=0.7)
    ax3.xaxis.set_major_locator(mdates.DayLocator(interval=14))
    ax3.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax3.tick_params(axis="both", labelsize=9)

    # Shared Legend
    fig.legend(
        [l1, l2, l3],
        ["Observed (ABH)", "HyMAP-2 Historical (linres=1, spinup restart)", "HyMAP-2 New (linres=0, coldstart)"],
        loc="upper center",
        bbox_to_anchor=(0.5, 0.985),
        ncol=3,
        frameon=True,
        facecolor="#ffffff",
        edgecolor="#cccccc",
        fontsize=10.5
    )

    plt.subplots_adjust(top=0.88, bottom=0.06, hspace=0.34, left=0.08, right=0.96)
    plt.savefig(out_fig_path, dpi=300)
    pdf_path = out_fig_path.replace(".png", ".pdf")
    plt.savefig(pdf_path, dpi=300)
    plt.close(fig)
    print(f"-> Figure enregistree : {out_fig_path} et {pdf_path}")
    return out_fig_path


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Evaluation hydrologique comparative Sebou & Bouregreg (OPL vs DA-NoCDF vs DA-CDF)."
    )
    parser.add_argument(
        "--routing-dir",
        default=None,
        help="Repertoire racine de routing (par defaut: detecte automatiquement)."
    )
    parser.add_argument(
        "--clean-dir",
        default=None,
        help="Repertoire des observations nettoyees (data/streamflow_clean)."
    )
    parser.add_argument(
        "--fig-linres0-2018",
        action="store_true",
        help="Genere la figure comparative 2018 3 panneaux linres0 vs linres1 et la table de metriques."
    )
    parser.add_argument(
        "--fig-chafia-en-only",
        action="store_true",
        help="Regenere uniquement la figure en anglais de Lalla Chafia 2018 (lalla_chafia_streamflow_2018_en.png)."
    )
    parser.add_argument(
        "--plots-dir",
        default=None,
        help="Repertoire de sortie des figures et tables (plots/sebou_bouregreg)."
    )
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))
    if args.routing_dir:
        base_dir = os.path.abspath(args.routing_dir)
    else:
        base_dir = os.path.abspath(os.path.join(script_dir, ".."))

    repo_root = os.path.abspath(os.path.join(base_dir, "../../.."))
    if args.clean_dir:
        clean_dir = os.path.abspath(args.clean_dir)
    else:
        clean_dir = os.path.join(repo_root, "data/streamflow_clean")

    if args.plots_dir:
        out_dir = os.path.abspath(args.plots_dir)
    else:
        out_dir = os.path.join(base_dir, "plots/sebou_bouregreg")

    print("=" * 95)
    print("EVALUATION HYDROLOGIQUE CIBLEE : SEBOU & BOUREGREG (OPL vs DA-NoCDF vs DA-CDF)")
    print("=" * 95)
    fig_streamflow_dir = os.path.join(out_dir, "figures/streamflow")
    table_dir = os.path.join(out_dir, "tables")
    os.makedirs(fig_streamflow_dir, exist_ok=True)
    os.makedirs(table_dir, exist_ok=True)

    opl_out_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee")
    da_nocdf_dir = os.path.join(base_dir, "output/DA_nocdf_2016_2020")
    da_cdf_dir = os.path.join(base_dir, "output/DA_cdf_2016_2020")

    pairing_csv = os.path.join(base_dir, "stations/hymap_stations_pairing.csv")
    df_p = pd.read_csv(pairing_csv)
    # Filtrer uniquement Sebou et Bouregreg (exclusion explicite de Ksob/Adamna)
    df_p = df_p[df_p["bassin"].isin(["Sebou", "Bouregreg"])].reset_index(drop=True)

    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_obs_monthly["year_month"] = df_obs_monthly["annee"].astype(str) + "-" + df_obs_monthly["mois"].astype(str).str.zfill(2)

    # Chargement des debits simules
    df_q_opl_d = pd.read_csv(os.path.join(opl_out_dir, "t7_sim_daily_12stations_corrigee.csv"))
    df_q_nocdf_d = pd.read_csv(os.path.join(da_nocdf_dir, "t8_sim_daily_12stations_da_nocdf.csv"))
    df_q_cdf_d = pd.read_csv(os.path.join(da_cdf_dir, "t9_sim_daily_12stations_da_cdf.csv"))

    # Agregations mensuelles
    for df in [df_q_opl_d, df_q_nocdf_d, df_q_cdf_d]:
        df["year_month"] = pd.to_datetime(df["date"]).dt.to_period("M").astype(str)

    df_q_opl_m = df_q_opl_d.groupby("year_month").mean(numeric_only=True).reset_index()
    df_q_nocdf_m = df_q_nocdf_d.groupby("year_month").mean(numeric_only=True).reset_index()
    df_q_cdf_m = df_q_cdf_d.groupby("year_month").mean(numeric_only=True).reset_index()

    if args.fig_linres0_2018:
        linres0_csv = os.path.join(base_dir, "output/OPL_linres0_2016_2020/t_sim_daily_12stations_opl_linres0.csv")
        out_fig = os.path.join(fig_streamflow_dir, "lalla_chafia_2018_hymap2_linres0_vs_hist.png")
        out_tab = os.path.join(table_dir, "table_metrics_2018_lalla_chafia_linres0.csv")
        plot_lalla_chafia_2018_linres0_comparison(clean_dir, opl_out_dir, linres0_csv, out_fig, out_tab)
        print("Fin du mode exclusif --fig-linres0-2018.")
        return

    if args.fig_chafia_en_only:
        sub_o = df_obs_daily[(df_obs_daily["station_id"] == "b_l_chafia") & (df_obs_daily["date"].str.startswith("2018"))].copy()
        m_2018_fast = pd.merge(sub_o[["date", "q_m3s"]], df_q_opl_d[["date", "b_l_chafia"]], on="date", how="inner").rename(columns={"b_l_chafia": "q_opl"})
        m_2018_fast = pd.merge(m_2018_fast, df_q_nocdf_d[["date", "b_l_chafia"]], on="date", how="inner").rename(columns={"b_l_chafia": "q_nocdf"})
        m_2018_fast = pd.merge(m_2018_fast, df_q_cdf_d[["date", "b_l_chafia"]], on="date", how="inner").rename(columns={"b_l_chafia": "q_cdf"})
        out_en = plot_lalla_chafia_2018_en(m_2018_fast, fig_streamflow_dir)
        print("Fin du mode exclusif --fig-chafia-en-only.")
        return

    # Dictionnaire de métadonnées officiel
    meta_dict = {
        "b_a_loudah": {"ire": "2673/20", "oued": "Korifla", "aire_off": 697.6, "note": "Duplication exacte avec S.M. Cherif (série ABH non indépendante)"},
        "b_s_cherif": {"ire": "2674/20", "oued": "Mechraa", "aire_off": 649.5, "note": "Duplication exacte avec Ain Loudah (série ABH non indépendante)"},
        "b_s_jabeur": {"ire": "964/21",  "oued": "Grou",    "aire_off": 3138.5, "note": "Station de référence Bouregreg (100% couv)"},
        "b_l_chafia": {"ire": "963/21",  "oued": "Bouregreg","aire_off": 3341.6, "note": "Station aval Bouregreg (99.95% couv)"},
        "ain_timedrine": {"ire": "581/22", "oued": "Sebou", "aire_off": 4387.0, "note": "Grand Sebou (100% couv, 60 mois)"},
        "ait_khabbach":  {"ire": "585/22", "oued": "Guigou", "aire_off": 1240.0, "note": "Partiel (73.3% couv, 44 mois)"},
        "azzaba":        {"ire": "583/22", "oued": "Sebou", "aire_off": 4640.0, "note": "Sebou amont (100% couv, 60 mois)"},
        "dar_el_hamra":  {"ire": "1000/23","oued": "Zloul", "aire_off": 670.0,  "note": "Affluent Zloul (100% couv, 60 mois)"},
        "el_mers":       {"ire": "541/23", "oued": "Masser","aire_off": 1004.0, "note": "Partiel (33.3% couv, 20 mois)"},
        "pont_ait_aissa":{"ire": "198/30", "oued": "Guigou","aire_off": 205.0,  "note": "Haut Guigou (100% couv, 60 mois)"},
        "pont_de_mdez":  {"ire": "582/22", "oued": "Sebou", "aire_off": 3435.0, "note": "Partiel (73.3% couv, 44 mois)"}
    }

    def calc_metrics(obs, sim):
        r, _ = stats.pearsonr(obs, sim)
        alpha = np.std(sim, ddof=1) / (np.std(obs, ddof=1) + 1e-12)
        beta = np.mean(sim) / (np.mean(obs) + 1e-12)
        kge = 1.0 - np.sqrt((r - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)
        denom_nse = np.sum((obs - np.mean(obs))**2)
        nse = 1.0 - np.sum((sim - obs)**2) / (denom_nse + 1e-12)
        pbias = float(np.sum(sim - obs) / (np.sum(obs) + 1e-12) * 100.0)
        return {"r": r, "alpha": alpha, "beta": beta, "KGE": kge, "NSE": nse, "PBIAS": pbias,
                "mean_sim": float(np.mean(sim)), "median_sim": float(np.median(sim)),
                "max_sim": float(np.max(sim)), "min_sim": float(np.min(sim)),
                "mean_obs": float(np.mean(obs)), "median_obs": float(np.median(obs)),
                "max_obs": float(np.max(obs)), "min_obs": float(np.min(obs))}

    table_11_records = []
    merged_data = {}

    for _, p in df_p.iterrows():
        sid = p["station_id"]
        nom = p["nom"]
        bassin = p["bassin"]
        pas = p["type_pas"]
        meta = meta_dict[sid]

        if pas == "journalier":
            sub_o = df_obs_daily[(df_obs_daily["station_id"] == sid) & (df_obs_daily["date"] >= "2016-01-01") & (df_obs_daily["date"] <= "2020-12-31")].copy()
            m = pd.merge(sub_o[["date", "q_m3s"]], df_q_opl_d[["date", sid]], on="date", how="inner").rename(columns={sid: "q_opl"})
            m = pd.merge(m, df_q_nocdf_d[["date", sid]], on="date", how="inner").rename(columns={sid: "q_nocdf"})
            m = pd.merge(m, df_q_cdf_d[["date", sid]], on="date", how="inner").rename(columns={sid: "q_cdf"})
            time_col = "date"
        else:
            sub_o = df_obs_monthly[(df_obs_monthly["station_id"] == sid) & (df_obs_monthly["annee"] >= 2016) & (df_obs_monthly["annee"] <= 2020)].copy()
            m = pd.merge(sub_o[["year_month", "q_m3s"]], df_q_opl_m[["year_month", sid]], on="year_month", how="inner").rename(columns={sid: "q_opl"})
            m = pd.merge(m, df_q_nocdf_m[["year_month", sid]], on="year_month", how="inner").rename(columns={sid: "q_nocdf"})
            m = pd.merge(m, df_q_cdf_m[["year_month", sid]], on="year_month", how="inner").rename(columns={sid: "q_cdf"})
            time_col = "year_month"

        merged_data[sid] = (m, time_col)
        o = m["q_m3s"].to_numpy()
        s_opl = m["q_opl"].to_numpy()
        s_nocdf = m["q_nocdf"].to_numpy()
        s_cdf = m["q_cdf"].to_numpy()

        m_opl = calc_metrics(o, s_opl)
        m_nocdf = calc_metrics(o, s_nocdf)
        m_cdf = calc_metrics(o, s_cdf)

        table_11_records.append({
            "station_id": sid, "nom": nom, "oued": meta["oued"], "bassin": bassin, "pas": pas, "N": len(o),
            "KGE_opl": m_opl["KGE"], "KGE_nocdf": m_nocdf["KGE"], "KGE_cdf": m_cdf["KGE"],
            "dKGE_cdf_opl": m_cdf["KGE"] - m_opl["KGE"], "dKGE_cdf_nocdf": m_cdf["KGE"] - m_nocdf["KGE"],
            "r_opl": m_opl["r"], "r_nocdf": m_nocdf["r"], "r_cdf": m_cdf["r"], "dr_cdf_opl": m_cdf["r"] - m_opl["r"],
            "NSE_opl": m_opl["NSE"], "NSE_nocdf": m_nocdf["NSE"], "NSE_cdf": m_cdf["NSE"], "dNSE_cdf_opl": m_cdf["NSE"] - m_opl["NSE"],
            "PBIAS_opl": m_opl["PBIAS"], "PBIAS_nocdf": m_nocdf["PBIAS"], "PBIAS_cdf": m_cdf["PBIAS"],
            "dPBIAS_cdf_nocdf": m_cdf["PBIAS"] - m_nocdf["PBIAS"],
            "Q_obs_mean": m_opl["mean_obs"], "Q_opl_mean": m_opl["mean_sim"], "Q_nocdf_mean": m_nocdf["mean_sim"], "Q_cdf_mean": m_cdf["mean_sim"],
            "note": meta["note"]
        })

    df_table_11 = pd.DataFrame(table_11_records)
    csv_11_path = os.path.join(table_dir, "tableau_synthese_11stations_sebou_bouregreg.csv")
    df_table_11.to_csv(csv_11_path, index=False)
    print(f"-> Tableau 1 (11 stations) sauvegarde : {csv_11_path}")

    # =========================================================================
    # TABLEAU DIAGNOSTIQUE DÉTAILLÉ (5 STATIONS FOCUS)
    # =========================================================================
    focus_stations = ["b_s_jabeur", "b_l_chafia", "ain_timedrine", "dar_el_hamra", "pont_de_mdez"]
    diag_records = []

    for sid in focus_stations:
        m, time_col = merged_data[sid]
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        meta = meta_dict[sid]
        pas = p_row["type_pas"]
        o = m["q_m3s"].to_numpy()
        s_opl = m["q_opl"].to_numpy()
        s_nocdf = m["q_nocdf"].to_numpy()
        s_cdf = m["q_cdf"].to_numpy()

        if pas == "journalier":
            p95_o, p95_opl, p95_nocdf, p95_cdf = np.percentile(o, 95), np.percentile(s_opl, 95), np.percentile(s_nocdf, 95), np.percentile(s_cdf, 95)
            p99_o, p99_opl, p99_nocdf, p99_cdf = np.percentile(o, 99), np.percentile(s_opl, 99), np.percentile(s_nocdf, 99), np.percentile(s_cdf, 99)
        else:
            p95_o, p95_opl, p95_nocdf, p95_cdf = np.nan, np.nan, np.nan, np.nan
            p99_o, p99_opl, p99_nocdf, p99_cdf = np.nan, np.nan, np.nan, np.nan

        m_opl = calc_metrics(o, s_opl)
        m_nocdf = calc_metrics(o, s_nocdf)
        m_cdf = calc_metrics(o, s_cdf)

        ratio_peak_opl = m_opl["max_sim"] / m_opl["max_obs"] if m_opl["max_obs"] > 0 else np.nan
        ratio_peak_nocdf = m_nocdf["max_sim"] / m_nocdf["max_obs"] if m_nocdf["max_obs"] > 0 else np.nan
        ratio_peak_cdf = m_cdf["max_sim"] / m_cdf["max_obs"] if m_cdf["max_obs"] > 0 else np.nan

        diag_records.append({
            "station_id": sid, "nom": p_row["nom"], "bassin": p_row["bassin"], "pas": pas, "N": len(o),
            "Q_mean_obs": m_opl["mean_obs"], "Q_mean_opl": m_opl["mean_sim"], "Q_mean_nocdf": m_nocdf["mean_sim"], "Q_mean_cdf": m_cdf["mean_sim"],
            "Q_med_obs": m_opl["median_obs"], "Q_med_opl": m_opl["median_sim"], "Q_med_nocdf": m_nocdf["median_sim"], "Q_med_cdf": m_cdf["median_sim"],
            "P95_obs": p95_o, "P95_opl": p95_opl, "P95_nocdf": p95_nocdf, "P95_cdf": p95_cdf,
            "P99_obs": p99_o, "P99_opl": p99_opl, "P99_nocdf": p99_nocdf, "P99_cdf": p99_cdf,
            "Q_max_obs": m_opl["max_obs"], "Q_max_opl": m_opl["max_sim"], "Q_max_nocdf": m_nocdf["max_sim"], "Q_max_cdf": m_cdf["max_sim"],
            "Ratio_peak_opl": ratio_peak_opl, "Ratio_peak_nocdf": ratio_peak_nocdf, "Ratio_peak_cdf": ratio_peak_cdf,
            "PBIAS_opl": m_opl["PBIAS"], "PBIAS_nocdf": m_nocdf["PBIAS"], "PBIAS_cdf": m_cdf["PBIAS"],
            "KGE_opl": m_opl["KGE"], "KGE_nocdf": m_nocdf["KGE"], "KGE_cdf": m_cdf["KGE"],
            "NSE_opl": m_opl["NSE"], "NSE_nocdf": m_nocdf["NSE"], "NSE_cdf": m_cdf["NSE"],
            "r_opl": m_opl["r"], "r_nocdf": m_nocdf["r"], "r_cdf": m_cdf["r"]
        })

    df_diag = pd.DataFrame(diag_records)
    csv_diag_path = os.path.join(table_dir, "tableau_diagnostic_5stations.csv")
    df_diag.to_csv(csv_diag_path, index=False)
    print(f"-> Tableau 2 (diagnostic 5 stations) sauvegarde : {csv_diag_path}")

    # =========================================================================
    # FIGURES DÉTAILLÉES POUR SIDI JABEUR ET LALLA CHAFIA (BOUREGREG 2018)
    # =========================================================================
    c_obs = "#1f77b4"    # Bleu
    c_opl = "#7f7f7f"    # Gris
    c_nocdf = "#d62728"  # Rouge
    c_cdf = "#2ca02c"    # Vert

    for sid in ["b_s_jabeur", "b_l_chafia"]:
        m, _ = merged_data[sid]
        nom = meta_dict[sid]["oued"]
        s_nom = "Sidi Jabeur" if sid == "b_s_jabeur" else "Lalla Chafia"
        m_2018 = m[m["date"].str.startswith("2018")].copy().reset_index(drop=True)
        dates_2018 = pd.to_datetime(m_2018["date"]).dt.to_pydatetime()

        fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(13, 9), dpi=150, gridspec_kw={"height_ratios": [1.8, 1.2]})

        # Panneau 1 : Année civile 2018
        max_obs_val = m_2018['q_m3s'].max()
        max_obs_date = m_2018.loc[m_2018['q_m3s'].idxmax(), 'date']
        max_opl_val = m_2018['q_opl'].max()
        max_nocdf_val = m_2018['q_nocdf'].max()
        max_cdf_val = m_2018['q_cdf'].max()

        ax_top.plot(dates_2018, m_2018["q_m3s"].to_numpy(), color=c_obs, lw=1.5, label="Observations ABH", alpha=0.9)
        ax_top.plot(dates_2018, m_2018["q_opl"].to_numpy(), color=c_opl, lw=1.2, label=f"OPL (Moy={m_2018['q_opl'].mean():.1f} m³/s, Max ann.={max_opl_val:.1f})", alpha=0.8)
        ax_top.plot(dates_2018, m_2018["q_nocdf"].to_numpy(), color=c_nocdf, lw=1.2, ls="--", label=f"DA-NoCDF (Moy={m_2018['q_nocdf'].mean():.1f} m³/s, Max ann.={max_nocdf_val:.1f})", alpha=0.85)
        ax_top.plot(dates_2018, m_2018["q_cdf"].to_numpy(), color=c_cdf, lw=1.3, ls="-.", label=f"DA-CDF (Moy={m_2018['q_cdf'].mean():.1f} m³/s, Max ann.={max_cdf_val:.1f})", alpha=0.9)

        ax_top.set_title(f"{s_nom} (Oued {nom}, Bouregreg) — Année civile 2018\n[Haut] Dynamique des débits et crues — Maxima annuels non synchrones (Obs max = {max_obs_val:.1f} m³/s le {max_obs_date})", fontweight="bold", fontsize=11)
        ax_top.set_ylabel("Débit journalier (m³/s)")
        ax_top.grid(True, ls=":", alpha=0.5)
        ax_top.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax_top.xaxis.set_major_locator(mdates.MonthLocator())
        ax_top.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        # Panneau 2 : Faibles débits et étiage avec représentation explicite des zéros
        q_obs_arr = m_2018["q_m3s"].to_numpy()
        q_obs_pos = np.where(q_obs_arr > 0.0, q_obs_arr, np.nan)
        mask_zeros = (q_obs_arr == 0.0)
        dates_assecs = dates_2018[mask_zeros]

        ax_bot.plot(dates_2018, q_obs_pos, color=c_obs, lw=1.5, label="Obs positives (m³/s)", alpha=0.9)
        if len(dates_assecs) > 0:
            ax_bot.scatter(dates_assecs, [0.015]*len(dates_assecs), color="#e377c2", marker="|", s=40, label=f"Assecs observés stricts (0.0 m³/s, {len(dates_assecs)} jours)", zorder=5)

        ax_bot.plot(dates_2018, m_2018["q_opl"].to_numpy(), color=c_opl, lw=1.2, label=f"OPL (Min = {m_2018['q_opl'].min():.2f} m³/s)", alpha=0.8)
        ax_bot.plot(dates_2018, m_2018["q_nocdf"].to_numpy(), color=c_nocdf, lw=1.2, ls="--", label=f"DA-NoCDF (Min = {m_2018['q_nocdf'].min():.2f} m³/s)", alpha=0.85)
        ax_bot.plot(dates_2018, m_2018["q_cdf"].to_numpy(), color=c_cdf, lw=1.3, ls="-.", label=f"DA-CDF (Min = {m_2018['q_cdf'].min():.2f} m³/s)", alpha=0.9)

        ax_bot.set_yscale("log")
        ax_bot.set_ylim(0.01, max(m_2018["q_m3s"].max(), m_2018["q_nocdf"].max()) * 1.5)
        ax_bot.set_title("[Bas] Échelle semi-logarithmique : Étiages et récessions estivales", fontweight="bold", fontsize=10)
        ax_bot.set_ylabel("Débit log10 (m³/s)")
        ax_bot.set_xlabel("Date (2018)")
        ax_bot.grid(True, which="both", ls=":", alpha=0.5)
        ax_bot.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
        ax_bot.xaxis.set_major_locator(mdates.MonthLocator())
        ax_bot.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

        plt.tight_layout()
        fig_path = os.path.join(fig_streamflow_dir, f"fig_detaillee_2018_{sid}.png")
        fig.savefig(fig_path, dpi=150)
        plt.close(fig)
        print(f"-> Figure detaillee 2018 mise a jour : {fig_path}")

    # =========================================================================
    # FIGURE COMPARATIVE MENSUELLE SEBOU (AIN TIMEDRINE, DAR EL HAMRA, PONT DE MDEZ)
    # =========================================================================
    fig_sebou, axes_sebou = plt.subplots(3, 1, figsize=(14, 11), sharex=False, dpi=150)
    sebou_focus = [
        ("ain_timedrine", "Ain Timedrine (Oued Sebou, 4 387 km²)", "CDF : réduction du déficit volumique (PBIAS -56.8% vs -77.3% OPL) et hausse de r (0.62 vs 0.38)"),
        ("dar_el_hamra", "Dar El Hamra (Oued Zloul, 670 km²)", "Contre-exemple : NoCDF plus proche en volume (PBIAS -25.4% vs -45.4% CDF), compensation possible de forçage"),
        ("pont_de_mdez", "Pont de Mdez (Oued Sebou, 3 435 km²)", "CDF : gains relatifs (KGE = +0.07, NSE = +0.02, r = 0.62 contre KGE = -0.19 en OPL)")
    ]

    for idx, (sid, title_s, subtitle_s) in enumerate(sebou_focus):
        ax = axes_sebou[idx]
        m, _ = merged_data[sid]
        dates_m = pd.to_datetime(m["year_month"]).dt.to_pydatetime()
        row_diag = df_diag[df_diag["station_id"] == sid].iloc[0]

        ax.plot(dates_m, m["q_m3s"].to_numpy(), color=c_obs, lw=1.6, marker="o", markersize=4, label=f"Obs ({len(m)} mois jaugés | Moy={row_diag['Q_mean_obs']:.2f} m³/s)", alpha=0.9)
        ax.plot(dates_m, m["q_opl"].to_numpy(), color=c_opl, lw=1.2, label=f"OPL (Moy={row_diag['Q_mean_opl']:.2f} | KGE={row_diag['KGE_opl']:.2f}, r={row_diag['r_opl']:.2f}, PB={row_diag['PBIAS_opl']:+.1f}%)", alpha=0.8)
        ax.plot(dates_m, m["q_nocdf"].to_numpy(), color=c_nocdf, lw=1.2, ls="--", label=f"DA-NoCDF (Moy={row_diag['Q_mean_nocdf']:.2f} | KGE={row_diag['KGE_nocdf']:.2f}, r={row_diag['r_nocdf']:.2f}, PB={row_diag['PBIAS_nocdf']:+.1f}%)", alpha=0.85)
        ax.plot(dates_m, m["q_cdf"].to_numpy(), color=c_cdf, lw=1.4, ls="-.", label=f"DA-CDF (Moy={row_diag['Q_mean_cdf']:.2f} | KGE={row_diag['KGE_cdf']:.2f}, r={row_diag['r_cdf']:.2f}, PB={row_diag['PBIAS_cdf']:+.1f}%)", alpha=0.9)

        ax.set_title(f"{title_s}\nDiagnostic : {subtitle_s}", fontweight="bold", fontsize=10.5)
        ax.set_ylabel("Débit mensuel (m³/s)")
        ax.grid(True, ls=":", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    axes_sebou[-1].set_xlabel("Année (2016–2020)")
    plt.suptitle("Comparaison mensuelle ciblée — Bassin du Sebou (Périodes observées strictes)\nObservations ABH vs Open-Loop vs DA-NoCDF vs DA-CDF", fontweight="bold", fontsize=12, y=0.995)
    plt.tight_layout()
    sebou_path = os.path.join(fig_streamflow_dir, "fig_comparative_mensuelle_sebou.png")
    fig_sebou.savefig(sebou_path, dpi=150)
    plt.close(fig_sebou)
    print(f"-> Figure comparative Sebou mise a jour : {sebou_path}")

    # =========================================================================
    # RECONDUCTION DU TABLEAU DES APPORTS
    # =========================================================================
    print("Recalcul / verification tableau apports 2018...")
    ldt_path = os.path.join(base_dir, "ldt_hymap/lis_input_corrigee.d01.nc")
    ds_ldt = nc.Dataset(ldt_path)
    grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
    flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
    flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
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
                if (pr, pc) not in parents: parents[(pr, pc)] = []
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

    station_masks = {}
    for sid in focus_stations:
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        cat = get_catchment(int(p_row["row_hymap"]), int(p_row["col_hymap"]))
        m = np.zeros((R, C), dtype=bool)
        for cr, cc in cat: m[cr, cc] = True
        station_masks[sid] = m

    def scan_year_runoff(rdir, year=2018):
        files = sorted(glob.glob(os.path.join(rdir, f"{year}*/*.nc")))
        qs_tot = {sid: 0.0 for sid in focus_stations}
        qsb_tot = {sid: 0.0 for sid in focus_stations}
        for f in files:
            with nc.Dataset(f) as ds:
                qs = np.nan_to_num(ds["Qs_tavg"][:])
                qsb = np.nan_to_num(ds["Qsb_tavg"][:])
                if qs.ndim == 3: qs = qs[0]
                if qsb.ndim == 3: qsb = qsb[0]
                vol_qs = np.maximum(qs, 0.0) * 1e-3 * grid_area * 86400.0 / 1e6
                vol_qsb = np.maximum(qsb, 0.0) * 1e-3 * grid_area * 86400.0 / 1e6
                for sid, mask in station_masks.items():
                    qs_tot[sid] += float(np.sum(vol_qs[mask]))
                    qsb_tot[sid] += float(np.sum(vol_qsb[mask]))
        return qs_tot, qsb_tot

    qs_opl, qsb_opl = scan_year_runoff(os.path.join(base_dir, "runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"), 2018)
    qs_nocdf, qsb_nocdf = scan_year_runoff(os.path.join(base_dir, "runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL"), 2018)
    qs_cdf, qsb_cdf = scan_year_runoff(os.path.join(base_dir, "runoff_remap_180x120/DA_cdf_noirr_2016_2020/SURFACEMODEL"), 2018)

    apports_records = []
    for sid in focus_stations:
        p_row = df_p[df_p["station_id"] == sid].iloc[0]
        v_tot_opl = qs_opl[sid] + qsb_opl[sid]
        v_tot_nocdf = qs_nocdf[sid] + qsb_nocdf[sid]
        v_tot_cdf = qs_cdf[sid] + qsb_cdf[sid]

        apports_records.append({
            "station_id": sid, "nom": p_row["nom"], "bassin": p_row["bassin"],
            "Qs_2018_OPL_hm3": qs_opl[sid], "Qsb_2018_OPL_hm3": qsb_opl[sid], "Vtot_2018_OPL_hm3": v_tot_opl,
            "Qs_2018_NoCDF_hm3": qs_nocdf[sid], "Qsb_2018_NoCDF_hm3": qsb_nocdf[sid], "Vtot_2018_NoCDF_hm3": v_tot_nocdf,
            "Qs_2018_CDF_hm3": qs_cdf[sid], "Qsb_2018_CDF_hm3": qsb_cdf[sid], "Vtot_2018_CDF_hm3": v_tot_cdf,
            "Ratio_CDF_NoCDF_pct": (v_tot_cdf / v_tot_nocdf * 100.0) if v_tot_nocdf > 0 else np.nan,
            "Ratio_CDF_OPL_pct": (v_tot_cdf / v_tot_opl * 100.0) if v_tot_opl > 0 else np.nan
        })

    df_apports = pd.DataFrame(apports_records)
    csv_apports_path = os.path.join(table_dir, "tableau_apports_noahmp_2018.csv")
    df_apports.to_csv(csv_apports_path, index=False)
    print(f"-> Tableau 3 (apports amont 2018) sauvegarde : {csv_apports_path}")

    print("\n" + "=" * 95)
    print("FIN DU TRAITEMENT DES LIVRABLES FOCUS SEBOU & BOUREGREG")
    print("=" * 95)

if __name__ == "__main__":
    main()
