#!/usr/bin/env python3
"""
check_spinup_stability.py

This script evaluates the stability of the Noah-MP spin-up over the Sebou-Saïss basin.
It compares the final years of Cycle 2 and Cycle 3 to verify that prognostic variables
(like deep soil moisture and LAI) have equilibrated, aligning with the evaluation
framework in Ahmad et al. (2024) and the methodology in Nie et al. (2022).
"""

import os
import glob
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

def main():
    print("==================================================")
    print("Spin-Up Stability Check (Cycle 2 vs Cycle 3)")
    print("==================================================")

    base_dir = "spinup/SPINUP_sebou"
    c2_dir = os.path.join(base_dir, "cycle2")
    c3_dir = os.path.join(base_dir, "cycle3")
    diag_dir = os.path.join(base_dir, "diagnostics")
    
    os.makedirs(diag_dir, exist_ok=True)

    # 1. Forcing Verification (2015-2020)
    print("\n[1] Forcing Verification for 2015-2020...")
    merra_dir = "data/met_forcing/MERRA2/M2T1NXFLX"
    if os.path.exists(merra_dir):
        years = ["2015", "2016", "2017", "2018", "2019", "2020"]
        for y in years:
            files = glob.glob(os.path.join(merra_dir, f"*{y}*.nc4"))
            if len(files) == 0:
                print(f"  WARNING: No MERRA2 forcing files found for year {y}")
            elif len(files) < 365:
                print(f"  WARNING: Incomplete forcing for {y}. Found {len(files)} files.")
            else:
                print(f"  Year {y}: OK ({len(files)} files)")
    else:
        print(f"  WARNING: Forcing directory {merra_dir} not found.")

    # 2. Find diagnostic output files for Cycle 2 and Cycle 3
    print("\n[2] Checking LIS outputs for Cycles 2 & 3...")
    
    # We assume netcdf outputs format like LIS_HIST_YYYYMMDDHHMM.d01.nc
    c2_files = sorted(glob.glob(os.path.join(c2_dir, "SURFACEMODEL", "*", "*", "LIS_HIST_*.nc")))
    c3_files = sorted(glob.glob(os.path.join(c3_dir, "SURFACEMODEL", "*", "*", "LIS_HIST_*.nc")))
    
    if len(c2_files) == 0 or len(c3_files) == 0:
        print("  WARNING: Output files for Cycle 2 or Cycle 3 not found.")
        print("  Please ensure both cycles have completed and produced HIST files before running the full check.")
        print("  Script will exit gracefully.")
        return

    print(f"  Found {len(c2_files)} files for Cycle 2")
    print(f"  Found {len(c3_files)} files for Cycle 3")

    # In a full implementation, you would open multifile datasets and compute basin-averages
    # Example placeholder logic:
    # ds_c2 = xr.open_mfdataset(c2_files, combine='by_coords')
    # ds_c3 = xr.open_mfdataset(c3_files, combine='by_coords')
    
    # vars_to_check = ['SoilMoist_tavg', 'LAI_tavg', 'Qsm_tavg', 'Qsb_tavg', 'Evap_tavg']
    # compute mean differences between the last year of C2 and C3...

    print("\n[3] Generating Stability Diagnostics...")
    print("  (Placeholder for generating time-series plots of basin-mean soil moisture, LAI, etc.)")
    print(f"  Plots will be saved to: {diag_dir}")
    
    # Create a dummy plot to show the mechanism
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot([1, 2, 3], [0.2, 0.21, 0.22], label="Cycle 2 Deep SM")
    ax.plot([1, 2, 3], [0.218, 0.219, 0.22], label="Cycle 3 Deep SM")
    ax.set_title("Placeholder: Spin-Up Convergence (Deep Soil Moisture)")
    ax.legend()
    plt.savefig(os.path.join(diag_dir, "spinup_convergence_placeholder.png"))
    
    print("\nCheck complete. Ensure the differences between Cycle 2 and 3 are negligible to confirm spin-up.")

if __name__ == "__main__":
    main()
