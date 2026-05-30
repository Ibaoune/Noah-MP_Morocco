# Author: M. EL Aabaribaoune (@um6p)
import os
import glob
import numpy as np
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import warnings

warnings.filterwarnings("ignore")

# Define paths
BASE_DIR = 'experiments'
EXPERIMENTS = {
    'Open-Loop': 'OPL_sebou',
    'DA SMAP': 'DA_SM_sebou',
    'DA MODIS LAI': 'DA_LAI_sebou',
    'DA Joint': 'DA_Joint_sebou'
}

COLORS = {
    'Open-Loop': 'black',
    'DA SMAP': 'blue',
    'DA MODIS LAI': 'green',
    'DA Joint': 'red'
}

OUT_DIR = os.path.join(BASE_DIR, 'plots')
os.makedirs(OUT_DIR, exist_ok=True)

# Variables to extract
VARIABLES = ['SoilMoist_tavg', 'LAI_inst', 'Evap_tavg', 'Qs_tavg', 'Qsb_tavg']
FILL_VALUE = -9999.0

# Soil layer thicknesses in meters for Noah-MP (0.1, 0.3, 0.6, 1.0)
SOIL_THICKNESS = np.array([0.1, 0.3, 0.6, 1.0])
TOTAL_THICKNESS = np.sum(SOIL_THICKNESS)

def load_experiment_data(exp_name, exp_folder):
    """Loads and preprocesses netCDF data for a given experiment."""
    files = sorted(glob.glob(os.path.join(BASE_DIR, exp_folder, 'SURFACEMODEL', '202006', 'LIS_HIST_*.nc')))
    if not files:
        print(f"Warning: No files found for {exp_name} in {exp_folder}")
        return None
    
    # Open dataset avoiding dask (which is causing version mismatch errors)
    datasets_list = []
    for f in files:
        with xr.open_dataset(f) as temp_ds:
            temp_ds.load()
            datasets_list.append(temp_ds)
            
    ds = xr.concat(datasets_list, dim='time')
    
    # Mask invalid values
    for var in VARIABLES:
        if var in ds:
            ds[var] = ds[var].where(ds[var] != FILL_VALUE)
            
    # Calculate derived variables
    if 'SoilMoist_tavg' in ds:
        # Surface Soil Moisture (Layer 1)
        ds['SSM'] = ds['SoilMoist_tavg'].isel(SoilMoist_profiles=0)
        ds['SSM'].attrs['long_name'] = 'Surface Soil Moisture (0-10cm)'
        ds['SSM'].attrs['units'] = 'm3/m3'
        
        # Root Zone Soil Moisture (Weighted average of all 4 layers, 0-200cm)
        # Multiply each layer by its thickness, sum them, and divide by total thickness
        rzsm = (ds['SoilMoist_tavg'] * xr.DataArray(SOIL_THICKNESS, dims=['SoilMoist_profiles'])).sum(dim='SoilMoist_profiles') / TOTAL_THICKNESS
        # Re-apply mask where any layer was missing
        mask = ds['SoilMoist_tavg'].isel(SoilMoist_profiles=0).notnull()
        ds['RZSM'] = rzsm.where(mask)
        ds['RZSM'].attrs['long_name'] = 'Root Zone Soil Moisture (0-200cm)'
        ds['RZSM'].attrs['units'] = 'm3/m3'
        
    if 'Qs_tavg' in ds and 'Qsb_tavg' in ds:
        ds['Total_Runoff'] = ds['Qs_tavg'] + ds['Qsb_tavg']
        ds['Total_Runoff'].attrs['long_name'] = 'Total Runoff'
        ds['Total_Runoff'].attrs['units'] = 'kg m-2 s-1'

    return ds

print("Loading data...")
datasets = {}
for name, folder in EXPERIMENTS.items():
    ds = load_experiment_data(name, folder)
    if ds is not None:
        datasets[name] = ds

if not datasets:
    raise ValueError("No data could be loaded!")

