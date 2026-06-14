import os
import numpy as np

# ==========================================
# 1. DIRECTORY PATHS
# ==========================================
PROJECT_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"

# LIS Outputs (3 days test setup, to be updated for full runs)
DIR_OUTPUT_OL = os.path.join(PROJECT_ROOT, "experiments/3days/opl/output/SURFACEMODEL")
DIR_OUTPUT_DA = os.path.join(PROJECT_ROOT, "experiments/3days/assim_tests/output_smap/SURFACEMODEL")

# HyMAP Outputs (Currently missing, update when available)
DIR_OUTPUT_ROUTING_OL = os.path.join(PROJECT_ROOT, "experiments/3days/opl/output/ROUTING")
DIR_OUTPUT_ROUTING_DA = os.path.join(PROJECT_ROOT, "experiments/3days/assim_tests/output_smap/ROUTING")

# Observation / Forcing Data
DIR_OBS_GLDAS = os.path.join(PROJECT_ROOT, "data/observations/GLDAS") # Missing
FILE_OBS_GMIA = os.path.join(PROJECT_ROOT, "data/land_params/GMIA/gmia_v5_aei_pct.asc")
DIR_OBS_INSITU = os.path.join(PROJECT_ROOT, "data/validation/streamflow") # Missing
FILE_DEM_SRTM = os.path.join(PROJECT_ROOT, "data/lis_input/MNT_SRTM_30m.tif") # Update with actual if available

# Output directory for figures
DIR_FIGURES = os.path.join(PROJECT_ROOT, "scripts/postproc/postproc_01/Figs")
os.makedirs(DIR_FIGURES, exist_ok=True)


# ==========================================
# 2. STUDY DOMAIN EXTENT (Sebou Basin)
# ==========================================
# Example bounds, adjust to exact LIS domain
DOMAIN_LON_MIN = -7.0
DOMAIN_LON_MAX = -4.0
DOMAIN_LAT_MIN = 33.0
DOMAIN_LAT_MAX = 35.5


# ==========================================
# 3. PLOTTING CONFIGURATION (Q1 Publication)
# ==========================================
PLOT_RC_PARAMS = {
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 12,
    'axes.labelsize': 14,
    'axes.titlesize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 12,
    'figure.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.format': 'png'
}

COLORS = {
    'OL': '#1f77b4',     # Blue
    'DA': '#ff7f0e',     # Orange
    'OBS': '#2ca02c',    # Green
    'DIFF': 'coolwarm'   # Colormap for difference maps
}


# ==========================================
# 4. STATISTICAL METRICS (Common Functions)
# ==========================================
def calc_bias(sim, obs):
    return np.nanmean(sim - obs)

def calc_rmse(sim, obs):
    return np.sqrt(np.nanmean((sim - obs)**2))

def calc_kge(sim, obs):
    """
    Kling-Gupta Efficiency (KGE)
    """
    valid = ~np.isnan(sim) & ~np.isnan(obs)
    if not np.any(valid): return np.nan
    sim, obs = sim[valid], obs[valid]
    
    r = np.corrcoef(sim, obs)[0, 1]
    alpha = np.std(sim) / np.std(obs)
    beta = np.mean(sim) / np.mean(obs)
    
    return 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

def calc_nse(sim, obs):
    """
    Nash-Sutcliffe Efficiency (NSE)
    """
    valid = ~np.isnan(sim) & ~np.isnan(obs)
    if not np.any(valid): return np.nan
    sim, obs = sim[valid], obs[valid]
    
    return 1 - (np.sum((sim - obs)**2) / np.sum((obs - np.mean(obs))**2))
