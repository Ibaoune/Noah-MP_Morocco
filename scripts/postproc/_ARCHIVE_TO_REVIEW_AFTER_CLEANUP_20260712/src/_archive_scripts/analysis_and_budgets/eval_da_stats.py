# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Author : M. EL AAbaribaoune
# Purpose: Data Assimilation EnKF Diagnostics.
#          Evaluates probability distributions of state variables before and 
#          after assimilation to check for climatological shifts, and extracts
#          DA Increments and Innovations when available in the history files.
# ==============================================================================

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import netCDF4 as nc
from datetime import datetime
from utils_eval import get_lis_files, load_lis_variable

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

# ==============================================================================
# 2. DATA EXTRACTION
# ==============================================================================
# Soil Moisture (Top Layer: index 0)
opl_sm = load_lis_variable(opl_files, "SoilMoist_tavg", extract_layer=0)
da_sm = load_lis_variable(da_files, "SoilMoist_tavg", extract_layer=0)

def extract_da_diagnostics(da_files):
    """Extract increments or innovations if available, otherwise return None."""
    increments = load_lis_variable(da_files, "SmInc_tavg")
    innovations = load_lis_variable(da_files, "SmInnov_tavg")
    return increments, innovations

increments, innovations = extract_da_diagnostics(da_files)


# ==============================================================================
# 3. PLOTTING FUNCTIONS
# ==============================================================================

def plot_pdf(opl_data, da_data, var_name, title, xlabel):
    """
    Plots the Probability Density Function (PDF) for OPL and DA.
    Helps visualize how DA shifts or tightens the distribution of states.
    """
    if opl_data is None or da_data is None:
        return
        
    # Flatten arrays and apply landmask to isolate basin pixels
    opl_flat = opl_data[:, landmask == 1].flatten()
    da_flat = da_data[:, landmask == 1].flatten()
    
    # Remove missing/NaN data
    opl_valid = opl_flat[~np.isnan(opl_flat)]
    da_valid = da_flat[~np.isnan(da_flat)]
    
    plt.figure(figsize=(9, 6))
    
    # Plot PDFs (density=True)
    sns.histplot(opl_valid, bins=50, stat="density", color='blue', alpha=0.5, label='OPL', kde=True)
    sns.histplot(da_valid, bins=50, stat="density", color='red', alpha=0.5, label='DA', kde=True)
    
    # Plot vertical lines for Means
    plt.axvline(np.mean(opl_valid), color='blue', linestyle='dashed', linewidth=2, label=f'OPL Mean: {np.mean(opl_valid):.3f}')
    plt.axvline(np.mean(da_valid), color='red', linestyle='dashed', linewidth=2, label=f'DA Mean: {np.mean(da_valid):.3f}')
    
    plt.title(title, fontsize=14, fontweight='bold')
    plt.xlabel(xlabel, fontweight='bold')
    plt.ylabel('Density', fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, f"pdf_{var_name}.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_increments(increments):
    """Plots the spatial mean assimilation increment map."""
    if increments is None:
        return
        
    mean_inc = np.nanmean(increments, axis=0)
    mean_inc = np.ma.masked_where(landmask != 1, mean_inc)
    
    plt.figure(figsize=(9, 6))
    
    vmax = np.nanmax(np.abs(mean_inc))
    if vmax == 0 or np.isnan(vmax): vmax = 1
        
    plt.imshow(mean_inc, cmap='RdBu', origin='lower', vmin=-vmax, vmax=vmax)
    plt.colorbar(label='Mean Increment (m³/m³)')
    plt.title('Mean Assimilation Increment', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "mean_increment_map.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


def plot_innovations(innovations):
    """Plots the histogram of observation innovations (Observation - Background)."""
    if innovations is None:
        return
        
    innov_flat = innovations[:, landmask == 1].flatten()
    innov_valid = innov_flat[~np.isnan(innov_flat)]
    
    plt.figure(figsize=(9, 6))
    sns.histplot(innov_valid, bins=50, stat="density", color='green', alpha=0.7, kde=True)
    
    plt.axvline(0, color='black', linestyle='--', linewidth=1.5)
    plt.axvline(np.mean(innov_valid), color='red', linestyle='-', linewidth=2, label=f'Mean: {np.mean(innov_valid):.4f}')
    
    plt.title('Innovation Distribution (Observation - Background)', fontsize=14, fontweight='bold')
    plt.xlabel('Innovation (m³/m³)', fontweight='bold')
    plt.ylabel('Density', fontweight='bold')
    plt.legend(frameon=True, shadow=True)
    
    plt.tight_layout()
    save_path = os.path.join(OUT_FIG_DIR, "innovation_pdf.png")
    plt.savefig(save_path, dpi=300)
    plt.close()
    print(f"Saved: {save_path}")


# ==============================================================================
# 4. EXECUTE ALL PLOTS
# ==============================================================================
print("Plotting distribution PDFs...")
plot_pdf(opl_sm, da_sm, "SM_top", "Probability Density Function: Top Layer SM", "Soil Moisture (m³/m³)")

if increments is not None:
    print("Plotting Increment statistics...")
    plot_increments(increments)
else:
    print("Note: Increment variable not found in history files.")

if innovations is not None:
    print("Plotting Innovation statistics...")
    plot_innovations(innovations)
else:
    print("Note: Innovation variable not found in history files.")

print("\nDA diagnostics evaluation completed.")
