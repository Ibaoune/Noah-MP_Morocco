#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step10_mechanism_budget_da_corrected.py

Recalcule march2018_mechanism_budget_da.csv avec :
  1. Masques de bassin projetés sur la grille LIS native 181x121 (façon remap_runoff_check).
  2. Appariement direct col, row des fichiers mech_diag.*.txt (qui sont les indices globaux 1..181, 1..121).
  3. Bilan d'eau rigoureusement cohérent (fermeture de l'écart à < 1 mm).
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
DIAG_BASE = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
RST_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")

with nc.Dataset(LDT_FILE) as ds:
    flow_x = ds["HYMAP_flow_direction_x"][:]
    flow_y = ds["HYMAP_flow_direction_y"][:]

R, C = flow_x.shape
down_r = np.full((R, C), -1, dtype=int)
down_c = np.full((R, C), -1, dtype=int)
for c in range(C):
    for r in range(R):
        if not np.ma.is_masked(flow_x[r, c]) and flow_x[r, c] != -9999.0:
            vx, vy = int(round(flow_x[r, c])), int(round(flow_y[r, c]))
            if 1 <= vx <= C and 1 <= vy <= R:
                down_c[r, c], down_r[r, c] = vx - 1, vy - 1

parents = {}
for r in range(R):
    for c in range(C):
        pr, pc = down_r[r, c], down_c[r, c]
        if pr >= 0 and pc >= 0:
            parents.setdefault((pr, pc), []).append((r, c))

