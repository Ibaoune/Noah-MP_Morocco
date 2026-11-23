#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step10_mechanism_budget_da.py

Calcule le bilan du mécanisme sur les 6 expériences de Mars 2018 :
  1. ENS_STATE_201803
  2. ENS_STATE_201803_noRyu
  3. ENS_FORC_201803
  4. ENS_FORC_201803_noRyu
  5. DA_nocdf_201803_diag
  6. DA_cdf_201803_diag

Termes décomposés (mm) :
  - w_pert : perturbation GMAO
  - w_ryu : correction Ryu
  - w_qc : écrêtage qcsoilm
  - w_mid_pert : midrange pendant perturbation
  - w_mid_da : midrange pendant analyse DA
  - w_rec : recentrage ensemble
  - w_incr : incrément EnKF réellement appliqué
  - w_sum : somme de tous les termes
  - minus_R : -R mesuré du bilan hydrique
  - gap : minus_R - w_sum

Zones évaluées :
  - Domaine complet (16 030 mailles)
  - Bassin amont de Lalla Chafia
  - Bassin amont de Sidi Jabeur
  - Classes de theta1 (<0.05, 0.05-0.10, 0.10-0.20, >0.20)

Sorties CSV :
  - paper1/tables/march2018_mechanism_budget_da.csv
  - paper1/tables/march2018_mechanism_budget_da_by_theta1.csv
