import os, sys, datetime
import netCDF4 as nc
import numpy as np
import pandas as pd

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SENS_DIR = f"{BASE_DIR}/experiments/NorthMor/opl_hydrology_sensitivity"
LDT_PATH = f"{BASE_DIR}/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"
OBS_CSV = f"{BASE_DIR}/data/streamflow_clean/obs_daily.csv"

SCHEMES = [
    ("OL_R1_SIMGM", "SIMGM (Ref)"),
    ("OL_R2_SIMTOP", "SIMTOP"),
    ("OL_R3_SCHAAKE96", "Schaake96"),
    ("OL_R4_BATS", "BATS")
]

STATIONS = {
    'b_l_chafia': {'name': 'Lalla Chafia', 'cell': (75, 71)},
    'b_s_jabeur': {'name': 'Sidi Jabeur', 'cell': (71, 71)}
}

# 1. Catchment delineation
with nc.Dataset(LDT_PATH) as ds:
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

st_weights = {}
st_areas = {}
for sid, sinfo in STATIONS.items():
    out_r, out_c = sinfo['cell']
    vis = set([(out_r, out_c)])
    q = [(out_r, out_c)]
    while q:
        curr = q.pop(0)
        if curr in parents:
            for p in parents[curr]:
                if p not in vis:
                    vis.add(p)
                    q.append(p)
    w = np.zeros_like(area)
    tot_area = sum(area[r, c] for r, c in vis)
    for r, c in vis:
        w[r, c] = area[r, c] / tot_area
    st_weights[sid] = w
    st_areas[sid] = tot_area / 1e6
    print(f"Station {sid} ({sinfo['name']}): {len(vis)} cellules, Superficie D8 = {st_areas[sid]:.2f} km²")

# 2. Daily P, Qs, Qsb extraction
dates_2018 = [datetime.date(2018, 1, 1) + datetime.timedelta(days=i) for i in range(365)]
flux_data = {exp_id: {sid: {'P': [], 'Qs': [], 'Qsb': []} for sid in STATIONS} for exp_id, _ in SCHEMES}

for exp_id, label in SCHEMES:
    noah_dir = f"{SENS_DIR}/experiments/{exp_id}/output"
    remap_dir = f"{SENS_DIR}/routing/runs/remap_180x120/{exp_id}/SURFACEMODEL"
    
    missing_count = 0
    for d in dates_2018:
        file_dt = d + datetime.timedelta(days=1)
        m_folder = d.strftime('%Y-%m')
        ym = file_dt.strftime('%Y%m')
        fname = f"LIS_HIST_{file_dt.strftime('%Y%m%d0000')}.d01.nc"
        
        noah_f = f"{noah_dir}/{m_folder}/SURFACEMODEL/{ym}/{fname}"
        remap_f = f"{remap_dir}/{ym}/{fname}"
        
        if not os.path.exists(noah_f):
            print(f"ERROR: Missing Noah-MP file: {noah_f}")
            missing_count += 1
            p_val = np.nan
        else:
            with nc.Dataset(noah_f, 'r') as ds:
                p_arr = ds['Rainf_f_tavg'][:]
                if p_arr.ndim == 3: p_arr = p_arr[0]
                p_rem = 0.25 * (p_arr[:-1, :-1] + p_arr[:-1, 1:] + p_arr[1:, :-1] + p_arr[1:, 1:])
                for sid in STATIONS:
                    flux_data[exp_id][sid]['P'].append(float(np.sum(p_rem * st_weights[sid]) * 86400.0))
                    
        with nc.Dataset(remap_f, 'r') as ds:
            qs_arr = ds['Qs_tavg'][:]
            qsb_arr = ds['Qsb_tavg'][:]
            if qs_arr.ndim == 3: qs_arr = qs_arr[0]
            if qsb_arr.ndim == 3: qsb_arr = qsb_arr[0]
            for sid in STATIONS:
                flux_data[exp_id][sid]['Qs'].append(float(np.sum(qs_arr * st_weights[sid]) * 86400.0))
                flux_data[exp_id][sid]['Qsb'].append(float(np.sum(qsb_arr * st_weights[sid]) * 86400.0))
                
    print(f"[{exp_id}] Extraction terminee (fichiers manquants: {missing_count}).")

# Verification de la precipitation identique entre les 4 schemas
print("\n" + "="*70)
print("VERIFICATION DES PRECIPITATIONS ANNUELLES ET MENSUELLES (mm)")
print("="*70)
for sid in STATIONS:
    print(f"\n--- Station: {STATIONS[sid]['name']} ---")
    for exp_id, label in SCHEMES:
        p_tot = sum(flux_data[exp_id][sid]['P'])
        print(f"  {label:16s}: Total P 2018 = {p_tot:.2f} mm")

# Verification mensuelle
df_p_test = pd.DataFrame({
    label: flux_data[exp_id]['b_l_chafia']['P'] for exp_id, label in SCHEMES
}, index=pd.date_range('2018-01-01', '2018-12-31'))
p_monthly = df_p_test.resample('M').sum()
print("\nCumuls mensuels de P à Lalla Chafia (comparaison 4 schémas) :")
print(p_monthly.round(2).to_string())

diff_p = (df_p_test.max(axis=1) - df_p_test.min(axis=1)).max()
print(f"\nEcart maximal de P journalier entre schemas: {diff_p:.6e} mm (Strictement identique: {diff_p < 1e-5})")
