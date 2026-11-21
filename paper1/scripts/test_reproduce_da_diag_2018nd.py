#!/usr/bin/env python3
"""
test_reproduce_da_diag_2018nd.py -- Bloc A4 (paper1, lot 1).

Vérifie que le run DA_nocdf_diag_2018ND reproduit strictement la production
DA_nocdf_noirr_2016_2020 sur le jour test (2018-11-01, fichier LIS_HIST_201811020000.d01.nc).
Critère requis : écart d'humidité du sol (SMC) et des flux < 1e-6.

Sortie :
  paper1/tables/test_reproduce_da_diag_2018nd.csv
"""
import os
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
F_PROD = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-11/SURFACEMODEL/201811/LIS_HIST_201811020000.d01.nc")
F_DIAG = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/output/SURFACEMODEL/201811/LIS_HIST_201811020000.d01.nc")
TABLE_DIR = os.path.join(BASE_DIR, "paper1/tables")


def main():
    os.makedirs(TABLE_DIR, exist_ok=True)
    vars_to_check = ['SoilMoist_tavg', 'Evap_tavg', 'Qs_tavg', 'Qsb_tavg', 'TotalPrecip_tavg']

    rows = []
    with nc.Dataset(F_PROD) as ds_p, nc.Dataset(F_DIAG) as ds_d:
        for v in vars_to_check:
            vp = ds_p.variables[v][:]
            vd = ds_d.variables[v][:]
            max_diff = float(np.max(np.abs(vp - vd)))
            mean_diff = float(np.mean(np.abs(vp - vd)))
            passed = max_diff < 1e-6
            rows.append({
                "variable": v,
                "test_date": "2018-11-01",
                "max_abs_diff": max_diff,
                "mean_abs_diff": mean_diff,
                "threshold": 1e-6,
                "status": "PASSED" if passed else "FAILED"
            })

    df = pd.DataFrame(rows)
    out_csv = os.path.join(TABLE_DIR, "test_reproduce_da_diag_2018nd.csv")
    df.to_csv(out_csv, index=False)
    print(f"[OK] Table de reproduction sauvegardée : {out_csv}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
