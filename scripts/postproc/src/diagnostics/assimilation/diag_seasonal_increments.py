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

from .utils import get_lat_lon, add_map_features, generate_filename

def run_seasonal_increments(config, base_dir_da, out_dir):
    print("Running seasonal increments diagnostics...")
    
    start_date = config['start_date']
    end_date = config['end_date']
    exp_name = config['experiment_name']
    year_str = end_date.strftime('%Y')
    
    cfg5 = config.get("seasonal_increment_wet_dry", {})
    s_cfg = cfg5.get("seasons", {})
    
    month_map = {"Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6, 
                 "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12}
                 
    wet_str = s_cfg.get("wet", {}).get("months", ["Nov", "Dec", "Jan", "Feb", "Mar", "Apr"])
    dry_str = s_cfg.get("dry", {}).get("months", ["May", "Jun", "Jul", "Aug", "Sep", "Oct"])
    
    wet_months = [month_map.get(m[:3].capitalize(), 1) for m in wet_str]
    dry_months = [month_map.get(m[:3].capitalize(), 1) for m in dry_str]
    
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    sample_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
    if not sample_files:
        return
        
    lat, lon = get_lat_lon(base_dir_da, start_date)
    if lat is None: return
    
    grid_shape = (len(lat), len(lon))
    incr_sum_wet = np.zeros(grid_shape)
    counts_incr_wet = np.zeros(grid_shape)
    incr_sum_dry = np.zeros(grid_shape)
    counts_incr_dry = np.zeros(grid_shape)
    
    curr_date = start_date
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        is_wet = curr_date.month in wet_months
        is_dry = curr_date.month in dry_months
        
        incr_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_incr.a01.d01.nc"))
        for f in incr_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'anlys_incr_Soil Moisture Layer 1_01' in ds.variables:
                    inc = ds.variables['anlys_incr_Soil Moisture Layer 1_01'][:]
                    if np.ma.is_masked(inc):
                        inc = inc.filled(-9999)
                        
                    mask_inc = np.where((inc > -100) & (inc < 100), 1, 0)
                    valid_inc = np.where(mask_inc == 1, inc, 0)
                    
                    if is_wet:
                        incr_sum_wet += valid_inc
                        counts_incr_wet += mask_inc
                    elif is_dry:
                        incr_sum_dry += valid_inc
                        counts_incr_dry += mask_inc
                ds.close()
            except:
                pass
                
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    mean_incr_wet = np.where(counts_incr_wet > 0, incr_sum_wet / counts_incr_wet, np.nan)
    mean_incr_dry = np.where(counts_incr_dry > 0, incr_sum_dry / counts_incr_dry, np.nan)
    
    # ---------------------------------------------------------
    # Fig 7: Seasonal Increment (Wet and Dry)
    # ---------------------------------------------------------
    # Validation prints for WET season
    data_min_wet_raw = np.nanmin(mean_incr_wet)
    data_max_wet_raw = np.nanmax(mean_incr_wet)
    data_mean_wet_raw = np.nanmean(mean_incr_wet)
    data_median_wet_raw = np.nanmedian(mean_incr_wet)
    valid_cells_wet = np.sum(~np.isnan(mean_incr_wet))
    nan_cells_wet = np.sum(np.isnan(mean_incr_wet))
    pos_incr_pct_wet = np.sum(mean_incr_wet > 0) / valid_cells_wet * 100 if valid_cells_wet > 0 else 0
    neg_incr_pct_wet = np.sum(mean_incr_wet < 0) / valid_cells_wet * 100 if valid_cells_wet > 0 else 0
    
    print("Variable: mean_incr_wet")
    print(f"Wet months used: {wet_str}")
    print(f"Data min (raw): {data_min_wet_raw}, max (raw): {data_max_wet_raw}")
    print(f"Spatial mean (raw): {data_mean_wet_raw}, median (raw): {data_median_wet_raw}")
    print(f"Valid cells: {valid_cells_wet}, NaN cells: {nan_cells_wet}")
    print(f"Positive increment: {pos_incr_pct_wet:.1f}%")
    print(f"Negative increment: {neg_incr_pct_wet:.1f}%")

    # Validation prints for DRY season
    data_min_dry_raw = np.nanmin(mean_incr_dry)
    data_max_dry_raw = np.nanmax(mean_incr_dry)
    data_mean_dry_raw = np.nanmean(mean_incr_dry)
    data_median_dry_raw = np.nanmedian(mean_incr_dry)
    valid_cells_dry = np.sum(~np.isnan(mean_incr_dry))
    nan_cells_dry = np.sum(np.isnan(mean_incr_dry))
    pos_incr_pct_dry = np.sum(mean_incr_dry > 0) / valid_cells_dry * 100 if valid_cells_dry > 0 else 0
    neg_incr_pct_dry = np.sum(mean_incr_dry < 0) / valid_cells_dry * 100 if valid_cells_dry > 0 else 0
    
    print("Variable: mean_incr_dry")
    print(f"Dry months used: {dry_str}")
    print(f"Data min (raw): {data_min_dry_raw}, max (raw): {data_max_dry_raw}")
    print(f"Spatial mean (raw): {data_mean_dry_raw}, median (raw): {data_median_dry_raw}")
    print(f"Valid cells: {valid_cells_dry}, NaN cells: {nan_cells_dry}")
    print(f"Positive increment: {pos_incr_pct_dry:.1f}%")
    print(f"Negative increment: {neg_incr_pct_dry:.1f}%")

    # Display scaling
    scale_factor = cfg5.get("display", {}).get("scale_factor", 1000.0)
    data_wet_plot = mean_incr_wet * scale_factor
    data_dry_plot = mean_incr_dry * scale_factor
    
    lcfg5 = cfg5.get("layout", {})
    fig4 = plt.figure(figsize=(14, 6))
    fig4.subplots_adjust(
        left=lcfg5.get("left", 0.05),
        right=lcfg5.get("right", 0.88),
        bottom=lcfg5.get("bottom", 0.08),
        top=lcfg5.get("top", 0.86),
        wspace=lcfg5.get("wspace", 0.06)
    )
    
    # Colormap and levels
    cm_cfg5 = cfg5.get("colormap", {})
    cb_cfg5 = cfg5.get("colorbar", {})
    
    levels5 = cb_cfg5.get("bounds", [-2.5, -2.0, -1.5, -1.0, -0.5, 0.0, 0.5, 1.0, 1.5, 2.0, 2.5])
    cmap_name5 = cm_cfg5.get("name", "RdBu")
    
    if cm_cfg5.get("discrete", True):
        cmap5 = plt.get_cmap(cmap_name5, len(levels5) - 1).copy()
    else:
        cmap5 = plt.get_cmap(cmap_name5).copy()
        
    if cm_cfg5.get("reverse", False):
        cmap5 = cmap5.reversed()
        
    cmap5.set_bad(color=cm_cfg5.get("bad_color", "lightgrey"))
    norm5 = mcolors.BoundaryNorm(levels5, ncolors=cmap5.N, clip=True)
    
    map_cfg5 = cfg5.get("map", {})
    gl_cfg5 = cfg5.get("gridlines", {})
    pt_cfg5 = cfg5.get("panel_titles", {})
    
    # Fonts and styling
    plt.rcParams.update({'font.size': 10, 'axes.labelsize': 10, 'xtick.labelsize': 9, 'ytick.labelsize': 9})
    
    # Title - Removed per request
                      
    # WET
    ax4a = fig4.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    add_map_features(ax4a, map_cfg=map_cfg5, gl_cfg=gl_cfg5)
    ax4a.set_title("Wet season", fontsize=10, fontweight="bold", pad=6)
    pcm4a = ax4a.pcolormesh(lon, lat, data_wet_plot, cmap=cmap5, norm=norm5, transform=ccrs.PlateCarree())
    
    # DRY
    ax4b = fig4.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    gl_cfg5_right = gl_cfg5.copy()
    # Remove y-labels (latitude) for the right panel to avoid clutter, keeping only gridlines
    gl_cfg5_right["left_labels"] = False
    
    add_map_features(ax4b, map_cfg=map_cfg5, gl_cfg=gl_cfg5_right)
    ax4b.set_title("Dry season", fontsize=10, fontweight="bold", pad=6)
    pcm4b = ax4b.pcolormesh(lon, lat, data_dry_plot, cmap=cmap5, norm=norm5, transform=ccrs.PlateCarree())
    
    # Colorbar
    if cb_cfg5.get("align_to_panel_height", True):
        fig4.canvas.draw()
        pos_left = ax4a.get_position()
        pos_right = ax4b.get_position()
        
        cbar_y0 = min(pos_left.y0, pos_right.y0)
        cbar_y1 = max(pos_left.y1, pos_right.y1)
        
        cax = fig4.add_axes([
            pos_right.x1 + cb_cfg5.get("pad", 0.012),
            cbar_y0,
            cb_cfg5.get("width", 0.016),
            cbar_y1 - cbar_y0
        ])
        
        global_min = min(np.nanmin(data_wet_plot), np.nanmin(data_dry_plot))
        global_max = max(np.nanmax(data_wet_plot), np.nanmax(data_dry_plot))
        
        if global_min < levels5[0] and global_max > levels5[-1]:
            extend_val = "both"
        elif global_min < levels5[0]:
            extend_val = "min"
        elif global_max > levels5[-1]:
            extend_val = "max"
        else:
            extend_val = "neither"
            
        cbar4 = fig4.colorbar(pcm4b, cax=cax, orientation=cb_cfg5.get("orientation", "vertical"), extend=extend_val)
    else:
        cbar4 = fig4.colorbar(pcm4b, ax=[ax4a, ax4b], orientation=cb_cfg5.get("orientation", "vertical"), 
                              pad=cb_cfg5.get("pad", 0.025), fraction=cb_cfg5.get("width", 0.035))
        
    ticks5 = cb_cfg5.get("ticks", levels5)
    cbar4.set_ticks(ticks5)
    cbar4.set_label("SMAP analysis increment (×10⁻³ m³ m⁻³)", fontsize=10)
    cbar4.ax.tick_params(labelsize=9)
    
    out_cfg5 = cfg5.get("output", {})
    f4a_png = os.path.join(out_dir, out_cfg5.get("filename", "Fig05_wet_dry_season_increment_comparison_DA-noCDF-noIRR_2016.png"))
    fig4.savefig(f4a_png, dpi=out_cfg5.get("dpi", 300), bbox_inches=out_cfg5.get("bbox_inches", "tight"))
    plt.close(fig4)
