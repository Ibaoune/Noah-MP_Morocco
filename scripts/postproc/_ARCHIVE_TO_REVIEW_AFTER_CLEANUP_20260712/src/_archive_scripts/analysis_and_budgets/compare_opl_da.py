# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Author : M. EL AAbaribaoune
# Purpose: Direct comparative diagnostics between Open Loop (OPL) and 
#          Data Assimilation (DA) experiments. Computes statistical differences
#          and generates basin-wide time-series and spatial difference maps.
# ==============================================================================

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import netCDF4 as nc
from datetime import datetime

# Local utility imports
from utils_eval import get_lis_files, load_lis_variable, calculate_basin_average, calculate_metrics

# Apply beautiful seaborn styling
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ==============================================================================
# 1. CONFIGURATION & SETUP
# ==============================================================================
import config_postproc as cfg

OPL_DIR = cfg.DIR_OUTPUT_OL
DA_DIR = cfg.DIR_OUTPUT_DA
START_DATE = cfg.START_DATE
END_DATE = cfg.END_DATE
LDT_FILE = cfg.LDT_FILE
OUT_FIG_DIR = cfg.DIR_FIGURES

os.makedirs(OUT_FIG_DIR, exist_ok=True)

# Load domain definitions (Lat/Lon and Landmask)
print("Loading spatial domain and data...")
ds_ldt = nc.Dataset(LDT_FILE, "r")
lats_ldt = ds_ldt.variables["lat"][:]
lons_ldt = ds_ldt.variables["lon"][:]
landmask = ds_ldt.variables["LANDMASK"][:]
ds_ldt.close()

# Gather File Paths
opl_files = get_lis_files(OPL_DIR, START_DATE, END_DATE)
da_files = get_lis_files(DA_DIR, START_DATE, END_DATE)

# Safe guard against missing files
if not opl_files or not da_files:
    print("Error: Missing OPL or DA files. Please verify the directories.")
    exit()

days = np.arange(len(opl_files))


# ==============================================================================
# 2. DATA EXTRACTION
# ==============================================================================
# Runoff extraction
opl_qs = load_lis_variable(opl_files, "Qs_tavg")
da_qs = load_lis_variable(da_files, "Qs_tavg")

# Soil Moisture extraction (Top Layer: index 0)
opl_sm = load_lis_variable(opl_files, "SoilMoist_tavg", extract_layer=0)
da_sm = load_lis_variable(da_files, "SoilMoist_tavg", extract_layer=0)

# Evapotranspiration extraction (with W/m2 to kg/m2/s conversion fallback)
opl_et = load_lis_variable(opl_files, "Evap_tavg")
da_et = load_lis_variable(da_files, "Evap_tavg")
if opl_et is None:
    qle_opl = load_lis_variable(opl_files, "Qle_tavg")
    if qle_opl is not None: opl_et = qle_opl / 2.501e6
if da_et is None:
    qle_da = load_lis_variable(da_files, "Qle_tavg")
    if qle_da is not None: da_et = qle_da / 2.501e6


# ==============================================================================
# 3. PLOTTING FUNCTIONS
# ==============================================================================

def plot_spatial_diff(opl_data, da_data, var_name, title, cmap='RdBu'):
    """
    Computes the temporal mean of the difference (DA - OPL) and plots it 
    spatially across the NorthMor basin.
    """
    if opl_data is None or da_data is None:
        return
        
    # Compute mean difference over time, masked by the land basin
    diff = np.nanmean(da_data - opl_data, axis=0)
    diff = np.ma.masked_where(landmask != 1, diff)
    
    fig, ax = plt.subplots(figsize=(10, 8), dpi=150)
    
    # Establish symmetric color bounds around zero
    vmax = np.nanmax(np.abs(diff))
    if vmax == 0 or np.isnan(vmax):
        vmax = 1
        
    # Plot heatmap
    im = ax.pcolormesh(lons_ldt, lats_ldt, diff, cmap=cmap, vmin=-vmax, vmax=vmax, shading="auto")
    
    # Overlay basin boundary
    ax.contour(lons_ldt, lats_ldt, landmask, colors='black', linewidths=1.2)
    
    # Custom Colorbar
    cbar = plt.colorbar(im, ax=ax, orientation='vertical', pad=0.03, shrink=0.8)
    cbar.set_label(f"Difference: DA - OPL", fontsize=11, fontweight='bold')
    
    period_str = f"{START_DATE.strftime('%b %Y')} to {END_DATE.strftime('%b %Y')}"
    plt.title(f"Spatial Mean Difference (DA - OPL): {title}\nPeriod: {period_str} | Resolution: 5 km", fontsize=14, fontweight="bold", pad=15)
    
    # Save Image
    save_path = os.path.join(OUT_FIG_DIR, f"diff_map_{var_name}.png")
    plt.savefig(save_path, bbox_inches="tight")
    plt.close()
    print(f"Saved: {save_path}")


