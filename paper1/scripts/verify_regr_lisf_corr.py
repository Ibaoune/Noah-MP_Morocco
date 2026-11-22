#!/usr/bin/env python3
import sys, os, csv
import netCDF4 as nc
import numpy as np

PROD_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/201801"
TEST_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/regr_lisf_corr_201801/output/SURFACEMODEL/201801"
CSV_OUT = "paper1/tables/regr_lisf_corr_201801.csv"

days = ["LIS_HIST_201801020000.d01.nc", "LIS_HIST_201801030000.d01.nc"]
rows = []
all_ok = True

print("=== VÉRIFICATION DE NON-RÉGRESSION (DA_nocdf_nowilt_2018 vs lisf_corr Ryu=1) ===")

for day_f in days:
    f_prod = os.path.join(PROD_DIR, day_f)
    f_test = os.path.join(TEST_DIR, day_f)
    
    if not os.path.exists(f_test):
        print(f"[ERREUR] Fichier de test manquant : {f_test}")
        sys.exit(1)
    if not os.path.exists(f_prod):
        print(f"[ERREUR] Fichier de reference manquant : {f_prod}")
        sys.exit(1)
        
    with nc.Dataset(f_prod) as ds_p, nc.Dataset(f_test) as ds_t:
        for varname in ['SoilMoist_tavg', 'Evap_tavg', 'Qs_tavg', 'Qsb_tavg']:
            if varname in ds_p.variables and varname in ds_t.variables:
                v_p = ds_p.variables[varname][:]
                v_t = ds_t.variables[varname][:]
                diff = np.abs(v_p - v_t)
                max_diff = float(np.max(diff))
                mean_diff = float(np.mean(diff))
                passed = max_diff < 1e-6
                status = "PASS" if passed else "FAIL"
                print(f"[{status}] {day_f} - {varname:15s}: max abs diff = {max_diff:.6e}, mean diff = {mean_diff:.6e}")
                if not passed:
                    all_ok = False
                rows.append({
                    "day_file": day_f,
                    "variable": varname,
                    "max_abs_diff": max_diff,
                    "mean_diff": mean_diff,
                    "status": status
                })

os.makedirs("paper1/tables", exist_ok=True)
with open(CSV_OUT, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["day_file", "variable", "max_abs_diff", "mean_diff", "status"])
    writer.writeheader()
    writer.writerows(rows)

print(f"Saved {CSV_OUT}")

if all_ok:
    print("\n>>> SUCCÈS : Non-régression VALIDÉE (écart = 0 sur SMC, ET, Qs, Qsb). <<<")
else:
    print("\n>>> ÉCHEC : Non-régression NON VALIDÉE ! <<<")
    sys.exit(1)
