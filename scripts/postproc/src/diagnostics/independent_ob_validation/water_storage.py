# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import os
import logging
import xarray as xr
import pandas as pd
import numpy as np
from .observation_loader import ObservationLoader
from .lis_loader import LISLoader
from .temporal_alignment import TemporalAlignment
from .spatial_alignment import SpatialAlignment
from .dataset_registry import DatasetRegistry
from .plotting import Plotting
import warnings

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "water_storage")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    registry = DatasetRegistry(os.path.join(project_root, "scripts/postproc/configs/observations"))
    
    for name, cfg in registry.get_ready_datasets().items():
        if cfg.get("validation_category") == "water_storage":
            sub_dir = os.path.join(out_dir, name)
            os.makedirs(sub_dir, exist_ok=True)
            try:
                _run_single_validation(cfg, experiments, sub_dir)
            except Exception as e:
                logger.error(f"Water Storage Validation failed for {name}: {e}")

def _run_single_validation(cfg, experiments, out_dir):
    logger.info(f"Running Water Storage validation for {cfg['display_name']}")
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_var = cfg["variables"]["lis"]
    
    from src.core.config import get_experiments_catalog
    catalog = get_experiments_catalog()
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        exp_info = catalog.get(exp_name, {})
        full_exp_path = exp_info.get("path_abs")
        if not full_exp_path:
            logger.error(f"Path for experiment {exp_name} not found in catalog.")
            continue
        try:
            ds = LISLoader.load_variable(full_exp_path, "TWS_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS TWS for {exp_name}: {e}")
            
    if not lis_datasets: return
    
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

    _log_stats(cfg["display_name"], obs_ds[obs_var])
    for exp_name, ds in lis_datasets.items():
        _log_stats(exp_name, ds["TWS_tavg"])
        # If LIS is in kg m-2, it's equivalent to mm.
        ds["TWS_tavg"].attrs['units'] = 'mm'
        
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
        
    Plotting.setup_style()
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["TWS_tavg"].notnull()
        
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    # SCIENTIFIC QC: Check Anomaly Baseline Compatibility
    obs_mean_val = float(masked_obs[obs_var].mean().compute())
    
    if abs(obs_mean_val) > 1.0:
        logger.error(f"Incompatible baseline detected. GRACE mean over 2016 is {obs_mean_val:.1f} mm, indicating a climatological baseline (e.g. 2004-2009) not available in the 2016-only LIS simulation.")
        raise ValueError("Incompatible TWS anomaly baselines between LIS (2016 only) and GRACE. Stopping comparison.")
        
    grace_anom = masked_obs[obs_var] - masked_obs[obs_var].mean(dim='time')
    lis_anom = {exp: ds["TWS_tavg"] - ds["TWS_tavg"].mean(dim='time') for exp, ds in masked_lis.items()}
    
    n_matched = int(valid_mask.any(dim=['lat', 'lon']).sum().compute())
    
    # WS-02: TWS Anomaly Amplitude (Std Dev)
    # The mean anomaly over the reference period is zero. We plot standard deviation instead.
    grace_std_anom = grace_anom.std(dim='time')
    
    opl_name = next((exp for exp in experiments if 'opl' in exp.lower()), list(experiments)[0])
    lis_std_anom = lis_anom[opl_name].std(dim='time')
    diff_std = lis_std_anom - grace_std_anom
    
    Plotting.plot_tws_mean_panels(
        grace_std_anom, 
        lis_std_anom, 
        diff_std,
        "Terrestrial water-storage anomaly amplitude (std dev) over matched GRACE months, 2016",
        os.path.join(out_dir, "TWS_mean_maps_corrected"),
        lis_bounds,
        n_matched=n_matched,
        metrics_dict={
            "title": "TWS Anomaly Amplitude vs GRACE",
            "caption": "Spatial distribution of the terrestrial water-storage anomaly standard deviation for the independent GRACE dataset and the Noah-MP open loop.",
            "diagnostic_type": "independent_ob_validation",
            "variable": "Water_Storage",
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # WS-03: Time Series
    obs_lat_name = 'lat' if 'lat' in grace_anom.coords else 'latitude'
    obs_lon_name = 'lon' if 'lon' in grace_anom.coords else 'longitude'
    weights = np.cos(np.deg2rad(grace_anom[obs_lat_name]))
    weights.name = "weights"
    
    grace_weighted = grace_anom.weighted(weights)
    df_data = {'OBS': grace_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()}
    
    for exp_name, ds in lis_anom.items():
        lis_weighted = ds.weighted(weights)
        df_data[exp_name] = lis_weighted.mean(dim=[obs_lat_name, obs_lon_name]).to_series()
        
    df = pd.DataFrame(df_data).dropna(how='all')
    
    subtitle = "Area-weighted NorthMor mean; LIS and GRACE expressed relative to the same reference period."
    Plotting.plot_tws_time_series(
        df,
        "Monthly terrestrial water-storage anomalies over NorthMor — 2016",
        subtitle,
        os.path.join(out_dir, "TWS_timeseries_corrected"),
        metrics_dict={
            "title": "Time Series vs GRACE TWSA",
            "caption": "Domain-averaged monthly time series of terrestrial water storage anomalies for the model experiments compared to independent GRACE observations.",
            "diagnostic_type": "independent_ob_validation",
            "variable": "Water_Storage",
            "experiment": "OPL_noCDF_CDF"
        }
    )
