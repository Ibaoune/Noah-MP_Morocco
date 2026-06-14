"""
fig02_methodology_flowchart.py

Objective: Generate Figure 2 for the publication.
Describe clearly the experimental protocol (Forcing -> LIS/Noah-MP -> OL vs DA -> HyMAP).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import config_postproc as config

def plot_flowchart():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')

    # Define box properties
    box_props = dict(boxstyle="round,pad=0.5", fc="white", ec="black", lw=2)
    da_props = dict(boxstyle="round,pad=0.5", fc="#ffeedd", ec="#ff7f0e", lw=2)
    ol_props = dict(boxstyle="round,pad=0.5", fc="#ddeeff", ec="#1f77b4", lw=2)

    # 1. Forcings
    ax.text(0.5, 0.9, "Meteorological Forcings\n(IMERG, GDAS, etc.)", 
            ha="center", va="center", size=14, fontweight='bold', bbox=box_props)

    # 2. Model
    ax.text(0.5, 0.7, "Land Information System (LIS)\nNoah-MP Surface Model", 
            ha="center", va="center", size=14, fontweight='bold', bbox=box_props)

    # 3. Simulations
    ax.text(0.25, 0.5, "Open Loop (OL)\nSimulation\n(No Assimilation)", 
            ha="center", va="center", size=14, fontweight='bold', bbox=ol_props)

    ax.text(0.75, 0.5, "Data Assimilation (DA)\nSimulation\n(EnKF SMAP DA)", 
            ha="center", va="center", size=14, fontweight='bold', bbox=da_props)

    # 4. Routing
    ax.text(0.5, 0.3, "HyMAP\nOffline Routing", 
            ha="center", va="center", size=14, fontweight='bold', bbox=box_props)

    # 5. Validation
    ax.text(0.5, 0.1, "Validation\n(In-situ discharge, GLDAS)", 
            ha="center", va="center", size=14, fontweight='bold', bbox=box_props)

    # Arrows
    arrow_props = dict(facecolor='black', edgecolor='black', shrink=0.05, width=2, headwidth=8)
    
    # Forcings -> LIS
    ax.annotate('', xy=(0.5, 0.75), xytext=(0.5, 0.85), arrowprops=arrow_props)
    
    # LIS -> OL / DA
    ax.annotate('', xy=(0.3, 0.55), xytext=(0.45, 0.65), arrowprops=arrow_props)
    ax.annotate('', xy=(0.7, 0.55), xytext=(0.55, 0.65), arrowprops=arrow_props)
    
    # OL / DA -> HyMAP
    ax.annotate('', xy=(0.45, 0.35), xytext=(0.3, 0.45), arrowprops=arrow_props)
    ax.annotate('', xy=(0.55, 0.35), xytext=(0.7, 0.45), arrowprops=arrow_props)
    
    # HyMAP -> Validation
    ax.annotate('', xy=(0.5, 0.15), xytext=(0.5, 0.25), arrowprops=arrow_props)

    plt.title("Figure 2: Experimental Protocol", fontweight='bold', size=16, y=1.05)
    
    output_path = os.path.join(config.DIR_FIGURES, "fig02_methodology_flowchart.png")
    plt.savefig(output_path)
    print(f"Figure 2 saved to: {output_path}")

if __name__ == "__main__":
    plot_flowchart()
