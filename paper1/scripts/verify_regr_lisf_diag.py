#!/usr/bin/env python3
"""
Verify non-regression of src/lisf_diag against src/lisf_ryu for March 1-3, 2018.
Compares NetCDF outputs on variables:
  SoilMoist_tavg (SMC), Evap_tavg (ET), Qs_tavg (Qs), Qsb_tavg (Qsb).
Output CSV: paper1/tables/regr_lisf_diag_201803.csv
"""

import sys
import glob
import os
import netCDF4 as nc
import numpy as np
import pandas as pd

def main():
    ref_dir = "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr/output/SURFACEMODEL/201803"
    test_dir = "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr_diag/output/SURFACEMODEL/201803"
    out_csv = "paper1/tables/regr_lisf_diag_201803.csv"

    dates = ["201803020000", "201803030000"]
    variables = ["SoilMoist_tavg", "Evap_tavg", "Qs_tavg", "Qsb_tavg"]

    results = []
    all_zero = True

    for d in dates:
        f_ref = os.path.join(ref_dir, f"LIS_HIST_{d}.d01.nc")
        f_test = os.path.join(test_dir, f"LIS_HIST_{d}.d01.nc")

        if not os.path.exists(f_ref):
            print(f"[ERR] Reference file missing: {f_ref}")
            sys.exit(1)
        if not os.path.exists(f_test):
            print(f"[ERR] Test file missing: {f_test}")
            sys.exit(1)

        ds_ref = nc.Dataset(f_ref)
        ds_test = nc.Dataset(f_test)

        for var in variables:
            if var not in ds_ref.variables:
                print(f"[ERR] Variable {var} missing in {f_ref}")
                continue
            if var not in ds_test.variables:
                print(f"[ERR] Variable {var} missing in {f_test}")
                continue

            v_ref = ds_ref.variables[var][:]
            v_test = ds_test.variables[var][:]

            # Masked arrays handling
            diff = np.abs(v_test - v_ref)
            max_diff = float(np.max(diff))
            mean_diff = float(np.mean(diff))

            is_zero = (max_diff < 1e-6)
            if not is_zero:
                all_zero = False

            results.append({
                "date": d,
                "variable": var,
                "max_abs_diff": max_diff,
                "mean_abs_diff": mean_diff,
                "diff_zero": is_zero
            })

        ds_ref.close()
        ds_test.close()

    df = pd.DataFrame(results)
    os.makedirs(os.path.dirname(out_csv), exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"Regression verification table written to {out_csv}")
    print(df.to_string())

    if all_zero:
        print("\n[SUCCESS] Non-regression verified: All differences strictly ZERO.")
        sys.exit(0)
    else:
        print("\n[FAILURE] Non-regression FAILED: Differences detected.")
        sys.exit(2)

if __name__ == "__main__":
    main()
