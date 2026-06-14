"""
fig02_spatial_impact_fluxes.py

Objective: Generate Figure 2 for the SSM-DA evaluation publication.
Map differences (\Delta R and \Delta Anomaly R) between SSM-DA and OL 
for E, T, ET, GPP, and NPP. Validates against FAO WaPOR and FLUXSAT.
"""

import os
import sys
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import config

def plot_spatial_impact_fluxes():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    # Check if validation data exists
    if not os.path.exists(config.DIR_OBS_WAPOR) or not os.path.exists(config.DIR_OBS_FLUXSAT):
        print("Error: Validation datasets (WaPOR / FLUXSAT) not found. Missing directories:", file=sys.stderr)
        print(f"  - WaPOR: {config.DIR_OBS_WAPOR}", file=sys.stderr)
        print(f"  - FLUXSAT: {config.DIR_OBS_FLUXSAT}", file=sys.stderr)
        sys.exit(1)
        
    print("Validation data found. Proceeding with analysis...")
    
    # The actual implementation will:
    # 1. Load monthly OL, DA outputs (Evap_tavg, TVeg_tavg, GPP_tavg, NPP_tavg).
    # 2. Load monthly WaPOR (E, T, ET, NPP) and FLUXSAT (GPP).
    # 3. Interpolate/Harmonize observations onto the Noah-MP LIS grid.
    # 4. Calculate R(SSM-DA) - R(OL) where R is correlation coefficient.
    # 5. Calculate Anomaly R(SSM-DA) - Anomaly R(OL).
    # 6. Plot a multi-panel figure using cartopy.
    
    # Placeholder for the actual plotting logic
    fig, axes = plt.subplots(5, 2, figsize=(12, 20), subplot_kw={'projection': ccrs.PlateCarree()})
    
    variables = ['Evaporation (E)', 'Transpiration (T)', 'Evapotranspiration (ET)', 'GPP', 'NPP']
    
    for i, var in enumerate(variables):
        # Delta R
        ax_r = axes[i, 0]
        ax_r.add_feature(ccrs.cartopy.feature.COASTLINE)
        ax_r.set_title(f"$\Delta$R: {var} (DA - OL)")
        
        # Delta Anomaly R
        ax_anom = axes[i, 1]
        ax_anom.add_feature(ccrs.cartopy.feature.COASTLINE)
        ax_anom.set_title(f"$\Delta$Anomaly R: {var} (DA - OL)")

    plt.tight_layout()
    output_path = os.path.join(config.DIR_FIGURES, "fig02_spatial_impact_fluxes.png")
    plt.savefig(output_path)
    print(f"Figure 2 saved to: {output_path}")

if __name__ == "__main__":
    plot_spatial_impact_fluxes()
