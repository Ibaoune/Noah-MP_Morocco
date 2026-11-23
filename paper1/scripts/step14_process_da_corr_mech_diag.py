#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step14_process_da_corr_mech_diag.py

Analyse le run diagnostique DA_corr Mars 2018 et produit :
  - paper1/tables/march2018_mechanism_budget_da_corr.csv
  - paper1/tables/comparison_march2018_diag_vs_prod.csv

Correctifs appliqués :
  1. Incréments archivés pris directement dans les fichiers EnKF du run diag
     (diag_mech/DA_corr_201803_diag/output/EnKF/201803) avec colonne source_archived.
  2. Eau rejetée calculée directement par différence (δ demandé - δ appliqué, par couche) :
     - clip_qc_layer1_mm : écart couche 1 (écrêtage qc) dans une colonne séparée
     - rejected_water_l2_mm, l3, l4 : rejets couches 2 à 4
     - rejected_water_total_l2_l4_mm : somme des couches 2 à 4 uniquement
  3. Comptage des cas rejetés uniquement si |δ demandé| > 1e-6 m3/m3, avec le nombre
     total de mises à jour membre×couche du mois.
  4. Comparaison mars complet diag vs production (P, ET, Qs, Qsb, ΔS, Incr_EnKF).
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
EXP_PROD_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018")
EXP_DIAG_DIR = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/diag_mech/DA_corr_201803_diag")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
RST_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")

os.makedirs(TABLES_DIR, exist_ok=True)

# 0. Masque du domaine et bassins versants amont
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

# 1. Incréments archivés : pris directement dans les fichiers EnKF du run diag
diag_enkf_files = sorted(glob.glob(os.path.join(EXP_DIAG_DIR, "output/EnKF/201803/*_incr.*.nc")))
if not diag_enkf_files:
    source_archived = "NON_EXISTANT"
    print("[ATTENTION] Aucun fichier EnKF trouvé dans le run diag !")
    # Repli sur production avec marquage
    enkf_source_files = sorted(glob.glob(os.path.join(EXP_PROD_DIR, "output/EnKF/201803/*_incr.*.nc")))
    source_archived = "experiments/NorthMor/.../DA_corr_2018/output/EnKF/201803 (repli)"
else:
    source_archived = "diag_mech/DA_corr_201803_diag/output/EnKF/201803"
    enkf_source_files = diag_enkf_files
    print(f"[OK] {len(enkf_source_files)} fichiers EnKF du run diag trouvés.")

enkf_data = {}
arch_grid = np.zeros((4, 121, 181), dtype=np.float64)
for f in enkf_source_files:
    parts = os.path.basename(f).split("_")
    ts_str = parts[3]
    ts = (int(ts_str[:4]), int(ts_str[4:6]), int(ts_str[6:8]), int(ts_str[8:10]), int(ts_str[10:12]))
    with nc.Dataset(f) as ds:
        arr = np.zeros((4, 121, 181), dtype=np.float32)
        for l in range(4):
            v = ds[f"anlys_incr_Soil Moisture Layer {l+1}_01"][:].squeeze()
            arr[l] = np.where(v == -9999.0, 0.0, v)
            arch_grid[l] += arr[l] * dz[l] * 1000.0
        enkf_data[ts] = arr

# 2. Bornes des 32 rangs MPI
ranks_bounds = {}
for i in range(32):
    lf = os.path.join(EXP_DIAG_DIR, f"logs/lislog.{i:04d}")
    with open(lf) as fp:
        for l in fp:
            if "local domain   " in l:
                p = l.split()
                ranks_bounds[i] = (float(p[3]), float(p[5]))

# 3. Lecture des fichiers mech_diag.*.txt du run instrumenté
mech_files = sorted(glob.glob(os.path.join(EXP_DIAG_DIR, "output/mech_diag.*.txt")))
print(f"Extraction des diagnostics instrumentés depuis {len(mech_files)} fichiers mech_diag...")

applied_grid = np.zeros((4, 121, 181), dtype=np.float64)
mid_da_tot = np.zeros((121, 181), dtype=np.float64)
mid_cases = np.zeros((121, 181), dtype=int)

other_pert = np.zeros((121, 181), dtype=np.float64)
other_ryu  = np.zeros((121, 181), dtype=np.float64)
other_qc   = np.zeros((121, 181), dtype=np.float64)
other_rec  = np.zeros((121, 181), dtype=np.float64)

wl = catchment_weights_181["Lalla_Chafia"]
wj = catchment_weights_181["Sidi_Jabeur"]

