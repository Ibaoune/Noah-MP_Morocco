#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_identity_simgm_vs_opl.py
Test d'identité SIMGM nouveau vs OPL historique sur 2018 (jour par jour).
Compare Qs_tavg et Qsb_tavg reprojetés (grille HyMAP 180x120).
"""

import os
import glob
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

REPO = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
NEW_DIR = f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R1_SIMGM/SURFACEMODEL"
HIST_DIR = f"{REPO}/experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"

# Lalla Chafia coordinates on 180x120 grid
ROW_LC, COL_LC = 75, 71

start_date = datetime.date(2018, 1, 1)
end_date = datetime.date(2018, 12, 31)

records = []

max_diff_qs = 0.0
max_diff_qsb = 0.0

sum_new_qs_domain = 0.0
sum_hist_qs_domain = 0.0
sum_new_qsb_domain = 0.0
sum_hist_qsb_domain = 0.0

daily_new_qs_domain = []
daily_hist_qs_domain = []
daily_new_qsb_domain = []
daily_hist_qsb_domain = []

daily_new_qs_lc = []
daily_hist_qs_lc = []
daily_new_qsb_lc = []
daily_hist_qsb_lc = []

cur = start_date
missing_days = 0

while cur <= end_date:
    ym = cur.strftime("%Y%m")
    ymd = cur.strftime("%Y%m%d")
    fname = f"LIS_HIST_{ymd}0000.d01.nc"
    
    f_new = os.path.join(NEW_DIR, ym, fname)
    f_hist = os.path.join(HIST_DIR, ym, fname)
    
    if not os.path.exists(f_new) or not os.path.exists(f_hist):
        print(f"Missing file for {ymd}: new={os.path.exists(f_new)}, hist={os.path.exists(f_hist)}")
        missing_days += 1
        cur += datetime.timedelta(days=1)
        continue
        
    ds_new = nc.Dataset(f_new, "r")
    ds_hist = nc.Dataset(f_hist, "r")
    
    qs_new = ds_new["Qs_tavg"][:].squeeze()
    qsb_new = ds_new["Qsb_tavg"][:].squeeze()
    
    qs_hist = ds_hist["Qs_tavg"][:].squeeze()
    qsb_hist = ds_hist["Qsb_tavg"][:].squeeze()
    
    ds_new.close()
    ds_hist.close()
    
    # Differences
    diff_qs = np.abs(qs_new - qs_hist)
    diff_qsb = np.abs(qsb_new - qsb_hist)
    
    dmax_qs = float(np.max(diff_qs))
    dmax_qsb = float(np.max(diff_qsb))
    
    if dmax_qs > max_diff_qs: max_diff_qs = dmax_qs
    if dmax_qsb > max_diff_qsb: max_diff_qsb = dmax_qsb
    
    s_new_qs = float(np.sum(qs_new))
    s_hist_qs = float(np.sum(qs_hist))
    s_new_qsb = float(np.sum(qsb_new))
    s_hist_qsb = float(np.sum(qsb_hist))
    
    sum_new_qs_domain += s_new_qs
    sum_hist_qs_domain += s_hist_qs
    sum_new_qsb_domain += s_new_qsb
    sum_hist_qsb_domain += s_hist_qsb
    
    daily_new_qs_domain.append(s_new_qs)
    daily_hist_qs_domain.append(s_hist_qs)
    daily_new_qsb_domain.append(s_new_qsb)
    daily_hist_qsb_domain.append(s_hist_qsb)
    
    val_new_qs_lc = float(qs_new[ROW_LC, COL_LC])
    val_hist_qs_lc = float(qs_hist[ROW_LC, COL_LC])
    val_new_qsb_lc = float(qsb_new[ROW_LC, COL_LC])
    val_hist_qsb_lc = float(qsb_hist[ROW_LC, COL_LC])
    
    daily_new_qs_lc.append(val_new_qs_lc)
    daily_hist_qs_lc.append(val_hist_qs_lc)
    daily_new_qsb_lc.append(val_new_qsb_lc)
    daily_hist_qsb_lc.append(val_hist_qsb_lc)
    
    records.append({
        "date": cur.strftime("%Y-%m-%d"),
        "dmax_qs": dmax_qs,
        "dmax_qsb": dmax_qsb,
        "new_qs_sum": s_new_qs,
        "hist_qs_sum": s_hist_qs,
        "new_qsb_sum": s_new_qsb,
        "hist_qsb_sum": s_hist_qsb,
        "new_qs_lc": val_new_qs_lc,
        "hist_qs_lc": val_hist_qs_lc,
        "new_qsb_lc": val_new_qsb_lc,
        "hist_qsb_lc": val_hist_qsb_lc,
    })
    
    cur += datetime.timedelta(days=1)

df = pd.DataFrame(records)
out_csv = f"{REPO}/experiments/NorthMor/sensitivity_runoff_2018/_inventory/test_identity_daily_2018.csv"
df.to_csv(out_csv, index=False)
print(f"Saved daily comparison to {out_csv}")

# Correlations
def corr(x, y):
    std_x = np.std(x)
    std_y = np.std(y)
    if std_x == 0 or std_y == 0:
        return 1.0 if np.allclose(x, y) else 0.0
    return float(np.corrcoef(x, y)[0, 1])

corr_qs_domain = corr(daily_new_qs_domain, daily_hist_qs_domain)
corr_qsb_domain = corr(daily_new_qsb_domain, daily_hist_qsb_domain)
corr_qtot_domain = corr(np.array(daily_new_qs_domain) + np.array(daily_new_qsb_domain),
                        np.array(daily_hist_qs_domain) + np.array(daily_hist_qsb_domain))

corr_qs_lc = corr(daily_new_qs_lc, daily_hist_qs_lc)
corr_qsb_lc = corr(daily_new_qsb_lc, daily_hist_qsb_lc)
corr_qtot_lc = corr(np.array(daily_new_qs_lc) + np.array(daily_new_qsb_lc),
                     np.array(daily_hist_qs_lc) + np.array(daily_hist_qsb_lc))

ratio_qs_domain = sum_new_qs_domain / sum_hist_qs_domain if sum_hist_qs_domain > 0 else np.nan
ratio_qsb_domain = sum_new_qsb_domain / sum_hist_qsb_domain if sum_hist_qsb_domain > 0 else np.nan
ratio_qtot_domain = (sum_new_qs_domain + sum_new_qsb_domain) / (sum_hist_qs_domain + sum_hist_qsb_domain) if (sum_hist_qs_domain + sum_hist_qsb_domain) > 0 else np.nan

# Conclusion determination
rel_diff_qs = abs(sum_new_qs_domain - sum_hist_qs_domain) / sum_hist_qs_domain
rel_diff_qsb = abs(sum_new_qsb_domain - sum_hist_qsb_domain) / sum_hist_qsb_domain

if max_diff_qs == 0.0 and max_diff_qsb == 0.0:
    conclusion = "identiques"
elif rel_diff_qs < 0.01 and rel_diff_qsb < 0.01 and corr_qs_domain > 0.999 and corr_qsb_domain > 0.999:
    conclusion = "quasi identiques (<1 %)"
else:
    conclusion = "différents"

summary_data = {
    "Variable": ["Qs_tavg (surface)", "Qsb_tavg (subsurface)", "Total (Qs + Qsb)"],
    "Max_|diff|": [max_diff_qs, max_diff_qsb, max(max_diff_qs, max_diff_qsb)],
    "Ratio_Sommes_Annuelles_Domaine": [ratio_qs_domain, ratio_qsb_domain, ratio_qtot_domain],
    "Correlation_Journaliere_Domaine": [corr_qs_domain, corr_qsb_domain, corr_qtot_domain],
    "Correlation_Journaliere_Lalla_Chafia": [corr_qs_lc, corr_qsb_lc, corr_qtot_lc],
    "Conclusion": [conclusion, conclusion, conclusion]
}

df_summary = pd.DataFrame(summary_data)
summary_csv = f"{REPO}/experiments/NorthMor/sensitivity_runoff_2018/_inventory/test_identity_summary.csv"
df_summary.to_csv(summary_csv, index=False)
print("\n=== SUMMARY RESULTS ===")
print(df_summary.to_string(index=False))
print(f"\nConclusion finale: {conclusion}")
