#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Check and compare short sanity test outputs across the 4 OPL hydrology formulations.
"""
import os
import netCDF4 as nc
import numpy as np

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"

experiments = [
    ("OL_R1_SIMGM", "SIMGM (Option 1)"),
    ("OL_R2_SIMTOP", "SIMTOP (Option 2)"),
    ("OL_R3_SCHAAKE96", "Schaake96 (Option 3)"),
    ("OL_R4_BATS", "BATS (Option 4)")
]

files_to_check = ["LIS_HIST_201701020000.d01.nc", "LIS_HIST_201701030000.d01.nc"]

print("=" * 80)
print(" SHORT SANITY TEST VALIDATION (2017-01-01 to 2017-01-03)")
print("=" * 80)

for fname in files_to_check:
    print(f"\n>>> Checking History File: {fname}")
    header = f"{'Experiment':<16} | {'Qs [mm/d]':<11} | {'Qsb [mm/d]':<11} | {'Qtot [mm/d]':<11} | {'Evap [mm/d]':<11} | {'SM_L1 [m3/m3]':<12} | {'SM_L4 [m3/m3]':<12}"
    print(header)
    print("-" * len(header))
    
    for exp_id, exp_label in experiments:
        fpath = f"{base_proj}/experiments/{exp_id}/test_short/output/SURFACEMODEL/201701/{fname}"
        if not os.path.exists(fpath):
            print(f"{exp_id:<16} | FILE NOT FOUND")
            continue
            
        ds = nc.Dataset(fpath)
        # Fluxes are in kg m-2 s-1 == mm/s. Convert to mm/day by * 86400
        qs = ds["Qs_tavg"][:] * 86400.0
        qsb = ds["Qsb_tavg"][:] * 86400.0
        qtot = qs + qsb
        evap = ds["Evap_tavg"][:] * 86400.0 if "Evap_tavg" in ds.variables else np.nan
        sm = ds["SoilMoist_tavg"][:]  # (time, soil_layer, lat, lon)
        
        # Valid data mask (exclude < 0)
        valid = (qs >= 0) & ~np.isnan(qs)
        
        m_qs = np.nanmean(qs[valid])
        m_qsb = np.nanmean(qsb[valid])
        m_qtot = np.nanmean(qtot[valid])
        m_evap = np.nanmean(evap[valid]) if not np.isnan(evap).all() else 0.0
        
        if sm.ndim == 4:
            sm_l1 = np.nanmean(sm[0, 0][valid[0] if valid.ndim==3 else valid])
            sm_l4 = np.nanmean(sm[0, 3][valid[0] if valid.ndim==3 else valid])
        else:
            sm_l1 = np.nan
            sm_l4 = np.nan
            
        ds.close()
        
        print(f"{exp_id:<16} | {m_qs:11.4f} | {m_qsb:11.4f} | {m_qtot:11.4f} | {m_evap:11.4f} | {sm_l1:12.4f} | {sm_l4:12.4f}")

# Also check restart file at 2017-01-03 00:00:00
print("\n" + "=" * 80)
print(" TERMINAL RESTART VERIFICATION (LIS_RST_NOAHMP401_201701030000.d01.nc)")
print("=" * 80)
rst_header = f"{'Experiment':<16} | {'ZWT [m]':<10} | {'WA [mm]':<10} | {'SMC_L1':<10} | {'SMC_L4':<10} | {'SFCRUNOFF':<10} | {'UDRRUNOFF':<10}"
print(rst_header)
print("-" * len(rst_header))

for exp_id, exp_label in experiments:
    rpath = f"{base_proj}/experiments/{exp_id}/test_short/output/SURFACEMODEL/201701/LIS_RST_NOAHMP401_201701030000.d01.nc"
    if not os.path.exists(rpath):
        print(f"{exp_id:<16} | RESTART NOT FOUND")
        continue
    ds = nc.Dataset(rpath)
    zwt = np.nanmean(ds["ZWT"][:]) if "ZWT" in ds.variables else np.nan
    wa = np.nanmean(ds["WA"][:]) if "WA" in ds.variables else np.nan
    smc = ds["SMC"][:]
    smc_l1 = np.nanmean(smc[0])
    smc_l4 = np.nanmean(smc[3])
    sfc_r = np.nanmean(ds["SFCRUNOFF"][:])
    udr_r = np.nanmean(ds["UDRRUNOFF"][:])
    ds.close()
    print(f"{exp_id:<16} | {zwt:10.3f} | {wa:10.1f} | {smc_l1:10.4f} | {smc_l4:10.4f} | {sfc_r:10.3f} | {udr_r:10.3f}")

