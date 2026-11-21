#!/usr/bin/env python3
"""
b2_verify_regression.py

Vérification de non-régression entre le run avec binaire patché (Ryu=1)
et le run de production ENS_STATE_201803 sur au moins 2 jours (March 1 & March 2, 2018).
Critère strict : max abs diff < 1e-6 sur SMC (SoilMoist_tavg) et ET (Evap_tavg).
"""

import sys
import os
import netCDF4 as nc
import numpy as np

PROD_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803/output/SURFACEMODEL/201803"
TEST_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr/output/SURFACEMODEL/201803"

days = ["LIS_HIST_201803020000.d01.nc", "LIS_HIST_201803030000.d01.nc"]
all_ok = True

print("=== VÉRIFICATION DE NON-RÉGRESSION (ENS_STATE_201803 Ryu=1 vs Production) ===")

for day_f in days:
    f_prod = os.path.join(PROD_DIR, day_f)
    f_test = os.path.join(TEST_DIR, day_f)
    
    if not os.path.exists(f_test):
        print(f"[ERREUR] Fichier de test manquant : {f_test}")
        sys.exit(1)
    if not os.path.exists(f_prod):
        print(f"[ERREUR] Fichier de production manquant : {f_prod}")
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

if all_ok:
    print("\n>>> SUCCÈS : Non-régression VALIDÉE (écart < 1e-6 sur toutes les variables et tous les jours). <<<")
else:
    print("\n>>> ÉCHEC : Non-régression NON VALIDÉE ! <<<")
    sys.exit(1)
