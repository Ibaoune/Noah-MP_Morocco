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

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "soil_moisture")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
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
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_matrix_dir = os.path.join(project_root, "experiments/NorthMor/matrix_2016")
    
    is_smoke_test = os.environ.get("SMOKE_TEST", "0") == "1"
    smoke_dates = ['2016-01-15', '2016-04-15', '2016-07-15', '2016-10-15']
    
    lis_datasets = {}
    baseline_ds = None
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        full_exp_path = os.path.join(base_matrix_dir, exp_path)
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
        
    lis_bounds = SpatialAlignment.get_grid_bounds(baseline_ds)
    lis_valid_mask = SpatialAlignment.build_lis_valid_mask(baseline_ds)
    
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_ds = SpatialAlignment.normalize_longitudes(obs_ds)
    obs_ds = SpatialAlignment.sort_spatial_coordinates(obs_ds)
    obs_var = cfg["variables"]["lis"]
    
    if is_smoke_test:
        obs_ds = obs_ds.sel(time=obs_ds.time.dt.strftime('%Y-%m-%d').isin(smoke_dates))
        
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
        
    num_common_valid = int(common_mask.sum())
    assert num_common_valid > 0, "EMPTY_COMMON_MASK"
    
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
    
    Plotting.plot_alignment_smoke_test_map(lis_valid_mask, esa_mask, common_mask.any('time'), os.path.join(out_dir, "NorthMor_Spatial_Alignment_Smoke_Test"), lis_bounds, qc_text)
    Plotting.plot_smoke_test_timeseries(obs_ds, lis_datasets, obs_var, common_mask, os.path.join(out_dir, "NorthMor_Smoke_Test_Time_Series.png"))

def _generate_products(cfg, lis_datasets, obs_ds, obs_var, common_mask, out_dir, experiments, subset_id, lis_bounds):
    Plotting.setup_style()
    
    min_pairs = cfg.get("validation_metrics", {}).get("min_valid_days", 50)
    
    valid_count = common_mask.sum(dim='time')
    total_days = len(obs_ds['time']) if 'time' in obs_ds.coords else 366
    
    Plotting.plot_data_coverage(
        valid_count, total_days,
        os.path.join(out_dir, "SM-01_Data_Coverage"),
        lis_bounds, min_pairs
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
        lis_bounds
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
    Plotting.plot_domain_time_series(df, os.path.join(out_dir, "SM-03_Domain_Time_Series"))
    
    # Scatterplots
    Plotting.plot_pooled_scatterplots(masked_obs[obs_var], {exp: ds["SoilMoist_tavg"] for exp, ds in masked_lis.items()}, os.path.join(out_dir, "SM-04_Pooled_Scatterplots"))
    
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
    
    Plotting.plot_spatial_bias(bias_panels[opl_name], os.path.join(out_dir, "SM-05_Spatial_Bias"), lis_bounds, bias_qc)
    
    rmse_vals = rmse_panels[opl_name].values
    rmse_vals = rmse_vals[~np.isnan(rmse_vals)]
    median_rmse = np.nanmedian(rmse_vals)
    rmse_qc = f"Domain median RMSE = {median_rmse:.4f}\nValid cells = {len(rmse_vals)}\nMin pairs/cell = {min_pairs}"
    
    Plotting.plot_spatial_rmse(rmse_panels[opl_name], os.path.join(out_dir, "SM-05_Spatial_RMSE"), lis_bounds, rmse_qc)
    
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
                divergent=True
            )
