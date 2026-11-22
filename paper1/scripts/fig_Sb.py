#!/usr/bin/env python3
"""
fig_Sb.py
---------
Figure S-b: High-frequency verification of applied vs archived EnKF analysis increments (Step 4 v2).
Panels:
  (a) Scatter comparison of event-mean applied jump vs archived increment (mm) across 12 assimilation events (Nov 1-5, 2018).
  (b) Overall Pearson correlation (r) and recovery ratio (applied / archived) by soil layer.
  (c) Contrast between unperturbed analysis hours (07:00, 19:00: pure analysis jump, ratio ~ 1.00)
      and 3-hourly perturbation hours (06:00, 18:00: corrected via witness perturbation).

Outputs:
  paper1/figures/fig_Sb.png (200 dpi)
  paper1/figures/fig_Sb_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
EVENTS_CSV = os.path.join(BASE_DIR, "paper1/tables/applied_vs_archived_increments_v2.csv")
SUMMARY_CSV = os.path.join(BASE_DIR, "paper1/tables/applied_vs_archived_increments_summary_v2.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_Sb.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_Sb_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    df_events = pd.read_csv(EVENTS_CSV)
    df_summary = pd.read_csv(SUMMARY_CSV)
    
    # Save plotted data CSV
    with open(OUT_CSV, 'w') as f:
        f.write("# SUMMARY_INCREMENTS_RECOVERY\n")
        df_summary.to_csv(f, index=False)
        f.write("\n# EVENT_LEVEL_INCREMENTS_DATA\n")
        df_events.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # Setup Figure (3 panels)
    fig = plt.figure(figsize=(18, 6))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.1, 1.0, 1.1], wspace=0.25,
                           left=0.06, right=0.96, top=0.86, bottom=0.15)
                           
    layer_colors = {
        'Layer 1': '#D55E00',       # Vermillion
        'Layer 2': '#E69F00',       # Orange
        'Layer 3': '#56B4E9',       # Sky Blue
        'Layer 4': '#CC79A7',       # Purple
        'Column Total': '#009E73'   # Green
    }
    
    # ── Panel (a): Scatter Plot across 12 events ──────────────────────────────
    ax_a = fig.add_subplot(gs[0])
    
    for l_name, col in layer_colors.items():
        sub = df_events[df_events['layer'] == l_name]
        x_val = sub['mean_archived_mm'].to_numpy()
        y_val = sub['mean_applied_mm'].to_numpy()
        ax_a.scatter(x_val, y_val, color=col, s=45, edgecolor='black', lw=0.6, label=f"{l_name}")
        
    # 1:1 Identity Line
    lims = [-5, 12]
    ax_a.plot(lims, lims, color='black', linestyle='--', linewidth=1.2, label='1:1 Ideal Identity')
    ax_a.set_xlim(lims)
    ax_a.set_ylim(lims)
    ax_a.set_title("(a) Event-Mean Applied vs Archived Increment (mm)", fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Archived EnKF Increment (mm)", fontsize=10.5)
    ax_a.set_ylabel("Diagnosed Applied Jump $\\Delta_{net}$ (mm)", fontsize=10.5)
    ax_a.grid(True, linestyle=':', alpha=0.6)
    ax_a.legend(loc='upper left', fontsize=8.5, framealpha=0.95)
    
    # ── Panel (b): Recovery Ratio and Correlation by Layer ────────────────────
    ax_b = fig.add_subplot(gs[1])
    
    levels = df_summary['level'].tolist()
    r_vals = df_summary['correlation_r'].to_numpy()
    ratio_vals = df_summary['ratio_applied_archived'].to_numpy()
    
    x_b = np.arange(len(levels))
    width_b = 0.35
    
    rects1 = ax_b.bar(x_b - width_b/2, r_vals, width_b, label='Pearson Correlation (r)', color='#0072B2', edgecolor='black', lw=0.7)
    rects2 = ax_b.bar(x_b + width_b/2, ratio_vals, width_b, label='Recovery Ratio (Applied / Arch)', color='#E69F00', edgecolor='black', lw=0.7)
    
    ax_b.axhline(1.0, color='gray', linestyle='--', linewidth=0.8)
    ax_b.set_title("(b) Increment Fidelity (N = 22,077 Grid Cells)", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xticks(x_b)
    lbls = ['L1\n(0-10cm)', 'L2\n(10-40cm)', 'L3\n(40-100cm)', 'L4\n(100-200cm)', 'Column\n(0-200cm)']
    ax_b.set_xticklabels(lbls, fontsize=8.5)
    ax_b.set_ylabel("Metric Value", fontsize=10.5)
    ax_b.set_ylim(0, 1.4)
    ax_b.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    for r, h in zip(rects1, r_vals):
        ax_b.annotate(f"{h:.3f}", xy=(r.get_x() + r.get_width()/2, h + 0.02),
                      ha='center', va='bottom', fontsize=7.5, rotation=45)
    for r, h in zip(rects2, ratio_vals):
        if h < 2.0:
            ax_b.annotate(f"{h:.2f}", xy=(r.get_x() + r.get_width()/2, h + 0.02),
                          ha='center', va='bottom', fontsize=7.5, rotation=45)
        else:
            ax_b.annotate(f"{h:.2f}*", xy=(r.get_x() + r.get_width()/2, 1.32),
                          ha='center', va='bottom', fontsize=7.5, color='red', fontweight='bold')
                          
    # ── Panel (c): Perturbation Hour vs Non-Perturbation Hour Ratio ───────────
    ax_c = fig.add_subplot(gs[2])
    
    sub_l1 = df_events[df_events['layer'] == 'Layer 1']
    sub_col = df_events[df_events['layer'] == 'Column Total']
    
    # Plot ratios for L1 and Column over events
    events_x = np.arange(len(sub_l1))
    times = [t.split()[1] for t in sub_l1['event_time']]
    is_pert = sub_l1['is_pert_hour'].to_numpy()
    
    bar_cols = ['#D55E00' if p else '#0072B2' for p in is_pert]
    bars_c = ax_c.bar(events_x, sub_col['ratio_applied_archived'].to_numpy(), color=bar_cols, edgecolor='black', lw=0.7, width=0.6)
    
    ax_c.axhline(1.0, color='black', linestyle='--', linewidth=0.9)
    ax_c.set_title("(c) Event Column Recovery Ratio (Red: 3h Perturbation Hours)", fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xticks(events_x)
    ax_c.set_xticklabels(times, fontsize=8.0, rotation=45)
    ax_c.set_xlabel("Event Assimilation Time (Nov 1–5, 2018)", fontsize=10.0)
    ax_c.set_ylabel("Column Ratio (Applied / Archived)", fontsize=10.5)
    ax_c.set_ylim(0.7, 1.3)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    # Custom legend
    from matplotlib.patches import Patch
    leg_elements = [
        Patch(facecolor='#0072B2', edgecolor='black', label='Pure Analysis (07:00, 19:00) [Ratio: 1.003]'),
        Patch(facecolor='#D55E00', edgecolor='black', label='With Perturbation (06:00, 18:00) [Ratio: 0.954]')
    ]
    ax_c.legend(handles=leg_elements, loc='upper right', fontsize=8.2, framealpha=0.95)
    
    fig.suptitle("Figure S-b — High-Frequency Diagnosis of Applied vs Archived EnKF Increments (DA_nocdf_diag_15min)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
