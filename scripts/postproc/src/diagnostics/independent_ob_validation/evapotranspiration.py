# Author: M. EL Aabaribaoune (@um6p)
"""
Evapotranspiration Independent Validation Diagnostic
Validates Noah-MP simulations (Open-Loop, DA-NoCDF, DA-CDF v2)
against independent satellite/reanalysis benchmark (GLEAM v4.3a) over 2016-2020.
"""

import os
import sys
import glob
import logging
import numpy as np
import pandas as pd
import xarray as xr
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.colors import ListedColormap, BoundaryNorm
from scipy.stats import pearsonr

try:
    from .dataset_registry import DatasetRegistry
    from .observation_loader import ObservationLoader
    from .lis_loader import LISLoader
    from .spatial_alignment import SpatialAlignment
    from .temporal_alignment import TemporalAlignment
    from .plotting import Plotting
except (ImportError, ValueError):
    from src.diagnostics.independent_ob_validation.dataset_registry import DatasetRegistry
    from src.diagnostics.independent_ob_validation.observation_loader import ObservationLoader
    from src.diagnostics.independent_ob_validation.lis_loader import LISLoader
    from src.diagnostics.independent_ob_validation.spatial_alignment import SpatialAlignment
    from src.diagnostics.independent_ob_validation.temporal_alignment import TemporalAlignment
    from src.diagnostics.independent_ob_validation.plotting import Plotting

logger = logging.getLogger(__name__)

# Default project paths
PROJECT_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
AUDIT_ROOT = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/smap-xai-audit"
DEFAULT_CACHE_DIR = os.path.join(AUDIT_ROOT, "data/processed/value/gleam")

def create_nie_colormap():
    """Create a discrete symmetric colormap matching Nie et al. (2022)."""
    colors = [
        '#7a00cc',   # deep purple (-0.4 to -0.3)
        '#1f7fff',   # blue (-0.3 to -0.2)
        '#38d6e6',   # cyan (-0.2 to -0.1)
        '#e0f7fa',   # light cyan / neutral (-0.1 to 0.0)
        '#fff3b0',   # pale yellow (0.0 to 0.1)
        '#f7a53a',   # yellow-orange (0.1 to 0.2)
        '#ff6b2d',   # orange (0.2 to 0.3)
        '#ff2a1f'    # red (0.3 to 0.4)
    ]
    cmap = ListedColormap(colors)
    cmap.set_over('#ff2a1f')
    cmap.set_under('#7a00cc')
    boundaries = [-0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4]
    norm = BoundaryNorm(boundaries, cmap.N, clip=True)
    return cmap, norm

# NOTE MÉTHODOLOGIQUE (Correction Étape 5) :
# L'évaluation de la significativité statistique d'une différence de corrélations appariées
# (DA vs GLEAM comparé à OL vs GLEAM, qui partagent la même série de référence et présentent
# une autocorrélation temporelle marquée) ne peut être réalisée rigoureusement par un test
# classique fondé sur la transformation de Fisher (qui suppose l'indépendance mutuelle des
# séries et des échantillons).
# Les cartes ΔR et ΔR_anom sont donc présentées à titre purement descriptif.
# Une analyse d'incertitude par bootstrap temporel apparié par blocs (paired block bootstrap)
# pourra être mise en œuvre ultérieurement si nécessaire.

def format_geo_map(ax, extent=[-10.5, -0.5, 29.5, 36.5]):
    """Apply consistent geographic formatting to a Cartopy axis."""
    ax.set_facecolor('white')
    ax.add_feature(cfeature.COASTLINE, linewidth=0.6, edgecolor='#333333', zorder=2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.6, linestyle=':', edgecolor='#555555', zorder=2)
    ax.set_extent(extent, crs=ccrs.PlateCarree())
    gl = ax.gridlines(draw_labels=True, linewidth=0.3, color='#DADADA', alpha=0.5, linestyle='--', zorder=3)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 8}
    gl.ylabel_style = {'size': 8}

def compute_spatial_stats(arr):
    """Compute standard summary metrics over valid spatial pixels."""
    valid = arr[~np.isnan(arr)]
    if len(valid) == 0:
        return {'mean': np.nan, 'median': np.nan, 'std': np.nan, 'q25': np.nan, 'q75': np.nan}
    return {
        'mean': float(np.mean(valid)),
        'median': float(np.median(valid)),
        'std': float(np.std(valid)),
        'q25': float(np.percentile(valid, 25)),
        'q75': float(np.percentile(valid, 75))
    }

