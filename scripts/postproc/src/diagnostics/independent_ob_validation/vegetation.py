# Author: M. El Aabaribaoune (@um6p)
import os
import sys
import logging
import xarray as xr
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import cartopy.crs as ccrs
import seaborn as sns
import cartopy.feature as cfeature
from scipy import stats
import matplotlib.dates as mdates

from .observation_loader import ObservationLoader
from .lis_loader import LISLoader
from .temporal_alignment import TemporalAlignment
from .spatial_alignment import SpatialAlignment
from .dataset_registry import DatasetRegistry
from .plotting import Plotting

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "vegetation")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    registry = DatasetRegistry(os.path.join(project_root, "scripts/postproc/configs/observations"))
    
    for name, cfg in registry.get_ready_datasets().items():
        if cfg.get("validation_category") == "vegetation":
            sub_dir = os.path.join(out_dir, name)
            os.makedirs(sub_dir, exist_ok=True)
            try:
                _run_single_validation(cfg, experiments, sub_dir)
            except Exception as e:
                logger.error(f"Vegetation Validation failed for {name}: {e}")
                import traceback
                traceback.print_exc()

def _run_single_validation(cfg, experiments, out_dir):
    logger.info(f"Running Vegetation validation for {cfg['display_name']}")
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_var = cfg["variables"]["lis"]
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_matrix_dir = os.path.join(project_root, "experiments/NorthMor/matrix_2016")
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        try:
            ds = LISLoader.load_variable(os.path.join(base_matrix_dir, exp_path), "GPP_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS Veg for {exp_name}: {e}")
            
    if not lis_datasets: return
    
    freq = cfg["temporal"].get("target_frequency", "daily")
    
    # 1. DIAGNOSTICS & UNIT CONVERSIONS BEFORE AGGREGATION
    diag_file = open(os.path.join(out_dir, "diagnostic_summary.txt"), "w")
    diag_file.write("Dataset | Original units | Time step | Conversion | Final units | Min | Median | Mean | P95 | Max | NaNs\n")
    
    def log_stats(name, da, orig_units, conv_factor, final_units):
        n_nan = da.isnull().sum().compute().item()
        vmean = da.mean().compute().item()
        
        if np.isnan(vmean):
            diag_file.write(f"{name} | {orig_units} | N/A | {conv_factor} | {final_units} | ALL NaN\n")
            raise ValueError(f"All pixels in {name} are NaN!")
            
        vmin = da.min().compute().item()
        vmax = da.max().compute().item()
        diag_file.write(f"{name} | {orig_units} | N/A | {conv_factor} | {final_units} | {vmin:.4f} | N/A | {vmean:.4f} | N/A | {vmax:.4f} | {n_nan}\n")
        logger.info(f"{name} stats -> Mean: {vmean:.4e}, Max: {vmax:.4e}, NaNs: {n_nan}")
        
        if vmean < 1e-3 and 'fluxsat' not in name.lower():
            raise ValueError(f"{name} values remain suspiciously low ({vmean:.4e}). Unit conversion failed?")
        
        # Check zeros approximately
        zero_fraction = (da == 0).sum().compute().item() / (da.size - n_nan)
        if zero_fraction > 0.95:
            raise ValueError(f"More than 95% of valid pixels in {name} are zero!")
            
    # Process OBS
    obs_units = obs_ds[obs_var].attrs.get('units', 'unknown')
    if 'gCm' in obs_units.replace(' ', '') or 'gC' in obs_units:
        obs_conv = 1.0
        final_obs_units = "g C m-2 day-1"
    else:
        obs_conv = 1.0
        final_obs_units = obs_units
        logger.warning(f"OBS units unrecognized: {obs_units}")
        
    log_stats("FLUXSAT", obs_ds[obs_var], obs_units, obs_conv, final_obs_units)
    
    # Process LIS
    for exp_name, ds in lis_datasets.items():
        lis_units = ds["GPP_tavg"].attrs.get('units', 'unknown')
        if 's-1' in lis_units:
            lis_conv = 86400.0
            final_lis_units = "g C m-2 day-1"
        else:
            lis_conv = 1.0
            final_lis_units = lis_units
            logger.warning(f"LIS units unrecognized: {lis_units}")
            
        # Apply conversion immediately
        ds["GPP_tavg"] = ds["GPP_tavg"] * lis_conv
        ds["GPP_tavg"].attrs['units'] = final_lis_units
        log_stats(exp_name, ds["GPP_tavg"], lis_units, lis_conv, final_lis_units)
        
    diag_file.close()
    
    # 2. HARMONIZATION (Spatial and Temporal)
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
    temporally_aligned_obs = None
    for exp_name, ds in aligned_lis_datasets.items():
        lis_aligned, obs_aligned = TemporalAlignment.align(ds, obs_subset, freq, "mean")
        temporally_aligned_lis[exp_name] = lis_aligned
        if temporally_aligned_obs is None:
            temporally_aligned_obs = obs_aligned
            
    # 3. COMMON MASK
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["GPP_tavg"].notnull()
        
    # We also require at least some valid vegetation. The notnull() already enforces valid data.
    # We don't apply .mean(dim='time') yet for the mask because we want a 3D mask (time, lat, lon).
    # Wait, the user asked for a common mask for spatial means, meaning pixels that have ANY valid data.
    # Actually, they want to use EXACTLY the same mask for all products.
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    # 4. TEMPORARY DIAGNOSTICS PLOTS
    _plot_temporary_diagnostics(masked_obs, masked_lis, obs_var, valid_mask, out_dir)
    
    # 5. MEAN MAPS (VG-02)
    mean_obs = masked_obs[obs_var].mean(dim='time')
    panels = {'FLUXSAT': mean_obs}
    # Ensure correct names
    name_mapping = {
        'OPL_noirr_2016': 'Open loop',
        'DA_smap_nocdf_noirr_2016': 'SMAP-DA without CDF',
        'DA_smap_cdf_noirr_2016': 'SMAP-DA with CDF'
    }
    
    for exp_name, ds in masked_lis.items():
        display_name = name_mapping.get(exp_name, exp_name)
        panels[display_name] = ds["GPP_tavg"].mean(dim='time')
        
    _plot_gpp_mean_maps(panels, out_dir)
    
    # 6. TIME SERIES (VG-03)
    obs_lat_name = 'lat' if 'lat' in masked_obs.coords else 'latitude'
    weights = np.cos(np.deg2rad(masked_obs[obs_lat_name]))
    weights.name = "weights"
    
    df_data = {'FLUXSAT': masked_obs[obs_var].weighted(weights).mean(dim=['lat', 'lon']).to_series()}
    for exp_name, ds in masked_lis.items():
        display_name = name_mapping.get(exp_name, exp_name)
        df_data[display_name] = ds["GPP_tavg"].weighted(weights).mean(dim=['lat', 'lon']).to_series()
        
    _plot_gpp_time_series(pd.DataFrame(df_data), out_dir)


