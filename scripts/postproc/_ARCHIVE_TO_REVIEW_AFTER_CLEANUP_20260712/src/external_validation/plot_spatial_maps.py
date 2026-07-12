"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: external_validation.plot_spatial_maps
Description: Validation of model outputs against external observational datasets.
================================================================================
"""
import os
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import numpy as np

def run(cfg):
    print("--- Running Spatial Maps Validation ---")
    plt.rcParams.update(cfg.PLOT_RC_PARAMS)
    
    # 1. Spatial Impact Fluxes (Delta R, Delta Anomaly R)
    if not os.path.exists(cfg.DIR_OBS_WAPOR) or not os.path.exists(cfg.DIR_OBS_FLUXSAT):
        print("  -> Warning: Validation datasets (WaPOR / FLUXSAT) not found. Plotting skeleton for Fluxes.")
    
    fig, axes = plt.subplots(5, 2, figsize=(12, 20), subplot_kw={'projection': ccrs.PlateCarree()})
    variables = ['Evaporation (E)', 'Transpiration (T)', 'Evapotranspiration (ET)', 'GPP', 'NPP']
    
    for i, var in enumerate(variables):
        # Delta R
        ax_r = axes[i, 0]
        ax_r.add_feature(cfeature.COASTLINE)
        ax_r.set_extent([cfg.DOMAIN_LON_MIN, cfg.DOMAIN_LON_MAX, cfg.DOMAIN_LAT_MIN, cfg.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
        ax_r.set_title(f"$\Delta$R: {var} (DA - OL)")
        
        # Delta Anomaly R
        ax_anom = axes[i, 1]
        ax_anom.add_feature(cfeature.COASTLINE)
        ax_anom.set_extent([cfg.DOMAIN_LON_MIN, cfg.DOMAIN_LON_MAX, cfg.DOMAIN_LAT_MIN, cfg.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
        ax_anom.set_title(f"$\Delta$Anomaly R: {var} (DA - OL)")

    plt.tight_layout()
    output_path = os.path.join(cfg.DIR_FIGURES, "spatial_impact_fluxes.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    print(f"  -> Saved: {output_path}")

    # 2. SM Assimilation Impact (Mean Differences)
    fig, axes = plt.subplots(1, 4, figsize=(20, 5), subplot_kw={'projection': ccrs.PlateCarree()})
    titles = ['MAM', 'JJA', 'SON', 'DJF']
    
    for i, title in enumerate(titles):
        ax = axes[i]
        ax.set_extent([cfg.DOMAIN_LON_MIN, cfg.DOMAIN_LON_MAX, cfg.DOMAIN_LAT_MIN, cfg.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.set_title(f"$\Delta$SM - {title}", fontweight='bold')
        gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
        gl.top_labels = False; gl.right_labels = False
        
        # Placeholder for data
        ax.text(0.5, 0.5, "Data Placeholder", transform=ax.transAxes, ha='center', va='center')

    plt.tight_layout()
    output_path = os.path.join(cfg.DIR_FIGURES, "sm_assim_impact.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    print(f"  -> Saved: {output_path}")

    print("--- Spatial Maps Validation Completed ---\n")
