#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diagnostic des mécanismes hydrologiques Noah-MP 4.0.1 sur le bassin de Lalla Chafia :
Comparaison journalière des événements de Mars 2018 (01-15 mars) et Avril 2018 (20-30 avril).
Analyse des précipitations, de la production de ruissellement (Qs, Qsb), de l'humidité du sol (L1-L4),
de la fraction saturée (FSAT), de l'aquifère (WA) et des hydrogrammes routés HyMAP (linres=1 vs linres=0).
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

# 1. Masque amont Lalla Chafia (133 cellules)
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

# 2. Lecture des débits de référence (Obs, HyMAP linres=1 et linres=0)
df_flux = pd.read_csv(csv_flux_path)
df_flux['date'] = pd.to_datetime(df_flux['date'])
df_flux.set_index('date', inplace=True)

periods = [
    ('mars_2018', datetime.date(2018, 3, 1), datetime.date(2018, 3, 15)),
    ('avril_2018', datetime.date(2018, 4, 20), datetime.date(2018, 4, 30))
]

dz = [0.1, 0.3, 0.6, 1.0]
records = []

for p_name, d_start, d_end in periods:
    curr = d_start
    while curr <= d_end:
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
        ec_val = remap_and_avg(ds['ECanop_tavg'][:]) * 86400.0
        es_val = remap_and_avg(ds['ESoil_tavg'][:]) * 86400.0
        tv_val = remap_and_avg(ds['TVeg_tavg'][:]) * 86400.0
        pet_val = remap_and_avg(ds['PotEvap_tavg'][:]) * 86400.0
        
        smc_vals = [remap_and_avg(ds['SoilMoist_tavg'][l]) for l in range(4)]
        s_soil = sum(dz[l] * smc_vals[l] * 1000.0 for l in range(4))
        
        # Canopée et neige pour soustraction exacte de WA depuis TWS
        can_val = remap_and_avg(ds['CanopInt_tavg'][:]) if 'CanopInt_tavg' in ds.variables else 0.0
        swe_val = remap_and_avg(ds['SWE_tavg'][:]) if 'SWE_tavg' in ds.variables else 0.0
        tws_val = remap_and_avg(ds['TWS_tavg'][:])
        wa_val = tws_val - (s_soil + can_val + swe_val)
        
        # Calcul cellule par cellule de FSAT
        zwt_rem = remap_2d(ds['WaterTableD_tavg'][:])
        zwt_cells = zwt_rem[cat_rows, cat_cols]
        zwt_val = float(np.sum(zwt_cells * cat_areas) / tot_area_m2)
        fsat_cells = 0.38 * np.exp(-3.0 * (zwt_cells - 2.0))
        fsat_avg_pct = float(np.sum(fsat_cells * cat_areas) / tot_area_m2 * 100.0)
        
        ds.close()
        
        dt_pd = pd.to_datetime(curr)
        q_sim_hist = float(df_flux.loc[dt_pd, 'q_sim_hist_m3s']) if dt_pd in df_flux.index else np.nan
        q_sim_lin0 = float(df_flux.loc[dt_pd, 'q_sim_linres0_m3s']) if dt_pd in df_flux.index else np.nan
        q_obs = float(df_flux.loc[dt_pd, 'q_obs_m3s']) if dt_pd in df_flux.index else np.nan
        
        records.append({
            'periode': p_name,
            'date': curr.strftime('%Y-%m-%d'),
            'P_mm_d': round(p_val, 3),
            'ET_mm_d': round(et_val, 3),
            'Ec_mm_d': round(ec_val, 3),
            'Es_mm_d': round(es_val, 3),
            'Tv_mm_d': round(tv_val, 3),
            'PotEvap_mm_d': round(pet_val, 3),
            'Qs_mm_d': round(qs_val, 4),
            'Qsb_mm_d': round(qsb_val, 4),
            'Qtot_sim_mm_d': round(qs_val + qsb_val, 4),
            'FSAT_ponderee_pct': round(fsat_avg_pct, 3),
            'theta_1_m3m3': round(smc_vals[0], 4),
            'theta_2_m3m3': round(smc_vals[1], 4),
            'theta_3_m3m3': round(smc_vals[2], 4),
            'theta_4_m3m3': round(smc_vals[3], 4),
            'S_soil_mm': round(s_soil, 2),
            'Canop_mm': round(can_val, 3),
            'SWE_mm': round(swe_val, 3),
            'ZWT_m': round(zwt_val, 3),
            'WA_mm': round(wa_val, 2),
            'TWS_mm': round(tws_val, 2),
            'Qsim_hist_linres1_m3s': round(q_sim_hist, 2),
            'Qsim_recent_linres0_m3s': round(q_sim_lin0, 2),
            'Qobs_ABH_m3s': round(q_obs, 2)
        })
        curr += datetime.timedelta(days=1)

df_out = pd.DataFrame(records)
csv_events_path = os.path.join(out_table_dir, "daily_events_lalla_chafia_mar_apr_2018.csv")
df_out.to_csv(csv_events_path, index=False)
print(f"[OK] Table journaliere enregistree : {csv_events_path}")

