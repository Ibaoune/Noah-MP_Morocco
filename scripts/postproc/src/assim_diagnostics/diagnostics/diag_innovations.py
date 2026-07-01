import os
import glob
from datetime import timedelta
import calendar
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs

from utils import get_lat_lon, add_map_features, generate_filename

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
    fig1 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax1 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax1)
    
    ax1.set_title(f"Time-averaged SMAP innovation (Obs - Forecast) – {exp_name}, {period_str}", fontsize=11, fontweight='bold', pad=15)
    
    vmax1 = np.nanpercentile(np.abs(mean_innov), 98) if not np.all(np.isnan(mean_innov)) else 0.05
    if np.isnan(vmax1) or vmax1 == 0: vmax1 = 0.05
    levels1 = np.linspace(-vmax1, vmax1, 11)
    cmap1 = plt.get_cmap('RdBu').copy()
    cmap1.set_bad(color='#f0f0f0')
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, mean_innov, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation='vertical', shrink=0.8, pad=0.03)
    cbar1.set_label('Innovation', fontsize=12, fontweight='bold')
    cbar1.ax.tick_params(labelsize=10)
    
    f1_png = generate_filename(out_dir, "04a", "mean_innovation", exp_name, year_str)
    fig1.savefig(f1_png, dpi=300)
    plt.close(fig1)
    
    # ---------------------------------------------------------
    # Fig 5: Mean Increment
    # ---------------------------------------------------------
    fig2 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax2)
    
    ax2.set_title(f"Time-averaged SMAP increment (Analysis - Forecast) – {exp_name}, {period_str}", fontsize=11, fontweight='bold', pad=15)
    
    vmax2 = np.nanpercentile(np.abs(mean_incr), 98) if not np.all(np.isnan(mean_incr)) else 0.05
    if np.isnan(vmax2) or vmax2 == 0: vmax2 = 0.05
    levels2 = np.linspace(-vmax2, vmax2, 11)
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap1.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, mean_incr, cmap=cmap1, norm=norm2, transform=ccrs.PlateCarree())
    cbar2 = fig2.colorbar(pcm2, ax=ax2, orientation='vertical', shrink=0.8, pad=0.03)
    cbar2.set_label('Increment', fontsize=12, fontweight='bold')
    cbar2.ax.tick_params(labelsize=10)
    
    f2_png = generate_filename(out_dir, "04b", "mean_increment", exp_name, year_str)
    fig2.savefig(f2_png, dpi=300)
    plt.close(fig2)
    
    # ---------------------------------------------------------
    # Fig 6: Increment Histogram
    # ---------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(8, 6), constrained_layout=True)
    if len(all_incr_values) > 0:
        ax3.hist(all_incr_values, bins=50, color='skyblue', edgecolor='black', alpha=0.7)
    
    ax3.set_title(f"Distribution of SMAP increments – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    ax3.set_xlabel("Increment", fontsize=12)
    ax3.set_ylabel("Frequency", fontsize=12)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    
    f3_png = generate_filename(out_dir, "04c", "increment_histogram", exp_name, year_str)
    fig3.savefig(f3_png, dpi=300)
    plt.close(fig3)
