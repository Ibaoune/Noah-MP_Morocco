#!/usr/bin/env python3
"""
confrontation_adamna.py
Confrontation de la simulation HYMAP2 OPL aux 20 observations mensuelles d'Adamna
(janvier 2016 a aout 2017) depuis data/streamflow_data/adamna monthly.xlsx (LECTURE SEULE).
Calcul des metriques : KGE, NSE sur anomalies, Biais relatif, Correlation Pearson, NSE standard.
Tracé de l'hydrogramme comparatif (PNG).
"""

import os
import zipfile
import xml.etree.ElementTree as ET
import datetime
import calendar
import csv
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def read_adamna_obs(excel_path):
    z = zipfile.ZipFile(excel_path, 'r')
    shared_strings = []
    if 'xl/sharedStrings.xml' in z.namelist():
        tree = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}si'):
            t = si.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}t')
            shared_strings.append(t.text if t is not None else '')

    sheet_xml = z.read('xl/worksheets/sheet1.xml')
    tree = ET.fromstring(sheet_xml)
    rows = tree.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}sheetData/{http://schemas.openxmlformats.org/spreadsheetml/2006/main}row')

    obs_records = []
    # Base Excel date: 1899-12-30
    excel_epoch = datetime.datetime(1899, 12, 30)

    for row in rows[1:]: # Skip header
        row_vals = []
        for c in row.findall('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}c'):
            v = c.find('{http://schemas.openxmlformats.org/spreadsheetml/2006/main}v')
            val = v.text if v is not None else ''
            t = c.get('t')
            if t == 's' and val:
                val = shared_strings[int(val)]
            row_vals.append(val)
        if len(row_vals) >= 2 and row_vals[0]:
            try:
                serial_date = float(row_vals[0])
                dt = excel_epoch + datetime.timedelta(days=serial_date)
                q_obs = float(row_vals[1])
                # Filtrer sur la periode d'Adamna : 2016-01 a 2017-08 (20 mois)
                if (dt.year == 2016) or (dt.year == 2017 and dt.month <= 8):
                    obs_records.append((dt.year, dt.month, q_obs))
            except ValueError:
                pass
    z.close()
    return obs_records

def main():
    excel_path = "data/streamflow_data/adamna monthly.xlsx"
    sim_csv = "experiments/NorthMor/routing/output/OPL_2016_2020/streamflow_9stations_daily_2016_2020.csv"
    plots_dir = "experiments/NorthMor/routing/plots"
    os.makedirs(plots_dir, exist_ok=True)
    out_dir = "experiments/NorthMor/routing/output/OPL_2016_2020"

    # 1. Lire les observations
    obs_list = read_adamna_obs(excel_path)
    print(f"Observations lues pour Adamna : {len(obs_list)} mois (attendu 20 mois)")
    for y, m, q in obs_list:
        print(f"  Obs {y}-{m:02d} : {q:.4f} m3/s")

    # 2. Lire les debits journaliers simules d'Adamna
    sim_daily = {}
    with open(sim_csv, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            d = datetime.datetime.strptime(row["date"], "%Y-%m-%d").date()
            sim_daily[d] = float(row["Adamna_station"])

    # 3. Agréger les débits simulés en moyennes mensuelles pour les 20 mois
    sim_monthly = []
    obs_monthly = []
    month_labels = []
    month_dts = []

    for y, m, q_obs in obs_list:
        _, num_days = calendar.monthrange(y, m)
        q_days = [sim_daily[datetime.date(y, m, d)] for d in range(1, num_days + 1) if datetime.date(y, m, d) in sim_daily]
        q_sim_m = float(np.mean(q_days))
        sim_monthly.append(q_sim_m)
        obs_monthly.append(q_obs)
        month_labels.append(f"{y}-{m:02d}")
        month_dts.append(datetime.datetime(y, m, 15))

    sim_arr = np.array(sim_monthly)
    obs_arr = np.array(obs_monthly)

    # 4. Calcul des métriques hydrologiques
    # Biais relatif (PBIAS)
    pbias = np.sum(sim_arr - obs_arr) / np.sum(obs_arr) * 100.0
    rel_bias = (np.mean(sim_arr) - np.mean(obs_arr)) / np.mean(obs_arr) * 100.0

    # Correlation de Pearson r
    r_corr = np.corrcoef(obs_arr, sim_arr)[0, 1]

    # Ratio de variabilite alpha = sigma_sim / sigma_obs
    alpha = np.std(sim_arr) / np.std(obs_arr)
    # Ratio de moyenne beta = mu_sim / mu_obs
    beta = np.mean(sim_arr) / np.mean(obs_arr)

    # Kling-Gupta Efficiency (KGE)
    kge = 1.0 - np.sqrt((r_corr - 1.0)**2 + (alpha - 1.0)**2 + (beta - 1.0)**2)

    # Nash-Sutcliffe Efficiency (NSE standard)
    nse = 1.0 - np.sum((sim_arr - obs_arr)**2) / np.sum((obs_arr - np.mean(obs_arr))**2)

    # NSE sur les anomalies (par rapport a la moyenne mensuelle multi-annuelle / climatologie de l'echantillon)
    # Calcul des anomalies :
    obs_clim = {}
    for i, (y, m, _) in enumerate(obs_list):
        if m not in obs_clim: obs_clim[m] = []
        obs_clim[m].append(obs_arr[i])
    for m in obs_clim:
        obs_clim[m] = np.mean(obs_clim[m])

    obs_anom = np.array([obs_arr[i] - obs_clim[obs_list[i][1]] for i in range(len(obs_arr))])
    sim_anom = np.array([sim_arr[i] - obs_clim[obs_list[i][1]] for i in range(len(sim_arr))])
    
    nse_anom = 1.0 - np.sum((sim_arr - obs_arr)**2) / np.sum(obs_anom**2)

    # Tableau comparatif
    print("\n" + "="*70)
    print("CONFRONTATION MENSUELLE ADAMNA (JANVIER 2016 - AOUT 2017) :")
    print("="*70)
    print(f"{'Mois':8s} | {'Obs (m3/s)':12s} | {'Sim (m3/s)':12s} | {'Ecart (m3/s)':13s} | {'Ratio Sim/Obs':13s}")
    print("-"*70)
    for i in range(len(obs_list)):
        ecart = sim_arr[i] - obs_arr[i]
        ratio = sim_arr[i] / obs_arr[i] if obs_arr[i] > 0 else np.nan
        ratio_str = f"{ratio:10.2f}" if not np.isnan(ratio) else "       N/A"
        print(f"{month_labels[i]:8s} | {obs_arr[i]:12.4f} | {sim_arr[i]:12.4f} | {ecart:+13.4f} | {ratio_str}")
    print("="*70)

    print("\nMETRIQUES DE PERFORMANCE :")
    print(f"  Nombre de mois observes   : {len(obs_arr)}")
    print(f"  Debit moyen observe       : {np.mean(obs_arr):.4f} m3/s")
    print(f"  Debit moyen simule        : {np.mean(sim_arr):.4f} m3/s")
    print(f"  Correlation de Pearson (r): {r_corr:+.4f}")
    print(f"  Biais relatif (PBIAS)     : {pbias:+.2f}%")
    print(f"  Ratio variabilite (alpha) : {alpha:.4f}")
    print(f"  Ratio moyenne (beta)      : {beta:.4f}")
    print(f"  Kling-Gupta (KGE)         : {kge:+.4f}")
    print(f"  Nash-Sutcliffe (NSE std)  : {nse:+.4f}")
    print(f"  NSE sur anomalies         : {nse_anom:+.4f}")

    # Sauvegarder les resultats dans un fichier texte / CSV
    out_table = os.path.join(out_dir, "adamna_monthly_comparison.csv")
    with open(out_table, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["mois", "obs_m3s", "sim_m3s", "ecart_m3s"])
        for i in range(len(obs_list)):
            writer.writerow([month_labels[i], f"{obs_arr[i]:.4f}", f"{sim_arr[i]:.4f}", f"{sim_arr[i]-obs_arr[i]:.4f}"])

    # 5. Tracer le graphique comparatif
    fig, ax = plt.subplots(figsize=(13, 6))

    # Tracer les courbes mensuelles
    ax.plot(month_dts, obs_arr, marker="o", color="#d62728", lw=2.2, markersize=6, label="Observé (ABHT Adamna)", zorder=5)
    ax.plot(month_dts, sim_arr, marker="s", color="#1f77b4", lw=2.2, markersize=6, label="Simulé (HyMAP2 OPL - non calé)", zorder=4)

    # Tracer aussi le fond journalier simule pour voir la dynamique intra-mensuelle
    daily_dts = [datetime.datetime(d.year, d.month, d.day) for d in sim_daily if datetime.date(2016, 1, 1) <= d <= datetime.date(2017, 8, 31)]
    daily_vals = [sim_daily[d.date()] for d in daily_dts]
    ax.plot(daily_dts, daily_vals, color="#a6cee3", lw=0.9, alpha=0.6, label="Simulé journalier (HyMAP2)", zorder=2)

    ax.set_title("Confrontation HyMAP2 OPL vs Observations à la Station Adamna (Bassin du Ksob, 1617 km²)\n"
                 "Période Janvier 2016 - Août 2017 (20 mois observés)", fontsize=13, fontweight="bold")
    ax.set_ylabel("Débit (m³/s)", fontsize=11)
    ax.set_xlabel("Date (Mois)", fontsize=11)
    ax.grid(True, linestyle="--", alpha=0.6)
    
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    plt.xticks(rotation=30, ha="right")

    # Boîte de métriques
    metrics_text = (
        f"Métriques de Performance (20 mois) :\n"
        f"  • KGE = {kge:+.3f}\n"
        f"  • Corrélation (r) = {r_corr:+.3f}\n"
        f"  • NSE anomalies = {nse_anom:+.3f}\n"
        f"  • NSE standard = {nse:+.3f}\n"
        f"  • Biais relatif = {pbias:+.1f}%\n"
        f"  • Moyenne Obs = {np.mean(obs_arr):.2f} m³/s\n"
        f"  • Moyenne Sim = {np.mean(sim_arr):.2f} m³/s"
    )
    ax.text(0.68, 0.95, metrics_text, transform=ax.transAxes, fontsize=10, verticalalignment="top",
            bbox=dict(boxstyle="round,pad=0.5", fc="#f8f9fa", alpha=0.92, ec="#ced4da", lw=1.2))

    ax.legend(loc="upper left", framealpha=0.9)
    plt.tight_layout()

    out_plot = os.path.join(plots_dir, "adamna_confrontation_2016_2017.png")
    plt.savefig(out_plot, dpi=200)
    plt.close()
    print(f"\nGraphique de confrontation sauvegarde dans : {out_plot}")

if __name__ == "__main__":
    main()