# 3. Figure comparative des deux événements
plt.rcParams.update({
    'font.sans-serif': 'DejaVu Sans',
    'font.family': 'sans-serif',
    'font.size': 9.2,
    'axes.labelsize': 9.8,
    'axes.titlesize': 10.2,
    'xtick.labelsize': 8.8,
    'ytick.labelsize': 8.8,
    'axes.grid': True,
    'grid.alpha': 0.35,
    'grid.linestyle': '--'
})

fig, axes = plt.subplots(4, 2, figsize=(15.2, 11.2), sharex=False)
fig.subplots_adjust(top=0.89, bottom=0.065, left=0.07, right=0.93, hspace=0.35, wspace=0.22)

df_mar = df_out[df_out['periode'] == 'mars_2018'].copy().reset_index(drop=True)
df_apr = df_out[df_out['periode'] == 'avril_2018'].copy().reset_index(drop=True)
df_mar['dt'] = pd.to_datetime(df_mar['date'])
df_apr['dt'] = pd.to_datetime(df_apr['date'])

ev_data = [
    ('Mars 2018 (01–15 Mars) : Épisode pluvieux prolongé', df_mar, 0),
    ('Avril 2018 (20–30 Avril) : Épisode convectif intense', df_apr, 1)
]

for title, df_e, col in ev_data:
    x_dates = df_e['dt']
    x_str = [d.strftime('%d/%m') for d in x_dates]
    x_idx = np.arange(len(x_dates))
    
    # Ligne 1 : Pluie P et Évapotranspiration ET
    ax1 = axes[0, col]
    ax1.bar(x_idx - 0.18, df_e['P_mm_d'].values, width=0.36, label='Précipitation P', color='#1f77b4', alpha=0.85)
    ax1.bar(x_idx + 0.18, df_e['ET_mm_d'].values, width=0.36, label='Évapotranspiration ET', color='#2ca02c', alpha=0.85)
    ax1.set_ylabel('Flux (mm/jour)', fontweight='bold')
    ax1.set_title(f'{title}\n(a) Forçage précipitant & Flux d\'évapotranspiration', pad=6, fontweight='bold')
    ax1.set_xticks(x_idx)
    ax1.set_xticklabels(x_str, rotation=35, ha='right')
    ax1.set_ylim(0, 65)
    ax1.legend(loc='upper right', framealpha=0.9, fontsize=8.2)
    for i, v in enumerate(df_e['P_mm_d'].values):
        if v > 15.0:
            ax1.annotate(f'{v:.1f}', (x_idx[i] - 0.18, v), xytext=(0, 2), textcoords="offset points", ha='center', fontsize=7.5, fontweight='bold')

    # Ligne 2 : Production de ruissellement Noah-MP (Qs et Qsb)
    ax2 = axes[1, col]
    ax2.bar(x_idx - 0.18, df_e['Qs_mm_d'].values, width=0.36, label='Ruissellement de surface Qs', color='#d62728', alpha=0.85)
    ax2.bar(x_idx + 0.18, df_e['Qsb_mm_d'].values, width=0.36, label='Drainage souterrain Qsb (QDIS)', color='#9467bd', alpha=0.85)
    ax2.set_ylabel('Ruissellement (mm/jour)', fontweight='bold')
    ax2.set_title('(b) Production de flux Noah-MP (Qs surface vs Qsb nappe)', pad=6, fontweight='bold')
    ax2.set_xticks(x_idx)
    ax2.set_xticklabels(x_str, rotation=35, ha='right')
    ax2.set_ylim(0, 3.2)
    ax2.legend(loc='upper right', framealpha=0.9, fontsize=8.2)
    for i, v in enumerate(df_e['Qs_mm_d'].values):
        if v > 0.4:
            ax2.annotate(f'{v:.2f}', (x_idx[i] - 0.18, v), xytext=(0, 2), textcoords="offset points", ha='center', fontsize=7.5, fontweight='bold')

    # Ligne 3 : Profil d'humidité du sol L1-L4 et Profondeur de nappe ZWT
    ax3 = axes[2, col]
    ax3.plot(x_idx, df_e['theta_1_m3m3'].values, marker='o', markersize=3.5, label='L1 (0–10 cm)', color='#e377c2', linewidth=1.5)
    ax3.plot(x_idx, df_e['theta_2_m3m3'].values, marker='s', markersize=3.5, label='L2 (10–40 cm)', color='#bcbd22', linewidth=1.5)
    ax3.plot(x_idx, df_e['theta_3_m3m3'].values, marker='^', markersize=3.5, label='L3 (40–100 cm)', color='#17becf', linewidth=1.5)
    ax3.plot(x_idx, df_e['theta_4_m3m3'].values, marker='d', markersize=3.5, label='L4 (100–200 cm)', color='#8c564b', linewidth=1.5)
    ax3.set_ylabel('Humidité volumique $\\theta$ (m³/m³)', fontweight='bold')
    ax3.set_title('(c) Humidité du sol (L1 à L4) et Niveau de nappe (ZWT)', pad=6, fontweight='bold')
    ax3.set_xticks(x_idx)
    ax3.set_xticklabels(x_str, rotation=35, ha='right')
    ax3.set_ylim(0.20, 0.38)
    
    # Axe secondaire pour ZWT
    ax3_twin = ax3.twinx()
    ax3_twin.plot(x_idx, df_e['ZWT_m'].values, color='black', linestyle='--', linewidth=1.8, label='Niveau nappe ZWT (m)')
    ax3_twin.set_ylabel('ZWT (m)', fontweight='bold', color='black')
    ax3_twin.set_ylim(3.05, 2.65)  # Inversé : surface en haut
    ax3_twin.grid(False)
    
    lines_1, labels_1 = ax3.get_legend_handles_labels()
    lines_2, labels_2 = ax3_twin.get_legend_handles_labels()
    ax3.legend(lines_1 + lines_2, labels_1 + labels_2, loc='lower right', framealpha=0.9, fontsize=7.2, ncol=2)

    # Ligne 4 : Hydrogrammes à l'exutoire (Obs ABH vs HyMAP linres=1 vs linres=0)
    ax4 = axes[3, col]
    ax4.plot(x_idx, df_e['Qobs_ABH_m3s'].values, marker='s', markersize=4, label='Observations ABH (Lalla Chafia)', color='#000000', linewidth=2.2, zorder=5)
    ax4.plot(x_idx, df_e['Qsim_hist_linres1_m3s'].values, marker='o', markersize=3.5, label='HyMAP-2 linres=1 (historique)', color='#1f77b4', linewidth=1.8, zorder=4)
    ax4.plot(x_idx, df_e['Qsim_recent_linres0_m3s'].values, marker='^', markersize=3.5, linestyle='--', label='HyMAP-2 linres=0 (récent)', color='#d62728', linewidth=1.8, zorder=4)
    
    ax4.set_ylabel('Débit exutoire (m³/s)', fontweight='bold')
    ax4.set_title('(d) Hydrogrammes à l\'exutoire : Routages linres=1 vs linres=0', pad=6, fontweight='bold')
    ax4.set_xticks(x_idx)
    ax4.set_xticklabels(x_str, rotation=35, ha='right')
    if col == 0:
        ax4.set_ylim(0, 225)
    else:
        ax4.set_ylim(0, 78)
    ax4.legend(loc='upper right', framealpha=0.9, fontsize=8.0)
    
    # Annotations des pics
    obs_vals = df_e['Qobs_ABH_m3s'].values
    hist_vals = df_e['Qsim_hist_linres1_m3s'].values
    lin0_vals = df_e['Qsim_recent_linres0_m3s'].values
    
    max_obs_idx = np.nanargmax(obs_vals)
    max_hist_idx = np.nanargmax(hist_vals)
    max_lin0_idx = np.nanargmax(lin0_vals)
    
    # Obs annotation
    ax4.annotate(f"Obs: {obs_vals[max_obs_idx]:.1f} m³/s ({x_str[max_obs_idx]})",
                 (x_idx[max_obs_idx], obs_vals[max_obs_idx]),
                 xytext=(0, 6), textcoords="offset points", ha='center', fontsize=7.6, fontweight='bold', color='black')
    # linres=1 annotation
    y_off_h = -12 if col == 0 else -14
    ax4.annotate(f"linres=1: {hist_vals[max_hist_idx]:.1f} ({x_str[max_hist_idx]})",
                 (x_idx[max_hist_idx], hist_vals[max_hist_idx]),
                 xytext=(0, y_off_h), textcoords="offset points", ha='center', fontsize=7.6, fontweight='bold', color='#1f77b4')
    # linres=0 annotation
    y_off_0 = 6 if col == 1 else 14
    ax4.annotate(f"linres=0: {lin0_vals[max_lin0_idx]:.1f} ({x_str[max_lin0_idx]})",
                 (x_idx[max_lin0_idx], lin0_vals[max_lin0_idx]),
                 xytext=(0, y_off_0), textcoords="offset points", ha='center', fontsize=7.6, fontweight='bold', color='#d62728')

fig.suptitle("Diagnostic physique des événements hydrologiques 2018 à Lalla Chafia (Noah-MP 4.0.1 / HyMAP-2)\n"
             "Analyse comparative du forçage, de la production de flux, de l'état du sol et des routages linres=1 vs linres=0",
             fontweight='bold', y=0.965, fontsize=11.5)

png_path = os.path.join(out_fig_dir, "events_comparison_mar_apr_2018.png")
pdf_path = os.path.join(out_fig_dir, "events_comparison_mar_apr_2018.pdf")
plt.savefig(png_path, dpi=300)
plt.savefig(pdf_path)
plt.close()

if os.path.exists(artifact_dir):
    art_path = os.path.join(artifact_dir, "events_comparison_mar_apr_2018.png")
    shutil.copy2(png_path, art_path)
    print(f"[OK] Figure copiee vers artefacts : {art_path}")

print("[OK] Script termine avec succes.")
