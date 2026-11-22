# -*- coding: utf-8 -*-
"""
Calcul du bilan hydrique moyen mensuel 2018 sur les bassins versants amont reels
de Lalla Chafia et Sidi Jabeur pour les 6 experiences :
OPL, OL_DAIC, ENS_OPL, DA_nocdf, DA_cdf, DA_nocdf_nowilt.

Variables : P, ET, Qs, Qsb, Delta_S, Increments EnKF par couche (Layer 1 a 4 et Total).
"""
import os
import glob
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_FILE = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
TABLES_DIR = os.path.join(BASE_DIR, "paper1/tables")

# 1. Delimitation HyMAP D8
with nc.Dataset(LDT_FILE) as ds:
    area_180 = ds["HYMAP_grid_area"][:]
    flow_x = ds["HYMAP_flow_direction_x"][:]
    flow_y = ds["HYMAP_flow_direction_y"][:]

def get_catchment_cells(ldt_path, outlet_row, outlet_col):
    with nc.Dataset(ldt_path) as ds:
        flow_x = ds['HYMAP_flow_direction_x'][:]
        flow_y = ds['HYMAP_flow_direction_y'][:]
        area = ds['HYMAP_grid_area'][:].filled(0.0)
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
                if (pr, pc) not in parents:
                    parents[(pr, pc)] = []
                parents[(pr, pc)].append((r, c))

    vis = set([(outlet_row, outlet_col)])
    q = [(outlet_row, outlet_col)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis, area

cells_lalla, area_180 = get_catchment_cells(LDT_FILE, 75, 71)
cells_jabeur, _ = get_catchment_cells(LDT_FILE, 71, 71)

catchments = {
    "b_l_chafia": ("Lalla Chafia", cells_lalla),
    "b_s_jabeur": ("Sidi Jabeur", cells_jabeur)
}

# Masques et poids
masks_180 = {}
weights_180 = {}
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
        w181[r, c] += 0.25
        w181[r, c+1] += 0.25
        w181[r+1, c] += 0.25
        w181[r+1, c+1] += 0.25
    weights_181[cid] = w181 / np.sum(w181)

dz = np.array([0.1, 0.3, 0.6, 1.0])

# Repertoires des ruissellements remappes 180x120
REMAP_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"),
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OL_DAIC_2018/SURFACEMODEL"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_noirr_2016_2020/SURFACEMODEL"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_cdf_noirr_2016_2020/SURFACEMODEL"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_nowilt_2018/SURFACEMODEL"),
}

# Repertoires des sorties natives 181x121
NATIVE_DIRS = {
    "OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020"),
    "OL_DAIC": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018"),
    "ENS_OPL": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018"),
    "DA_nocdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020"),
    "DA_cdf": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020"),
    "DA_nocdf_nowilt": os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018"),
}

# Fonction pour trouver les fichiers natifs d'un mois donne
def get_native_files_month(exp, year, month):
    exp_dir = NATIVE_DIRS[exp]
    ym = f"{year}{month:02d}"
    m_label = f"{year}-{month:02d}"
    
    if exp in ["OPL", "DA_nocdf", "DA_cdf"]:
        d = os.path.join(exp_dir, f"output/{m_label}/SURFACEMODEL/{ym}")
        files = sorted(glob.glob(os.path.join(d, "LIS_HIST_*.d01.nc")))
        # Fichier du 1er jour du mois suivant
        next_m = month + 1 if month < 12 else 1
        next_y = year if month < 12 else year + 1
        next_m_label = f"{next_y}-{next_m:02d}"
        next_ym = f"{next_y}{next_m:02d}"
        f_last = os.path.join(exp_dir, f"output/{next_m_label}/SURFACEMODEL/{next_ym}/LIS_HIST_{next_ym}010000.d01.nc")
        if os.path.exists(f_last) and f_last not in files:
            files.append(f_last)
    else:
        d = os.path.join(exp_dir, f"output/SURFACEMODEL/{ym}")
        files = sorted(glob.glob(os.path.join(d, "LIS_HIST_*.d01.nc")))
        next_m = month + 1 if month < 12 else 1
        next_y = year if month < 12 else year + 1
        next_ym = f"{next_y}{next_m:02d}"
        f_last = os.path.join(exp_dir, f"output/SURFACEMODEL/{next_ym}/LIS_HIST_{next_ym}010000.d01.nc")
        if not os.path.exists(f_last) and month == 5:
            f_last = os.path.join(exp_dir, f"output/_partial_201806_hang/SURFACEMODEL_{next_ym}/LIS_HIST_{next_ym}010000.d01.nc")
        if os.path.exists(f_last) and f_last not in files:
            files.append(f_last)
            
    return files