def _plot_gpp_mean_maps(panels, out_dir):
    Plotting.setup_style()
    fig = plt.figure(figsize=(18, 6.5))
    gs = gridspec.GridSpec(1, 4, wspace=0.1, top=0.85, bottom=0.25)
    
    all_vals = []
    for da in panels.values():
        all_vals.append(da.values.flatten())
    all_vals = np.concatenate(all_vals)
    all_vals = all_vals[~np.isnan(all_vals)]
    
    vmin = 0
    vmax = np.nanpercentile(all_vals, 98)
    vmax = np.ceil(vmax) # Round to readable value
    
    axes = []
    letters = ['(a)', '(b)', '(c)', '(d)']
    
    for i, (panel_title, da) in enumerate(panels.items()):
        ax = fig.add_subplot(gs[i], projection=ccrs.PlateCarree())
        axes.append(ax)
        lon_name = 'lon' if 'lon' in da.coords else 'longitude'
        lat_name = 'lat' if 'lat' in da.coords else 'latitude'
        lon = da[lon_name].values
        lat = da[lat_name].values
        
        im = ax.pcolormesh(lon, lat, da.values, transform=ccrs.PlateCarree(), cmap='YlGn', vmin=vmin, vmax=vmax, shading='auto')
        ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
        ax.add_feature(cfeature.BORDERS, linewidth=0.8, linestyle=':')
        
        valid_mask = da.notnull().compute()
        if valid_mask.any():
            dropped = valid_mask.where(valid_mask, drop=True)
            lat_min, lat_max = np.nanmin(dropped[lat_name].values), np.nanmax(dropped[lat_name].values)
            lon_min, lon_max = np.nanmin(dropped[lon_name].values), np.nanmax(dropped[lon_name].values)
            ax.set_extent([lon_min - 0.5, lon_max + 0.5, lat_min - 0.5, lat_max + 0.5], crs=ccrs.PlateCarree())
            
        gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        gl.top_labels = False
        gl.right_labels = False
        if i > 0: gl.left_labels = False
        
        ax.set_title(f"{letters[i]} {panel_title}", fontsize=13)
        
    fig.suptitle("Mean GPP over Vegetated Areas for Common FLUXSAT–Model Dates", fontsize=16, fontweight='semibold', y=0.95)
    cbar_ax = fig.add_axes([0.3, 0.15, 0.4, 0.03])
    cbar = fig.colorbar(im, cax=cbar_ax, orientation='horizontal', extend='max')
    cbar.set_label("Mean GPP [g C m⁻² day⁻¹]")
    
    Plotting.save_figure(fig, os.path.join(out_dir, "VG-02_Mean_Vegetation_corrected"), {
        "title": "Annual Mean GPP vs FluxSat",
        "caption": "Spatial distribution of annual mean GPP from the independent FluxSat dataset and the Noah-MP experiments.",
        "diagnostic_type": "independent_ob_validation",
        "variable": "GPP",
        "experiment": "OPL_noCDF_CDF"
    })