def plot_basin_time_series():
    """
    Plots the basin-averaged time series for Surface Runoff, Soil Moisture, and ET.
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
    
    # 1. Surface Runoff
    if opl_qs is not None and da_qs is not None:
        axes[0].plot(days, calculate_basin_average(opl_qs, landmask)*86400, 'b-', linewidth=2, label='OPL')
        axes[0].plot(days, calculate_basin_average(da_qs, landmask)*86400, 'r--', linewidth=2, label='DA')
        axes[0].set_ylabel('Runoff (mm/day)', fontweight='bold')
        axes[0].set_title('Daily Basin-Averaged Surface Runoff', fontsize=12, fontweight='bold')
        axes[0].legend(frameon=True, shadow=True)

    # 2. Top Layer Soil Moisture
    if opl_sm is not None and da_sm is not None:
        axes[1].plot(days, calculate_basin_average(opl_sm, landmask), 'b-', linewidth=2, label='OPL')
        axes[1].plot(days, calculate_basin_average(da_sm, landmask), 'r--', linewidth=2, label='DA')
        axes[1].set_ylabel('SM (m³/m³)', fontweight='bold')
        axes[1].set_title('Daily Basin-Averaged Top Layer Soil Moisture (0-10 cm)', fontsize=12, fontweight='bold')

    # 3. Evapotranspiration
    if opl_et is not None and da_et is not None:
        axes[2].plot(days, calculate_basin_average(opl_et, landmask)*86400, 'b-', linewidth=2, label='OPL')
        axes[2].plot(days, calculate_basin_average(da_et, landmask)*86400, 'r--', linewidth=2, label='DA')
        axes[2].set_ylabel('ET (mm/day)', fontweight='bold')
        axes[2].set_title('Daily Basin-Averaged Evapotranspiration', fontsize=12, fontweight='bold')

    period_str = f"{START_DATE.strftime('%b %d, %Y')} to {END_DATE.strftime('%b %d, %Y')}"
    fig.suptitle(f"Hydrological Variables Comparison: Open Loop (OPL) vs. Data Assimilation (DA)\nNorth Morocco Basin | {period_str}", fontsize=14, fontweight='bold', y=0.98)
    
    axes[2].set_xlabel('Days since start', fontweight='bold')
    plt.tight_layout()
    fig.subplots_adjust(top=0.92)
    
    save_path = os.path.join(OUT_FIG_DIR, "basin_time_series_compare.png")
    plt.savefig(save_path)
    plt.close()
    print(f"Saved: {save_path}")


def print_comparative_statistics():
    """
    Computes summary statistics representing the deviation of DA relative to OPL.
    """
    if opl_sm is None or da_sm is None:
        return
        
    opl_sm_flat = opl_sm[:, landmask == 1].flatten()
    da_sm_flat = da_sm[:, landmask == 1].flatten()
    
    stats = calculate_metrics(opl_sm_flat, da_sm_flat)
    std_opl = np.std(opl_sm_flat)
    std_da = np.std(da_sm_flat)
    
    print("\n" + "="*50)
    print("--- Statistics for Top Layer SM (DA vs OPL) ---")
    print("="*50)
    print(f"OPL StdDev:  {std_opl:.4f}")
    print(f"DA StdDev:   {std_da:.4f}")
    print(f"Correlation: {stats['corr']:.4f}")
    print(f"RMSE:        {stats['rmse']:.4f}")
    print(f"Bias:        {stats['bias']:.4f}")
    print("="*50 + "\n")


# ==============================================================================
# 4. EXECUTE ALL PLOTS
# ==============================================================================
print("Plotting spatial difference maps...")
plot_spatial_diff(opl_qs, da_qs, "Runoff", "Surface Runoff")
plot_spatial_diff(opl_sm, da_sm, "SM_top", "Top Layer Soil Moisture", cmap='BrBG')
plot_spatial_diff(opl_et, da_et, "ET", "Evapotranspiration", cmap='PiYG')

print("Plotting basin-wide time series...")
plot_basin_time_series()

print("Calculating statistical distributions...")
print_comparative_statistics()

print("Comparative evaluation completed.")
