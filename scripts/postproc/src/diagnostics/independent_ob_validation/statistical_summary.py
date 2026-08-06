# Author: M. EL Aabaribaoune (@um6p)

import os
import sys
import logging
import xarray as xr
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.stats import pearsonr

from src.diagnostics.independent_ob_validation.observation_loader import ObservationLoader
from src.diagnostics.independent_ob_validation.lis_loader import LISLoader
from src.diagnostics.independent_ob_validation.spatial_alignment import SpatialAlignment
from src.diagnostics.independent_ob_validation.dataset_registry import DatasetRegistry
from src.core.config import get_experiments_catalog

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

def compute_anomaly_r(model_da, obs_da):
    """Computes anomaly Pearson correlation coefficient pixel by pixel."""
    model_clim = model_da.groupby('time.month').mean('time')
    obs_clim = obs_da.groupby('time.month').mean('time')
    
    model_anom = model_da.groupby('time.month') - model_clim
    obs_anom = obs_da.groupby('time.month') - obs_clim
    
    cov = (model_anom * obs_anom).mean(dim='time')
    model_std = model_anom.std(dim='time')
    obs_std = obs_anom.std(dim='time')
    
    denom = model_std * obs_std
    return xr.where(denom != 0, cov / denom, np.nan)

def compute_metrics(model_da, obs_da):
    # R
    model_anom_time = model_da - model_da.mean('time')
    obs_anom_time = obs_da - obs_da.mean('time')
    cov = (model_anom_time * obs_anom_time).mean('time')
    r = xr.where((model_anom_time.std('time') * obs_anom_time.std('time')) != 0,
                 cov / (model_anom_time.std('time') * obs_anom_time.std('time')), np.nan)
    
    # Anomaly R
    anomaly_r = compute_anomaly_r(model_da, obs_da)
    
    # RMSD
    rmsd = np.sqrt(((model_da - obs_da)**2).mean('time'))
    
    # Bias
    bias = (model_da - obs_da).mean('time')
    
    return {
        'R': r,
        'Anomaly R': anomaly_r,
        'RMSD': rmsd,
        'Bias': bias
    }

