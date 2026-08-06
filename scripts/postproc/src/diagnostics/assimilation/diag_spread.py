# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import os
import glob
from datetime import timedelta
import calendar
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter

from .utils import get_lat_lon, add_map_features


def extract_spread_data(config, base_dir_da):
    start_date = config['start_date']
    end_date = config['end_date']
    
    lat, lon = get_lat_lon(base_dir_da, start_date)
    if lat is None: return None, None, None, None, None
    
    grid_shape = (len(lat), len(lon))
    
    # 1. Extract Forecast Observation-Space Uncertainty (innov)
    spread_sum = np.zeros(grid_shape)
    counts_spread = np.zeros(grid_shape)
    
    curr_date = start_date
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        innov_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
        
        for f in innov_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'forecast_sigma_01' in ds.variables:
                    sprd = ds.variables['forecast_sigma_01'][:]
                    if np.ma.is_masked(sprd):
                        sprd = sprd.filled(-9999)
                        
                    mask_sprd = np.where((sprd > -100) & (sprd < 100), 1, 0)
                    valid_sprd = np.where(mask_sprd == 1, sprd, 0)
                    
                    spread_sum += valid_sprd
                    counts_spread += mask_sprd
                ds.close()
            except:
                pass
                
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    data_raw = np.where(counts_spread > 0, spread_sum / counts_spread, np.nan)
    
    # 2. Extract State Ensemble Spread snapshot (spread)
    posterior_names = [
        'posterior ensemble spread', 'analysis ensemble spread', 
        'posterior spread', 'analysis spread', 'ens_spread_post', 
        'ens_spread_analysis', 'post_ens_spread', 'anl_ens_spread',
        'ensspread_Soil Moisture Layer 1_01', 'analysis_sigma_01'
    ]
    
    posterior_var_found = None
    posterior_files_type = None
    
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    sample_spread_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*.nc"))
    if sample_spread_files:
        for ds_file in sample_spread_files:
            try:
                with nc.Dataset(ds_file, 'r') as ds:
                    for v in ds.variables:
                        if v in posterior_names:
                            posterior_var_found = v
                            posterior_files_type = ds_file.split('_')[-1].split('.')[0]
                            break
            except:
                pass
            if posterior_var_found:
                break
                
    if not posterior_var_found:
        print("WARNING: Ensemble spread variable not found among the suggested names.")
        return data_raw, None, None, lat, lon
        
    post_spread_sum = np.zeros(grid_shape)
    post_counts = np.zeros(grid_shape)
    
    curr_date = start_date
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        post_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", f"*_{posterior_files_type}*.nc"))
        
        for f in post_files:
            try:
                with nc.Dataset(f, 'r') as ds:
                    if posterior_var_found in ds.variables:
                        sprd = ds.variables[posterior_var_found][:]
                        if np.ma.is_masked(sprd):
                            sprd = sprd.filled(np.nan)
                            
                        # Correct if it is expressed as a percentage
                        mask_sprd = np.where(~np.isnan(sprd) & (sprd > -10) & (sprd < 100), 1, 0)
                        if "ensspread" in posterior_var_found:
                            valid_temp = sprd[mask_sprd == 1]
                            if len(valid_temp) > 0 and np.nanmean(valid_temp) > 0.05:
                                sprd = sprd / 100.0
                                
                        valid_sprd = np.where(mask_sprd == 1, sprd, 0)
                        
                        post_spread_sum += valid_sprd
                        post_counts += mask_sprd
            except:
                pass
                
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    post_raw = np.where(post_counts > 0, post_spread_sum / post_counts, np.nan)
    return data_raw, post_raw, posterior_var_found, lat, lon


