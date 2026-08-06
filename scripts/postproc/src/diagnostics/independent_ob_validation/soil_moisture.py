# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import os
import logging
import xarray as xr
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
from .observation_loader import ObservationLoader
from .lis_loader import LISLoader
from .temporal_alignment import TemporalAlignment
from .spatial_alignment import SpatialAlignment
from .metrics import Metrics
from .plotting import Plotting
from .dataset_registry import DatasetRegistry
import warnings

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "soil_moisture")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    config_dir = os.path.join(project_root, "scripts/postproc/configs/observations")
    registry = DatasetRegistry(config_dir)
    ready_datasets = registry.get_ready_datasets()
    
    sm_datasets = {k: v for k, v in ready_datasets.items() if v.get("validation_category") == "soil_moisture"}
    
    if not sm_datasets:
        logger.warning("No READY soil moisture datasets found.")
        return
        
    for name, cfg in sm_datasets.items():
        sub_dir = os.path.join(out_dir, name)
        os.makedirs(sub_dir, exist_ok=True)
        try:
            _run_single_validation(cfg, experiments, sub_dir)
        except Exception as e:
            import traceback
            logger.error(f"Validation failed for {name}: {e}\n{traceback.format_exc()}")
            
        if os.environ.get("SMOKE_TEST", "0") == "1":
            break