# 1. Time Series Plots (Basin Spatial Mean)
print("Computing spatial means and plotting time series...")
plot_vars = {
    'SSM': 'Surface Soil Moisture (m³/m³)',
    'RZSM': 'Root Zone Soil Moisture (m³/m³)',
    'LAI_inst': 'Leaf Area Index (-)',
    'Evap_tavg': 'Total Evapotranspiration (kg m⁻² s⁻¹)',
    'Total_Runoff': 'Total Runoff (kg m⁻² s⁻¹)'
}

fig, axes = plt.subplots(len(plot_vars), 1, figsize=(10, 15), sharex=True)
plt.subplots_adjust(hspace=0.3)

for ax, (var, ylabel) in zip(axes, plot_vars.items()):
    for exp_name, ds in datasets.items():
        if var in ds:
            # Calculate spatial mean over valid pixels
            spatial_mean = ds[var].mean(dim=['north_south', 'east_west']).compute()
            
            # Create a simple time array based on days (since time var might be missing or complex)
            days = np.arange(1, len(spatial_mean) + 1)
            
            ax.plot(days, spatial_mean, label=exp_name, color=COLORS.get(exp_name, 'black'), marker='o', linewidth=2)
            
    ax.set_ylabel(ylabel)
    ax.set_title(f'Basin-Averaged {var}')
    ax.grid(True, linestyle='--', alpha=0.7)
    if ax == axes[0]:
        ax.legend()

axes[-1].set_xlabel('Simulation Day (June 2020)')
axes[-1].set_xticks([1, 2, 3])
axes[-1].set_xticklabels(['June 2', 'June 3', 'June 4'])

out_ts_path = os.path.join(OUT_DIR, 'DA_TimeSeries_Comparison.png')
plt.savefig(out_ts_path, dpi=300, bbox_inches='tight')
print(f"Saved time series plot to {out_ts_path}")
plt.close()

# 2. Spatial Difference Maps (Mean over the 3 days)
# We will plot DA_Joint - Open-Loop
print("Generating spatial difference maps (DA_Joint - Open-Loop)...")

if 'Open-Loop' in datasets and 'DA Joint' in datasets:
    ds_opl = datasets['Open-Loop'].mean(dim='time').compute()
    ds_joint = datasets['DA Joint'].mean(dim='time').compute()
    
    map_vars = ['SSM', 'RZSM', 'LAI_inst', 'Evap_tavg']
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()
    
    for ax, var in zip(axes, map_vars):
        if var in ds_opl and var in ds_joint:
            diff = ds_joint[var] - ds_opl[var]
            
            # Determine symmetric color limits for difference
            vmax = np.nanpercentile(np.abs(diff.values), 98)
            if np.isnan(vmax) or vmax == 0:
                vmax = 1e-5 # fallback
                
            im = ax.imshow(diff.values, cmap='RdBu', origin='lower', vmin=-vmax, vmax=vmax)
            ax.set_title(f'Δ {var} (DA Joint - OPL)')
            ax.axis('off')
            plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
            
    plt.tight_layout()
    out_map_path = os.path.join(OUT_DIR, 'DA_Spatial_Difference_Maps.png')
    plt.savefig(out_map_path, dpi=300, bbox_inches='tight')
    print(f"Saved spatial difference maps to {out_map_path}")
    plt.close()

# Let's also do a specific DA LAI - OPL map for LAI
if 'Open-Loop' in datasets and 'DA MODIS LAI' in datasets:
    ds_lai_da = datasets['DA MODIS LAI'].mean(dim='time').compute()
    
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    diff_lai = ds_lai_da['LAI_inst'] - ds_opl['LAI_inst']
    vmax = np.nanpercentile(np.abs(diff_lai.values), 98)
    if np.isnan(vmax) or vmax == 0: vmax = 1e-5
    
    im = ax.imshow(diff_lai.values, cmap='RdBu', origin='lower', vmin=-vmax, vmax=vmax)
    ax.set_title('Δ LAI (DA MODIS LAI - OPL)')
    ax.axis('off')
    plt.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    
    out_lai_map = os.path.join(OUT_DIR, 'DA_LAI_Difference_Map.png')
    plt.savefig(out_lai_map, dpi=300, bbox_inches='tight')
    print(f"Saved LAI spatial difference map to {out_lai_map}")
    plt.close()

print("Plotting complete!")
