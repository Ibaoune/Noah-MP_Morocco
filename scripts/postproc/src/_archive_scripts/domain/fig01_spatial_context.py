"""
===============================================================================
Script: fig01_spatial_context.py
Author: M. El Aabaribaoune (@um6p)

Objective: Generate supplementary spatial context maps for publication.

Description:
    Establishes the spatial context by identifying regions where vegetation, 
    soil, and irrigation interactions are likely to influence water balances.
    Specifically, this script plots the main land cover classes and highlights 
    the irrigation intensity fraction.

Dependencies:
    matplotlib, cartopy, xarray, rasterio
===============================================================================
"""

import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config_postproc as config

def plot_spatial_context():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    # We will plot two subplots: (a) Land Cover, (b) Irrigation Intensity
    fig, axes = plt.subplots(1, 2, figsize=(16, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Subplot (a): Land Cover
    ax1 = axes[0]
    ax1.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, 
                    config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax1.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax1.add_feature(cfeature.BORDERS, linestyle=':')
    ax1.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=1.0, alpha=0.6)
    
    # Placeholder for Land Cover plot
    # TODO: Load MODIS MCD12Q1 from LIS input or specific file
    # Example pseudo-code:
    # if os.path.exists(config.FILE_LAND_COVER):
    #     import xarray as xr
    #     ds = xr.open_dataset(config.FILE_LAND_COVER)
    #     lc = ds['LANDCOVER_INDEX'] # or similar variable
    #     lc.plot(ax=ax1, cmap='tab20', add_colorbar=True)
    ax1.set_title("(a) Main Land Cover Classes (MODIS)", fontweight='bold')
    
    gl1 = ax1.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl1.top_labels = False
    gl1.right_labels = False

    # Subplot (b): Irrigation Intensity
    ax2 = axes[1]
    ax2.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, 
                    config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    ax2.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax2.add_feature(cfeature.BORDERS, linestyle=':')
    ax2.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=1.0, alpha=0.6)

    # Placeholder for Irrigation Plot
    # TODO: Load GMIA or GRIPC using rasterio/xarray
    # if os.path.exists(config.FILE_OBS_GMIA):
    #     import rasterio
    #     from rasterio.plot import show
    #     src = rasterio.open(config.FILE_OBS_GMIA)
    #     show(src, ax=ax2, cmap='Blues', title="Irrigation Area Fraction")
    ax2.set_title("(b) Irrigation Intensity", fontweight='bold')

    gl2 = ax2.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl2.top_labels = False
    gl2.right_labels = False
    gl2.left_labels = False # Avoid duplicate labels in the middle

    plt.tight_layout()
    output_path = os.path.join(config.DIR_FIGURES_DOMAIN, "fig01_spatial_context.png")
    plt.savefig(output_path)
    print(f"Figure 1 saved to: {output_path}")

if __name__ == "__main__":
    plot_spatial_context()
