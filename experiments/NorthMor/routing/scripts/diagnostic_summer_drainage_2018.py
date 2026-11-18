#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic du drainage souterrain estival Noah-MP 4.0.1 (SIMGM) à Lalla Chafia :
Analyse de la période 1er mai au 30 novembre 2018 (focus juin-septembre).
Évaluation de l'aquifère (WA, ZWT), de la décharge souterraine (Qsb = QDIS),
de la recharge nette estimée (QIN = Delta_WA + Qsb) et des débits routés (linres=1 vs linres=0 vs ABH).
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

project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
ldt_path = os.path.join(project_root, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
noah_base = os.path.join(project_root, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output")
csv_flux_path = os.path.join(project_root, "experiments/NorthMor/routing/plots/sebou_bouregreg/tables/lalla_chafia_fluxes_2018.csv")
out_table_dir = os.path.join(project_root, "experiments/NorthMor/routing/plots/sebou_bouregreg/tables")
out_fig_dir = os.path.join(project_root, "experiments/NorthMor/routing/plots/sebou_bouregreg/figures/forcing_runoff")
artifact_dir = "/home/mohammad.elaabaribao/.gemini/antigravity-ide/brain/617ae310-cb70-490f-af94-9e341785512e"

os.makedirs(out_table_dir, exist_ok=True)
os.makedirs(out_fig_dir, exist_ok=True)

# 1. Masque amont Lalla Chafia (133 cellules, 3333.35 km²)
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

def remap_2d(var_2d):
    if var_2d.ndim == 3:
        var_2d = var_2d[0]
    return 0.25 * (var_2d[:-1, :-1] + var_2d[:-1, 1:] + var_2d[1:, :-1] + var_2d[1:, 1:])

def remap_and_avg(var_2d):
    v_rem = remap_2d(var_2d)
    return float(np.sum(v_rem[cat_rows, cat_cols] * cat_areas) / tot_area_m2)

# 2. Lecture des flux et débits journaliers de référence
df_flux = pd.read_csv(csv_flux_path)
df_flux['date'] = pd.to_datetime(df_flux['date'])
df_flux.set_index('date', inplace=True)

start_date = datetime.date(2018, 5, 1)
end_date = datetime.date(2018, 11, 30)

dz = [0.1, 0.3, 0.6, 1.0]
records = []
curr = start_date

while curr <= end_date:
    next_dt = curr + datetime.timedelta(days=1)
    fn = f"LIS_HIST_{next_dt.strftime('%Y%m%d0000')}.d01.nc"
    p_noah = os.path.join(noah_base, curr.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
    if not os.path.exists(p_noah):
        p_noah = os.path.join(noah_base, next_dt.strftime('%Y-%m'), 'SURFACEMODEL', next_dt.strftime('%Y%m'), fn)
        if not os.path.exists(p_noah):
            p_noah = os.path.join(noah_base, curr.strftime('%Y-%m'), 'SURFACEMODEL', curr.strftime('%Y%m'), fn)
    
    ds = nc.Dataset(p_noah)
    p_val = remap_and_avg(ds['TotalPrecip_tavg'][:]) * 86400.0
    qs_val = remap_and_avg(ds['Qs_tavg'][:]) * 86400.0
    qsb_val = remap_and_avg(ds['Qsb_tavg'][:]) * 86400.0
    et_val = remap_and_avg(ds['Evap_tavg'][:]) * 86400.0
    
    smc_vals = [remap_and_avg(ds['SoilMoist_tavg'][l]) for l in range(4)]
    s_soil = sum(dz[l] * smc_vals[l] * 1000.0 for l in range(4))
    
    can_val = remap_and_avg(ds['CanopInt_tavg'][:]) if 'CanopInt_tavg' in ds.variables else 0.0
    swe_val = remap_and_avg(ds['SWE_tavg'][:]) if 'SWE_tavg' in ds.variables else 0.0
    tws_val = remap_and_avg(ds['TWS_tavg'][:])
    wa_val = tws_val - (s_soil + can_val + swe_val)
    
    zwt_rem = remap_2d(ds['WaterTableD_tavg'][:])
    zwt_cells = zwt_rem[cat_rows, cat_cols]
    zwt_val = float(np.sum(zwt_cells * cat_areas) / tot_area_m2)
    ds.close()
    
    dt_pd = pd.to_datetime(curr)
    q_sim_hist = float(df_flux.loc[dt_pd, 'q_sim_hist_m3s']) if dt_pd in df_flux.index else np.nan
    q_sim_lin0 = float(df_flux.loc[dt_pd, 'q_sim_linres0_m3s']) if dt_pd in df_flux.index else np.nan
    q_obs = float(df_flux.loc[dt_pd, 'q_obs_m3s']) if dt_pd in df_flux.index else np.nan
    
    records.append({
        'date': curr.strftime('%Y-%m-%d'),
        'P_mm_d': round(p_val, 3),
        'ET_mm_d': round(et_val, 3),
        'Qs_mm_d': round(qs_val, 4),
        'Qsb_mm_d': round(qsb_val, 4),
        'Qtot_sim_mm_d': round(qs_val + qsb_val, 4),
        'theta_1_m3m3': round(smc_vals[0], 4),
        'theta_2_m3m3': round(smc_vals[1], 4),
        'theta_3_m3m3': round(smc_vals[2], 4),
        'theta_4_m3m3': round(smc_vals[3], 4),
        'S_soil_mm': round(s_soil, 2),
        'ZWT_m': round(zwt_val, 3),
        'WA_mm': round(wa_val, 2),
        'TWS_mm': round(tws_val, 2),
        'Qsim_hist_linres1_m3s': round(q_sim_hist, 2),
        'Qsim_recent_linres0_m3s': round(q_sim_lin0, 2),
        'Qobs_ABH_m3s': round(q_obs, 2)
    })
    curr += datetime.timedelta(days=1)

df_daily = pd.DataFrame(records)
csv_daily_path = os.path.join(out_table_dir, "daily_summer_drainage_lalla_chafia_2018.csv")
df_daily.to_csv(csv_daily_path, index=False)
print(f"[OK] CSV journalier enregistre : {csv_daily_path}")

# 3. Lecture des Restarts mensuels (01/05, 01/06, ..., 01/12)
rst_dates = [
    '2018-05-01', '2018-06-01', '2018-07-01', '2018-08-01',
    '2018-09-01', '2018-10-01', '2018-11-01', '2018-12-01'
]
rst_vals = {}

for dt_str in rst_dates:
    dt = datetime.datetime.strptime(dt_str, '%Y-%m-%d')
    prev_m = (dt - datetime.timedelta(days=1)).strftime('%Y-%m')
    curr_m = dt.strftime('%Y%m')
    fn = f"LIS_RST_NOAHMP401_{dt.strftime('%Y%m%d0000')}.d01.nc"
    p = os.path.join(noah_base, prev_m, 'SURFACEMODEL', curr_m, fn)
    ds = nc.Dataset(p)
    lat_r = ds['lat'][:]
    lon_r = ds['lon'][:]
    r_idx = np.round((lat_r - 30.0) / 0.05).astype(int)
    c_idx = np.round((lon_r - (-10.0)) / 0.05).astype(int)
    
    grid_wa = np.zeros((121, 181), dtype=np.float32)
    grid_zwt = np.zeros((121, 181), dtype=np.float32)
    grid_smc = np.zeros((4, 121, 181), dtype=np.float32)
    for l in range(4):
        grid_smc[l, r_idx, c_idx] = ds['SMC'][l, :]
    grid_wa[r_idx, c_idx] = ds['WA'][:]
    grid_zwt[r_idx, c_idx] = ds['ZWT'][:]
    grid_can = np.zeros((121, 181), dtype=np.float32)
    grid_sneqv = np.zeros((121, 181), dtype=np.float32)
    grid_can[r_idx, c_idx] = ds['CANWAT'][:]
    grid_sneqv[r_idx, c_idx] = ds['SNEQV'][:]
    ds.close()
    
    wa_v = remap_and_avg(grid_wa)
    zwt_v = remap_and_avg(grid_zwt)
    can_v = remap_and_avg(grid_can)
    swe_v = remap_and_avg(grid_sneqv)
    smc_l = [remap_and_avg(grid_smc[l]) for l in range(4)]
    s_soil = sum(dz[l] * smc_l[l] * 1000.0 for l in range(4))
    tws_v = s_soil + can_v + swe_v + wa_v
    
    rst_vals[dt_str] = {
        'wa_mm': wa_v, 'zwt_m': zwt_v, 'can_mm': can_v, 'swe_mm': swe_v,
        's_soil_mm': s_soil, 'tws_mm': tws_v
    }

# 4. Assemblage du tableau mensuel et calcul du bilan SIMGM : QIN = Delta_WA + Qsb
months_info = [
    ('Mai 2018', '2018-05-01', '2018-05-31', '2018-05-01', '2018-06-01'),
    ('Juin 2018', '2018-06-01', '2018-06-30', '2018-06-01', '2018-07-01'),
    ('Juillet 2018', '2018-07-01', '2018-07-31', '2018-07-01', '2018-08-01'),
    ('Août 2018', '2018-08-01', '2018-08-31', '2018-08-01', '2018-09-01'),
    ('Septembre 2018', '2018-09-01', '2018-09-30', '2018-09-01', '2018-10-01'),
    ('Octobre 2018', '2018-10-01', '2018-10-31', '2018-10-01', '2018-11-01'),
    ('Novembre 2018', '2018-11-01', '2018-11-30', '2018-11-01', '2018-12-01'),
]

monthly_rows = []
for m_label, d_ini, d_end, rst1, rst2 in months_info:
    sub = df_daily[(df_daily['date'] >= d_ini) & (df_daily['date'] <= d_end)]
    p_m = sub['P_mm_d'].sum()
    et_m = sub['ET_mm_d'].sum()
    qs_m = sub['Qs_mm_d'].sum()
    qsb_m = sub['Qsb_mm_d'].sum()
    qtot_m = sub['Qtot_sim_mm_d'].sum()
    
    s_ini = rst_vals[rst1]['s_soil_mm']
    s_fin = rst_vals[rst2]['s_soil_mm']
    d_soil = s_fin - s_ini
    d_wa = rst_vals[rst2]['wa_mm'] - rst_vals[rst1]['wa_mm']
    d_tws = rst_vals[rst2]['tws_mm'] - rst_vals[rst1]['tws_mm']
    d_zwt = rst_vals[rst2]['zwt_m'] - rst_vals[rst1]['zwt_m']
    
    # Bilan de réservoir SIMGM : Delta_WA = QIN - QDIS => QIN = Delta_WA + Qsb (car QDIS == Qsb)
    qin_est = d_wa + qsb_m
    
    # Résidu du bilan hydrique total : P - (ET + Qs + Qsb) - Delta_TWS
    flux_out = et_m + qs_m + qsb_m
    residu = (p_m - flux_out) - d_tws
    
    qobs_mean = sub['Qobs_ABH_m3s'].mean()
    qobs_mm = sub['Qobs_ABH_m3s'].sum() * 86400.0 / tot_area_m2 * 1000.0
    
    qsim_h_mean = sub['Qsim_hist_linres1_m3s'].mean()
    qsim_h_mm = sub['Qsim_hist_linres1_m3s'].sum() * 86400.0 / tot_area_m2 * 1000.0
    
    qsim_0_mean = sub['Qsim_recent_linres0_m3s'].mean()
    qsim_0_mm = sub['Qsim_recent_linres0_m3s'].sum() * 86400.0 / tot_area_m2 * 1000.0
    
    monthly_rows.append({
        'mois': m_label,
        'P_mm': round(p_m, 2),
        'ET_mm': round(et_m, 2),
        'Qs_mm': round(qs_m, 2),
        'Qsb_mm': round(qsb_m, 2),
        'Qtot_sim_mm': round(qtot_m, 2),
        'S_soil_ini_mm': round(s_ini, 2),
        'S_soil_fin_mm': round(s_fin, 2),
        'delta_S_soil_mm': round(d_soil, 2),
        'WA_ini_mm': round(rst_vals[rst1]['wa_mm'], 2),
        'WA_fin_mm': round(rst_vals[rst2]['wa_mm'], 2),
        'delta_WA_mm': round(d_wa, 2),
        'delta_TWS_mm': round(d_tws, 2),
        'QIN_estime_mm': round(qin_est, 2),
        'residu_fermeture_mm': round(residu, 2),
        'ZWT_ini_m': round(rst_vals[rst1]['zwt_m'], 3),
        'ZWT_fin_m': round(rst_vals[rst2]['zwt_m'], 3),
        'delta_ZWT_m': round(d_zwt, 3),
        'Qobs_m3s': round(qobs_mean, 2),
        'Qobs_mm': round(qobs_mm, 2),
        'Qsim_linres1_m3s': round(qsim_h_mean, 2),
        'Qsim_linres1_mm': round(qsim_h_mm, 2),
        'Qsim_linres0_m3s': round(qsim_0_mean, 2),
        'Qsim_linres0_mm': round(qsim_0_mm, 2)
    })

df_monthly = pd.DataFrame(monthly_rows)
csv_monthly_path = os.path.join(out_table_dir, "monthly_summer_drainage_lalla_chafia_2018.csv")
df_monthly.to_csv(csv_monthly_path, index=False)
print(f"[OK] Tableau mensuel enregistre : {csv_monthly_path}")

# 5. Figure synthétique à trois panneaux
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'font.size': 9.5,
    'axes.labelsize': 10,
    'axes.titlesize': 10.5,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

fig, axes = plt.subplots(3, 1, figsize=(14, 10.5), sharex=True)
fig.subplots_adjust(top=0.91, bottom=0.07, left=0.08, right=0.92, hspace=0.25)

x_dates = pd.to_datetime(df_daily['date']).values

# Panneau 1 : Précipitations et Ruissellement produit (Qs vs Qsb)
ax1 = axes[0]
ax1.bar(x_dates, df_daily['P_mm_d'].values, width=1.0, label='Précipitations P', color='#1f77b4', alpha=0.7)
ax1.plot(x_dates, df_daily['Qs_mm_d'].values, label='Ruissellement de surface Qs', color='#d62728', linewidth=1.5)
ax1.plot(x_dates, df_daily['Qsb_mm_d'].values, label='Drainage souterrain Qsb (QDIS)', color='#9467bd', linewidth=1.8)
ax1.set_ylabel('Flux journalier (mm/jour)', fontweight='bold')
ax1.set_title('(a) Forçage pluviométrique et production de flux Noah-MP (Qs vs Qsb)', pad=6, fontweight='bold')
ax1.set_ylim(0, 45)
ax1.legend(loc='upper right', framealpha=0.9, fontsize=8.8)

# Panneau 2 : Stockage d'aquifère WA et Profondeur de nappe ZWT
ax2 = axes[1]
line_wa = ax2.plot(x_dates, df_daily['WA_mm'].values, color='#2ca02c', linewidth=2.0, label='Stock d\'aquifère WA (diagnostic journalier)')
ax2.set_ylabel('Stock d\'aquifère WA (mm)', fontweight='bold', color='#1b7837')
ax2.set_ylim(4825, 4860)
ax2.tick_params(axis='y', labelcolor='#1b7837')

# Axe jumeau pour ZWT
ax2_twin = ax2.twinx()
line_zwt = ax2_twin.plot(x_dates, df_daily['ZWT_m'].values, color='#000000', linestyle='--', linewidth=1.8, label='Profondeur de nappe ZWT (m)')
ax2_twin.set_ylabel('Profondeur nappe ZWT (m)', fontweight='bold', color='black')
ax2_twin.set_ylim(2.88, 2.70)  # Inversé : surface du sol en haut
ax2_twin.grid(False)

# Marqueurs des restarts mensuels
rst_dt = [pd.to_datetime(d).to_datetime64() for d in rst_dates]
rst_wa = [rst_vals[d]['wa_mm'] for d in rst_dates]
sc_rst = ax2.scatter(rst_dt, rst_wa, color='#d95f02', s=45, zorder=6, label='Restarts mensuels (état instantané 00:00 UTC)')

lines = line_wa + line_zwt + [sc_rst]
labels = [l.get_label() for l in lines]
ax2.legend(lines, labels, loc='lower left', framealpha=0.9, fontsize=8.5)
ax2.set_title('(b) Évolution du réservoir souterrain (WA et ZWT) et repères des restarts mensuels', pad=6, fontweight='bold')

# Panneau 3 : Débits observés vs HyMAP linres=1 vs HyMAP linres=0
ax3 = axes[2]
ax3.plot(x_dates, df_daily['Qobs_ABH_m3s'].values, label='Observations ABH (Lalla Chafia)', color='#000000', linewidth=2.0, zorder=5)
ax3.plot(x_dates, df_daily['Qsim_hist_linres1_m3s'].values, label='HyMAP-2 linres=1 (historique avec réservoir)', color='#1f77b4', linewidth=1.8, zorder=4)
ax3.plot(x_dates, df_daily['Qsim_recent_linres0_m3s'].values, label='HyMAP-2 linres=0 (récent sans réservoir)', color='#d62728', linestyle='--', linewidth=1.8, zorder=4)
ax3.set_ylabel('Débit à l\'exutoire (m³/s)', fontweight='bold')
ax3.set_title('(c) Débit à l\'exutoire : Observations ABH vs Routages HyMAP (linres=1 vs linres=0)', pad=6, fontweight='bold')
ax3.set_ylim(0, 50)
ax3.legend(loc='upper right', framealpha=0.9, fontsize=8.8)

# Mise en évidence de la saison sèche estivale (Juin-Septembre)
for ax in [ax1, ax2, ax3]:
    ax.axvspan(pd.to_datetime('2018-06-01'), pd.to_datetime('2018-09-30'), color='#ffffbf', alpha=0.25, label='_nolegend_')

fig.suptitle("Diagnostic du drainage souterrain estival Noah-MP 4.0.1 (SIMGM) à Lalla Chafia (Mai–Novembre 2018)\n"
             "Analyse de l'inertie du réservoir souterrain (WA), du maintien de Qsb et de la persistance du biais estival",
             fontweight='bold', y=0.965, fontsize=11.5)

png_path = os.path.join(out_fig_dir, "summer_drainage_lalla_chafia_2018.png")
pdf_path = os.path.join(out_fig_dir, "summer_drainage_lalla_chafia_2018.pdf")
plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
plt.close()

if os.path.exists(artifact_dir):
    art_path = os.path.join(artifact_dir, "summer_drainage_lalla_chafia_2018.png")
    shutil.copy2(png_path, art_path)
    print(f"[OK] Figure copiee vers artefacts : {art_path}")

print("[OK] Script de diagnostic estival termine avec succes.")