upd_counts = {"Domain": np.zeros(4, int), "Lalla_Chafia": np.zeros(4, int), "Sidi_Jabeur": np.zeros(4, int)}
rej_counts = {"Domain": np.zeros(4, int), "Lalla_Chafia": np.zeros(4, int), "Sidi_Jabeur": np.zeros(4, int)}

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
            c0 = int(round((lon - (-10.0)) / 0.05))
            r0 = int(round((lat - 30.0) / 0.05))

            if not (0 <= c0 < 181 and 0 <= r0 < 121):
                continue

            if rtype == "SETD":
                ts = (int(p[0]), int(p[1]), int(p[2]), int(p[3]), int(p[4]))
                n_mid = int(p[11])
                mid_cases[r0, c0] += n_mid
                wm = sum(float(p[12 + j]) for j in range(4))
                mid_da_tot[r0, c0] += wm

                applied_grid[0, r0, c0] += float(p[16])
                applied_grid[1, r0, c0] += float(p[17])
                applied_grid[2, r0, c0] += float(p[18])
                applied_grid[3, r0, c0] += float(p[19])

                rejs = [0, int(p[20]), int(p[21]), int(p[22])]
                delta_dem = enkf_data[ts][:, r0, c0]

                in_lc = wl[r0, c0] > 0
                in_sj = wj[r0, c0] > 0

                for l in range(4):
                    if abs(delta_dem[l]) > 1e-6:
                        upd_counts["Domain"][l] += 20
                        rej_counts["Domain"][l] += rejs[l]
                        if in_lc:
                            upd_counts["Lalla_Chafia"][l] += 20
                            rej_counts["Lalla_Chafia"][l] += rejs[l]
                        if in_sj:
                            upd_counts["Sidi_Jabeur"][l] += 20
                            rej_counts["Sidi_Jabeur"][l] += rejs[l]

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
# Résidu brut R = P - ET - Q - Delta_S
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
    # Incréments archivés (mm)
    ai_l1 = float(np.sum(arch_grid[0] * w_map))
    ai_l2 = float(np.sum(arch_grid[1] * w_map))
    ai_l3 = float(np.sum(arch_grid[2] * w_map))
    ai_l4 = float(np.sum(arch_grid[3] * w_map))
    ai_tot = ai_l1 + ai_l2 + ai_l3 + ai_l4

    # Incréments appliqués (mm)
    ap_l1 = float(np.sum(applied_grid[0] * w_map))
    ap_l2 = float(np.sum(applied_grid[1] * w_map))
    ap_l3 = float(np.sum(applied_grid[2] * w_map))
    ap_l4 = float(np.sum(applied_grid[3] * w_map))
    ap_tot = ap_l1 + ap_l2 + ap_l3 + ap_l4

    # Eau rejetée directement (δ demandé - δ appliqué, par couche)
    clip_qc_l1 = ai_l1 - ap_l1
    rej_l2 = ai_l2 - ap_l2
    rej_l3 = ai_l3 - ap_l3
    rej_l4 = ai_l4 - ap_l4
    rej_tot = rej_l2 + rej_l3 + rej_l4 # Somme couches 2-4 uniquement

    # Mises à jour demandées et rejets comptés uniquement si |δ| > 1e-6
    tot_upd_l1 = int(upd_counts[reg_name][0])
    tot_upd_l2 = int(upd_counts[reg_name][1])
    tot_upd_l3 = int(upd_counts[reg_name][2])
    tot_upd_l4 = int(upd_counts[reg_name][3])
    tot_upd_l2_l4 = tot_upd_l2 + tot_upd_l3 + tot_upd_l4
    tot_upd_all = tot_upd_l1 + tot_upd_l2_l4

    n_rej_2 = int(rej_counts[reg_name][1])
    n_rej_3 = int(rej_counts[reg_name][2])
    n_rej_4 = int(rej_counts[reg_name][3])
    n_rej_tot_l2_l4 = n_rej_2 + n_rej_3 + n_rej_4

    pct_rej = (n_rej_tot_l2_l4 / tot_upd_l2_l4 * 100.0) if tot_upd_l2_l4 > 0 else 0.0

    # Midrange et autres termes mécanisme
    w_mid = float(np.sum(mid_da_tot * w_map))
    n_mid = int(np.sum(mid_cases * (w_map > 0))) if reg_name != "Domain" else int(np.sum(mid_cases))

    w_p = float(np.sum(other_pert * w_map))
    w_r = float(np.sum(other_ryu * w_map))
    w_q = float(np.sum(other_qc * w_map))
    w_rc = float(np.sum(other_rec * w_map))
    other_tot = w_p + w_r + w_q + w_rc

    # Somme réelle appliquée et fermeture
    w_sum_applied = ap_tot + w_mid + other_tot
    r_raw = R_raw_dict[reg_name] # P - ET - Q - Delta_S = R
    minus_r = -r_raw              # -R = -(P - ET - Q - Delta_S)
    gap = minus_r - w_sum_applied

    records.append({
        "run": "DA_corr_201803",
        "region": reg_name,
        "source_archived": source_archived,
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
        "clip_qc_layer1_mm": round(clip_qc_l1, 4),
        "rejected_water_l2_mm": round(rej_l2, 4),
        "rejected_water_l3_mm": round(rej_l3, 4),
        "rejected_water_l4_mm": round(rej_l4, 4),
        "rejected_water_total_l2_l4_mm": round(rej_tot, 4),
        "total_updates_member_layer_l2_l4": tot_upd_l2_l4,
        "total_updates_member_layer_all": tot_upd_all,
        "rejected_cases_l2": n_rej_2,
        "rejected_cases_l3": n_rej_3,
        "rejected_cases_l4": n_rej_4,
        "rejected_cases_total_l2_l4": n_rej_tot_l2_l4,
        "pct_rejected_cases_l2_l4": round(pct_rej, 4),
        "midrange_water_mm": round(w_mid, 4),
        "midrange_cases": n_mid,
        "other_mechanism_water_mm": round(other_tot, 4),
        "w_sum_applied_mm": round(w_sum_applied, 4),
        "gap_minusR_minus_applied_mm": round(gap, 4),
        "closure_valid_lt_1mm": abs(gap) < 1.0
    })

