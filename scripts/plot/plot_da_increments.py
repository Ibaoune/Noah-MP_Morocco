# Author: M. EL Aabaribaoune (@um6p)
import os
import glob
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import warnings

warnings.filterwarnings("ignore")

# Define directories
EXP_DIR = "experiments/DA_Joint_sebou/EnKF"
OUT_DIR = "experiments/plots"
os.makedirs(OUT_DIR, exist_ok=True)

def plot_lai_increments():
    # Find all increment files for LAI (a02)
    files = sorted(glob.glob(os.path.join(EXP_DIR, "*", "*_incr.a02.d01.nc")))
    
    if not files:
        print(f"No LAI increment files found in {EXP_DIR}")
        return
        
    dates = []
    mean_increments = []
    
    print(f"Found {len(files)} LAI increment files. Processing...")
    
    for f in files:
        # Extract date from filename, e.g., LIS_DA_EnKF_202006090000_incr.a02.d01.nc
        basename = os.path.basename(f)
        date_str = basename.split('_')[3]
        date_obj = pd.to_datetime(date_str, format='%Y%m%d%H%M')
        
        # Open dataset
        ds = xr.open_dataset(f)
        
        # Calculate spatial mean of the increment
        incr_val = ds['anlys_incr_LAI_02'].mean().values
        
        dates.append(date_obj)
        mean_increments.append(float(incr_val))
        ds.close()
        
    # Plotting
    plt.figure(figsize=(10, 5))
    plt.plot(dates, mean_increments, marker='o', linestyle='-', color='forestgreen', linewidth=2, markersize=8)
    
    plt.axhline(0, color='black', linestyle='--', linewidth=1)
    
    plt.title('Basin-Averaged LAI Assimilation Increments (Summer 2020)', fontsize=14, pad=15)
    plt.ylabel('Δ LAI Increment (-)', fontsize=12)
    plt.xlabel('Date', fontsize=12)
    plt.grid(True, linestyle=':', alpha=0.7)
    
    # Format x-axis
    plt.gcf().autofmt_xdate()
    
    out_path = os.path.join(OUT_DIR, 'DA_LAI_Increments_TimeSeries.png')
    plt.savefig(out_path, dpi=300, bbox_inches='tight')
    print(f"Saved LAI Increment plot to {out_path}")
    plt.close()

if __name__ == "__main__":
    plot_lai_increments()
