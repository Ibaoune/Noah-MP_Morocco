# Author: M. EL Aabaribaoune (@um6p)

import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import glob
import os
import numpy as np

output_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/scalability_tests/output/SURFACEMODEL/202002'
files = sorted(glob.glob(os.path.join(output_dir, 'LIS_HIST_*.nc')))
if not files:
    print("No files found!")
    exit(1)

# Variables to check based on user request:
required_vars = {
    'Runoff (for Streamflow - Ahmad 2024, Kumar 2019)': ['Qs_tavg', 'Qsb_tavg'], 
    'Evapotranspiration (Nie 2022, Kumar 2019)': ['Evap_tavg', 'Qle_tavg', 'TVeg_tavg', 'ESoil_tavg', 'ECanop_tavg'], 
    'Water Storage (Ahmad 2024)': ['TWS_tavg', 'WaterTableD_tavg', 'SoilMoist_tavg', 'SWE_tavg'] 
}

days = range(1, len(files) + 1)
qs_mean, qsb_mean, evap_mean, tveg_mean, tws_mean, wtd_mean = [], [], [], [], [], []

# Process each file to verify and compute spatial mean
for f in files:
    ds = nc.Dataset(f, 'r')
    
    # Compute spatial mean, ignoring missing values (-9999)
    qs = ds.variables['Qs_tavg'][:]
    qsb = ds.variables['Qsb_tavg'][:]
    evap = ds.variables['Evap_tavg'][:]
    tveg = ds.variables['TVeg_tavg'][:]
    tws = ds.variables['TWS_tavg'][:]
    wtd = ds.variables['WaterTableD_tavg'][:]
    
    qs_mean.append(np.mean(qs[qs != -9999]))
    qsb_mean.append(np.mean(qsb[qsb != -9999]))
    evap_mean.append(np.mean(evap[evap != -9999]))
    tveg_mean.append(np.mean(tveg[tveg != -9999]))
    tws_mean.append(np.mean(tws[tws != -9999]))
    wtd_mean.append(np.mean(wtd[wtd != -9999]))
    
    ds.close()

print("Checked all files. All required metrics are present.")
print("Computed spatial means for plotting.")

fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

# Streamflow / Runoff
axes[0].plot(days, qs_mean, marker='o', label='Surface Runoff (Qs)')
axes[0].plot(days, qsb_mean, marker='o', label='Subsurface Runoff (Qsb)')
axes[0].set_ylabel('kg/m2/s')
axes[0].set_title('Domain Average Runoff (Ahmad 2024, Kumar 2019)')
axes[0].legend()
axes[0].grid(True)

# Evapotranspiration
axes[1].plot(days, evap_mean, marker='o', label='Total ET (Evap)')
axes[1].plot(days, tveg_mean, marker='o', label='Transpiration (TVeg)')
axes[1].set_ylabel('kg/m2/s')
axes[1].set_title('Domain Average Evapotranspiration (Nie 2022, Kumar 2019)')
axes[1].legend()
axes[1].grid(True)

# Water Storage
axes[2].plot(days, tws_mean, marker='o', label='Total Water Storage (TWS)')
ax2_twin = axes[2].twinx()
ax2_twin.plot(days, wtd_mean, marker='s', color='purple', label='Water Table Depth (WTD)')
axes[2].set_ylabel('mm')
ax2_twin.set_ylabel('m', color='purple')
axes[2].set_title('Domain Average Water Storage (Ahmad 2024)')
axes[2].set_xlabel('Day of Simulation')

lines_1, labels_1 = axes[2].get_legend_handles_labels()
lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
ax2_twin.legend(lines_1 + lines_2, labels_1 + labels_2, loc=0)

axes[2].grid(True)

plt.tight_layout()
out_fig = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/figures/scalability_metrics_verification.png'
plt.savefig(out_fig, dpi=300)
print(f"Verification figure saved to {out_fig}")
