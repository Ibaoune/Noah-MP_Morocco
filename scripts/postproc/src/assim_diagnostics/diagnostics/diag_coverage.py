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
    
    # ---------------------------------------------------------
    # Fig 1: Total Assimilated Obs
    # ---------------------------------------------------------
    fig1 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax1 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax1)
    
    ax1.set_title(f"Total assimilated SMAP observations – {exp_name}, {period_str}", fontsize=11, fontweight='bold', pad=15)
    
    cmap1 = plt.get_cmap('YlGnBu').copy()
    cmap1.set_bad(color='#f0f0f0')
    vmax1 = np.nanpercentile(total_obs_plot, 98) if not np.all(np.isnan(total_obs_plot)) else 100
    if np.isnan(vmax1) or vmax1 == 0: vmax1 = 100
    levels1 = np.linspace(0, vmax1, 11)
    norm1 = mcolors.BoundaryNorm(levels1, ncolors=cmap1.N, clip=True)
    
    pcm1 = ax1.pcolormesh(lon, lat, total_obs_plot, cmap=cmap1, norm=norm1, transform=ccrs.PlateCarree())
    cbar1 = fig1.colorbar(pcm1, ax=ax1, orientation='vertical', shrink=0.8, pad=0.03)
    cbar1.set_label('Total Observations', fontsize=12, fontweight='bold')
    cbar1.ax.tick_params(labelsize=10)
    
    f1_png = generate_filename(out_dir, "01", "total_assimilated_obs_map", exp_name, year_str)
    fig1.savefig(f1_png, dpi=300)
    plt.close(fig1)
    
    # ---------------------------------------------------------
    # Fig 2: Assimilation Frequency
    # ---------------------------------------------------------
    fig2 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax2 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax2)
    
    ax2.set_title(f"Assimilation frequency (obs/day) – {exp_name}, {period_str}", fontsize=11, fontweight='bold', pad=15)
    
    cmap2 = plt.get_cmap('YlOrRd').copy()
    cmap2.set_bad(color='#f0f0f0')
    vmax2 = np.nanpercentile(assim_freq_plot, 98) if not np.all(np.isnan(assim_freq_plot)) else 1.0
    if np.isnan(vmax2) or vmax2 == 0: vmax2 = 1.0
    levels2 = np.linspace(0, vmax2, 11)
    norm2 = mcolors.BoundaryNorm(levels2, ncolors=cmap2.N, clip=True)
    
    pcm2 = ax2.pcolormesh(lon, lat, assim_freq_plot, cmap=cmap2, norm=norm2, transform=ccrs.PlateCarree())
    cbar2 = fig2.colorbar(pcm2, ax=ax2, orientation='vertical', shrink=0.8, pad=0.03)
    cbar2.set_label('Obs / Day', fontsize=12, fontweight='bold')
    cbar2.ax.tick_params(labelsize=10)
    
    f2_png = generate_filename(out_dir, "02", "assimilation_frequency_map", exp_name, year_str)
    fig2.savefig(f2_png, dpi=300)
    plt.close(fig2)
    
    # ---------------------------------------------------------
    # Fig 3: Monthly Total
    # ---------------------------------------------------------
    fig3, ax3 = plt.subplots(figsize=(8, 5), constrained_layout=True)
    ax3.bar(month_labels, monthly_totals, color='steelblue', edgecolor='black', alpha=0.8)
    
    ax3.set_title(f"Monthly total assimilated SMAP observations – {exp_name}, {year_str}", fontsize=11, fontweight='bold')
    ax3.set_ylabel("Total Observations", fontsize=12)
    ax3.grid(axis='y', linestyle='--', alpha=0.7)
    
    f3_png = generate_filename(out_dir, "03", "monthly_total_assimilated_obs", exp_name, year_str)
    fig3.savefig(f3_png, dpi=300)
    plt.close(fig3)
