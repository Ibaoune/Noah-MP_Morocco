#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step14_process_da_corr_mech_diag.py

Analyse le run diagnostique DA_corr Mars 2018 et produit :
  - paper1/tables/march2018_mechanism_budget_da_corr.csv

Sépare en particulier :
  - l'incrément archivé (depuis les NetCDF EnKF)
  - l'incrément réellement appliqué par couche (depuis mech_diag.*.txt SETD)
  - les rejets hors-bornes couches 2-4 (noahmp401_setsoilm.F90) : nombre de cas et eau rejetée
  - les remplacements par le midrange pendant l'analyse DA : nombre de cas et eau
  - la fermeture du bilan d'eau par rapport au résidu mesuré (-R)
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
EXP_DIAG_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/DA_corr_201803_diag")
EXP_PROD_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
RST_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")

with nc.Dataset(RST_PATH) as ds:
    lats = ds.variables["lat"][::20]
    lons = ds.variables["lon"][::20]
landmask = np.zeros((121, 181), dtype=bool)
for lat, lon in zip(lats, lons):
    c0 = int(round((lon - (-10.0)) / 0.05))
    r0 = int(round((lat - 30.0) / 0.05))
    landmask[r0, c0] = True

n_domain = int(np.sum(landmask)) # 16030

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

dz = np.array([0.1, 0.3, 0.6, 1.0], dtype=np.float32)

# 1. Bornes géographiques des 32 rangs MPI
ranks_bounds = {}
for i in range(32):
    lf = os.path.join(EXP_DIAG_DIR, f"logs/lislog.{i:04d}")
    if not os.path.exists(lf):
        lf = os.path.join(BASE_DIR, f"experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/ENS_STATE_201803/logs/lislog_ENS_STATE_201803.{i:04d}")
    with open(lf) as fp:
        for l in fp:
            if "local domain   " in l:
                p = l.split()
                ranks_bounds[i] = (float(p[3]), float(p[5])) # minlat, minlon

# 2. Incréments archivés depuis les fichiers NetCDF EnKF pour Mars 2018
inc_files = sorted(glob.glob(os.path.join(EXP_PROD_DIR, "output/EnKF/201803/*_incr.*.nc")))
print(f"Extraction des incréments archivés depuis {len(inc_files)} fichiers NetCDF...")

arch_l1 = np.zeros((121, 181), dtype=float)
arch_l2 = np.zeros((121, 181), dtype=float)
arch_l3 = np.zeros((121, 181), dtype=float)
arch_l4 = np.zeros((121, 181), dtype=float)

for f in inc_files:
    with nc.Dataset(f) as ds:
        v1 = np.where(ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze())
        v2 = np.where(ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze())
        v3 = np.where(ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze())
        v4 = np.where(ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze() == -9999.0, 0.0, ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze())
        arch_l1 += v1 * dz[0] * 1000.0
        arch_l2 += v2 * dz[1] * 1000.0
        arch_l3 += v3 * dz[2] * 1000.0
        arch_l4 += v4 * dz[3] * 1000.0

# 3. Lecture des fichiers mech_diag.*.txt du run instrumenté
mech_files = sorted(glob.glob(os.path.join(EXP_DIAG_DIR, "output/mech_diag.*.txt")))
print(f"Extraction des diagnostics instrumentés depuis {len(mech_files)} fichiers mech_diag...")

applied_l1 = np.zeros((121, 181), dtype=float)
applied_l2 = np.zeros((121, 181), dtype=float)
applied_l3 = np.zeros((121, 181), dtype=float)
applied_l4 = np.zeros((121, 181), dtype=float)
mid_da_tot = np.zeros((121, 181), dtype=float)

rej_cases_l2 = np.zeros((121, 181), dtype=int)
rej_cases_l3 = np.zeros((121, 181), dtype=int)
rej_cases_l4 = np.zeros((121, 181), dtype=int)
mid_cases    = np.zeros((121, 181), dtype=int)

other_pert = np.zeros((121, 181), dtype=float)
other_ryu  = np.zeros((121, 181), dtype=float)
other_qc   = np.zeros((121, 181), dtype=float)
other_rec  = np.zeros((121, 181), dtype=float)

for f in mech_files:
    if os.path.getsize(f) == 0:
        continue
    rk = int(f.split(".")[-2])
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
            c0 = int(round((lon - (-10.0)) / 0.05)) # 0..180
            r0 = int(round((lat - 30.0) / 0.05))   # 0..120

            if not (0 <= c0 < 181 and 0 <= r0 < 121):
                continue

            if rtype == "SETD":
                n_mid = int(p[11])
                mid_cases[r0, c0] += n_mid
                wm = sum(float(p[12 + j]) for j in range(4))
                mid_da_tot[r0, c0] += wm
                
                applied_l1[r0, c0] += float(p[16])
                applied_l2[r0, c0] += float(p[17])
                applied_l3[r0, c0] += float(p[18])
                applied_l4[r0, c0] += float(p[19])

                rej_cases_l2[r0, c0] += int(p[20])
                rej_cases_l3[r0, c0] += int(p[21])
                rej_cases_l4[r0, c0] += int(p[22])

            elif rtype == "PERT":
                wp = sum(float(p[10 + j]) for j in range(4)) * 0.5
                wr = sum(float(p[14 + j]) for j in range(4)) * 0.5
                other_pert[r0, c0] += wp
                other_ryu[r0, c0] += wr
            elif rtype == "QCSM":
                other_qc[r0, c0] += float(p[12])
            elif rtype in ("SETM", "SETP"):
                other_rec[r0, c0] += sum(float(p[17 + j]) for j in range(4))