def process_variable(ds_id, obs_cfg, experiments_dict):
    logger.info(f"Processing {ds_id}...")
    
    obs_ds = ObservationLoader.load_dataset(obs_cfg)
    obs_var = obs_cfg["variables"]["lis"] # ObservationLoader renames to lis_var
    lis_var = obs_cfg["variables"]["lis"]
    
    if 'dim_0' in obs_ds.coords:
        obs_ds = obs_ds.rename({'dim_0': 'time'})
    if 'dim_0' in obs_ds.dims:
        obs_ds = obs_ds.rename_dims({'dim_0': 'time'})
        
    logger.info(f"Loaded OBS {ds_id}: shape {obs_ds[obs_var].shape}, time {obs_ds['time'].values[0]} to {obs_ds['time'].values[-1]}")
    
    # Pre-process LIS datasets
    lis_datasets = {}
    for exp_name, exp_path in experiments_dict.items():
        try:
            ds = LISLoader.load_variable(exp_path, lis_var)
            lis_datasets[exp_name] = ds
        except Exception as e:
            logger.error(f"Failed to load LIS for {exp_name}: {e}")
            
    if not lis_datasets:
        return None
        
    # 1. Spatial Alignment (aggregate obs to LIS grid)
    logger.info(f"Spatially aggregating OBS {ds_id} to LIS grid...")
    obs_ds = SpatialAlignment.normalize_longitudes(obs_ds)
    obs_ds = SpatialAlignment.sort_spatial_coordinates(obs_ds)
    for k, v in lis_datasets.items():
        if 'north_south' in v.dims and 'east_west' in v.dims:
            lat_v = 'lat' if 'lat' in v.variables else 'latitude'
            lon_v = 'lon' if 'lon' in v.variables else 'longitude'
            if len(v[lat_v].dims) == 2:
                lat_1d = v[lat_v].isel(east_west=0).values
                lon_1d = v[lon_v].isel(north_south=0).values
            else:
                lat_1d = v[lat_v].values
                lon_1d = v[lon_v].values
            v = v.drop_vars([lat_v, lon_v], errors='ignore')
            v = v.rename_dims({'north_south': 'lat', 'east_west': 'lon'})
            v = v.assign_coords({lat_v: ('lat', lat_1d), lon_v: ('lon', lon_1d)})
        lis_datasets[k] = SpatialAlignment.normalize_longitudes(v)
        lis_datasets[k] = SpatialAlignment.sort_spatial_coordinates(lis_datasets[k])
        
    # Get LIS common spatial grid from the first experiment (after dimension renaming)
    first_exp = list(lis_datasets.keys())[0]
    lis_grid_ds = lis_datasets[first_exp].isel(time=0).drop_vars('time', errors='ignore')
    
    lis_grid_ds = SpatialAlignment.normalize_longitudes(lis_grid_ds)
    lis_grid_ds = SpatialAlignment.sort_spatial_coordinates(lis_grid_ds)
    
    # Crop global observation datasets to LIS domain to save memory and time
    lis_lat_name = 'lat' if 'lat' in lis_grid_ds.coords else 'latitude'
    lis_lon_name = 'lon' if 'lon' in lis_grid_ds.coords else 'longitude'
    obs_lat_name = 'lat' if 'lat' in obs_ds.coords else 'latitude'
    obs_lon_name = 'lon' if 'lon' in obs_ds.coords else 'longitude'
    
    min_lat, max_lat = float(lis_grid_ds[lis_lat_name].min()) - 1.0, float(lis_grid_ds[lis_lat_name].max()) + 1.0
    min_lon, max_lon = float(lis_grid_ds[lis_lon_name].min()) - 1.0, float(lis_grid_ds[lis_lon_name].max()) + 1.0
    
    if len(obs_ds[obs_lat_name].dims) == 1:
        lat_vals = obs_ds[obs_lat_name].values
        lon_vals = obs_ds[obs_lon_name].values
        
        lat_slice = slice(max_lat, min_lat) if lat_vals[0] > lat_vals[-1] else slice(min_lat, max_lat)
        lon_slice = slice(max_lon, min_lon) if lon_vals[0] > lon_vals[-1] else slice(min_lon, max_lon)
        
        obs_ds = obs_ds.sel({obs_lat_name: lat_slice, obs_lon_name: lon_slice})
        
        logger.info("Loading cropped OBS into memory...")
        obs_ds = obs_ds.compute()
    
    aligned_obs_ds = SpatialAlignment.aggregate_observation_to_lis_grid(obs_ds, lis_grid_ds)
    
    # 2. Temporal Aggregation (to monthly)
    logger.info(f"Temporally aggregating OBS and LIS to monthly sums...")
    
    # OBS Aggregation
    if "wapor" in ds_id.lower():
        # Dekadal -> sum to monthly
        obs_monthly = aligned_obs_ds.resample(time="MS").sum(skipna=True, min_count=1)
    else:
        # Daily -> sum to monthly
        obs_monthly = aligned_obs_ds.resample(time="MS").sum(skipna=True, min_count=1)
        
    # LIS Aggregation
    lis_monthly = {}
    for exp_name, ds in lis_datasets.items():
        da = ds[lis_var]
        # LIS is daily mean rate (kg/m2/s or gC/m2/s)
        # Convert to daily total
        if 's-1' in da.attrs.get('units', 'unknown') or float(da.mean().compute()) < 1.0:
            da_daily = da * 86400.0
        else:
            da_daily = da
        
        # Sum to monthly
        da_monthly = da_daily.resample(time="MS").sum(skipna=True, min_count=1)
        lis_monthly[exp_name] = da_monthly
        
    # 3. Time alignment (Intersection)
    obs_dates = pd.to_datetime(obs_monthly.time.values).strftime('%Y-%m-%d')
    lis_dates = pd.to_datetime(lis_monthly[first_exp].time.values).strftime('%Y-%m-%d')
    common_dates = np.intersect1d(obs_dates, lis_dates)
    
    # Filter for 2016-2020
    common_dates = [d for d in common_dates if '2016-01-01' <= d <= '2020-12-31']
    
    obs_monthly = obs_monthly.sel(time=common_dates)
    for exp_name in lis_monthly:
        lis_monthly[exp_name] = lis_monthly[exp_name].sel(time=common_dates)
        
    logger.info(f"Common evaluation period: {common_dates[0]} to {common_dates[-1]} ({len(common_dates)} months)")
    
    # 4. Strict Common Mask
    # Create a common mask where BOTH datasets have valid data
    # Only keep pixels that have at least minimum_valid_pairs across time
    min_pairs = int(obs_cfg.get("quality_control", {}).get("minimum_valid_pairs", 30))
    # Cap min_pairs to the actual number of months available to avoid excluding WaPOR (which has 12 months)
    min_pairs = min(min_pairs, len(common_dates))
    
    valid_count = (obs_monthly[obs_var].notnull() & xr.concat([da.notnull() for da in lis_monthly.values()], dim='exp').all('exp')).sum(dim='time')
    common_mask = valid_count >= min_pairs
    
    n_valid_pixels = int(common_mask.sum())
    logger.info(f"N valid pixels in common mask (>= {min_pairs} months): {n_valid_pixels}")
    
    if n_valid_pixels == 0:
        logger.error("0 valid pixels found after masking.")
        return None
        
    # Mask data
    obs_masked = obs_monthly[obs_var].where(common_mask)
    lis_masked = {k: v.where(common_mask) for k, v in lis_monthly.items()}
    
    # 5. Compute Metrics
    results = {}
    all_maps = []
    
    for exp_name, model_da in lis_masked.items():
        logger.info(f"Computing metrics for {exp_name}...")
        metrics = compute_metrics(model_da, obs_masked)
        
        exp_ds = xr.Dataset(metrics).expand_dims(exp=[exp_name])
        all_maps.append(exp_ds)
        
        stats = {}
        for m_name, m_da in metrics.items():
            vals = m_da.values[common_mask.values]
            stats[m_name] = {
                'mean': float(np.nanmean(vals)),
                'median': float(np.nanmedian(vals)),
                'q25': float(np.nanpercentile(vals, 25)),
                'q75': float(np.nanpercentile(vals, 75))
            }
        results[exp_name] = stats
        
    combined_ds = xr.concat(all_maps, dim='exp')
    out_dir = Path("outputs/independent_ob_validation")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_nc = out_dir / f"skill_maps_{ds_id}.nc"
    combined_ds.to_netcdf(out_nc)
    logger.info(f"Saved 2D skill maps to {out_nc}")
    
    return {
        'n_months': len(common_dates),
        'period_start': common_dates[0],
        'period_end': common_dates[-1],
        'n_valid_pixels': n_valid_pixels,
        'metrics': results
    }

