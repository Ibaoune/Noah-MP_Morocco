#!/usr/bin/env python3
"""
fig_08.py
---------
Figure 8: Evapotranspiration (ET) independent evaluation against WaPOR v3 (primary reference)
and GLEAM v4.3a (secondary reference).

Includes:
- Simulation runs: OL_DAIC, ENS_OPL, ENS_corr, DA_nocdf, DA_cdf, DA_corr, DA_nocdf_nowilt.
- 5 clean differences:
  1) ENS_corr - OL_DAIC (Effet residuel ensemble corrige)
  2) ENS_OPL - OL_DAIC (Effet ensemble production)
  3) DA_corr - ENS_corr (Effet observations systeme corrige)
  4) DA_nocdf - ENS_OPL (Effet observations systeme production)
  5) DA_nocdf_nowilt - DA_nocdf (Effet filtre fletrissement)
- WaPOR v3 presented first (primary), GLEAM v4.3a second (secondary).

Outputs:
  paper1/figures/fig_08.png (200 dpi)
  paper1/figures/fig_08_data.csv
"""

import os
import glob
import pandas as pd
import numpy as np
import netCDF4 as nc
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LIS_INPUT = os.path.join(BASE_DIR, "data/lis_input/lis_input_NorthMor_5km.nc")
HYMAP_PARAMS = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc")
GLEAM_FILE = os.path.join(BASE_DIR, "data/validation/evapotranspiration/GLEAM/raw/E_2018_GLEAM_v4.3a.nc")