"""

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
DIAG_BASE = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech")
RST_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")
INPUT_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")

os.makedirs(TABLES_DIR, exist_ok=True)

# 1. Bornes des 32 rangs MPI
ranks_bounds = {}
for i in range(32):
    f = os.path.join(DIAG_BASE, f"ENS_STATE_201803/logs/lislog_ENS_STATE_201803.{i:04d}")
    with open(f) as fp:
        for l in fp:
            if "local domain   " in l:
                p = l.split()
                ranks_bounds[i] = (float(p[3]), float(p[5]))
                break

# 2. Délimitation des bassins versants amont (Lalla Chafia et Sidi Jabeur)
with nc.Dataset(LDT_FILE) as ds:
    area_180 = ds["HYMAP_grid_area"][:].filled(0.0)
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
    w181 = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w181[r, c] += 0.25 * area_180[r, c]
        w181[r, c+1] += 0.25 * area_180[r, c]
        w181[r+1, c] += 0.25 * area_180[r, c]
        w181[r+1, c+1] += 0.25 * area_180[r, c]
    tot_w = np.sum(w181)
    if tot_w > 0:
        w181 /= tot_w
    catchment_weights_181[cname] = w181

# 3. Attributs des 16 030 mailles
with nc.Dataset(RST_PATH) as ds:
    lats = ds.variables["lat"][::20]
    lons = ds.variables["lon"][::20]
    smc1 = ds.variables["SMC"][0, 19::20] # couche 1, membre 20

cell_info = {}
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
    
    w_lc = catchment_weights_181["Lalla_Chafia"][gr - 1, gc - 1]
    w_sj = catchment_weights_181["Sidi_Jabeur"][gr - 1, gc - 1]
    
    cell_info[(gc, gr)] = {
        "theta1_class": th1_c,
        "w_lalla": w_lc,
        "w_jabeur": w_sj
    }

# 4. Valeurs de R mesurées pour Mars 2018
# Domaine complet
R_domain = {
    "ENS_STATE_201803": -8.26,
    "ENS_STATE_201803_noRyu": -22.94,
    "ENS_FORC_201803": -1.98,
    "ENS_FORC_201803_noRyu": 0.93,
    "DA_nocdf_201803_diag": 15.67,
    "DA_cdf_201803_diag": -3.52 # Bilan mensuel DA_cdf Mars 2018
}

# Bassins versants amont (issus de water_balance_upstream_catchments_2018.csv)
R_catchments = {
    "Lalla_Chafia": {
        "ENS_STATE_201803": -12.26,
        "ENS_STATE_201803_noRyu": -25.80,
        "ENS_FORC_201803": -3.10,
        "ENS_FORC_201803_noRyu": 0.50,
        "DA_nocdf_201803_diag": -4.89,
        "DA_cdf_201803_diag": -10.30
    },
    "Sidi_Jabeur": {
        "ENS_STATE_201803": -13.61,
        "ENS_STATE_201803_noRyu": -28.40,
        "ENS_FORC_201803": -3.50,
        "ENS_FORC_201803_noRyu": 0.20,
        "DA_nocdf_201803_diag": -23.92,
        "DA_cdf_201803_diag": -28.45
    }
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

for rname in RUNS:
    print(f"\nTraitement {rname}...")
    out_dir = os.path.join(DIAG_BASE, rname, "output")
    files = sorted(glob.glob(os.path.join(out_dir, "mech_diag.*.txt")))
    if not files:
        print(f"  [ATTENTION] Aucun fichier mech_diag trouvé dans {out_dir}")
        continue
    
    # Accumulateurs : [w_pert, w_ryu, w_qc, w_mid_pert, w_mid_da, w_rec, w_incr]
    acc = {k: np.zeros(7, dtype=np.float64) for k in cell_info.keys()}
    
    for f in files:
        if os.path.getsize(f) == 0:
            continue
        rk = int(os.path.basename(f).split(".")[1])
        minlat, minlon = ranks_bounds[rk]
        
        with open(f, "r") as fp:
            for line in fp:
                p = line.split()
                if len(p) < 8:
                    continue
                rtype = p[6]
                col = int(p[8])
                row = int(p[9])
                lat = minlat + (row - 1) * 0.05
                lon = minlon + (col - 1) * 0.05
                gc = int(round((lon - (-10.0)) / 0.05)) + 1
                gr = int(round((lat - 30.0) / 0.05)) + 1
                
                ckey = (gc, gr)
                if ckey not in acc:
                    continue
                
                if rtype == "PERT":
                    # GMAO perturbation and Ryu
                    wp = sum(float(p[10 + j]) for j in range(4)) * 0.5
                    wr = sum(float(p[14 + j]) for j in range(4)) * 0.5
                    acc[ckey][0] += wp
                    acc[ckey][1] += wr
                elif rtype == "QCSM":
                    wqc = float(p[12])
                    acc[ckey][2] += wqc
                elif rtype in ("SETM", "SETP"):
                    # Midrange during perturbation & recentering
                    wm = sum(float(p[12 + j]) for j in range(4))
                    wrc = sum(float(p[17 + j]) for j in range(4))
                    acc[ckey][3] += wm
                    acc[ckey][5] += wrc
                elif rtype == "SETD":
                    # Midrange during DA analysis & EnKF increment applied
                    wm_da = sum(float(p[12 + j]) for j in range(4))
                    w_inc = sum(float(p[16 + j]) for j in range(4))
                    acc[ckey][4] += wm_da
                    acc[ckey][6] += w_inc

    records = []
    for ckey, vals in acc.items():
        c_meta = cell_info[ckey]
        records.append({
            "gc": ckey[0],
            "gr": ckey[1],
            "theta1_class": c_meta["theta1_class"],
            "w_lalla": c_meta["w_lalla"],
            "w_jabeur": c_meta["w_jabeur"],
            "w_pert": vals[0],
            "w_ryu": vals[1],
            "w_qc": vals[2],
            "w_mid_pert": vals[3],
            "w_mid_da": vals[4],
            "w_rec": vals[5],
            "w_incr": vals[6],
            "w_sum": np.sum(vals)
        })
    df_cells = pd.DataFrame(records)
    
    # 1. Bilan Domaine complet (moyenne arithmétique 16 030 mailles)
    m_p = df_cells["w_pert"].mean()
    m_r = df_cells["w_ryu"].mean()
    m_q = df_cells["w_qc"].mean()
    m_mp = df_cells["w_mid_pert"].mean()
    m_md = df_cells["w_mid_da"].mean()
    m_rc = df_cells["w_rec"].mean()
    m_inc = df_cells["w_incr"].mean()
    m_sum = m_p + m_r + m_q + m_mp + m_md + m_rc + m_inc
    
    r_dom = R_domain.get(rname, np.nan)
    minus_r = -r_dom
    gap = minus_r - m_sum
    
    budget_rows.append({
        "run": rname,
        "region": "Domain",
        "R_mm": round(r_dom, 2),
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
    print(f"  [Domain] -R={minus_r:.2f}, w_sum={m_sum:.4f}, gap={gap:.4f}")

    # 2. Bassins versants amont
    for cname, cweight_col in [("Lalla_Chafia", "w_lalla"), ("Sidi_Jabeur", "w_jabeur")]:
        sub_c = df_cells[df_cells[cweight_col] > 0]
        w_norm = sub_c[cweight_col] / sub_c[cweight_col].sum()
        
        c_p = (sub_c["w_pert"] * w_norm).sum()
        c_r = (sub_c["w_ryu"] * w_norm).sum()
        c_q = (sub_c["w_qc"] * w_norm).sum()
        c_mp = (sub_c["w_mid_pert"] * w_norm).sum()
        c_md = (sub_c["w_mid_da"] * w_norm).sum()
        c_rc = (sub_c["w_rec"] * w_norm).sum()
        c_inc = (sub_c["w_incr"] * w_norm).sum()
        c_sum = c_p + c_r + c_q + c_mp + c_md + c_rc + c_inc
        
        r_cat = R_catchments[cname].get(rname, np.nan)
        minus_r_cat = -r_cat
        gap_cat = minus_r_cat - c_sum
        
        budget_rows.append({
            "run": rname,
            "region": cname,
            "R_mm": round(r_cat, 2),
            "minus_R_mm": round(minus_r_cat, 2),
            "w_pert_mm": round(c_p, 4),
            "w_ryu_mm": round(c_r, 4),
            "w_qc_mm": round(c_q, 4),
            "w_mid_pert_mm": round(c_mp, 4),
            "w_mid_da_mm": round(c_md, 4),
            "w_rec_mm": round(c_rc, 4),
            "w_incr_mm": round(c_inc, 4),
            "w_sum_mm": round(c_sum, 4),
            "gap_minusR_minus_sum_mm": round(gap_cat, 4)
        })
        print(f"  [{cname}] -R={minus_r_cat:.2f}, w_sum={c_sum:.4f}, gap={gap_cat:.4f}")

    # 3. Décomposition par classe de theta1
    all_th1_classes = ["< 0.05", "0.05-0.10", "0.10-0.20", "> 0.20"]
    for cls in all_th1_classes:
        sub = df_cells[df_cells["theta1_class"] == cls]
        cnt = len(sub)
        if cnt > 0:
            theta1_rows.append({
                "run": rname,
                "theta1_class": cls,
                "n_cells": cnt,
                "w_pert_mm": round(sub["w_pert"].mean(), 4),
                "w_ryu_mm": round(sub["w_ryu"].mean(), 4),
                "w_qc_mm": round(sub["w_qc"].mean(), 4),
                "w_mid_pert_mm": round(sub["w_mid_pert"].mean(), 4),
                "w_mid_da_mm": round(sub["w_mid_da"].mean(), 4),
                "w_rec_mm": round(sub["w_rec"].mean(), 4),
                "w_incr_mm": round(sub["w_incr"].mean(), 4),
                "w_sum_mm": round(sub["w_sum"].mean(), 4)
            })
        else:
            theta1_rows.append({
                "run": rname,
                "theta1_class": cls,
                "n_cells": 0,
                "w_pert_mm": 0.0,
                "w_ryu_mm": 0.0,
                "w_qc_mm": 0.0,
                "w_mid_pert_mm": 0.0,
                "w_mid_da_mm": 0.0,
                "w_rec_mm": 0.0,
                "w_incr_mm": 0.0,
                "w_sum_mm": 0.0
            })

df_budget = pd.DataFrame(budget_rows)
df_theta1 = pd.DataFrame(theta1_rows)

out_budget = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da.csv")
out_theta1 = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da_by_theta1.csv")

df_budget.to_csv(out_budget, index=False)
df_theta1.to_csv(out_theta1, index=False)

print("\nSauvegardes terminées :")
print(f"  - {out_budget}")
print(f"  - {out_theta1}")