def print_inventory_and_table(all_results):
    print("\n" + "="*60)
    print("REFERENCE DATA INVENTORY")
    print("="*60)
    for var_ref, info in all_results.items():
        print(f"\n{var_ref}")
        print(f"native temporal resolution: {info['native_temporal']}")
        print(f"native units: {info['native_units']}")
        print(f"native spatial resolution: {info['native_spatial']}")
        print(f"actual available period: {info['actual_period']}")
        print(f"common model/reference period: {info['period_start']} to {info['period_end']}")
        print(f"conversion performed: {info['conversion']}")
        print(f"evaluation grid: {info['eval_grid']}")
        print(f"N months: {info['n_months']}")
        print(f"N valid pixels: {info['n_valid_pixels']}")
        
    print("\n" + "="*60)
    print("NUMERICAL TABLE (SPATIAL MEDIANS)")
    print("="*60)
    
    experiments = ['OPL', 'DA_NoCDF', 'DA_CDF']
    print(f"{'':<20} {'OL':<12} {'DA-NoCDF':<12} {'DA-CDF':<12}")
    
    for var_ref, info in all_results.items():
        print(f"{var_ref}")
        metrics_dict = info['metrics']
        
        for m in ['R', 'Anomaly R', 'RMSD', 'Bias']:
            row_vals = []
            for exp in experiments:
                exp_key = exp if exp in metrics_dict else None
                
                if exp_key is not None and m in metrics_dict[exp_key]:
                    row_vals.append(f"{metrics_dict[exp_key][m]['median']:.3f}")
                else:
                    row_vals.append("N/A")
            print(f"{m:<20} {row_vals[0]:<12} {row_vals[1]:<12} {row_vals[2]:<12}")
        print("-" * 55)

if __name__ == "__main__":
    project_root = global_cfg.get("_project_root", "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco") if "global_cfg" in locals() else "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
    config_dir = os.path.join(project_root, "scripts/postproc/configs/observations")
    
    registry = DatasetRegistry(config_dir)
    ready_datasets = registry.get_ready_datasets()
    
    target_datasets = ['gleam', 'wapor_v2_aeti', 'fluxsat_gpp']
    
    if len(sys.argv) > 1:
        target_datasets = [sys.argv[1]]
        print(f"Running specifically for dataset: {target_datasets[0]}")
    
    # Map experiments
    catalog = get_experiments_catalog()
    # We want OPL, DA_NoCDF, DA_CDF
    exp_keys = ['OPL', 'DA_NoCDF', 'DA_CDF']
    exp_paths = {k: catalog[k]['path_abs'] for k in exp_keys if k in catalog}
    
    all_results = {}
    
    for ds_id in target_datasets:
        if ds_id in ready_datasets:
            cfg = ready_datasets[ds_id]
            res = process_variable(ds_id, cfg, exp_paths)
            if res:
                var_name = "ET" if "evapotranspiration" in cfg["validation_category"] else "GPP"
                ref_name = cfg["display_name"].split()[0]
                
                if "WaPOR" in cfg["display_name"]: ref_name = "WaPOR"
                if "GLEAM" in cfg["display_name"]: ref_name = "GLEAM"
                if "FLUXSAT" in cfg["display_name"]: ref_name = "FLUXSAT"
                
                key = f"{var_name}-{ref_name}"
                
                res['native_temporal'] = cfg['temporal'].get('native_frequency', 'unknown')
                res['native_units'] = cfg['units'].get('native', 'unknown')
                res['native_spatial'] = cfg['spatial'].get('native_resolution', 'unknown')
                res['actual_period'] = f"{cfg['period'].get('start')} to {cfg['period'].get('end')}"
                res['conversion'] = "Aggregated to monthly sum"
                res['eval_grid'] = "Common Model-Scale Grid (conservative)"
                
                all_results[key] = res
                
    print_inventory_and_table(all_results)
