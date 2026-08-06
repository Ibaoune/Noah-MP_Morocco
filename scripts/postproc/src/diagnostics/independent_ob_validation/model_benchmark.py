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

logger = logging.getLogger(__name__)

def run_validation(config, experiments, base_out_dir):
    out_dir = os.path.join(base_out_dir, "model_benchmark")
    os.makedirs(out_dir, exist_ok=True)
    
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    registry = DatasetRegistry(os.path.join(project_root, "scripts/postproc/configs/observations"))
    
    for name, cfg in registry.get_ready_datasets().items():
        if cfg.get("validation_category") == "model_benchmark":
            sub_dir = os.path.join(out_dir, name)
            os.makedirs(sub_dir, exist_ok=True)
            try:
                _run_single_validation(cfg, experiments, sub_dir)
            except Exception as e:
                logger.error(f"Model Benchmark Validation failed for {name}: {e}")

def _run_single_validation(cfg, experiments, out_dir):
    logger.info(f"Running Model Benchmark validation for {cfg['display_name']}")
    obs_ds = ObservationLoader.load_dataset(cfg)
    obs_var = cfg["variables"]["lis"]
    
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    base_matrix_dir = os.path.join(project_root, "experiments/NorthMor/matrix_2016_2020")
    
    lis_datasets = {}
    for exp_path in experiments:
        exp_name = os.path.basename(exp_path)
        try:
            # For GLDAS we usually compare SoilMoist_tavg
            ds = LISLoader.load_variable(os.path.join(base_matrix_dir, exp_path + "_noirr_2016_2020", "output"), "SoilMoist_tavg")
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Could not load LIS SoilMoist_tavg for {exp_name}: {e}")
            
    if not lis_datasets: return
    
    freq = cfg["temporal"].get("target_frequency", "M")
    
    temporally_aligned_lis = {}
    obs_ds = SpatialAlignment.normalize_longitudes(obs_ds)
    for exp_name, ds in lis_datasets.items():
        ds = SpatialAlignment.normalize_longitudes(ds)
        ds = SpatialAlignment.align_lis_to_obs(ds, obs_ds)
        lis_aligned, obs_aligned = TemporalAlignment.align(ds, obs_ds, freq, "mean")
        temporally_aligned_lis[exp_name] = lis_aligned
        temporally_aligned_obs = obs_aligned
        
    Plotting.setup_style()
    valid_mask = temporally_aligned_obs[obs_var].notnull()
    for ds in temporally_aligned_lis.values():
        valid_mask = valid_mask & ds["SoilMoist_tavg"].notnull()
        
    masked_obs = temporally_aligned_obs.where(valid_mask)
    masked_lis = {exp: ds.where(valid_mask) for exp, ds in temporally_aligned_lis.items()}
    
    # BM-02: Mean Soil Moisture
    mean_obs = masked_obs[obs_var].mean(dim='time')
    panels = {cfg['display_name']: mean_obs}
    for exp_name, ds in masked_lis.items():
        panels[exp_name] = ds["SoilMoist_tavg"].mean(dim='time')
        
    Plotting.plot_map_panels(
        panels,
        f"Mean Soil Moisture vs {cfg['display_name']}",
        os.path.join(out_dir, "BM-02_Mean_SM"),
        "Soil Moisture [m³ m⁻³]",
        cmap="YlGnBu",
        divergent=False
    )
    
    # BM-03: Time Series
    df_data = {'OBS': masked_obs[obs_var].mean(dim=['lat', 'lon']).to_series()}
    for exp_name, ds in masked_lis.items():
        df_data[exp_name] = ds["SoilMoist_tavg"].mean(dim=['lat', 'lon']).to_series()
        
    Plotting.plot_time_series(
        pd.DataFrame(df_data).dropna(),
        f"Domain Mean SM vs {cfg['display_name']}",
        "Soil Moisture [m³ m⁻³]",
        os.path.join(out_dir, "BM-03_Time_Series")
    )
