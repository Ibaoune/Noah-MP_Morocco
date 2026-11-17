#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
compute_summer_water_balance.py
Calcule le bilan estival Qsb contre débit routé pour Lalla Chafia et Sidi Jabeur
sur Juin-Août 2018 et Juin-Septembre 2018 pour :
- SIMGM (Opt 1)
- SIMTOP (Opt 2)
- Schaake96 (Opt 3)
- BATS (Opt 4)
- OPL Historique (référence)
"""

import os
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

REPO = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_PATH = f"{REPO}/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"
PAIRING_CSV = f"{REPO}/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv"
OBS_CSV = f"{REPO}/data/streamflow_clean/obs_daily.csv"
INV_DIR = f"{REPO}/experiments/NorthMor/sensitivity_runoff_2018/_inventory"

# 1. Delimitation D8 des bassins versants amont
# Reprise exacte de evaluate_sebou_bouregreg.py (lignes 673-716)
ds_ldt = nc.Dataset(LDT_PATH)
grid_area = ds_ldt["HYMAP_grid_area"][:].filled(0.0)
flow_x = ds_ldt["HYMAP_flow_direction_x"][:]
flow_y = ds_ldt["HYMAP_flow_direction_y"][:]
R, C = flow_x.shape
ds_ldt.close()

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
            if (pr, pc) not in parents: parents[(pr, pc)] = []
            parents[(pr, pc)].append((r, c))

def get_catchment(orow, ocol):
    vis = set([(orow, ocol)])
    q = [(orow, ocol)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    return vis

# Stations cibles
df_pair = pd.read_csv(PAIRING_CSV)
target_stations = {
    'b_l_chafia': {
        'nom': 'Lalla Chafia',
        'row': int(df_pair[df_pair['station_id']=='b_l_chafia']['row_hymap'].iloc[0]),
        'col': int(df_pair[df_pair['station_id']=='b_l_chafia']['col_hymap'].iloc[0]),
        'area_km2': float(df_pair[df_pair['station_id']=='b_l_chafia']['aire_hymap_km2'].iloc[0])
    },
    'b_s_jabeur': {
        'nom': 'Sidi Jabeur',
        'row': int(df_pair[df_pair['station_id']=='b_s_jabeur']['row_hymap'].iloc[0]),
        'col': int(df_pair[df_pair['station_id']=='b_s_jabeur']['col_hymap'].iloc[0]),
        'area_km2': float(df_pair[df_pair['station_id']=='b_s_jabeur']['aire_hymap_km2'].iloc[0])
    }
}

catchments = {}
weights = {}
for sid, info in target_stations.items():
    cat = get_catchment(info['row'], info['col'])
    catchments[sid] = cat
    tot_a = sum(grid_area[cr, cc] for cr, cc in cat)
    w = np.zeros((R, C), dtype=float)
    for cr, cc in cat:
        w[cr, cc] = grid_area[cr, cc] / tot_a
    weights[sid] = w
    print(f"Station {sid} ({info['nom']}): {len(cat)} mailles D8, aire grille = {tot_a:.2f} km2, aire pairing = {info['area_km2']:.2f} km2")

# Schemes and paths
schemes = {
    'OL_R1_SIMGM': {
        'name': 'SIMGM (Opt 1)',
        'remap_dir': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R1_SIMGM/SURFACEMODEL",
        'q_sim_csv': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/outputs/OL_R1_SIMGM/streamflow_daily_stations.csv"
    },
    'OL_R2_SIMTOP': {
        'name': 'SIMTOP (Opt 2)',
        'remap_dir': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R2_SIMTOP/SURFACEMODEL",
        'q_sim_csv': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/outputs/OL_R2_SIMTOP/streamflow_daily_stations.csv"
    },
    'OL_R3_SCHAAKE96': {
        'name': 'Schaake96 (Opt 3)',
        'remap_dir': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R3_SCHAAKE96/SURFACEMODEL",
        'q_sim_csv': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/outputs/OL_R3_SCHAAKE96/streamflow_daily_stations.csv"
    },
    'OL_R4_BATS': {
        'name': 'BATS (Opt 4)',
        'remap_dir': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/remap_180x120/OL_R4_BATS/SURFACEMODEL",
        'q_sim_csv': f"{REPO}/experiments/NorthMor/opl_hydrology_sensitivity/routing/outputs/OL_R4_BATS/streamflow_daily_stations.csv"
    },
    'OPL_HIST': {
        'name': 'OPL Historique (linres=1)',
        'remap_dir': f"{REPO}/experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL",
        'q_sim_csv': f"{REPO}/experiments/NorthMor/routing/output/OPL_2016_2020_corrigee/t7_sim_daily_12stations_corrigee.csv"
    }
}

# Charger les observations ABH
df_obs = pd.read_csv(OBS_CSV)
df_obs['date_dt'] = pd.to_datetime(df_obs['date'])
df_obs['q_num'] = pd.to_numeric(df_obs['q_m3s'], errors='coerce')

# Charger les series simulees de debit
q_sim_data = {}
for sc_id, sc_info in schemes.items():
    df_q = pd.read_csv(sc_info['q_sim_csv'])
    df_q['date_dt'] = pd.to_datetime(df_q['date'])
    q_sim_data[sc_id] = df_q

# Extraire pour chaque jour de 2018 les flux Qs et Qsb amont
start_date = datetime.date(2018, 1, 1)
end_date = datetime.date(2018, 12, 31)

daily_records = {sid: {sc: [] for sc in schemes} for sid in target_stations}

cur = start_date
while cur <= end_date:
    ym = cur.strftime("%Y%m")
    ymd = cur.strftime("%Y%m%d")
    fname = f"LIS_HIST_{ymd}0000.d01.nc"
    dt_str = cur.strftime("%Y-%m-%d")
    
    for sc_id, sc_info in schemes.items():
        fpath = os.path.join(sc_info['remap_dir'], ym, fname)
        with nc.Dataset(fpath, "r") as ds:
            qs = ds["Qs_tavg"][:].squeeze()
            qsb = ds["Qsb_tavg"][:].squeeze()
            
        for sid, info in target_stations.items():
            w = weights[sid]
            # kg m-2 s-1 -> mm/day (86400)
            qs_mm_d = float(np.sum(qs * w) * 86400.0)
            qsb_mm_d = float(np.sum(qsb * w) * 86400.0)
            
            # Conversion en m3/s = mm/j * A[km2] / 86.4
            qs_m3s = qs_mm_d * info['area_km2'] / 86.4
            qsb_m3s = qsb_mm_d * info['area_km2'] / 86.4
            
            daily_records[sid][sc_id].append({
                'date': dt_str,
                'qs_mm_d': qs_mm_d,
                'qsb_mm_d': qsb_mm_d,
                'qs_m3s': qs_m3s,
                'qsb_m3s': qsb_m3s
            })
            
    cur += datetime.timedelta(days=1)

# Periodes estivales
periods = {
    'JJA_2018': ('2018-06-01', '2018-08-31', 'Juin–Août 2018 (92j)'),
    'JJAS_2018': ('2018-06-01', '2018-09-30', 'Juin–Septembre 2018 (122j)')
}

results = []

for per_id, (d_start, d_end, per_label) in periods.items():
    for sid, info in target_stations.items():
        st_name = info['nom']
        area = info['area_km2']
        
        # Observations ABH sur la periode
        sub_obs = df_obs[(df_obs['station_id'] == sid) & 
                         (df_obs['date'] >= d_start) & 
                         (df_obs['date'] <= d_end)]
        obs_mean = float(sub_obs['q_num'].mean())
        obs_median = float(sub_obs['q_num'].median())
        obs_count = int(sub_obs['q_num'].count())
        
        for sc_id, sc_info in schemes.items():
            sc_name = sc_info['name']
            
            # Flux journaliers
            df_flx = pd.DataFrame(daily_records[sid][sc_id])
            sub_flx = df_flx[(df_flx['date'] >= d_start) & (df_flx['date'] <= d_end)]
            
            qs_mm_mean = float(sub_flx['qs_mm_d'].mean())
            qs_mm_med = float(sub_flx['qs_mm_d'].median())
            qsb_mm_mean = float(sub_flx['qsb_mm_d'].mean())
            qsb_mm_med = float(sub_flx['qsb_mm_d'].median())
            
            qs_m3s_mean = float(sub_flx['qs_m3s'].mean())
            qs_m3s_med = float(sub_flx['qs_m3s'].median())
            qsb_m3s_mean = float(sub_flx['qsb_m3s'].mean())
            qsb_m3s_med = float(sub_flx['qsb_m3s'].median())
            
            # Debit route simule
            df_qsim = q_sim_data[sc_id]
            col_q = sid if sid in df_qsim.columns else [c for c in df_qsim.columns if sid in c][0]
            sub_qsim = df_qsim[(df_qsim['date'] >= d_start) & (df_qsim['date'] <= d_end)]
            qsim_mean = float(sub_qsim[col_q].mean())
            qsim_median = float(sub_qsim[col_q].median())
            
            results.append({
                'Periode': per_label,
                'Station_ID': sid,
                'Station_Nom': st_name,
                'Aire_km2': round(area, 2),
                'Schema_ID': sc_id,
                'Schema_Nom': sc_name,
                'Qs_mean_mm_j': round(qs_mm_mean, 4),
                'Qs_median_mm_j': round(qs_mm_med, 4),
                'Qs_mean_m3s': round(qs_m3s_mean, 3),
                'Qs_median_m3s': round(qs_m3s_med, 3),
                'Qsb_mean_mm_j': round(qsb_mm_mean, 4),
                'Qsb_median_mm_j': round(qsb_mm_med, 4),
                'Qsb_mean_m3s': round(qsb_m3s_mean, 3),
                'Qsb_median_m3s': round(qsb_m3s_med, 3),
                'Q_route_mean_m3s': round(qsim_mean, 3),
                'Q_route_median_m3s': round(qsim_median, 3),
                'Q_obs_mean_m3s': round(obs_mean, 3),
                'Q_obs_median_m3s': round(obs_median, 3),
                'N_obs': obs_count
            })

df_res = pd.DataFrame(results)
csv_out = f"{INV_DIR}/bilan_estival_qsb_debit_2018.csv"
md_out = f"{INV_DIR}/bilan_estival_qsb_debit_2018.md"

df_res.to_csv(csv_out, index=False)
print(f"Saved CSV: {csv_out}")

# Generer le tableau Markdown
with open(md_out, "w", encoding="utf-8") as f:
    f.write("# Bilan Estival Qs / Qsb contre Débit Routé et Observé (2018)\n\n")
    f.write("Délimitation amont : fonction `get_catchment` de `experiments/NorthMor/routing/scripts/evaluate_sebou_bouregreg.py` (lignes 699–708).\n")
    f.write("Superficies : `experiments/NorthMor/routing/stations/hymap_stations_pairing.csv` (Lalla Chafia: 3341.60 km², Sidi Jabeur: 3138.52 km²).\n")
    f.write("Conversion : $m^3/s = mm/j \\times A[km^2] / 86.4$.\n\n")
    f.write(df_res.to_markdown(index=False))
    f.write("\n")

print(f"Saved Markdown: {md_out}")
print("\n" + df_res[['Periode', 'Station_Nom', 'Schema_Nom', 'Qs_mean_m3s', 'Qsb_mean_m3s', 'Q_route_mean_m3s', 'Q_obs_mean_m3s']].to_string(index=False))
