#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step10_update_mechanism_budget_da.py

Met à jour march2018_mechanism_budget_da.csv avec les vraies valeurs mesurées de R
pour chaque expérience sur le Domaine et les deux bassins versants amont.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
CSV_PATH = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da.csv")

# Valeurs réelles de R mesurées (P - ET - Q - Delta S) pour Mars 2018 :
true_R = {
    ("ENS_STATE_201803", "Domain"): -8.26,
    ("ENS_STATE_201803", "Lalla_Chafia"): -12.56,
    ("ENS_STATE_201803", "Sidi_Jabeur"): -13.88,

    ("ENS_STATE_201803_noRyu", "Domain"): -22.94,
    ("ENS_STATE_201803_noRyu", "Lalla_Chafia"): -8.67,
    ("ENS_STATE_201803_noRyu", "Sidi_Jabeur"): -12.14,

    ("ENS_FORC_201803", "Domain"): -1.98,
    ("ENS_FORC_201803", "Lalla_Chafia"): -4.43,
    ("ENS_FORC_201803", "Sidi_Jabeur"): -4.87,

    ("ENS_FORC_201803_noRyu", "Domain"): 0.93,
    ("ENS_FORC_201803_noRyu", "Lalla_Chafia"): 2.81,
    ("ENS_FORC_201803_noRyu", "Sidi_Jabeur"): 0.70,

    ("DA_nocdf_201803_diag", "Domain"): 15.67, # avec incrément : R_raw = -8.93, mais -R_raw = 8.93 vs w_sum (sans incr = -16.03 + 24.60 = 8.57) => gap = 0.36 mm
    ("DA_nocdf_201803_diag", "Lalla_Chafia"): -48.80,
    ("DA_nocdf_201803_diag", "Sidi_Jabeur"): -45.89,

    ("DA_cdf_201803_diag", "Domain"): -3.52,
    ("DA_cdf_201803_diag", "Lalla_Chafia"): -21.91,
    ("DA_cdf_201803_diag", "Sidi_Jabeur"): -32.28,
}

df = pd.read_csv(CSV_PATH)

for idx, row in df.iterrows():
    key = (row["run"], row["region"])
    if key in true_R:
        r_val = true_R[key]
        minus_r = -r_val
        w_sum = row["w_sum_mm"]
        gap = minus_r - w_sum
        df.at[idx, "R_mm"] = round(r_val, 2)
        df.at[idx, "minus_R_mm"] = round(minus_r, 2)
        df.at[idx, "gap_minusR_minus_sum_mm"] = round(gap, 4)

df.to_csv(CSV_PATH, index=False)
print(f"[OK] Sauvegardé {CSV_PATH}")
print(df[["run", "region", "minus_R_mm", "w_sum_mm", "gap_minusR_minus_sum_mm"]])
