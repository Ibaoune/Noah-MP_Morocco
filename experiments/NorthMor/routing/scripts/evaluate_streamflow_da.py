#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
evaluate_streamflow_da.py
-------------------------
Evaluation hydrologique standardisee et modulaire des debits simules par HyMAP (HyMAP-2 / HyMAP-3)
face aux observations hydrometriques ABH (Open-Loop, DA-NoCDF, DA-CDF).

Metriques calculees par station et par experience :
  - KGE (Gupta et al., 2009) et ses 3 composantes :
      * r     : coefficient de correlation lineaire de Pearson
      * alpha : ratio de variabilite (sigma_sim / sigma_obs)
      * beta  : ratio des moyennes (mu_sim / mu_obs)
  - NSE (Nash & Sutcliffe, 1970)
  - log_NSE (NSE sur debits logarithmiques avec offset epsilon)
  - Scores saisonniers :
      * Saison humide (Octobre a Mai) : KGE, r, alpha, beta, NSE, log_NSE
      * Ete (Juin a Septembre)        : KGE, r, alpha, beta, NSE, log_NSE
  - Debits moyens d ete observes et simules

Sorties :
  - Tableaux de metriques CSV (global, saisonnier, composantes KGE)
  - Figure multi-panneaux des composantes du KGE par station et experience (libelles en anglais)
  - Hydrogrammes chronologiques pour les stations selectionnees