# Initialisation du stockage de l'humidite du sol au 2018-01-01 00:00
initial_sm = {}
# Pour OPL et ENS_OPL : etat OPL
f_init_opl = os.path.join(NATIVE_DIRS["OPL"], "output/2017-12/SURFACEMODEL/201801/LIS_HIST_201801010000.d01.nc")
with nc.Dataset(f_init_opl) as ds:
    initial_sm["OPL"] = ds["SoilMoist_tavg"][:].squeeze()
    initial_sm["ENS_OPL"] = ds["SoilMoist_tavg"][:].squeeze()

# Pour DA_nocdf, DA_cdf, OL_DAIC, DA_nocdf_nowilt : etat DA_nocdf
f_init_da = os.path.join(NATIVE_DIRS["DA_nocdf"], "output/2017-12/SURFACEMODEL/201801/LIS_HIST_201801010000.d01.nc")
with nc.Dataset(f_init_da) as ds:
    sm_da_init = ds["SoilMoist_tavg"][:].squeeze()
    initial_sm["DA_nocdf"] = sm_da_init
    initial_sm["DA_cdf"] = sm_da_init
    initial_sm["OL_DAIC"] = sm_da_init
    initial_sm["DA_nocdf_nowilt"] = sm_da_init

# Fonction extraction increments EnKF
def get_enkf_increments_month(exp, year, month, w_181):
    if exp not in ["DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]:
        return (0.0, 0.0, 0.0, 0.0, 0.0)
    
    ym = f"{year}{month:02d}"
    m_label = f"{year}-{month:02d}"
    exp_dir = NATIVE_DIRS[exp]
    
    if exp == "DA_nocdf_nowilt":
        files = sorted(glob.glob(os.path.join(exp_dir, f"output/EnKF/{ym}/LIS_DA_EnKF_*_incr.*.nc")))
    else:
        files = sorted(glob.glob(os.path.join(exp_dir, f"output/{m_label}/EnKF/{ym}/LIS_DA_EnKF_*_incr.*.nc")))
        
    i1, i2, i3, i4 = 0.0, 0.0, 0.0, 0.0
    for f in files:
        with nc.Dataset(f) as ds:
            v1 = ds["anlys_incr_Soil Moisture Layer 1_01"][:].squeeze()
            v2 = ds["anlys_incr_Soil Moisture Layer 2_01"][:].squeeze()
            v3 = ds["anlys_incr_Soil Moisture Layer 3_01"][:].squeeze()
            v4 = ds["anlys_incr_Soil Moisture Layer 4_01"][:].squeeze()
            i1 += float(np.sum(v1 * w_181)) * dz[0] * 1000.0
            i2 += float(np.sum(v2 * w_181)) * dz[1] * 1000.0
            i3 += float(np.sum(v3 * w_181)) * dz[2] * 1000.0
            i4 += float(np.sum(v4 * w_181)) * dz[3] * 1000.0
    return (i1, i2, i3, i4, i1 + i2 + i3 + i4)

print(">>> Calcul du bilan complet mensuel 2018 sur Lalla Chafia et Sidi Jabeur...")

# Pre-calcul de P mensuel (identique pour toutes les experiences)
monthly_P = {}
for cid in catchments:
    w181 = weights_181[cid]
    p_months = []
    for m in range(1, 13):
        files_p = get_native_files_month("OPL", 2018, m)
        p_val = 0.0
        for f in files_p:
            with nc.Dataset(f) as ds:
                p_val += float(np.sum(ds["TotalPrecip_tavg"][:].squeeze() * 86400.0 * w181))
        p_months.append(p_val)
    monthly_P[cid] = p_months

# Etat courant de SoilMoist par exp
current_sm = {exp: initial_sm[exp].copy() for exp in REMAP_DIRS}

all_records = []
exps = ["OPL", "OL_DAIC", "ENS_OPL", "DA_nocdf", "DA_cdf", "DA_nocdf_nowilt"]

for m in range(1, 13):
    ym_str = f"2018-{m:02d}"
    print(f"  Mois {ym_str}...")
    
    for exp in exps:
        # Fichiers remappes pour Qs et Qsb
        r_dir = REMAP_DIRS[exp]
        ym_remap = f"2018{m:02d}"
        files_remap = sorted(glob.glob(os.path.join(r_dir, f"{ym_remap}/*.d01.nc")))
        next_m = m + 1 if m < 12 else 1
        next_y = 2018 if m < 12 else 2019
        next_ym = f"{next_y}{next_m:02d}"
        f_remap_last = os.path.join(r_dir, f"{next_ym}/LIS_HIST_{next_ym}010000.d01.nc")
        if os.path.exists(f_remap_last) and f_remap_last not in files_remap:
            files_remap.append(f_remap_last)

        # Calcul Qs et Qsb 180x120
        qs_grid = np.zeros((120, 180), dtype=float)
        qsb_grid = np.zeros((120, 180), dtype=float)
        for f in files_remap:
            fname = os.path.basename(f)
            if not fname.startswith("LIS_HIST_"):
                continue
            with nc.Dataset(f) as ds:
                qs_grid += np.squeeze(ds["Qs_tavg"][:]) * 86400.0
                qsb_grid += np.squeeze(ds["Qsb_tavg"][:]) * 86400.0

        # Fichiers natifs pour ET et fin de mois SoilMoist
        files_nat = get_native_files_month(exp, 2018, m)
        et_grid = np.zeros((121, 181), dtype=float)
        for f in files_nat:
            with nc.Dataset(f) as ds:
                et_grid += ds["Evap_tavg"][:].squeeze() * 86400.0
        
        # SoilMoist a la fin du mois
        f_last_month = files_nat[-1]
        with nc.Dataset(f_last_month) as ds:
            end_sm = ds["SoilMoist_tavg"][:].squeeze()

        # Delta S global par maille : sum_l (end_sm - current_sm) * dz * 1000
        delta_sm_grid = np.zeros((121, 181), dtype=float)
        for l in range(4):
            delta_sm_grid += (end_sm[l] - current_sm[exp][l]) * dz[l] * 1000.0

        for cid, (cname, _) in catchments.items():
            w180 = weights_180[cid]
            w181 = weights_181[cid]
            
            p_val = monthly_P[cid][m-1]
            qs_val = float(np.sum(qs_grid * w180))
            qsb_val = float(np.sum(qsb_grid * w180))
            et_val = float(np.sum(et_grid * w181))
            delta_s_val = float(np.sum(delta_sm_grid * w181))
            
            i1, i2, i3, i4, itot = get_enkf_increments_month(exp, 2018, m, w181)
            
            residual = p_val - et_val - (qs_val + qsb_val) + itot - delta_s_val
            
            all_records.append({
                "station": cname,
                "station_id": cid,
                "experiment": exp,
                "year_month": ym_str,
                "P_mm": p_val,
                "ET_mm": et_val,
                "Qs_mm": qs_val,
                "Qsb_mm": qsb_val,
                "TotalRunoff_mm": qs_val + qsb_val,
                "Delta_S_mm": delta_s_val,
                "Incr_Layer1_mm": i1,
                "Incr_Layer2_mm": i2,
                "Incr_Layer3_mm": i3,
                "Incr_Layer4_mm": i4,
                "Incr_Total_mm": itot,
                "WaterBalance_Residual_mm": residual
            })
            
        current_sm[exp] = end_sm.copy()

df_wb_full = pd.DataFrame(all_records)
out_csv = os.path.join(TABLES_DIR, "water_balance_upstream_catchments_2018.csv")
df_wb_full.to_csv(out_csv, index=False)
print(f"[OK] Table de bilan hydrique generee avec succes : {out_csv} ({len(df_wb_full)} lignes)")
