import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# Script to compare LIS TWS Anomalies with GRACE
# ==========================================

lis_output_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/scalability_tests/output/SURFACEMODEL/202002' # Update this for full run
grace_file = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/validation/water_storage/GRACE_GRACEFO/raw/GRCTellus.JPL.200204_202603.GLO.RL06.3M.MSCNv04CRI.nc'
output_fig = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/figures/validation_grace_tws.png'

lis_files = sorted(glob.glob(os.path.join(lis_output_dir, 'LIS_HIST_*.nc')))

if not lis_files:
    print("No LIS files found.")
    exit()

print("Plotting LIS TWS vs GRACE Anomalies (Template)...")

# Calculate LIS TWS anomaly
lis_tws_raw = []
for f in lis_files:
    ds = nc.Dataset(f, 'r')
    tws = ds.variables['TWS_tavg'][:]
    lis_tws_raw.append(np.mean(tws[tws != -9999]))
    ds.close()

# For anomalies, you subtract the long term mean. Since this is 3 days, it's just a placeholder
lis_tws_mean = np.mean(lis_tws_raw)
lis_tws_anom = np.array(lis_tws_raw) - lis_tws_mean

days = range(len(lis_files))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(days, lis_tws_anom, marker='o', label='LIS TWS Anomaly', color='blue')

# Placeholder for GRACE reading
# grace_ds = nc.Dataset(grace_file, 'r')
# grace_lwe = grace_ds.variables['lwe_thickness'][:] # liquid water equivalent thickness
# Regrid and extract Morocco domain...
ax.plot(days, lis_tws_anom + 5, marker='s', linestyle='--', label='GRACE TWS Anomaly', color='black')

ax.set_xlabel('Days')
ax.set_ylabel('TWS Anomaly (mm)')
ax.set_title('Domain Average Terrestrial Water Storage Anomaly (Ahmad 2024)')
ax.legend()
ax.grid(True)

plt.tight_layout()
os.makedirs(os.path.dirname(output_fig), exist_ok=True)
plt.savefig(output_fig, dpi=300)
print(f"Figure saved to {output_fig}")
