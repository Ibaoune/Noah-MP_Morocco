import subprocess
import os
import matplotlib.pyplot as plt

# We don't import config here in case config itself has issues, but we can try
import config

scripts = {
    "fig01_study_domain.py": "fig01_study_domain.png",
    "fig02_methodology_flowchart.py": "fig02_methodology_flowchart.png",
    "fig03_sm_assim_impact.py": "fig03_sm_assim_impact_Overall.png", # Might produce multiple, but we expect at least one
    "fig04_runoff_irrigation.py": "fig04_runoff_irrigation.png",
    "fig05_runoff_decomposition.py": "fig05_runoff_decomposition.png",
    "fig06_09_gldas_intercomparison.py": "fig06_09_gldas_intercomparison_placeholder.png",
    "fig10_12_streamflow_validation.py": "fig10_12_streamflow_validation_placeholder.png",
    "fig13_14_spatial_impact_drivers.py": "fig13_14_impact_drivers_placeholder.png"
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

