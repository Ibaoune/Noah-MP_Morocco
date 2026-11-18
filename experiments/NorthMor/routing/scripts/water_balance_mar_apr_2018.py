#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic du bilan hydrique Noah-MP sur le bassin de Lalla Chafia (Mars et Avril 2018).
Évaluation des flux (P, ET, Qs, Qsb) et des stocks (Sol, Nappe, Canopée, Neige, TWS)
à partir des sorties OPL 2018 et des fichiers de redémarrage (Restarts).
"""

import os
import datetime
import netCDF4 as nc
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import shutil

# Chemins
project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
ldt_path = os.path.join(project_root, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
noah_base = os.path.join(project_root, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output")
out_table_dir = os.path.join(project_root, "experiments/NorthMor/routing/plots/sebou_bouregreg/tables")
out_fig_dir = os.path.join(project_root, "experiments/NorthMor/routing/plots/sebou_bouregreg/figures/forcing_runoff")
artifact_dir = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e"

os.makedirs(out_table_dir, exist_ok=True)
os.makedirs(out_fig_dir, exist_ok=True)

# 1. Géométrie Lalla Chafia
ds_ldt = nc.Dataset(ldt_path)
flow_x = ds_ldt['HYMAP_flow_direction_x'][:]
flow_y = ds_ldt['HYMAP_flow_direction_y'][:]
area = ds_ldt['HYMAP_grid_area'][:].filled(0.0)
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
            if (pr, pc) not in parents:
                parents[(pr, pc)] = []
            parents[(pr, pc)].append((r, c))

vis = set([(75, 71)])
q = [(75, 71)]
while q:
    curr = q.pop(0)
    if curr in parents:
        for p in parents[curr]:
            if p not in vis:
                vis.add(p)
                q.append(p)

cat = sorted(list(vis))
cat_rows = np.array([r for r, c in cat], dtype=np.int32)
cat_cols = np.array([c for r, c in cat], dtype=np.int32)
cat_areas = area[cat_rows, cat_cols]
tot_area_m2 = float(np.sum(cat_areas))

def remap_and_avg(var_2d):
    if var_2d.ndim == 3:
        var_2d = var_2d[0]
    v_rem = 0.25 * (var_2d[:-1, :-1] + var_2d[:-1, 1:] + var_2d[1:, :-1] + var_2d[1:, 1:])
    return float(np.sum(v_rem[cat_rows, cat_cols] * cat_areas) / tot_area_m2)

# 2. Extraction des Restarts aux bornes de mois
rst_files = {
    '2018-03-01': os.path.join(noah_base, '2018-02/SURFACEMODEL/201803/LIS_RST_NOAHMP401_201803010000.d01.nc'),
    '2018-04-01': os.path.join(noah_base, '2018-03/SURFACEMODEL/201804/LIS_RST_NOAHMP401_201804010000.d01.nc'),
    '2018-05-01': os.path.join(noah_base, '2018-04/SURFACEMODEL/201805/LIS_RST_NOAHMP401_201805010000.d01.nc')
}

dz = [0.1, 0.3, 0.6, 1.0]
rst_data = {}

for dt_str, fn in rst_files.items():
    ds_r = nc.Dataset(fn)
    lat_r = ds_r['lat'][:]
    lon_r = ds_r['lon'][:]
    r_idx = np.round((lat_r - 30.0) / 0.05).astype(int)
    c_idx = np.round((lon_r - (-10.0)) / 0.05).astype(int)
    
    grid_smc = np.zeros((4, 121, 181), dtype=np.float32)
    grid_can = np.zeros((121, 181), dtype=np.float32)
    grid_sneqv = np.zeros((121, 181), dtype=np.float32)
    grid_wa = np.zeros((121, 181), dtype=np.float32)
    grid_wt = np.zeros((121, 181), dtype=np.float32)
    grid_zwt = np.zeros((121, 181), dtype=np.float32)
    
    for l in range(4):
        grid_smc[l, r_idx, c_idx] = ds_r['SMC'][l, :]
    grid_can[r_idx, c_idx] = ds_r['CANWAT'][:]
    grid_sneqv[r_idx, c_idx] = ds_r['SNEQV'][:]
    grid_wa[r_idx, c_idx] = ds_r['WA'][:]
    grid_wt[r_idx, c_idx] = ds_r['WT'][:]
    grid_zwt[r_idx, c_idx] = ds_r['ZWT'][:]
    ds_r.close()
    
    smc_l = [remap_and_avg(grid_smc[l]) for l in range(4)]
    can_v = remap_and_avg(grid_can)
    swe_v = remap_and_avg(grid_sneqv)
    wa_v = remap_and_avg(grid_wa)
    wt_v = remap_and_avg(grid_wt)
    zwt_v = remap_and_avg(grid_zwt)
    s_soil = sum(dz[l] * smc_l[l] * 1000.0 for l in range(4))
    # Dans Noah-MP 4.0.1 sous LIS (NoahMP401_main.F90 ligne 1360) :
    # TWS = SWE + CanopInt + Soil moisture + WA
    # Note : comme ZWT > 2m partout, WA == WT numériquement (aucun horizon de sol saturé).
    tws_v = s_soil + can_v + swe_v + wa_v
    
    rst_data[dt_str] = {
        'smc_1': smc_l[0], 'smc_2': smc_l[1], 'smc_3': smc_l[2], 'smc_4': smc_l[3],
        's_soil_mm': s_soil, 'can_mm': can_v, 'swe_mm': swe_v,
        'wa_mm': wa_v, 'wt_mm': wt_v, 'zwt_m': zwt_v, 'tws_mm': tws_v
    }

# 3. Extraction des flux mensuels
def extract_flux_sums(start_date, end_date):
    curr = start_date
    sums = {'p': 0.0, 'rf': 0.0, 'sf': 0.0, 'et': 0.0, 'ec': 0.0, 'es': 0.0, 'tv': 0.0,
            'sub_s': 0.0, 'pet': 0.0, 'qs': 0.0, 'qsb': 0.0, 'qtot': 0.0, 'qsm': 0.0}
    while curr <= end_date:
        next_dt = curr + datetime.timedelta(days=1)
        fn = f"LIS_HIST_{next_dt.strftime('%Y%m%d0000')}.d01.nc"
        p_noah = os.path.join(noah_base, curr.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
        if not os.path.exists(p_noah):
            p_noah = os.path.join(noah_base, next_dt.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
            if not os.path.exists(p_noah):
                p_noah = os.path.join(noah_base, curr.strftime('%Y-%m'), 'SURFACEMODEL', curr.strftime('%Y%m'), fn)
        
        ds = nc.Dataset(p_noah)
        sums['p'] += remap_and_avg(ds['TotalPrecip_tavg'][:]) * 86400.0
        sums['rf'] += remap_and_avg(ds['Rainf_f_tavg'][:]) * 86400.0
        sums['sf'] += remap_and_avg(ds['Snowf_tavg'][:]) * 86400.0
        sums['et'] += remap_and_avg(ds['Evap_tavg'][:]) * 86400.0
        sums['ec'] += remap_and_avg(ds['ECanop_tavg'][:]) * 86400.0
        sums['es'] += remap_and_avg(ds['ESoil_tavg'][:]) * 86400.0
        sums['tv'] += remap_and_avg(ds['TVeg_tavg'][:]) * 86400.0
        sums['sub_s'] += remap_and_avg(ds['SubSnow_tavg'][:]) * 86400.0
        sums['pet'] += remap_and_avg(ds['PotEvap_tavg'][:]) * 86400.0
        sums['qs'] += remap_and_avg(ds['Qs_tavg'][:]) * 86400.0
        sums['qsb'] += remap_and_avg(ds['Qsb_tavg'][:]) * 86400.0
        sums['qtot'] += (remap_and_avg(ds['Qs_tavg'][:]) + remap_and_avg(ds['Qsb_tavg'][:])) * 86400.0
        sums['qsm'] += remap_and_avg(ds['Qsm_tavg'][:]) * 86400.0
        ds.close()
        curr += datetime.timedelta(days=1)
    return sums

flux_mar = extract_flux_sums(datetime.date(2018, 3, 1), datetime.date(2018, 3, 31))
flux_apr = extract_flux_sums(datetime.date(2018, 4, 1), datetime.date(2018, 4, 30))

# Observations ABH pour contexte
df_fluxes = pd.read_csv(os.path.join(out_table_dir, "lalla_chafia_fluxes_2018.csv"))
df_fluxes['date'] = pd.to_datetime(df_fluxes['date'])
q_obs_mar = float(df_fluxes[df_fluxes['date'].dt.month == 3]['q_obs_m3s'].sum() * 86400.0 / (tot_area_m2) * 1000.0)
q_obs_apr = float(df_fluxes[df_fluxes['date'].dt.month == 4]['q_obs_m3s'].sum() * 86400.0 / (tot_area_m2) * 1000.0)

# Assemblage du tableau comparatif
months = [
    {
        'mois': 'Mars 2018',
        'start_date': '2018-03-01',
        'end_date': '2018-03-31',
        'days': 31,
        'flux': flux_mar,
        'st_start': rst_data['2018-03-01'],
        'st_end': rst_data['2018-04-01'],
        'q_obs_mm': q_obs_mar
    },
    {
        'mois': 'Avril 2018',
        'start_date': '2018-04-01',
        'end_date': '2018-04-30',
        'days': 30,
        'flux': flux_apr,
        'st_start': rst_data['2018-04-01'],
        'st_end': rst_data['2018-05-01'],
        'q_obs_mm': q_obs_apr
    }
]

table_rows = []
for m in months:
    f = m['flux']
    s1 = m['st_start']
    s2 = m['st_end']
    
    ds_soil = s2['s_soil_mm'] - s1['s_soil_mm']
    ds_can = s2['can_mm'] - s1['can_mm']
    ds_swe = s2['swe_mm'] - s1['swe_mm']
    ds_wa = s2['wa_mm'] - s1['wa_mm']
    ds_wt = s2['wt_mm'] - s1['wt_mm']
    ds_tws = s2['tws_mm'] - s1['tws_mm']
    
    flux_out = f['et'] + f['qs'] + f['qsb']
    net_inflow = f['p'] - flux_out
    residu = net_inflow - ds_tws
    
    table_rows.append({
        'mois': m['mois'],
        'jours': m['days'],
        'P_mm': round(f['p'], 2),
        'ET_mm': round(f['et'], 2),
        'E_canop_mm': round(f['ec'], 2),
        'E_soil_mm': round(f['es'], 2),
        'T_veg_mm': round(f['tv'], 2),
        'PotEvap_mm': round(f['pet'], 2),
        'Qs_mm': round(f['qs'], 2),
        'Qsb_mm': round(f['qsb'], 2),
        'Qtot_sim_mm': round(f['qtot'], 2),
        'Qobs_ABH_mm': round(m['q_obs_mm'], 2),
        'theta1_ini_m3m3': round(s1['smc_1'], 4),
        'theta2_ini_m3m3': round(s1['smc_2'], 4),
        'theta3_ini_m3m3': round(s1['smc_3'], 4),
        'theta4_ini_m3m3': round(s1['smc_4'], 4),
        'S_soil_ini_mm': round(s1['s_soil_mm'], 2),
        'S_soil_end_mm': round(s2['s_soil_mm'], 2),
        'delta_S_soil_mm': round(ds_soil, 2),
        'delta_Can_mm': round(ds_can, 2),
        'delta_SWE_mm': round(ds_swe, 2),
        'delta_WA_aquifer_mm': round(ds_wa, 2),
        'delta_WT_mm': round(ds_wt, 2),
        'delta_TWS_mm': round(ds_tws, 2),
        'residu_fermeture_mm': round(residu, 2),
        'taux_fermeture_pct': round((1.0 - abs(residu)/f['p']) * 100.0, 2),
        'ratio_Qs_Qtot_pct': round(f['qs'] / f['qtot'] * 100.0, 1),
        'ratio_Qtot_P_pct': round(f['qtot'] / f['p'] * 100.0, 1),
        'ratio_Qobs_P_pct': round(m['q_obs_mm'] / f['p'] * 100.0, 1),
        'ratio_ET_P_pct': round(f['et'] / f['p'] * 100.0, 1),
        'ratio_deltaTWS_P_pct': round(ds_tws / f['p'] * 100.0, 1)
    })

df_out = pd.DataFrame(table_rows)
csv_wb_path = os.path.join(out_table_dir, "water_balance_lalla_chafia_mar_apr_2018.csv")
df_out.to_csv(csv_wb_path, index=False)
print(f"[OK] Table de bilan hydrique enregistree : {csv_wb_path}")

# 4. Production de la figure comparative
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'font.size': 10,
    'axes.labelsize': 10.5,
    'axes.titlesize': 11,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

fig, axes = plt.subplots(1, 3, figsize=(16, 5.2))
fig.subplots_adjust(top=0.86, bottom=0.14, left=0.07, right=0.96, wspace=0.28)

# Panneau A : Flux principaux et Partition (P vs ET vs Qs vs Qsb)
ax = axes[0]
categories = ['Précip. P', 'Évapo. ET', 'Ruiss. Qs', 'Drain. Qsb', 'Apport Qtot', 'Obs. Qobs']
x = np.arange(len(categories))
width = 0.35

v_mar = [df_out.loc[0, 'P_mm'], df_out.loc[0, 'ET_mm'], df_out.loc[0, 'Qs_mm'], df_out.loc[0, 'Qsb_mm'], df_out.loc[0, 'Qtot_sim_mm'], df_out.loc[0, 'Qobs_ABH_mm']]
v_apr = [df_out.loc[1, 'P_mm'], df_out.loc[1, 'ET_mm'], df_out.loc[1, 'Qs_mm'], df_out.loc[1, 'Qsb_mm'], df_out.loc[1, 'Qtot_sim_mm'], df_out.loc[1, 'Qobs_ABH_mm']]

rects1 = ax.bar(x - width/2, v_mar, width, label='Mars 2018 (31 j)', color='#1f77b4', alpha=0.88, edgecolor='#08519c')
rects2 = ax.bar(x + width/2, v_apr, width, label='Avril 2018 (30 j)', color='#ff7f0e', alpha=0.88, edgecolor='#d94701')

ax.set_ylabel('Lame d\'eau équivalente (mm)', fontweight='bold')
ax.set_title('(a) Flux hydrologiques mensuels', fontweight='bold', pad=8)
ax.set_xticks(x)
ax.set_xticklabels(categories, rotation=25, ha='right')
ax.legend(loc='upper right', framealpha=0.9)
ax.set_ylim(0, 175)

for rect in rects1:
    h = rect.get_height()
    ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=8)
for rect in rects2:
    h = rect.get_height()
    ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, 2), textcoords="offset points", ha='center', va='bottom', fontsize=8)

# Panneau B : Décomposition de l'Évapotranspiration et Variations de Stocks
ax = axes[1]
cats_et_s = ['Intercep. Ec', 'Sol nu Es', 'Transpir. Tv', 'ΔS Sol', 'ΔS Aquifère (WA)', 'ΔTWS']
x2 = np.arange(len(cats_et_s))

v_mar_s = [df_out.loc[0, 'E_canop_mm'], df_out.loc[0, 'E_soil_mm'], df_out.loc[0, 'T_veg_mm'],
           df_out.loc[0, 'delta_S_soil_mm'], df_out.loc[0, 'delta_WA_aquifer_mm'], df_out.loc[0, 'delta_TWS_mm']]
v_apr_s = [df_out.loc[1, 'E_canop_mm'], df_out.loc[1, 'E_soil_mm'], df_out.loc[1, 'T_veg_mm'],
           df_out.loc[1, 'delta_S_soil_mm'], df_out.loc[1, 'delta_WA_aquifer_mm'], df_out.loc[1, 'delta_TWS_mm']]

rects21 = ax.bar(x2 - width/2, v_mar_s, width, label='Mars 2018', color='#1f77b4', alpha=0.88, edgecolor='#08519c')
rects22 = ax.bar(x2 + width/2, v_apr_s, width, label='Avril 2018', color='#ff7f0e', alpha=0.88, edgecolor='#d94701')

ax.axhline(0, color='black', linewidth=0.8, linestyle='-')
ax.set_ylabel('Lame ou Variation de stock (mm)', fontweight='bold')
ax.set_title('(b) Composantes ET & Variations de stocks (ΔS)', fontweight='bold', pad=8)
ax.set_xticks(x2)
ax.set_xticklabels(cats_et_s, rotation=25, ha='right')
ax.set_ylim(-15, 75)
ax.legend(loc='upper right', framealpha=0.9)

for rect in rects21:
    h = rect.get_height()
    va = 'bottom' if h >= 0 else 'top'
    yoff = 2 if h >= 0 else -2
    ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, yoff), textcoords="offset points", ha='center', va=va, fontsize=8)
for rect in rects22:
    h = rect.get_height()
    va = 'bottom' if h >= 0 else 'top'
    yoff = 2 if h >= 0 else -2
    ax.annotate(f'{h:.1f}', xy=(rect.get_x() + rect.get_width()/2, h),
                xytext=(0, yoff), textcoords="offset points", ha='center', va=va, fontsize=8)

# Panneau C : Profil vertical d'humidité initiale du sol (Restarts)
ax = axes[2]
layers = ['L1 (0–10 cm)', 'L2 (10–40 cm)', 'L3 (40–100 cm)', 'L4 (100–200 cm)']
y_pos = np.arange(len(layers))

th_mar = [df_out.loc[0, f'theta{l}_ini_m3m3'] for l in [1, 2, 3, 4]]
th_apr = [df_out.loc[1, f'theta{l}_ini_m3m3'] for l in [1, 2, 3, 4]]
th_may = [rst_data['2018-05-01'][f'smc_{l}'] for l in [1, 2, 3, 4]]

h_bar = 0.25
ax.barh(y_pos + h_bar, th_mar, height=h_bar, label='01/03/2018 (État initial Mars)', color='#2ca02c', alpha=0.85, edgecolor='#1b7837')
ax.barh(y_pos, th_apr, height=h_bar, label='01/04/2018 (État initial Avril)', color='#1f77b4', alpha=0.85, edgecolor='#08519c')
ax.barh(y_pos - h_bar, th_may, height=h_bar, label='01/05/2018 (Fin Avril)', color='#ff7f0e', alpha=0.85, edgecolor='#d94701')

ax.set_yticks(y_pos)
ax.set_yticklabels(layers)
ax.invert_yaxis()  # Surface en haut
ax.set_xlabel('Teneur en eau volumique $\\theta$ (m³/m³)', fontweight='bold')
ax.set_title('(c) Profils de sol initiaux aux Restarts', fontweight='bold', pad=8)
ax.set_xlim(0, 0.40)
ax.legend(loc='lower right', framealpha=0.9, fontsize=8.2)

fig.suptitle("Diagnostic du bilan hydrique Noah-MP à Lalla Chafia : Comparaison Mars vs Avril 2018\n"
             "Analyse de la partition de l'eau, de la variation du stockage de l'aquifère et des conditions initiales de sol",
             fontweight='bold', y=0.98)

png_path = os.path.join(out_fig_dir, "water_balance_lalla_chafia_mar_apr_2018.png")
pdf_path = os.path.join(out_fig_dir, "water_balance_lalla_chafia_mar_apr_2018.pdf")
plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
plt.close()

if os.path.exists(artifact_dir):
    art_path = os.path.join(artifact_dir, "water_balance_lalla_chafia_mar_apr_2018.png")
    shutil.copy2(png_path, art_path)
    print(f"[OK] Figure copiee vers artefacts : {art_path}")

print("[OK] Script de diagnostic du bilan hydrique termine avec succes.")
