import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

import config

figures = {
    "fig01_study_domain.png": "Requires cartopy/xarray environment.\nPlease run python3 fig01_study_domain.py\nin your conda spatial environment.",
    "fig02_methodology_flowchart.png": "Requires matplotlib/graphviz.\nPlease run python3 fig02_methodology_flowchart.py.",
    "fig03_sm_assim_impact_Overall.png": "Requires cartopy/xarray environment.\nPlease run python3 fig03_sm_assim_impact.py.",
    "fig04_runoff_irrigation.png": "Requires cartopy/xarray environment.\nPlease run python3 fig04_runoff_irrigation.py.",
    "fig05_runoff_decomposition.png": "Requires cartopy/xarray environment.\nPlease run python3 fig05_runoff_decomposition.py.",
    "fig06_09_gldas_intercomparison_placeholder.png": "Figures 6-9: GLDAS Intercomparison\n(Requires GLDAS NetCDF data)",
    "fig13_14_impact_drivers_placeholder.png": "Figures 13-14: Spatial Impact Drivers\n(Requires full HyMAP data)"
}

for filename, message in figures.items():
    filepath = os.path.join(config.DIR_FIGURES, filename)
    if not os.path.exists(filepath):
        plt.rcParams.update(config.PLOT_RC_PARAMS)
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, message, ha='center', va='center', size=14, wrap=True)
        plt.axis('off')
        plt.savefig(filepath)
        plt.close()
        print(f"Generated placeholder for {filename}")