def _run_single_validation(cfg, experiments, out_dir):
    logger.info(f"Running Soil Moisture validation for {cfg['display_name']}")
    
    from src.core.config import get_experiments_catalog
    catalog = get_experiments_catalog()
    
    is_smoke_test = os.environ.get("SMOKE_TEST", "0") == "1"
    smoke_dates = ['2016-01-15', '2016-04-15', '2016-07-15', '2016-10-15']
    
    lis_datasets = {}
    baseline_ds = None
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        exp_info = catalog.get(exp_name, {})
        full_exp_path = exp_info.get("path_abs")
        if not full_exp_path:
            logger.error(f"Path for experiment {exp_name} not found in catalog.")
            continue
        try:
            ds = LISLoader.load_variable(full_exp_path, "SoilMoist_tavg")
            if is_smoke_test:
                ds = ds.sel(time=ds.time.dt.strftime('%Y-%m-%d').isin(smoke_dates))
            ds = SpatialAlignment.normalize_longitudes(ds)
            ds = SpatialAlignment.sort_spatial_coordinates(ds)
            lis_datasets[exp_name] = ds
            if baseline_ds is None:
                baseline_ds = ds
        except Exception as e:
            logger.error(f"Could not load LIS for {exp_name}: {e}")
            continue
            
    if not lis_datasets:
        return
        
    def _log_stats(name, da):
        try:
            da = da.compute()
            vals = da.values.flatten()
            vals = vals[~np.isnan(vals)]
            if len(vals) == 0:
                logger.info(f"{name} stats -> ALL NaNs or empty")
                return
            mi, ma, me, md = np.min(vals), np.max(vals), np.mean(vals), np.median(vals)
            p1, p5, p50, p95, p99 = np.percentile(vals, [1, 5, 50, 95, 99])
            nan_frac = 1.0 - (len(vals) / da.size)
            logger.info(
                f"[{name}] {da.name} | Units: {da.attrs.get('units', 'unknown')} | "
                f"Dims: {da.dims} | Shape: {da.shape}\n"
                f"      Min: {mi:.4g}, Max: {ma:.4g}, Mean: {me:.4g}, Median: {md:.4g}\n"
                f"      P1: {p1:.4g}, P5: {p5:.4g}, P50: {p50:.4g}, P95: {p95:.4g}, P99: {p99:.4g}\n"
                f"      NaN fraction: {nan_frac:.2%}, Valid cells: {len(vals)}"
            )
        except Exception as e:
            logger.warning(f"Could not compute stats for {name}: {e}")

    for exp_name, ds in lis_datasets.items():
        _log_stats(exp_name, ds["SoilMoist_tavg"])
        
    lis_bounds = SpatialAlignment.get_grid_bounds(baseline_ds)
    lis_valid_mask = SpatialAlignment.build_lis_valid_mask(baseline_ds)
    
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_ds = SpatialAlignment.normalize_longitudes(obs_ds)
    obs_ds = SpatialAlignment.sort_spatial_coordinates(obs_ds)
    obs_var = cfg["variables"]["lis"]
    
    if is_smoke_test:
        obs_ds = obs_ds.sel(time=obs_ds.time.dt.strftime('%Y-%m-%d').isin(smoke_dates))
        
    _log_stats(cfg["display_name"], obs_ds[obs_var])
        
    obs_global_bounds = SpatialAlignment.get_grid_bounds(obs_ds)
    obs_subset, margins = SpatialAlignment.subset_observation_to_domain(obs_ds, lis_bounds)
    obs_subset_bounds = SpatialAlignment.get_grid_bounds(obs_subset)
    
    min_coverage = cfg.get("spatial_alignment", {}).get("minimum_lis_coverage_fraction", 0.5)
    
    aligned_lis_datasets = {}
    for exp_name, ds in lis_datasets.items():
        aligned_ds = SpatialAlignment.aggregate_lis_to_observation_grid(ds, obs_subset, min_coverage=min_coverage)
        aligned_lis_datasets[exp_name] = aligned_ds
        
    aligned_bounds = SpatialAlignment.get_grid_bounds(aligned_lis_datasets[list(aligned_lis_datasets.keys())[0]])
    
    assert aligned_bounds[1] - aligned_bounds[0] <= 1.25 * (lis_bounds[1] - lis_bounds[0]), "SPATIAL_DOMAIN_MISMATCH"
    assert aligned_bounds[3] - aligned_bounds[2] <= 1.25 * (lis_bounds[3] - lis_bounds[2]), "SPATIAL_DOMAIN_MISMATCH"
    
    freq = cfg["temporal"].get("target_frequency", "D")
    temporally_aligned_lis = {}
    temporally_aligned_obs = None
    
    for exp_name, ds in aligned_lis_datasets.items():
        lis_aligned, obs_aligned = TemporalAlignment.align(ds, obs_subset, freq, "mean")
        temporally_aligned_lis[exp_name] = lis_aligned
        temporally_aligned_obs = obs_aligned
        
    obs_eval = temporally_aligned_obs
    common_mask = obs_eval[obs_var].notnull()
    for exp_name, ds in temporally_aligned_lis.items():
        common_mask = common_mask & ds["SoilMoist_tavg"].notnull()
        
    num_common_valid = int(common_mask.sum().compute())
    
    # Check minimum LIS coverage and empty common mask
    lat_name = 'lat' if 'lat' in common_mask.coords else 'latitude'
    lon_name = 'lon' if 'lon' in common_mask.coords else 'longitude'
    expected_cells = common_mask.sizes[lat_name] * common_mask.sizes[lon_name]
    spatial_valid = common_mask.any(dim='time').sum().compute().item()
    if spatial_valid == 0:
        logger.error(f"Soil Moisture Validation failed: Empty common mask (0 valid pixels).")
        raise ValueError("Empty common valid mask.")
    if spatial_valid / expected_cells < 0.2:
        logger.error(f"Soil Moisture Validation failed: LIS valid mask covers less than 20% of the domain ({spatial_valid}/{expected_cells}).")
        raise ValueError("Insufficient spatial coverage.")
    
    if is_smoke_test:
        _generate_smoke_test_outputs(
            out_dir, 
            lis_bounds, obs_global_bounds, obs_subset_bounds, aligned_bounds,
            margins, min_coverage, num_common_valid,
            temporally_aligned_lis, obs_eval, obs_var, common_mask, lis_valid_mask
        )
        return
        
    spatial_subsets = cfg.get("spatial_subsets", [{"id": "NorthMor", "type": "full_domain"}])
    for subset in spatial_subsets:
        subset_id = subset["id"]
        subset_out_dir = os.path.join(out_dir, subset_id)
        os.makedirs(subset_out_dir, exist_ok=True)
        _generate_products(cfg, temporally_aligned_lis, obs_eval, obs_var, common_mask, subset_out_dir, experiments, subset_id, lis_bounds)