# 4. Synthèse par région
# Résidus bruts R = P - ET - Q - Delta_S (mm)
R_raw_dict = {
    "Domain": 21.9041,
    "Lalla_Chafia": -11.4595,
    "Sidi_Jabeur": -76.1337
}

records = []

for reg_name, w_map in [
    ("Domain", np.where(landmask, 1.0 / n_domain, 0.0)),
    ("Lalla_Chafia", catchment_weights_181["Lalla_Chafia"]),
    ("Sidi_Jabeur", catchment_weights_181["Sidi_Jabeur"])
]:
    # Incréments archivés par couche (mm)
    ai_l1 = float(np.sum(arch_l1 * w_map))
    ai_l2 = float(np.sum(arch_l2 * w_map))
    ai_l3 = float(np.sum(arch_l3 * w_map))
    ai_l4 = float(np.sum(arch_l4 * w_map))
    ai_tot = ai_l1 + ai_l2 + ai_l3 + ai_l4

    # Incréments appliqués par couche (mm)
    ap_l1 = float(np.sum(applied_l1 * w_map))
    ap_l2 = float(np.sum(applied_l2 * w_map))
    ap_l3 = float(np.sum(applied_l3 * w_map))
    ap_l4 = float(np.sum(applied_l4 * w_map))
    ap_tot = ap_l1 + ap_l2 + ap_l3 + ap_l4

    # Eau rejetée (mm)
    rej_l1 = ai_l1 - ap_l1
    rej_l2 = ai_l2 - ap_l2
    rej_l3 = ai_l3 - ap_l3
    rej_l4 = ai_l4 - ap_l4
    rej_tot = ai_tot - ap_tot

    # Nombre de cas rejetés
    n_rej_2 = int(np.sum(rej_cases_l2 * (w_map > 0))) if reg_name != "Domain" else int(np.sum(rej_cases_l2))
    n_rej_3 = int(np.sum(rej_cases_l3 * (w_map > 0))) if reg_name != "Domain" else int(np.sum(rej_cases_l3))
    n_rej_4 = int(np.sum(rej_cases_l4 * (w_map > 0))) if reg_name != "Domain" else int(np.sum(rej_cases_l4))
    n_rej_tot = n_rej_2 + n_rej_3 + n_rej_4

    # Midrange
    w_mid = float(np.sum(mid_da_tot * w_map))
    n_mid = int(np.sum(mid_cases * (w_map > 0))) if reg_name != "Domain" else int(np.sum(mid_cases))

    # Autres termes mécanisme
    w_p = float(np.sum(other_pert * w_map))
    w_r = float(np.sum(other_ryu * w_map))
    w_q = float(np.sum(other_qc * w_map))
    w_rc = float(np.sum(other_rec * w_map))
    other_tot = w_p + w_r + w_q + w_rc

    # Somme réelle appliquée au modèle
    w_sum_applied = ap_tot + w_mid + other_tot
    r_raw = R_raw_dict[reg_name]
    minus_r = -r_raw
    gap = minus_r - w_sum_applied

    # Ratio eau appliquée / archivée
    ratio_applied = (ap_tot / ai_tot) if abs(ai_tot) > 1e-4 else np.nan

    records.append({
        "run": "DA_corr_201803",
        "region": reg_name,
        "R_raw_mm": round(r_raw, 4),
        "minus_R_raw_mm": round(minus_r, 4),
        "incr_archived_l1_mm": round(ai_l1, 4),
        "incr_archived_l2_mm": round(ai_l2, 4),
        "incr_archived_l3_mm": round(ai_l3, 4),
        "incr_archived_l4_mm": round(ai_l4, 4),
        "incr_archived_total_mm": round(ai_tot, 4),
        "incr_applied_l1_mm": round(ap_l1, 4),
        "incr_applied_l2_mm": round(ap_l2, 4),
        "incr_applied_l3_mm": round(ap_l3, 4),
        "incr_applied_l4_mm": round(ap_l4, 4),
        "incr_applied_total_mm": round(ap_tot, 4),
        "rejected_water_l2_mm": round(rej_l2, 4),
        "rejected_water_l3_mm": round(rej_l3, 4),
        "rejected_water_l4_mm": round(rej_l4, 4),
        "rejected_water_total_mm": round(rej_tot, 4),
        "rejected_cases_l2": n_rej_2,
        "rejected_cases_l3": n_rej_3,
        "rejected_cases_l4": n_rej_4,
        "rejected_cases_total": n_rej_tot,
        "midrange_water_mm": round(w_mid, 4),
        "midrange_cases": n_mid,
        "other_mechanism_water_mm": round(other_tot, 4),
        "w_sum_applied_mm": round(w_sum_applied, 4),
        "gap_minusR_minus_applied_mm": round(gap, 4),
        "ratio_applied_over_archived": round(ratio_applied, 4) if not np.isnan(ratio_applied) else np.nan
    })

df_out = pd.DataFrame(records)
out_csv = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da_corr.csv")
df_out.to_csv(out_csv, index=False)
print(f"[OK] Sauvegardé {out_csv}")
print("\n=== Synthèse Fermeture DA_corr Mars 2018 complet ===")
for r in records:
    print(f"Région: {r['region']:12s} | -R = {r['minus_R_raw_mm']:8.4f} mm | Appliqué = {r['w_sum_applied_mm']:8.4f} mm | Écart = {r['gap_minusR_minus_applied_mm']:7.4f} mm | < 1 mm : {abs(r['gap_minusR_minus_applied_mm']) < 1.0}")