def plot_spread_diagnostics_consistency_check(config, out_dir, data_raw, post_raw, posterior_var_found, lat, lon):
    cfg = config.get("spread_diagnostics_consistency_check", {})
    if not cfg.get("enabled", True):
        return
        
    print("\nRunning spread diagnostics consistency check...")
    print("WARNING: forecast_sigma_01 and ensspread_Soil Moisture Layer 1_01 are not directly comparable. Only a diagnostic consistency-check figure is generated.\n")

    prior_valid_mask = np.isfinite(data_raw)
    posterior_valid_mask = np.isfinite(post_raw)
    
    common_valid_mask = prior_valid_mask & posterior_valid_mask
    prior_only_mask = prior_valid_mask & ~posterior_valid_mask
    posterior_only_mask = posterior_valid_mask & ~prior_valid_mask
    
    cat = cfg.get("categories", {})
    mask_diff = np.ones_like(data_raw, dtype=int) * 0
    mask_diff[common_valid_mask] = 1
    mask_diff[prior_only_mask] = 2
    mask_diff[posterior_only_mask] = 3
    
    lcfg = cfg.get("layout", {})
    fig = plt.figure(figsize=(lcfg.get("figure_width", 14), lcfg.get("figure_height", 5.5)))
    fig.subplots_adjust(
        left=lcfg.get("left", 0.04), right=lcfg.get("right", 0.98),
        bottom=lcfg.get("bottom", 0.15), top=lcfg.get("top", 0.82),
        wspace=lcfg.get("wspace", 0.08)
    )
    
    tcfg = cfg.get("title", {})
    fig.suptitle(tcfg.get("main", "Spread diagnostic consistency check"), 
                 fontsize=tcfg.get("main_fontsize", 13), 
                 fontweight=tcfg.get("main_fontweight", "bold"), y=0.97)
    
    fig.text(0.5, 0.92, tcfg.get("subtitle", "forecast_sigma_01 and ensspread are not directly comparable | DA-noCDF-noIRR experiment"),
             ha='center', va='center', fontsize=tcfg.get("subtitle_fontsize", 10))
    
    ax1 = fig.add_subplot(1, 3, 1, projection=ccrs.PlateCarree())
    ax2 = fig.add_subplot(1, 3, 2, projection=ccrs.PlateCarree())
    ax3 = fig.add_subplot(1, 3, 3, projection=ccrs.PlateCarree())
    
    map_cfg = cfg.get("map", {})
    gl_cfg = cfg.get("gridlines", {})
    for i, ax in enumerate([ax1, ax2, ax3]):
        add_map_features(ax, map_cfg=map_cfg, gl_cfg=gl_cfg)
        ax.set_xticks([-9, -7.5, -6, -4.5, -3, -1.5], crs=ccrs.PlateCarree())
        ax.set_yticks([30, 31, 32, 33, 34, 35, 36], crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(zero_direction_label=True)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        ax.tick_params(axis='both', labelsize=8)
        if i > 0:
            ax.set_yticklabels([])
        
    p_tcfg = cfg.get("panel_titles", {})
    pt_fs = p_tcfg.get("main_fontsize", 10)
    pt_sub_fs = p_tcfg.get("subtitle_fontsize", 8)
    pt_fw = p_tcfg.get("main_fontweight", "bold")
    
    mp_cfg = cfg.get("mask_panels", {})
    invalid_c = mp_cfg.get("invalid_color", "#E0E0E0")
    valid_c = mp_cfg.get("valid_color", "#1B9E77")
    cmap_binary = mcolors.ListedColormap([invalid_c, valid_c])
    
    ax1.set_title(p_tcfg.get("forecast_sigma", {}).get("main", "(a) forecast_sigma_01 valid mask") + "\n" +
                  p_tcfg.get("forecast_sigma", {}).get("subtitle", ""), fontsize=pt_fs, fontweight=pt_fw)
    ax1.pcolormesh(lon, lat, prior_valid_mask, cmap=cmap_binary, transform=ccrs.PlateCarree())
    
    ax2.set_title(p_tcfg.get("ensspread", {}).get("main", "(b) ensspread valid mask") + "\n" +
                  p_tcfg.get("ensspread", {}).get("subtitle", ""), fontsize=pt_fs, fontweight=pt_fw)
    ax2.pcolormesh(lon, lat, posterior_valid_mask, cmap=cmap_binary, transform=ccrs.PlateCarree())
    
    ax3.set_title(p_tcfg.get("mask_difference", {}).get("main", "(c) Mask difference") + "\n" +
                  p_tcfg.get("mask_difference", {}).get("subtitle", ""), fontsize=pt_fs, fontweight=pt_fw)
                  
    cmap_diff = mcolors.ListedColormap([
        cat.get("invalid_both", {}).get("color", "#E0E0E0"),
        cat.get("valid_both", {}).get("color", "#1B9E77"),
        cat.get("forecast_sigma_only", {}).get("color", "#D95F02"),
        cat.get("ensspread_only", {}).get("color", "#377EB8")
    ])
    ax3.pcolormesh(lon, lat, mask_diff, cmap=cmap_diff, vmin=-0.5, vmax=3.5, transform=ccrs.PlateCarree())
    
    legend_elements = [
        mpatches.Patch(color=cat.get("invalid_both", {}).get("color", "#E0E0E0"), label=cat.get("invalid_both", {}).get("label", "Invalid both")),
        mpatches.Patch(color=cat.get("valid_both", {}).get("color", "#1B9E77"), label=cat.get("valid_both", {}).get("label", "Common valid")),
        mpatches.Patch(color=cat.get("forecast_sigma_only", {}).get("color", "#D95F02"), label=cat.get("forecast_sigma_only", {}).get("label", "forecast_sigma only")),
        mpatches.Patch(color=cat.get("ensspread_only", {}).get("color", "#377EB8"), label=cat.get("ensspread_only", {}).get("label", "ensspread only"))
    ]
    ax3.legend(handles=legend_elements, loc='lower center', bbox_to_anchor=(0.5, -0.35), ncol=2, frameon=False, fontsize=9)
    
    n_p = np.sum(prior_valid_mask)
    n_pos = np.sum(posterior_valid_mask)
    n_com = np.sum(common_valid_mask)
    n_po = np.sum(prior_only_mask)
    n_poso = np.sum(posterior_only_mask)
    
    print(f"forecast_sigma valid = {n_p} cells")
    print(f"ensspread valid = {n_pos} cells")
    print(f"common valid = {n_com} cells")
    
    sb_cfg = cfg.get("statistics_box", {})
    if sb_cfg.get("enabled", True):
        box_text = "\n".join([line.format(
            n_forecast_sigma_valid=n_p,
            n_ensspread_valid=n_pos,
            n_common_valid=n_com,
            n_forecast_sigma_only=n_po,
            n_ensspread_only=n_poso
        ) for line in sb_cfg.get("content", [])])
        
        props = dict(boxstyle="round,pad=0.30", facecolor="white", alpha=0.85, edgecolor="0.4", linewidth=0.5)
        ax1.text(0.0, -0.15, box_text, transform=ax1.transAxes, fontsize=sb_cfg.get("fontsize", 8), ha='left', va='top', bbox=props)
    
    out_cfg = cfg.get("output", {})
    f_png = os.path.join(out_dir, out_cfg.get("filename", "Fig06_spread_diagnostics_consistency_check_DA-noCDF-noIRR_2016.png"))
    fig.savefig(f_png, dpi=out_cfg.get("dpi", 300), bbox_inches=out_cfg.get("bbox_inches", "tight"))
    plt.close(fig)
    
    print(f"Spread diagnostics consistency check completed. Figure saved: {f_png}")


def plot_prior_posterior_spread_comparison(config, out_dir, data_raw, post_raw, posterior_var_found, lat, lon):
    cfg = config.get("prior_posterior_spread_comparison", {})
    if not cfg.get("enabled", True):
        return
        
    print("\nRunning prior_posterior_spread_comparison...")
    
    # 1. Apply sqrt if configured, and scale
    forecast_sigma = data_raw.copy()
    if cfg.get("scientific_context", {}).get("compute_sqrt_forecast_sigma", True):
        forecast_sigma = np.where(forecast_sigma >= 0, np.sqrt(forecast_sigma), np.nan)
        
    scale_factor = 1000.0
    forecast_plot = forecast_sigma * scale_factor
    ensspread_plot = post_raw * scale_factor
    
    # 2. Apply common mask
    prior_valid_mask = np.isfinite(forecast_plot)
    posterior_valid_mask = np.isfinite(ensspread_plot)
    final_mask = prior_valid_mask & posterior_valid_mask
    
    forecast_plot_masked = np.where(final_mask, forecast_plot, np.nan)
    ensspread_plot_masked = np.where(final_mask, ensspread_plot, np.nan)
    
    forecast_values = forecast_plot_masked[final_mask]
    ensspread_values = ensspread_plot_masked[final_mask]
    n_valid = len(forecast_values)
    
    # 3. Setup Layout
    fig = plt.figure(figsize=(10.5, 7.5))
    
    gs = fig.add_gridspec(
        nrows=2,
        ncols=2,
        width_ratios=[1.0, 1.0],
        height_ratios=[1.0, 0.85],
        left=0.06, right=0.90,
        bottom=0.08, top=0.90,
        wspace=0.25, hspace=0.20
    )
    
    fig.suptitle("Spread-related diagnostics | DA-noCDF-noIRR, 2016", 
                 fontsize=14, y=0.97)
    
    ax1 = fig.add_subplot(gs[0, 0], projection=ccrs.PlateCarree())
    ax2 = fig.add_subplot(gs[0, 1], projection=ccrs.PlateCarree())
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])
    
    map_cfg = cfg.get("map", {})
    map_cfg["coastline_color"] = "gray"
    map_cfg["coastline_linewidth"] = 0.5
    map_cfg["border_color"] = "gray"
    map_cfg["border_linewidth"] = 0.4
    
    gl_cfg = cfg.get("gridlines", {})
    gl_cfg["linewidth"] = 0.3
    gl_cfg["alpha"] = 0.4
    gl_cfg["color"] = "lightgray"
    
    for ax in [ax1, ax2]:
        gl = add_map_features(ax, map_cfg=map_cfg, gl_cfg=gl_cfg)
        # Suppress cartopy gridliner labels to avoid overlapping with matplotlib ticks
        gl.bottom_labels = False
        gl.left_labels = False
        gl.top_labels = False
        gl.right_labels = False
        
        ax.set_xticks([-9, -7.5, -6, -4.5, -3, -1.5], crs=ccrs.PlateCarree())
        ax.set_yticks([30, 31, 32, 33, 34, 35, 36], crs=ccrs.PlateCarree())
        lon_formatter = LongitudeFormatter(zero_direction_label=True)
        lat_formatter = LatitudeFormatter()
        ax.xaxis.set_major_formatter(lon_formatter)
        ax.yaxis.set_major_formatter(lat_formatter)
        
        # Keep longitude on both bottoms, latitude only on the left map
        is_left = (ax == ax1)
        ax.tick_params(axis='both', labelsize=8, 
                       bottom=True, top=False, 
                       left=is_left, right=False, 
                       labelbottom=True, labeltop=False, 
                       labelleft=is_left, labelright=False)
        
    # ---------------------------
    # Panel (a) and (b) Colorbars setup
    # ---------------------------
    fc_bounds = [0, 20, 30, 40, 45, 50, 55, 60, 70]
    cmap1 = plt.get_cmap("YlOrBr", len(fc_bounds) - 1).copy()
    cmap1.set_bad(color="#F0F0F0")
    norm1 = mcolors.BoundaryNorm(fc_bounds, ncolors=cmap1.N, clip=True)
    
    es_bounds = [0, 0.5, 1.0, 1.3, 1.6, 1.8, 2.0, 2.5, 3.0, 4.0]
    cmap2 = plt.get_cmap("YlOrBr", len(es_bounds) - 1).copy()
    cmap2.set_bad(color="#F0F0F0")
    norm2 = mcolors.BoundaryNorm(es_bounds, ncolors=cmap2.N, clip=True)
    
    cbar_label1 = "Forecast uncertainty (×10⁻³ m³ m⁻³)"
    cbar_label2 = "Model-state spread (×10⁻³ m³ m⁻³)"
    cbar_ticks1 = [0, 10, 20, 30, 40, 50, 60, 70]
    cbar_ticks2 = [0, 1, 2, 3, 4]
    
    # ---------------------------
    # Panel (a)
    # ---------------------------
    ax1.set_title("(a) Forecast uncertainty", fontsize=11)
    pcm1 = ax1.pcolormesh(lon, lat, forecast_plot_masked, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    
    # ---------------------------
    # Panel (b)
    # ---------------------------
    ax2.set_title("(b) Model-state spread", fontsize=11)
    pcm2 = ax2.pcolormesh(lon, lat, ensspread_plot_masked, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    
    fig.canvas.draw()
    
    cb_width = 0.012
    cb_pad = 0.015
    
    pos1 = ax1.get_position()
    cax1 = fig.add_axes([pos1.x1 + cb_pad, pos1.y0, cb_width, pos1.height])
    cbar1 = fig.colorbar(pcm1, cax=cax1, orientation="vertical", extend="max")
    cbar1.set_ticks(cbar_ticks1)
    cbar1.set_label(cbar_label1, fontsize=10)
    cbar1.ax.tick_params(labelsize=8)
    
    pos2 = ax2.get_position()
    cax2 = fig.add_axes([pos2.x1 + cb_pad, pos2.y0, cb_width, pos2.height])
    cbar2 = fig.colorbar(pcm2, cax=cax2, orientation="vertical", extend="max")
    cbar2.set_ticks(cbar_ticks2)
    cbar2.set_label(cbar_label2, fontsize=10)
    cbar2.ax.tick_params(labelsize=8)
    
    # ---------------------------
    # Panel (c) and (d) Histograms
    # ---------------------------
    bins = 60
    
    weights1 = np.ones_like(forecast_values) * 100.0 / n_valid if n_valid > 0 else None
    weights2 = np.ones_like(ensspread_values) * 100.0 / n_valid if n_valid > 0 else None
    
    ax3.set_title("(c) Forecast uncertainty distribution", fontsize=11)
    ax3.hist(forecast_values, bins=bins, weights=weights1, color="#D95F02", alpha=0.85, edgecolor="0.25", linewidth=0.5)
    ax3.set_xlabel("Forecast uncertainty (×10⁻³ m³ m⁻³)", fontsize=10)
    ax3.set_ylabel("Frequency (%)", fontsize=10)
    ax3.set_xlim(0, 70)
    ax3.tick_params(labelsize=9)
    
    if n_valid > 0:
        ax3.axvline(np.nanmean(forecast_values), color='k', linestyle='--', linewidth=1.2, label="Mean")
        ax3.axvline(np.nanmedian(forecast_values), color='k', linestyle='-.', linewidth=1.2, label="Median")
        ax3.axvline(np.nanpercentile(forecast_values, 95), color='k', linestyle=':', linewidth=1.2, label="P95")
    ax3.legend(loc='upper right', fontsize=8, frameon=False)
    
    ax4.set_title("(d) Model-state spread distribution", fontsize=11)
    ax4.hist(ensspread_values, bins=bins, weights=weights2, color="#377EB8", alpha=0.85, edgecolor="0.25", linewidth=0.5)
    ax4.set_xlabel("Model-state spread (×10⁻³ m³ m⁻³)", fontsize=10)
    ax4.set_ylabel("Frequency (%)", fontsize=10)
    ax4.set_xlim(0, 5)
    ax4.tick_params(labelsize=9)
    
    ylim3 = ax3.get_ylim()
    ax4.set_ylim(ylim3)
    
    if n_valid > 0:
        ax4.axvline(np.nanmean(ensspread_values), color='k', linestyle='--', linewidth=1.2, label="Mean")
        ax4.axvline(np.nanmedian(ensspread_values), color='k', linestyle='-.', linewidth=1.2, label="Median")
        ax4.axvline(np.nanpercentile(ensspread_values, 95), color='k', linestyle=':', linewidth=1.2, label="P95")
    ax4.legend(loc='upper right', fontsize=8, frameon=False)
    
    f_png = os.path.join(out_dir, "Fig07_spread_related_diagnostics_obsspace_vs_state_DA-noCDF-noIRR_2016.png")
    fig.savefig(f_png, dpi=400, bbox_inches="tight")
    plt.close(fig)
    
    print(f"Spread comparative figure completed. Figure saved: {f_png}")


def run_spread(config, base_dir_da, out_dir):
    data_raw, post_raw, posterior_var_found, lat, lon = extract_spread_data(config, base_dir_da)
    if lat is None or posterior_var_found is None:
        return
        
    plot_spread_diagnostics_consistency_check(config, out_dir, data_raw, post_raw, posterior_var_found, lat, lon)
    plot_prior_posterior_spread_comparison(config, out_dir, data_raw, post_raw, posterior_var_found, lat, lon)
