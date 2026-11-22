#!/usr/bin/env python3
"""
fig_07.py
---------
Figure 7: Water balance closure and mechanism analysis.
Panels:
  (a) 2018 Monthly water balance residual R = P - ET - Qs - Qsb - ΔS
      for OL-DAIC, ENS-OL, DA-NoCDF, and DA-NoCDF-noWQC, with EnKF increments.
  (b) Monthly simulated Evapotranspiration (ET) in 2018 across experiments.
  (c) March 2018 sensitivity tests: residual R across OL-DAIC, NOSTATE, FORC,
      FORC-noRyu, STATE, STATE-noRyu, and ENS.
  (d) E6 mechanism water terms decomposition (stacked bars) from instrumented Step 2 runs.
  [Panel (e) 2018 vs 2017 omitted pending completion of 2017 multi-year runs].

Outputs:
  paper1/figures/fig_07.png (200 dpi)
  paper1/figures/fig_07_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
WB_MONTHLY_CSV = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit/reports/audits/diag2018_e6_clean/internal_water_balance_monthly.csv"
MARCH_TESTS_CSV = os.path.join(BASE_DIR, "paper1/tables/march2018_ryu_test.csv")
MECH_BUDGET_CSV = os.path.join(BASE_DIR, "paper1/tables/march2018_mechanism_budget.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_07.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_07_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Load Data ───────────────────────────────────────────────────────────
    df_wb = pd.read_csv(WB_MONTHLY_CSV)
    df_wb_12 = df_wb[df_wb['month'].str.startswith('2018-')].copy()
    
    df_march = pd.read_csv(MARCH_TESTS_CSV)
    df_mech = pd.read_csv(MECH_BUDGET_CSV)
    
    # Save combined plot data
    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_B_MONTHLY_WATER_BALANCE_2018\n")
        df_wb_12.to_csv(f, index=False)
        f.write("\n# PANEL_C_MARCH_2018_SENSITIVITY_RESIDUALS\n")
        df_march[['run', 'P_mm', 'ET_mm', 'Qs_mm', 'Qsb_mm', 'dStock_mm', 'Residu_mm']].to_csv(f, index=False)
        f.write("\n# PANEL_D_MECHANISM_WATER_TERMS_STEP2\n")
        df_mech.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")
    
    # ── 2. Setup Figure (2x2 Grid) ─────────────────────────────────────────────
    fig = plt.figure(figsize=(18, 12))
    gs = gridspec.GridSpec(2, 2, height_ratios=[1.0, 1.0], width_ratios=[1.1, 1.0],
                           hspace=0.28, wspace=0.20, left=0.06, right=0.96, top=0.92, bottom=0.08)
                           
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Consistent colorblind-friendly colors:
    c_oldaic = '#56B4E9'  # Sky Blue
    c_ens = '#009E73'     # Green
    c_nocdf = '#D55E00'   # Vermillion
    c_nowilt = '#E69F00'  # Orange
    
    # ── Panel (a): Monthly Water Balance Residual R & Increments ───────────────
    ax_a = fig.add_subplot(gs[0, 0])
    
    ax_a.plot(months, df_wb_12['Residu_OL_DAIC'].to_numpy(), color=c_oldaic, linestyle='-', linewidth=2.0,
              marker='o', markersize=4, label='OL-DAIC Residual (Unperturbed baseline)')
    ax_a.plot(months, df_wb_12['Residu_ENS'].to_numpy(), color=c_ens, linestyle='-', linewidth=2.0,
              marker='s', markersize=4, label='ENS-OL Residual (Additive pert. leak)')
    ax_a.plot(months, df_wb_12['Residu_DA'].to_numpy(), color=c_nocdf, linestyle='-', linewidth=2.2,
              marker='^', markersize=4.5, label='DA-NoCDF Residual R')
    ax_a.plot(months, df_wb_12['Incr_EnKF'].to_numpy(), color=c_nocdf, linestyle=':', linewidth=1.8,
              label='DA-NoCDF Archived Incr')
    ax_a.plot(months, df_wb_12['Residu_DA_nowilt'].to_numpy(), color=c_nowilt, linestyle='-', linewidth=2.2,
              marker='v', markersize=4.5, label='DA-NoCDF-noWQC Residual R')
    ax_a.plot(months, df_wb_12['Incr_EnKF_nowilt'].to_numpy(), color=c_nowilt, linestyle=':', linewidth=1.8,
              label='DA-NoCDF-noWQC Archived Incr')
              
    ax_a.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    ax_a.set_title("(a) Monthly Internal Water Balance Residual $R = P - ET - Q_s - Q_{sb} - \\Delta S$ (2018)",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Month of Year", fontsize=10.5)
    ax_a.set_ylabel("Water Equivalent (mm / month)", fontsize=10.5)
    ax_a.set_xticks(months)
    ax_a.set_xticklabels(month_names, fontsize=8.5)
    ax_a.grid(True, linestyle=':', alpha=0.6)
    ax_a.legend(loc='lower left', fontsize=8.5, framealpha=0.95, ncol=2)
    
    # ── Panel (b): Monthly Simulated ET ────────────────────────────────────────
    ax_b = fig.add_subplot(gs[0, 1])
    
    ax_b.plot(months, df_wb_12['ET_OL_DAIC'].to_numpy(), color=c_oldaic, linestyle='-', linewidth=2.0,
              marker='o', markersize=4, label='OL-DAIC')
    ax_b.plot(months, df_wb_12['ET_ENS'].to_numpy(), color=c_ens, linestyle='-', linewidth=2.0,
              marker='s', markersize=4, label='ENS-OL (+5.9 mm/mo in spring)')
    ax_b.plot(months, df_wb_12['ET_DA'].to_numpy(), color=c_nocdf, linestyle='-', linewidth=2.2,
              marker='^', markersize=4.5, label='DA-NoCDF (Reduced ET)')
    ax_b.plot(months, df_wb_12['ET_DA_nowilt'].to_numpy(), color=c_nowilt, linestyle='-', linewidth=2.2,
              marker='v', markersize=4.5, label='DA-NoCDF-noWQC (Lowest ET)')
              
    ax_b.set_title("(b) Monthly Evapotranspiration (ET) in 2018", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xlabel("Month of Year", fontsize=10.5)
    ax_b.set_ylabel("ET (mm / month)", fontsize=10.5)
    ax_b.set_xticks(months)
    ax_b.set_xticklabels(month_names, fontsize=8.5)
    ax_b.grid(True, linestyle=':', alpha=0.6)
    ax_b.legend(loc='upper right', fontsize=9.0, framealpha=0.95)
    
    # ── Panel (c): March 2018 Sensitivity Tests ────────────────────────────────
    ax_c = fig.add_subplot(gs[1, 0])
    
    # Order of runs: OL_DAIC, NOSTATE, FORC, FORC_noRyu, STATE, STATE_noRyu, ENS
    target_order = ['OL_DAIC', 'NOSTATE', 'FORC', 'FORC_noRyu', 'STATE', 'STATE_noRyu', 'ENS']
    df_march_sorted = df_march.set_index('run').reindex(target_order).reset_index()
    
    x_c = np.arange(len(target_order))
    res_c = df_march_sorted['Residu_mm'].to_numpy()
    
    colors_c = ['#56B4E9', '#0072B2', '#490092', '#882255', '#D55E00', '#B22222', '#009E73']
    bars_c = ax_c.bar(x_c, res_c, color=colors_c, edgecolor='black', linewidth=0.7, width=0.55)
    
    ax_c.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax_c.set_title("(c) March 2018 Water Balance Residual: Deconstructing Perturbation Leaks",
                   fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xticks(x_c)
    ax_c.set_xticklabels(target_order, fontsize=9.0, rotation=20)
    ax_c.set_ylabel("Residual $R$ (mm / month)", fontsize=10.5)
    ax_c.grid(True, axis='y', linestyle='--', alpha=0.7)
    
    for b in bars_c:
        h = b.get_height()
        va = 'top' if h < 0 else 'bottom'
        y_pos = h - 1.0 if h < 0 else h + 0.4
        ax_c.annotate(f"{h:.2f} mm",
                      xy=(b.get_x() + b.get_width() / 2, y_pos),
                      ha='center', va=va, fontsize=8.5, fontweight='bold')
    ax_c.set_ylim(-26, 3)
    
    # ── Panel (d): Stacked Bar Water Decomposition (Step 2 Mechanism E6) ───────
    ax_d = fig.add_subplot(gs[1, 1])
    
    # Runs in step 2:
    # ENS_STATE_201803, ENS_STATE_201803_noRyu, ENS_FORC_201803, ENS_FORC_201803_noRyu
    mech_runs = ['ENS_STATE', 'STATE_noRyu', 'ENS_FORC', 'FORC_noRyu']
    x_d = np.arange(len(mech_runs))
    
    w_pert = df_mech['w_pert_mm'].to_numpy()
    w_ryu = df_mech['w_ryu_mm'].to_numpy()
    w_qc = df_mech['w_qc_mm'].to_numpy()
    w_mid = df_mech['w_mid_mm'].to_numpy()
    w_rec = df_mech['w_rec_mm'].to_numpy()
    
    # Stacked components
    p1 = ax_d.bar(x_d, w_pert, 0.5, label='applyLSMPert (raw pert)', color='#490092', edgecolor='black', lw=0.6)
    p2 = ax_d.bar(x_d, w_ryu, 0.5, bottom=w_pert, label='Ryu Recentering', color='#56B4E9', edgecolor='black', lw=0.6)
    p3 = ax_d.bar(x_d, w_qc, 0.5, bottom=w_pert+w_ryu, label='NoahMP401_qcsoilm', color='#E69F00', edgecolor='black', lw=0.6)
    p4 = ax_d.bar(x_d, w_mid, 0.5, bottom=w_pert+w_ryu+w_qc, label='Midrange Replacement', color='#D55E00', edgecolor='black', lw=0.6)
    p5 = ax_d.bar(x_d, w_rec, 0.5, bottom=w_pert+w_ryu+w_qc+w_mid, label='setsoilm Recentering', color='#009E73', edgecolor='black', lw=0.6)
    
    # Net sum points
    ax_d.scatter(x_d, df_mech['w_sum_mm'].to_numpy(), color='black', s=50, zorder=5, label='Net Code Water Flux ($\\Sigma w$)')
    
    ax_d.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax_d.set_title("(d) Step 2 Instrumented Water Budget Breakdown (Mechanism E6)", fontsize=11.5, fontweight='bold', pad=8)
    ax_d.set_xticks(x_d)
    ax_d.set_xticklabels(mech_runs, fontsize=9.0)
    ax_d.set_ylabel("Water Added / Removed (mm / month)", fontsize=10.5)
    ax_d.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_d.legend(loc='lower left', fontsize=8.0, framealpha=0.95)
    
    fig.suptitle("Figure 7 — Water Balance Non-Closure and Deconstruction of State Perturbation Artifacts",
                 fontsize=14, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
