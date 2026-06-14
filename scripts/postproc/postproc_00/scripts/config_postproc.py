import os
import numpy as np
from datetime import datetime

# ==========================================
# 1. DIRECTORY PATHS
# ==========================================
PROJECT_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"

# LIS Outputs (NorthMor 3days experiment)
DIR_OUTPUT_OL = os.path.join(PROJECT_ROOT, "experiments/NorthMor/3days/opl/output/SURFACEMODEL")
DIR_OUTPUT_DA = os.path.join(PROJECT_ROOT, "experiments/NorthMor/3days/assim/smap_assim/output/SURFACEMODEL")

# Simulation period
START_DATE = datetime(2016, 1, 1) # Updating to default starting date. Scripts will use what is available.
END_DATE = datetime(2016, 1, 3)

# Observation / Forcing Data
FILE_DEM_SRTM = os.path.join(PROJECT_ROOT, "data/lis_input/MNT_SRTM_30m.tif")
FILE_LAND_COVER = os.path.join(PROJECT_ROOT, "data/lis_input/lis_input_NorthMor_5km.nc") # Also acts as LDT_FILE
LDT_FILE = FILE_LAND_COVER
FILE_OBS_GMIA = os.path.join(PROJECT_ROOT, "data/land_params/GMIA/gmia_v5_aei_pct.asc")
DIR_OBS_MODIS_LAI = os.path.join(PROJECT_ROOT, "data/observations_archive/MODIS_LAI/processed")
DIR_OBS_WAPOR = os.path.join(PROJECT_ROOT, "data/observations/WaPOR")
DIR_OBS_FLUXSAT = os.path.join(PROJECT_ROOT, "data/observations/FLUXSAT")
DIR_OBS_GLDAS = os.path.join(PROJECT_ROOT, "data/observations/GLDAS")
DIR_OBS_INSITU = os.path.join(PROJECT_ROOT, "data/validation/streamflow")

# Output directory for figures
DIR_FIGURES = os.path.join(PROJECT_ROOT, "scripts/postproc/postproc_00/figures")
os.makedirs(DIR_FIGURES, exist_ok=True)

# ==========================================
# 2. STUDY DOMAIN EXTENT (North Morocco Basin)
# ==========================================
DOMAIN_LON_MIN = -10.0
DOMAIN_LON_MAX = -1.0
DOMAIN_LAT_MIN = 30.0
DOMAIN_LAT_MAX = 36.0

# ==========================================
# 3. PLOTTING CONFIGURATION
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
    'DIFF': 'coolwarm',  # Colormap for difference maps
    'AGRI': '#e377c2',
    'FOREST': '#2ca02c',
    'SHRUB': '#8c564b',
    'GRASS': '#bcbd22'
}

# ==========================================
# 4. STATISTICAL METRICS (Common Functions)
# ==========================================
def calc_bias(sim, obs):
    return np.nanmean(sim - obs)

def calc_rmse(sim, obs):
    return np.sqrt(np.nanmean((sim - obs)**2))

def calc_ubrmse(sim, obs):
    bias = calc_bias(sim, obs)
    rmse = calc_rmse(sim, obs)
    if np.isnan(bias) or np.isnan(rmse): return np.nan
    val = rmse**2 - bias**2
    return np.sqrt(val) if val > 0 else 0.0

def calc_pearson_r(sim, obs):
    valid = ~np.isnan(sim) & ~np.isnan(obs)
    if not np.any(valid): return np.nan
    if len(sim[valid]) < 2: return np.nan
    return np.corrcoef(sim[valid], obs[valid])[0, 1]

def calc_kge(sim, obs):
    valid = ~np.isnan(sim) & ~np.isnan(obs)
    if not np.any(valid): return np.nan
    sim, obs = sim[valid], obs[valid]
    if len(sim) == 0: return np.nan
    r = np.corrcoef(sim, obs)[0, 1]
    std_obs = np.std(obs)
    mean_obs = np.mean(obs)
    if std_obs == 0 or mean_obs == 0: return np.nan
    alpha = np.std(sim) / std_obs
    beta = np.mean(sim) / mean_obs
    return 1 - np.sqrt((r - 1)**2 + (alpha - 1)**2 + (beta - 1)**2)

def calc_nse(sim, obs):
    valid = ~np.isnan(sim) & ~np.isnan(obs)
    if not np.any(valid): return np.nan
    sim, obs = sim[valid], obs[valid]
    if len(sim) == 0: return np.nan
    denom = np.sum((obs - np.mean(obs))**2)
    if denom == 0: return np.nan
    return 1 - (np.sum((sim - obs)**2) / denom)
