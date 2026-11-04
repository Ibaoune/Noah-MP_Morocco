#!/usr/bin/env python3
"""
extract_and_plot_9stations_2016_2020.py
Extrait les debits journaliers simules (Streamflow_tavg) aux 9 exutoires/stations
sur toute la periode 2016-2020 (1827 jours) et trace les hydrogrammes.
"""

import os
import glob
import csv
import datetime
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def main():
    pairing_csv = "experiments/NorthMor/routing/output/OPL_201801/stations_hymap_pairing.csv"
    routing_dir = "experiments/NorthMor/routing/output/OPL_2016_2020/ROUTING"
    out_csv = "experiments/NorthMor/routing/output/OPL_2016_2020/streamflow_9stations_daily_2016_2020.csv"
    plots_dir = "experiments/NorthMor/routing/plots"
    os.makedirs(plots_dir, exist_ok=True)

    # 1. Lire stations
    stations = []
    with open(pairing_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            stations.append({
                "nom": row["nom"],
                "row": int(row["row_hymap"]),
                "col": int(row["col_hymap"]),
                "aire_off": float(row["aire_off_km2"]) if row["aire_off_km2"] else None,
                "aire_hymap": float(row["aire_hymap_km2"])
            })

    # 2. Chercher les fichiers LIS_HIST
    hist_files = sorted(glob.glob(os.path.join(routing_dir, "20*/**/LIS_HIST_*.d01.nc"), recursive=True))
    print(f"Trouve {len(hist_files)} fichiers journaliers de routage 2016-2020.")
    
    dates = []
    q_data = {st["nom"]: [] for st in stations}

    for idx, fpath in enumerate(hist_files):
        with nc.Dataset(fpath) as ds:
            # Date
            t_units = ds["time"].units
            t_val = ds["time"][0]
            base_str = t_units.replace("minutes since ", "")
            base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
            file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
            sim_dt = file_dt - datetime.timedelta(days=1)
            dates.append(sim_dt)

            flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
            if flow.ndim == 3: flow = flow[0]

            for st in stations:
                r, c = st["row"], st["col"]
                q_data[st["nom"]].append(float(flow[r, c]))

        if (idx + 1) % 365 == 0 or idx == len(hist_files) - 1:
            print(f"  Traite {idx + 1}/{len(hist_files)} jours ({sim_dt.strftime('%Y-%m-%d')})...")

    # 3. Ecrire le CSV
    with open(out_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        header = ["date"] + [st["nom"] for st in stations]
        writer.writerow(header)
        for i, dt in enumerate(dates):
            row = [dt.strftime("%Y-%m-%d")] + [f"{q_data[st['nom']][i]:.4f}" for st in stations]
            writer.writerow(row)
    print(f"Extraction terminee. CSV sauvegarde dans : {out_csv}")

    # 4. Tracer la figure combinee 9 panneaux (3x3)
    fig, axes = plt.subplots(3, 3, figsize=(18, 12), sharex=True)
    axes = axes.flatten()

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22"]

    for i, st in enumerate(stations):
        ax = axes[i]
        nom = st["nom"]
        q_series = np.array(q_data[nom])
        ax.plot(dates, q_series, color=colors[i % len(colors)], lw=1.2, label=f"{nom}")
        ax.set_title(f"{nom} (Aire = {st['aire_hymap']:.0f} km²)", fontsize=11, fontweight="bold")
        ax.set_ylabel("Débit (m³/s)", fontsize=9)
        ax.grid(True, linestyle="--", alpha=0.5)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        
        # Max stats
        q_max = np.max(q_series)
        q_mean = np.mean(q_series)
        ax.text(0.03, 0.85, f"Moy = {q_mean:.1f} m³/s\nMax = {q_max:.1f} m³/s",
                transform=ax.transAxes, fontsize=8, verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8, ec="gray"))

    fig.suptitle("Hydrogrammes Journaliers HyMAP2 (Simulation OPL Continue 2016-2020) - 9 Stations / Exutoires",
                 fontsize=14, fontweight="bold", y=0.99)
    plt.tight_layout()
    comb_png = os.path.join(plots_dir, "hydrographs_9stations_2016_2020.png")
    plt.savefig(comb_png, dpi=200)
    plt.close()
    print(f"Figure combinee sauvegardee dans : {comb_png}")

    # 5. Tracer les hydrogrammes individuels
    for i, st in enumerate(stations):
        nom = st["nom"]
        fig, ax = plt.subplots(figsize=(12, 5))
        q_series = np.array(q_data[nom])
        ax.plot(dates, q_series, color="#0b559f", lw=1.3, label="Débit simulé (HyMAP2 OPL)")
        ax.set_title(f"Hydrogramme Journalier 2016-2020 : {nom} (Bassin = {st['aire_hymap']:.0f} km²)", fontsize=12, fontweight="bold")
        ax.set_ylabel("Débit (m³/s)", fontsize=10)
        ax.set_xlabel("Année", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.xaxis.set_major_locator(mdates.YearLocator())
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonth=[4, 7, 10]))
        
        q_max = np.max(q_series)
        q_mean = np.mean(q_series)
        q_vol = np.sum(q_series) * 86400 / 1e9 # en km3
        ax.text(0.02, 0.90, f"Moyenne : {q_mean:.2f} m³/s\nPic max : {q_max:.2f} m³/s\nVolume 5 ans : {q_vol:.2f} km³",
                transform=ax.transAxes, fontsize=9, verticalalignment="top",
                bbox=dict(boxstyle="round,pad=0.4", fc="white", alpha=0.85, ec="gray"))
        ax.legend(loc="upper right")
        plt.tight_layout()
        indiv_png = os.path.join(plots_dir, f"hydrograph_{nom}_2016_2020.png")
        plt.savefig(indiv_png, dpi=180)
        plt.close()
    print(f"9 figures individuelles sauvegardees dans {plots_dir}/")

if __name__ == "__main__":
    main()
