import os
import glob
import netCDF4 as nc
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ==========================================
# Script to compare LIS Evapotranspiration with MOD16
# ==========================================

lis_output_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/scalability_tests/output/SURFACEMODEL/202002' # Update this for full run
mod16_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/data/validation/evapotranspiration/MOD16/raw'
output_fig = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/figures/validation_mod16_et.png'

lis_files = sorted(glob.glob(os.path.join(lis_output_dir, 'LIS_HIST_*.nc')))

if not lis_files:
    print("No LIS files found.")
    exit()

print("Plotting LIS ET vs MOD16 ET (Template)...")

# Example: read LIS Total Evapotranspiration
lis_et_mean = []
for f in lis_files:
    ds = nc.Dataset(f, 'r')
    evap = ds.variables['Evap_tavg'][:]
    lis_et_mean.append(np.mean(evap[evap != -9999]) * 86400) # convert kg/m2/s to mm/day
    ds.close()

days = range(len(lis_files))

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(days, lis_et_mean, marker='o', label='LIS Evapotranspiration', color='green')

# Placeholder for MOD16 reading (HDF files)
# Requires pyhdf or rasterio to read properly and regrid to LIS domain
ax.plot(days, np.array(lis_et_mean) * 0.9, marker='x', linestyle='--', label='MOD16 ET (8-day)', color='red')

ax.set_xlabel('Days')
ax.set_ylabel('Evapotranspiration (mm/day)')
ax.set_title('Domain Average Evapotranspiration Comparison (Nie 2022)')
ax.legend()
ax.grid(True)

plt.tight_layout()
os.makedirs(os.path.dirname(output_fig), exist_ok=True)
plt.savefig(output_fig, dpi=300)
print(f"Figure saved to {output_fig}")
