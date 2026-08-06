# Author: M. EL Aabaribaoune (@um6p)

"""
fig04_runoff_irrigation.py

Objective: Generate Figure 4 for the publication.
Demonstrate if assimilation captures the effect of irrigation indirectly and modifies runoff.
Produces spatial maps of total runoff (OL and DA), their differences, and overlaps with GMIA irrigation percentages.
"""

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config_postproc as config

def load_runoff_data(dir_path):
    """
    Load LIS output netCDF files and compute Total Runoff (Qs_tavg + Qsb_tavg).
    """
    files = sorted(glob.glob(os.path.join(dir_path, "*", "*", "*.nc")))
    if not files:
        print(f"Warning: No netCDF files found in {dir_path}")
        return None
    
    ds = xr.open_mfdataset(files, combine='by_coords')
    
    # Total runoff is Surface Runoff (Qs) + Subsurface Runoff (Qsb)
    if 'Qs_tavg' in ds.variables and 'Qsb_tavg' in ds.variables:
        total_runoff = ds['Qs_tavg'] + ds['Qsb_tavg']
    else:
        print(f"Warning: Qs_tavg or Qsb_tavg not found in dataset from {dir_path}")
        return None
        
    return total_runoff

def plot_runoff_irrigation():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    print("Loading OL runoff data...")
    runoff_ol = load_runoff_data(config.DIR_OUTPUT_OL)
    print("Loading DA runoff data...")
    runoff_da = load_runoff_data(config.DIR_OUTPUT_DA)
    
    if runoff_ol is None or runoff_da is None:
        print("Runoff data is missing. Skipping Figure 4.")
        return
        
    # Time mean
    mean_ol = runoff_ol.mean('time')
    mean_da = runoff_da.mean('time')
    diff_data = mean_da - mean_ol
    
    # Setup Figure
    fig, axes = plt.subplots(2, 2, figsize=(15, 12), subplot_kw={'projection': ccrs.PlateCarree()})
    axes = axes.flatten()
    
    # -----------------------------------------------------
    # 1. Plot OL Runoff
    # -----------------------------------------------------
    ax = axes[0]
    ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    im1 = mean_ol.plot(ax=ax, cmap='Blues', transform=ccrs.PlateCarree(), add_colorbar=False)
    plt.colorbar(im1, ax=ax, orientation='horizontal', pad=0.05).set_label('Total Runoff (kg m-2 s-1)')
    ax.set_title("Open Loop (OL) Runoff", fontweight='bold')
    
    # -----------------------------------------------------
    # 2. Plot DA Runoff
    # -----------------------------------------------------
    ax = axes[1]
    ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    im2 = mean_da.plot(ax=ax, cmap='Blues', transform=ccrs.PlateCarree(), add_colorbar=False)
    plt.colorbar(im2, ax=ax, orientation='horizontal', pad=0.05).set_label('Total Runoff (kg m-2 s-1)')
    ax.set_title("Data Assimilation (DA) Runoff", fontweight='bold')
    
    # -----------------------------------------------------
    # 3. Plot Difference (DA - OL)
    # -----------------------------------------------------
    ax = axes[2]
    ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    vmax_diff = max(abs(diff_data.min().values), abs(diff_data.max().values))
    im3 = diff_data.plot(ax=ax, cmap=config.COLORS['DIFF'], transform=ccrs.PlateCarree(), add_colorbar=False, vmin=-vmax_diff, vmax=vmax_diff)
    plt.colorbar(im3, ax=ax, orientation='horizontal', pad=0.05).set_label('Difference (DA - OL)')
    ax.set_title("Runoff Difference (DA - OL)", fontweight='bold')
    
    # -----------------------------------------------------
    # 4. Plot GMIA Irrigation Percentage
    # -----------------------------------------------------
    ax = axes[3]
    ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    
    try:
        import rasterio
        from rasterio.plot import show
        if os.path.exists(config.FILE_OBS_GMIA):
            src = rasterio.open(config.FILE_OBS_GMIA)
            # Read data and handle no-data values
            data = src.read(1)
            data = np.where(data == src.nodata, np.nan, data)
            im4 = ax.imshow(data, cmap='YlGn', transform=ccrs.PlateCarree(), extent=(src.bounds.left, src.bounds.right, src.bounds.bottom, src.bounds.top))
            plt.colorbar(im4, ax=ax, orientation='horizontal', pad=0.05).set_label('Area Equipped for Irrigation (%)')
        else:
            ax.text(0.5, 0.5, "GMIA File Not Found", ha='center', va='center', transform=ax.transAxes)
    except Exception as e:
        ax.text(0.5, 0.5, f"Error loading GMIA:\n{str(e)}", ha='center', va='center', transform=ax.transAxes)
        
    ax.set_title("FAO GMIA Irrigation (%)", fontweight='bold')

    # Add Gridlines
    for ax in axes:
        gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
        gl.top_labels = False; gl.right_labels = False

    plt.tight_layout()
    output_path = os.path.join(config.DIR_FIGURES, "fig04_runoff_irrigation.png")
    plt.savefig(output_path)
    print(f"Figure 4 saved to: {output_path}")

if __name__ == "__main__":
    plot_runoff_irrigation()
