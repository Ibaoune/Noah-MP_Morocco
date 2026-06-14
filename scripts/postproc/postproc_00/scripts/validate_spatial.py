# ==============================================================================
# Author : M. EL AAbaribaoune
# Purpose: Independent Spatial Validation against external datasets.
#          Aggregates LIS outputs to construct Terrestrial Water Storage (TWS)
#          anomalies for GRACE comparison, and plots basin-averaged time series
#          for SM and ET against simulated satellite observations (ASCAT/GLEAM).
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
from utils_eval import get_lis_files, load_lis_variable, calculate_basin_average

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

# Placeholder paths for validation datasets (To be activated with multi-year data)
GRACE_FILE = "data/validation/water_storage/GRACE_GRACEFO/raw/GRCTellus.JPL.200204_202603.GLO.RL06.3M.MSCNv04CRI.nc"

os.makedirs(OUT_FIG_DIR, exist_ok=True)

# Load Landmask
print("Loading spatial domain and data...")
ds_ldt = nc.Dataset(LDT_FILE, "r")
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

# Noah-MP layer thicknesses in mm
DZ = np.array([100.0, 300.0, 600.0, 1000.0])

# ==============================================================================
# 2. DATA EXTRACTION & TWS CONSTRUCTION
# ==============================================================================
# Soil Moisture (Top Layer)
opl_sm = load_lis_variable(opl_files, "SoilMoist_tavg", extract_layer=0)
da_sm = load_lis_variable(da_files, "SoilMoist_tavg", extract_layer=0)

# Evapotranspiration
opl_et = load_lis_variable(opl_files, "Evap_tavg")
da_et = load_lis_variable(da_files, "Evap_tavg")
if opl_et is None:
    opl_qle = load_lis_variable(opl_files, "Qle_tavg")
    if opl_qle is not None: opl_et = opl_qle / 2.501e6
if da_et is None:
    da_qle = load_lis_variable(da_files, "Qle_tavg")
    if da_qle is not None: da_et = da_qle / 2.501e6

def construct_tws(files):
    """
    Constructs Terrestrial Water Storage (TWS) by summing soil moisture 
    (across all 4 layers), canopy interception, and snow water equivalent.
    """
    sm = load_lis_variable(files, "SoilMoist_tavg")
    canop = load_lis_variable(files, "CanopInt_tavg")
    swe = load_lis_variable(files, "SWE_tavg")
    
    if sm is None: 
        return None
    
    # Initialize TWS array
    tws = np.zeros((sm.shape[0], sm.shape[2], sm.shape[3]))
    
    # Add Soil Moisture layers (converted to mm)
    for i in range(4):
        tws += sm[:, i, :, :] * DZ[i]
        
    # Add Canopy and SWE if they exist
    if canop is not None: tws += canop
    if swe is not None: tws += swe
    
    return tws

opl_tws = construct_tws(opl_files)
da_tws = construct_tws(da_files)


# ==============================================================================
# 3. PLOTTING FUNCTIONS
# ==============================================================================

def plot_grace_validation(opl_tws, da_tws):
    """Plots TWS Anomalies against GRACE observation data."""
    if opl_tws is None or da_tws is None: return
    
    # Compute basin averages
    opl_tws_avg = calculate_basin_average(opl_tws, landmask)
    da_tws_avg = calculate_basin_average(da_tws, landmask)
    
    # Compute anomalies (Subtracting the temporal mean)
    opl_anom = opl_tws_avg - np.mean(opl_tws_avg)
    da_anom = da_tws_avg - np.mean(da_tws_avg)
    
    plt.figure(figsize=(10, 5))
    plt.plot(days, opl_anom, 'b-', marker='o', linewidth=2, label='OPL TWS Anomaly')
    plt.plot(days, da_anom, 'r--', marker='s', linewidth=2, label='DA TWS Anomaly')
    
    # Placeholder for actual GRACE data (which is monthly)
    plt.axhline(0, color='k', linestyle=':', linewidth=2, label='GRACE Anomaly (Monthly)')
    
    plt.title('Independent Validation: TWS Anomalies vs GRACE', fontsize=14, fontweight='bold')
    plt.xlabel('Days since start', fontweight='bold')
    plt.ylabel('TWS Anomaly (mm)', fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "validation_grace_tws.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_ascat_validation(opl_sm, da_sm):
    """Plots Top Layer Soil Moisture against ASCAT simulated observation data."""
    if opl_sm is None or da_sm is None: return
    
    opl_sm_avg = calculate_basin_average(opl_sm, landmask)
    da_sm_avg = calculate_basin_average(da_sm, landmask)
    
    plt.figure(figsize=(10, 5))
    plt.plot(days, opl_sm_avg, 'b-', marker='o', linewidth=2, label='OPL Top Layer SM')
    plt.plot(days, da_sm_avg, 'r--', marker='s', linewidth=2, label='DA Top Layer SM')
    
    # Mock ASCAT observation for testing the script structure
    mock_ascat = opl_sm_avg + np.random.normal(0, 0.02, size=len(opl_sm_avg))
    plt.plot(days, mock_ascat, 'g^', markersize=8, label='ASCAT Obs (Mock)')
    
    plt.title('Independent Validation: Surface Soil Moisture vs ASCAT', fontsize=14, fontweight='bold')
    plt.xlabel('Days since start', fontweight='bold')
    plt.ylabel('Soil Moisture (m³/m³)', fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "validation_ascat_sm.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_et_validation(opl_et, da_et):
    """Plots Evapotranspiration against GLEAM/MOD16 simulated observation data."""
    if opl_et is None or da_et is None: return
    
    opl_et_avg = calculate_basin_average(opl_et, landmask) * 86400
    da_et_avg = calculate_basin_average(da_et, landmask) * 86400
    
    plt.figure(figsize=(10, 5))
    plt.plot(days, opl_et_avg, 'b-', marker='o', linewidth=2, label='OPL ET')
    plt.plot(days, da_et_avg, 'r--', marker='s', linewidth=2, label='DA ET')
    
    # Mock GLEAM observation for testing the script structure
    mock_gleam = opl_et_avg * 1.1 + np.random.normal(0, 0.5, size=len(opl_et_avg))
    plt.plot(days, mock_gleam, 'mD', markersize=8, label='GLEAM/MOD16 ET (Mock)')
    
    plt.title('Independent Validation: Evapotranspiration vs GLEAM/MOD16', fontsize=14, fontweight='bold')
    plt.xlabel('Days since start', fontweight='bold')
    plt.ylabel('ET (mm/day)', fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "validation_et.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


# ==============================================================================
# 4. EXECUTE ALL PLOTS
# ==============================================================================
print("Plotting GRACE TWS validation...")
plot_grace_validation(opl_tws, da_tws)

print("Plotting ASCAT SM validation...")
plot_ascat_validation(opl_sm, da_sm)

print("Plotting GLEAM/MOD16 ET validation...")
plot_et_validation(opl_et, da_et)

print("\nIndependent Spatial Validation completed.")
