"""
fig05_drought_categorization.py

Objective: Generate Figure 5 for the SSM-DA evaluation publication.
5a: Time series of the percentage of area affected by drought categories (D0 to D4).
5b: Scatterplot of drought-affected area percentage (OL vs SSM-DA).

Droughts are calculated using daily percentiles of root-zone soil moisture
relative to the OL climatology.
"""

import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import config_postproc as config

def plot_drought_categorization():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    # Placeholder logic:
    # 1. Load root-zone soil moisture from OL and DA.
    # 2. Calculate daily percentiles based on the OL multi-year climatology.
    # 3. Classify into D0 (<30%), D1 (<20%), D2 (<10%), D3 (<5%), D4 (<2%).
    # 4. Calculate % area in each category over time.
    
    # Generate dummy data
    dates = pd.date_range(start="2015-01-01", periods=1800, freq="D")
    
    # Simulated percentage of area in drought (D0 to D4)
    # D0 > D1 > D2 > D3 > D4
    np.random.seed(123)
    base_drought = np.sin(np.linspace(0, 10*np.pi, 1800)) * 20 + 25
    base_drought += np.random.normal(0, 5, 1800)
    base_drought = np.clip(base_drought, 0, 100)
    
    ol_d0 = base_drought
    ol_d1 = ol_d0 * 0.7
    ol_d2 = ol_d1 * 0.5
    ol_d3 = ol_d2 * 0.4
    ol_d4 = ol_d3 * 0.2
    
    # DA might reduce false alarm droughts due to irrigation assimilation
    da_d0 = ol_d0 * 0.85 + np.random.normal(0, 2, 1800)
    da_d0 = np.clip(da_d0, 0, 100)
    
    # Plotting
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [2, 1]})
    
    # Figure 5a: Time series of area affected (using stacked or overlapping, here overlapping lines for OL)
    # To keep it readable, let's plot D0 to D4 for DA as filled areas, and OL as lines
    ax1.fill_between(dates, 0, da_d0, color='#ffff00', label='D0 Abnormally Dry (DA)', alpha=0.8)
    ax1.fill_between(dates, 0, da_d0*0.7, color='#fcd37f', label='D1 Moderate (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.35, color='#ffaa00', label='D2 Severe (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.14, color='#e60000', label='D3 Extreme (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.03, color='#730000', label='D4 Exceptional (DA)', alpha=0.9)
    
    # Plot OL D0 as a reference line
    ax1.plot(dates, ol_d0, color='black', linestyle='--', linewidth=1.5, label='D0 Total (OL)')
    
    ax1.set_title("(a) Drought Area Evolution based on Root-Zone Soil Moisture")
    ax1.set_ylabel("Basin Area (%)")
    ax1.set_xlabel("Year")
    ax1.set_ylim(0, 100)
    ax1.legend(loc='upper right', ncol=2, fontsize=10)
    
    # Figure 5b: Scatterplot OL vs DA (D0+ Area)
    ax2.scatter(ol_d0, da_d0, color=config.COLORS['DA'], alpha=0.5, s=15)
    ax2.plot([0, 100], [0, 100], 'k--', linewidth=2)
    ax2.set_title("(b) Drought Area Scatterplot (D0+)")
    ax2.set_xlabel("% Area in Drought (OL)")
    ax2.set_ylabel("% Area in Drought (SSM-DA)")
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle=':', alpha=0.7)

    plt.tight_layout()
    output_path = os.path.join(config.DIR_FIGURES, "fig05_drought_categorization.png")
    plt.savefig(output_path)
    print(f"Figure 5 saved to: {output_path}")

if __name__ == "__main__":
    plot_drought_categorization()
