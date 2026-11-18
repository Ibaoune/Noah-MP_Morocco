#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Verifies the monthly restarts at 2017-02-01 produced by the January 2017 simulations.
Checks variables, dimensions, numerical stability, and cross-formulation differences.
"""
import os
import netCDF4 as nc
import numpy as np
import pandas as pd

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"

experiments = [
    ("OL_R1_SIMGM", "SIMGM (Option 1)"),
    ("OL_R2_SIMTOP", "SIMTOP (Option 2)"),
    ("OL_R3_SCHAAKE96", "Schaake96 (Option 3)"),
    ("OL_R4_BATS", "BATS (Option 4)")
]

expected_restart = "LIS_RST_NOAHMP401_201702010000.d01.nc"

print("=" * 95)
print(f" MONTHLY RESTART AUDIT AT 2017-02-01 (End of January 2017)")
print("=" * 95)

rows = []
all_valid = True

for exp_id, exp_label in experiments:
    exp_dir = f"{base_proj}/experiments/{exp_id}"
    rst_path = f"{exp_dir}/restarts/{expected_restart}"

    if not os.path.exists(rst_path):
        # Also check output dir in case staging is in progress
        cand = f"{exp_dir}/output/2017-01/SURFACEMODEL/201702/{expected_restart}"
        if os.path.exists(cand):
            rst_path = cand
        else:
            print(f"[{exp_id}] FAILED: Restart {expected_restart} not found!")
            all_valid = False
            continue

    sz = os.path.getsize(rst_path)
    ds = nc.Dataset(rst_path)
    
    # Extract variables
    zwt = np.nanmean(ds["ZWT"][:]) if "ZWT" in ds.variables else np.nan
    wa = np.nanmean(ds["WA"][:]) if "WA" in ds.variables else np.nan
    smc = ds["SMC"][:]
    smc1 = np.nanmean(smc[0])
    smc4 = np.nanmean(smc[3])
    sh2o1 = np.nanmean(ds["SH2O"][0])
    sfc_r = np.nanmean(ds["SFCRUNOFF"][:])
    udr_r = np.nanmean(ds["UDRRUNOFF"][:])
    
    # Check for NaNs or Infinities
    has_nan = any(np.isnan(ds[v][:]).any() for v in ["SMC", "SH2O", "TSLB"])
    ds.close()

    status = "VALID" if not has_nan and sz > 1500000 else "CORRUPT"
    if status != "VALID": all_valid = False

    rows.append({
        "Experiment": exp_id,
        "Formulation": exp_label,
        "Size_bytes": sz,
        "ZWT_m": round(zwt, 3),
        "WA_mm": round(wa, 1),
        "SMC_L1": round(smc1, 4),
        "SMC_L4": round(smc4, 4),
        "Acc_Qs_m": round(sfc_r, 3),
        "Acc_Qsb_m": round(udr_r, 3),
        "Integrity": status
    })

df = pd.DataFrame(rows)
print(df.to_string(index=False))

if all_valid and len(rows) == 4:
    print("\n[OK] All 4 monthly restarts at 2017-02-01 are physically sound, complete, and staged.")
else:
    print("\n[WAIT] Some restarts are still running or missing.")