DIR_CHANGE_CSV = os.path.join(BASE_DIR, "paper1/tables/et_direction_of_change_corrected_2018.csv")
ET_EVAL_CSV = os.path.join(BASE_DIR, "paper1/tables/et_evaluation_corrected_2018.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_08.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_08_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Setup Grids and Masks ───────────────────────────────────────────────
    with nc.Dataset(LIS_INPUT) as ds:
        landmask_181 = ds.variables["LANDMASK"][:].squeeze().astype(bool)
        lat_181 = ds.variables["lat"][:, 0]
        lon_181 = ds.variables["lon"][0, :]

    with nc.Dataset(HYMAP_PARAMS) as ds_h:
        hymap_basin = ds_h.variables["HYMAP_basin"][:]
        lat_180_0 = float(ds_h.variables["lat"][0, 0])
        lon_180_0 = float(ds_h.variables["lon"][0, 0])

    basin_181 = np.full((121, 181), -9999.0, dtype=np.float32)
    for j in range(121):
        j_180 = np.clip(int(np.round((lat_181[j] - lat_180_0) / 0.05)), 0, 119)
        for i in range(181):
            i_180 = np.clip(int(np.round((lon_181[i] - lon_180_0) / 0.05)), 0, 179)
            basin_181[j, i] = hymap_basin[j_180, i_180]

    mask_domain = landmask_181
    mask_sebou = (basin_181 == 155.0) & landmask_181
    mask_bouregreg = (basin_181 == 150.0) & landmask_181

    # GLEAM Coordinates (60, 90)
    with nc.Dataset(GLEAM_FILE) as ds_g:
        g_lat_all = ds_g.variables["lat"][:]
        g_lon_all = ds_g.variables["lon"][:]
        lat_idx_g = np.where((g_lat_all >= 30.0) & (g_lat_all <= 36.0))[0]
        lon_idx_g = np.where((g_lon_all >= -10.0) & (g_lon_all <= -1.0))[0]
        gleam_lats = g_lat_all[lat_idx_g]
        gleam_lons = g_lon_all[lon_idx_g]
        e_raw = ds_g.variables["E"][:, lat_idx_g, lon_idx_g]

    def regrid_to_gleam(grid_181, mask_weights=None):
        out_grid = np.full((60, 90), np.nan, dtype=np.float32)
        weights = landmask_181 if mask_weights is None else (landmask_181 & mask_weights)
        for j, lat_c in enumerate(gleam_lats):
            r_idx = np.where((lat_181 >= lat_c - 0.05 - 1e-4) & (lat_181 <= lat_c + 0.05 + 1e-4))[0]
            for i, lon_c in enumerate(gleam_lons):
                c_idx = np.where((lon_181 >= lon_c - 0.05 - 1e-4) & (lon_181 <= lon_c + 0.05 + 1e-4))[0]
                sub_w = weights[np.ix_(r_idx, c_idx)]
                if np.any(sub_w):
                    sub_data = grid_181[np.ix_(r_idx, c_idx)]
                    out_grid[j, i] = np.mean(sub_data[sub_w])
        return out_grid

    mask_g_domain = ~np.isnan(regrid_to_gleam(np.where(mask_domain, 1.0, np.nan)))
    mask_g_sebou = ~np.isnan(regrid_to_gleam(np.where(mask_sebou, 1.0, np.nan)))
    mask_g_bouregreg = ~np.isnan(regrid_to_gleam(np.where(mask_bouregreg, 1.0, np.nan)))

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gleam_monthly = []
    d_start = 0
    for m, nd in enumerate(days_in_month):
        d_end = d_start + nd
        sub_e = e_raw[d_start:d_end, :, :]
        sub_e = np.where(sub_e < -900, np.nan, sub_e)
        m_mean = np.nanmean(sub_e, axis=0) * nd
        gleam_monthly.append(m_mean)
        d_start = d_end
    gleam_monthly = np.array(gleam_monthly, dtype=np.float32)

    gleam_sebou = [float(np.nanmean(gleam_monthly[m][mask_g_sebou])) for m in range(12)]
    gleam_boureg = [float(np.nanmean(gleam_monthly[m][mask_g_bouregreg])) for m in range(12)]
    gleam_dom = [float(np.nanmean(gleam_monthly[m][mask_g_domain])) for m in range(12)]

    # ── 2. Load Simulation Monthly ET ──────────────────────────────────────────
    exp_configs = [
        ('OL_DAIC', 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
        ('ENS_OPL', 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
        ('ENS_corr', 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_corr_2018/output/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
        ('DA_nocdf', 'experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-{m:02d}/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
        ('DA_corr', 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/output/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
        ('DA_nocdf_nowilt', 'experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/2018{m:02d}/LIS_HIST_*.nc'),
    ]

    sim_monthly = {}
    for exp_id, pat_template in exp_configs:
        sim_monthly[exp_id] = {'Domain': [], 'Sebou': [], 'Bouregreg': []}
        for m in range(1, 13):
            pat = os.path.join(BASE_DIR, pat_template.format(m=m))
            files = sorted(glob.glob(pat))
            if files:
                sub_f = files[::max(1, len(files)//6)]
                vals = []
                for fp in sub_f:
                    with nc.Dataset(fp) as ds:
                        if 'Evap_tavg' in ds.variables:
                            ev = np.squeeze(ds.variables["Evap_tavg"][:])
                            ev = np.where((ev > -100) & (ev < 1000), ev, np.nan)
                            vals.append(ev)
                if vals:
                    mean_ev_rate = np.nanmean(vals, axis=0)
                    m_tot = mean_ev_rate * 86400.0 * days_in_month[m-1]
                    sim_monthly[exp_id]['Domain'].append(float(np.nanmean(m_tot[mask_domain])))
                    sim_monthly[exp_id]['Sebou'].append(float(np.nanmean(m_tot[mask_sebou])))
                    sim_monthly[exp_id]['Bouregreg'].append(float(np.nanmean(m_tot[mask_bouregreg])))
                else:
                    sim_monthly[exp_id]['Domain'].append(np.nan)
                    sim_monthly[exp_id]['Sebou'].append(np.nan)
                    sim_monthly[exp_id]['Bouregreg'].append(np.nan)
            else:
                sim_monthly[exp_id]['Domain'].append(np.nan)
                sim_monthly[exp_id]['Sebou'].append(np.nan)
                sim_monthly[exp_id]['Bouregreg'].append(np.nan)

    # ── 3. Load CSV Metric Tables ──────────────────────────────────────────────
    df_dir = pd.read_csv(DIR_CHANGE_CSV)
    df_eval = pd.read_csv(ET_EVAL_CSV)

    wap_dom = float(df_eval[(df_eval['experiment'] == 'OL_DAIC') & (df_eval['reference'] == 'WaPOR_v3') & (df_eval['stratum'] == 'Domain')]['et_obs_mean_mm'].values[0])
    wap_seb = float(df_eval[(df_eval['experiment'] == 'OL_DAIC') & (df_eval['reference'] == 'WaPOR_v3') & (df_eval['stratum'] == 'Sebou')]['et_obs_mean_mm'].values[0])
    wap_bou = float(df_eval[(df_eval['experiment'] == 'OL_DAIC') & (df_eval['reference'] == 'WaPOR_v3') & (df_eval['stratum'] == 'Bouregreg')]['et_obs_mean_mm'].values[0])

    # ── 4. Save Plotted Data CSV ───────────────────────────────────────────────
    m_data = {
        'month': np.arange(1, 13),
        'GLEAM_Sebou': gleam_sebou,
        'GLEAM_Bouregreg': gleam_boureg,
        'GLEAM_Domain': gleam_dom,
    }
    for exp_id, _ in exp_configs:
        for b in ['Sebou', 'Bouregreg', 'Domain']:
            m_data[f'{exp_id}_{b}'] = sim_monthly[exp_id][b]
    df_m_basin = pd.DataFrame(m_data)

    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_MONTHLY_ET_CYCLE_BY_BASIN_2018\n")
        df_m_basin.to_csv(f, index=False)
        f.write("\n# PANEL_B_DIRECTION_OF_CHANGE_EVALUATION\n")
        df_dir.to_csv(f, index=False)
        f.write("\n# ANNUAL_WAPOR_V3_BENCHMARKS\n")
        f.write(f"Domain_WaPOR_v3_Annual_mm,{wap_dom:.2f}\n")
        f.write(f"Sebou_WaPOR_v3_Annual_mm,{wap_seb:.2f}\n")
        f.write(f"Bouregreg_WaPOR_v3_Annual_mm,{wap_bou:.2f}\n")
    print(f"Saved plotted data to {OUT_CSV}")

    # ── 5. Setup Figure (2x3 Grid) ─────────────────────────────────────────────
    fig = plt.figure(figsize=(20, 12))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1.0, 1.15], width_ratios=[1.0, 1.0, 1.05],
                           hspace=0.32, wspace=0.22, left=0.06, right=0.96, top=0.92, bottom=0.08)

    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

    colors = {
        'OL_DAIC': '#56B4E9',
        'ENS_OPL': '#E69F00',
        'ENS_corr': '#009E73',
        'DA_nocdf': '#D55E00',
        'DA_corr': '#0072B2',
        'DA_nocdf_nowilt': '#CC79A7'
    }

    labels_exp = {
        'OL_DAIC': 'OL-DAIC (Ref)',
        'ENS_OPL': 'ENS-OPL (Prod)',
        'ENS_corr': 'ENS-corr (Corr)',
        'DA_nocdf': 'DA-nocdf (Prod)',
        'DA_corr': 'DA-corr (Corr)',
        'DA_nocdf_nowilt': 'DA-noWQC (Prod)'
    }

    # ── Row 1: Monthly ET Cycles ───────────────────────────────────────────────
    basins = [
        ('Sebou', 0, 0, gleam_sebou, wap_seb),
        ('Bouregreg', 0, 1, gleam_boureg, wap_bou),
        ('Domain (North Morocco)', 0, 2, gleam_dom, wap_dom)
    ]
    panel_letters = ['(a1)', '(a2)', '(a3)']

    for (b_name, r, c, gl_vals, wap_val), p_let in zip(basins, panel_letters):
        ax = fig.add_subplot(gs[r, c])
        ax.plot(months, gl_vals, color='#111111', linestyle='-', linewidth=2.8, marker='s', markersize=4.5,
                label='GLEAM v4.3a (Monthly Obs)', zorder=6)
        
        ax.axhline(wap_val / 12.0, color='#2CA02C', linestyle=':', linewidth=1.8,
                   label=f'WaPOR v3 Mean ({wap_val:.0f} mm/yr)', zorder=5)

        b_key = 'Domain' if 'Domain' in b_name else b_name
        for exp_id, _ in exp_configs:
            y = sim_monthly[exp_id][b_key]
            ls = '--' if 'DA' in exp_id else '-'
            lw = 2.2 if exp_id in ['ENS_corr', 'DA_corr'] else 1.6
            ax.plot(months, y, color=colors[exp_id], linestyle=ls, linewidth=lw, label=labels_exp[exp_id], zorder=4)

        ax.set_title(f"{p_let} Monthly ET — {b_name} (2018)", fontsize=11.5, fontweight='bold', pad=8)
        ax.set_xlabel("Month of Year", fontsize=10)
        ax.set_ylabel("ET (mm / month)", fontsize=10)
        ax.set_xticks(months)
        ax.set_xticklabels(month_names, fontsize=8.5)
        ax.grid(True, linestyle=':', alpha=0.6)
        if c == 0:
            ax.legend(loc='upper right', fontsize=8.0, framealpha=0.92, ncol=2)

    # ── Row 2: Evaluation of the 5 Clean Differences ───────────────────────────
    pairs = [
        ('ENS_corr - OL_DAIC', '1. Ensemble corr\n(ENS_corr − OL)'),
        ('ENS_OPL - OL_DAIC', '2. Ensemble prod\n(ENS_OPL − OL)'),
        ('DA_corr - ENS_corr', '3. Obs corr\n(DA_corr − ENS_corr)'),
        ('DA_nocdf - ENS_OPL', '4. Obs prod\n(DA_nocdf − ENS_OPL)'),
        ('DA_nocdf_nowilt - DA_nocdf', '5. Wilting filter\n(noWQC − DA_nocdf)')
    ]

    x_pairs = np.arange(len(pairs))
    width_p = 0.32

    c_wap = '#D95F02'  # WaPOR primary
    c_gleam = '#2B83BA' # GLEAM secondary

    d_bias_wap_dom, d_bias_gl_dom = [], []
    frac_wap_dom, frac_gl_dom = [], []

    for p_id, _ in pairs:
        row_wap = df_dir[(df_dir['pair'] == p_id) & (df_dir['reference'] == 'WaPOR_v3') & (df_dir['stratum'] == 'Domain') & (df_dir['season'] == 'Annual')]
        d_bias_wap_dom.append(float(row_wap['delta_abs_bias_mm'].values[0]) if len(row_wap) > 0 else 0.0)
        frac_wap_dom.append(float(row_wap['frac_closer_pct'].values[0]) if len(row_wap) > 0 else 0.0)

        row_gl = df_dir[(df_dir['pair'] == p_id) & (df_dir['reference'] == 'GLEAM_v4.3a') & (df_dir['stratum'] == 'Domain') & (df_dir['season'] == 'Annual')]
        d_bias_gl_dom.append(float(row_gl['delta_abs_bias_mm'].values[0]) if len(row_gl) > 0 else 0.0)
        frac_gl_dom.append(float(row_gl['frac_closer_pct'].values[0]) if len(row_gl) > 0 else 0.0)

    # Panel (b1): Δ|Bias|
    ax_b1 = fig.add_subplot(gs[1, 0])
    rects_wap_b = ax_b1.bar(x_pairs - width_p/2, d_bias_wap_dom, width_p, label='WaPOR v3 (Primary, Indep.)', color=c_wap, edgecolor='black', lw=0.7)
    rects_gl_b = ax_b1.bar(x_pairs + width_p/2, d_bias_gl_dom, width_p, label='GLEAM v4.3a (Secondary)', color=c_gleam, edgecolor='black', lw=0.7)

    ax_b1.axhline(0, color='black', linestyle='-', linewidth=0.9)
    ax_b1.set_title("(b1) Change in Absolute Bias $\\Delta|\\mathrm{Bias}|$ [Domain]\nNegative = Improvement towards Observation", fontsize=11.0, fontweight='bold', pad=8)
    ax_b1.set_xticks(x_pairs)
    ax_b1.set_xticklabels([lbl for _, lbl in pairs], fontsize=8.0)
    ax_b1.set_ylabel("$\\Delta|\\mathrm{Bias}|$ (mm / year)", fontsize=10)
    ax_b1.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b1.legend(loc='upper right', fontsize=8.5, framealpha=0.92)

    for rects in [rects_wap_b, rects_gl_b]:
        for r in rects:
            h = r.get_height()
            va = 'top' if h < 0 else 'bottom'
            y_pos = h - 6.0 if h < 0 else h + 2.0
            ax_b1.annotate(f"{h:+.1f}",
                           xy=(r.get_x() + r.get_width() / 2, y_pos),
                           ha='center', va=va, fontsize=8.0, fontweight='bold')

    # Panel (b2): Fraction of Cells Improving
    ax_b2 = fig.add_subplot(gs[1, 1])
    rects_wap_f = ax_b2.bar(x_pairs - width_p/2, frac_wap_dom, width_p, label='WaPOR v3 (Primary, Indep.)', color=c_wap, edgecolor='black', lw=0.7)
    rects_gl_f = ax_b2.bar(x_pairs + width_p/2, frac_gl_dom, width_p, label='GLEAM v4.3a (Secondary)', color=c_gleam, edgecolor='black', lw=0.7)

    ax_b2.axhline(50, color='red', linestyle='--', linewidth=1.1, label='50% Neutral Threshold')
    ax_b2.set_title("(b2) Fraction of Grid Cells Improving (%) [Domain]\nValues > 50% indicate Net Spatial Improvement", fontsize=11.0, fontweight='bold', pad=8)
    ax_b2.set_xticks(x_pairs)
    ax_b2.set_xticklabels([lbl.split('\n')[0] for _, lbl in pairs], fontsize=8.2)
    ax_b2.set_ylabel("Cells closer to Obs (%)", fontsize=10)
    ax_b2.set_ylim(0, 105)
    ax_b2.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b2.legend(loc='lower left', fontsize=8.5, framealpha=0.92)

    for rects in [rects_wap_f, rects_gl_f]:
        for r in rects:
            h = r.get_height()
            ax_b2.annotate(f"{h:.1f}%",
                           xy=(r.get_x() + r.get_width() / 2, h + 1.5),
                           ha='center', va='bottom', fontsize=8.0, fontweight='bold')

    # Panel (b3): Impact by Soil Texture against WaPOR v3 (Primary Reference)
    ax_b3 = fig.add_subplot(gs[1, 2])
    textures = [
        ('Texture_3_Sandy Loam', 'Sandy Loam'),
        ('Texture_6_Loam', 'Loam'),
        ('Texture_7_Sandy Clay Loam', 'S. Clay Loam'),
        ('Texture_9_Clay Loam', 'Clay Loam'),
        ('Texture_12_Clay', 'Clay')
    ]
    x_tex = np.arange(len(textures))
    w_t = 0.35

    d_bias_prod_tex, d_bias_corr_tex = [], []
    for t_id, _ in textures:
        row_p = df_dir[(df_dir['pair'] == 'DA_nocdf - ENS_OPL') & (df_dir['reference'] == 'WaPOR_v3') & (df_dir['stratum'] == t_id) & (df_dir['season'] == 'Annual')]
        d_bias_prod_tex.append(float(row_p['delta_abs_bias_mm'].values[0]) if len(row_p) > 0 else 0.0)

        row_c = df_dir[(df_dir['pair'] == 'DA_corr - ENS_corr') & (df_dir['reference'] == 'WaPOR_v3') & (df_dir['stratum'] == t_id) & (df_dir['season'] == 'Annual')]
        d_bias_corr_tex.append(float(row_c['delta_abs_bias_mm'].values[0]) if len(row_c) > 0 else 0.0)

    rects_tp = ax_b3.bar(x_tex - w_t/2, d_bias_prod_tex, w_t, label='Obs Effect: Prod (DA_nocdf − ENS)', color='#D55E00', edgecolor='black', lw=0.7)
    rects_tc = ax_b3.bar(x_tex + w_t/2, d_bias_corr_tex, w_t, label='Obs Effect: Corr (DA_corr − ENS_corr)', color='#0072B2', edgecolor='black', lw=0.7)

    ax_b3.axhline(0, color='black', linestyle='-', linewidth=0.9)
    ax_b3.set_title("(b3) Observation Effect $\\Delta|\\mathrm{Bias}|$ by Texture\nagainst WaPOR v3 (Primary Reference)", fontsize=11.0, fontweight='bold', pad=8)
    ax_b3.set_xticks(x_tex)
    ax_b3.set_xticklabels([name for _, name in textures], fontsize=8.0, rotation=15)
    ax_b3.set_ylabel("$\\Delta|\\mathrm{Bias}|$ (mm / year)", fontsize=10)
    ax_b3.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b3.legend(loc='lower left', fontsize=8.0, framealpha=0.92)

    for rects in [rects_tp, rects_tc]:
        for r in rects:
            h = r.get_height()
            va = 'top' if h < 0 else 'bottom'
            y_pos = h - 6.0 if h < 0 else h + 2.0
            ax_b3.annotate(f"{h:+.1f}",
                           xy=(r.get_x() + r.get_width() / 2, y_pos),
                           ha='center', va=va, fontsize=7.5, fontweight='bold')

    fig.suptitle("Figure 8 — Independent Evaluation of Evapotranspiration: WaPOR v3 (Primary) and GLEAM v4.3a (Secondary) in 2018",
                 fontsize=13.5, fontweight='bold', y=0.98)

    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