df_budget = pd.DataFrame(records)
out_budget_csv = os.path.join(TABLES_DIR, "march2018_mechanism_budget_da_corr.csv")
df_budget.to_csv(out_budget_csv, index=False)
print(f"[OK] Sauvegardé {out_budget_csv}")

# 5. Table comparative complète Mars 2018 : Diag vs Production
print("\n>>> Calcul de la comparaison Mars complet : Diag vs Production...")
dates_march = [f"201803{d:02d}0000" for d in range(2, 32)] + ["201804010000"]

def calc_fluxes(dir_path):
    p_grid = np.zeros((121, 181))
    et_grid = np.zeros((121, 181))
    qs_grid = np.zeros((121, 181))
    qsb_grid = np.zeros((121, 181))
    for dt_str in dates_march:
        ym = dt_str[:6]
        f = os.path.join(dir_path, f"output/SURFACEMODEL/{ym}/LIS_HIST_{dt_str}.d01.nc")
        with nc.Dataset(f) as ds:
            p_grid += ds["TotalPrecip_tavg"][:].squeeze() * 86400.0
            et_grid += ds["Evap_tavg"][:].squeeze() * 86400.0
            qs_grid += ds["Qs_tavg"][:].squeeze() * 86400.0
            qsb_grid += ds["Qsb_tavg"][:].squeeze() * 86400.0
    return p_grid, et_grid, qs_grid, qsb_grid

p_prod, et_prod, qs_prod, qsb_prod = calc_fluxes(EXP_PROD_DIR)
p_diag, et_diag, qs_diag, qsb_diag = calc_fluxes(EXP_DIAG_DIR)

def calc_storage(rst_file):
    with nc.Dataset(rst_file) as ds:
        smc = ds["SMC"][:]
        wa = ds["WA"][:]
        can = ds["CANWAT"][:]
        sn = ds["SNEQV"][:]
        if smc.shape[1] == 320600:
            smc = smc.reshape(4, 16030, 20).mean(axis=2)
            wa = wa.reshape(16030, 20).mean(axis=1)
            can = can.reshape(16030, 20).mean(axis=1)
            sn = sn.reshape(16030, 20).mean(axis=1)
        tot_mm = np.sum(smc * dz[:, None], axis=0) * 1000.0 + wa + can + sn
        grid = np.zeros((121, 181))
        lats = ds["lat"][:][::20] if len(ds["lat"][:]) == 320600 else ds["lat"][:]
        lons = ds["lon"][:][::20] if len(ds["lon"][:]) == 320600 else ds["lon"][:]
        for i in range(len(lats)):
            c = int(round((lons[i] - (-10.0)) / 0.05))
            r = int(round((lats[i] - 30.0) / 0.05))
            grid[r, c] = tot_mm[i]
        return grid