def run_gleam_validation_cached(cache_dir, out_dir, table_dir):
    """
    High-performance validation using pre-aligned 2016-2020 GLEAM and Noah-MP caches.
    """
    logger.info(f"Loading cached GLEAM ET products from {cache_dir}...")
    
    # 1. Load Reference and Model NetCDFs
    ref_files = sorted(glob.glob(os.path.join(cache_dir, "reference", "gleam_et_*.nc")))
    opl_files = sorted(glob.glob(os.path.join(cache_dir, "model_et", "opl", "et_on_gleam_*.nc")))
    nocdf_files = sorted(glob.glob(os.path.join(cache_dir, "model_et", "da_nocdf", "et_on_gleam_*.nc")))
    cdf_files = sorted(glob.glob(os.path.join(cache_dir, "model_et", "da_cdf", "et_on_gleam_*.nc")))
    mask_file = os.path.join(cache_dir, "reference", "final_common_mask.npy")
    
    if not (ref_files and opl_files and nocdf_files and cdf_files and os.path.exists(mask_file)):
        raise FileNotFoundError(f"Missing required cache files in {cache_dir}")
        
    ds_ref = xr.open_mfdataset(ref_files)
    ds_opl = xr.open_mfdataset(opl_files)
    ds_nocdf = xr.open_mfdataset(nocdf_files)
    ds_cdf = xr.open_mfdataset(cdf_files)
    
    final_common_mask = np.load(mask_file) # (1827, 62, 92)
    spatial_mask_2d = final_common_mask.all(axis=0) # (62, 92), 4110 valid pixels
    
    lats = ds_ref['lat'].values
    lons = ds_ref['lon'].values
    times = pd.to_datetime(ds_ref['time'].values)
    n_days = len(times)
    
    logger.info(f"Loaded {n_days} daily steps (from {times[0].strftime('%Y-%m-%d')} to {times[-1].strftime('%Y-%m-%d')}).")
    logger.info(f"Spatial grid: {len(lats)} lats x {len(lons)} lons. Valid pixels: {int(spatial_mask_2d.sum())}.")
    
    # Extract 3D arrays and mask non-valid pixels
    ref_3d = np.where(final_common_mask, ds_ref['et_reference'].values, np.nan) # (1827, 62, 92)
    opl_3d = np.where(final_common_mask, ds_opl['et'].values, np.nan)
    nocdf_3d = np.where(final_common_mask, ds_nocdf['et'].values, np.nan)
    cdf_3d = np.where(final_common_mask, ds_cdf['et'].values, np.nan)
    
    datasets_3d = {
        'OPL': opl_3d,
        'DA_NoCDF': nocdf_3d,
        'DA_CDF': cdf_3d
    }
    
    exp_display_names = {
        'OPL': 'Open-Loop (OL)',
        'DA_NoCDF': 'SMAP DA (No-CDF)',
        'DA_CDF': 'SMAP DA (CDF v2)'
    }
    
    # 2. Daily Metrics Calculation (2D maps)
    logger.info("Computing daily pixel-by-pixel metrics...")
    
    # Multi-year monthly climatology for daily anomaly correlation
    months = times.month
    ref_clim = np.full((12, len(lats), len(lons)), np.nan)
    datasets_clim = {k: np.full((12, len(lats), len(lons)), np.nan) for k in datasets_3d}
    for m in range(1, 13):
        m_idx = (months == m)
        ref_clim[m-1] = np.nanmean(ref_3d[m_idx], axis=0)
        for k in datasets_3d:
            datasets_clim[k][m-1] = np.nanmean(datasets_3d[k][m_idx], axis=0)
            
    ref_anom_3d = np.full_like(ref_3d, np.nan)
    datasets_anom_3d = {k: np.full_like(v, np.nan) for k, v in datasets_3d.items()}
    for m in range(1, 13):
        m_idx = (months == m)
        ref_anom_3d[m_idx] = ref_3d[m_idx] - ref_clim[m-1]
        for k in datasets_3d:
            datasets_anom_3d[k][m_idx] = datasets_3d[k][m_idx] - datasets_clim[k][m-1]

    metrics_daily = {}
    for exp_id, mod_3d in datasets_3d.items():
        bias_map = np.nanmean(mod_3d - ref_3d, axis=0)
        rmse_map = np.sqrt(np.nanmean((mod_3d - ref_3d)**2, axis=0))
        
        # Pearson R
        mod_anom_t = mod_3d - np.nanmean(mod_3d, axis=0)
        ref_anom_t = ref_3d - np.nanmean(ref_3d, axis=0)
        cov = np.nanmean(mod_anom_t * ref_anom_t, axis=0)
        std_mod = np.nanstd(mod_3d, axis=0)
        std_ref = np.nanstd(ref_3d, axis=0)
        r_map = np.where((std_mod * std_ref) > 0, cov / (std_mod * std_ref), np.nan)
        
        # Anomaly R
        cov_a = np.nanmean(datasets_anom_3d[exp_id] * ref_anom_3d, axis=0)
        std_mod_a = np.nanstd(datasets_anom_3d[exp_id], axis=0)
        std_ref_a = np.nanstd(ref_anom_3d, axis=0)
        r_anom_map = np.where((std_mod_a * std_ref_a) > 0, cov_a / (std_mod_a * std_ref_a), np.nan)
        
        metrics_daily[exp_id] = {
            'Bias': bias_map,
            'RMSE': rmse_map,
            'R': r_map,
            'Anomaly_R': r_anom_map
        }

    # 3. Monthly Resampling & Metrics (60 monthly steps)
    logger.info("Computing monthly metrics (60 months)...")
    ds_ref_m = ds_ref['et_reference'].resample(time='1MS').mean().compute()
    ds_opl_m = ds_opl['et'].resample(time='1MS').mean().compute()
    ds_nocdf_m = ds_nocdf['et'].resample(time='1MS').mean().compute()
    ds_cdf_m = ds_cdf['et'].resample(time='1MS').mean().compute()
    
    ref_m_3d = np.where(spatial_mask_2d, ds_ref_m.values, np.nan)
    opl_m_3d = np.where(spatial_mask_2d, ds_opl_m.values, np.nan)
    nocdf_m_3d = np.where(spatial_mask_2d, ds_nocdf_m.values, np.nan)
    cdf_m_3d = np.where(spatial_mask_2d, ds_cdf_m.values, np.nan)
    
    datasets_m_3d = {'OPL': opl_m_3d, 'DA_NoCDF': nocdf_m_3d, 'DA_CDF': cdf_m_3d}
    times_m = pd.to_datetime(ds_ref_m['time'].values)
    months_m = times_m.month
    n_months = len(times_m)
    
    metrics_monthly = {}
    for exp_id, mod_m in datasets_m_3d.items():
        bias_m = np.nanmean(mod_m - ref_m_3d, axis=0)
        rmse_m = np.sqrt(np.nanmean((mod_m - ref_m_3d)**2, axis=0))
        
        cov_m = np.nanmean((mod_m - np.nanmean(mod_m, axis=0)) * (ref_m_3d - np.nanmean(ref_m_3d, axis=0)), axis=0)
        std_mod_m = np.nanstd(mod_m, axis=0)
        std_ref_m = np.nanstd(ref_m_3d, axis=0)
        r_m = np.where((std_mod_m * std_ref_m) > 0, cov_m / (std_mod_m * std_ref_m), np.nan)
        
        # Monthly Anomaly R
        m_anom_m = np.zeros_like(mod_m)
        r_anom_m = np.zeros_like(ref_m_3d)
        for mo in range(1, 13):
            mo_idx = (months_m == mo)
            m_anom_m[mo_idx] = mod_m[mo_idx] - np.nanmean(mod_m[mo_idx], axis=0)
            r_anom_m[mo_idx] = ref_m_3d[mo_idx] - np.nanmean(ref_m_3d[mo_idx], axis=0)
        cov_am = np.nanmean(m_anom_m * r_anom_m, axis=0)
        std_mam = np.nanstd(m_anom_m, axis=0)
        std_ram = np.nanstd(r_anom_m, axis=0)
        r_anom_m = np.where((std_mam * std_ram) > 0, cov_am / (std_mam * std_ram), np.nan)
        
        metrics_monthly[exp_id] = {
            'Bias': bias_m,
            'RMSE': rmse_m,
            'R': r_m,
            'Anomaly_R': r_anom_m
        }

    # 4. Seasonal Metrics (Wet: Nov-Apr, Dry: May-Oct)
    logger.info("Computing seasonal metrics (Wet vs Dry)...")
    wet_idx = np.isin(months, [11, 12, 1, 2, 3, 4])
    dry_idx = np.isin(months, [5, 6, 7, 8, 9, 10])
    
    seasons = {
        'Wet (Nov-Apr)': wet_idx,
        'Dry (May-Oct)': dry_idx,
        'DJF': np.isin(months, [12, 1, 2]),
        'JJA': np.isin(months, [6, 7, 8])
    }
    
    metrics_seasonal = {}
    for s_name, s_idx in seasons.items():
        metrics_seasonal[s_name] = {}
        ref_s = ref_3d[s_idx]
        for exp_id, mod_3d in datasets_3d.items():
            mod_s = mod_3d[s_idx]
            bias_s = np.nanmean(mod_s - ref_s, axis=0)
            rmse_s = np.sqrt(np.nanmean((mod_s - ref_s)**2, axis=0))
            cov_s = np.nanmean((mod_s - np.nanmean(mod_s, axis=0)) * (ref_s - np.nanmean(ref_s, axis=0)), axis=0)
            std_mod_s = np.nanstd(mod_s, axis=0)
            std_ref_s = np.nanstd(ref_s, axis=0)
            r_s = np.where((std_mod_s * std_ref_s) > 0, cov_s / (std_mod_s * std_ref_s), np.nan)
            
            metrics_seasonal[s_name][exp_id] = {
                'Bias': bias_s,
                'RMSE': rmse_s,
                'R': r_s
            }

    # 5. Build Synthetic CSV Metrics Table
    logger.info("Generating synthetic metrics CSV table...")
    csv_rows = []
    
    def add_table_rows(scale_name, season_name, dict_data):
        for m_key in ['R', 'Anomaly_R', 'RMSE', 'Bias']:
            if m_key not in dict_data['OPL']: continue
            opl_s = compute_spatial_stats(dict_data['OPL'][m_key])
            nocdf_s = compute_spatial_stats(dict_data['DA_NoCDF'][m_key])
            cdf_s = compute_spatial_stats(dict_data['DA_CDF'][m_key])
            
            # Differences vs OPL
            delta_nocdf = nocdf_s['median'] - opl_s['median']
            delta_cdf = cdf_s['median'] - opl_s['median']
            
            # Relative gain (%)
            rel_nocdf = (delta_nocdf / abs(opl_s['median'])) * 100.0 if opl_s['median'] != 0 else np.nan
            rel_cdf = (delta_cdf / abs(opl_s['median'])) * 100.0 if opl_s['median'] != 0 else np.nan
            
            csv_rows.append({
                'Temporal_Scale': scale_name,
                'Season': season_name,
                'Metric': m_key,
                'OL_Mean': opl_s['mean'],
                'OL_Median': opl_s['median'],
                'OL_Std': opl_s['std'],
                'DA_NoCDF_Mean': nocdf_s['mean'],
                'DA_NoCDF_Median': nocdf_s['median'],
                'DA_NoCDF_Std': nocdf_s['std'],
                'DA_CDF_Mean': cdf_s['mean'],
                'DA_CDF_Median': cdf_s['median'],
                'DA_CDF_Std': cdf_s['std'],
                'Delta_DA_NoCDF_vs_OL_Median': delta_nocdf,
                'Delta_DA_CDF_vs_OL_Median': delta_cdf,
                'Relative_Change_DA_NoCDF_pct': rel_nocdf,
                'Relative_Change_DA_CDF_pct': rel_cdf
            })

    add_table_rows('Daily (1827 days)', 'All-Year (2016-2020)', metrics_daily)
    add_table_rows('Monthly (60 months)', 'All-Year (2016-2020)', metrics_monthly)
    for s_name in ['Wet (Nov-Apr)', 'Dry (May-Oct)', 'DJF', 'JJA']:
        add_table_rows('Daily', s_name, metrics_seasonal[s_name])
        
    df_metrics = pd.DataFrame(csv_rows)
    os.makedirs(table_dir, exist_ok=True)
    table_path = os.path.join(table_dir, "et_validation_gleam_metrics.csv")
    df_metrics.to_csv(table_path, index=False)
    logger.info(f"Saved synthetic metrics table to {table_path}")

    # Also save a 2D NetCDF Skill Map
    skill_ds = xr.Dataset(
        data_vars={
            'R': (('exp', 'lat', 'lon'), [metrics_daily[k]['R'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
            'Anomaly_R': (('exp', 'lat', 'lon'), [metrics_daily[k]['Anomaly_R'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
            'RMSE': (('exp', 'lat', 'lon'), [metrics_daily[k]['RMSE'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
            'Bias': (('exp', 'lat', 'lon'), [metrics_daily[k]['Bias'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
            'R_monthly': (('exp', 'lat', 'lon'), [metrics_monthly[k]['R'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
            'Anomaly_R_monthly': (('exp', 'lat', 'lon'), [metrics_monthly[k]['Anomaly_R'] for k in ['OPL', 'DA_NoCDF', 'DA_CDF']]),
        },
        coords={
            'exp': ['OPL', 'DA_NoCDF', 'DA_CDF'],
            'lat': lats,
            'lon': lons
        },
        attrs={
            'description': 'Daily and monthly ET validation skill maps vs GLEAM v4.3a (2016-2020)',
            'reference': 'GLEAM v4.3a Actual Evapotranspiration (E)',
            'units': 'mm/day for Bias and RMSE; dimensionless for R'
        }
    )
    skill_nc_path = os.path.join(out_dir, "skill_maps_gleam.nc")
    skill_ds.to_netcdf(skill_nc_path)
    logger.info(f"Saved skill maps NetCDF to {skill_nc_path}")

    # =========================================================================
    # 6. FIGURES PRODUCTION
    # =========================================================================
    os.makedirs(out_dir, exist_ok=True)
    plt.rcParams.update({'font.sans-serif': 'DejaVu Sans', 'font.size': 9})
    
    # -------------------------------------------------------------------------
    # FIGURE A1: Performance Maps - Mean Signed Bias (Shared Colorbar)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure A1: ET Performance Maps (Bias)...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), subplot_kw={'projection': ccrs.PlateCarree()})
    bias_cmap = 'RdBu_r'
    bias_vmin, bias_vmax = -0.6, 0.6
    
    for ax, exp_id in zip(axes, ['OPL', 'DA_NoCDF', 'DA_CDF']):
        format_geo_map(ax)
        bias_arr = metrics_daily[exp_id]['Bias']
        im = ax.pcolormesh(lons, lats, bias_arr, cmap=bias_cmap, vmin=bias_vmin, vmax=bias_vmax,
                           shading='auto', transform=ccrs.PlateCarree())
        med_val = np.nanmedian(bias_arr)
        mean_val = np.nanmean(bias_arr)
        ax.set_title(f"{exp_display_names[exp_id]}: Mean: {mean_val:+.3f} | Median: {med_val:+.3f} mm d⁻¹", fontsize=10, weight='bold')
        
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.03])
    cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both')
    cb.set_label("Mean Signed ET Bias vs GLEAM v4.3a [mm day⁻¹]", fontsize=10)
    fig.suptitle("Daily Evapotranspiration Bias (2016–2020)", fontsize=13, weight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.18, top=0.88, wspace=0.15)
    
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_bias.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_bias.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE A2: Performance Maps - Pearson Correlation R (Shared Colorbar)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure A2: ET Performance Maps (Correlation)...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), subplot_kw={'projection': ccrs.PlateCarree()})
    r_cmap = 'YlGnBu'
    r_vmin, r_vmax = 0.1, 0.8
    
    for ax, exp_id in zip(axes, ['OPL', 'DA_NoCDF', 'DA_CDF']):
        format_geo_map(ax)
        r_arr = metrics_daily[exp_id]['R']
        im = ax.pcolormesh(lons, lats, r_arr, cmap=r_cmap, vmin=r_vmin, vmax=r_vmax,
                           shading='auto', transform=ccrs.PlateCarree())
        med_val = np.nanmedian(r_arr)
        mean_val = np.nanmean(r_arr)
        ax.set_title(f"{exp_display_names[exp_id]}: Mean R: {mean_val:.3f} | Median R: {med_val:.3f}", fontsize=10, weight='bold')
        
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.03])
    cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both')
    cb.set_label("Pearson Correlation R vs GLEAM v4.3a [-]", fontsize=10)
    fig.suptitle("Daily Evapotranspiration Pearson Correlation R (2016–2020)", fontsize=13, weight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.18, top=0.88, wspace=0.15)
    
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_correlation.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_correlation.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE A3: Performance Maps - Anomaly Correlation R_anom (Shared Colorbar)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure A3: ET Performance Maps (Anomaly Correlation)...")
    fig, axes = plt.subplots(1, 3, figsize=(15, 5.5), subplot_kw={'projection': ccrs.PlateCarree()})
    
    for ax, exp_id in zip(axes, ['OPL', 'DA_NoCDF', 'DA_CDF']):
        format_geo_map(ax)
        ranom_arr = metrics_daily[exp_id]['Anomaly_R']
        im = ax.pcolormesh(lons, lats, ranom_arr, cmap='viridis', vmin=0.1, vmax=0.7,
                           shading='auto', transform=ccrs.PlateCarree())
        med_val = np.nanmedian(ranom_arr)
        mean_val = np.nanmean(ranom_arr)
        ax.set_title(f"{exp_display_names[exp_id]}: Mean: {mean_val:.3f} | Median: {med_val:.3f}", fontsize=10, weight='bold')
        
    cbar_ax = fig.add_axes([0.25, 0.08, 0.5, 0.03])
    cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both')
    cb.set_label("Anomaly Correlation R_anom vs GLEAM v4.3a [-]", fontsize=10)
    fig.suptitle("Daily ET Anomaly Correlation R_anom (2016–2020, Seasonal Cycle Removed)", fontsize=13, weight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.18, top=0.88, wspace=0.15)
    
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_anomaly_correlation.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_performance_maps_anomaly_correlation.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE A4: Skill Change Maps - Delta R and Delta Anomaly R vs OL (Nie et al.)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure A4: Skill Change Maps (Delta R and Delta Anomaly R)...")
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    nie_cmap, nie_norm = create_nie_colormap()
    
    r_ol = metrics_daily['OPL']['R']
    ranom_ol = metrics_daily['OPL']['Anomaly_R']
    
    plot_items = [
        (0, 0, 'DA_NoCDF', 'R', metrics_daily['DA_NoCDF']['R'] - r_ol, r_ol, "ΔR: DA-NoCDF minus OL"),
        (0, 1, 'DA_CDF', 'R', metrics_daily['DA_CDF']['R'] - r_ol, r_ol, "ΔR: DA-CDF v2 minus OL"),
        (1, 0, 'DA_NoCDF', 'Anomaly_R', metrics_daily['DA_NoCDF']['Anomaly_R'] - ranom_ol, ranom_ol, "ΔR_anom: DA-NoCDF minus OL"),
        (1, 1, 'DA_CDF', 'Anomaly_R', metrics_daily['DA_CDF']['Anomaly_R'] - ranom_ol, ranom_ol, "ΔR_anom: DA-CDF v2 minus OL"),
    ]
    
    for row, col, exp_id, m_key, delta_map, ol_map, title_str in plot_items:
        ax = axes[row, col]
        format_geo_map(ax)
        
        # Land background
        land_bg = np.where(~np.isnan(ol_map), 1, np.nan)
        ax.pcolormesh(lons, lats, land_bg, cmap=ListedColormap(['#F2F2F2']), shading='auto', transform=ccrs.PlateCarree(), zorder=1)
        
        im = ax.pcolormesh(lons, lats, delta_map, cmap=nie_cmap, norm=nie_norm,
                           shading='auto', transform=ccrs.PlateCarree(), zorder=2)
        
        med_delta = np.nanmedian(delta_map)
        mean_delta = np.nanmean(delta_map)
        ax.set_title(f"{title_str}: Median Δ: {med_delta:+.3f} (Mean: {mean_delta:+.3f})", fontsize=9.5, weight='bold')

    cbar_ax = fig.add_axes([0.2, 0.05, 0.6, 0.025])
    cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal')
    cb.set_label("Correlation Difference ΔR vs Open-Loop [-]", fontsize=10)
    fig.suptitle("Daily ET Skill Changes Relative to Open-Loop (2016–2020 vs GLEAM v4.3a)", fontsize=12, weight='bold', y=0.98)
    fig.subplots_adjust(bottom=0.12, top=0.92, hspace=0.25, wspace=0.15)
    
    fig.savefig(os.path.join(out_dir, "ET_skill_maps_delta_R.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_skill_maps_delta_R.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE A5: Skill Change Maps - Delta RMSE & Delta Bias vs OL
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure A5: Skill Change Maps (Delta RMSE & Delta Bias)...")
    fig, axes = plt.subplots(2, 2, figsize=(11, 9), subplot_kw={'projection': ccrs.PlateCarree()})
    
    bias_ol = metrics_daily['OPL']['Bias']
    rmse_ol = metrics_daily['OPL']['RMSE']
    
    # Delta RMSE: Blue = improved (negative diff), Red = degraded (positive diff)
    im_rmse = None
    im_bias = None
    for col, exp_id in enumerate(['DA_NoCDF', 'DA_CDF']):
        # Row 0: Delta RMSE
        ax0 = axes[0, col]
        format_geo_map(ax0)
        delta_rmse = metrics_daily[exp_id]['RMSE'] - rmse_ol
        im_rmse = ax0.pcolormesh(lons, lats, delta_rmse, cmap='RdBu', vmin=-0.1, vmax=0.1,
                                 shading='auto', transform=ccrs.PlateCarree())
        med_dr = np.nanmedian(delta_rmse)
        ax0.set_title(f"ΔRMSE: {exp_display_names[exp_id]} minus OL: Median: {med_dr:+.3f} mm d⁻¹ (blue = improved)", fontsize=9, weight='bold')
        
        # Row 1: Delta Bias
        ax1 = axes[1, col]
        format_geo_map(ax1)
        delta_bias = metrics_daily[exp_id]['Bias'] - bias_ol
        im_bias = ax1.pcolormesh(lons, lats, delta_bias, cmap='RdBu_r', vmin=-0.3, vmax=0.3,
                                 shading='auto', transform=ccrs.PlateCarree())
        med_db = np.nanmedian(delta_bias)
        ax1.set_title(f"ΔBias: {exp_display_names[exp_id]} minus OL: Median: {med_db:+.3f} mm d⁻¹", fontsize=9, weight='bold')

    fig.subplots_adjust(bottom=0.12, top=0.92, hspace=0.25, wspace=0.15)
    cbar_ax0 = fig.add_axes([0.15, 0.05, 0.32, 0.02])
    cb0 = fig.colorbar(im_rmse, cax=cbar_ax0, orientation='horizontal', extend='both')
    cb0.set_label("ΔRMSE [mm day⁻¹] (negative = improved)", fontsize=8)
    
    cbar_ax1 = fig.add_axes([0.55, 0.05, 0.32, 0.02])
    cb1 = fig.colorbar(im_bias, cax=cbar_ax1, orientation='horizontal', extend='both')
    cb1.set_label("ΔBias [mm day⁻¹]", fontsize=8)
    
    fig.suptitle("Daily ET RMSE and Bias Changes Relative to Open-Loop (2016–2020)", fontsize=12, weight='bold', y=0.98)
    fig.savefig(os.path.join(out_dir, "ET_skill_maps_delta_rmse_bias.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_skill_maps_delta_rmse_bias.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE B: Annual Cycle Climatology (12 Months) & Monthly Series (2016-2020)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure B: Annual Cycle Climatology...")
    
    # Area weighting: cos(latitude)
    lat_weights = np.cos(np.deg2rad(lats))
    lat_weights_2d = np.repeat(lat_weights[:, np.newaxis], len(lons), axis=1)
    cell_weights = lat_weights_2d * spatial_mask_2d
    w_sum = cell_weights.sum()
    
    # 1. Compute 12-month multi-year monthly climatology
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_nums = np.arange(1, 13)
    
    clim_stats = {'GLEAM': {'mean': [], 'std': []}, 'OPL': {'mean': [], 'std': []},
                  'DA_NoCDF': {'mean': [], 'std': []}, 'DA_CDF': {'mean': [], 'std': []}}
                  
    for m in range(1, 13):
        # We compute for each year to get interannual standard deviation
        yearly_means = {'GLEAM': [], 'OPL': [], 'DA_NoCDF': [], 'DA_CDF': []}
        for y in range(2016, 2021):
            t_mask = (times.year == y) & (times.month == m)
            if not np.any(t_mask): continue
            
            # Domain-mean ET for this month and year
            r_ym = np.nansum(ref_3d[t_mask] * cell_weights, axis=(1,2)) / w_sum
            yearly_means['GLEAM'].append(np.mean(r_ym))
            
            for k in datasets_3d:
                mod_ym = np.nansum(datasets_3d[k][t_mask] * cell_weights, axis=(1,2)) / w_sum
                yearly_means[k].append(np.mean(mod_ym))
                
        for k in clim_stats:
            clim_stats[k]['mean'].append(np.mean(yearly_means[k]))
            clim_stats[k]['std'].append(np.std(yearly_means[k]))
            
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8.5), gridspec_kw={'height_ratios': [1.2, 1.0]})
    
    # Subplot 1: 12-Month Climatology
    styles = {
        'GLEAM': {'color': '#111111', 'lw': 2.6, 'marker': 'o', 'ms': 6, 'label': 'GLEAM v4.3a (Reference)'},
        'OPL': {'color': '#1f77b4', 'lw': 1.8, 'marker': 's', 'ms': 5, 'label': 'Open-Loop (OL)'},
        'DA_NoCDF': {'color': '#2ca02c', 'lw': 1.8, 'marker': '^', 'ms': 5, 'label': 'SMAP DA without CDF'},
        'DA_CDF': {'color': '#d62728', 'lw': 1.8, 'marker': 'D', 'ms': 5, 'label': 'SMAP DA with CDF v2'}
    }
    
    for k, st in styles.items():
        m_arr = np.array(clim_stats[k]['mean'])
        s_arr = np.array(clim_stats[k]['std'])
        ax1.plot(month_nums, m_arr, color=st['color'], lw=st['lw'], marker=st['marker'],
                 markersize=st['ms'], label=st['label'], zorder=4)
        ax1.fill_between(month_nums, m_arr - s_arr, m_arr + s_arr, color=st['color'], alpha=0.12, zorder=2)
        
    ax1.set_xticks(month_nums)
    ax1.set_xticklabels(month_names, fontsize=10)
    ax1.set_ylabel("Evapotranspiration [mm day⁻¹]", fontsize=11)
    ax1.set_title("(a) Mean Annual ET Climatology (2016–2020) with Interannual Spread (±1σ)", fontsize=11, weight='bold')
    ax1.grid(True, linestyle='--', alpha=0.5)
    ax1.legend(loc='upper right', frameon=True, fontsize=9.5)
    ax1.set_ylim(0, 1.6)
    
    # Subplot 2: Full 5-Year Monthly Time Series (60 months)
    r_monthly_ts = [np.nansum(ref_m_3d[t] * cell_weights) / w_sum for t in range(n_months)]
    opl_monthly_ts = [np.nansum(opl_m_3d[t] * cell_weights) / w_sum for t in range(n_months)]
    nocdf_monthly_ts = [np.nansum(nocdf_m_3d[t] * cell_weights) / w_sum for t in range(n_months)]
    cdf_monthly_ts = [np.nansum(cdf_m_3d[t] * cell_weights) / w_sum for t in range(n_months)]
    
    ax2.plot(times_m, r_monthly_ts, color='#111111', lw=2.2, label='GLEAM v4.3a')
    ax2.plot(times_m, opl_monthly_ts, color='#1f77b4', lw=1.5, label='OL')
    ax2.plot(times_m, nocdf_monthly_ts, color='#2ca02c', lw=1.5, label='DA-NoCDF')
    ax2.plot(times_m, cdf_monthly_ts, color='#d62728', lw=1.5, label='DA-CDF v2')
    
    ax2.set_ylabel("Monthly ET [mm day⁻¹]", fontsize=11)
    ax2.set_title("(b) Domain-Averaged Monthly ET Time Series (2016–2020)", fontsize=11, weight='bold')
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(loc='upper right', frameon=True, fontsize=9.5)
    ax2.set_ylim(0, 1.8)
    
    fig.suptitle("Evapotranspiration Annual Cycle & Chronological Dynamics vs GLEAM", fontsize=13, weight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    
    fig.savefig(os.path.join(out_dir, "ET_annual_cycle_climatology.png"), dpi=300)
    fig.savefig(os.path.join(out_dir, "ET_annual_cycle_climatology.pdf"))
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE C1: Seasonal Evaluation - Wet vs Dry Skill Comparison
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure C1: Seasonal Evaluation (Wet vs Dry)...")
    fig, axes = plt.subplots(2, 2, figsize=(11, 8.5))
    
    metrics_to_plot = [
        ('R', 'Pearson Correlation R [-]', axes[0, 0], '(a)'),
        ('RMSE', 'RMSE [mm day⁻¹]', axes[0, 1], '(b)'),
        ('Bias', 'Mean Signed Bias [mm day⁻¹]', axes[1, 0], '(c)'),
    ]
    
    exp_colors = {'OPL': '#1f77b4', 'DA_NoCDF': '#2ca02c', 'DA_CDF': '#d62728'}
    
    for m_key, y_label, ax, panel_tag in metrics_to_plot:
        # Group data for Wet (Nov-Apr) and Dry (May-Oct)
        data_wet = [metrics_seasonal['Wet (Nov-Apr)'][exp][m_key][spatial_mask_2d] for exp in ['OPL', 'DA_NoCDF', 'DA_CDF']]
        data_dry = [metrics_seasonal['Dry (May-Oct)'][exp][m_key][spatial_mask_2d] for exp in ['OPL', 'DA_NoCDF', 'DA_CDF']]
        
        pos_wet = [1, 2, 3]
        pos_dry = [5, 6, 7]
        
        bp_w = ax.boxplot(data_wet, positions=pos_wet, widths=0.6, patch_artist=True, showfliers=False,
                          medianprops=dict(color='black', lw=1.5))
        bp_d = ax.boxplot(data_dry, positions=pos_dry, widths=0.6, patch_artist=True, showfliers=False,
                          medianprops=dict(color='black', lw=1.5))
                          
        for bp in [bp_w, bp_d]:
            for patch, exp in zip(bp['boxes'], ['OPL', 'DA_NoCDF', 'DA_CDF']):
                patch.set_facecolor(exp_colors[exp])
                patch.set_alpha(0.7)
                
        ax.set_xticks([2, 6])
        ax.set_xticklabels(['Wet Season (Nov–Apr)', 'Dry Season (May–Oct)'], fontsize=10, weight='bold')
        ax.set_ylabel(y_label, fontsize=10)
        ax.set_title(f"{panel_tag} {m_key} Distribution Across Domain", fontsize=10.5, weight='bold')
        ax.grid(True, linestyle='--', alpha=0.5)
        if m_key == 'Bias':
            ax.axhline(0, color='gray', linestyle=':', lw=1)

    # Panel 4: Gain/Loss vs OL summary bar chart
    ax_bar = axes[1, 1]
    seasons_list = ['Wet (Nov-Apr)', 'Dry (May-Oct)']
    x = np.arange(len(seasons_list))
    w = 0.35
    
    # Delta R
    dr_nocdf = [np.nanmedian(metrics_seasonal[s]['DA_NoCDF']['R'] - metrics_seasonal[s]['OPL']['R']) for s in seasons_list]
    dr_cdf = [np.nanmedian(metrics_seasonal[s]['DA_CDF']['R'] - metrics_seasonal[s]['OPL']['R']) for s in seasons_list]
    
    b1 = ax_bar.bar(x - w/2, dr_nocdf, width=w, color='#2ca02c', alpha=0.8, label='DA-NoCDF vs OL')
    b2 = ax_bar.bar(x + w/2, dr_cdf, width=w, color='#d62728', alpha=0.8, label='DA-CDF v2 vs OL')
    
    ax_bar.axhline(0, color='black', lw=0.8)
    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels(['Wet Season (Nov–Apr)', 'Dry Season (May–Oct)'], fontsize=10, weight='bold')
    ax_bar.set_ylabel("Median Skill Difference ΔR [-]", fontsize=10)
    ax_bar.set_title("(d) Correlation Gain/Loss vs OL (ΔR)", fontsize=10.5, weight='bold')
    ax_bar.grid(True, linestyle='--', alpha=0.5)
    ax_bar.legend(loc='best', fontsize=9)
    
    # Legend for boxplots on top
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='#1f77b4', alpha=0.7, label='Open-Loop (OL)'),
        Patch(facecolor='#2ca02c', alpha=0.7, label='SMAP DA without CDF'),
        Patch(facecolor='#d62728', alpha=0.7, label='SMAP DA with CDF v2')
    ]
    axes[0, 0].legend(handles=legend_elements, loc='upper left', fontsize=8.5)
    
    fig.suptitle("Seasonal Evaluation of Evapotranspiration Skill vs GLEAM v4.3a", fontsize=12.5, weight='bold', y=0.98)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    
    fig.savefig(os.path.join(out_dir, "ET_seasonal_evaluation_wet_dry.png"), dpi=300)
    fig.savefig(os.path.join(out_dir, "ET_seasonal_evaluation_wet_dry.pdf"))
    plt.close(fig)

    # -------------------------------------------------------------------------
    # FIGURE C2: Seasonal Bias Maps (2 rows x 3 cols)
    # -------------------------------------------------------------------------
    logger.info("Plotting Figure C2: Seasonal Bias Maps...")
    fig, axes = plt.subplots(2, 3, figsize=(15, 9.5), subplot_kw={'projection': ccrs.PlateCarree()})
    
    for row_idx, (s_name, s_tag) in enumerate([('Wet (Nov-Apr)', 'Wet Season (Nov–Apr)'), ('Dry (May-Oct)', 'Dry Season (May–Oct)')]):
        for col_idx, exp_id in enumerate(['OPL', 'DA_NoCDF', 'DA_CDF']):
            ax = axes[row_idx, col_idx]
            format_geo_map(ax)
            b_arr = metrics_seasonal[s_name][exp_id]['Bias']
            im = ax.pcolormesh(lons, lats, b_arr, cmap='RdBu_r', vmin=-0.8, vmax=0.8,
                               shading='auto', transform=ccrs.PlateCarree())
            med_val = np.nanmedian(b_arr)
            mean_val = np.nanmean(b_arr)
            ax.set_title(f"{s_tag} — {exp_display_names[exp_id]}: Mean: {mean_val:+.3f} | Median: {med_val:+.3f} mm d⁻¹", fontsize=9, weight='bold')

    fig.subplots_adjust(bottom=0.1, top=0.92, hspace=0.2, wspace=0.12)
    cbar_ax = fig.add_axes([0.25, 0.04, 0.5, 0.025])
    cb = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='both')
    cb.set_label("Mean Signed ET Bias vs GLEAM v4.3a [mm day⁻¹]", fontsize=10)
    fig.suptitle("Seasonal Evapotranspiration Bias Maps: Wet vs Dry Season (2016–2020)", fontsize=13, weight='bold', y=0.97)
    
    fig.savefig(os.path.join(out_dir, "ET_seasonal_maps_bias.png"), dpi=300, bbox_inches='tight')
    fig.savefig(os.path.join(out_dir, "ET_seasonal_maps_bias.pdf"), bbox_inches='tight')
    plt.close(fig)

    # -------------------------------------------------------------------------
    # Legacy outputs for backward pipeline compatibility: ET_mean_maps_corrected
    # -------------------------------------------------------------------------
    mean_obs_2d = np.nanmean(ref_3d, axis=0)
    panels = {'GLEAM ET': xr.DataArray(mean_obs_2d, coords={'lat': lats, 'lon': lons}, dims=['lat', 'lon'])}
    for exp_id in ['OPL', 'DA_NoCDF', 'DA_CDF']:
        m_2d = np.nanmean(datasets_3d[exp_id], axis=0)
        panels[exp_display_names[exp_id]] = xr.DataArray(m_2d, coords={'lat': lats, 'lon': lons}, dims=['lat', 'lon'])
        
    Plotting.setup_style()
    Plotting.plot_map_panels(
        panels,
        "Mean Evapotranspiration over Common Support (2016–2020)",
        os.path.join(out_dir, "ET_mean_maps_corrected"),
        "ET [mm day⁻¹]",
        cmap="YlGnBu",
        divergent=False
    )
    
    df_ts = pd.DataFrame({
        'GLEAM ET': r_monthly_ts,
        'Open loop': opl_monthly_ts,
        'SMAP-DA without CDF': nocdf_monthly_ts,
        'SMAP-DA with CDF': cdf_monthly_ts
    }, index=times_m)
    Plotting.plot_time_series(
        df_ts,
        "Domain-Mean Monthly Evapotranspiration: GLEAM and Noah-MP Experiments (2016–2020)",
        "ET [mm day⁻¹]",
        os.path.join(out_dir, "ET_timeseries_corrected")
    )

    logger.info("GLEAM validation completed successfully!")
    return {
        'status': 'SUCCESS',
        'metrics_table': table_path,
        'skill_nc': skill_nc_path,
        'figures_dir': out_dir
    }

def run_validation(config, experiments, base_out_dir):
    """Entry point called by postproc adapter."""
    out_dir = os.path.join(base_out_dir, "evapotranspiration")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = PROJECT_ROOT
    registry = DatasetRegistry(os.path.join(project_root, "scripts/postproc/configs/observations"))
    
    table_dir = os.path.join(PROJECT_ROOT, "scripts/postproc/outputs/matrix_2016_2020/tables/smap_cdf_sensitivity_2016_2020/independent_obs_validation")
    
    for name, cfg in registry.get_ready_datasets().items():
        if cfg.get("validation_category") == "evapotranspiration":
            sub_dir = os.path.join(out_dir, name)
            os.makedirs(sub_dir, exist_ok=True)
            
            # SÉPARATION STRICTE DES RÉFÉRENCES D'OBSERVATION (Correction Étape 5)
            # Le cache GLEAM pré-aligné ne doit être mobilisé EXCLUSIVEMENT que pour la référence GLEAM.
            # Ne jamais utiliser ce cache pour WaPOR ou d'autres produits d'observation.
            is_gleam = (
                "gleam" in name.lower() or 
                "gleam" in cfg.get("dataset_id", "").lower() or 
                "gleam" in cfg.get("display_name", "").lower()
            )
            
            if is_gleam:
                if os.path.exists(DEFAULT_CACHE_DIR):
                    try:
                        logger.info(f"[GLEAM] Utilisation exclusive du cache pré-aligné pour {name} ({cfg.get('display_name')})")
                        run_gleam_validation_cached(DEFAULT_CACHE_DIR, sub_dir, table_dir)
                        continue
                    except Exception as e:
                        logger.warning(f"Cached GLEAM validation failed, falling back to LISLoader: {e}")
                try:
                    _run_single_validation(cfg, experiments, sub_dir)
                except Exception as e:
                    logger.error(f"ET Validation failed for {name}: {e}")
            else:
                logger.info(f"[NON-GLEAM] Référence '{name}' ({cfg.get('display_name')}) détectée: contournement strict du cache GLEAM.")
                # Préservation du flux existant sans contamination par les caches GLEAM
                try:
                    _run_single_validation(cfg, experiments, sub_dir)
                except Exception as e:
                    logger.error(f"ET Validation failed for {name}: {e}")

def _run_single_validation(cfg, experiments, out_dir):
    """Legacy single validation path (fallback if cache is not present)."""
    logger.info(f"Running fallback ET validation for {cfg['display_name']}")
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_var = cfg["variables"]["lis"]
    
    from src.core.config import get_experiments_catalog
    catalog = get_experiments_catalog()
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        exp_info = catalog.get(exp_name, {})
        full_exp_path = exp_info.get("path_abs")
        if not full_exp_path: continue
        try:
            ds = LISLoader.load_variable(full_exp_path, "Evap_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS ET for {exp_name}: {e}")
            
    if not lis_datasets: return
    
    for exp_name, ds in lis_datasets.items():
        if float(ds["Evap_tavg"].mean().compute()) < 1.0:
            ds["Evap_tavg"] = ds["Evap_tavg"] * 86400
            ds["Evap_tavg"].attrs['units'] = 'mm day-1'
            
    freq = cfg["temporal"].get("target_frequency", "M")
    obs_ds = SpatialAlignment.normalize_longitudes(obs_ds)
    obs_ds = SpatialAlignment.sort_spatial_coordinates(obs_ds)
    lis_bounds = SpatialAlignment.get_grid_bounds(list(lis_datasets.values())[0])
    obs_subset, _ = SpatialAlignment.subset_observation_to_domain(obs_ds, lis_bounds)
    
    aligned_lis_datasets = {}
    for exp_name, ds in lis_datasets.items():
        ds = SpatialAlignment.normalize_longitudes(ds)
        ds = SpatialAlignment.sort_spatial_coordinates(ds)
        aligned_ds = SpatialAlignment.aggregate_lis_to_observation_grid(ds, obs_subset, min_coverage=0.5)
        aligned_lis_datasets[exp_name] = aligned_ds
        
    temporally_aligned_lis = {}
    for exp_name, ds in aligned_lis_datasets.items():
        lis_aligned, obs_aligned = TemporalAlignment.align(ds, obs_subset, freq, "mean")
        temporally_aligned_lis[exp_name] = lis_aligned
        temporally_aligned_obs = obs_aligned
        
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["Evap_tavg"].notnull()
        
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    mean_obs = masked_obs[obs_var].mean(dim='time')
    panels = {'GLEAM ET': mean_obs}
    for exp_name, ds in masked_lis.items():
        panels[exp_name] = ds["Evap_tavg"].mean(dim='time')
        
    Plotting.setup_style()
    Plotting.plot_map_panels(
        panels,
        "Mean Evapotranspiration over Common Dates",
        os.path.join(out_dir, "ET_mean_maps_corrected"),
        "ET [mm day⁻¹]",
        cmap="YlGnBu",
        divergent=False
    )

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    logger.info("Executing standalone GLEAM ET validation...")
    
    fig_dir = os.path.join(PROJECT_ROOT, "scripts/postproc/outputs/matrix_2016_2020/figures/smap_cdf_sensitivity_2016_2020/independent_obs_validation/evapotranspiration/gleam")
    tab_dir = os.path.join(PROJECT_ROOT, "scripts/postproc/outputs/matrix_2016_2020/tables/smap_cdf_sensitivity_2016_2020/independent_obs_validation")
    
    res = run_gleam_validation_cached(DEFAULT_CACHE_DIR, fig_dir, tab_dir)
    logger.info(f"Execution finished with result: {res}")
