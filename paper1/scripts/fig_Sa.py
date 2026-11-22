#!/usr/bin/env python3
"""
fig_Sa.py
---------
Figure S-a: Supplementary diagnostic of streamflow and baseflow anomaly at Lalla Chafia (Sebou).
Panels:
  (a) Annual baseflow (Qsb) difference map (DA_nocdf - ENS_OPL, mm/year)
      with Lalla Chafia and Sidi Jabeur upstream catchment boundaries,
      highlighting the localized groundwater drainage surge.
  (b) Daily streamflow comparison at Lalla Chafia across routing regimes
      (linres=1 historical vs linres=0 baseline vs observations).

Outputs:
  paper1/figures/fig_Sa.png (200 dpi)
  paper1/figures/fig_Sa_data.csv
"""

import os
import pandas as pd
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import BoundaryNorm
import matplotlib.dates as mdates

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
TOP20_CSV = os.path.join(BASE_DIR, "paper1/tables/top20_cells_qsb_difference.csv")
DAILY_CSV = os.path.join(BASE_DIR, "paper1/tables/daily_streamflow_lalla_chafia_sidi_jabeur_2018.csv")
LINRES_CSV = os.path.join(BASE_DIR, "paper1/tables/lalla_chafia_streamflow_linres1_vs_linres0_2018.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_Sa.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_Sa_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_top20 = pd.read_csv(TOP20_CSV)
    df_daily = pd.read_csv(DAILY_CSV)
    df_daily['date'] = pd.to_datetime(df_daily['date'])
    df_linres = pd.read_csv(LINRES_CSV)
    df_linres['date'] = pd.to_datetime(df_linres['date'])
    
    # Merge for output CSV
    with open(OUT_CSV, 'w') as f:
        f.write("# TOP20_CELLS_QSB_DIFFERENCE\n")
        df_top20.to_csv(f, index=False)
        f.write("\n# LINRES_COMPARISON_LALLA_CHAFIA_2018\n")
        df_linres.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # ── 2. Load Coordinates & Baseflow diff ─────────────────────────────────────
    with nc.Dataset(LIS_INPUT) as ds:
        lat = ds.variables['lat'][:]
        lon = ds.variables['lon'][:]
        landmask = ds.variables['LANDMASK'][:].squeeze()
        
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    
    # Create 2D grid of difference from top20 and parquet
    # Load 2018 Qsb from parquet
    pq_file = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/To_rm/data/processed/monthly_pixel_dataset_2016_2020_static.parquet"
    df_pq = pd.read_parquet(pq_file)
    df_2018 = df_pq[df_pq['year'] == 2018].groupby(['north_south', 'east_west'])[['Qsb_tavg_DA_NoCDF', 'Qsb_tavg_OPL']].sum().reset_index()
    
    diff_grid = np.full((121, 181), np.nan, dtype=np.float32)
    for _, row in df_2018.iterrows():
        r = int(row['north_south'])
        c = int(row['east_west'])
        diff_grid[r, c] = row['Qsb_tavg_DA_NoCDF'] - row['Qsb_tavg_OPL']
        
    # ── 3. Setup Figure (2 panels) ─────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 8))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.1, 1.1], wspace=0.22,
                           left=0.06, right=0.96, top=0.90, bottom=0.12)
                           
    # Panel (a): Qsb Difference Map
    ax_a = fig.add_subplot(gs[0])
    levels = [-50, -20, -10, 0, 10, 20, 50, 100, 200, 400, 600, 1000]
    cmap = plt.get_cmap('RdBu_r')
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    
    im_a = ax_a.imshow(diff_grid, origin='lower', extent=extent, cmap=cmap, norm=norm, aspect='auto')
    ax_a.set_title("(a) Annual Baseflow Difference $\\Delta Q_{sb}$ (DA-NoCDF - OPL, mm/year)", fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Longitude (°E)", fontsize=10)
    ax_a.set_ylabel("Latitude (°N)", fontsize=10)
    ax_a.grid(True, linestyle=':', alpha=0.5)
    
    # Highlight top 20 cells
    ax_a.scatter(df_top20['lon'], df_top20['lat'], color='yellow', edgecolor='black', s=40, zorder=5, label='Top 20 Outlier Cells')
    # Station locations
    ax_a.scatter([-4.95], [34.02], color='red', marker='^', s=90, edgecolor='black', zorder=6, label='Lalla Chafia Station')
    ax_a.scatter([-6.38], [32.42], color='purple', marker='^', s=90, edgecolor='black', zorder=6, label='Sidi Jabeur Station')
    ax_a.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    cbar_a = fig.colorbar(im_a, ax=ax_a, orientation='horizontal', fraction=0.06, pad=0.14, ticks=levels[::2])
    cbar_a.set_label("$\\Delta Q_{sb}$ (mm / year)", fontsize=9.5)
    cbar_a.ax.tick_params(labelsize=8.5)
    
    # Panel (b): Hydrographs at Lalla Chafia
    ax_b = fig.add_subplot(gs[1])
    dates = df_daily['date'].to_numpy()
    
    ax_b.plot(dates, df_daily['obs_lalla_chafia'].to_numpy(), color='black', lw=2.2, label='Observed (In Situ)', zorder=6)
    ax_b.plot(dates, df_daily['DA_nocdf_lalla_chafia'].to_numpy(), color='#D55E00', lw=2.0, ls='-', label='DA-NoCDF (linres=0, coldstart)')
    ax_b.plot(df_linres['date'].to_numpy(), df_linres["q_linres1"].to_numpy(), color='#882255', lw=1.6, ls='--', label='DA-NoCDF (linres=1, linear reservoir)')
    ax_b.plot(dates, df_daily['ENS_OPL_lalla_chafia'].to_numpy(), color='#009E73', lw=1.6, ls=':', label='ENS-OL (linres=0)')
    ax_b.plot(dates, df_daily['OPL_lalla_chafia'].to_numpy(), color='#1f77b4', lw=1.4, ls='-', label='OPL (linres=0)')
    
    ax_b.set_yscale('log')
    ax_b.set_ylim(0.04, 300)
    ax_b.set_ylabel("Streamflow ($m^3 / s$) [Log Scale]", fontsize=10.5)
    ax_b.set_title("(b) Lalla Chafia Streamflow: linres=0 vs linres=1 Historical Routing", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.grid(True, which='both', linestyle=':', alpha=0.5)
    ax_b.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    ax_b.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
    ax_b.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    
    fig.suptitle("Figure S-a — Lalla Chafia Baseflow Anomaly Diagnostic and Routing Invariance (2018)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
