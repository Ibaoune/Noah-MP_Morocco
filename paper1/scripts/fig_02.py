#!/usr/bin/env python3
"""
fig_02.py
---------
Figure 2: Fraction of otherwise valid SMAP retrievals rejected by the wilting point filter
in DA-NoCDF (2016-2020).
Panels:
  (a) Spatial map of rejection fraction in Spring (MAM) for DA-NoCDF
  (b) Spatial map of rejection fraction in Summer (JJA) for DA-NoCDF
  (c) Rejection fraction by USDA soil texture class: DA-NoCDF vs DA-CDF (MAM & JJA)

Outputs:
  paper1/figures/fig_02.png (200 dpi)
  paper1/figures/fig_02_data.csv
"""

import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import BoundaryNorm
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
NPZ_PATH = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/censorship_budget_2016_2020.npz"
CSV_TEXTURE_PATH = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/censorship_budget_by_texture.csv"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_02.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_02_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # 1. Load domain coordinates and landmask
    with nc.Dataset(LIS_INPUT) as ds:
        lat = ds.variables['lat'][:] # (121, 181)
        lon = ds.variables['lon'][:] # (121, 181)
        landmask = ds.variables['LANDMASK'][:].squeeze() # (121, 181)
    
    # 2. Load NPZ budget data
    data_npz = np.load(NPZ_PATH)
    nocdf_rej = data_npz['nocdf_wilt_rej_monthly']   # (12, 121, 181)
    nocdf_valid = data_npz['nocdf_valid_monthly']   # (12, 121, 181)
    
    # Months: MAM = indices 2, 3, 4; JJA = indices 5, 6, 7
    mam_rej = np.sum(nocdf_rej[2:5, :, :], axis=0)
    mam_valid = np.sum(nocdf_valid[2:5, :, :], axis=0)
    
    jja_rej = np.sum(nocdf_rej[5:8, :, :], axis=0)
    jja_valid = np.sum(nocdf_valid[5:8, :, :], axis=0)
    
    with np.errstate(divide='ignore', invalid='ignore'):
        mam_rate = np.where((landmask == 1) & (mam_valid > 0), (mam_rej / mam_valid) * 100.0, np.nan)
        jja_rate = np.where((landmask == 1) & (jja_valid > 0), (jja_rej / jja_valid) * 100.0, np.nan)
        
    # 3. Load texture table
    df_tex = pd.read_csv(CSV_TEXTURE_PATH)
    # Save plotted data CSV
    df_tex.to_csv(OUT_CSV, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # 4. Create Figure
    fig = plt.figure(figsize=(16, 10))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.1, 1.0], width_ratios=[1.0, 1.0],
                           hspace=0.28, wspace=0.18, left=0.06, right=0.94, top=0.92, bottom=0.08)
    
    # Colormap and levels for maps
    levels = [0, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    cmap = plt.get_cmap('YlOrRd')
    norm = BoundaryNorm(levels, ncolors=cmap.N, clip=True)
    
    # Map extent
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    
    # Panel (a): MAM Map
    ax_a = fig.add_subplot(gs[0, 0])
    im_a = ax_a.imshow(mam_rate, origin='lower', extent=extent, cmap=cmap, norm=norm, aspect='auto')
    ax_a.set_title("(a) DA-NoCDF wilting filter rejection rate — Spring (MAM)", fontsize=12, fontweight='bold', pad=8)
    ax_a.set_xlabel("Longitude (°E)", fontsize=10)
    ax_a.set_ylabel("Latitude (°N)", fontsize=10)
    ax_a.grid(True, linestyle=':', alpha=0.5)
    
    # Panel (b): JJA Map
    ax_b = fig.add_subplot(gs[0, 1])
    im_b = ax_b.imshow(jja_rate, origin='lower', extent=extent, cmap=cmap, norm=norm, aspect='auto')
    ax_b.set_title("(b) DA-NoCDF wilting filter rejection rate — Summer (JJA)", fontsize=12, fontweight='bold', pad=8)
    ax_b.set_xlabel("Longitude (°E)", fontsize=10)
    ax_b.set_ylabel("Latitude (°N)", fontsize=10)
    ax_b.grid(True, linestyle=':', alpha=0.5)
    
    # Shared colorbar for maps
    cbar_ax = fig.add_axes([0.25, 0.51, 0.50, 0.02])
    cbar = fig.colorbar(im_a, cax=cbar_ax, orientation='horizontal', ticks=levels)
    cbar.set_label("Fraction of valid SMAP retrievals rejected (%)", fontsize=10, labelpad=5)
    cbar.ax.tick_params(labelsize=9)
    
    # Panel (c): Bar plot by texture
    ax_c = fig.add_subplot(gs[1, :])
    
    textures = df_tex['texture'].tolist()
    x = np.arange(len(textures))
    width = 0.20
    
    # Colors matching colorblind-safe rules:
    # DA-NoCDF: vermillion (#D55E00) / orange (#E69F00)
    # DA-CDF: sky blue (#56B4E9) / reddish purple (#CC79A7)
    c_nocdf_mam = '#D55E00'
    c_nocdf_jja = '#E69F00'
    c_cdf_mam = '#56B4E9'
    c_cdf_jja = '#CC79A7'
    
    rects1 = ax_c.bar(x - 1.5*width, df_tex['nocdf_mam_pct'], width, label='DA-NoCDF (MAM)', color=c_nocdf_mam, edgecolor='black', linewidth=0.7)
    rects2 = ax_c.bar(x - 0.5*width, df_tex['nocdf_jja_pct'], width, label='DA-NoCDF (JJA)', color=c_nocdf_jja, edgecolor='black', linewidth=0.7)
    rects3 = ax_c.bar(x + 0.5*width, df_tex['cdf_mam_pct'], width, label='DA-CDF (MAM)', color=c_cdf_mam, edgecolor='black', linewidth=0.7)
    rects4 = ax_c.bar(x + 1.5*width, df_tex['cdf_jja_pct'], width, label='DA-CDF (JJA)', color=c_cdf_jja, edgecolor='black', linewidth=0.7)
    
    ax_c.set_title("(c) Wilting filter rejection rate by soil texture class: DA-NoCDF vs DA-CDF", fontsize=12, fontweight='bold', pad=8)
    ax_c.set_xticks(x)
    labels = [f"{t}\n(Clay: {c:.0f}%, $\\theta_{{wilt}}$: {w:.3f})" for t, c, w in zip(df_tex['texture'], df_tex['clay_fraction_pct'], df_tex['smcwlt'])]
    ax_c.set_xticklabels(labels, fontsize=9.5)
    ax_c.set_ylabel("Retrievals rejected (%)", fontsize=10.5)
    ax_c.set_ylim(0, 110)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_c.legend(loc='upper left', framealpha=0.95, fontsize=10, ncol=4)
    
    # Add values on top of bars
    for rects in [rects1, rects2, rects3, rects4]:
        for r in rects:
            h = r.get_height()
            if h > 2.0:
                ax_c.annotate(f'{h:.1f}%',
                              xy=(r.get_x() + r.get_width() / 2, h),
                              xytext=(0, 2), textcoords="offset points",
                              ha='center', va='bottom', fontsize=7.5, rotation=45)
    
    fig.suptitle("Figure 2 — Rejection of Valid SMAP Retrievals by the Noah-MP Wilting Filter (2016–2020)",
                 fontsize=14, fontweight='bold', y=0.98)
    
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
