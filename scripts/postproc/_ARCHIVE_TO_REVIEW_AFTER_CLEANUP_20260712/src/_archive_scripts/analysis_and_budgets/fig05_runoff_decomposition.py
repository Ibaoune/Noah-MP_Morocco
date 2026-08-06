# Author: M. EL Aabaribaoune (@um6p)

"""
fig05_runoff_decomposition.py

Objective: Generate Figure 5 for the publication.
Analyze separately the surface runoff (Qs) and the baseflow (Qsb).
Determine which hydrological component is most sensitive to assimilation.
Produces maps, time series, and correlations between soil moisture changes and runoff components.
"""

import os
import glob
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config_postproc as config

def load_data(dir_path):
    """
    Load Qs, Qsb, and top soil moisture from LIS outputs.
    """
    files = sorted(glob.glob(os.path.join(dir_path, "*", "*", "*.nc")))
    if not files:
        return None
    ds = xr.open_mfdataset(files, combine='by_coords')
    
    data = {}
    if 'Qs_tavg' in ds.variables:
        data['Qs'] = ds['Qs_tavg']
    if 'Qsb_tavg' in ds.variables:
        data['Qsb'] = ds['Qsb_tavg']
    if 'SoilMoist_tavg' in ds.variables:
        if 'SoilMoist_profiles' in ds.dims:
            data['SM'] = ds['SoilMoist_tavg'].isel(SoilMoist_profiles=0)
        else:
            data['SM'] = ds['SoilMoist_tavg']
            
    return data

def plot_runoff_decomposition():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    print("Loading OL data for runoff decomposition...")
    data_ol = load_data(config.DIR_OUTPUT_OL)
    print("Loading DA data for runoff decomposition...")
    data_da = load_data(config.DIR_OUTPUT_DA)
    
    if not data_ol or not data_da or 'Qs' not in data_ol or 'Qsb' not in data_ol:
        print("Data missing. Skipping Figure 5.")
        return
        
    # Calculate differences (DA - OL)
    diff_Qs = data_da['Qs'].mean('time') - data_ol['Qs'].mean('time')
    diff_Qsb = data_da['Qsb'].mean('time') - data_ol['Qsb'].mean('time')
    diff_SM = data_da['SM'].mean('time') - data_ol['SM'].mean('time')

    # Time series (Spatial average over the basin)
    ts_Qs_ol = data_ol['Qs'].mean(dim=['lat', 'lon'])
    ts_Qs_da = data_da['Qs'].mean(dim=['lat', 'lon'])
    ts_Qsb_ol = data_ol['Qsb'].mean(dim=['lat', 'lon'])
    ts_Qsb_da = data_da['Qsb'].mean(dim=['lat', 'lon'])
    
    fig = plt.figure(figsize=(18, 12))
    
    # -----------------------------------------------------------------
    # Top Row: Spatial Maps of Differences
    # -----------------------------------------------------------------
    ax1 = plt.subplot(2, 3, 1, projection=ccrs.PlateCarree())
    ax1.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE); ax1.add_feature(cfeature.BORDERS, linestyle=':')
    im1 = diff_Qs.plot(ax=ax1, cmap=config.COLORS['DIFF'], transform=ccrs.PlateCarree(), add_colorbar=False)
    plt.colorbar(im1, ax=ax1, orientation='horizontal', pad=0.05).set_label('Δ Qs (DA - OL)')
    ax1.set_title("Surface Runoff Difference", fontweight='bold')
    
    ax2 = plt.subplot(2, 3, 2, projection=ccrs.PlateCarree())
    ax2.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax2.add_feature(cfeature.COASTLINE); ax2.add_feature(cfeature.BORDERS, linestyle=':')
    im2 = diff_Qsb.plot(ax=ax2, cmap=config.COLORS['DIFF'], transform=ccrs.PlateCarree(), add_colorbar=False)
    plt.colorbar(im2, ax=ax2, orientation='horizontal', pad=0.05).set_label('Δ Qsb (DA - OL)')
    ax2.set_title("Baseflow Difference", fontweight='bold')
    
    ax3 = plt.subplot(2, 3, 3, projection=ccrs.PlateCarree())
    ax3.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax3.add_feature(cfeature.COASTLINE); ax3.add_feature(cfeature.BORDERS, linestyle=':')
    im3 = diff_SM.plot(ax=ax3, cmap=config.COLORS['DIFF'], transform=ccrs.PlateCarree(), add_colorbar=False)
    plt.colorbar(im3, ax=ax3, orientation='horizontal', pad=0.05).set_label('Δ SM (DA - OL)')
    ax3.set_title("Soil Moisture Difference", fontweight='bold')

    # -----------------------------------------------------------------
    # Bottom Row: Time Series and Scatter
    # -----------------------------------------------------------------
    ax4 = plt.subplot(2, 2, 3)
    ts_Qs_ol.plot(ax=ax4, label='OL Qs', color=config.COLORS['OL'], linestyle='--')
    ts_Qs_da.plot(ax=ax4, label='DA Qs', color=config.COLORS['DA'], linestyle='--')
    ts_Qsb_ol.plot(ax=ax4, label='OL Qsb', color=config.COLORS['OL'], linestyle='-')
    ts_Qsb_da.plot(ax=ax4, label='DA Qsb', color=config.COLORS['DA'], linestyle='-')
    ax4.set_title("Basin-Averaged Time Series", fontweight='bold')
    ax4.set_ylabel("Runoff (kg m-2 s-1)")
    ax4.legend()
    
    # Scatter: Delta SM vs Delta Qs / Delta Qsb
    ax5 = plt.subplot(2, 2, 4)
    # Flatten spatial arrays for scatter
    d_sm_flat = diff_SM.values.flatten()
    d_qs_flat = diff_Qs.values.flatten()
    d_qsb_flat = diff_Qsb.values.flatten()
    
    # Remove nans
    mask = ~np.isnan(d_sm_flat) & ~np.isnan(d_qs_flat) & ~np.isnan(d_qsb_flat)
    
    ax5.scatter(d_sm_flat[mask], d_qs_flat[mask], alpha=0.5, label='Δ Qs', s=10)
    ax5.scatter(d_sm_flat[mask], d_qsb_flat[mask], alpha=0.5, label='Δ Qsb', s=10)
    ax5.set_xlabel("Δ Soil Moisture (DA - OL)")
    ax5.set_ylabel("Δ Runoff Component (DA - OL)")
    ax5.set_title("Sensitivity to Soil Moisture Changes", fontweight='bold')
    ax5.axhline(0, color='black', linestyle='--', linewidth=0.5)
    ax5.axvline(0, color='black', linestyle='--', linewidth=0.5)
    ax5.legend()
    
    plt.tight_layout()
    output_path = os.path.join(config.DIR_FIGURES, "fig05_runoff_decomposition.png")
    plt.savefig(output_path)
    print(f"Figure 5 saved to: {output_path}")

if __name__ == "__main__":
    plot_runoff_decomposition()
