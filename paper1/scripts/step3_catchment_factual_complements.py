#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
step3_catchment_factual_complements.py
Complements factuels sur Lalla Chafia et le Top 20 des mailles :
3b. Qs et Qsb annuels 2016-2020 pour OPL et DA_cdf sur Lalla Chafia et Sidi Jabeur.
3c. Innovations et increments de DA_nocdf et DA_cdf sur Lalla Chafia (mensuel 2018 et annuel 2016-2020).
3d. Innovations et increments sur les 20 mailles de top20_cells_qsb_difference.csv.
"""

import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")
TOP20_CSV = os.path.join(TABLES_DIR, "top20_cells_qsb_difference.csv")
os.makedirs(TABLES_DIR, exist_ok=True)

# 1. Delimitation HyMAP D8
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

catchments = {
    "b_l_chafia": ("Lalla Chafia", cells_lalla),
    "b_s_jabeur": ("Sidi Jabeur", cells_jabeur)
}

# Masques et poids sur 180x120 et 181x121
masks_180 = {}
weights_180 = {}
masks_181 = {}
weights_181 = {}

for cid, (cname, ccells) in catchments.items():
    m180 = np.zeros((120, 180), dtype=bool)
    for r, c in ccells:
        m180[r, c] = True
    masks_180[cid] = m180
    
    tot_area = sum(area_180[r, c] for r, c in ccells)
    w180 = np.zeros((120, 180), dtype=float)
    for r, c in ccells:
        w180[r, c] = area_180[r, c] / tot_area
    weights_180[cid] = w180

    w181 = np.zeros((121, 181), dtype=float)
    for r, c in ccells:
        w181[r, c] += 0.25 * area_180[r, c]
        w181[r, c+1] += 0.25 * area_180[r, c]
        w181[r+1, c] += 0.25 * area_180[r, c]
        w181[r+1, c+1] += 0.25 * area_180[r, c]
    weights_181[cid] = w181 / np.sum(w181)
    masks_181[cid] = w181 > 0

# Masque des 20 mailles du Top 20 sur 180x120 et projection 181x121
df_top20 = pd.read_csv(TOP20_CSV)
top20_cells_180 = list(zip(df_top20["row_180"].astype(int), df_top20["col_180"].astype(int)))

mask_top20_180 = np.zeros((120, 180), dtype=bool)
w_top20_180 = np.zeros((120, 180), dtype=float)
w_top20_181 = np.zeros((121, 181), dtype=float)

tot_area_top20 = sum(area_180[r, c] for r, c in top20_cells_180)
for r, c in top20_cells_180:
    mask_top20_180[r, c] = True
    w_top20_180[r, c] = area_180[r, c] / tot_area_top20
    w_top20_181[r, c] += 0.25 * area_180[r, c]
    w_top20_181[r, c+1] += 0.25 * area_180[r, c]
    w_top20_181[r+1, c] += 0.25 * area_180[r, c]
    w_top20_181[r+1, c+1] += 0.25 * area_180[r, c]

w_top20_181 = w_top20_181 / np.sum(w_top20_181)
mask_top20_181 = w_top20_181 > 0

dz = np.array([0.1, 0.3, 0.6, 1.0])

# =========================================================================
# PARTIE 3b : Qs et Qsb annuels 2016-2020 pour OPL et DA_cdf
# =========================================================================
print(">>> PARTIE 3b : Calcul de Qs et Qsb annuels 2016-2020 pour OPL et DA_cdf...")

REMAP_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_cdf_noirr_2016_2020/SURFACEMODEL"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL")
}

years = [2016, 2017, 2018, 2019, 2020]

records_3b = []
for exp in ["OPL", "DA_cdf"]:
    remap_dir = REMAP_DIRS[exp]
    for yr in years:
        n_days = 366 if yr in [2016, 2020] else 365
        yr_files = sorted(glob.glob(os.path.join(remap_dir, f"{yr}*/*.d01.nc")))
        f_next = os.path.join(remap_dir, f"{yr+1}01/LIS_HIST_{yr+1}01010000.d01.nc")
        if os.path.exists(f_next):
            yr_files.append(f_next)
        
        # Filtre premier fichier 01010000 de l'annee en cours
        yr_files = [f for f in yr_files if not os.path.basename(f).startswith(f"LIS_HIST_{yr}01010000")]

        qs_sum = {cid: 0.0 for cid in catchments}
        qsb_sum = {cid: 0.0 for cid in catchments}

        for f in yr_files:
            fname = os.path.basename(f)
            if not fname.startswith("LIS_HIST_"):
                continue
            with nc.Dataset(f) as ds:
                qs = np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb = np.squeeze(ds["Qsb_tavg"][:]) * 86400.0
                for cid in catchments:
                    w180 = weights_180[cid]
                    m180 = masks_180[cid]
                    qs_sum[cid] += float(np.sum(qs[m180] * w180[m180]))
                    qsb_sum[cid] += float(np.sum(qsb[m180] * w180[m180]))

        for cid, (cname, ccells) in catchments.items():
            tot_area_km2 = sum(area_180[r, c] for r, c in ccells) / 1e6
            qs_val = qs_sum[cid]
            qsb_val = qsb_sum[cid]
            tot_q_mm = qs_val + qsb_val
            vol_hm3 = tot_q_mm * tot_area_km2 / 1000.0
            q_mean_m3s = vol_hm3 * 1e6 / (n_days * 86400.0)

            records_3b.append({
                "experiment": exp,
                "station": cname,
                "station_id": cid,
                "year": yr,
                "n_days": n_days,
                "area_km2": round(tot_area_km2, 4),
                "Qs_mm": round(qs_val, 4),
                "Qsb_mm": round(qsb_val, 4),
                "TotalRunoff_mm": round(tot_q_mm, 4),
                "TotalRunoff_hm3": round(vol_hm3, 4),
                "Q_mean_m3s_equivalent": round(q_mean_m3s, 4)
            })

df_3b = pd.DataFrame(records_3b)
out_3b_csv = os.path.join(TABLES_DIR, "opl_da_cdf_annual_runoff_catchment_2016_2020.csv")
df_3b.to_csv(out_3b_csv, index=False)
print(f"[OK] Table 3b sauvee : {out_3b_csv}")

# Sauvegarder egalement les tables individuelles au format exact de da_nocdf
for exp in ["OPL", "DA_cdf"]:
    sub = df_3b[df_3b["experiment"] == exp].drop(columns=["experiment"])
    out_exp_csv = os.path.join(TABLES_DIR, f"{exp.lower()}_annual_runoff_catchment_2016_2020.csv")
    sub.to_csv(out_exp_csv, index=False)
    print(f"  [OK] Table individuelle : {out_exp_csv}")

# =========================================================================
# PARTIE 3c & 3d : Innovations et Incréments EnKF
# =========================================================================
print("\n>>> PARTIE 3c & 3d : Extraction des innovations et incréments EnKF...")

EXP_DA_DIRS = {
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output")
}

def analyze_innov_and_increments(exp_key, year, month=None, target_mask=None, target_weights=None):
    """
    Calcule pour une periode donnee (mois ou annee) :
      - nombre d'observations assimilees
      - innovation moyenne (obs - prevision)
      - increment moyen par couche (en mm et en m3/m3)
    """
    out_dir = EXP_DA_DIRS[exp_key]
    if month is not None:
        ym = f"{year}{month:02d}"
        m_lbl = f"{year}-{month:02d}"
        pat_innov = os.path.join(out_dir, f"{m_lbl}/EnKF/{ym}/*_innov.*.nc")
        pat_incr = os.path.join(out_dir, f"{m_lbl}/EnKF/{ym}/*_incr.*.nc")
    else:
        pat_innov = os.path.join(out_dir, f"{year}-*/EnKF/{year}*/*_innov.*.nc")
        pat_incr = os.path.join(out_dir, f"{year}-*/EnKF/{year}*/*_incr.*.nc")
        
    innov_files = sorted(glob.glob(pat_innov))
    incr_files = sorted(glob.glob(pat_incr))

    # 1. Innovations
    all_innovs = []
    n_obs_assimilated = 0

    for f in innov_files:
        with nc.Dataset(f) as ds:
            d = ds["innov_01"][:].squeeze()
            valid = (d != -9999.0) & (~np.isnan(d))
            if target_mask is not None:
                valid = valid & target_mask
            if np.sum(valid) > 0:
                vals = d[valid]
                all_innovs.extend(vals)
                n_obs_assimilated += len(vals)

    mean_innov = float(np.mean(all_innovs)) if len(all_innovs) > 0 else 0.0

    # 2. Increments par couche
    # Somme des increments integres sur les mailles cibles
    w_norm = target_weights / np.sum(target_weights)
    i1_mm, i2_mm, i3_mm, i4_mm = 0.0, 0.0, 0.0, 0.0
    i1_vol, i2_vol, i3_vol, i4_vol = 0.0, 0.0, 0.0, 0.0

    for f in incr_files:
        with nc.Dataset(f) as ds:
            v1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
            v2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
            v3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
            v4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
            
            # Masquer valeurs manquantes eventuelles
            v1 = np.where(v1 == -9999.0, 0.0, v1)
            v2 = np.where(v2 == -9999.0, 0.0, v2)
            v3 = np.where(v3 == -9999.0, 0.0, v3)
            v4 = np.where(v4 == -9999.0, 0.0, v4)

            # En m3/m3
            i1_vol += float(np.sum(v1 * w_norm))
            i2_vol += float(np.sum(v2 * w_norm))
            i3_vol += float(np.sum(v3 * w_norm))
            i4_vol += float(np.sum(v4 * w_norm))

    # Conversion en mm d'eau
    i1_mm = i1_vol * dz[0] * 1000.0
    i2_mm = i2_vol * dz[1] * 1000.0
    i3_mm = i3_vol * dz[2] * 1000.0
    i4_mm = i4_vol * dz[3] * 1000.0
    itot_mm = i1_mm + i2_mm + i3_mm + i4_mm

    return {
        "n_obs_assimilated": n_obs_assimilated,
        "mean_innovation_m3m3": round(mean_innov, 6),
        "incr_layer1_m3m3": round(i1_vol, 6),
        "incr_layer2_m3m3": round(i2_vol, 6),
        "incr_layer3_m3m3": round(i3_vol, 6),
        "incr_layer4_m3m3": round(i4_vol, 6),
        "incr_layer1_mm": round(i1_mm, 4),
        "incr_layer2_mm": round(i2_mm, 4),
        "incr_layer3_mm": round(i3_mm, 4),
        "incr_layer4_mm": round(i4_mm, 4),
        "incr_total_mm": round(itot_mm, 4)
    }

# 3c. Sur le bassin amont de Lalla Chafia
print("  Calcul pour le bassin amont de Lalla Chafia...")
records_3c = []

for exp in ["DA_nocdf", "DA_cdf"]:
    print(f"    Experience : {exp}")
    # Mensuel 2018
    for m in range(1, 13):
        res = analyze_innov_and_increments(exp, 2018, month=m, target_mask=masks_181["b_l_chafia"], target_weights=weights_181["b_l_chafia"])
        records_3c.append({
            "target": "Lalla Chafia",
            "experiment": exp,
            "period_type": "monthly_2018",
            "period": f"2018-{m:02d}",
            **res
        })
    # Annuel 2016-2020
    for yr in years:
        res = analyze_innov_and_increments(exp, yr, month=None, target_mask=masks_181["b_l_chafia"], target_weights=weights_181["b_l_chafia"])
        records_3c.append({
            "target": "Lalla Chafia",
            "experiment": exp,
            "period_type": "annual_2016_2020",
            "period": str(yr),
            **res
        })

df_3c = pd.DataFrame(records_3c)
out_3c_csv = os.path.join(TABLES_DIR, "lalla_chafia_innovations_and_increments.csv")
df_3c.to_csv(out_3c_csv, index=False)
print(f"[OK] Table 3c sauvee : {out_3c_csv}")

# 3d. Sur les 20 mailles du Top 20 (moyen sur les 20 mailles)
print("  Calcul pour les 20 mailles du Top 20...")
records_3d = []

for exp in ["DA_nocdf", "DA_cdf"]:
    print(f"    Experience : {exp}")
    # Mensuel 2018
    for m in range(1, 13):
        res = analyze_innov_and_increments(exp, 2018, month=m, target_mask=mask_top20_181, target_weights=w_top20_181)
        records_3d.append({
            "target": "Top20_Cells_Mean",
            "experiment": exp,
            "period_type": "monthly_2018",
            "period": f"2018-{m:02d}",
            **res
        })
    # Annuel 2016-2020
    for yr in years:
        res = analyze_innov_and_increments(exp, yr, month=None, target_mask=mask_top20_181, target_weights=w_top20_181)
        records_3d.append({
            "target": "Top20_Cells_Mean",
            "experiment": exp,
            "period_type": "annual_2016_2020",
            "period": str(yr),
            **res
        })

df_3d = pd.DataFrame(records_3d)
out_3d_csv = os.path.join(TABLES_DIR, "top20_cells_innovations_and_increments.csv")
df_3d.to_csv(out_3d_csv, index=False)
print(f"[OK] Table 3d sauvee : {out_3d_csv}")

print("\n>>> TOUTES LES TABLES DE FACTUAL COMPLEMENTS ONT ETE CALCULEES AVEC SUCCES.")