rst_start_prod = os.path.join(EXP_PROD_DIR, "output/SURFACEMODEL/201802/LIS_RST_NOAHMP401_201802282345.d01.nc")
rst_end_prod = os.path.join(EXP_PROD_DIR, "output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
ds_prod_grid = calc_storage(rst_end_prod) - calc_storage(rst_start_prod)

rst_end_diag = os.path.join(EXP_DIAG_DIR, "output/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803312345.d01.nc")
ds_diag_grid = calc_storage(rst_end_diag) - calc_storage(rst_start_prod)

def calc_increments(dir_path):
    files = sorted(glob.glob(os.path.join(dir_path, "output/EnKF/201803/*_incr.*.nc")))
    tot = np.zeros((121, 181))
    for f in files:
        with nc.Dataset(f) as ds:
            for l in range(4):
                v = np.where(ds[f"anlys_incr_Soil Moisture Layer {l+1}_01"][:].squeeze() == -9999.0, 0.0, ds[f"anlys_incr_Soil Moisture Layer {l+1}_01"][:].squeeze())
                tot += v * dz[l] * 1000.0
    return tot

inc_prod_grid = calc_increments(EXP_PROD_DIR)
inc_diag_grid = calc_increments(EXP_DIAG_DIR)

comp_regions = [
    ("Domain", np.where(landmask, 1.0 / n_domain, 0.0)),
    ("Lalla_Chafia", catchment_weights_181["Lalla_Chafia"]),
    ("Sidi_Jabeur", catchment_weights_181["Sidi_Jabeur"])
]

comp_rows = []
for rname, w in comp_regions:
    comp_rows.append({
        "region": rname,
        "P_prod_mm": round(float(np.sum(p_prod * w)), 4),
        "P_diag_mm": round(float(np.sum(p_diag * w)), 4),
        "diff_P_mm": round(float(np.sum(p_diag * w)) - float(np.sum(p_prod * w)), 4),
        "ET_prod_mm": round(float(np.sum(et_prod * w)), 4),
        "ET_diag_mm": round(float(np.sum(et_diag * w)), 4),
        "diff_ET_mm": round(float(np.sum(et_diag * w)) - float(np.sum(et_prod * w)), 4),
        "Qs_prod_mm": round(float(np.sum(qs_prod * w)), 4),
        "Qs_diag_mm": round(float(np.sum(qs_diag * w)), 4),
        "diff_Qs_mm": round(float(np.sum(qs_diag * w)) - float(np.sum(qs_prod * w)), 4),
        "Qsb_prod_mm": round(float(np.sum(qsb_prod * w)), 4),
        "Qsb_diag_mm": round(float(np.sum(qsb_diag * w)), 4),
        "diff_Qsb_mm": round(float(np.sum(qsb_diag * w)) - float(np.sum(qsb_prod * w)), 4),
        "Delta_S_prod_mm": round(float(np.sum(ds_prod_grid * w)), 4),
        "Delta_S_diag_mm": round(float(np.sum(ds_diag_grid * w)), 4),
        "diff_Delta_S_mm": round(float(np.sum(ds_diag_grid * w)) - float(np.sum(ds_prod_grid * w)), 4),
        "Incr_prod_mm": round(float(np.sum(inc_prod_grid * w)), 4),
        "Incr_diag_mm": round(float(np.sum(inc_diag_grid * w)), 4),
        "diff_Incr_mm": round(float(np.sum(inc_diag_grid * w)) - float(np.sum(inc_prod_grid * w)), 4),
    })

df_comp = pd.DataFrame(comp_rows)
out_comp_csv = os.path.join(TABLES_DIR, "comparison_march2018_diag_vs_prod.csv")
df_comp.to_csv(out_comp_csv, index=False)
print(f"[OK] Sauvegardé {out_comp_csv}")

print("\n=== Synthèse Fermeture DA_corr Mars 2018 ===")
for r in records:
    print(f"Région: {r['region']:12s} | -R = {r['minus_R_raw_mm']:8.4f} mm | Appliqué = {r['w_sum_applied_mm']:8.4f} mm | Écart = {r['gap_minusR_minus_applied_mm']:7.4f} mm | < 1 mm : {r['closure_valid_lt_1mm']}")
print("\n=== Comparaison Diag vs Production Mars 2018 ===")
print(df_comp.to_string())
