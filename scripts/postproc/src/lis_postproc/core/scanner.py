"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.core.scanner
Description: Core framework logic: configuration, variables, and experiment parsing.
================================================================================
"""
import os
import glob
import pandas as pd
import xarray as xr
import logging

logger = logging.getLogger(__name__)

def scan_variables(recipe, experiments_catalog, global_cfg):
    """
    Scans the NetCDF output files for the experiments defined in the recipe,
    and produces available_variables.csv with metadata and basic statistics.
    """
    logger.info("Starting variable scan...")
    
    metrics_dir = recipe.outputs.metrics_dir
    os.makedirs(metrics_dir, exist_ok=True)
    out_csv = os.path.join(metrics_dir, "available_variables.csv")
    
    year = recipe.year
    results = []
    
    for exp_id in recipe.experiments:
        if exp_id not in experiments_catalog:
            logger.warning(f"Experiment {exp_id} not found in catalog.")
            continue
            
        exp_info = experiments_catalog[exp_id]
        project_root = global_cfg.get('paths', {}).get('project_root', '')
        base_path = os.path.join(project_root, exp_info.get('path', ''))
        if not base_path or not os.path.exists(base_path):
            logger.warning(f"Path for {exp_id} does not exist: {base_path}")
            continue
            
        # Find all LIS_HIST files for the given year
        search_pattern = os.path.join(base_path, f"{year}-*", "SURFACEMODEL", f"{year}*", "LIS_HIST*.nc")
        files = sorted(glob.glob(search_pattern))
        
        if not files:
            logger.warning(f"No NetCDF files found for {exp_id} in {year}.")
            continue
            
        logger.info(f"Scanning {len(files)} files for {exp_id}...")
        
        # We'll use the first file to get metadata (units, long_name, dimensions)
        first_file = files[0]
        last_file = files[-1]
        
        try:
            with xr.open_dataset(first_file) as ds:
                variables = list(ds.data_vars.keys())
                for var_name in variables:
                    var = ds[var_name]
                    # Filter out obvious coordinate variables
                    if var_name in ['lat', 'lon', 'time', 'north_south', 'east_west']:
                        continue
                        
                    results.append({
                        "experiment": exp_id,
                        "file_pattern": search_pattern,
                        "variable_name": var_name,
                        "dimensions": str(var.dims),
                        "units": var.attrs.get('units', ''),
                        "long_name": var.attrs.get('long_name', ''),
                        "first_date": os.path.basename(first_file),
                        "last_date": os.path.basename(last_file),
                        "min_value": "Compute omitted (too slow)",
                        "max_value": "Compute omitted (too slow)",
                        "nan_fraction": "Compute omitted"
                    })
        except Exception as e:
            logger.error(f"Error reading {first_file}: {e}")
            
    if results:
        df = pd.DataFrame(results)
        df.to_csv(out_csv, index=False)
        logger.info(f"Variable scan completed. Results saved to {out_csv}")
    else:
        logger.warning("No variables found during scan.")
