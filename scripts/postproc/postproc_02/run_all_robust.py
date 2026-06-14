import subprocess
import os
import matplotlib.pyplot as plt

# We don't import config here in case config itself has issues, but we can try
import config

scripts = {
    "fig01_spatial_context.py": "fig01_spatial_context.png",
    "fig02_spatial_impact_fluxes.py": "fig02_spatial_impact_fluxes_placeholder.png",
    "fig03_stats_by_ecosystem.py": "fig03_stats_by_ecosystem_placeholder.png",
    "fig04_lai_dynamics.py": "fig04_lai_dynamics.png",
    "fig05_drought_categorization.py": "fig05_drought_categorization.png",
    "fig06_extreme_event_response.py": "fig06_extreme_event_response_placeholder.png",
    "supp_statistical_analysis.py": "supp_statistical_analysis_placeholder.png"
}

os.environ['MPLBACKEND'] = 'Agg'

for script, expected_png in scripts.items():
    print(f"Running {script}...")
    res = subprocess.run(["python3", script], capture_output=True, text=True)
    
    png_path = os.path.join(config.DIR_FIGURES, expected_png)
    
    if res.returncode != 0:
        print(f"Error running {script}:\n{res.stderr}")
        # Generate placeholder
        plt.figure(figsize=(10, 6))
        # Keep error message short
        err_msg = res.stderr.strip().split('\n')[-1] if res.stderr else "Unknown error"
        msg = f"Failed to generate {script}\n\nError:\n{err_msg}\n\nPlease run in a conda environment with cartopy/xarray."
        plt.text(0.5, 0.5, msg, ha='center', va='center', size=12, wrap=True)
        plt.axis('off')
        plt.savefig(png_path, bbox_inches='tight')
        plt.close()
    else:
        print(f"{script} ran successfully.")

