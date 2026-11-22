#!/usr/bin/env python3
"""
fig_Sc.py
---------
Figure S-c: Normalized innovations and ensemble spread diagnostics (Step 5d).
Panels:
  (a) Monthly variance of normalized innovations Var(d / sqrt(HPH^T + R)) with sigma_o = 0.04.
      (Ideal filter = 1.0; highlights summer collapse in DA-NoCDF due to wilting filter truncation).
  (b) Monthly mean normalized innovation (normalized bias).
  (c) Mean surface soil moisture spread (theta_1) comparing standard DA against NOSTATE (MAM 2018).

Outputs:
  paper1/figures/fig_Sc.png (200 dpi)
  paper1/figures/fig_Sc_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
INNOV_CSV = os.path.join(BASE_DIR, "paper1/tables/innovations_and_spread_by_month_and_texture.csv")
NOSTATE_CSV = os.path.join(BASE_DIR, "paper1/tables/comparison_da_nocdf_vs_nostate_mam2018.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_Sc.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_Sc_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_innov = pd.read_csv(INNOV_CSV)
    df_nostate = pd.read_csv(NOSTATE_CSV)
    
    # Filter Domain_All
    df_dom = df_innov[df_innov['texture_class'] == 'Domain_All'].copy()
    
    # Save plotted data CSV
    with open(OUT_CSV, 'w') as f:
        f.write("# DOMAIN_INNOVATIONS_AND_SPREAD\n")
        df_dom.to_csv(f, index=False)
        f.write("\n# NOSTATE_VS_NOCDF_MAM2018_COMPARISON\n")
        df_nostate.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # ── 2. Setup Figure (3 panels) ─────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 6))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.1, 1.0], wspace=0.25,
                           left=0.06, right=0.96, top=0.86, bottom=0.15)
                           
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Consistent experiment colors:
    # DA_nocdf: '#D55E00' (Vermillion)
    # DA_cdf: '#CC79A7'   (Reddish Purple)
    # DA_nocdf_nowilt: '#E69F00' (Orange)
    c_nocdf = '#D55E00'
    c_cdf = '#CC79A7'
    c_nowilt = '#E69F00'
    
    # ── Panel (a): Variance of Normalized Innovations ──────────────────────────
    ax_a = fig.add_subplot(gs[0])
    
    for exp, col, ls, lbl in [('DA_nocdf', c_nocdf, '-', 'DA-NoCDF (Wilting QC)'),
                              ('DA_cdf', c_cdf, '-.', 'DA-CDF (Rescaled)'),
                              ('DA_nocdf_nowilt', c_nowilt, '--', 'DA-NoCDF-noWQC (Uncensored)')]:
        sub = df_dom[df_dom['experiment'] == exp].sort_values('month')
        if not sub.empty:
            ax_a.plot(months, sub['var_norm_innov'].to_numpy(), color=col, linestyle=ls,
                      linewidth=2.0, marker='o', markersize=4, label=lbl)
                      
    ax_a.axhline(1.0, color='black', linestyle='--', linewidth=1.0, label='Ideal Variance = 1.0')
    ax_a.set_title("(a) Variance of Normalized Innovations: $\\mathrm{Var}(d / \\sqrt{HPH^T + R})$",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Month of Year (2018)", fontsize=10.5)
    ax_a.set_ylabel("Normalized Variance", fontsize=10.5)
    ax_a.set_xticks(months)
    ax_a.set_xticklabels(month_names, fontsize=8.5)
    ax_a.set_ylim(0.1, 1.7)
    ax_a.grid(True, linestyle=':', alpha=0.6)
    ax_a.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    # Highlight summer truncation
    ax_a.annotate("Summer artificial collapse:\nWilting filter censors dry tail\n(Var drops to 0.31)",
                  xy=(6, 0.31), xytext=(4.2, 0.55),
                  arrowprops=dict(arrowstyle="->", color=c_nocdf, lw=1.2),
                  fontsize=8.5, color='#B25000', fontweight='bold')
                  
    # ── Panel (b): Mean Normalized Innovation (Normalized Bias) ────────────────
    ax_b = fig.add_subplot(gs[1])
    
    for exp, col, ls, lbl in [('DA_nocdf', c_nocdf, '-', 'DA-NoCDF'),
                              ('DA_cdf', c_cdf, '-.', 'DA-CDF'),
                              ('DA_nocdf_nowilt', c_nowilt, '--', 'DA-NoCDF-noWQC')]:
        sub = df_dom[df_dom['experiment'] == exp].sort_values('month')
        if not sub.empty:
            ax_b.plot(months, sub['mean_norm_innov'].to_numpy(), color=col, linestyle=ls,
                      linewidth=2.0, marker='s', markersize=4, label=lbl)
                      
    ax_b.axhline(0.0, color='black', linestyle='--', linewidth=0.8, label='Zero Bias')
    ax_b.set_title("(b) Mean Normalized Innovation: $\\mathrm{Mean}(d / \\sqrt{HPH^T + R})$",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xlabel("Month of Year (2018)", fontsize=10.5)
    ax_b.set_ylabel("Normalized Mean", fontsize=10.5)
    ax_b.set_xticks(months)
    ax_b.set_xticklabels(month_names, fontsize=8.5)
    ax_b.set_ylim(-0.6, 0.5)
    ax_b.grid(True, linestyle=':', alpha=0.6)
    ax_b.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    # ── Panel (c): Ensemble Spread Comparison (Standard vs NOSTATE) ────────────
    ax_c = fig.add_subplot(gs[2])
    
    # Contrast DA_nocdf (standard additive state pert) vs DA_nocdf_nostate_2018MAM (forcing pert only)
    x_c = np.arange(2)
    spread_vals = [0.04396, 0.01250]
    labels_c = ['DA-NoCDF\n(State + Forc Pert)', 'DA-NoState\n(Forcing Pert Only)']
    colors_c = [c_nocdf, '#0072B2']
    
    bars_c = ax_c.bar(x_c, spread_vals, color=colors_c, edgecolor='black', linewidth=0.8, width=0.5)
    
    ax_c.set_title("(c) Spring (MAM) $\\theta_1$ Ensemble Spread", fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(labels_c, fontsize=9.5)
    ax_c.set_ylabel("$\\theta_1$ Spread ($m^3 / m^3$)", fontsize=10.5)
    ax_c.set_ylim(0, 0.06)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    for b in bars_c:
        h = b.get_height()
        ax_c.annotate(f"{h:.4f} m³/m³",
                      xy=(b.get_x() + b.get_width() / 2, h + 0.0015),
                      ha='center', va='bottom', fontsize=9.0, fontweight='bold')
                      
    ax_c.annotate("-71.6% Spread Collapse\nwithout state pert",
                  xy=(1, 0.0125), xytext=(0.4, 0.025),
                  arrowprops=dict(arrowstyle="->", color='#0072B2', lw=1.2),
                  fontsize=8.5, color='#0072B2', fontweight='bold')
                  
    fig.suptitle("Figure S-c — Normalized Innovations and Ensemble Spread Diagnostics (2018)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
