#!/usr/bin/env python3
"""
fig_04.py
---------
Figure 4: Spring (MAM) soil moisture dry-down dynamics: uncensored SMAP vs Noah-MP OL.
Panels:
  (a) Drying time constant tau (days) by soil texture class (SMAP uncensored vs OL).
  (b) 5th percentile soil moisture floor P5 vs Noah-MP wilting point (SMCWLT).
  (c) Linear regression of tau against soil clay fraction: physical SMAP slope (+4.4 d/fraction)
      vs inverted Noah-MP slope (-18.4 d/fraction).

Outputs:
  paper1/figures/fig_04.png (200 dpi)
  paper1/figures/fig_04_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TAU_CSV = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/tau_class_medians_with_ci.csv"
CONS_CSV = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/consolidated_drydown_censored_vs_uncensored.csv"
SLOPES_CSV = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/tau_vs_clay_slopes_bootstrap.csv"

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_04.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_04_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # 1. Load data
    df_tau = pd.read_csv(TAU_CSV)
    df_cons = pd.read_csv(CONS_CSV)
    df_slopes = pd.read_csv(SLOPES_CSV)
    
    # Filter MAM
    tau_mam = df_tau[df_tau['season'] == 'MAM'].copy().sort_values('clay_fraction_pct')
    cons_mam = df_cons[df_cons['season'] == 'MAM'].copy().sort_values('clay_pct')
    
    # Merge for output CSV
    merged = pd.merge(tau_mam, cons_mam[['texture', 'smcwlt', 'p5_smap_uncensored', 'p5_ol']], on='texture')
    merged.to_csv(OUT_CSV, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # 2. Setup Figure (3 panels horizontally)
    fig = plt.figure(figsize=(18, 6))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.1, 1.1], wspace=0.25,
                           left=0.06, right=0.96, top=0.86, bottom=0.15)
                           
    textures = merged['texture'].tolist()
    clays = merged['clay_fraction_pct'].to_numpy()
    x = np.arange(len(textures))
    width = 0.35
    
    # Color conventions:
    # SMAP uncensored: '#D55E00' (or dark orange / amber)
    # Noah-MP OL: '#1f77b4' (blue)
    c_smap = '#E69F00' # Orange
    c_ol = '#1f77b4'   # Blue
    c_wilt = '#D55E00' # Vermillion
    
    # ── Panel (a): tau by texture ──────────────────────────────────────────────
    ax_a = fig.add_subplot(gs[0])
    
    tau_smap = merged['tau_smap_median'].to_numpy()
    tau_smap_err_low = (merged['tau_smap_median'] - merged['tau_smap_ci95_low']).to_numpy()
    tau_smap_err_high = (merged['tau_smap_ci95_high'] - merged['tau_smap_median']).to_numpy()
    err_smap = [tau_smap_err_low, tau_smap_err_high]
    
    tau_ol = merged['tau_ol_median'].to_numpy()
    tau_ol_err_low = (merged['tau_ol_median'] - merged['tau_ol_ci95_low']).to_numpy()
    tau_ol_err_high = (merged['tau_ol_ci95_high'] - merged['tau_ol_median']).to_numpy()
    err_ol = [tau_ol_err_low, tau_ol_err_high]
    
    b1 = ax_a.bar(x - width/2, tau_smap, width, yerr=err_smap, capsize=3,
                  label='SMAP (uncensored)', color=c_smap, edgecolor='black', linewidth=0.7)
    b2 = ax_a.bar(x + width/2, tau_ol, width, yerr=err_ol, capsize=3,
                  label='Noah-MP OL', color=c_ol, edgecolor='black', linewidth=0.7)
                  
    ax_a.set_title("(a) Spring drying time scale $\\tau$ (days)", fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xticks(x)
    labels = [f"{t}\n({c:.0f}% clay)" for t, c in zip(textures, clays)]
    ax_a.set_xticklabels(labels, fontsize=8.5)
    ax_a.set_ylabel("$\\tau$ (days) [median $\\pm$ 95% CI]", fontsize=10.5)
    ax_a.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_a.legend(loc='upper right', fontsize=9.5)
    
    # ── Panel (b): P5 floor vs SMCWLT ─────────────────────────────────────────
    ax_b = fig.add_subplot(gs[1])
    
    p5_smap = merged['p5_smap_uncensored'].to_numpy()
    p5_ol = merged['p5_ol'].to_numpy()
    wilt = merged['smcwlt'].to_numpy()
    
    w_b = 0.26
    ax_b.bar(x - w_b, p5_smap, w_b, label='SMAP uncensored $P_5$', color=c_smap, edgecolor='black', linewidth=0.7)
    ax_b.bar(x, p5_ol, w_b, label='Noah-MP OL $P_5$', color=c_ol, edgecolor='black', linewidth=0.7)
    ax_b.bar(x + w_b, wilt, w_b, label='Noah-MP $\\theta_{\\mathrm{wilt}}$', color=c_wilt, edgecolor='black', linewidth=0.7, hatch='//')
    
    ax_b.set_title("(b) Dry-down floor $P_5$ vs Wilting Point $\\theta_{\\mathrm{wilt}}$", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(labels, fontsize=8.5)
    ax_b.set_ylabel("Surface Soil Moisture ($\\mathrm{m}^3\\,\\mathrm{m}^{-3}$)", fontsize=10.5)
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b.legend(loc='upper left', fontsize=9.5)
    
    # ── Panel (c): tau vs clay regression ─────────────────────────────────────
    ax_c = fig.add_subplot(gs[2])
    
    # Plot points
    ax_c.scatter(clays, tau_smap, color=c_smap, s=70, edgecolor='black', zorder=4, label='SMAP points')
    ax_c.scatter(clays, tau_ol, color=c_ol, s=70, edgecolor='black', zorder=4, label='OL points')
    
    # Add regression lines
    # From bootstrap slopes MAM: SMAP slope = +4.40 d/fraction (or +0.044 d/%clay), OL slope = -18.38 d/fraction (-0.1838 d/%clay)
    # Fit linear models on the class medians for the plot line
    poly_smap = np.polyfit(clays, tau_smap, 1)
    poly_ol = np.polyfit(clays, tau_ol, 1)
    
    x_fine = np.linspace(0, 65, 100)
    ax_c.plot(x_fine, np.polyval(poly_smap, x_fine), color=c_smap, linestyle='-', linewidth=2.0,
              label=f"SMAP slope: +4.40 d / frac [p<0.001]")
    ax_c.plot(x_fine, np.polyval(poly_ol, x_fine), color=c_ol, linestyle='--', linewidth=2.0,
              label=f"OL slope: -18.38 d / frac [p<0.001]")
              
    ax_c.set_title("(c) Drying time scale $\\tau$ vs Clay Fraction", fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xlabel("Clay Fraction (%)", fontsize=10.5)
    ax_c.set_ylabel("$\\tau$ (days)", fontsize=10.5)
    ax_c.set_xlim(0, 65)
    ax_c.set_ylim(0, 35)
    ax_c.grid(True, linestyle=':', alpha=0.7)
    ax_c.legend(loc='upper right', fontsize=9.0)
    
    # Note on physical meaning
    ax_c.annotate("Physical: capillary retention\nslows drying as clay increases",
                  xy=(35, 5), xytext=(22, 10),
                  arrowprops=dict(arrowstyle="->", color=c_smap, lw=1.2),
                  fontsize=8.5, color='#B25000', fontweight='bold')
                  
    ax_c.annotate("Noah-MP inverted artifact:\nsand dries in 30d, clay in 6d",
                  xy=(10, 25), xytext=(15, 27),
                  arrowprops=dict(arrowstyle="->", color=c_ol, lw=1.2),
                  fontsize=8.5, color='#004C99', fontweight='bold')
    
    fig.suptitle("Figure 4 — Spring (MAM) Soil Moisture Dry-Down Dynamics: Physical SMAP vs Inverted Noah-MP",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