def _plot_gpp_time_series(df, out_dir):
    Plotting.setup_style()
    fig = plt.figure(figsize=(12, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[2, 1], hspace=0.1)
    ax1 = fig.add_subplot(gs[0])
    ax2 = fig.add_subplot(gs[1], sharex=ax1)
    
    colors = {'FLUXSAT': 'black', 'Open loop': '#1f77b4', 'SMAP-DA without CDF': '#ff7f0e', 'SMAP-DA with CDF': '#2ca02c'}
    styles = {'Open loop': '-', 'SMAP-DA without CDF': '--', 'SMAP-DA with CDF': '-.'}
    
    # Top Panel
    ax1.plot(df.index, df['FLUXSAT'], label='FLUXSAT GPP', color=colors['FLUXSAT'], marker='o', markersize=4, linestyle='none')
    
    for exp in ['Open loop', 'SMAP-DA without CDF', 'SMAP-DA with CDF']:
        if exp in df.columns:
            ax1.plot(df.index, df[exp], label=exp, color=colors[exp], linestyle=styles[exp], linewidth=2)
            
    ax1.set_ylabel("GPP [g C m⁻² day⁻¹]")
    ax1.set_title("Domain-Mean GPP: FLUXSAT and Noah-MP Experiments", fontweight='semibold', fontsize=14)
    ax1.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
    
    ymax = np.ceil(np.nanmax(df.values))
    ax1.set_ylim(0, ymax)
    
    # Statistics
    stats_text = ""
    valid = df.dropna()
    for exp in ['Open loop', 'SMAP-DA without CDF', 'SMAP-DA with CDF']:
        if exp in valid.columns:
            r, _ = stats.pearsonr(valid['FLUXSAT'], valid[exp])
            bias = (valid[exp] - valid['FLUXSAT']).mean()
            rmse = np.sqrt(((valid[exp] - valid['FLUXSAT'])**2).mean())
            stats_text += f"{exp}:\n  Bias={bias:.2f}, RMSE={rmse:.2f}, r={r:.2f}\n"
    stats_text += f"\nN common dates = {len(valid)}"
    ax1.text(1.02, 0.05, stats_text, transform=ax1.transAxes, verticalalignment='bottom', bbox=dict(boxstyle='round', facecolor='white', alpha=0.9), fontsize=10)

    # Bottom Panel
    diff_limits = []
    for exp in ['SMAP-DA without CDF', 'SMAP-DA with CDF']:
        if exp in df.columns:
            diff = df[exp] - df['Open loop']
            ax2.plot(df.index, diff, color=colors[exp], linestyle=styles[exp], linewidth=2, label=f"{exp} − OPL")
            diff_limits.extend([np.nanpercentile(diff, 1), np.nanpercentile(diff, 99)])
            
    ax2.axhline(0, color='gray', linestyle='-', linewidth=1)
    ax2.set_ylabel("GPP difference\n[g C m⁻² day⁻¹]")
    ax2.legend(loc='upper left', bbox_to_anchor=(1.02, 1))
    
    if diff_limits:
        limit = np.max(np.abs(diff_limits))
        if np.isnan(limit) or limit == 0: limit = 0.5
        ax2.set_ylim(-limit, limit)
        
    plt.setp(ax1.get_xticklabels(), visible=False)
    ax2.xaxis.set_major_locator(mdates.MonthLocator())
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    
    Plotting.save_figure(fig, os.path.join(out_dir, "VG-03_Time_Series_corrected"), {
        "title": "Time Series vs FluxSat",
        "caption": "Domain-averaged daily time series of GPP for the model experiments compared to the independent FluxSat observations.",
        "diagnostic_type": "independent_ob_validation",
        "variable": "GPP",
        "experiment": "OPL_noCDF_CDF"
    })


def _plot_temporary_diagnostics(masked_obs, masked_lis, obs_var, valid_mask, out_dir):
    Plotting.setup_style()
    
    # 1. Histograms - ONLY ON TIME MEAN TO SAVE MEMORY
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    axes = axes.flatten()
    
    mean_obs = masked_obs[obs_var].mean(dim='time').compute()
    sns.histplot(mean_obs.values.flatten(), bins=50, ax=axes[0], color='black')
    axes[0].set_title("FLUXSAT Mean Histogram")
    
    i = 1
    for exp, ds in masked_lis.items():
        mean_lis = ds["GPP_tavg"].mean(dim='time').compute()
        sns.histplot(mean_lis.values.flatten(), bins=50, ax=axes[i], color='blue')
        axes[i].set_title(f"{exp} Mean Histogram")
        i += 1
        
    Plotting.save_figure(fig, os.path.join(out_dir, "diag_histograms"))
    
    # 2. Map of valid dates count per pixel
    valid_count = valid_mask.sum(dim='time')
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    lon = valid_count.coords.get('lon', valid_count.coords.get('longitude')).values
    lat = valid_count.coords.get('lat', valid_count.coords.get('latitude')).values
    im = ax.pcolormesh(lon, lat, valid_count.values, transform=ccrs.PlateCarree(), cmap='viridis')
    ax.add_feature(cfeature.COASTLINE)
    fig.colorbar(im, ax=ax, label="Number of common valid dates")
    ax.set_title("Common Valid Dates per Pixel")
    Plotting.save_figure(fig, os.path.join(out_dir, "diag_valid_dates_map"))

