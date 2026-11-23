#!/usr/bin/env python3
"""
verify_regr_lisf_diag_da.py
Vérification de la non-régression de src/lisf_diag contre la production DA_nocdf
sur les 2 jours du 01 au 03 mars 2018.
Sortie CSV : paper1/tables/regr_lisf_diag_da_201803.csv
"""

import os
import glob
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TEST_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/regr_lisf_diag_da_201803/output/SURFACEMODEL/201803")
PROD_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-03/SURFACEMODEL/201803")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

def main():
    print("=== VÉRIFICATION DE LA NON-RÉGRESSION DA_NOCDF (2 JOURS) ===")
    
    test_files = sorted(glob.glob(os.path.join(TEST_DIR, "LIS_HIST_*.nc")))
    if not test_files:
        print(f"[ERREUR] Aucun fichier trouvé dans {TEST_DIR}")
        return False

    records = []
    all_zero = True

    variables = ["SoilMoist_tavg", "Evap_tavg", "Qs_tavg", "Qsb_tavg"]

    for tf in test_files:
        fname = os.path.basename(tf)
        date_str = fname.replace("LIS_HIST_", "").replace(".d01.nc", "")
        pf = os.path.join(PROD_DIR, fname)
        if not os.path.exists(pf):
            print(f"[ERREUR] Fichier de production correspondant introuvable : {pf}")
            all_zero = False
            continue

        with nc.Dataset(tf) as ds_t, nc.Dataset(pf) as ds_p:
            for var in variables:
                vt = ds_t.variables[var][:]
                vp = ds_p.variables[var][:]

                # Mask out NaNs and fill values (-9999.0)
                mask = ~np.isnan(vt) & ~np.isnan(vp) & (vt != -9999.0) & (vp != -9999.0)
                diff = np.abs(vt[mask] - vp[mask])

                max_diff = float(np.max(diff)) if len(diff) > 0 else np.nan
                mean_diff = float(np.mean(diff)) if len(diff) > 0 else np.nan
                is_zero = bool(max_diff == 0.0)

                if not is_zero:
                    all_zero = False

                records.append({
                    "date": date_str,
                    "variable": var,
                    "max_abs_diff": max_diff,
                    "mean_abs_diff": mean_diff,
                    "diff_zero": is_zero
                })

    df = pd.DataFrame(records)
    out_csv = os.path.join(TABLES_DIR, "regr_lisf_diag_da_201803.csv")
    df.to_csv(out_csv, index=False)
    print(f"\n[OK] Résultats sauvegardés dans : {out_csv}")
    print(df)

    if all_zero and len(df) == 8:
        print("\n>>> CONCLUSION : NON-RÉGRESSION 100% VALIDÉE (Écart = 0.000000e+00).")
        return True
    else:
        print("\n>>> ATTENTION : Non-régression non validée ou incomplète !")
        return False

if __name__ == "__main__":
    main()
