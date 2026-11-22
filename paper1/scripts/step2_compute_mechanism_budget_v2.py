#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step2_compute_mechanism_budget_v2.py
Recalcul rigoureux du bilan du mécanisme E6 (mars 2018) sur l'ensemble des 16 030 mailles du domaine.
Génère :
  - paper1/tables/march2018_mechanism_budget.csv
  - paper1/tables/march2018_mechanism_by_theta1_class.csv
  - paper1/tables/march2018_mechanism_by_texture.csv
"""

import os, glob
import numpy as np
import pandas as pd
import netCDF4 as nc

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
DIAG_BASE = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech")
RST_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")
INPUT_NC = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
RYU_CSV = os.path.join(TABLES_DIR, "march2018_ryu_test.csv")

TEXTURE_NAMES = {
    1: "Sand", 2: "Loamy Sand", 3: "Sandy Loam", 4: "Silt Loam", 5: "Silt",
    6: "Loam", 7: "Sandy Clay Loam", 8: "Silty Clay Loam", 9: "Clay Loam",
    10: "Sandy Clay", 11: "Silty Clay", 12: "Clay", 13: "Organic material",
    14: "Water", 15: "Bedrock", 16: "Other"
}

# 1. R relu depuis march2018_ryu_test.csv
df_ryu = pd.read_csv(RYU_CSV).set_index("run")
R_values = {
    "ENS_STATE_201803": float(df_ryu.loc["STATE", "Residu_mm"]),
    "ENS_STATE_201803_noRyu": float(df_ryu.loc["STATE_noRyu", "Residu_mm"]),
    "ENS_FORC_201803": float(df_ryu.loc["FORC", "Residu_mm"]),
    "ENS_FORC_201803_noRyu": float(df_ryu.loc["FORC_noRyu", "Residu_mm"])
}

# 2. Bornes des 32 rangs MPI
ranks_bounds = {}
for i in range(32):
    f = os.path.join(DIAG_BASE, f"ENS_STATE_201803/logs/lislog_ENS_STATE_201803.{i:04d}")
    with open(f) as fp:
        for l in fp:
            if "local domain   " in l:
                p = l.split()
                ranks_bounds[i] = (float(p[3]), float(p[5]))
                break

# 3. Attributs des 16 030 mailles
with nc.Dataset(RST_PATH) as ds:
    lats = ds.variables["lat"][::20]
    lons = ds.variables["lon"][::20]
    smc1 = ds.variables["SMC"][0, 19::20] # couche 1, membre 20

with nc.Dataset(INPUT_NC) as ds:
    tex_3d = ds.variables["TEXTURE"][:]
    dom_tex = np.argmax(tex_3d, axis=0) + 1

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
    
    tid = int(dom_tex[gr - 1, gc - 1])
    tname = TEXTURE_NAMES.get(tid, f"Tex_{tid}")
    
    cell_info[(gc, gr)] = {
        "theta1_class": th1_c,
        "texture_id": tid,
        "texture_name": tname
    }

RUNS = [
    "ENS_STATE_201803",
    "ENS_STATE_201803_noRyu",
    "ENS_FORC_201803",
    "ENS_FORC_201803_noRyu"
]

budget_rows = []
theta1_rows = []
texture_rows = []

for rname in RUNS:
    print(f"\nProcessing {rname} on all 16,030 cells...")
    out_dir = os.path.join(DIAG_BASE, rname, "output")
    files = sorted(glob.glob(os.path.join(out_dir, "mech_diag.*.txt")))
    
    # Accumulateurs par maille : (gc, gr) -> [w_pert, w_ryu, w_qc, w_mid, w_rec]
    acc = {k: np.zeros(5, dtype=np.float64) for k in cell_info.keys()}
    
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
                    # nmetforc = 2, so weight 0.5 per line
                    wp = sum(float(p[10 + j]) for j in range(4)) * 0.5
                    wr = sum(float(p[14 + j]) for j in range(4)) * 0.5
                    acc[ckey][0] += wp
                    acc[ckey][1] += wr
                elif rtype == "QCSM":
                    wqc = float(p[12])
                    acc[ckey][2] += wqc
                elif rtype == "SETM":
                    wm = sum(float(p[12 + j]) for j in range(4))
                    wrc = sum(float(p[17 + j]) for j in range(4))
                    acc[ckey][3] += wm
                    acc[ckey][4] += wrc

    # Convert to DataFrame
    records = []
    for ckey, vals in acc.items():
        c_meta = cell_info[ckey]
        records.append({
            "gc": ckey[0],
            "gr": ckey[1],
            "theta1_class": c_meta["theta1_class"],
            "texture_id": c_meta["texture_id"],
            "texture_name": c_meta["texture_name"],
            "w_pert": vals[0],
            "w_ryu": vals[1],
            "w_qc": vals[2],
            "w_mid": vals[3],
            "w_rec": vals[4],
            "w_sum": np.sum(vals)
        })
    df_cells = pd.DataFrame(records)
    
    # 1. Bilan domaine complet (moyenne arithmétique sur 16 030 mailles)
    m_pert = df_cells["w_pert"].mean()
    m_ryu = df_cells["w_ryu"].mean()
    m_qc = df_cells["w_qc"].mean()
    m_mid = df_cells["w_mid"].mean()
    m_rec = df_cells["w_rec"].mean()
    m_sum = m_pert + m_ryu + m_qc + m_mid + m_rec
    
    R = R_values[rname]
    minus_R = -R
    gap = minus_R - m_sum
    
    budget_rows.append({
        "run": rname,
        "status": "COMPLETED",
        "R_mm": round(R, 2),
        "minus_R_mm": round(minus_R, 2),
        "w_pert_mm": round(m_pert, 4),
        "w_ryu_mm": round(m_ryu, 4),
        "w_qc_mm": round(m_qc, 4),
        "w_mid_mm": round(m_mid, 4),
        "w_rec_mm": round(m_rec, 4),
        "w_sum_mm": round(m_sum, 4),
        "gap_minusR_minus_sum_mm": round(gap, 4)
    })
    print(f"  Domain Mean: -R={minus_R:.2f}, w_sum={m_sum:.4f}, gap={gap:.4f}")

    # 2. Par classe de theta1
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
                "w_mid_mm": round(sub["w_mid"].mean(), 4),
                "w_rec_mm": round(sub["w_rec"].mean(), 4),
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
                "w_mid_mm": 0.0,
                "w_rec_mm": 0.0,
                "w_sum_mm": 0.0
            })

    # 3. Par texture
    for tid, grp in df_cells.groupby("texture_id"):
        tname = TEXTURE_NAMES.get(tid, f"Tex_{tid}")
        texture_rows.append({
            "run": rname,
            "texture_id": tid,
            "texture_name": tname,
            "n_cells": len(grp),
            "w_pert_mm": round(grp["w_pert"].mean(), 4),
            "w_ryu_mm": round(grp["w_ryu"].mean(), 4),
            "w_qc_mm": round(grp["w_qc"].mean(), 4),
            "w_mid_mm": round(grp["w_mid"].mean(), 4),
            "w_rec_mm": round(grp["w_rec"].mean(), 4),
            "w_sum_mm": round(grp["w_sum"].mean(), 4)
        })

df_budget = pd.DataFrame(budget_rows)
df_theta1 = pd.DataFrame(theta1_rows)
df_texture = pd.DataFrame(texture_rows)

out_budget = os.path.join(TABLES_DIR, "march2018_mechanism_budget.csv")
out_theta1 = os.path.join(TABLES_DIR, "march2018_mechanism_by_theta1_class.csv")
out_texture = os.path.join(TABLES_DIR, "march2018_mechanism_by_texture.csv")

df_budget.to_csv(out_budget, index=False)
df_theta1.to_csv(out_theta1, index=False)
df_texture.to_csv(out_texture, index=False)

print("\nSaved files:")
print(f"  - {out_budget}")
print(f"  - {out_theta1}")
print(f"  - {out_texture}")
