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

def run_innovations(config, base_dir_da, out_dir):
    print("Running innovation and increment diagnostics...")
    
    start_date = config['start_date']
    end_date = config['end_date']
    exp_name = config['experiment_name']
    year_str = end_date.strftime('%Y')
    period_str = f"{start_date.strftime('%b %Y')}–{end_date.strftime('%b %Y')}"
    
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    sample_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
    if not sample_files:
        print("No DA files found to determine grid.")
        return
        
    lat, lon = get_lat_lon(base_dir_da, start_date)
    if lat is None: return
    
    grid_shape = (len(lat), len(lon))
    innov_sum = np.zeros(grid_shape)
    incr_sum = np.zeros(grid_shape)
    counts_innov = np.zeros(grid_shape)
    counts_incr = np.zeros(grid_shape)
    all_incr_values = []
    
    curr_date = start_date
    
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        innov_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
        incr_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_incr.a01.d01.nc"))
        
        for f in innov_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'innov_01' in ds.variables:
                    inv = ds.variables['innov_01'][:]
                    if np.ma.is_masked(inv):
                        inv = inv.filled(-9999)
                    
                    mask_inv = np.where((inv > -100) & (inv < 100), 1, 0)
                    valid_inv = np.where(mask_inv == 1, inv, 0)
                    
                    innov_sum += valid_inv
                    counts_innov += mask_inv
                ds.close()
            except:
                pass
                
        for f in incr_files:
            try:
                ds = nc.Dataset(f, 'r')
                if 'anlys_incr_Soil Moisture Layer 1_01' in ds.variables:
                    inc = ds.variables['anlys_incr_Soil Moisture Layer 1_01'][:]
                    if np.ma.is_masked(inc):
                        inc = inc.filled(-9999)
                        
                    mask_inc = np.where((inc > -100) & (inc < 100), 1, 0)
                    valid_inc = np.where(mask_inc == 1, inc, 0)
                    
                    incr_sum += valid_inc
                    counts_incr += mask_inc
                    
                    inc_vals = inc[mask_inc == 1].flatten()
                    if len(inc_vals) > 0:
                        all_incr_values.extend(inc_vals)
                ds.close()
            except:
                pass
                
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    mean_innov = np.where(counts_innov > 0, innov_sum / counts_innov, np.nan)
    mean_incr = np.where(counts_incr > 0, incr_sum / counts_incr, np.nan)
    
    # ---------------------------------------------------------
    # Fig 4: Mean Innovation
    # ---------------------------------------------------------
    data_min1 = np.nanmin(mean_innov)
    data_max1 = np.nanmax(mean_innov)
    data_mean1 = np.nanmean(mean_innov)
    data_median1 = np.nanmedian(mean_innov)
    valid_cells1 = np.sum(~np.isnan(mean_innov))
    nan_cells1 = np.sum(np.isnan(mean_innov))
    pos_innov_pct = np.sum(mean_innov > 0) / valid_cells1 * 100 if valid_cells1 > 0 else 0
    neg_innov_pct = np.sum(mean_innov < 0) / valid_cells1 * 100 if valid_cells1 > 0 else 0
    
    print("Variable: mean_innov")
    print(f"Data min: {data_min1}, max: {data_max1}")
    print(f"Spatial mean: {data_mean1}, median: {data_median1}")
    print(f"Valid cells: {valid_cells1}, NaN cells: {nan_cells1}")
    print(f"Positive innovation (observation wetter than model): {pos_innov_pct:.1f}%")
    print(f"Negative innovation (observation drier than model): {neg_innov_pct:.1f}%")
    
    if np.abs(data_max1) > 1.0 or np.abs(data_min1) > 1.0:
        raise ValueError(f"Values are suspiciously large (min={data_min1}, max={data_max1}). Not an innovation field.")
        
    cfg1 = config.get("mean_innovation_map", {})
    scale_factor1 = cfg1.get("display", {}).get("scale_factor", 1000.0)
    
    mean_innov_plot = mean_innov * scale_factor1
    data_min1_plot = data_min1 * scale_factor1
    data_max1_plot = data_max1 * scale_factor1
    data_mean1_plot = data_mean1 * scale_factor1
    
    # Layout config
    lcfg1 = cfg1.get("layout", {})
    fig1 = plt.figure(figsize=(9, 7))
    fig1.subplots_adjust(
        left=lcfg1.get("left", 0.07),
        right=lcfg1.get("right", 0.88),
        bottom=lcfg1.get("bottom", 0.08),
        top=lcfg1.get("top", 0.86)
    )
    
    ax1 = fig1.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    map_cfg1 = cfg1.get("map", {})
    gl_cfg1 = cfg1.get("gridlines", {})
    gl1 = add_map_features(ax1, map_cfg=map_cfg1, gl_cfg=gl_cfg1)
    
    # Fonts and styling
    plt.rcParams.update({'font.size': 10, 'axes.labelsize': 10, 'xtick.labelsize': 9, 'ytick.labelsize': 9})
    
    # Title - Removed per request
    
    # Colormap
    cm_cfg1 = cfg1.get("colormap", {})
    cb_cfg1 = cfg1.get("colorbar", {})
    
    levels1 = cb_cfg1.get("bounds", [-0.05, -0.04, -0.03, -0.02, -0.01, 0.0, 0.01, 0.02, 0.03, 0.04, 0.05])
    
    cmap_name1 = cm_cfg1.get("name", "RdBu_r")
    if cm_cfg1.get("discrete", True):
        cmap1 = plt.get_cmap(cmap_name1, len(levels1) - 1).copy()
    else:
        cmap1 = plt.get_cmap(cmap_name1).copy()
        
    cmap1.set_bad(color=cm_cfg1.get("bad_color", "#F0F0F0"))
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, mean_innov_plot, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    
    if cb_cfg1.get("align_to_map_height", True):
        fig1.canvas.draw()
        pos1 = ax1.get_position()
        
        cax1 = fig1.add_axes([
            pos1.x1 + cb_cfg1.get("pad", 0.012),
            pos1.y0,
            cb_cfg1.get("width", 0.018),
            pos1.height
        ])
        
        if data_min1_plot < levels1[0] and data_max1_plot > levels1[-1]:
            extend_val1 = "both"
        elif data_min1_plot < levels1[0]:
            extend_val1 = "min"
        elif data_max1_plot > levels1[-1]:
            extend_val1 = "max"
        else:
            extend_val1 = "neither"
            
        cbar1 = fig1.colorbar(pcm1, cax=cax1, orientation=cb_cfg1.get("orientation", "vertical"), extend=extend_val1)
    else:
        cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation=cb_cfg1.get("orientation", "vertical"), 
                              pad=cb_cfg1.get("pad", 0.025), fraction=cb_cfg1.get("width", 0.035))
        
    ticks1 = cb_cfg1.get("ticks", levels1)
    cbar1.set_ticks(ticks1)
    cbar1.set_label(cb_cfg1.get("label", "SMAP innovation (m³ m⁻³)"), fontsize=cb_cfg1.get("label_fontsize", 11))
    cbar1.ax.tick_params(labelsize=cb_cfg1.get("tick_fontsize", 9))
    
    # Annotation box
    ann_cfg1 = cfg1.get("annotation", {})
    if ann_cfg1.get("enabled", True):
        tmpl1 = "Mean = {data_mean:.3f}\nMin = {data_min:.3f}\nMax = {data_max:.3f}"
        box_text1 = tmpl1.format(data_mean=data_mean1_plot, data_min=data_min1_plot, data_max=data_max1_plot)
        props1 = dict(boxstyle="square,pad=0.25", facecolor="white", alpha=0.85, edgecolor="none")
        ax1.text(0.02, 0.98, box_text1, transform=ax1.transAxes, fontsize=8, 
                 ha="left", va="top", bbox=props1)
    
    out_cfg1 = cfg1.get("output", {})
    f1_png = os.path.join(out_dir, out_cfg1.get("filename", "Fig04a_mean_innovation_observation_space_DA-noCDF-noIRR_2016.png"))
    fig1.savefig(f1_png, dpi=out_cfg1.get("dpi", 300), bbox_inches=out_cfg1.get("bbox_inches", "tight"))
    plt.close(fig1)
    
    # ---------------------------------------------------------
    # Fig 5: Mean Increment
    # ---------------------------------------------------------
    data_min2_raw = np.nanmin(mean_incr)
    data_max2_raw = np.nanmax(mean_incr)
    data_mean2_raw = np.nanmean(mean_incr)
    data_median2_raw = np.nanmedian(mean_incr)
    valid_cells2 = np.sum(~np.isnan(mean_incr))
    nan_cells2 = np.sum(np.isnan(mean_incr))
    pos_incr_pct = np.sum(mean_incr > 0) / valid_cells2 * 100 if valid_cells2 > 0 else 0
    neg_incr_pct = np.sum(mean_incr < 0) / valid_cells2 * 100 if valid_cells2 > 0 else 0
    
    print("Variable: mean_incr")
    print(f"Data min (raw): {data_min2_raw}, max (raw): {data_max2_raw}")
    print(f"Spatial mean (raw): {data_mean2_raw}, median (raw): {data_median2_raw}")
    print(f"Valid cells: {valid_cells2}, NaN cells: {nan_cells2}")
    print(f"Positive increment (assimilation wets model): {pos_incr_pct:.1f}%")
    print(f"Negative increment (assimilation dries model): {neg_incr_pct:.1f}%")
    
    if np.abs(data_max2_raw) > 0.05 or np.abs(data_min2_raw) > 0.05:
        raise ValueError(f"Values are suspiciously large for an increment (min={data_min2_raw}, max={data_max2_raw}). Expected ~10^-3.")
        
    cfg2 = config.get("mean_increment_map", {})
    scale_factor = cfg2.get("display", {}).get("scale_factor", 1000.0)
    
    mean_incr_plot = mean_incr * scale_factor
    data_min2_plot = data_min2_raw * scale_factor
    data_max2_plot = data_max2_raw * scale_factor
    data_mean2_plot = data_mean2_raw * scale_factor
    
    # Layout config
    lcfg2 = cfg2.get("layout", {})
    fig2 = plt.figure(figsize=(9, 7))
    fig2.subplots_adjust(
        left=lcfg2.get("left", 0.07),
        right=lcfg2.get("right", 0.88),
        bottom=lcfg2.get("bottom", 0.08),
        top=lcfg2.get("top", 0.86)
    )
    
    ax2 = fig2.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    map_cfg2 = cfg2.get("map", {})
    gl_cfg2 = cfg2.get("gridlines", {})
    gl2 = add_map_features(ax2, map_cfg=map_cfg2, gl_cfg=gl_cfg2)
    
    # Title - Removed per request
    
    # Colormap
    cm_cfg2 = cfg2.get("colormap", {})
    cb_cfg2 = cfg2.get("colorbar", {})
    
    levels2 = cb_cfg2.get("bounds", [-1.5, -1.2, -0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.5])
    
    cmap_name2 = cm_cfg2.get("name", "RdBu")
    if cm_cfg2.get("discrete", True):
        cmap2 = plt.get_cmap(cmap_name2, len(levels2) - 1).copy()
    else:
        cmap2 = plt.get_cmap(cmap_name2).copy()
        
    if cm_cfg2.get("reverse", False):
        cmap2 = cmap2.reversed()
        
    cmap2.set_bad(color=cm_cfg2.get("bad_color", "#F0F0F0"))
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap2.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, mean_incr_plot, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    
    if cb_cfg2.get("align_to_map_height", True):
        fig2.canvas.draw()
        pos2 = ax2.get_position()
        
        cax2 = fig2.add_axes([
            pos2.x1 + cb_cfg2.get("pad", 0.012),
            pos2.y0,
            cb_cfg2.get("width", 0.018),
            pos2.height
        ])
        
        if data_min2_plot < levels2[0] and data_max2_plot > levels2[-1]:
            extend_val2 = "both"
        elif data_min2_plot < levels2[0]:
            extend_val2 = "min"
        elif data_max2_plot > levels2[-1]:
            extend_val2 = "max"
        else:
            extend_val2 = "neither"
            
        cbar2 = fig2.colorbar(pcm2, cax=cax2, orientation=cb_cfg2.get("orientation", "vertical"), extend=extend_val2)
    else:
        cbar2 = fig2.colorbar(pcm2, ax=ax2, orientation=cb_cfg2.get("orientation", "vertical"), 
                              pad=cb_cfg2.get("pad", 0.025), fraction=cb_cfg2.get("width", 0.035))
        
    ticks2 = cb_cfg2.get("ticks", levels2)
    cbar2.set_ticks(ticks2)
    cbar2.set_label(cb_cfg2.get("label", "SMAP analysis increment (×10⁻³ m³ m⁻³)"), fontsize=cb_cfg2.get("label_fontsize", 11))
    cbar2.ax.tick_params(labelsize=cb_cfg2.get("tick_fontsize", 9))
    
    # Annotation box
    ann_cfg2 = cfg2.get("annotation", {})
    if ann_cfg2.get("enabled", True):
        tmpl2 = "Mean = {data_mean_scaled:.2f}\nMin = {data_min_scaled:.2f}\nMax = {data_max_scaled:.2f}"
        box_text2 = tmpl2.format(data_mean_scaled=data_mean2_plot, data_min_scaled=data_min2_plot, data_max_scaled=data_max2_plot)
        props2 = dict(boxstyle="square,pad=0.25", facecolor="white", alpha=0.85, edgecolor="none")
        ax2.text(0.02, 0.98, box_text2, transform=ax2.transAxes, fontsize=8, 
                 ha="left", va="top", bbox=props2)
    
    out_cfg2 = cfg2.get("output", {})
    f2_png = os.path.join(out_dir, out_cfg2.get("filename", "Fig04b_mean_soil_moisture_increment_DA-noCDF-noIRR_2016.png"))
    fig2.savefig(f2_png, dpi=out_cfg2.get("dpi", 300), bbox_inches=out_cfg2.get("bbox_inches", "tight"))
    plt.close(fig2)
    
    # ---------------------------------------------------------
    # Fig 6: Increment Histogram
    # ---------------------------------------------------------
    cfg3 = config.get("increment_histogram", {})
    
    if len(all_incr_values) > 0:
        increments_raw = np.array(all_incr_values)
        
        # Raw stats
        total_vals = len(increments_raw)
        n_nan = np.sum(np.isnan(increments_raw))
        n_inf = np.sum(np.isinf(increments_raw))
        n_exact_zero = np.sum(increments_raw == 0)
        frac_zero = (n_exact_zero / total_vals * 100) if total_vals > 0 else 0
        
        valid_raw = increments_raw[np.isfinite(increments_raw)]
        min_raw = np.min(valid_raw) if len(valid_raw) > 0 else np.nan
        max_raw = np.max(valid_raw) if len(valid_raw) > 0 else np.nan
        mean_raw = np.mean(valid_raw) if len(valid_raw) > 0 else np.nan
        median_raw = np.median(valid_raw) if len(valid_raw) > 0 else np.nan
        std_raw = np.std(valid_raw) if len(valid_raw) > 0 else np.nan
        
        print("Variable: all_incr_values")
        print(f"Total values: {total_vals}")
        print(f"NaN: {n_nan}, Inf: {n_inf}, Exact zeros: {n_exact_zero}")
        print(f"Fraction of exact zeros: {frac_zero:.1f}%")
        print(f"Raw Min: {min_raw}, Max: {max_raw}")
        print(f"Raw Mean: {mean_raw}, Median: {median_raw}, Std: {std_raw}")
        if len(valid_raw) > 0:
            print(f"Percentiles - P1: {np.percentile(valid_raw, 1)}, P5: {np.percentile(valid_raw, 5)}, P50: {np.percentile(valid_raw, 50)}, P95: {np.percentile(valid_raw, 95)}, P99: {np.percentile(valid_raw, 99)}")
            
        # Filtering
        filt_cfg = cfg3.get("data_filtering", {})
        active_incr = valid_raw
        if filt_cfg.get("exclude_exact_zero", True):
            tol = filt_cfg.get("zero_tolerance", 1e-10)
            active_incr = valid_raw[np.abs(valid_raw) > tol]
            
        # Display scaling
        disp_cfg = cfg3.get("display", {})
        scale_factor = disp_cfg.get("scale_factor", 1000.0)
        increments_plot = active_incr * scale_factor
        
        # Stats for box
        n_valid = len(increments_plot)
        mean_scaled = np.mean(increments_plot) if n_valid > 0 else np.nan
        median_scaled = np.median(increments_plot) if n_valid > 0 else np.nan
        p5_scaled = np.percentile(increments_plot, 5) if n_valid > 0 else np.nan
        p95_scaled = np.percentile(increments_plot, 95) if n_valid > 0 else np.nan
        
        # Layout config
        lcfg3 = cfg3.get("layout", {})
        fig3 = plt.figure(figsize=(8, 6))
        fig3.subplots_adjust(
            left=lcfg3.get("left", 0.10),
            right=lcfg3.get("right", 0.97),
            bottom=lcfg3.get("bottom", 0.13),
            top=lcfg3.get("top", 0.86)
        )
        ax3 = fig3.add_subplot(1, 1, 1)
        
        hist_cfg = cfg3.get("histogram", {})
        bins = hist_cfg.get("bins", 80)
        
        if disp_cfg.get("use_percentage", True) and n_valid > 0:
            weights = np.ones_like(increments_plot) * 100.0 / n_valid
            ax3.hist(increments_plot, bins=bins, weights=weights,
                     color=hist_cfg.get("color", "#8EC7DA"),
                     edgecolor=hist_cfg.get("edgecolor", "0.25"),
                     linewidth=hist_cfg.get("linewidth", 0.5),
                     alpha=hist_cfg.get("alpha", 0.90))
        else:
            ax3.hist(increments_plot, bins=bins,
                     color=hist_cfg.get("color", "#8EC7DA"),
                     edgecolor=hist_cfg.get("edgecolor", "0.25"),
                     linewidth=hist_cfg.get("linewidth", 0.5),
                     alpha=hist_cfg.get("alpha", 0.90))
                     
        if disp_cfg.get("y_log_scale", False):
            ax3.set_yscale('log')
            
        ax_cfg3 = cfg3.get("axes", {})
        ax3.set_xlabel("SMAP analysis increment (×10⁻³ m³ m⁻³)", fontsize=10)
        ax3.set_ylabel("Frequency (%)", fontsize=10)
        ax3.tick_params(axis='both', labelsize=9)
        
        # Enforce fixed xlim to match NoCDF and CDF visually
        ax3.set_xlim(-6, 6)
                
        # Ref lines
        ref_cfg = cfg3.get("reference_lines", {})
        zl_cfg = ref_cfg.get("zero_line", {})
        if zl_cfg.get("enabled", True):
            ax3.axvline(0, color=zl_cfg.get("color", "0.15"), linestyle=zl_cfg.get("linestyle", "-"), 
                        linewidth=zl_cfg.get("linewidth", 1.0), label=zl_cfg.get("label", "Zero"))
                        
        ml_cfg = ref_cfg.get("mean_line", {})
        if ml_cfg.get("enabled", True) and n_valid > 0:
            ax3.axvline(mean_scaled, color=ml_cfg.get("color", "#B2182B"), linestyle=ml_cfg.get("linestyle", "--"), 
                        linewidth=ml_cfg.get("linewidth", 1.2), label=ml_cfg.get("label", "Mean"))
                        
        medl_cfg = ref_cfg.get("median_line", {})
        if medl_cfg.get("enabled", True) and n_valid > 0:
            ax3.axvline(median_scaled, color=medl_cfg.get("color", "#2166AC"), linestyle=medl_cfg.get("linestyle", ":"), 
                        linewidth=medl_cfg.get("linewidth", 1.4), label=medl_cfg.get("label", "Median"))
                        
        leg_cfg = cfg3.get("legend", {})
        if leg_cfg.get("enabled", True):
            ax3.legend(loc=leg_cfg.get("location", "upper left"), fontsize=leg_cfg.get("fontsize", 8), frameon=leg_cfg.get("frameon", False))
            
        # Stats box
        sb_cfg = cfg3.get("statistics_box", {})
        if sb_cfg.get("enabled", True):
            box_text3 = f"Mean = {mean_scaled:.2f}\nMedian = {median_scaled:.2f}\nP5 = {p5_scaled:.2f}\nP95 = {p95_scaled:.2f}\nZeros = {frac_zero:.1f}%"
            props3 = dict(boxstyle="square,pad=0.25", facecolor="white", alpha=0.85, edgecolor="none")
            ax3.text(0.02, 0.98, box_text3, transform=ax3.transAxes, fontsize=8,
                     ha='left', va='top', bbox=props3)
                     
        # Title - Removed per request
                      
        grid_cfg3 = cfg3.get("grid", {})
        if grid_cfg3.get("enabled", True):
            ax3.grid(axis=grid_cfg3.get("axis", "y"), 
                     linestyle=grid_cfg3.get("linestyle", "--"), 
                     linewidth=grid_cfg3.get("linewidth", 0.5), 
                     color=grid_cfg3.get("color", "0.75"), 
                     alpha=grid_cfg3.get("alpha", 0.6))
                     
        out_cfg3 = cfg3.get("output", {})
        f3_png = os.path.join(out_dir, out_cfg3.get("filename", "Fig04c_soil_moisture_increment_distribution_DA-noCDF-noIRR_2016.png"))
        fig3.savefig(f3_png, dpi=out_cfg3.get("dpi", 300), bbox_inches=out_cfg3.get("bbox_inches", "tight"))
        plt.close(fig3)
