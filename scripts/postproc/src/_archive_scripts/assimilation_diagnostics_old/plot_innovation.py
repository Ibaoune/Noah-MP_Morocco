import os
import glob
import netCDF4 as nc
import calendar
from datetime import timedelta
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from utils.masking import get_lat_lon

def plot_innovation_increment(data_dict, out_dir):
    """
    Génère 3 figures séparées de niveau publication (Q1) illustrant :
    1. La carte de l'innovation moyenne (Obs - Forecast).
    2. La carte de l'incrément moyen (Analysis - Forecast).
    3. L'histogramme des incréments avec ligne verticale à x=0.
    """
    print("Generating SMAP innovation and increment figures...")
    files_cdf = data_dict.get('files_da_nocdf', [])
    if not files_cdf:
        print("No DA files found.")
        return None
        
    lat, lon = get_lat_lon(files_cdf)
    if lat is None: return None
    
    # Extract the experiment name from the file path
    # Path is like: .../experiments/NorthMor/matrix_2016/DA_nocdf_noirr_2016/EnKF/...
    base_dir_da = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(files_cdf[0]))))
    if os.path.basename(base_dir_da) == "output":
        exp_name = os.path.basename(os.path.dirname(base_dir_da))
    else:
        exp_name = os.path.basename(base_dir_da)
    
    grid_shape = (len(lat), len(lon))
    innov_sum = np.zeros(grid_shape)
    incr_sum = np.zeros(grid_shape)
    counts_innov = np.zeros(grid_shape)
    counts_incr = np.zeros(grid_shape)
    
    incr_sum_djf = np.zeros(grid_shape)
    counts_incr_djf = np.zeros(grid_shape)
    incr_sum_jja = np.zeros(grid_shape)
    counts_incr_jja = np.zeros(grid_shape)
    
    spread_sum = np.zeros(grid_shape)
    counts_spread = np.zeros(grid_shape)
    all_spread_values = []
    
    all_incr_values = []
    
    curr_date = data_dict['start_date']
    end_date = data_dict['end_date']
    
    while curr_date <= end_date:
        yr = curr_date.strftime("%Y")
        mo = curr_date.strftime("%m")
        is_djf = curr_date.month in [12, 1, 2]
        is_jja = curr_date.month in [6, 7, 8]
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
                
                if 'forecast_sigma_01' in ds.variables:
                    sprd = ds.variables['forecast_sigma_01'][:]
                    if np.ma.is_masked(sprd):
                        sprd = sprd.filled(-9999)
                    mask_sprd = np.where((sprd > -100) & (sprd < 100), 1, 0)
                    valid_sprd = np.where(mask_sprd == 1, sprd, 0)
                    spread_sum += valid_sprd
                    counts_spread += mask_sprd
                    sprd_vals = sprd[mask_sprd == 1].flatten()
                    if len(sprd_vals) > 0:
                        all_spread_values.extend(sprd_vals)
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
                    
                    if is_djf:
                        incr_sum_djf += valid_inc
                        counts_incr_djf += mask_inc
                    elif is_jja:
                        incr_sum_jja += valid_inc
                        counts_incr_jja += mask_inc
                    
                    # Accumulate valid increments for histogram
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
    mean_incr_djf = np.where(counts_incr_djf > 0, incr_sum_djf / counts_incr_djf, np.nan)
    mean_incr_jja = np.where(counts_incr_jja > 0, incr_sum_jja / counts_incr_jja, np.nan)
    mean_spread = np.where(counts_spread > 0, spread_sum / counts_spread, np.nan)
    
    start_str = data_dict['start_date'].strftime('%b')
    end_str = data_dict['end_date'].strftime('%b %Y')
    year_str = data_dict['end_date'].strftime('%Y')
    period_str = f"{start_str}–{end_str}"
    
    os.makedirs(out_dir, exist_ok=True)
    
    def add_map_features(ax):
        ax.coastlines(linewidth=0.5, color='black')
        ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle=':', color='black')
        ax.set_facecolor('#f0f0f0') # gris clair pour zones sans données
        
        gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        gl.xlabel_style = {'size': 10}
        gl.ylabel_style = {'size': 10}
        return gl
    
    # ==============================================================
    # Figure 1: Mean Innovation
    # ==============================================================
    fig1 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax1 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax1)
    
    ax1.set_title(f"Time-averaged SMAP innovation (Obs - Forecast) – {exp_name}, {period_str}", fontsize=13, fontweight='bold', pad=15)
    
    vmax1 = np.nanpercentile(np.abs(mean_innov), 98) if not np.all(np.isnan(mean_innov)) else 0.05
    if np.isnan(vmax1) or vmax1 == 0: vmax1 = 0.05
    
    # Discrete colorbar for Innovation
    levels1 = np.linspace(-vmax1, vmax1, 11)
    cmap1 = plt.get_cmap('RdBu').copy()
    cmap1.set_bad('#f0f0f0')
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, mean_innov, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation='vertical', shrink=0.8, pad=0.03)
    cbar1.set_label("Innovation (m³ m⁻³)", fontsize=11)
    cbar1.ax.tick_params(labelsize=10)
    
    f1_png = os.path.join(out_dir, f"03a_smap_mean_innovation_{exp_name}_{year_str}.png")
    fig1.savefig(f1_png, dpi=300)
    plt.close(fig1)
    
    # ==============================================================
    # Figure 2: Mean Increment
    # ==============================================================
    fig2 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax2)
    
    ax2.set_title(f"Time-averaged SMAP increment (Analysis - Forecast) – {exp_name}, {period_str}", fontsize=13, fontweight='bold', pad=15)
    
    vmax2 = np.nanpercentile(np.abs(mean_incr), 98) if not np.all(np.isnan(mean_incr)) else 0.05
    if np.isnan(vmax2) or vmax2 == 0: vmax2 = 0.05
    
    # Discrete colorbar for Increment
    levels2 = np.linspace(-vmax2, vmax2, 11)
    cmap2 = plt.get_cmap('RdBu').copy()
    cmap2.set_bad('#f0f0f0')
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap2.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, mean_incr, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    cbar2 = fig2.colorbar(pcm2, ax=ax2, orientation='vertical', shrink=0.8, pad=0.03)
    cbar2.set_label("Increment (m³ m⁻³)", fontsize=11)
    cbar2.ax.tick_params(labelsize=10)
    
    f2_png = os.path.join(out_dir, f"03b_smap_mean_increment_{exp_name}_{year_str}.png")
    fig2.savefig(f2_png, dpi=300)
    plt.close(fig2)
    
    # ==============================================================
    # Figure 3: Histogram of increments
    # ==============================================================
    fig3, ax3 = plt.subplots(figsize=(8, 5), constrained_layout=True)
    
    if all_incr_values:
        # Use a reasonable range filtering out extreme outliers for histogram
        p1, p99 = np.percentile(all_incr_values, [1, 99])
        filtered_vals = [v for v in all_incr_values if p1 <= v <= p99]
        if not filtered_vals: filtered_vals = all_incr_values
        
        ax3.hist(filtered_vals, bins=60, color='#4575b4', edgecolor='black', alpha=0.8, zorder=3)
    
    ax3.axvline(x=0, color='red', linestyle='--', linewidth=1.5, zorder=4, label='Zero increment')
    ax3.legend(loc='upper right', fontsize=10)
    
    ax3.set_title(f"Distribution of SMAP increments – {exp_name}, {year_str}", fontsize=14, fontweight='bold', pad=15)
    ax3.set_xlabel("Increment (m³ m⁻³)", fontsize=11)
    ax3.set_ylabel("Count", fontsize=11)
    ax3.tick_params(axis='both', labelsize=10)
    
    ax3.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
    ax3.grid(axis='x', linestyle=':', alpha=0.4, zorder=0)
    ax3.spines['top'].set_visible(False)
    ax3.spines['right'].set_visible(False)
    
    f3_png = os.path.join(out_dir, f"03c_smap_increment_histogram_{exp_name}_{year_str}.png")
    fig3.savefig(f3_png, dpi=300)
    plt.close(fig3)
    
    # ==============================================================
    # Figure 4: Seasonal Increment (DJF and JJA)
    # ==============================================================
    fig4 = plt.figure(figsize=(14, 6), constrained_layout=True)
    
    # DJF
    ax4a = fig4.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    add_map_features(ax4a)
    ax4a.set_title(f"Mean SMAP increment (DJF) – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    
    vmax4 = np.nanpercentile(np.abs(mean_incr_djf), 98) if not np.all(np.isnan(mean_incr_djf)) else 0.05
    if np.isnan(vmax4) or vmax4 == 0: vmax4 = 0.05
    levels4 = np.linspace(-vmax4, vmax4, 11)
    norm4 = mcolors.BoundaryNorm(levels4, ncolors=cmap1.N, clip=True)
    
    pcm4a = ax4a.pcolormesh(lon, lat, mean_incr_djf, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    # JJA
    ax4b = fig4.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    add_map_features(ax4b)
    ax4b.set_title(f"Mean SMAP increment (JJA) – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    
    pcm4b = ax4b.pcolormesh(lon, lat, mean_incr_jja, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    cbar4 = fig4.colorbar(pcm4b, ax=[ax4a, ax4b], orientation='vertical', shrink=0.8, pad=0.02)
    cbar4.set_label('Increment', fontsize=12, fontweight='bold')
    cbar4.ax.tick_params(labelsize=10)
    
    f4a_png = os.path.join(out_dir, f"04a_smap_seasonal_increment_DJF_JJA_{exp_name}_{year_str}.png")
    fig4.savefig(f4a_png, dpi=300)
    plt.close(fig4)
    
    # ==============================================================
    # Figure 5: Prior Ensemble Spread Map
    # ==============================================================
    fig5 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax5 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax5)
    
    ax5.set_title(f"Time-averaged SMAP prior ensemble spread – {exp_name}, {period_str}", fontsize=13, fontweight='bold', pad=15)
    
    cmap5 = plt.get_cmap('YlOrRd').copy()
    cmap5.set_bad(color='#f0f0f0')
    
    vmax5 = np.nanpercentile(mean_spread, 98) if not np.all(np.isnan(mean_spread)) else 0.05
    if np.isnan(vmax5) or vmax5 == 0: vmax5 = 0.05
    levels5 = np.linspace(0, vmax5, 11)
    norm5 = mcolors.BoundaryNorm(levels5, ncolors=cmap5.N, clip=True)
    
    pcm5 = ax5.pcolormesh(lon, lat, mean_spread, cmap=cmap5, norm=norm5, transform=ccrs.PlateCarree())
    
    cbar5 = fig5.colorbar(pcm5, ax=ax5, orientation='vertical', shrink=0.8, pad=0.03)
    cbar5.set_label('Spread', fontsize=12, fontweight='bold')
    cbar5.ax.tick_params(labelsize=10)
    
    f4b_png = os.path.join(out_dir, f"04b_smap_prior_ensemble_spread_map_{exp_name}_{year_str}.png")
    fig5.savefig(f4b_png, dpi=300)
    plt.close(fig5)
    
    # ==============================================================
    # Figure 6: Prior Ensemble Spread Histogram
    # ==============================================================
    fig6, ax6 = plt.subplots(figsize=(8, 6), constrained_layout=True)
    if len(all_spread_values) > 0:
        ax6.hist(all_spread_values, bins=50, color='orange', edgecolor='black', alpha=0.7)
    
    ax6.set_title(f"Histogram of SMAP prior ensemble spread – {exp_name}, {year_str}", fontsize=13, fontweight='bold')
    ax6.set_xlabel("Ensemble Spread", fontsize=12)
    ax6.set_ylabel("Frequency", fontsize=12)
    ax6.grid(axis='y', linestyle='--', alpha=0.7)
    
    f4c_png = os.path.join(out_dir, f"04c_smap_prior_ensemble_spread_histogram_{exp_name}_{year_str}.png")
    fig6.savefig(f4c_png, dpi=300)
    plt.close(fig6)

    return [f1_png, f2_png, f3_png, f4a_png, f4b_png, f4c_png]
