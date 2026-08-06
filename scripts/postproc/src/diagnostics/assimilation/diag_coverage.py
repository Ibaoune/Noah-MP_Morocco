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
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs

from .utils import get_lat_lon, add_map_features, generate_filename

def run_coverage(config, base_dir_da, out_dir):
    print("Running coverage diagnostics...")
    
    start_date = config['start_date']
    end_date = config['end_date']
    exp_name = config['experiment_name']
    year_str = end_date.strftime('%Y')
    period_str = f"{start_date.strftime('%b %Y')}–{end_date.strftime('%b %Y')}"
    
    # We just need to find one file to get lat/lon
    # We will search the first month
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    sample_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
    if not sample_files:
        print("No DA files found to determine grid.")
        return
        
    lat, lon = get_lat_lon(base_dir_da, start_date)
    if lat is None: return
    
    grid_shape = (len(lat), len(lon))
    total_obs = np.zeros(grid_shape)
    assim_days = np.zeros(grid_shape)
    
    monthly_totals = []
    month_labels = []
    
    curr_date = start_date
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        innov_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
        
        month_obs = np.zeros(grid_shape)
        
        for f in innov_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'innov_01' in ds.variables:
                    inv = ds.variables['innov_01'][:]
                    if np.ma.is_masked(inv):
                        inv = inv.filled(-9999)
                    
                    mask_inv = np.where((inv > -100) & (inv < 100), 1, 0)
                    month_obs += mask_inv
                ds.close()
            except:
                pass
                
        total_obs += month_obs
        days_with_obs = np.where(month_obs > 0, 1, 0)
        assim_days += days_with_obs
        
        monthly_totals.append(np.sum(month_obs))
        month_labels.append(curr_date.strftime('%b'))
        
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    total_days = (end_date - start_date).days + 1
    assim_freq = np.where(assim_days > 0, total_obs / total_days, 0)
    total_obs_plot = np.where(total_obs > 0, total_obs, np.nan)
    assim_freq_plot = np.where(assim_freq > 0, assim_freq, np.nan)
    
    # Before plotting, print and check
    data_min = np.nanmin(total_obs_plot)
    data_max = np.nanmax(total_obs_plot)
    valid_cells = np.sum(~np.isnan(total_obs_plot))
    nan_cells = np.sum(np.isnan(total_obs_plot))
    print(f"Data min: {data_min}, max: {data_max}")
    print(f"Valid cells: {valid_cells}, NaN cells: {nan_cells}")
    if data_max > 800:
        raise ValueError(f"Max value {data_max} is > 800. This is not the correct variable (likely indices or frequency).")

    # ---------------------------------------------------------
    # Fig 1: Total Assimilated Obs
    # ---------------------------------------------------------
    cfg = config.get("assimilation_observations_map", {})
    
    # Layout config
    lcfg = cfg.get("layout", {})
    fig1 = plt.figure(figsize=(9, 7))
    fig1.subplots_adjust(
        left=lcfg.get("left", 0.07),
        right=lcfg.get("right", 0.88),
        bottom=lcfg.get("bottom", 0.08),
        top=lcfg.get("top", 0.88)
    )
    
    ax1 = fig1.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    map_cfg = cfg.get("map", {})
    gl_cfg = cfg.get("gridlines", {})
    gl1 = add_map_features(ax1, map_cfg=map_cfg, gl_cfg=gl_cfg)
    
    # Fonts and styling
    plt.rcParams.update({'font.size': 10, 'axes.labelsize': 10, 'xtick.labelsize': 9, 'ytick.labelsize': 9})
    
    # Title - Removed per request
    
    # Colormap
    cm_cfg = cfg.get("colormap", {})
    cb_cfg = cfg.get("colorbar", {})
    
    levels1 = cb_cfg.get("bounds", [0, 25, 50, 75, 100, 125, 150, 175, 200, 225, 250, 275])
    cmap_name = cm_cfg.get("name", "YlGnBu")
    
    if cm_cfg.get("discrete", True):
        cmap1 = plt.get_cmap(cmap_name, len(levels1) - 1).copy()
    else:
        cmap1 = plt.get_cmap(cmap_name).copy()
        
    cmap1.set_bad(color=cm_cfg.get("bad_color", "lightgrey"))
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, total_obs_plot, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    
    if cb_cfg.get("align_to_map_height", True):
        fig1.canvas.draw()  # Required for Cartopy to resolve actual aspect ratio map height
        pos = ax1.get_position()
        
        # Apply shrink factor to height, center it vertically relative to map
        shrink = cb_cfg.get("shrink", 1.0)
        cb_height = pos.height * shrink
        cb_y0 = pos.y0 + (pos.height - cb_height) / 2.0
        
        cax = fig1.add_axes([
            pos.x1 + cb_cfg.get("pad", 0.015),
            cb_y0,
            cb_cfg.get("width", 0.02),
            cb_height
        ])
        cbar1 = fig1.colorbar(pcm1, cax=cax, orientation=cb_cfg.get("orientation", "vertical"), extend=cb_cfg.get("extend", "neither"))
    else:
        cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation=cb_cfg.get("orientation", "vertical"), 
                              pad=cb_cfg.get("pad", 0.025), fraction=cb_cfg.get("width", 0.035))
        
    cbar1.set_ticks(cb_cfg.get("ticks", levels1))
    cbar1.set_label(cb_cfg.get("label", "Assimilated SMAP observations"), fontsize=cb_cfg.get("label_fontsize", 11))
    cbar1.ax.tick_params(labelsize=cb_cfg.get("tick_fontsize", 9))
    
    # Annotation box
    ann_cfg = cfg.get("annotation", {})
    if ann_cfg.get("enabled", True):
        tmpl = "Max = {data_max:.0f} obs"
        box_text = tmpl.format(data_max=data_max)
        props = dict(boxstyle="square,pad=0.25", facecolor="white", alpha=0.85, edgecolor="none")
        ax1.text(0.02, 0.98, box_text, transform=ax1.transAxes, fontsize=8, 
                 ha="left", va="top", bbox=props)
    
    out_cfg = cfg.get("output", {})
    f1_png = os.path.join(out_dir, out_cfg.get("filename", "Fig01_smap_assimilated_observation_count_DA-noCDF-noIRR_2016.png"))
    fig1.savefig(f1_png, dpi=out_cfg.get("dpi", 300), bbox_inches=out_cfg.get("bbox_inches", "tight"))
    plt.close(fig1)
    
    # ---------------------------------------------------------
    # Fig 2: Assimilation Frequency and Monthly Totals
    # ---------------------------------------------------------
    data_min2 = np.nanmin(assim_freq_plot)
    data_max2 = np.nanmax(assim_freq_plot)
    
    print("Variable: assim_freq_plot")
    print(f"Data min: {data_min2}, max: {data_max2}")
    if data_max2 > 10:
        raise ValueError(f"Max value {data_max2} is > 10. This is not the correct variable.")
        
    print("Variable: monthly_totals")
    print(f"Monthly min: {np.nanmin(monthly_totals)}, max: {np.nanmax(monthly_totals)}")
    mean_monthly = np.nanmean(monthly_totals)
    
    cfg2 = config.get("assimilation_frequency_map", {})
    cfg3 = config.get("monthly_total_assimilated_obs", {})
    
    # We create a 1x2 figure with GridSpec for 60/40 ratio
    fig2 = plt.figure(figsize=(12, 5.5))
    gs = gridspec.GridSpec(1, 2, width_ratios=[1.7, 1], wspace=0.15, left=0.04, right=0.96, bottom=0.18, top=0.82)
    
    # Title - Removed per request
    
    # Panel 1: Map
    ax2 = fig2.add_subplot(gs[0], projection=ccrs.PlateCarree())
    map_cfg2 = cfg2.get("map", {})
    gl_cfg2 = cfg2.get("gridlines", {})
    add_map_features(ax2, map_cfg=map_cfg2, gl_cfg=gl_cfg2)
    
    p_tcfg = cfg2.get("panel_titles", {})
    # Title - Removed per request
    
    cm_cfg2 = cfg2.get("colormap", {})
    cb_cfg2 = cfg2.get("colorbar", {})
    levels2 = cb_cfg2.get("bounds", [0.0, 0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    cmap_name2 = cm_cfg2.get("name", "YlOrRd")
    
    if cm_cfg2.get("discrete", True):
        cmap2 = plt.get_cmap(cmap_name2, len(levels2) - 1).copy()
    else:
        cmap2 = plt.get_cmap(cmap_name2).copy()
        
    cmap2.set_bad(color=cm_cfg2.get("bad_color", "#F0F0F0"))
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap2.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, assim_freq_plot, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    
    fig2.canvas.draw()
    pos2 = ax2.get_position()
    
    cbar_orientation = cb_cfg2.get("orientation", "horizontal")
    if cbar_orientation == "horizontal":
        cax2 = fig2.add_axes([pos2.x0 + 0.05, pos2.y0 - 0.09, pos2.width - 0.1, 0.025])
        cbar2 = fig2.colorbar(pcm2, cax=cax2, orientation="horizontal", extend=cb_cfg2.get("extend", "max"))
    else:
        cax2 = fig2.add_axes([pos2.x1 + 0.012, pos2.y0, 0.015, pos2.height])
        cbar2 = fig2.colorbar(pcm2, cax=cax2, orientation="vertical", extend=cb_cfg2.get("extend", "max"))
        
    cbar2.set_ticks(levels2)
    cbar2.set_label(cb_cfg2.get("label", "Assimilation frequency (obs d⁻¹)"), fontsize=cb_cfg2.get("label_fontsize", 10))
    cbar2.ax.tick_params(labelsize=cb_cfg2.get("tick_fontsize", 9))
    
    # Annotation box for Map
    ann_cfg2 = cfg2.get("annotation", {})
    if ann_cfg2.get("enabled", True):
        tmpl2 = "Max = {data_max:.2f} obs d⁻¹"
        box_text2 = tmpl2.format(data_max=data_max2)
        props2 = dict(boxstyle="square,pad=0.25", facecolor="white", alpha=0.85, edgecolor="none")
        ax2.text(0.02, 0.98, box_text2, transform=ax2.transAxes, fontsize=8, 
                 ha="left", va="top", bbox=props2)
                 
    # Panel 2: Bar Plot
    ax3 = fig2.add_subplot(gs[1])
    
    ax_cfg3 = cfg3.get("axes", {})
    scale_factor = ax_cfg3.get("y_scale_factor", 1000)
    monthly_totals_displayed = [v / scale_factor for v in monthly_totals]
    
    bars_cfg3 = cfg3.get("bars", {})
    bars = ax3.bar(month_labels, monthly_totals_displayed, 
                   color=bars_cfg3.get("color", "#899BAA"), 
                   edgecolor=bars_cfg3.get("edgecolor", "0.3"), 
                   linewidth=bars_cfg3.get("linewidth", 0.6),
                   width=bars_cfg3.get("width", 0.72),
                   alpha=bars_cfg3.get("alpha", 0.95))
                   
    p_tcfg3 = cfg3.get("panel_titles", {})
    # Title - Removed per request
    
    ax3.set_xlabel("Month", fontsize=ax_cfg3.get("xlabel_fontsize", 10))
    ax3.set_ylabel("Assimilated observations (×10³)", fontsize=ax_cfg3.get("ylabel_fontsize", 10))
    ax3.tick_params(axis='both', labelsize=ax_cfg3.get("tick_fontsize", 9))
    
    y_min = ax_cfg3.get("y_min", 0)
    y_max = ax_cfg3.get("y_max", 160)
    interval = ax_cfg3.get("y_tick_interval", 20)
    ax3.set_ylim(y_min, y_max)
    ax3.set_yticks(np.arange(y_min, y_max + interval, interval))
            
    grid_cfg3 = cfg3.get("grid", {})
    if grid_cfg3.get("enabled", True):
        ax3.grid(axis='y', linestyle='--', linewidth=0.5, color='0.8')
                 
    mean_cfg3 = cfg3.get("mean_line", {})
    if mean_cfg3.get("enabled", True):
        mean_val = mean_monthly / scale_factor
        ax3.axhline(mean_val, linestyle=mean_cfg3.get("linestyle", "--"), color=mean_cfg3.get("color", "0.3"), linewidth=mean_cfg3.get("linewidth", 1.0))
        ax3.text(len(month_labels) - 1, mean_val + 2, mean_cfg3.get("label", "2016 monthly mean"),
                 color=mean_cfg3.get("color", "0.3"), fontsize=8, ha='right', va='bottom')
        
    out_cfg2 = cfg2.get("output", {})
    f2_png = os.path.join(out_dir, out_cfg2.get("filename", "Fig02_smap_assimilation_frequency_DA-noCDF-noIRR_2016.png"))
    fig2.savefig(f2_png, dpi=out_cfg2.get("dpi", 300), bbox_inches="tight")
    plt.close(fig2)