Compatible avec toute version de routage (HyMAP-2 ou HyMAP-3).
"""

import os
import sys
import argparse
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

STATION_ORDER = [
    "b_a_loudah", "b_l_chafia", "b_s_cherif", "b_s_jabeur",
    "ain_timedrine", "ait_khabbach", "azzaba", "dar_el_hamra",
    "el_mers", "pont_ait_aissa", "pont_de_mdez", "adamna"
]

STATION_METADATA = {
    "b_a_loudah": {"name": "Ain Loudah", "basin": "Bouregreg", "oued": "Korifla", "area": 697.6},
    "b_l_chafia": {"name": "Lalla Chafia", "basin": "Bouregreg", "oued": "Bouregreg", "area": 3341.6},
    "b_s_cherif": {"name": "S.M. Cherif", "basin": "Bouregreg", "oued": "Mechraa", "area": 649.5},
    "b_s_jabeur": {"name": "Sidi Jabeur", "basin": "Bouregreg", "oued": "Grou", "area": 3138.5},
    "ain_timedrine": {"name": "Ain Timedrine", "basin": "Sebou", "oued": "Sebou", "area": 4387.0},
    "ait_khabbach": {"name": "Ait Khabbach", "basin": "Sebou", "oued": "Guigou", "area": 1240.0},
    "azzaba": {"name": "Azzaba", "basin": "Sebou", "oued": "Sebou", "area": 4640.0},
    "dar_el_hamra": {"name": "Dar El Hamra", "basin": "Sebou", "oued": "Zloul", "area": 670.0},
    "el_mers": {"name": "El Mers", "basin": "Sebou", "oued": "Masser", "area": 1004.0},
    "pont_ait_aissa": {"name": "Pont Ait Aissa", "basin": "Sebou", "oued": "Guigou", "area": 205.0},
    "pont_de_mdez": {"name": "Pont de Mdez", "basin": "Sebou", "oued": "Sebou", "area": 3435.0},
    "adamna": {"name": "Adamna", "basin": "Ksob", "oued": "Ksob", "area": 1617.0},
}


def compute_metrics(obs, sim, eps=0.01):
    """Calcule KGE (r, alpha, beta), NSE, log-NSE et biais."""
    n = len(obs)
    if n < 3:
        return {
            "n": n, "mean_obs": np.nan, "mean_sim": np.nan,
            "bias": np.nan, "rel_bias": np.nan, "rmse": np.nan,
            "r": np.nan, "alpha": np.nan, "beta": np.nan,
            "kge": np.nan, "nse": np.nan, "log_nse": np.nan
        }

    mu_o = float(np.mean(obs))
    mu_s = float(np.mean(sim))
    std_o = float(np.std(obs, ddof=0))
    std_s = float(np.std(sim, ddof=0))

    bias = mu_s - mu_o
    rel_bias = (bias / (mu_o + 1e-12)) * 100.0
    rmse = float(np.sqrt(np.mean((sim - obs) ** 2)))

    # Pearson r
    if std_o > 1e-12 and std_s > 1e-12:
        r = float(np.corrcoef(obs, sim)[0, 1])
        alpha = float(std_s / std_o)
    else:
        r = np.nan
        alpha = np.nan

    # Beta
    beta = float(mu_s / (mu_o + 1e-12)) if mu_o > 1e-12 else np.nan

    # KGE
    if not np.isnan(r) and not np.isnan(alpha) and not np.isnan(beta):
        ed = np.sqrt((r - 1.0) ** 2 + (alpha - 1.0) ** 2 + (beta - 1.0) ** 2)
        kge = float(1.0 - ed)
    else:
        kge = np.nan

    # NSE
    denom_nse = np.sum((obs - mu_o) ** 2)
    if denom_nse > 1e-12:
        nse = float(1.0 - (np.sum((sim - obs) ** 2) / denom_nse))
    else:
        nse = np.nan

    # Log-NSE
    log_o = np.log(np.maximum(obs, 0.0) + eps)
    log_s = np.log(np.maximum(sim, 0.0) + eps)
    denom_log = np.sum((log_o - np.mean(log_o)) ** 2)
    if denom_log > 1e-12:
        log_nse = float(1.0 - (np.sum((log_s - log_o) ** 2) / denom_log))
    else:
        log_nse = np.nan

    return {
        "n": n, "mean_obs": mu_o, "mean_sim": mu_s,
        "bias": bias, "rel_bias": rel_bias, "rmse": rmse,
        "r": r, "alpha": alpha, "beta": beta,
        "kge": kge, "nse": nse, "log_nse": log_nse
    }


def load_observations(obs_daily_file, obs_monthly_file=None):
    """Charge et structure les observations journalieres et mensuelles."""
    obs_dict = {}

    if obs_daily_file and os.path.isfile(obs_daily_file):
        df_d = pd.read_csv(obs_daily_file)
        if "station_id" in df_d.columns and "date" in df_d.columns and "q_m3s" in df_d.columns:
            for sid, group in df_d.groupby("station_id"):
                sub = group[["date", "q_m3s"]].dropna().copy()
                sub["date"] = pd.to_datetime(sub["date"]).dt.strftime("%Y-%m-%d")
                obs_dict[sid] = {"timestep": "daily", "df": sub}

    if obs_monthly_file and os.path.isfile(obs_monthly_file):
        df_m = pd.read_csv(obs_monthly_file)
        if "station_id" in df_m.columns and "q_m3s" in df_m.columns:
            if "annee" in df_m.columns and "mois" in df_m.columns:
                df_m["year_month"] = df_m["annee"].astype(str) + "-" + df_m["mois"].astype(str).str.zfill(2)
            for sid, group in df_m.groupby("station_id"):
                if sid not in obs_dict: # Ne pas ecraser si une observation journaliere existe deja
                    sub = group[["year_month", "q_m3s"]].dropna().copy()
                    obs_dict[sid] = {"timestep": "monthly", "df": sub}

    return obs_dict


def evaluate_streamflow(sim_files, obs_dict, start_date="2017-01-01", end_date="2020-12-31", eps=0.01):
    """Effectue le calcul complet des metriques globales et saisonnieres."""
    records_overall = []
    records_seasonal = []
    paired_series = {} # { (station_id, exp_name): df_paired }

    # Charger les simulations
    sim_dfs = {}
    for exp_name, path in sim_files.items():
        if path and os.path.isfile(path):
            df = pd.read_csv(path)
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")
            df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()
            sim_dfs[exp_name] = df
        else:
            print(f"[AVERTISSEMENT] Fichier de simulation introuvable pour {exp_name} : {path}")

    all_stations = [s for s in STATION_ORDER if s in obs_dict]

    for sid in all_stations:
        obs_info = obs_dict[sid]
        step = obs_info["timestep"]
        df_o = obs_info["df"]

        meta = STATION_METADATA.get(sid, {"name": sid, "basin": "Unknown", "oued": "Unknown", "area": np.nan})

        for exp_name, df_s in sim_dfs.items():
            if sid not in df_s.columns:
                continue

            if step == "daily":
                # Appariement journalier
                df_sub_s = df_s[["date", sid]].rename(columns={sid: "q_sim"})
                m = pd.merge(df_o, df_sub_s, on="date").dropna().sort_values("date").reset_index(drop=True)
                m["month"] = pd.to_datetime(m["date"]).dt.month
            else:
                # Agregation mensuelle du journalier simule
                df_s_copy = df_s[["date", sid]].copy()
                df_s_copy["year_month"] = pd.to_datetime(df_s_copy["date"]).dt.strftime("%Y-%m")
                df_s_m = df_s_copy.groupby("year_month")[sid].mean().reset_index().rename(columns={sid: "q_sim"})
                m = pd.merge(df_o, df_s_m, on="year_month").dropna().sort_values("year_month").reset_index(drop=True)
                m["month"] = pd.to_datetime(m["year_month"] + "-01").dt.month

            if len(m) == 0:
                continue

            paired_series[(sid, exp_name)] = m

            # 1. Metriques globales (pluriannuelles)
            res_all = compute_metrics(m["q_m3s"].to_numpy(), m["q_sim"].to_numpy(), eps=eps)
            records_overall.append({
                "station_id": sid,
                "name": meta["name"],
                "basin": meta["basin"],
                "area_km2": meta["area"],
                "experiment": exp_name,
                "timestep": step,
                "n_obs": res_all["n"],
                "q_obs_mean": round(res_all["mean_obs"], 3),
                "q_sim_mean": round(res_all["mean_sim"], 3),
                "bias": round(res_all["bias"], 3),
                "rel_bias_pct": round(res_all["rel_bias"], 1),
                "rmse": round(res_all["rmse"], 3),
                "r": round(res_all["r"], 3),
                "alpha": round(res_all["alpha"], 3),
                "beta": round(res_all["beta"], 3),
                "kge": round(res_all["kge"], 3),
                "nse": round(res_all["nse"], 3),
                "log_nse": round(res_all["log_nse"], 3)
            })

            # 2. Metriques saison humide (Oct-Mai : mois 10,11,12, 1,2,3,4,5)
            m_wet = m[m["month"].isin([10, 11, 12, 1, 2, 3, 4, 5])]
            res_wet = compute_metrics(m_wet["q_m3s"].to_numpy(), m_wet["q_sim"].to_numpy(), eps=eps)

            # 3. Metriques ete (Juin-Sept : mois 6,7,8,9)
            m_dry = m[m["month"].isin([6, 7, 8, 9])]
            res_dry = compute_metrics(m_dry["q_m3s"].to_numpy(), m_dry["q_sim"].to_numpy(), eps=eps)

            records_seasonal.append({
                "station_id": sid,
                "name": meta["name"],
                "basin": meta["basin"],
                "experiment": exp_name,
                # Saison humide
                "n_wet": res_wet["n"],
                "q_obs_wet": round(res_wet["mean_obs"], 3),
                "q_sim_wet": round(res_wet["mean_sim"], 3),
                "r_wet": round(res_wet["r"], 3),
                "alpha_wet": round(res_wet["alpha"], 3),
                "beta_wet": round(res_wet["beta"], 3),
                "kge_wet": round(res_wet["kge"], 3),
                "nse_wet": round(res_wet["nse"], 3),
                "log_nse_wet": round(res_wet["log_nse"], 3),
                # Ete
                "n_summer": res_dry["n"],
                "q_obs_summer": round(res_dry["mean_obs"], 3),
                "q_sim_summer": round(res_dry["mean_sim"], 3),
                "r_summer": round(res_dry["r"], 3),
                "alpha_summer": round(res_dry["alpha"], 3),
                "beta_summer": round(res_dry["beta"], 3),
                "kge_summer": round(res_dry["kge"], 3),
                "nse_summer": round(res_dry["nse"], 3),
                "log_nse_summer": round(res_dry["log_nse"], 3),
            })

    df_overall = pd.DataFrame(records_overall)
    df_seasonal = pd.DataFrame(records_seasonal)

    return df_overall, df_seasonal, paired_series


def plot_kge_components_figure(df_overall, out_png_path):
    """Genere la figure publication 2x2 des composantes du KGE par station et experience."""
    if df_overall.empty:
        return

    stations = [s for s in STATION_ORDER if s in df_overall["station_id"].unique()]
    exps = list(df_overall["experiment"].unique())

    # Mapping couleurs experiences
    colors = {
        "OL": "#1f77b4",       # bleu
        "NoCDF": "#ff7f0e",    # orange
        "CDF": "#2ca02c",      # vert
    }
    default_colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]

    fig, axes = plt.subplots(2, 2, figsize=(14, 9), dpi=300)
    plt.rcParams["font.sans-serif"] = "DejaVu Sans"

    metrics = [
        ("kge", "Kling-Gupta Efficiency (KGE)", 1.0, (-0.6, 1.05)),
        ("r", "Linear Correlation (r)", 1.0, (-0.2, 1.05)),
        ("alpha", "Variability Ratio (α = σ_sim / σ_obs)", 1.0, (0.0, 2.5)),
        ("beta", "Mean Bias Ratio (β = μ_sim / μ_obs)", 1.0, (0.0, 3.5)),
    ]

    x = np.arange(len(stations))
    n_exps = len(exps)
    width = 0.8 / max(n_exps, 1)

    station_labels = [STATION_METADATA.get(s, {}).get("name", s) for s in stations]

    for idx, (m_col, m_title, ref_val, y_lim) in enumerate(metrics):
        ax = axes[idx // 2, idx % 2]

        for i_exp, exp in enumerate(exps):
            sub = df_overall[df_overall["experiment"] == exp].set_index("station_id")
            vals = [sub.loc[s, m_col] if s in sub.index else np.nan for s in stations]
            offset = (i_exp - (n_exps - 1) / 2) * width
            c = colors.get(exp, default_colors[i_exp % len(default_colors)])
            ax.bar(x + offset, vals, width, label=exp if idx == 0 else "", color=c, alpha=0.88, edgecolor="#333333", lw=0.6)

        # Ligne de reference optimale
        ax.axhline(ref_val, color="#d62728", ls="--", lw=1.2, alpha=0.85, label="Optimal (= 1.0)" if idx == 0 else "")
        if m_col == "kge":
            ax.axhline(0.0, color="#888888", ls=":", lw=0.9, alpha=0.7)

        ax.set_title(m_title, fontsize=11, fontweight="bold", pad=8)
        ax.set_xticks(x)
        ax.set_xticklabels(station_labels, rotation=35, ha="right", fontsize=8.5)
        ax.set_ylim(y_lim)
        ax.grid(True, axis="y", ls=":", alpha=0.6)
        ax.tick_params(axis="both", labelsize=8.5)

    fig.legend(loc="upper center", bbox_to_anchor=(0.5, 0.985), ncol=n_exps + 1, frameon=True, fontsize=10)
    plt.subplots_adjust(top=0.92, bottom=0.12, hspace=0.36, wspace=0.18, left=0.06, right=0.97)

    plt.savefig(out_png_path, dpi=300)
    pdf_path = out_png_path.replace(".png", ".pdf")
    plt.savefig(pdf_path, dpi=300)
    plt.close(fig)
    print(f"-> Figure KGE enregistree : {out_png_path} et {pdf_path}")


def plot_station_hydrographs(paired_series, selected_stations, out_dir):
    """Genere les hydrogrammes chronologiques pour les stations demandees."""
    os.makedirs(out_dir, exist_ok=True)
    c_obs = "#111111"
    colors_exp = {"OL": "#1f77b4", "NoCDF": "#ff7f0e", "CDF": "#2ca02c"}

    for sid in selected_stations:
        # Trouver toutes les series pour cette station
        exp_data = {exp: df for (s, exp), df in paired_series.items() if s == sid}
        if not exp_data:
            continue

        first_exp = list(exp_data.keys())[0]
        df_base = exp_data[first_exp]
        step = "Daily" if "date" in df_base.columns else "Monthly"
        time_col = "date" if "date" in df_base.columns else "year_month"

        meta = STATION_METADATA.get(sid, {"name": sid, "basin": "Unknown", "oued": "Unknown"})

        fig, (ax_top, ax_bot) = plt.subplots(2, 1, figsize=(12, 7.5), dpi=300, sharex=True, gridspec_kw={"height_ratios": [1.4, 1.0]})

        dates = pd.to_datetime(df_base[time_col]).dt.to_pydatetime()
        o = df_base["q_m3s"].to_numpy()

        # Top: Echelle lineaire
        ax_top.plot(dates, o, color=c_obs, lw=1.5, label="Observed (ABH)", alpha=0.95, zorder=5)
        for exp, df_p in exp_data.items():
            ax_top.plot(dates, df_p["q_sim"].to_numpy(), color=colors_exp.get(exp, "#1f77b4"), lw=1.2, ls="--", label=f"Simulated ({exp})", alpha=0.85, zorder=4)

        ax_top.set_title(f"{meta['name']} ({meta['basin']} Basin, Oued {meta['oued']}) — {step} Streamflow Evaluation", fontsize=11, fontweight="bold", pad=8)
        ax_top.set_ylabel("Streamflow (m³/s)", fontsize=10)
        ax_top.grid(True, ls=":", alpha=0.6)
        ax_top.legend(loc="upper right", framealpha=0.9, fontsize=9)

        # Bottom: Echelle logarithmique (etiages)
        o_pos = np.where(o > 0, o, np.nan)
        ax_bot.plot(dates, o_pos, color=c_obs, lw=1.4, label="Observed (> 0)", alpha=0.95, zorder=5)
        for exp, df_p in exp_data.items():
            s_pos = np.where(df_p["q_sim"].to_numpy() > 0, df_p["q_sim"].to_numpy(), np.nan)
            ax_bot.plot(dates, s_pos, color=colors_exp.get(exp, "#1f77b4"), lw=1.1, ls="--", label=f"Simulated ({exp})", alpha=0.85, zorder=4)

        ax_bot.set_yscale("log")
        ax_bot.set_ylabel("Streamflow [log] (m³/s)", fontsize=10)
        ax_bot.set_xlabel("Date", fontsize=10)
        ax_bot.grid(True, which="both", ls=":", alpha=0.5)

        ax_bot.xaxis.set_major_locator(mdates.YearLocator())
        ax_bot.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))

        plt.subplots_adjust(top=0.92, bottom=0.10, hspace=0.15, left=0.08, right=0.96)
        out_path = os.path.join(out_dir, f"hydrograph_{sid}.png")
        plt.savefig(out_path, dpi=300)
        plt.close(fig)
        print(f"-> Hydrogramme {sid} enregistre : {out_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluation hydrologique standardisee HyMAP face aux observations ABH (OL, NoCDF, CDF)."
    )
    parser.add_argument("--ol-csv", default=None, help="Chemin du CSV de simulation Open-Loop (ex. t_sim_daily_12stations_opl_linres0.csv).")
    parser.add_argument("--nocdf-csv", default=None, help="Chemin du CSV de simulation DA-NoCDF.")
    parser.add_argument("--cdf-csv", default=None, help="Chemin du CSV de simulation DA-CDF.")
    parser.add_argument("--obs-daily-csv", default="NoahMP_Morocco/data/streamflow_clean/obs_daily.csv", help="Chemin du CSV des observations journalieres.")
    parser.add_argument("--obs-monthly-csv", default="NoahMP_Morocco/data/streamflow_clean/obs_monthly.csv", help="Chemin du CSV des observations mensuelles.")
    parser.add_argument("--start-date", default="2017-01-01", help="Date de debut d evaluation (YYYY-MM-DD). Defaut: 2017-01-01.")
    parser.add_argument("--end-date", default="2020-12-31", help="Date de fin d evaluation (YYYY-MM-DD). Defaut: 2020-12-31.")
    parser.add_argument("--output-dir", default="NoahMP_Morocco/experiments/NorthMor/routing/plots/sebou_bouregreg/evaluation_streamflow_da", help="Repertoire de sortie.")
    parser.add_argument("--hydrograph-stations", nargs="*", default=["b_l_chafia", "b_s_jabeur", "ain_timedrine", "dar_el_hamra"], help="Stations pour lesquelles generer un hydrogramme.")
    parser.add_argument("--log-eps", type=float, default=0.01, help="Offset epsilon pour le calcul du log-NSE (defaut: 0.01 m3/s).")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    table_dir = os.path.join(args.output_dir, "tables")
    fig_dir = os.path.join(args.output_dir, "figures")
    os.makedirs(table_dir, exist_ok=True)
    os.makedirs(fig_dir, exist_ok=True)

    sim_files = {}
    if args.ol_csv: sim_files["OL"] = args.ol_csv
    if args.nocdf_csv: sim_files["NoCDF"] = args.nocdf_csv
    if args.cdf_csv: sim_files["CDF"] = args.cdf_csv

    if not sim_files:
        print("[ERREUR] Veuillez fournir au moins un fichier de simulation (--ol-csv, --nocdf-csv ou --cdf-csv).")
        sys.exit(1)

    print(f"=== EVALUATION HYDROLOGIQUE STREAMFLOW DA ({args.start_date} a {args.end_date}) ===")
    print("Simulations chargees :", list(sim_files.keys()))

    obs_dict = load_observations(args.obs_daily_csv, args.obs_monthly_csv)
    print(f"Observations chargees pour {len(obs_dict)} stations.")

    df_overall, df_seasonal, paired_series = evaluate_streamflow(
        sim_files=sim_files,
        obs_dict=obs_dict,
        start_date=args.start_date,
        end_date=args.end_date,
        eps=args.log_eps
    )

    # 1. Sauvegarde des tables CSV
    csv_overall = os.path.join(table_dir, "table_streamflow_metrics_overall.csv")
    csv_seasonal = os.path.join(table_dir, "table_streamflow_metrics_seasonal.csv")
    df_overall.to_csv(csv_overall, index=False)
    df_seasonal.to_csv(csv_seasonal, index=False)
    print(f"-> Table globale enregistree : {csv_overall}")
    print(f"-> Table saisonniere enregistree : {csv_seasonal}")

    # Table dediee composantes KGE
    kge_cols = ["station_id", "name", "basin", "experiment", "n_obs", "r", "alpha", "beta", "kge", "nse", "log_nse"]
    csv_kge = os.path.join(table_dir, "table_kge_components.csv")
    df_overall[kge_cols].to_csv(csv_kge, index=False)
    print(f"-> Table composantes KGE enregistree : {csv_kge}")

    # 2. Figure des composantes KGE
    fig_kge_path = os.path.join(fig_dir, "kge_components_by_station.png")
    plot_kge_components_figure(df_overall, fig_kge_path)

    # 3. Hydrogrammes pour les stations selectionnees
    if args.hydrograph_stations:
        plot_station_hydrographs(paired_series, args.hydrograph_stations, os.path.join(fig_dir, "hydrographs"))

    print("\n=== EVALUATION TERMINEE AVEC SUCCES ===")

if __name__ == "__main__":
    main()
