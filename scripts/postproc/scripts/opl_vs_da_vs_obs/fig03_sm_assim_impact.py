"""
fig03_sm_assim_impact.py

Objective: Generate Figure 3 for the publication.
Compare OL and DA for surface soil moisture (0-5 cm).
Produces seasonal maps (Winter, Summer), differences (DA - OL), and spatial statistics.
"""

import os
import glob
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import config_postproc as config

def load_and_preprocess(dir_path):
    """
    Load LIS output netCDF files and extract the top soil moisture layer.
    """
    files = sorted(glob.glob(os.path.join(dir_path, "*", "*", "*.nc")))
    if not files:
        print(f"Warning: No netCDF files found in {dir_path}")
        return None
    
    # Load multi-file dataset
    ds = xr.open_mfdataset(files, combine='by_coords')
    
    # Extract SoilMoist_tavg (Layer 1: index 0)
    # LIS Noah-MP SoilMoist_tavg dimensions are usually (time, SoilMoist_profiles, lat, lon)
    if 'SoilMoist_profiles' in ds.dims:
        sm_top = ds['SoilMoist_tavg'].isel(SoilMoist_profiles=0)
    else:
        sm_top = ds['SoilMoist_tavg']
        
    return sm_top

def plot_sm_assim_impact():
    plt.rcParams.update(config.PLOT_RC_PARAMS)
    
    print("Loading OL data...")
    sm_ol = load_and_preprocess(config.DIR_OUTPUT_OL)
    print("Loading DA data...")
    sm_da = load_and_preprocess(config.DIR_OUTPUT_DA)
    
    if sm_ol is None or sm_da is None:
        print("Data is missing. Skipping Figure 3.")
        return

    # Check if dataset is long enough to compute seasonal means
    # If not (e.g. 3-day test), just compute the overall mean.
    days_count = len(sm_ol.time)
    
    if days_count > 90:
        # Compute seasonal means
        mean_ol = sm_ol.groupby('time.season').mean('time')
        mean_da = sm_da.groupby('time.season').mean('time')
        seasons_to_plot = ['DJF', 'JJA'] # Winter and Summer
    else:
        print("Dataset is too short for seasonal analysis. Computing overall mean.")
        mean_ol = sm_ol.mean('time').expand_dims({'season': ['Overall']})
        mean_da = sm_da.mean('time').expand_dims({'season': ['Overall']})
        seasons_to_plot = ['Overall']

    for season in seasons_to_plot:
        if season in mean_ol.season.values:
            ol_data = mean_ol.sel(season=season)
            da_data = mean_da.sel(season=season)
            diff_data = da_data - ol_data
            
            # Plotting
            fig, axes = plt.subplots(1, 3, figsize=(18, 5), subplot_kw={'projection': ccrs.PlateCarree()})
            
            titles = [f"Open Loop (OL) - {season}", f"Data Assimilation (DA) - {season}", f"Difference (DA - OL) - {season}"]
            data_to_plot = [ol_data, da_data, diff_data]
            cmaps = ['viridis', 'viridis', config.COLORS['DIFF']]
            
            for ax, data, title, cmap in zip(axes, data_to_plot, titles, cmaps):
                ax.set_extent([config.DOMAIN_LON_MIN, config.DOMAIN_LON_MAX, 
                               config.DOMAIN_LAT_MIN, config.DOMAIN_LAT_MAX], crs=ccrs.PlateCarree())
                ax.add_feature(cfeature.COASTLINE)
                ax.add_feature(cfeature.BORDERS, linestyle=':')
                
                # Plot data
                vmax = data.max().values if cmap != config.COLORS['DIFF'] else max(abs(data.min().values), abs(data.max().values))
                vmin = data.min().values if cmap != config.COLORS['DIFF'] else -vmax
                
                im = data.plot(ax=ax, cmap=cmap, transform=ccrs.PlateCarree(), add_colorbar=False, vmin=vmin, vmax=vmax)
                
                # Add colorbar
                cbar = plt.colorbar(im, ax=ax, orientation='horizontal', pad=0.05, shrink=0.8)
                cbar.set_label('Volumetric Soil Moisture (m³/m³)')
                
                ax.set_title(title, fontweight='bold')
                gl = ax.gridlines(draw_labels=True, linestyle='--', alpha=0.5)
                gl.top_labels = False; gl.right_labels = False

            output_path = os.path.join(config.DIR_FIGURES, f"fig03_sm_assim_impact_{season}.png")
            plt.savefig(output_path)
            print(f"Figure 3 ({season}) saved to: {output_path}")

if __name__ == "__main__":
    plot_sm_assim_impact()
