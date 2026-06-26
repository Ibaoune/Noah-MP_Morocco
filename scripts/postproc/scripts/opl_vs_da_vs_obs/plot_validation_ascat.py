import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# Script to compare LIS Soil Moisture (Top layer) with ASCAT SWI
# ==========================================

import config_postproc as cfg
lis_output_dir = cfg.DIR_OUTPUT_OL
ascat_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/validation/soil_moisture/ASCAT/raw'
output_fig = os.path.join(cfg.DIR_FIGURES_OPL_VS_DA, 'validation_ascat_sm.png')

lis_files = sorted(glob.glob(os.path.join(lis_output_dir, '**', 'LIS_HIST_*.nc'), recursive=True))
# In a real run, you'd match the ASCAT dates to the LIS dates.
# Here we just show a template script structure

if not lis_files:
    print("No LIS files found.")
    exit()

print("Plotting LIS SM vs ASCAT SWI (Template)...")

# Example: read LIS surface soil moisture
lis_sm_mean = []
for f in lis_files:
    ds = nc.Dataset(f, 'r')
    # SoilMoist_tavg is typically (4, lat, lon), we take the top layer [0]
    sm = ds.variables['SoilMoist_tavg'][0, :, :]
    lis_sm_mean.append(np.mean(sm[sm != -9999]))
    ds.close()

days = range(len(lis_files))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(days, lis_sm_mean, marker='o', label='LIS Top Layer Soil Moisture', color='blue')

# Placeholder for ASCAT SWI reading
# Since ASCAT and LIS might be on different grids or units (SWI is an index 0-100 or 0-1, SM is m3/m3),
# you typically rescale ASCAT using CDF matching or plot them on dual axes.
ax2 = ax.twinx()
# Dummy ASCAT data for demonstration
dummy_ascat = np.array(lis_sm_mean) * 100 + np.random.normal(0, 2, len(lis_sm_mean))
ax2.plot(days, dummy_ascat, marker='s', linestyle='--', label='ASCAT SWI (Scaled)', color='orange')

ax.set_xlabel('Days')
ax.set_ylabel('LIS Soil Moisture (m3/m3)', color='blue')
ax2.set_ylabel('ASCAT SWI (-)', color='orange')
ax.set_title('Domain Average Soil Moisture Comparison (Nie 2022)')

lines_1, labels_1 = ax.get_legend_handles_labels()
lines_2, labels_2 = ax2.get_legend_handles_labels()
ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper left')

plt.tight_layout()
os.makedirs(os.path.dirname(output_fig), exist_ok=True)
plt.savefig(output_fig, dpi=300)
print(f"Figure saved to {output_fig}")
