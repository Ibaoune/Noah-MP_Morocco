#!/usr/bin/env python3
"""
fig_03.py
---------
Figure 3: Selection bias induced by the Noah-MP wilting filter QC.
Panels:
  (a) Departure from Open-Loop (OL) for accepted vs uncensored SMAP retrievals,
      by month and soil texture class (2016-2020).
  (b) Summer (JJA) surface soil moisture difference Δθ1 (DA-NoCDF - OL)
      stratified by censorship rate class (IRRIGFRAC = 0).

Outputs:
  paper1/figures/fig_03.png (200 dpi)
  paper1/figures/fig_03_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SRC_CSV = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/drydown_point1_uncensored/e5_selection_bias_summary.csv"
OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_03.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_03_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # 1. Parse CSV (has two sections separated by comment)
    with open(SRC_CSV, 'r') as f:
        lines = f.readlines()
        
    part_a_lines = []
    part_b_lines = []
    current_part = None
    for line in lines:
        if line.startswith("# PARTIE A"):
            current_part = 'A'
            continue
        elif line.startswith("# PARTIE B"):
            current_part = 'B'
            continue
        if current_part == 'A' and line.strip():
            part_a_lines.append(line)
        elif current_part == 'B' and line.strip():
            part_b_lines.append(line)
            
    import io
    df_a = pd.read_csv(io.StringIO("".join(part_a_lines)))
    df_b = pd.read_csv(io.StringIO("".join(part_b_lines)))
    
    # Save combined plot data
    with open(OUT_CSV, 'w') as f:
        f.write("# PART_A_MONTHLY_DEPARTURE_BY_TEXTURE\n")
        df_a.to_csv(f, index=False)
        f.write("\n# PART_B_DELTA_THETA1_BY_CENSORSHIP_CLASS\n")
        df_b.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # 2. Setup Figure
    fig = plt.figure(figsize=(16, 7))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.3, 1.0], wspace=0.22,
                           left=0.07, right=0.95, top=0.88, bottom=0.14)
    
    # Panel (a): Monthly departures (accepted vs uncensored)
    ax_a = fig.add_subplot(gs[0])
    
    # Colors for textures (accessible palette)
    texture_colors = {
        'Domaine Entier': '#000000',
        'Sandy Loam': '#E69F00',
        'Loam': '#56B4E9',
        'Sandy Clay Loam': '#009E73',
        'Clay Loam': '#D55E00',
        'Clay': '#CC79A7'
    }
    
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    for soil, col in texture_colors.items():
        sub = df_a[df_a['soil_class'] == soil].sort_values('month')
        if not sub.empty:
            ls = '-' if soil == 'Domaine Entier' else '--'
            lw = 2.5 if soil in ['Domaine Entier', 'Clay', 'Clay Loam'] else 1.5
            x_vals = sub['month'].to_numpy()
            y_vals = (sub['selection_bias_accepted_minus_uncens'] * 1000.0).to_numpy()
            ax_a.plot(x_vals, y_vals,
                      label=f"{soil}", color=col, linestyle=ls, linewidth=lw, marker='o', markersize=4)
                      
    ax_a.set_title("(a) Positive selection bias in assimilated SMAP: $(O_{acc} - \\mathrm{OL}) - (O_{unc} - \\mathrm{OL})$",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Month of Year", fontsize=10.5)
    ax_a.set_ylabel("Selection Bias ($10^{-3}\\;\\mathrm{m}^3\\,\\mathrm{m}^{-3}$)", fontsize=10.5)
    ax_a.set_xticks(months)
    ax_a.set_xticklabels(month_names, fontsize=9.5)
    ax_a.grid(True, linestyle=':', alpha=0.6)
    ax_a.legend(loc='upper right', fontsize=9, framealpha=0.95)
    ax_a.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    
    # Panel (b): Δθ1 JJA by censorship class
    ax_b = fig.add_subplot(gs[1])
    
    classes = df_b['censorship_class'].tolist()
    delta_theta = (df_b['mean_delta_theta1_all'] * 1000.0).to_numpy() # Convert to 10^-3 m3/m3
    n_pix = df_b['n_pixels_total'].tolist()
    
    x_b = np.arange(len(classes))
    bars = ax_b.bar(x_b, delta_theta, color='#D55E00', edgecolor='black', linewidth=0.8, width=0.55)
    
    ax_b.set_title("(b) Summer (JJA) $\\Delta\\theta_1$ (DA-NoCDF - OL) by Censorship Class",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xticks(x_b)
    ax_b.set_xticklabels([f"{c}\n(N={n})" for c, n in zip(classes, n_pix)], fontsize=9.5)
    ax_b.set_xlabel("Wilting Filter Censorship Rate Class (JJA)", fontsize=10.5)
    ax_b.set_ylabel("Mean Summer $\\Delta\\theta_1$ ($10^{-3}\\;\\mathrm{m}^3\\,\\mathrm{m}^{-3}$)", fontsize=10.5)
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Add values on top of bars
    for b in bars:
        h = b.get_height()
        va = 'bottom' if h >= 0 else 'top'
        y_pos = h + (0.3 if h >= 0 else -0.5)
        ax_b.annotate(f"+{h:.2f}" if h >= 0 else f"{h:.2f}",
                      xy=(b.get_x() + b.get_width() / 2, y_pos),
                      ha='center', va=va, fontsize=9, fontweight='bold')
                      
    ax_b.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax_b.set_ylim(-1, 16)
    
    fig.suptitle("Figure 3 — Systematic Selection Effect of the Noah-MP Wilting Filter QC (2016–2020)",
                 fontsize=13.5, fontweight='bold', y=0.98)
    
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
