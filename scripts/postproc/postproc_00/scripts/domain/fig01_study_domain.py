"""
===============================================================================
Script: fig01_study_domain.py
Author: M. El Aabaribaoune (@um6p)

Objective: Generate supplementary domain overview visualizations.

Description:
    Contextualizes the physiographic and hydroclimatic characteristics of the 
    NorthMor basin. This script plots the 30m SRTM DEM (background) alongside 
    basin boundaries, the river network, validation stations, and MODIS IGBP 
    land cover overlays.

Dependencies:
    matplotlib, cartopy, rasterio, geopandas
===============================================================================
"""

import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config_postproc as config

def plot_study_domain():
    # Apply publication styling
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    fig = plt.figure(figsize=(10, 8))
    ax = plt.axes(projection=ccrs.PlateCarree())
    
    # Set domain bounds based on config
    ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, 
                   config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
    
    # Add geographical features
    ax.add_feature(cfeature.COASTLINE, linewidth=1.5)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    ax.add_feature(cfeature.RIVERS, edgecolor='blue', linewidth=1.0, alpha=0.6)
    ax.add_feature(cfeature.LAKES, facecolor='lightblue', alpha=0.5)

    # ---------------------------------------------------------
    # TODO: Load and plot MNT SRTM 30m using rasterio/xarray
    # ---------------------------------------------------------
    # Example pseudo-code for when data is fully confirmed:
    # if os.path.exists(config.FILE_DEM_SRTM):
    #     import rasterio
    #     from rasterio.plot import show
    #     src = rasterio.open(config.FILE_DEM_SRTM)
    #     show(src, ax=ax, cmap='terrain', alpha=0.6)

    # ---------------------------------------------------------
    # TODO: Load and plot Basin Boundaries / Land Cover
    # ---------------------------------------------------------
    # import geopandas as gpd
    # if os.path.exists(PATH_TO_SHAPEFILE):
    #     basin = gpd.read_file(PATH_TO_SHAPEFILE)
    #     basin.boundary.plot(ax=ax, color='black', linewidth=2)

    # ---------------------------------------------------------
    # TODO: Plot Streamflow Gauging Stations
    # ---------------------------------------------------------
    # Add scatter points for stations
    # ax.scatter(lon_stations, lat_stations, color='red', marker='^', s=50, label='Gauging Stations', transform=ccrs.PlateCarree())
    
    # Gridlines and Labels
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    plt.title("Figure 1: NorthMor Basin Study Domain", fontweight='bold')
    # plt.legend(loc='lower right')
    
    output_path = os.path.join(config.DIR_FIGURES_DOMAIN, "fig01_study_domain.png")
    plt.savefig(output_path)
    print(f"Figure 1 saved to: {output_path}")

if __name__ == "__main__":
    plot_study_domain()
