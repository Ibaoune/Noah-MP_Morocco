# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: opl_multiple_da.synthesis.plot_comprehensive
Description: Analysis of multiple Data Assimilation configurations vs Open Loop.
================================================================================
"""
import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.dates as mdates
from datetime import timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from utils.io_da import load_da_variable
from utils.io_lis import load_lis_variable
from utils.spatial_stats import calculate_basin_average
from utils.masking import get_landmask

def apply_mask(data, mask):
    if data is None or mask is None:
        return None
    # Mask invalid values
    data = np.where((data < -100) | (data > 100), np.nan, data)
    return np.where(mask, data, np.nan)

def plot_spatial(ax, data, mask, cmap_name, levels, title, cbar_label, extend='both'):
    cmap = plt.get_cmap(cmap_name).copy()
    cmap.set_bad(color='#f2f2f2') # very light grey for outside domain / invalid
    norm = mcolors.BoundaryNorm(levels, ncolors=cmap.N, extend=extend)
    
    masked_data = apply_mask(data, mask)
    im = ax.imshow(masked_data, cmap=cmap, norm=norm, origin='lower')
    ax.set_title(title, loc='left')
    ax.set_xticks([])
    ax.set_yticks([])
    
    cbar = plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04, extend=extend)
    cbar.set_label(cbar_label)
    return im

def setup_scientific_style():
    plt.rcParams.update({
        'font.size': 9, 
        'axes.titlesize': 10, 
        'axes.labelsize': 9, 
        'xtick.labelsize': 8, 
        'ytick.labelsize': 8,
        'axes.titleweight': 'normal',
        'figure.facecolor': 'white',
        'axes.facecolor': '#f2f2f2'
    })

def run_comprehensive_panel(data_dict, out_dir):
    print("  -> Generating Q1 publication-ready figures (Split into 2 figures)")
    setup_scientific_style()
    
    da_nocdf = data_dict.get('da_nocdf', {})
    da_cdf = data_dict.get('da_cdf', {})
    files_ol = data_dict.get('files_ol', [])
    files_nocdf = data_dict.get('files_da_nocdf', [])
    files_cdf = data_dict.get('files_da_cdf', [])
    start_date = data_dict.get('start_date')
    
    if not files_ol:
        print("Missing OL files, cannot generate comprehensive panels.")
        return []
        
    mask = get_landmask(files_ol)
    generated_files = []

    # ==========================================
    # DATA LOADING
    # ==========================================
    innov_cdf = load_da_variable(da_cdf.get('innov', []), 'innov_01')
    incr_cdf = load_da_variable(da_cdf.get('incr', []), 'anlys_incr_Soil Moisture Layer 1_01', extract_layer=0)
    incr_nocdf = load_da_variable(da_nocdf.get('incr', []), 'anlys_incr_Soil Moisture Layer 1_01', extract_layer=0)
    
    data_sm_ol = load_lis_variable(files_ol, 'SoilMoist_tavg')
    data_sm_nocdf = load_lis_variable(files_nocdf, 'SoilMoist_tavg') if files_nocdf else None
    data_sm_cdf = load_lis_variable(files_cdf, 'SoilMoist_tavg') if files_cdf else None
    
    data_et_ol = load_lis_variable(files_ol, 'Evap_tavg')
    data_et_nocdf = load_lis_variable(files_nocdf, 'Evap_tavg') if files_nocdf else None
    data_et_cdf = load_lis_variable(files_cdf, 'Evap_tavg') if files_cdf else None

    sm_ol_l1 = data_sm_ol[:, 0, :, :] if data_sm_ol is not None else None
    sm_nocdf_l1 = data_sm_nocdf[:, 0, :, :] if data_sm_nocdf is not None else None
    sm_cdf_l1 = data_sm_cdf[:, 0, :, :] if data_sm_cdf is not None else None
    
    mult_et = 86400.0
    et_ol = data_et_ol * mult_et if data_et_ol is not None else None
    et_nocdf = data_et_nocdf * mult_et if data_et_nocdf is not None else None
    et_cdf = data_et_cdf * mult_et if data_et_cdf is not None else None

    # ==========================================
    # FIGURE 1: ASSIMILATION DIAGNOSTICS
    # ==========================================
    fig1, axes1 = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
    
    # (a) Assimilated SMAP observation relative frequency
    if innov_cdf is not None:
        obs_count = np.sum(~np.isnan(innov_cdf), axis=0)
        max_cycles = innov_cdf.shape[0]
        obs_freq = np.where(obs_count > 0, (obs_count / max_cycles) * 100, np.nan)
        valid_freq = obs_freq[~np.isnan(obs_freq)]
        if len(valid_freq) > 0:
            p2, p98 = np.nanpercentile(valid_freq, 2), np.nanpercentile(valid_freq, 98)
            vmin = max(0, np.floor(p2))
            vmax = min(100, np.ceil(p98))
            if vmin >= vmax:
                vmin = max(0, vmin - 5)
                vmax = min(100, vmax + 5)
            # Ensure nice round levels
            levels_a = np.linspace(vmin, vmax, 10)
            levels_a = np.unique(levels_a) # Ensure strictly increasing
            if len(levels_a) < 2:
                levels_a = np.linspace(0, 100, 10)
            plot_spatial(axes1[0,0], obs_freq, mask, 'viridis', levels_a, 
                         "(a) Assimilated SMAP observation frequency — CDF", "Assimilation frequency (%)", extend='both')

    # (b) Mean innovation
    if innov_cdf is not None:
        mean_innov = np.nanmean(np.where((innov_cdf > -1) & (innov_cdf < 1), innov_cdf, np.nan), axis=0)
        levels_b = [-0.05, -0.04, -0.03, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.03, 0.04, 0.05]
        plot_spatial(axes1[0,1], mean_innov, mask, 'RdBu_r', levels_b, 
                     "(b) Mean innovation: SMAP − forecast", "Innovation (m³ m⁻³)")

    # (c) Mean analysis increment
    if incr_cdf is not None:
        mean_incr = np.nanmean(np.where((incr_cdf > -1) & (incr_cdf < 1), incr_cdf, np.nan), axis=0)
        levels_c = [-0.003, -0.002, -0.001, -0.0005, 0.0005, 0.001, 0.002, 0.003]
        plot_spatial(axes1[1,0], mean_incr, mask, 'RdBu_r', levels_c, 
                     "(c) Mean analysis increment", "Analysis increment (m³ m⁻³)")

    # (d) Increment distribution
    if incr_cdf is not None and incr_nocdf is not None:
        c_valid = incr_cdf[~np.isnan(incr_cdf)]
        n_valid = incr_nocdf[~np.isnan(incr_nocdf)]
        
        c_flat = c_valid[(c_valid > -0.1) & (c_valid < 0.1)]
        n_flat = n_valid[(n_valid > -0.1) & (n_valid < 0.1)]
        
        bins = np.arange(-0.05, 0.051, 0.002)
        
        axes1[1,1].hist(n_flat, bins=bins, histtype='step', linewidth=1.8, color='#E69F00', label='DA-NoCDF', density=True)
        axes1[1,1].hist(c_flat, bins=bins, histtype='step', linewidth=1.8, color='#0072B2', label='DA-CDF', density=True)
        axes1[1,1].axvline(0, color='k', linestyle=':', linewidth=1)
        axes1[1,1].set_xlim([-0.05, 0.05])
        axes1[1,1].set_yscale('log')
        axes1[1,1].set_xlabel('Analysis increment (m³ m⁻³)')
        axes1[1,1].set_ylabel('Log density')
        axes1[1,1].set_title('(d) Analysis increment distribution', loc='left')
        
        # Add stats text
        stats_text = (f"DA-NoCDF (μ={np.mean(n_flat):.4f})\n"
                      f"DA-CDF (μ={np.mean(c_flat):.4f})")
        axes1[1,1].text(0.05, 0.95, stats_text, transform=axes1[1,1].transAxes, 
                        fontsize=8, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        axes1[1,1].legend(loc='upper right')
        axes1[1,1].set_facecolor('white')

    out1_png = os.path.join(out_dir, "01_assimilation_diagnostics.png")
    out1_pdf = os.path.join(out_dir, "01_assimilation_diagnostics.pdf")
    fig1.savefig(out1_png, dpi=300, bbox_inches='tight')
    fig1.savefig(out1_pdf, bbox_inches='tight')
    plt.close(fig1)
    generated_files.extend([out1_png, out1_pdf])

    # ==========================================
    # FIGURE 2: HYDROLOGICAL RESPONSE
    # ==========================================
    fig2, axes2 = plt.subplots(2, 2, figsize=(10, 8), constrained_layout=True)
    
    levels_ef = [-0.05, -0.03, -0.02, -0.01, -0.005, 0.005, 0.01, 0.02, 0.03, 0.05]
    
    # (a) DA-NoCDF - OPL SSM
    if sm_nocdf_l1 is not None and sm_ol_l1 is not None:
        diff_nocdf_opl = np.nanmean(sm_nocdf_l1 - sm_ol_l1, axis=0)
        plot_spatial(axes2[0,0], diff_nocdf_opl, mask, 'RdBu_r', levels_ef, 
                     "(a) Surface soil moisture change: DA-NoCDF − open loop", "ΔSSM (m³ m⁻³)")

    # (b) DA-CDF - OPL SSM
    if sm_cdf_l1 is not None and sm_ol_l1 is not None:
        diff_cdf_opl = np.nanmean(sm_cdf_l1 - sm_ol_l1, axis=0)
        plot_spatial(axes2[0,1], diff_cdf_opl, mask, 'RdBu_r', levels_ef, 
                     "(b) Surface soil moisture change: DA-CDF − open loop", "ΔSSM (m³ m⁻³)")

    # (c) DA-NoCDF - DA-CDF SSM
    if sm_nocdf_l1 is not None and sm_cdf_l1 is not None:
        diff_nocdf_cdf = np.nanmean(sm_nocdf_l1 - sm_cdf_l1, axis=0)
        levels_g = [-0.02, -0.015, -0.01, -0.005, -0.0025, 0.0025, 0.005, 0.01, 0.015, 0.02]
        plot_spatial(axes2[1,0], diff_nocdf_cdf, mask, 'RdBu_r', levels_g, 
                     "(c) Surface soil moisture change: DA-NoCDF − DA-CDF", "ΔSSM (m³ m⁻³)")

    # (d) ET time series
    if et_ol is not None and start_date is not None:
        axes2[1,1].set_facecolor('white')
        ts_ol = calculate_basin_average(et_ol, mask)
        dates = [start_date + timedelta(days=i) for i in range(len(ts_ol))]
        
        axes2[1,1].plot(dates, ts_ol, color='#333333', linewidth=1.8, label='Open loop')
        
        max_val = np.nanmax(ts_ol)
        
        if et_nocdf is not None:
            ts_nocdf = calculate_basin_average(et_nocdf, mask)
            axes2[1,1].plot(dates, ts_nocdf, color='#E69F00', linewidth=1.8, label='DA-NoCDF', alpha=0.9)
            max_val = max(max_val, np.nanmax(ts_nocdf))
            
        if et_cdf is not None:
            ts_cdf = calculate_basin_average(et_cdf, mask)
            axes2[1,1].plot(dates, ts_cdf, color='#0072B2', linewidth=1.8, label='DA-CDF', alpha=0.9)
            max_val = max(max_val, np.nanmax(ts_cdf))
            
        axes2[1,1].set_title('(d) Basin-averaged evapotranspiration — 2016', loc='left')
        axes2[1,1].set_ylabel('ET (mm day⁻¹)')
        axes2[1,1].set_xlabel('Date')
        axes2[1,1].legend()
        axes2[1,1].grid(color='lightgrey', linestyle='--', linewidth=0.5)
        
        axes2[1,1].set_ylim(0, max(1.8, max_val * 1.05))
        
        axes2[1,1].xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        axes2[1,1].xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        plt.setp(axes2[1,1].xaxis.get_majorticklabels(), rotation=45, ha='right')

    out2_png = os.path.join(out_dir, "02_hydrological_response.png")
    out2_pdf = os.path.join(out_dir, "02_hydrological_response.pdf")
    fig2.savefig(out2_png, dpi=300, bbox_inches='tight')
    fig2.savefig(out2_pdf, bbox_inches='tight')
    plt.close(fig2)
    generated_files.extend([out2_png, out2_pdf])

    return generated_files
