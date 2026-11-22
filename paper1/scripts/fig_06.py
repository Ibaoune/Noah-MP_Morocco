#!/usr/bin/env python3
"""
fig_06.py
---------
Figure 6: Impact of the Noah-MP wilting point filter in 2018 (DA-NoCDF vs DA-NoCDF-noWQC).
Panels:
  (a) Accepted SMAP retrievals by month in 2018: DA-NoCDF vs DA-NoCDF-noWQC.
  (b) Annual ET difference ΔET (DA-NoCDF-noWQC - DA-NoCDF) by soil texture class.
  (c) Spatial map of summer (JJA) surface soil moisture difference Δθ1 (noWQC - NoCDF).

Outputs:
  paper1/figures/fig_06.png (200 dpi)
  paper1/figures/fig_06_data.csv
"""

import os
import glob
import pandas as pd
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import BoundaryNorm

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
ET_TEX_CSV = os.path.join(BASE_DIR, "paper1/tables/et_evaluation_by_texture.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_06.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_06_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Panel (a) Data: Accepted Observations per month ─────────────────────
    # Measured counts from 2018 EnKF innovation files:
    # DA_nocdf: [121390, 104873, 125382, 138181, 117545, 78264, 107081, 155329, 165143, 160167, 173620, 164040]
    # DA_nowilt: [185323, 161076, 229007, 255854, 228846, 234027, 273158, 267292, 246317, 241040, 230354, 236849]
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    obs_nocdf = np.array([121390, 104873, 125382, 138181, 117545, 78264, 107081, 155329, 165143, 160167, 173620, 164040])
    obs_nowilt = np.array([185323, 161076, 229007, 255854, 228846, 234027, 273158, 267292, 246317, 241040, 230354, 236849])
    
    # ── 2. Panel (b) Data: ΔET by texture ──────────────────────────────────────
    df_et = pd.read_csv(ET_TEX_CSV)
    df_et_gl = df_et[df_et['reference'] == 'GLEAM_v4.3a'].copy()
    
    # Textures of interest
    textures = ['Sand', 'Sandy Loam', 'Silt Loam', 'Loam', 'Sandy Clay Loam', 'Clay Loam', 'Clay']
    delta_et_by_tex = []
    tex_clays = [3.0, 10.0, 13.0, 19.0, 27.0, 34.0, 58.0]
    
    for t in textures:
        et_nc = df_et_gl[(df_et_gl['experiment'] == 'DA_nocdf') & (df_et_gl['texture_name'] == t)]['et_sim_mean_mm'].values
        et_nw = df_et_gl[(df_et_gl['experiment'] == 'DA_nocdf_nowilt') & (df_et_gl['texture_name'] == t)]['et_sim_mean_mm'].values
        if len(et_nc) > 0 and len(et_nw) > 0:
            diff = et_nw[0] - et_nc[0]
            delta_et_by_tex.append((t, diff, et_nc[0], et_nw[0]))
        else:
            delta_et_by_tex.append((t, np.nan, np.nan, np.nan))
            
    df_tex_diff = pd.DataFrame(delta_et_by_tex, columns=['texture', 'delta_ET_annual_mm', 'ET_nocdf_mm', 'ET_nowilt_mm'])
    
    # ── 3. Panel (c) Data: JJA Δθ1 Spatial Map ─────────────────────────────────
    with nc.Dataset(LIS_INPUT) as ds:
        lat = ds.variables['lat'][:]
        lon = ds.variables['lon'][:]
        landmask = ds.variables['LANDMASK'][:].squeeze()
        
    pattern_nowilt = os.path.join(BASE_DIR, 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/20180[678]/LIS_HIST_*.nc')
    pattern_nocdf = os.path.join(BASE_DIR, 'experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-0[678]/SURFACEMODEL/20180[678]/LIS_HIST_*.nc')
    
    f_nw = {os.path.basename(f): f for f in glob.glob(pattern_nowilt)}
    f_nc = {os.path.basename(f): f for f in glob.glob(pattern_nocdf)}
    common = sorted(list(set(f_nw.keys()) & set(f_nc.keys())))[::2]
    
    diffs = []
    for fname in common:
        with nc.Dataset(f_nw[fname]) as ds1, nc.Dataset(f_nc[fname]) as ds2:
            sm1 = ds1.variables['SoilMoist_tavg'][0, :, :]
            sm2 = ds2.variables['SoilMoist_tavg'][0, :, :]
            diffs.append(sm1 - sm2)
    mean_diff = np.mean(diffs, axis=0)
    jja_delta_theta1 = np.where(landmask == 1, mean_diff * 1000.0, np.nan) # in 10^-3 m3/m3
    
    # ── 4. Save CSV Data ───────────────────────────────────────────────────────
    df_out_a = pd.DataFrame({'month': months, 'month_name': month_names, 'obs_DA_nocdf': obs_nocdf, 'obs_DA_nowilt': obs_nowilt, 'obs_gained_nowilt': obs_nowilt - obs_nocdf})
    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_ACCEPTED_OBSERVATIONS_2018\n")
        df_out_a.to_csv(f, index=False)
        f.write("\n# PANEL_B_ANNUAL_DELTA_ET_BY_TEXTURE\n")
        df_tex_diff.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # ── 5. Setup Figure ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 6.5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.0, 1.1], wspace=0.25,
                           left=0.06, right=0.96, top=0.86, bottom=0.14)
                           
    c_nocdf = '#D55E00'   # Vermillion
    c_nowilt = '#E69F00'  # Orange
    
    # ── Panel (a): Monthly Accepted Retrievals ─────────────────────────────────
    ax_a = fig.add_subplot(gs[0])
    width_a = 0.38
    x_a = np.arange(len(months))
    ax_a.bar(x_a - width_a/2, obs_nocdf / 1000.0, width_a, label='DA-NoCDF (Standard QC)', color=c_nocdf, edgecolor='black', linewidth=0.7)
    ax_a.bar(x_a + width_a/2, obs_nowilt / 1000.0, width_a, label='DA-NoCDF-noWQC (Uncensored)', color=c_nowilt, edgecolor='black', linewidth=0.7)
    
    ax_a.set_title("(a) Accepted SMAP Retrievals in 2018", fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xticks(x_a)
    ax_a.set_xticklabels(month_names, fontsize=8.5)
    ax_a.set_ylabel("Accepted Retrievals ($10^3$ obs / month)", fontsize=10.5)
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_a.legend(loc='upper left', fontsize=9.0, framealpha=0.95)
    
    # Highlight summer gain
    ax_a.annotate("Summer surge:\n+199% in Jun\n+155% in Jul",
                  xy=(5.5, 230), xytext=(4.0, 245),
                  arrowprops=dict(arrowstyle="->", color=c_nowilt, lw=1.2),
                  fontsize=8.5, color='#B25000', fontweight='bold')
                  
    # ── Panel (b): ΔET by Texture ──────────────────────────────────────────────
    ax_b = fig.add_subplot(gs[1])
    x_b = np.arange(len(textures))
    y_b = df_tex_diff['delta_ET_annual_mm'].to_numpy()
    
    # Color bars based on sign (negative = drying/reduction in ET)
    bar_cols = [c_nowilt if v >= 0 else '#B25000' for v in y_b]
    bars_b = ax_b.bar(x_b, y_b, color=bar_cols, edgecolor='black', linewidth=0.7, width=0.55)
    
    ax_b.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax_b.set_title("(b) Annual $\\Delta$ET (noWQC - NoCDF) by Texture", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xticks(x_b)
    labels_b = [f"{t}\n({c:.0f}% clay)" for t, c in zip(textures, tex_clays)]
    ax_b.set_xticklabels(labels_b, fontsize=8.5)
    ax_b.set_ylabel("$\\Delta$ET (mm / year)", fontsize=10.5)
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    for b in bars_b:
        h = b.get_height()
        va = 'top' if h < 0 else 'bottom'
        y_pos = h - 4.0 if h < 0 else h + 1.0
        ax_b.annotate(f"{h:.1f}",
                      xy=(b.get_x() + b.get_width() / 2, y_pos),
                      ha='center', va=va, fontsize=8.5, fontweight='bold')
    ax_b.set_ylim(-125, 10)
    
    # ── Panel (c): JJA Δθ1 Spatial Map ────────────────────────────────────────
    ax_c = fig.add_subplot(gs[2])
    extent = [lon.min(), lon.max(), lat.min(), lat.max()]
    
    levels_c = [-25, -20, -15, -10, -5, 0, 5, 10, 15, 20, 25]
    cmap_c = plt.get_cmap('RdBu') # Red = dry/negative, Blue = wet/positive
    norm_c = BoundaryNorm(levels_c, ncolors=cmap_c.N, clip=True)
    
    im_c = ax_c.imshow(jja_delta_theta1, origin='lower', extent=extent, cmap=cmap_c, norm=norm_c, aspect='auto')
    ax_c.set_title("(c) Summer (JJA) Surface $\\Delta\\theta_1$ (noWQC - NoCDF)", fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xlabel("Longitude (°E)", fontsize=10)
    ax_c.set_ylabel("Latitude (°N)", fontsize=10)
    ax_c.grid(True, linestyle=':', alpha=0.5)
    
    cbar_c = fig.colorbar(im_c, ax=ax_c, orientation='horizontal', fraction=0.06, pad=0.18, ticks=levels_c[::2])
    cbar_c.set_label("$\\Delta\\theta_1$ ($10^{-3}\\;\\mathrm{m}^3\\,\\mathrm{m}^{-3}$)", fontsize=9.5)
    cbar_c.ax.tick_params(labelsize=8.5)
    
    fig.suptitle("Figure 6 — Impact of Removing the Wilting Point Filter in 2018 (DA-NoCDF vs DA-NoCDF-noWQC)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
