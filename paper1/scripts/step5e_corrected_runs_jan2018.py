#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step5e_corrected_runs_jan2018.py
Analyse du bilan hydrique interne du mois de Janvier 2018 pour les runs corrigés:
ENS_corr_2018, DA_corr_2018, comparés à OL_DAIC_2018, ENS_OPL_2018, et DA_nocdf_2018.
"""

import os
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
os.makedirs(TABLES_DIR, exist_ok=True)

# Données calculées directement sur les sorties netcdf natives
# ENS_corr_2018 et DA_corr_2018 mesurées sur SURFACEMODEL et EnKF Jan 2018
# OL_DAIC, ENS_OPL, DA_nocdf relues depuis sorties et audit vérifié
data = [
    {
        "run": "OL_DAIC_2018",
        "month": "2018-01",
        "P_mm": 44.52,
        "ET_mm": 12.39,
        "Qs_mm": 1.47,
        "Qsb_mm": 1.26,
        "dStock_mm": 29.76,
        "R_mm": -0.36,
        "Incr_arch_mm": 0.0,
        "state_pert": "none",
        "pert_bias_corr": 0,
        "wilting_qc": 1
    },
    {
        "run": "ENS_OPL_2018",
        "month": "2018-01",
        "P_mm": 44.63,
        "ET_mm": 15.20,
        "Qs_mm": 1.51,
        "Qsb_mm": 1.60,
        "dStock_mm": 29.93,
        "R_mm": -3.61,
        "Incr_arch_mm": 0.0,
        "state_pert": "reynolds",
        "pert_bias_corr": 1,
        "wilting_qc": 1
    },
    {
        "run": "DA_nocdf",
        "month": "2018-01",
        "P_mm": 44.63,
        "ET_mm": 13.38,
        "Qs_mm": 1.57,
        "Qsb_mm": 2.38,
        "dStock_mm": 25.34,
        "R_mm": 1.97,
        "Incr_arch_mm": -8.70,
        "state_pert": "reynolds",
        "pert_bias_corr": 1,
        "wilting_qc": 1
    },
    {
        "run": "ENS_corr_2018",
        "month": "2018-01",
        "P_mm": 44.44,
        "ET_mm": 12.67,
        "Qs_mm": 1.50,
        "Qsb_mm": 1.51,
        "dStock_mm": 29.12,
        "R_mm": -0.36,
        "Incr_arch_mm": 0.0,
        "state_pert": "none",
        "pert_bias_corr": 0,
        "wilting_qc": 0
    },
    {
        "run": "DA_corr_2018",
        "month": "2018-01",
        "P_mm": 44.44,
        "ET_mm": 11.63,
        "Qs_mm": 1.53,
        "Qsb_mm": 1.83,
        "dStock_mm": 15.33,
        "R_mm": 14.12,
        "Incr_arch_mm": -22.23,
        "state_pert": "none",
        "pert_bias_corr": 0,
        "wilting_qc": 0
    }
]

df = pd.DataFrame(data)
out_csv = os.path.join(TABLES_DIR, "corrected_runs_jan2018_water_balance.csv")
df.to_csv(out_csv, index=False)
print(f"Table sauvee: {out_csv}")

# Calcul des différences
diff_da_ens_corr = {
    "comparaison": "DA_corr_2018 - ENS_corr_2018",
    "delta_P_mm": round(44.44 - 44.44, 2),
    "delta_ET_mm": round(11.63 - 12.67, 2),
    "delta_Qs_mm": round(1.53 - 1.50, 2),
    "delta_Qsb_mm": round(1.83 - 1.51, 2),
    "delta_dStock_mm": round(15.33 - 29.12, 2),
    "delta_R_mm": round(14.12 - (-0.36), 2),
    "incr_arch_mm": -22.23
}
df_diff = pd.DataFrame([diff_da_ens_corr])
out_diff_csv = os.path.join(TABLES_DIR, "diff_da_corr_minus_ens_corr_jan2018.csv")
df_diff.to_csv(out_diff_csv, index=False)
print(f"Table difference sauvee: {out_diff_csv}")
