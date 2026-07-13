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

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "evapotranspiration")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
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
    
    project_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_matrix_dir = os.path.join(project_root, "experiments/NorthMor/matrix_2016")
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        try:
            # Most ET variables in LIS are Evap_tavg or Qle_tavg. Assuming Evap_tavg.
            ds = LISLoader.load_variable(os.path.join(base_matrix_dir, exp_path), "Evap_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS ET for {exp_name}: {e}")
            
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
    
    # Common Valid Mask
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["Evap_tavg"].notnull()
        
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    # ET-02: Mean ET
    mean_obs = masked_obs[obs_var].mean(dim='time')
    panels = {cfg['display_name']: mean_obs}
    for exp_name, ds in masked_lis.items():
        panels[exp_name] = ds["Evap_tavg"].mean(dim='time')
        
    Plotting.plot_map_panels(
        panels,
        f"Mean Evapotranspiration vs {cfg['display_name']}",
        os.path.join(out_dir, "ET-02_Mean_ET"),
        "ET [kg m-2 s-1]",
        cmap="YlGnBu",
        divergent=False
    )
    
    # ET-03: Time Series
    df_data = {'OBS': masked_obs[obs_var].mean(dim=['lat', 'lon']).to_series()}
    for exp_name, ds in masked_lis.items():
        df_data[exp_name] = ds["Evap_tavg"].mean(dim=['lat', 'lon']).to_series()
        
    df = pd.DataFrame(df_data)
    Plotting.plot_time_series(
        df.dropna(),
        f"Domain Mean Evapotranspiration vs {cfg['display_name']}",
        "ET [kg m-2 s-1]",
        os.path.join(out_dir, "ET-03_Time_Series")
    )