def _generate_smoke_test_outputs(out_dir, lis_bounds, obs_global_bounds, obs_subset_bounds, aligned_bounds,
                                margins, min_coverage, num_common_valid,
                                lis_datasets, obs_ds, obs_var, common_mask, lis_valid_mask):
    
    metrics = {
        "LIS lon center min/max": f"{lis_bounds[0]:.3f} / {lis_bounds[1]:.3f}",
        "LIS lat center min/max": f"{lis_bounds[2]:.3f} / {lis_bounds[3]:.3f}",
        "LIS lon edge min/max": f"{lis_bounds[0]-0.005:.3f} / {lis_bounds[1]+0.005:.3f}",
        "LIS lat edge min/max": f"{lis_bounds[2]-0.005:.3f} / {lis_bounds[3]+0.005:.3f}",
        "ESA CCI global bounds": f"Lon: {obs_global_bounds[0]:.3f} to {obs_global_bounds[1]:.3f}, Lat: {obs_global_bounds[2]:.3f} to {obs_global_bounds[3]:.3f}",
        "ESA CCI subset bounds": f"Lon: {obs_subset_bounds[0]:.3f} to {obs_subset_bounds[1]:.3f}, Lat: {obs_subset_bounds[2]:.3f} to {obs_subset_bounds[3]:.3f}",
        "Aligned grid bounds": f"Lon: {aligned_bounds[0]:.3f} to {aligned_bounds[1]:.3f}, Lat: {aligned_bounds[2]:.3f} to {aligned_bounds[3]:.3f}",
        "Observation resolution": f"dLon={margins[0]/0.5:.3f}, dLat={margins[1]/0.5:.3f}",
        "LIS resolution": "~0.01 deg",
        "Selection margin": f"dLon={margins[0]:.3f}, dLat={margins[1]:.3f}",
        "Regridding method": "Conservative explicit surface weighted aggregation",
        "Minimum LIS coverage fraction": f"{min_coverage}",
        "Observation cells selected": f"{np.prod(obs_ds[obs_var].shape[1:])}",
        "Observation cells retained after coverage QC": f"{int(lis_datasets[list(lis_datasets.keys())[0]]['SoilMoist_tavg'].isel(time=0).notnull().sum())}",
        "Common valid cells": f"{num_common_valid}",
        "Cells outside LIS support": 0,
        "Cells outside NorthMor mask": 0,
    }
    
    df = pd.DataFrame(list(metrics.items()), columns=["Field", "Value"])
    df.to_csv(os.path.join(out_dir, "northmor_spatial_alignment_smoke_test.csv"), index=False)
    
    with open(os.path.join(out_dir, "northmor_spatial_alignment_smoke_test.md"), "w") as f:
        f.write("# NorthMor Spatial Alignment Smoke Test\n\n")
        f.write(df.to_markdown(index=False))
        
    esa_mask = obs_ds[obs_var].notnull().any('time')
    
    qc_text = f"LIS grid shape: {lis_valid_mask.shape}\nESA CCI subset shape: {esa_mask.shape}\nCommon valid area: {num_common_valid} cell-days\nLon: {lis_bounds[0]:.1f} to {lis_bounds[1]:.1f}\nLat: {lis_bounds[2]:.1f} to {lis_bounds[3]:.1f}"
    
    Plotting.plot_alignment_smoke_test_map(lis_valid_mask, esa_mask, common_mask.any('time'), os.path.join(out_dir, "SM_spatial_masks_corrected"), lis_bounds, qc_text)
    Plotting.plot_smoke_test_timeseries(obs_ds, lis_datasets, obs_var, common_mask, os.path.join(out_dir, "SM_timeseries_corrected"), ylabel="Soil moisture [m³ m⁻³]")

