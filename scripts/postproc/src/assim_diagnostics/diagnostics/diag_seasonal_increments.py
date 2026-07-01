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

def run_seasonal_increments(config, base_dir_da, out_dir):
    print("Running seasonal increments diagnostics...")
    
    start_date = config['start_date']
    end_date = config['end_date']
    exp_name = config['experiment_name']
    year_str = end_date.strftime('%Y')
    
    wet_months = config['seasons']['wet_season']
    dry_months = config['seasons']['dry_season']
    
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
    fig4 = plt.figure(figsize=(14, 6), constrained_layout=True)
    cmap1 = plt.get_cmap('RdBu').copy()
    cmap1.set_bad(color='#f0f0f0')
    
    vmax4 = np.nanpercentile(np.abs(mean_incr_wet), 98) if not np.all(np.isnan(mean_incr_wet)) else 0.05
    if np.isnan(vmax4) or vmax4 == 0: vmax4 = 0.05
    levels4 = np.linspace(-vmax4, vmax4, 11)
    norm4 = mcolors.BoundaryNorm(levels4, ncolors=cmap1.N, clip=True)
    
    # WET
    ax4a = fig4.add_subplot(1, 2, 1, projection=ccrs.PlateCarree())
    add_map_features(ax4a)
    ax4a.set_title(f"Mean SMAP increment (Wet Season) – {exp_name}, {year_str}", fontsize=10, fontweight='bold', pad=15)
    ax4a.pcolormesh(lon, lat, mean_incr_wet, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    # DRY
    ax4b = fig4.add_subplot(1, 2, 2, projection=ccrs.PlateCarree())
    add_map_features(ax4b)
    ax4b.set_title(f"Mean SMAP increment (Dry Season) – {exp_name}, {year_str}", fontsize=10, fontweight='bold', pad=15)
    pcm4b = ax4b.pcolormesh(lon, lat, mean_incr_dry, cmap=cmap1, norm=norm4, transform=ccrs.PlateCarree())
    
    cbar4 = fig4.colorbar(pcm4b, ax=[ax4a, ax4b], orientation='vertical', shrink=0.8, pad=0.02)
    cbar4.set_label('Increment', fontsize=12, fontweight='bold')
    cbar4.ax.tick_params(labelsize=10)
    
    f4a_png = generate_filename(out_dir, "05", "seasonal_increment_wet_dry", exp_name, year_str)
    fig4.savefig(f4a_png, dpi=300)
    plt.close(fig4)
