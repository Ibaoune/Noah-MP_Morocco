#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step13_complete_innov_incr.py

Extrait les innovations et incréments par couche pour Lalla Chafia et Sidi Jabeur
pour DA_corr, DA_nocdf, DA_nocdf_nowilt et DA_cdf en 2018 (mensuel et annuel).
Sauvegarde dans paper1/tables/lalla_chafia_innovations_and_increments.csv
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")

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

weights_181 = {}
for cname, ccells in [("Lalla Chafia", cells_lalla), ("Sidi Jabeur", cells_jabeur)]:
    w = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w[r, c] += 0.25
        w[r, c+1] += 0.25
        w[r+1, c] += 0.25
        w[r+1, c+1] += 0.25
    w /= np.sum(w)
    weights_181[cname] = w

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

EXPERIMENTS_DA = {
    "DA_corr": {
        "style": "flat",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018")
    },
    "DA_nocdf": {
        "style": "hierarchical",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020")
    },
    "DA_nocdf_nowilt": {
        "style": "flat",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018")
    },
    "DA_cdf": {
        "style": "hierarchical",
        "dir": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020")
    }
}

innov_records = []

for st_name in ["Lalla Chafia", "Sidi Jabeur"]:
    w = weights_181[st_name]
    m_catch = w > 0.0
    w_norm = w / np.sum(w[m_catch])
    
    for da_exp, cfg in EXPERIMENTS_DA.items():
        print(f"Extraction {st_name} / {da_exp}...")
        exp_dir = cfg["dir"]
        all_innov_list = []
        n_obs_tot = 0
        i1_tot, i2_tot, i3_tot, i4_tot = 0.0, 0.0, 0.0, 0.0
        
        for m in range(1, 13):
            ym = f"2018{m:02d}"
            if cfg["style"] == "hierarchical":
                m_str = f"2018-{m:02d}"
                inv_files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_str}/EnKF/{ym}/*_innov.*.nc")))
                inc_files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_str}/EnKF/{ym}/*_incr.*.nc")))
            else:
                inv_files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/*_innov.*.nc")))
                inc_files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/*_incr.*.nc")))
                
            m_innovs = []
            n_obs_m = 0
            for f in inv_files:
                with nc.Dataset(f) as ds:
                    d = ds["innov_01"][:].squeeze()
                    valid = (d != -9999.0) & (~np.isnan(d)) & m_catch
                    if np.sum(valid) > 0:
                        n_obs_m += int(np.sum(valid))
                        m_innovs.extend(d[valid].tolist())
                        
            i1_m, i2_m, i3_m, i4_m = 0.0, 0.0, 0.0, 0.0
            for f in inc_files:
                with nc.Dataset(f) as ds:
                    v1 = np.where(ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze())
                    v2 = np.where(ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze())
                    v3 = np.where(ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze())
                    v4 = np.where(ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze())
                    i1_m += float(np.sum(v1 * w_norm))
                    i2_m += float(np.sum(v2 * w_norm))
                    i3_m += float(np.sum(v3 * w_norm))
                    i4_m += float(np.sum(v4 * w_norm))

            mean_inv_m = float(np.mean(m_innovs)) if len(m_innovs) > 0 else np.nan
            all_innov_list.extend(m_innovs)
            n_obs_tot += n_obs_m
            i1_tot += i1_m
            i2_tot += i2_m
            i3_tot += i3_m
            i4_tot += i4_m
            
            innov_records.append({
                "target": st_name,
                "experiment": da_exp,
                "period_type": "monthly_2018",
                "period": f"2018-{m:02d}",
                "n_obs_assimilated": n_obs_m,
                "mean_innovation_m3m3": round(mean_inv_m, 6) if not np.isnan(mean_inv_m) else np.nan,
                "incr_layer1_m3m3": round(i1_m, 6),
                "incr_layer2_m3m3": round(i2_m, 6),
                "incr_layer3_m3m3": round(i3_m, 6),
                "incr_layer4_m3m3": round(i4_m, 6),
                "incr_layer1_mm": round(i1_m * dz[0] * 1000.0, 4),
                "incr_layer2_mm": round(i2_m * dz[1] * 1000.0, 4),
                "incr_layer3_mm": round(i3_m * dz[2] * 1000.0, 4),
                "incr_layer4_mm": round(i4_m * dz[3] * 1000.0, 4),
                "incr_total_mm": round((i1_m*dz[0] + i2_m*dz[1] + i3_m*dz[2] + i4_m*dz[3]) * 1000.0, 4)
            })

        # Bilan annuel 2018
        mean_inv_ann = float(np.mean(all_innov_list)) if len(all_innov_list) > 0 else np.nan
        innov_records.append({
            "target": st_name,
            "experiment": da_exp,
            "period_type": "annual_2018",
            "period": "2018",
            "n_obs_assimilated": n_obs_tot,
            "mean_innovation_m3m3": round(mean_inv_ann, 6) if not np.isnan(mean_inv_ann) else np.nan,
            "incr_layer1_m3m3": round(i1_tot, 6),
            "incr_layer2_m3m3": round(i2_tot, 6),
            "incr_layer3_m3m3": round(i3_tot, 6),
            "incr_layer4_m3m3": round(i4_tot, 6),
            "incr_layer1_mm": round(i1_tot * dz[0] * 1000.0, 4),
            "incr_layer2_mm": round(i2_tot * dz[1] * 1000.0, 4),
            "incr_layer3_mm": round(i3_tot * dz[2] * 1000.0, 4),
            "incr_layer4_mm": round(i4_tot * dz[3] * 1000.0, 4),
            "incr_total_mm": round((i1_tot*dz[0] + i2_tot*dz[1] + i3_tot*dz[2] + i4_tot*dz[3]) * 1000.0, 4)
        })

df_innov = pd.DataFrame(innov_records)
out_innov = os.path.join(TABLES_DIR, "lalla_chafia_innovations_and_increments.csv")
df_innov.to_csv(out_innov, index=False)
print(f"[OK] Sauvegardé {out_innov} avec {len(df_innov)} enregistrements.")
