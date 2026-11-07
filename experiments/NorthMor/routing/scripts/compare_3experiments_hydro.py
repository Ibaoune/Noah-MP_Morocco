#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compare_3experiments_hydro.py
Comparaison hydrologique tripartite : Open-Loop (OPL) vs DA-NoCDF vs DA-CDF (2016-2020)
aux 12 stations de jaugeage ABH (Bouregreg, Sebou, Ksob).

Auteur: Équipe de modélisation / Antigravity
Date: Novembre 2026
"""

import os, sys, glob, datetime
import numpy as np
import pandas as pd
import scipy.stats as stats
import netCDF4 as nc

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    print("=" * 100)
    print("ÉVALUATION HYDROLOGIQUE COMPARATIVE TRIPARTITE (OPL vs DA-NoCDF vs DA-CDF) AUX 12 STATIONS ABH")
    print("=" * 100)

    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing"
    clean_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/streamflow_clean"
    out_dir = os.path.join(base_dir, "plots/_history/comparison_3experiments_raw")
    os.makedirs(out_dir, exist_ok=True)

    opl_out_dir = os.path.join(base_dir, "output/OPL_2016_2020_corrigee")
    da_nocdf_dir = os.path.join(base_dir, "output/DA_nocdf_2016_2020")
    da_cdf_dir = os.path.join(base_dir, "output/DA_cdf_2016_2020")

    pairing_csv = os.path.join(base_dir, "stations/hymap_stations_pairing.csv")
    df_p = pd.read_csv(pairing_csv)

    df_obs_daily = pd.read_csv(os.path.join(clean_dir, "obs_daily.csv"))
    df_obs_monthly = pd.read_csv(os.path.join(clean_dir, "obs_monthly.csv"))
    df_obs_monthly["year_month"] = df_obs_monthly["annee"].astype(str) + "-" + df_obs_monthly["mois"].astype(str).str.zfill(2)

    # 1. Extraction / Chargement DA-CDF
    sim_da_cdf_cache = os.path.join(da_cdf_dir, "t9_sim_daily_12stations_da_cdf.csv")
    if os.path.exists(sim_da_cdf_cache):
        print(f"-> Chargement des debits DA-CDF depuis le cache : {sim_da_cdf_cache}")
        df_q_cdf_d = pd.read_csv(sim_da_cdf_cache)
    else:
        print(f"-> Extraction des debits journaliers DA-CDF depuis les 1 827 LIS_HIST...")
        hist_files = sorted(glob.glob(os.path.join(da_cdf_dir, "ROUTING/20*/**/LIS_HIST_*.nc"), recursive=True))
        if len(hist_files) < 1827:
            raise RuntimeError(f"Fichiers LIS_HIST incomplets pour DA-CDF ({len(hist_files)} / 1827)")
        
        records = []
        for fpath in hist_files:
            with nc.Dataset(fpath) as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                dt_str = sim_dt.strftime("%Y-%m-%d")

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3: flow = flow[0]
                row_dict = {"date": dt_str}
                for _, row in df_p.iterrows():
                    sid = row["station_id"]
                    r, c = int(row["row_hymap"]), int(row["col_hymap"])
                    row_dict[sid] = float(flow[r, c])
                records.append(row_dict)
        
        df_q_cdf_d = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
        df_q_cdf_d.to_csv(sim_da_cdf_cache, index=False)
        print(f"   Extraction DA-CDF terminee ({len(df_q_cdf_d)} jours sauvegardes dans {sim_da_cdf_cache}).")

    # 2. Chargement OPL et DA-NoCDF
    sim_opl_cache = os.path.join(opl_out_dir, "t7_sim_daily_12stations_corrigee.csv")
    sim_nocdf_cache = os.path.join(da_nocdf_dir, "t8_sim_daily_12stations_da_nocdf.csv")
    df_q_opl_d = pd.read_csv(sim_opl_cache)
    df_q_nocdf_d = pd.read_csv(sim_nocdf_cache)

    # Agregations mensuelles
    df_q_cdf_d["year_month"] = pd.to_datetime(df_q_cdf_d["date"]).dt.to_period("M").astype(str)
    df_q_cdf_m = df_q_cdf_d.groupby("year_month").mean(numeric_only=True).reset_index()

    df_q_opl_d["year_month"] = pd.to_datetime(df_q_opl_d["date"]).dt.to_period("M").astype(str)
    df_q_opl_m = df_q_opl_d.groupby("year_month").mean(numeric_only=True).reset_index()

    df_q_nocdf_d["year_month"] = pd.to_datetime(df_q_nocdf_d["date"]).dt.to_period("M").astype(str)
    df_q_nocdf_m = df_q_nocdf_d.groupby("year_month").mean(numeric_only=True).reset_index()

    # Dictionnaire de métadonnées
    meta_dict = {
        "b_a_loudah": {"ire": "2673/20", "oued": "Korifla", "aire_off": 697.6, "note": "Duplication obs avec S.M. Cherif"},
        "b_s_cherif": {"ire": "2674/20", "oued": "Mechraa", "aire_off": 649.5, "note": "Duplication obs avec Ain Loudah"},
        "b_s_jabeur": {"ire": "964/21",  "oued": "Grou",    "aire_off": 3138.5, "note": "Station de reference Bouregreg"},
        "b_l_chafia": {"ire": "963/21",  "oued": "Bouregreg","aire_off": 3341.6, "note": "Station aval Bouregreg"},
        "adamna":     {"ire": "402/52",  "oued": "Ksob",    "aire_off": 1617.0, "note": "20 mois observes (33.3%)"},
        "ain_timedrine": {"ire": "581/22", "oued": "Sebou", "aire_off": 4387.0, "note": "60 mois observes"},
        "ait_khabbach":  {"ire": "585/22", "oued": "Guigou", "aire_off": 1240.0, "note": "44 mois observes (73.3%)"},
        "azzaba":        {"ire": "583/22", "oued": "Sebou", "aire_off": 4640.0, "note": "60 mois observes"},
        "dar_el_hamra":  {"ire": "1000/23","oued": "Zloul", "aire_off": 670.0,  "note": "60 mois observes"},
        "el_mers":       {"ire": "541/23", "oued": "Masser","aire_off": 1004.0, "note": "20 mois observes (33.3%)"},
        "pont_ait_aissa":{"ire": "198/30", "oued": "Guigou","aire_off": 205.0,  "note": "60 mois observes"},
        "pont_de_mdez":  {"ire": "582/22", "oued": "Sebou", "aire_off": 3435.0, "note": "44 mois observes (73.3%)"}
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
                "mean_sim": float(np.mean(sim)), "mean_obs": float(np.mean(obs))}

    records_metrics = []
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

        records_metrics.append({
            "station_id": sid,
            "nom": nom,
            "oued": meta["oued"],
            "bassin": bassin,
            "pas": pas,
            "n_obs": len(o),
            "note": meta["note"],
            # KGE
            "KGE_opl": m_opl["KGE"],
            "KGE_nocdf": m_nocdf["KGE"],
            "KGE_cdf": m_cdf["KGE"],
            "dKGE_nocdf_opl": m_nocdf["KGE"] - m_opl["KGE"],
            "dKGE_cdf_opl": m_cdf["KGE"] - m_opl["KGE"],
            "dKGE_cdf_nocdf": m_cdf["KGE"] - m_nocdf["KGE"],
            # Correlation
            "r_opl": m_opl["r"],
            "r_nocdf": m_nocdf["r"],
            "r_cdf": m_cdf["r"],
            "dr_nocdf_opl": m_nocdf["r"] - m_opl["r"],
            "dr_cdf_opl": m_cdf["r"] - m_opl["r"],
            "dr_cdf_nocdf": m_cdf["r"] - m_nocdf["r"],
            # NSE
            "NSE_opl": m_opl["NSE"],
            "NSE_nocdf": m_nocdf["NSE"],
            "NSE_cdf": m_cdf["NSE"],
            "dNSE_nocdf_opl": m_nocdf["NSE"] - m_opl["NSE"],
            "dNSE_cdf_opl": m_cdf["NSE"] - m_opl["NSE"],
            "dNSE_cdf_nocdf": m_cdf["NSE"] - m_nocdf["NSE"],
            # PBIAS
            "PBIAS_opl": m_opl["PBIAS"],
            "PBIAS_nocdf": m_nocdf["PBIAS"],
            "PBIAS_cdf": m_cdf["PBIAS"],
            "dPBIAS_nocdf_opl": m_nocdf["PBIAS"] - m_opl["PBIAS"],
            "dPBIAS_cdf_opl": m_cdf["PBIAS"] - m_opl["PBIAS"],
            "dPBIAS_cdf_nocdf": m_cdf["PBIAS"] - m_nocdf["PBIAS"],
            # Means
            "mean_obs": m_opl["mean_obs"],
            "mean_opl": m_opl["mean_sim"],
            "mean_nocdf": m_nocdf["mean_sim"],
            "mean_cdf": m_cdf["mean_sim"]
        })

    df_res = pd.DataFrame(records_metrics)
    csv_res_path = os.path.join(out_dir, "synthese_comparative_12stations_3exp.csv")
    df_res.to_csv(csv_res_path, index=False)
    print(f"\n-> Synthese metrique sauvegardee dans : {csv_res_path}")

    # =========================================================================
    # AFFICHAGE TERMINAL DES RESULTATS
    # =========================================================================
    print("\n" + "=" * 115)
    print("TABLEAU 1 : KGE-2009 & ECARTS DE PERFORMANCE PAR STATION")
    print("=" * 115)
    header = f"{'Station':16s} | {'Bassin':9s} | {'Pas':4s} | {'N':4s} | {'KGE OPL':8s} | {'KGE NoCDF':9s} | {'KGE CDF':8s} | {'Δ(NoCDF-OL)':11s} | {'Δ(CDF-OL)':10s} | {'Δ(CDF-NoCDF)':12s}"
    print(header)
    print("-" * 115)
    for _, r in df_res.iterrows():
        print(f"{r['nom']:16s} | {r['bassin']:9s} | {r['pas'][:4]:4s} | {r['n_obs']:4d} | {r['KGE_opl']:8.3f} | {r['KGE_nocdf']:9.3f} | {r['KGE_cdf']:8.3f} | {r['dKGE_nocdf_opl']:+11.3f} | {r['dKGE_cdf_opl']:+10.3f} | {r['dKGE_cdf_nocdf']:+12.3f}")

    print("\n" + "=" * 115)
    print("TABLEAU 2 : CORRELATION (r) & NSE PAR STATION")
    print("=" * 115)
    header2 = f"{'Station':16s} | {'r OPL':6s} | {'r NoCDF':7s} | {'r CDF':6s} | {'Δr(CDF-OL)':10s} | {'NSE OPL':8s} | {'NSE NoCDF':9s} | {'NSE CDF':8s} | {'ΔNSE(CDF-OL)':12s}"
    print(header2)
    print("-" * 115)
    for _, r in df_res.iterrows():
        print(f"{r['nom']:16s} | {r['r_opl']:6.3f} | {r['r_nocdf']:7.3f} | {r['r_cdf']:6.3f} | {r['dr_cdf_opl']:+10.3f} | {r['NSE_opl']:8.3f} | {r['NSE_nocdf']:9.3f} | {r['NSE_cdf']:8.3f} | {r['dNSE_cdf_opl']:+12.3f}")

    print("\n" + "=" * 115)
    print("TABLEAU 3 : BIAIS RELATIF (PBIAS %) & DEBITS MOYENS (m3/s)")
    print("=" * 115)
    header3 = f"{'Station':16s} | {'Obs':6s} | {'Q_OPL':6s} | {'Q_NoCDF':7s} | {'Q_CDF':6s} | {'PB OPL (%)':11s} | {'PB NoCDF(%)':12s} | {'PB CDF (%)':11s} | {'ΔPB(CDF-NoCDF)':14s}"
    print(header3)
    print("-" * 115)
    for _, r in df_res.iterrows():
        print(f"{r['nom']:16s} | {r['mean_obs']:6.2f} | {r['mean_opl']:6.2f} | {r['mean_nocdf']:7.2f} | {r['mean_cdf']:6.2f} | {r['PBIAS_opl']:+10.1f}% | {r['PBIAS_nocdf']:+11.1f}% | {r['PBIAS_cdf']:+10.1f}% | {r['dPBIAS_cdf_nocdf']:+13.1f}%")

    # =========================================================================
    # PRODUCTION DES FIGURES COMPARATIVES
    # =========================================================================
    print("\n" + "=" * 100)
    print("GÉNÉRATION DES HYDROGRAMMES COMPARATIFS (OPL vs DA-NoCDF vs DA-CDF vs OBS)")
    print("=" * 100)

    c_obs = "#1f77b4"    # Bleu
    c_opl = "#7f7f7f"    # Gris foncé
    c_nocdf = "#d62728"  # Rouge
    c_cdf = "#2ca02c"    # Vert

    priority_stations = [
        ("b_s_jabeur", "Sidi Jabeur", "Grou", "Bouregreg", "journalier"),
        ("b_l_chafia", "Lalla Chafia", "Bouregreg", "Bouregreg", "journalier"),
        ("ain_timedrine", "Ain Timedrine", "Sebou", "Sebou", "mensuel"),
        ("azzaba", "Azzaba", "Sebou", "Sebou", "mensuel"),
        ("adamna", "Adamna", "Ksob", "Ksob", "mensuel")
    ]

    # Figure composite 5 stations prioritaires
    fig, axes = plt.subplots(5, 1, figsize=(15, 18), dpi=150)
    for idx, (sid, nom, oued, bassin, pas) in enumerate(priority_stations):
        ax = axes[idx]
        m, time_col = merged_data[sid]
        r_meta = df_res[df_res["station_id"] == sid].iloc[0]

        if pas == "journalier":
            dates = pd.to_datetime(m["date"])
            ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.2, label=f"Observations (N={r_meta['n_obs']})", alpha=0.85)
            ax.plot(dates, m["q_opl"], color=c_opl, lw=1.1, label=f"OPL (KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PB={r_meta['PBIAS_opl']:+.1f}%)", alpha=0.8)
            ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.1, linestyle="--", label=f"DA-NoCDF (KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PB={r_meta['PBIAS_nocdf']:+.1f}%)", alpha=0.85)
            ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.2, linestyle="-.", label=f"DA-CDF (KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PB={r_meta['PBIAS_cdf']:+.1f}%)", alpha=0.9)
        else:
            dates = pd.to_datetime(m["year_month"])
            ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.6, marker="o", markersize=4, label=f"Observations (N={r_meta['n_obs']})", alpha=0.9)
            ax.plot(dates, m["q_opl"], color=c_opl, lw=1.3, label=f"OPL (KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PB={r_meta['PBIAS_opl']:+.1f}%)", alpha=0.85)
            ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.3, linestyle="--", label=f"DA-NoCDF (KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PB={r_meta['PBIAS_nocdf']:+.1f}%)", alpha=0.85)
            ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.4, linestyle="-.", label=f"DA-CDF (KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PB={r_meta['PBIAS_cdf']:+.1f}%)", alpha=0.9)

        ax.set_title(f"{nom} — Oued {oued} ({bassin}) | Pas: {pas} | Note: {r_meta['note']}", fontweight="bold", fontsize=11)
        ax.set_ylabel("Débit (m³/s)")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

    axes[-1].set_xlabel("Année")
    plt.suptitle("Hydrogrammes comparatifs aux 5 stations prioritaires (2016–2020)\nObservations vs OPL vs DA-NoCDF vs DA-CDF", fontweight="bold", fontsize=13, y=0.995)
    plt.tight_layout()
    fig5_path = os.path.join(out_dir, "hydrogrammes_5stations_prioritaires.png")
    fig.savefig(fig5_path, dpi=150)
    plt.close(fig)
    print(f"-> Figure composite 5 stations générée : {fig5_path}")

    # Figures individuelles pour les 5 stations prioritaires
    for sid, nom, oued, bassin, pas in priority_stations:
        fig_s, ax = plt.subplots(figsize=(12, 5.5), dpi=150)
        m, time_col = merged_data[sid]
        r_meta = df_res[df_res["station_id"] == sid].iloc[0]

        if pas == "journalier":
            dates = pd.to_datetime(m["date"])
            ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.3, label=f"Observations jaugées (N={r_meta['n_obs']})", alpha=0.85)
            ax.plot(dates, m["q_opl"], color=c_opl, lw=1.1, label=f"OPL | KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PBIAS={r_meta['PBIAS_opl']:+.1f}%", alpha=0.8)
            ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.1, linestyle="--", label=f"DA-NoCDF | KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PBIAS={r_meta['PBIAS_nocdf']:+.1f}%", alpha=0.85)
            ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.2, linestyle="-.", label=f"DA-CDF | KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PBIAS={r_meta['PBIAS_cdf']:+.1f}%", alpha=0.9)
        else:
            dates = pd.to_datetime(m["year_month"])
            ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.7, marker="o", markersize=4.5, label=f"Observations jaugées (N={r_meta['n_obs']})", alpha=0.9)
            ax.plot(dates, m["q_opl"], color=c_opl, lw=1.3, label=f"OPL | KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PBIAS={r_meta['PBIAS_opl']:+.1f}%", alpha=0.85)
            ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.3, linestyle="--", label=f"DA-NoCDF | KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PBIAS={r_meta['PBIAS_nocdf']:+.1f}%", alpha=0.85)
            ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.4, linestyle="-.", label=f"DA-CDF | KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PBIAS={r_meta['PBIAS_cdf']:+.1f}%", alpha=0.9)

        ax.set_title(f"Hydrogramme comparatif — {nom} (Oued {oued}, Bassin {bassin})\nPas {pas} (2016–2020) | {r_meta['note']}", fontweight="bold", fontsize=11)
        ax.set_ylabel("Débit (m³/s)")
        ax.set_xlabel("Année")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=9.5)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        plt.tight_layout()
        single_path = os.path.join(out_dir, f"hydrogramme_{sid}.png")
        fig_s.savefig(single_path, dpi=150)
        plt.close(fig_s)
        print(f"   -> Hydrogramme individuel : {single_path}")

    # Figures par bassin (Bouregreg, Sebou, Ksob)
    # Bouregreg (4 stations)
    fig_b, axes_b = plt.subplots(4, 1, figsize=(14, 13), sharex=True, dpi=150)
    b_st = ["b_s_jabeur", "b_l_chafia", "b_a_loudah", "b_s_cherif"]
    for idx, sid in enumerate(b_st):
        ax = axes_b[idx]
        m, _ = merged_data[sid]
        r_meta = df_res[df_res["station_id"] == sid].iloc[0]
        dates = pd.to_datetime(m["date"])
        ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.1, label=f"Obs ({r_meta['n_obs']} j)", alpha=0.85)
        ax.plot(dates, m["q_opl"], color=c_opl, lw=1.0, label=f"OPL (KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PB={r_meta['PBIAS_opl']:+.1f}%)", alpha=0.8)
        ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.0, ls="--", label=f"DA-NoCDF (KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PB={r_meta['PBIAS_nocdf']:+.1f}%)", alpha=0.85)
        ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.1, ls="-.", label=f"DA-CDF (KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PB={r_meta['PBIAS_cdf']:+.1f}%)", alpha=0.9)
        ax.set_title(f"{r_meta['nom']} — Oued {r_meta['oued']} | {r_meta['note']}", fontweight="bold", fontsize=10)
        ax.set_ylabel("Débit (m³/s)")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
    axes_b[-1].set_xlabel("Année")
    axes_b[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes_b[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.suptitle("Hydrogrammes journaliers — Bassin du Bouregreg (2016–2020) : OPL vs DA-NoCDF vs DA-CDF", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig_b.savefig(os.path.join(out_dir, "F_hydrogrammes_bouregreg_3exp.png"), dpi=150)
    plt.close(fig_b)

    # Sebou (7 stations)
    fig_s, axes_s = plt.subplots(7, 1, figsize=(14, 17), sharex=True, dpi=150)
    s_st = ["azzaba", "ain_timedrine", "dar_el_hamra", "pont_ait_aissa", "pont_de_mdez", "ait_khabbach", "el_mers"]
    for idx, sid in enumerate(s_st):
        ax = axes_s[idx]
        m, _ = merged_data[sid]
        r_meta = df_res[df_res["station_id"] == sid].iloc[0]
        dates = pd.to_datetime(m["year_month"])
        ax.plot(dates, m["q_m3s"], color=c_obs, lw=1.5, marker="o", markersize=3.5, label=f"Obs ({r_meta['n_obs']} mois)", alpha=0.85)
        ax.plot(dates, m["q_opl"], color=c_opl, lw=1.2, label=f"OPL (KGE={r_meta['KGE_opl']:.2f}, r={r_meta['r_opl']:.2f}, PB={r_meta['PBIAS_opl']:+.1f}%)", alpha=0.85)
        ax.plot(dates, m["q_nocdf"], color=c_nocdf, lw=1.2, ls="--", label=f"DA-NoCDF (KGE={r_meta['KGE_nocdf']:.2f}, r={r_meta['r_nocdf']:.2f}, PB={r_meta['PBIAS_nocdf']:+.1f}%)", alpha=0.85)
        ax.plot(dates, m["q_cdf"], color=c_cdf, lw=1.3, ls="-.", label=f"DA-CDF (KGE={r_meta['KGE_cdf']:.2f}, r={r_meta['r_cdf']:.2f}, PB={r_meta['PBIAS_cdf']:+.1f}%)", alpha=0.9)
        ax.set_title(f"{r_meta['nom']} — Oued {r_meta['oued']} | {r_meta['note']}", fontweight="bold", fontsize=10)
        ax.set_ylabel("Débit (m³/s)")
        ax.grid(True, linestyle=":", alpha=0.5)
        ax.legend(loc="upper right", framealpha=0.9, fontsize=8.5)
    axes_s[-1].set_xlabel("Année")
    axes_s[-1].xaxis.set_major_locator(mdates.YearLocator())
    axes_s[-1].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.suptitle("Hydrogrammes mensuels — Bassin du Sebou (2016–2020) : OPL vs DA-NoCDF vs DA-CDF", fontweight="bold", y=0.995)
    plt.tight_layout()
    fig_s.savefig(os.path.join(out_dir, "F_hydrogrammes_sebou_3exp.png"), dpi=150)
    plt.close(fig_s)

    print("\n-> Toutes les figures et syntheses ont ete produites avec succes dans :", out_dir)

if __name__ == "__main__":
    main()
