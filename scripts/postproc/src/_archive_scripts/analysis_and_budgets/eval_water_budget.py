# ==============================================================================
# Author : M. EL AAbaribaoune
# Purpose: Internal water budget consistency checks for LIS/Noah-MP runs.
#          Extracts Precipitation, ET, Runoff, and Storage to ensure that
#          data assimilation increments preserve the physical closure of the 
#          water cycle. Generates multiple isolated figures.
# ==============================================================================

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import netCDF4 as nc
from datetime import datetime
from utils_eval import get_lis_files, load_lis_variable, calculate_basin_average

# Apply beautiful seaborn styling
sns.set_theme(style="whitegrid", palette="muted", font_scale=1.1)

# ==============================================================================
# 1. CONFIGURATION
# ==============================================================================
import config_postproc as cfg

OPL_DIR = cfg.DIR_OUTPUT_OL
DA_DIR = cfg.DIR_OUTPUT_DA
START_DATE = cfg.START_DATE
END_DATE = cfg.END_DATE
LDT_FILE = cfg.LDT_FILE
OUT_FIG_DIR = cfg.DIR_FIGURES

os.makedirs(OUT_FIG_DIR, exist_ok=True)

# Standard Noah-MP vertical soil layer thicknesses (in mm)
DZ = np.array([100.0, 300.0, 600.0, 1000.0])

# Load Landmask for spatial averaging
ds_ldt = nc.Dataset(LDT_FILE, "r")
landmask = ds_ldt.variables["LANDMASK"][:]
ds_ldt.close()

# ==============================================================================
# 2. DATA EXTRACTION ENGINE
# ==============================================================================
def compute_water_budget(exp_dir, start_date, end_date):
    """
    Load all water budget components (fluxes and states) for a given experiment
    directory, convert them to standard units (mm), and compute basin averages.
    """
    files = get_lis_files(exp_dir, start_date, end_date)
    if not files:
        print(f"Warning: No files found in {exp_dir}")
        return None
        
    print(f"Processing {len(files)} files from {exp_dir}...")
    
    # --- Load Flux Variables (Output as kg/m2/s = mm/s) ---
    precip = load_lis_variable(files, "TotalPrecip_tavg")
    
    # Try fetching Evap directly, fallback to latent heat (Qle) converted to ET
    evap = load_lis_variable(files, "Evap_tavg") 
    if evap is None:
        qle = load_lis_variable(files, "Qle_tavg")
        if qle is not None:
            evap = qle / 2.501e6  # Convert W/m2 to kg/m2/s
            
    qs = load_lis_variable(files, "Qs_tavg")    # Surface Runoff
    qsb = load_lis_variable(files, "Qsb_tavg")  # Baseflow/Subsurface Runoff
    
    # --- Load State Variables (m3/m3 or kg/m2) ---
    sm = load_lis_variable(files, "SoilMoist_tavg") # (time, 4 layers, lat, lon)
    canop = load_lis_variable(files, "CanopInt_tavg")
    swe = load_lis_variable(files, "SWE_tavg")
    
    # --- Convert to Basin Averages (mm/day for fluxes) ---
    p_avg = calculate_basin_average(precip, landmask) * 86400 
    e_avg = calculate_basin_average(evap, landmask) * 86400 if evap is not None else np.zeros_like(p_avg)
    qs_avg = calculate_basin_average(qs, landmask) * 86400
    qsb_avg = calculate_basin_average(qsb, landmask) * 86400
    
    # Calculate total soil moisture column depth in mm
    if sm is not None:
        sm_mm = np.zeros((sm.shape[0], sm.shape[2], sm.shape[3]))
        for i in range(4):
            sm_mm += sm[:, i, :, :] * DZ[i]
        sm_avg = calculate_basin_average(sm_mm, landmask)
    else:
        sm_avg = np.zeros_like(p_avg)
        
    canop_avg = calculate_basin_average(canop, landmask) if canop is not None else np.zeros_like(p_avg)
    swe_avg = calculate_basin_average(swe, landmask) if swe is not None else np.zeros_like(p_avg)
    
    # Total Terrestrial Water Storage
    total_storage = sm_avg + canop_avg + swe_avg
    
    # Calculate derivative of storage (dS/dt) in mm/day using simple backward difference
    dsdt = np.zeros_like(p_avg)
    if len(total_storage) > 1:
        dsdt[1:] = total_storage[1:] - total_storage[:-1]
        dsdt[0] = 0 # Assume 0 change on the very first timestep
        
    # Calculate closure residual (P - E - R - dS/dt)
    residual = p_avg - e_avg - qs_avg - qsb_avg - dsdt
    
    return {
        "P": p_avg, "E": e_avg, "Qs": qs_avg, "Qsb": qsb_avg, 
        "dSdt": dsdt, "Residual": residual,
        "Storage": total_storage, "SM_profile": sm
    }