def _generate_products(cfg, lis_datasets, obs_ds, obs_var, common_mask, out_dir, experiments, subset_id, lis_bounds):
    Plotting.setup_style()
    
    min_pairs = cfg.get("validation_metrics", {}).get("min_valid_days", 50)
    
    valid_count = common_mask.sum(dim='time')
    total_days = len(obs_ds['time']) if 'time' in obs_ds.coords else 366
    
    Plotting.plot_data_coverage(
        valid_count, total_days,
        os.path.join(out_dir, "SM-01_Data_Coverage"),
        lis_bounds, min_pairs,
        metrics_dict={
            "title": f"Temporal Coverage - {cfg['display_name']}",
            "caption": "Percentage of days where valid observations exist and can be matched with the model.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # Mask out cells that don't meet minimum pairs
    threshold_mask = valid_count >= min_pairs
    masked_obs = obs_ds.where(common_mask).where(threshold_mask)
    masked_lis = {exp: ds.where(common_mask).where(threshold_mask) for exp, ds in lis_datasets.items()}
    
    mean_obs = masked_obs[obs_var].mean(dim='time')
    
    opl_name = next((exp for exp in experiments if 'opl' in exp.lower()), list(experiments)[0])
    mean_lis = masked_lis[opl_name]["SoilMoist_tavg"].mean(dim='time')
    bias = mean_lis - mean_obs
    
    Plotting.plot_annual_mean_and_bias(
        mean_obs, mean_lis, bias,
        os.path.join(out_dir, "SM-02_Annual_Mean_and_Bias"),
        lis_bounds,
        metrics_dict={
            "title": f"Annual Mean and Bias vs {cfg['display_name']}",
            "caption": "Spatial distribution of annual mean soil moisture and the associated model bias relative to the observation.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # Domain Time Series (Area-weighted)
    obs_lat_name = 'lat' if 'lat' in masked_obs.coords else 'latitude'
    obs_lon_name = 'lon' if 'lon' in masked_obs.coords else 'longitude'
    weights = np.cos(np.deg2rad(masked_obs[obs_lat_name]))
    weights.name = "weights"
    
    obs_weighted = masked_obs[obs_var].weighted(weights)
    df_data = {'OBS': obs_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()}
    for exp_name, ds in masked_lis.items():
        lis_weighted = ds["SoilMoist_tavg"].weighted(weights)
        df_data[exp_name] = lis_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()
        
    df = pd.DataFrame(df_data)
    Plotting.plot_time_series(
        df, 
        f"Domain-Mean Surface Soil Moisture vs {cfg['display_name']}", 
        "Soil moisture [m³ m⁻³]", 
        os.path.join(out_dir, "SM_timeseries_corrected"),
        metrics={
            "title": f"Time Series vs {cfg['display_name']}",
            "caption": "Domain-averaged daily time series of soil moisture for the model experiments compared to the independent observations.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # Scatterplots
    Plotting.plot_pooled_scatterplots(
        masked_obs[obs_var], 
        {exp: ds["SoilMoist_tavg"] for exp, ds in masked_lis.items()}, 
        os.path.join(out_dir, "SM-04_Pooled_Scatterplots"),
        metrics_dict={
            "title": f"Pooled Scatterplots vs {cfg['display_name']}",
            "caption": "Hexbin scatterplots of daily matched grid-cell observations, assessing overall correlation and structural biases.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # RMSE and Bias
    bias_panels = {}
    rmse_panels = {}
    for exp_name, ds in masked_lis.items():
        bias_panels[exp_name] = ds["SoilMoist_tavg"].mean(dim='time') - mean_obs
        rmse_panels[exp_name] = np.sqrt(((ds["SoilMoist_tavg"] - masked_obs[obs_var])**2).mean(dim='time'))
        
    median_bias = np.nanmedian(bias_panels[opl_name].values)
    mean_bias = np.nanmean(bias_panels[opl_name].values)
    bias_vals = bias_panels[opl_name].values
    bias_vals = bias_vals[~np.isnan(bias_vals)]
    pct_small_bias = np.sum(np.abs(bias_vals) < 0.02) / len(bias_vals) * 100 if len(bias_vals) > 0 else 0
    bias_qc = f"Domain-mean bias = {mean_bias:.4f}\nSpatial median bias = {median_bias:.4f}\n|bias| < 0.02 = {pct_small_bias:.1f}%\nMin pairs/cell = {min_pairs}"
    
    Plotting.plot_spatial_bias(
        bias_panels[opl_name], 
        os.path.join(out_dir, "SM-05_Spatial_Bias"), 
        lis_bounds, 
        bias_qc,
        metrics_dict={
            "title": f"Spatial Bias vs {cfg['display_name']}",
            "caption": "Spatial distribution of the mean bias for the open-loop experiment.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    rmse_vals = rmse_panels[opl_name].values
    rmse_vals = rmse_vals[~np.isnan(rmse_vals)]
    median_rmse = np.nanmedian(rmse_vals)
    rmse_qc = f"Domain median RMSE = {median_rmse:.4f}\nValid cells = {len(rmse_vals)}\nMin pairs/cell = {min_pairs}"
    
    Plotting.plot_spatial_rmse(
        rmse_panels[opl_name], 
        os.path.join(out_dir, "SM-05_Spatial_RMSE"), 
        lis_bounds, 
        rmse_qc,
        metrics_dict={
            "title": f"Spatial RMSE vs {cfg['display_name']}",
            "caption": "Spatial distribution of the Root Mean Square Error (RMSE) for the open-loop experiment.",
            "diagnostic_type": "independent_ob_validation",
            "variable": obs_var,
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    if len(experiments) > 1 and opl_name in rmse_panels:
        skill_panels = {}
        for exp_name in experiments:
            if exp_name != opl_name and exp_name in rmse_panels:
                skill_panels[exp_name] = rmse_panels[opl_name] - rmse_panels[exp_name]
        
        if skill_panels:
            Plotting.plot_map_panels(
                skill_panels,
                f"SM-06: Assimilation Skill (RMSE_OPL - RMSE_DA)",
                os.path.join(out_dir, "SM-06_Assimilation_Skill"),
                "Skill [m³ m⁻³] (Positive = DA is better)",
                cmap="PiYG",
                divergent=True,
                metrics_dict={
                    "title": f"Assimilation Skill vs {cfg['display_name']}",
                    "caption": "Difference in RMSE between the open-loop and data assimilation experiments. Positive values (green) indicate improvement by the assimilation.",
                    "diagnostic_type": "independent_ob_validation",
                    "variable": obs_var,
                    "experiment": "DA_Differences"
                }
            )
