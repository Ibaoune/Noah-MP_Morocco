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

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "water_storage")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
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
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_matrix_dir = os.path.join(project_root, "experiments/NorthMor/matrix_2016")
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        try:
            ds = LISLoader.load_variable(os.path.join(base_matrix_dir, exp_path), "TWS_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS TWS for {exp_name}: {e}")
            
    if not lis_datasets: return
    
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
    
    # WS-02: Mean TWS Anomaly
    grace_mean_anom = grace_anom.mean(dim='time')
    
    opl_name = next((exp for exp in experiments if 'opl' in exp.lower()), list(experiments)[0])
    lis_mean_anom = lis_anom[opl_name].mean(dim='time')
    diff_anom = lis_mean_anom - grace_mean_anom
    
    Plotting.plot_tws_mean_panels(
        grace_mean_anom, 
        lis_mean_anom, 
        diff_anom,
        "Mean terrestrial water-storage anomaly over NorthMor — matched GRACE months, 2016",
        os.path.join(out_dir, "WS-02_Mean_TWS"),
        lis_bounds,
        n_matched=n_matched
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
        os.path.join(out_dir, "WS-03_Time_Series")
    )
