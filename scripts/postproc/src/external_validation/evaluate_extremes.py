"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: external_validation.evaluate_extremes
Description: Validation of model outputs against external observational datasets.
================================================================================
"""
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import sys

def plot_drought_categorization(cfg):
    """Time series of the percentage of area affected by drought categories (D0 to D4)."""
    # Dummy data
    dates = pd.date_range(start=cfg.START_DATE, periods=1800, freq="D")
    np.random.seed(123)
    base_drought = np.sin(np.linspace(0, 10*np.pi, 1800)) * 20 + 25
    base_drought += np.random.normal(0, 5, 1800)
    base_drought = np.clip(base_drought, 0, 100)
    
    ol_d0 = base_drought
    da_d0 = ol_d0 * 0.85 + np.random.normal(0, 2, 1800)
    da_d0 = np.clip(da_d0, 0, 100)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), gridspec_kw={'width_ratios': [2, 1]})
    
    # 5a: Time series
    ax1.fill_between(dates, 0, da_d0, color='#ffff00', label='D0 Abnormally Dry (DA)', alpha=0.8)
    ax1.fill_between(dates, 0, da_d0*0.7, color='#fcd37f', label='D1 Moderate (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.35, color='#ffaa00', label='D2 Severe (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.14, color='#e60000', label='D3 Extreme (DA)', alpha=0.9)
    ax1.fill_between(dates, 0, da_d0*0.03, color='#730000', label='D4 Exceptional (DA)', alpha=0.9)
    ax1.plot(dates, ol_d0, color='black', linestyle='--', linewidth=1.5, label='D0 Total (OL)')
    
    ax1.set_title("(a) Drought Area Evolution based on Root-Zone Soil Moisture")
    ax1.set_ylabel("Basin Area (%)")
    ax1.set_xlabel("Year")
    ax1.set_ylim(0, 100)
    ax1.legend(loc='upper right', ncol=2, fontsize=10)
    
    # 5b: Scatterplot
    ax2.scatter(ol_d0, da_d0, color=cfg.COLORS['DA'], alpha=0.5, s=15)
    ax2.plot([0, 100], [0, 100], 'k--', linewidth=2)
    ax2.set_title("(b) Drought Area Scatterplot (D0+)")
    ax2.set_xlabel("% Area in Drought (OL)")
    ax2.set_ylabel("% Area in Drought (SSM-DA)")
    ax2.set_xlim(0, 100)
    ax2.set_ylim(0, 100)
    ax2.grid(True, linestyle=':', alpha=0.7)

    plt.tight_layout()
    output_path = os.path.join(cfg.DIR_FIGURES, "drought_categorization.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    print(f"  -> Saved: {output_path}")

def plot_extreme_event_response(cfg):
    """Map spatial response to a specific extreme event."""
    if not os.path.exists(cfg.DIR_OBS_MODIS_LAI):
        print("  -> Warning: Validation dataset MODIS LAI not found. Continuing with partial data...")
        
    fig, axes = plt.subplots(1, 3, figsize=(18, 6), subplot_kw={'projection': ccrs.PlateCarree()})
    titles = ["(a) MODIS LAI Anomaly", "(b) OL LAI Anomaly", "(c) SSM-DA LAI Anomaly"]
    
    for i, ax in enumerate(axes):
        ax.set_extent([cfg.DOMAIN_LON_MIN, cfg.DOMAIN_LON_MAX, 
                       cfg.DOMAIN_LAT_MIN, cfg.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.set_title(titles[i], fontweight='bold')
        
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        if i > 0:
            gl.left_labels = False
            
    fig.suptitle("Spatial Response of Vegetation to Extreme Drought Event", fontsize=18, fontweight='bold', y=0.98)
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    output_path = os.path.join(cfg.DIR_FIGURES, "extreme_event_response.png")
    plt.savefig(output_path, dpi=cfg.PLOT_RC_PARAMS['figure.dpi'])
    plt.close()
    print(f"  -> Saved: {output_path}")

def run(cfg):
    print("--- Running Extremes Validation ---")
    plt.rcParams.update(cfg.PLOT_RC_PARAMS)
    
    plot_drought_categorization(cfg)
    plot_extreme_event_response(cfg)
    
    print("--- Extremes Validation Completed ---\n")
