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

def run_spread(config, base_dir_da, out_dir):
    print("Running ensemble spread diagnostics...")
    
    start_date = config['start_date']
    end_date = config['end_date']
    exp_name = config['experiment_name']
    year_str = end_date.strftime('%Y')
    period_str = f"{start_date.strftime('%b %Y')}–{end_date.strftime('%b %Y')}"
    
    yr = start_date.strftime("%Y")
    mo = start_date.strftime("%m")
    sample_files = glob.glob(os.path.join(base_dir_da, f"{yr}-{mo}", "EnKF", f"{yr}{mo}", "*_innov.a01.d01.nc"))
    if not sample_files:
        return
        
    lat, lon = get_lat_lon(base_dir_da, start_date)
    if lat is None: return
    
    grid_shape = (len(lat), len(lon))
    spread_sum = np.zeros(grid_shape)
    counts_spread = np.zeros(grid_shape)
    all_spread_values = []
    
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
                    
                    sprd_vals = sprd[mask_sprd == 1].flatten()
                    if len(sprd_vals) > 0:
                        all_spread_values.extend(sprd_vals)
                ds.close()
            except:
                pass
                
        days_in_month = calendar.monthrange(curr_date.year, curr_date.month)[1]
        curr_date += timedelta(days=days_in_month)
        curr_date = curr_date.replace(day=1)
        
    mean_spread = np.where(counts_spread > 0, spread_sum / counts_spread, np.nan)
    
    # ---------------------------------------------------------
    # Fig 8: Prior Ensemble Spread Map
    # ---------------------------------------------------------
    fig5 = plt.figure(figsize=(9, 7), constrained_layout=True)
    ax5 = plt.axes(projection=ccrs.PlateCarree())
    add_map_features(ax5)
    
    ax5.set_title(f"Time-averaged SMAP prior ensemble spread – {exp_name}, {period_str}", fontsize=11, fontweight='bold', pad=15)
    
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
    
    f5_png = generate_filename(out_dir, "06a", "prior_ensemble_spread_map", exp_name, year_str)
    fig5.savefig(f5_png, dpi=300)
    plt.close(fig5)
    
    # ---------------------------------------------------------
    # Fig 9: Prior Ensemble Spread Histogram
    # ---------------------------------------------------------
    fig6, ax6 = plt.subplots(figsize=(8, 6), constrained_layout=True)
    if len(all_spread_values) > 0:
        ax6.hist(all_spread_values, bins=50, color='orange', edgecolor='black', alpha=0.7)
    
    ax6.set_title(f"Histogram of SMAP prior ensemble spread – {exp_name}, {year_str}", fontsize=12, fontweight='bold', pad=15)
    ax6.set_xlabel("Ensemble Spread", fontsize=12)
    ax6.set_ylabel("Frequency", fontsize=12)
    ax6.grid(axis='y', linestyle='--', alpha=0.7)
    
    f6_png = generate_filename(out_dir, "06b", "prior_ensemble_spread_histogram", exp_name, year_str)
    fig6.savefig(f6_png, dpi=300)
    plt.close(fig6)