# Execute extraction
print("Computing budget for Open Loop (OPL)...")
opl_budget = compute_water_budget(OPL_DIR, START_DATE, END_DATE)

print("Computing budget for Data Assimilation (DA)...")
da_budget = compute_water_budget(DA_DIR, START_DATE, END_DATE)

# Safe guard against empty directories
if opl_budget is None or da_budget is None:
    print("Cannot plot figures: One or both datasets are missing.")
    exit()

days = np.arange(len(opl_budget["P"]))


# ==============================================================================
# 3. PLOTTING FUNCTIONS
# ==============================================================================

def plot_budget_components():
    """Generates a stacked time-series of Precipitation, ET, Runoff, and Storage."""
    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Top Panel: Open Loop
    ax = axes[0]
    ax.plot(days, opl_budget["P"], 'b-', label='P (Precipitation)', linewidth=2)
    ax.plot(days, opl_budget["E"], 'g-', label='ET', linewidth=2)
    ax.plot(days, opl_budget["Qs"] + opl_budget["Qsb"], 'r-', label='Runoff (Qs + Qsb)', linewidth=2)
    ax.plot(days, opl_budget["dSdt"], 'c-', label='dS/dt (Storage Change)', linewidth=2)
    ax.set_ylabel('Flux (mm/day)', fontweight='bold')
    ax.set_title('Water Budget Components - Open Loop (OPL)', fontsize=13, fontweight='bold')
    ax.legend(loc='upper right', frameon=True, shadow=True)

    # Bottom Panel: Data Assimilation
    ax = axes[1]
    ax.plot(days, da_budget["P"], 'b-', label='P (Precipitation)', linewidth=2)
    ax.plot(days, da_budget["E"], 'g--', label='ET', linewidth=2)
    ax.plot(days, da_budget["Qs"] + da_budget["Qsb"], 'r--', label='Runoff (Qs + Qsb)', linewidth=2)
    ax.plot(days, da_budget["dSdt"], 'c--', label='dS/dt (Storage Change)', linewidth=2)
    ax.set_ylabel('Flux (mm/day)', fontweight='bold')
    ax.set_title('Water Budget Components - Data Assimilation (DA)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Days since start', fontweight='bold')
    ax.legend(loc='upper right', frameon=True, shadow=True)

    period_str = f"{START_DATE.strftime('%b %d, %Y')} to {END_DATE.strftime('%b %d, %Y')}"
    fig.suptitle(f"Water Budget Components (Fluxes & Storage Changes)\nNorth Morocco Basin | {period_str}", fontsize=15, fontweight='bold', y=0.98)

    plt.tight_layout()
    fig.subplots_adjust(top=0.92)
    save_path = os.path.join(OUT_FIG_DIR, "budget_components.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_budget_residual():
    """Plots the water budget closure error (Residual = P - E - R - dS/dt)."""
    plt.figure(figsize=(9, 5))
    
    plt.plot(days, opl_budget["Residual"], 'k-', linewidth=2, label='Residual OPL')
    plt.plot(days, da_budget["Residual"], 'r--', linewidth=2, label='Residual DA')
    
    plt.axhline(0, color='gray', linestyle=':')
    plt.ylabel('Residual (mm/day)', fontweight='bold')
    plt.xlabel('Days since start', fontweight='bold')
    
    period_str = f"{START_DATE.strftime('%b %d, %Y')} to {END_DATE.strftime('%b %d, %Y')}"
    plt.title(f'Daily Water Budget Closure Residual (P - E - R - dS/dt)\nNorth Morocco Basin | {period_str}', fontsize=14, fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "budget_residual.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_runoff_partitioning():
    """Evaluates the partitioning between Surface Runoff and Total Runoff."""
    plt.figure(figsize=(9, 5))
    
    opl_qtot = opl_budget["Qs"] + opl_budget["Qsb"]
    da_qtot = da_budget["Qs"] + da_budget["Qsb"]

    # Calculate ratios cleanly (avoid division by zero if total runoff is 0)
    opl_ratio = np.divide(opl_budget["Qs"], opl_qtot, out=np.zeros_like(opl_qtot), where=opl_qtot!=0)
    da_ratio = np.divide(da_budget["Qs"], da_qtot, out=np.zeros_like(da_qtot), where=da_qtot!=0)

    plt.plot(days, opl_ratio, 'b-', linewidth=2, label='OPL Surface Runoff Ratio')
    plt.plot(days, da_ratio, 'r--', linewidth=2, label='DA Surface Runoff Ratio')
    
    plt.ylabel('Ratio (Qs / Qtotal)', fontweight='bold')
    plt.xlabel('Days since start', fontweight='bold')
    
    period_str = f"{START_DATE.strftime('%b %d, %Y')} to {END_DATE.strftime('%b %d, %Y')}"
    plt.title(f'Runoff Partitioning Dynamics: Surface Runoff vs. Total Runoff\nNorth Morocco Basin | {period_str}', fontsize=14, fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "runoff_partitioning.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_sm_profile_evolution():
    """Plots the vertical soil moisture profile dynamics across the 4 Noah-MP layers."""
    # Pre-calculate basin averages for each layer independently
    opl_sm_profile = [calculate_basin_average(opl_budget["SM_profile"][:, i, :, :], landmask) for i in range(4)]
    da_sm_profile = [calculate_basin_average(da_budget["SM_profile"][:, i, :, :], landmask) for i in range(4)]

    fig, axes = plt.subplots(4, 1, figsize=(10, 11), sharex=True)
    layers = ['0 - 10 cm', '10 - 40 cm', '40 - 100 cm', '100 - 200 cm']
    
    for i in range(4):
        axes[i].plot(days, opl_sm_profile[i], 'b-', linewidth=2, label='OPL' if i==0 else "")
        axes[i].plot(days, da_sm_profile[i], 'r--', linewidth=2, label='DA' if i==0 else "")
        
        axes[i].set_ylabel('SM (m³/m³)', fontweight='bold')
        axes[i].set_title(f'Noah-MP Layer {i+1}: {layers[i]}', fontsize=11, fontweight='bold')
        
        if i == 0:
            axes[i].legend(loc='upper right', frameon=True, shadow=True)

    axes[3].set_xlabel('Days since start', fontweight='bold')
    period_str = f"{START_DATE.strftime('%b %d, %Y')} to {END_DATE.strftime('%b %d, %Y')}"
    fig.suptitle(f'Soil Moisture Profile Evolution (Noah-MP Layers 1 to 4)\nNorth Morocco Basin | {period_str}', fontsize=15, fontweight='bold', y=0.98)
    
    plt.tight_layout()
    fig.subplots_adjust(top=0.92)
    save_path = os.path.join(OUT_FIG_DIR, "sm_profile_evolution.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")

# ==============================================================================
# 4. EXECUTE ALL PLOTS
# ==============================================================================
plot_budget_components()
plot_budget_residual()
plot_runoff_partitioning()
plot_sm_profile_evolution()

print("\nAll Water Budget evaluations completed successfully.")
