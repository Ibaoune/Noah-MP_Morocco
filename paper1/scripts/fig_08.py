#!/usr/bin/env python3
"""
fig_08.py
---------
Figure 8: Evapotranspiration (ET) evaluation against independent products (GLEAM v4.3a & WaPOR v3).
Panels:
  (a) Monthly ET annual cycle by basin (Sebou, Bouregreg, and Domain)
      comparing simulations with GLEAM v4.3a.
  (b) Evaluation metrics for the three proper differences:
      (1) Ensemble effect (ENS_OPL - OL_DAIC)
      (2) Observation effect (DA_nocdf - ENS_OPL)
      (3) Wilting filter effect (DA_nocdf_nowilt - DA_nocdf)
      showing Δ|bias| and fraction of grid cells improving towards observations.

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
DIR_CHANGE_CSV = os.path.join(BASE_DIR, "paper1/tables/et_direction_of_change.csv")

OUT_FIG = os.path.join(BASE_DIR, "paper1/figures/fig_08.png")
OUT_CSV = os.path.join(BASE_DIR, "paper1/figures/fig_08_data.csv")

def main():
    os.makedirs(os.path.dirname(OUT_FIG), exist_ok=True)
    
    # ── 1. Setup Grids and Basins ──────────────────────────────────────────────
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

    # Regrid masks to GLEAM (60, 90)
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

    # ── 2. Load GLEAM Monthly Series ───────────────────────────────────────────
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

    # ── 3. Load Simulation Monthly ET ──────────────────────────────────────────
    exps = ['OPL', 'OL_DAIC', 'ENS_OPL', 'DA_nocdf', 'DA_cdf', 'DA_nocdf_nowilt']
    sim_monthly = {}

    for exp in exps:
        sim_monthly[exp] = {'Domain': [], 'Sebou': [], 'Bouregreg': []}
        
        if exp == "OPL":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2018-{m:02d}/**/LIS_HIST_*.nc")
        elif exp == "DA_nocdf":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_nocdf_noirr_2016_2020/output/2018-{m:02d}/**/LIS_HIST_*.nc")
        elif exp == "DA_cdf":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/DA_cdf_noirr_2016_2020/output/2018-{m:02d}/**/LIS_HIST_*.nc")
        elif exp == "OL_DAIC":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL/**/LIS_HIST_*.nc")
        elif exp == "ENS_OPL":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL/**/LIS_HIST_*.nc")
        elif exp == "DA_nocdf_nowilt":
            pattern = os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL/**/LIS_HIST_*.nc")

        for m in range(1, 13):
            m_str = f"2018{m:02d}"
            if exp in ["OPL", "DA_nocdf", "DA_cdf"]:
                m_pat = pattern.format(m=m)
            else:
                m_pat = os.path.join(os.path.dirname(pattern), m_str, "LIS_HIST_*.nc")
                
            files = sorted(glob.glob(m_pat))
            if files:
                sub_f = files[::max(1, len(files)//6)]
                vals = []
                for fp in sub_f:
                    with nc.Dataset(fp) as ds:
                        if 'Evap_tavg' in ds.variables:
                            ev = ds.variables['Evap_tavg'][0, :, :]
                            ev = np.where((ev > -100) & (ev < 1000), ev, np.nan)
                            vals.append(ev)
                if vals:
                    mean_ev_rate = np.nanmean(vals, axis=0)
                    m_tot = mean_ev_rate * 86400.0 * days_in_month[m-1]
                    sim_monthly[exp]['Domain'].append(float(np.nanmean(m_tot[mask_domain])))
                    sim_monthly[exp]['Sebou'].append(float(np.nanmean(m_tot[mask_sebou])))
                    sim_monthly[exp]['Bouregreg'].append(float(np.nanmean(m_tot[mask_bouregreg])))
                else:
                    sim_monthly[exp]['Domain'].append(np.nan)
                    sim_monthly[exp]['Sebou'].append(np.nan)
                    sim_monthly[exp]['Bouregreg'].append(np.nan)
            else:
                sim_monthly[exp]['Domain'].append(np.nan)
                sim_monthly[exp]['Sebou'].append(np.nan)
                sim_monthly[exp]['Bouregreg'].append(np.nan)

    # ── 4. Save Plotted Data CSV ───────────────────────────────────────────────
    df_dir = pd.read_csv(DIR_CHANGE_CSV)
    
    m_data = {'month': np.arange(1, 13), 'GLEAM_Sebou': gleam_sebou, 'GLEAM_Bouregreg': gleam_boureg, 'GLEAM_Domain': gleam_dom}
    for exp in exps:
        for b in ['Sebou', 'Bouregreg', 'Domain']:
            m_data[f'{exp}_{b}'] = sim_monthly[exp][b]
    df_m_basin = pd.DataFrame(m_data)
    
    with open(OUT_CSV, 'w') as f:
        f.write("# PANEL_A_MONTHLY_ET_CYCLE_BY_BASIN_2018\n")
        df_m_basin.to_csv(f, index=False)
        f.write("\n# PANEL_B_DIRECTION_OF_CHANGE_EVALUATION\n")
        df_dir.to_csv(f, index=False)
    print(f"Saved plotted data to {OUT_CSV}")

    # ── 5. Setup Figure ────────────────────────────────────────────────────────
    fig = plt.figure(figsize=(19, 11))
    gs = gridspec.GridSpec(2, 3, height_ratios=[1.0, 1.1], width_ratios=[1.0, 1.0, 1.1],
                           hspace=0.28, wspace=0.22, left=0.06, right=0.96, top=0.92, bottom=0.08)
                           
    months = np.arange(1, 13)
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    c_gleam = '#000000'
    colors = {
        'OPL': '#1f77b4',
        'OL_DAIC': '#56B4E9',
        'ENS_OPL': '#009E73',
        'DA_nocdf': '#D55E00',
        'DA_cdf': '#CC79A7',
        'DA_nocdf_nowilt': '#E69F00'
    }

    # ── Row 1: Monthly ET Cycles ───────────────────────────────────────────────
    basins = [('Sebou', 0, 0, gleam_sebou), ('Bouregreg', 0, 1, gleam_boureg), ('Domain (North Morocco)', 0, 2, gleam_dom)]
    panel_letters = ['(a1)', '(a2)', '(a3)']
    
    for (b_name, r, c, gl_vals), p_let in zip(basins, panel_letters):
        ax = fig.add_subplot(gs[r, c])
        ax.plot(months, gl_vals, color=c_gleam, linestyle='-', linewidth=2.5, marker='o', markersize=4, label='GLEAM v4.3a', zorder=5)
        b_key = 'Domain' if 'Domain' in b_name else b_name
        for exp in exps:
            y = sim_monthly[exp][b_key]
            ls = '--' if 'DA' in exp else '-'
            lw = 2.0 if exp in ['DA_nocdf', 'DA_nocdf_nowilt', 'ENS_OPL'] else 1.5
            ax.plot(months, y, color=colors[exp], linestyle=ls, linewidth=lw, label=exp)
            
        ax.set_title(f"{p_let} Monthly ET — {b_name} (2018)", fontsize=11.5, fontweight='bold', pad=8)
        ax.set_xlabel("Month of Year", fontsize=10)
        ax.set_ylabel("ET (mm / month)", fontsize=10)
        ax.set_xticks(months)
        ax.set_xticklabels(month_names, fontsize=8)
        ax.grid(True, linestyle=':', alpha=0.6)
        if c == 0:
            ax.legend(loc='upper right', fontsize=8.0, framealpha=0.95, ncol=2)

    # ── Row 2: Evaluation Metrics for Proper Differences ───────────────────────
    ax_b1 = fig.add_subplot(gs[1, 0:2])
    ax_b2 = fig.add_subplot(gs[1, 2])
    
    pairs = [
        ('ENS_OPL - OL_DAIC', 'Ensemble Effect\n(ENS - OL_DAIC)'),
        ('DA_nocdf - ENS_OPL', 'Observation Effect\n(DA - ENS)'),
        ('DA_nocdf_nowilt - DA_nocdf', 'Wilting Filter Effect\n(noWQC - NoCDF)')
    ]
    
    x_pairs = np.arange(len(pairs))
    width_p = 0.22
    
    c_gl_bar = '#56B4E9'
    c_wap_bar = '#E69F00'
    
    d_bias_gl_dom, d_bias_wap_dom = [], []
    frac_gl_dom, frac_wap_dom = [], []
    
    for p_id, _ in pairs:
        row = df_dir[(df_dir['pair'] == p_id) & (df_dir['reference'] == 'GLEAM_v4.3a') & (df_dir['stratum'] == 'Domain')]
        d_bias_gl_dom.append(row['delta_abs_bias_mm'].values[0] if len(row) > 0 else 0)
        frac_gl_dom.append(row['frac_closer_pct'].values[0] if len(row) > 0 else 0)
        
        row = df_dir[(df_dir['pair'] == p_id) & (df_dir['reference'] == 'WaPOR_v3') & (df_dir['stratum'] == 'Domain')]
        d_bias_wap_dom.append(row['delta_abs_bias_mm'].values[0] if len(row) > 0 else 0)
        frac_wap_dom.append(row['frac_closer_pct'].values[0] if len(row) > 0 else 0)
        
    rects_b1 = ax_b1.bar(x_pairs - width_p/2, d_bias_gl_dom, width_p, label='GLEAM v4.3a (Domain)', color=c_gl_bar, edgecolor='black', lw=0.7)
    rects_b2 = ax_b1.bar(x_pairs + width_p/2, d_bias_wap_dom, width_p, label='WaPOR v3 (Domain)', color=c_wap_bar, edgecolor='black', lw=0.7)
    
    ax_b1.axhline(0, color='black', linestyle='-', linewidth=0.8)
    ax_b1.set_title("(b1) Change in Absolute Bias $\\Delta|\\mathrm{Bias}|$ [Negative = Improvement towards Obs]", fontsize=11.5, fontweight='bold', pad=8)
    ax_b1.set_xticks(x_pairs)
    ax_b1.set_xticklabels([lbl for _, lbl in pairs], fontsize=9.5)
    ax_b1.set_ylabel("$\\Delta|\\mathrm{Bias}|$ (mm / year)", fontsize=10.5)
    ax_b1.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b1.legend(loc='lower left', fontsize=9.0, framealpha=0.95)
    
    for rects in [rects_b1, rects_b2]:
        for r in rects:
            h = r.get_height()
            va = 'top' if h < 0 else 'bottom'
            y_pos = h - 6.0 if h < 0 else h + 2.0
            ax_b1.annotate(f"{h:.1f}",
                           xy=(r.get_x() + r.get_width() / 2, y_pos),
                           ha='center', va=va, fontsize=8.5, fontweight='bold')
                           
    rects_f1 = ax_b2.bar(x_pairs - width_p/2, frac_gl_dom, width_p, label='GLEAM v4.3a', color=c_gl_bar, edgecolor='black', lw=0.7)
    rects_f2 = ax_b2.bar(x_pairs + width_p/2, frac_wap_dom, width_p, label='WaPOR v3', color=c_wap_bar, edgecolor='black', lw=0.7)
    
    ax_b2.axhline(50, color='red', linestyle='--', linewidth=0.9, label='50% Neutral Threshold')
    ax_b2.set_title("(b2) Fraction of Grid Cells Improving (%)", fontsize=11.5, fontweight='bold', pad=8)
    ax_b2.set_xticks(x_pairs)
    ax_b2.set_xticklabels([lbl.split('\n')[0] for _, lbl in pairs], fontsize=9.0)
    ax_b2.set_ylabel("Cells closer to Obs (%)", fontsize=10.5)
    ax_b2.set_ylim(0, 100)
    ax_b2.grid(True, axis='y', linestyle='--', alpha=0.7)
    ax_b2.legend(loc='upper right', fontsize=8.5, framealpha=0.95)
    
    for rects in [rects_f1, rects_f2]:
        for r in rects:
            h = r.get_height()
            ax_b2.annotate(f"{h:.1f}%",
                           xy=(r.get_x() + r.get_width() / 2, h + 1.5),
                           ha='center', va='bottom', fontsize=8.5, fontweight='bold')
                           
    fig.suptitle("Figure 8 — Independent Evaluation of Evapotranspiration against GLEAM v4.3a and WaPOR v3 (2018)",
                 fontsize=14, fontweight='bold', y=0.98)
                 
    fig.savefig(OUT_FIG, dpi=200, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"Saved figure to {OUT_FIG} (200 dpi)")

if __name__ == "__main__":
    main()