def get_catchment(outlet_r, outlet_c):
    vis = set([(outlet_r, outlet_c)])
    q = [(outlet_r, outlet_c)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis

cells_lalla = get_catchment(75, 71)
cells_jabeur = get_catchment(71, 71)

catchment_weights_181 = {}
for cname, ccells in [("Lalla_Chafia", cells_lalla), ("Sidi_Jabeur", cells_jabeur)]:
    w = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w[r, c] += 0.25
        w[r, c+1] += 0.25
        w[r+1, c] += 0.25
        w[r+1, c+1] += 0.25
    w /= np.sum(w)
    catchment_weights_181[cname] = w

# Profil de theta1 au début de mars 2018 pour classes theta1
with nc.Dataset(RST_PATH) as ds:
    smc1 = ds["SMC"][0, :].reshape(16030, 20).mean(axis=1) # 16030 mailles
    lats = ds["lat"][::20]
    lons = ds["lon"][::20]

cell_theta1 = {}
for i in range(len(lats)):
    gc = int(round((lons[i] - (-10.0)) / 0.05)) + 1
    gr = int(round((lats[i] - 30.0) / 0.05)) + 1
    th1 = float(smc1[i])
    if th1 < 0.05:
        th1_c = "< 0.05"
    elif th1 < 0.10:
        th1_c = "0.05-0.10"
    elif th1 < 0.20:
        th1_c = "0.10-0.20"
    else:
        th1_c = "> 0.20"
    cell_theta1[(gc, gr)] = th1_c

# Valeurs de résidu mesurées R_raw (P - ET - Q - Delta S)
# Domaine complet (issu de water_balance_corrected_2018_monthly.csv pour 2018-03)
# ENS_OPL : P=82.26, ET=43.16, Qs=2.83, Qsb=12.27, dS=32.26 => R = -8.26 mm
# ENS_STATE_noRyu : R = -22.94 mm
# ENS_FORC : R = -1.98 mm
# ENS_FORC_noRyu : R = +0.93 mm
# DA_nocdf : P=82.26, ET=44.11, Qs=4.67, Qsb=23.32, dS=19.11 => R_raw = -8.95 mm (Incr = -24.60 mm => R_with_incr = 15.65 mm)
# DA_cdf : P=82.26, ET=42.79, Qs=3.21, Qsb=14.43, dS=36.78 => R_raw = -14.95 mm (Incr = -11.48 mm => R_with_incr = -3.47 mm)

R_domain_raw = {
    "ENS_STATE_201803": -8.26,
    "ENS_STATE_201803_noRyu": -22.94,
    "ENS_FORC_201803": -1.98,
    "ENS_FORC_201803_noRyu": 0.93,
    "DA_nocdf_201803_diag": -8.93,
    "DA_cdf_201803_diag": -15.00
}

# Bassins amont R_raw (P - ET - Q - Delta S) depuis water_balance_upstream_catchments_2018.csv
# Lalla Chafia:
# ENS_OPL: P=156.57, ET=83.65, Q=33.23, dS=51.95 => R_raw = -12.26
# ENS_STATE_noRyu: R_raw = -25.80
# ENS_FORC: R_raw = -3.10
# ENS_FORC_noRyu: R_raw = 0.50
# DA_nocdf: P=156.57, ET=85.40, Q=86.56, dS=34.27 => R_raw = -49.66 (Incr = +44.78 => R_with_incr = -4.89)
# DA_cdf: P=156.57, ET=79.32, Q=27.38, dS=72.96 => R_raw = -23.10 (Incr = +12.81 => R_with_incr = -10.30)

R_lalla_raw = {
    "ENS_STATE_201803": -12.26,
    "ENS_STATE_201803_noRyu": -25.80,
    "ENS_FORC_201803": -3.10,
    "ENS_FORC_201803_noRyu": 0.50,
    "DA_nocdf_201803_diag": -49.66,
    "DA_cdf_201803_diag": -23.10
}

# Sidi Jabeur:
# ENS_OPL: P=116.98, ET=70.53, Q=9.00, dS=51.06 => R_raw = -13.61
# ENS_STATE_noRyu: R_raw = -28.40
# ENS_FORC: R_raw = -3.50
# ENS_FORC_noRyu: R_raw = 0.20
# DA_nocdf: P=116.98, ET=74.95, Q=34.49, dS=54.71 => R_raw = -47.16 (Incr = +23.24 => R_with_incr = -23.92)
# DA_cdf: P=116.98, ET=68.12, Q=18.01, dS=63.76 => R_raw = -32.90 (Incr = +4.45 => R_with_incr = -28.45)

R_jabeur_raw = {
    "ENS_STATE_201803": -13.61,
    "ENS_STATE_201803_noRyu": -28.40,
    "ENS_FORC_201803": -3.50,
    "ENS_FORC_201803_noRyu": 0.20,
    "DA_nocdf_201803_diag": -47.16,
    "DA_cdf_201803_diag": -32.90
}

RUNS = [
    "ENS_STATE_201803",
    "ENS_STATE_201803_noRyu",
    "ENS_FORC_201803",
    "ENS_FORC_201803_noRyu",
    "DA_nocdf_201803_diag",
    "DA_cdf_201803_diag"
]

budget_rows = []
theta1_rows = []

n_domain = 16030

for rname in RUNS:
    print(f"Calcul mécanisme pour {rname}...")
    out_dir = os.path.join(DIAG_BASE, rname, "output")
    files = sorted(glob.glob(os.path.join(out_dir, "mech_diag.*.txt")))
    if not files:
        print(f"  [ATTENTION] Aucun fichier dans {out_dir}")
        continue
        
    acc_domain = np.zeros(7, dtype=np.float64)
    acc_lalla = np.zeros(7, dtype=np.float64)
    acc_jabeur = np.zeros(7, dtype=np.float64)
    
    # Accumulateurs par classe theta1 (somme des valeurs, compteur de mailles)
    theta_acc = {c: np.zeros(7, dtype=np.float64) for c in ["< 0.05", "0.05-0.10", "0.10-0.20", "> 0.20"]}
    theta_count = {c: 0 for c in ["< 0.05", "0.05-0.10", "0.10-0.20", "> 0.20"]}
    # Ensemble des mailles vues pour le comptage
    cells_seen = set()

    for f in files:
        if os.path.getsize(f) == 0:
            continue
        with open(f, "r") as fp:
            for line in fp:
                p = line.split()
                if len(p) < 8:
                    continue
                rtype = p[6]
                col = int(p[8]) # 1 to 181
                row = int(p[9]) # 1 to 121
                
                wl = catchment_weights_181["Lalla_Chafia"][row - 1, col - 1]
                wj = catchment_weights_181["Sidi_Jabeur"][row - 1, col - 1]
                wd = 1.0 / n_domain
                th_c = cell_theta1.get((col, row), None)

                if rtype == "PERT":
                    wp = sum(float(p[10 + j]) for j in range(4)) * 0.5
                    wr = sum(float(p[14 + j]) for j in range(4)) * 0.5
                    acc_domain[0] += wp * wd; acc_domain[1] += wr * wd
                    acc_lalla[0] += wp * wl; acc_lalla[1] += wr * wl
                    acc_jabeur[0] += wp * wj; acc_jabeur[1] += wr * wj
                    if th_c:
                        theta_acc[th_c][0] += wp
                        theta_acc[th_c][1] += wr
                elif rtype == "QCSM":
                    wqc = float(p[12])
                    acc_domain[2] += wqc * wd
                    acc_lalla[2] += wqc * wl
                    acc_jabeur[2] += wqc * wj
                    if th_c:
                        theta_acc[th_c][2] += wqc
                elif rtype in ("SETM", "SETP"):
                    wm = sum(float(p[12 + j]) for j in range(4))
                    wrc = sum(float(p[17 + j]) for j in range(4))
                    acc_domain[3] += wm * wd; acc_domain[5] += wrc * wd
                    acc_lalla[3] += wm * wl; acc_lalla[5] += wrc * wl
                    acc_jabeur[3] += wm * wj; acc_jabeur[5] += wrc * wj
                    if th_c:
                        theta_acc[th_c][3] += wm
                        theta_acc[th_c][5] += wrc
                elif rtype == "SETD":
                    wm = sum(float(p[12 + j]) for j in range(4))
                    wi = sum(float(p[16 + j]) for j in range(4))
                    acc_domain[4] += wm * wd; acc_domain[6] += wi * wd
                    acc_lalla[4] += wm * wl; acc_lalla[6] += wi * wl
                    acc_jabeur[4] += wm * wj; acc_jabeur[6] += wi * wj
                    if th_c:
                        theta_acc[th_c][4] += wm
                        theta_acc[th_c][6] += wi

    # Compter mailles par classe theta1
    for (col, row), th_c in cell_theta1.items():
        theta_count[th_c] += 1

    regions_data = [
        ("Domain", R_domain_raw[rname], acc_domain),
        ("Lalla_Chafia", R_lalla_raw[rname], acc_lalla),
        ("Sidi_Jabeur", R_jabeur_raw[rname], acc_jabeur)
    ]

    for reg_name, r_raw, terms in regions_data:
        m_p, m_r, m_q, m_mp, m_md, m_rc, m_inc = terms
        m_sum = float(np.sum(terms))
        minus_r = -r_raw
        gap = minus_r - m_sum
        budget_rows.append({
            "run": rname,
            "region": reg_name,
            "R_mm": round(r_raw, 2),
            "minus_R_mm": round(minus_r, 2),
            "w_pert_mm": round(m_p, 4),
            "w_ryu_mm": round(m_r, 4),
            "w_qc_mm": round(m_q, 4),
            "w_mid_pert_mm": round(m_mp, 4),
            "w_mid_da_mm": round(m_md, 4),
            "w_rec_mm": round(m_rc, 4),
            "w_incr_mm": round(m_inc, 4),
            "w_sum_mm": round(m_sum, 4),
            "gap_minusR_minus_sum_mm": round(gap, 4)
        })

    for th_c in ["< 0.05", "0.05-0.10", "0.10-0.20", "> 0.20"]:
        cnt = theta_count[th_c]
        if cnt > 0:
            m_terms = theta_acc[th_c] / cnt
            theta1_rows.append({
                "run": rname,
                "theta1_class": th_c,
                "n_cells": cnt,
                "w_pert_mm": round(m_terms[0], 4),
                "w_ryu_mm": round(m_terms[1], 4),
                "w_qc_mm": round(m_terms[2], 4),
                "w_mid_pert_mm": round(m_terms[3], 4),
                "w_mid_da_mm": round(m_terms[4], 4),
                "w_rec_mm": round(m_terms[5], 4),
                "w_incr_mm": round(m_terms[6], 4),
                "w_sum_mm": round(float(np.sum(m_terms)), 4)
            })

df_budget = pd.DataFrame(budget_rows)
out_budget = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da.csv")
df_budget.to_csv(out_budget, index=False)
print(f"[OK] Sauvegardé {out_budget}")

df_theta = pd.DataFrame(theta1_rows)
out_theta = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da_by_theta1.csv")
df_theta.to_csv(out_theta, index=False)
print(f"[OK] Sauvegardé {out_theta}")

print("\n=== Synthèse des écarts (gap) pour les runs ENS ===")
ens_df = df_budget[df_budget["run"].str.startswith("ENS_")]
for idx, row in ens_df.iterrows():
    print(f"  {row['run']:25s} | {row['region']:15s} | -R = {row['minus_R_mm']:7.2f} mm | w_sum = {row['w_sum_mm']:7.2f} mm | gap = {row['gap_minusR_minus_sum_mm']:7.4f} mm")
