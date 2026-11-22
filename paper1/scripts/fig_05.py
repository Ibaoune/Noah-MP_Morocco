#!/usr/bin/env python3
"""
fig_05.py
---------
Figure 5: Multi-year monthly changes DA - OL (2016-2020) for DA-NoCDF and DA-CDF.
Panels:
  (a) Soil moisture change Δθ by soil layer (Layers 1-4: 0-10, 10-40, 40-100, 100-200 cm).
  (b) Monthly flux anomalies: Evapotranspiration (ΔET), surface runoff (ΔQs), baseflow (ΔQsb).
  (c) Column archived analysis increments vs water balance implied flux response.

Outputs:
  paper1/figures/fig_05.png (200 dpi)
  paper1/figures/fig_05_data.csv
"""

import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
PARQUET_FILE = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/To_rm/data/processed/monthly_pixel_dataset_2016_2020_static.parquet"

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_05.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_05_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # 1. Load Parquet
    print(f"Reading {PARQUET_FILE}...")
    df = pd.read_parquet(PARQUET_FILE)
    
    # Compute column increments in mm
    for exp in ['DA_NoCDF', 'DA_CDF']:
        df[f'incr_L1_mm_{exp}'] = df[f'increment_SMC_L1_{exp}'] * 100.0
        df[f'incr_L2_mm_{exp}'] = df[f'increment_SMC_L2_{exp}'] * 300.0
        df[f'incr_L3_mm_{exp}'] = df[f'increment_SMC_L3_{exp}'] * 600.0
        df[f'incr_L4_mm_{exp}'] = df[f'increment_SMC_L4_{exp}'] * 1000.0
        df[f'incr_col_mm_{exp}'] = (df[f'incr_L1_mm_{exp}'] + df[f'incr_L2_mm_{exp}'] +
                                    df[f'incr_L3_mm_{exp}'] + df[f'incr_L4_mm_{exp}'])
                                    
        # Layer moisture differences (DA - OPL) in m3/m3
        for k in range(1, 5):
            df[f'delta_SMC_L{k}_{exp}'] = df[f'SMC_L{k}_{exp}'] - df[f'SMC_L{k}_OPL']
            
        # Flux differences (DA - OPL) in mm/month
        df[f'delta_ET_{exp}'] = df[f'Evap_tavg_{exp}'] - df['Evap_tavg_OPL']
        df[f'delta_Qs_{exp}'] = df[f'Qs_tavg_{exp}'] - df['Qs_tavg_OPL']
        df[f'delta_Qsb_{exp}'] = df[f'Qsb_tavg_{exp}'] - df['Qsb_tavg_OPL']
        df[f'delta_flux_{exp}'] = df[f'delta_ET_{exp}'] + df[f'delta_Qs_{exp}'] + df[f'delta_Qsb_{exp}']

    # Groupby calendar month (1 to 12)
    m_agg = df.groupby('month').mean()
    m_agg.to_csv(OUT_CSV)
    print(f"Saved plotted data to {OUT_CSV}")
    
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Setup Figure (3 panels vertically or 1x3 horizontally)
    fig = plt.figure(figsize=(19, 6.5))
    gs = gridspec.GridSpec(1, 3, width_ratios=[1.0, 1.0, 1.0], wspace=0.25,
                           left=0.06, right=0.96, top=0.86, bottom=0.14)
                           
    # Color scheme:
    # DA-NoCDF: vermillion '#D55E00'
    # DA-CDF: reddish purple '#CC79A7'
    c_nocdf = '#D55E00'
    c_cdf = '#CC79A7'
    
    # ── Panel (a): Soil Moisture Changes Δθ by Layer ─────────────────────────
    ax_a = fig.add_subplot(gs[0])
    
    layer_styles = {
        1: ('-', 2.2, 'L1 (0–10 cm)'),
        2: ('--', 1.8, 'L2 (10–40 cm)'),
        3: ('-.', 1.5, 'L3 (40–100 cm)'),
        4: (':', 1.3, 'L4 (100–200 cm)')
    }
    
    for k, (ls, lw, lbl) in layer_styles.items():
        y_nocdf = (m_agg[f'delta_SMC_L{k}_DA_NoCDF'] * 1000.0).to_numpy()
        ax_a.plot(months, y_nocdf, color=c_nocdf, linestyle=ls, linewidth=lw,
                  label=f"NoCDF {lbl}")
                  
    # Add L1 and L2 for DA-CDF for direct contrast
    ax_a.plot(months, (m_agg['delta_SMC_L1_DA_CDF'] * 1000.0).to_numpy(),
              color=c_cdf, linestyle='-', linewidth=2.0, label="CDF L1 (0–10 cm)")
    ax_a.plot(months, (m_agg['delta_SMC_L2_DA_CDF'] * 1000.0).to_numpy(),
              color=c_cdf, linestyle='--', linewidth=1.6, label="CDF L2 (10–40 cm)")
              
    ax_a.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    ax_a.set_title("(a) Soil Moisture Anomaly $\\Delta\\theta$ (DA - OL)", fontsize=11.5, fontweight='bold', pad=8)
    ax_a.set_xlabel("Month of Year", fontsize=10.5)
    ax_a.set_ylabel("$\\Delta\\theta$ ($10^{-3}\\;\\mathrm{m}^3\\,\\mathrm{m}^{-3}$)", fontsize=10.5)
    ax_a.set_xticks(months)
    ax_a.set_xticklabels(month_names, fontsize=8.5)
    ax_a.grid(True, linestyle=':', alpha=0.6)
    ax_a.legend(loc='lower left', fontsize=8.0, framealpha=0.95, ncol=2)
    
    # ── Panel (b): Monthly Flux Anomalies ΔET, ΔQs, ΔQsb ─────────────────────
    ax_b = fig.add_subplot(gs[1])
    
    # DA-NoCDF
    ax_b.plot(months, m_agg['delta_ET_DA_NoCDF'].to_numpy(), color=c_nocdf, linestyle='-', linewidth=2.2,
              marker='o', markersize=4, label='NoCDF $\\Delta$ET')
    ax_b.plot(months, m_agg['delta_Qsb_DA_NoCDF'].to_numpy(), color=c_nocdf, linestyle='--', linewidth=1.8,
              marker='s', markersize=3.5, label='NoCDF $\\Delta$Qsb')
    ax_b.plot(months, m_agg['delta_Qs_DA_NoCDF'].to_numpy(), color=c_nocdf, linestyle=':', linewidth=1.5,
              label='NoCDF $\\Delta$Qs')
              
    # DA-CDF
    ax_b.plot(months, m_agg['delta_ET_DA_CDF'].to_numpy(), color=c_cdf, linestyle='-', linewidth=2.0,
              marker='^', markersize=4, label='CDF $\\Delta$ET')
    ax_b.plot(months, m_agg['delta_Qsb_DA_CDF'].to_numpy(), color=c_cdf, linestyle='--', linewidth=1.6,
              label='CDF $\\Delta$Qsb')
              
    ax_b.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    ax_b.set_title("(b) Water Flux Anomalies (DA - OL)", fontsize=11.5, fontweight='bold', pad=8)
    ax_b.set_xlabel("Month of Year", fontsize=10.5)
    ax_b.set_ylabel("Flux Difference (mm / month)", fontsize=10.5)
    ax_b.set_xticks(months)
    ax_b.set_xticklabels(month_names, fontsize=8.5)
    ax_b.grid(True, linestyle=':', alpha=0.6)
    ax_b.legend(loc='upper right', fontsize=8.5, framealpha=0.95, ncol=2)
    
    # ── Panel (c): Archived Increments vs Implied Water ──────────────────────
    ax_c = fig.add_subplot(gs[2])
    
    # Column increment vs ΔFlux
    ax_c.plot(months, m_agg['incr_col_mm_DA_NoCDF'].to_numpy(), color=c_nocdf, linestyle='-', linewidth=2.2,
              marker='o', markersize=4, label='NoCDF Archived Incr (mm)')
    ax_c.plot(months, m_agg['delta_flux_DA_NoCDF'].to_numpy(), color='#B25000', linestyle='--', linewidth=2.0,
              marker='s', markersize=3.5, label='NoCDF $\\Delta$(ET+Qs+Qsb)')
              
    ax_c.plot(months, m_agg['incr_col_mm_DA_CDF'].to_numpy(), color=c_cdf, linestyle='-', linewidth=2.0,
              marker='^', markersize=4, label='CDF Archived Incr (mm)')
    ax_c.plot(months, m_agg['delta_flux_DA_CDF'].to_numpy(), color='#7B3294', linestyle='--', linewidth=1.6,
              label='CDF $\\Delta$(ET+Qs+Qsb)')
              
    ax_c.axhline(0, color='gray', linestyle='-', linewidth=0.8)
    ax_c.set_title("(c) Archived Increments vs Implied Flux Change", fontsize=11.5, fontweight='bold', pad=8)
    ax_c.set_xlabel("Month of Year", fontsize=10.5)
    ax_c.set_ylabel("Water Equivalent (mm / month)", fontsize=10.5)
    ax_c.set_xticks(months)
    ax_c.set_xticklabels(month_names, fontsize=8.5)
    ax_c.grid(True, linestyle=':', alpha=0.6)
    ax_c.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    
    fig.suptitle("Figure 5 — Monthly DA - OL Hydrological Impact and Increment Water Balance (2016–2020)",
                 fontsize=13.5, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
