# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import os
import logging
import xarray as xr
import pandas as pd
from .observation_loader import ObservationLoader
from .lis_loader import LISLoader
from .temporal_alignment import TemporalAlignment
from .spatial_alignment import SpatialAlignment
from .dataset_registry import DatasetRegistry
from .plotting import Plotting
import numpy as np

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "evapotranspiration")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    registry = DatasetRegistry(os.path.join(project_root, "scripts/postproc/configs/observations"))
    
    for name, cfg in registry.get_ready_datasets().items():
        if cfg.get("validation_category") == "evapotranspiration":
            sub_dir = os.path.join(out_dir, name)
            os.makedirs(sub_dir, exist_ok=True)
            try:
                _run_single_validation(cfg, experiments, sub_dir)
            except Exception as e:
                logger.error(f"ET Validation failed for {name}: {e}")

def _run_single_validation(cfg, experiments, out_dir):
    logger.info(f"Running ET validation for {cfg['display_name']}")
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_var = cfg["variables"]["lis"]
    
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
            ds = LISLoader.load_variable(full_exp_path, "Evap_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS ET for {exp_name}: {e}")
            
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
        _log_stats(exp_name, ds["Evap_tavg"])
        
        # Unit conversion: if LIS is kg m-2 s-1, convert to mm day-1
        # 1 kg m-2 = 1 mm of water. 86400 seconds in a day.
        # Check original values. If they are very small (e.g. ~1e-5), they are per second.
        if float(ds["Evap_tavg"].mean().compute()) < 1.0:
            logger.info(f"Converting {exp_name} ET from kg m-2 s-1 to mm day-1")
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
        
    Plotting.setup_style()
    
    # Common Valid Mask
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["Evap_tavg"].notnull()
        
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    # ET-02: Mean ET
    mean_obs = masked_obs[obs_var].mean(dim='time')
    panels = {'GLEAM ET': mean_obs}
    for exp_name, ds in masked_lis.items():
        label_map = {
            'OPL_noirr_2016': 'Open loop',
            'DA_smap_nocdf_noirr_2016': 'SMAP-DA without CDF',
            'DA_smap_cdf_noirr_2016': 'SMAP-DA with CDF'
        }
        label = label_map.get(exp_name, exp_name)
        panels[label] = ds["Evap_tavg"].mean(dim='time')
        
    Plotting.plot_map_panels(
        panels,
        "Mean Evapotranspiration over Common Dates, 2016",
        os.path.join(out_dir, "ET_mean_maps_corrected"),
        "ET [mm day⁻¹]",
        cmap="YlGnBu",
        divergent=False,
        metrics_dict={
            "title": "Annual Mean Evapotranspiration vs GLEAM",
            "caption": "Spatial distribution of annual mean evapotranspiration from the independent GLEAM dataset and the Noah-MP experiments.",
            "diagnostic_type": "independent_ob_validation",
            "variable": "Evapotranspiration",
            "experiment": "OPL_noCDF_CDF"
        }
    )
    
    # ET-03: Time Series
    lat_name = 'lat' if 'lat' in masked_obs.coords else 'latitude'
    lon_name = 'lon' if 'lon' in masked_obs.coords else 'longitude'
    weights = np.cos(np.deg2rad(masked_obs[lat_name]))
    weights.name = "weights"
    
    df_data = {'GLEAM ET': masked_obs[obs_var].weighted(weights).mean(dim=[lat_name, lon_name]).to_series()}
    for exp_name, ds in masked_lis.items():
        label = label_map.get(exp_name, exp_name)
        df_data[label] = ds["Evap_tavg"].weighted(weights).mean(dim=[lat_name, lon_name]).to_series()
        
    df = pd.DataFrame(df_data).dropna(how='all')
    Plotting.plot_time_series(
        df,
        "Domain-Mean Evapotranspiration: GLEAM and Noah-MP Experiments",
        "ET [mm day⁻¹]",
        os.path.join(out_dir, "ET_timeseries_corrected"),
        metrics={
            "title": "Time Series vs GLEAM",
            "caption": "Domain-averaged daily time series of evapotranspiration for the model experiments compared to the independent GLEAM observations.",
            "diagnostic_type": "independent_ob_validation",
            "variable": "Evapotranspiration",
            "experiment": "OPL_noCDF_CDF"
        }
    )
