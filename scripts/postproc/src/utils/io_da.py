import os
import glob
from datetime import datetime
import netCDF4 as nc
import numpy as np

def get_da_files(experiment_path, start_date, end_date):
    """
    Finds LIS DA output files (EnKF and DAOBS) within a specified date range.
    Returns a dictionary grouping files by type.
    """
    da_files = {
        'innov': [],
        'incr': [],
        'spread': [],
        'obs': []
    }
    
    # Check if the output directory exists
    if os.path.basename(experiment_path) == 'output':
        output_dir = experiment_path
    else:
        output_dir = os.path.join(experiment_path, 'output')
        
    if not os.path.exists(output_dir):
        return da_files
        
    for month_dir in sorted(os.listdir(output_dir)):
        month_path = os.path.join(output_dir, month_dir)
        if not os.path.isdir(month_path):
            continue
            
        # Parse month_dir which is usually YYYY-MM
        try:
            dir_date = datetime.strptime(month_dir, "%Y-%m")
            if dir_date.year < start_date.year or dir_date.year > end_date.year:
                continue
        except ValueError:
            pass

        # Paths
        enkf_dir = os.path.join(month_path, 'EnKF', month_dir.replace('-', ''))
        daobs_dir = os.path.join(month_path, 'DAOBS', month_dir.replace('-', ''))
        
        # EnKF files
        if os.path.exists(enkf_dir):
            for f in sorted(os.listdir(enkf_dir)):
                if f.endswith('_innov.a01.d01.nc'):
                    da_files['innov'].append(os.path.join(enkf_dir, f))
                elif f.endswith('_incr.a01.d01.nc'):
                    da_files['incr'].append(os.path.join(enkf_dir, f))
                elif f.endswith('_spread.a01.d01.nc'):
                    da_files['spread'].append(os.path.join(enkf_dir, f))
                    
        # DAOBS files
        if os.path.exists(daobs_dir):
            for f in sorted(os.listdir(daobs_dir)):
                if f.startswith('LISDAOBS_') and f.endswith('.a01.d01.1gs4r'):
                    da_files['obs'].append(os.path.join(daobs_dir, f))
                    
    return da_files

def load_da_variable(files, var_name, extract_layer=None):
    """
    Loads a specific variable from a list of DA NetCDF files and concatenates them along the time dimension.
    """
    if not files:
        return None
        
    data = []
    for f in files:
        try:
            with nc.Dataset(f, 'r') as ds:
                if var_name in ds.variables:
                    val = ds.variables[var_name][:]
                    # If it has a layer dimension (like incr or spread)
                    if extract_layer is not None and val.ndim == 3:
                        val = val[extract_layer, :, :]
                    data.append(val)
        except Exception as e:
            print(f"Warning: Could not read {var_name} from {f} ({e})")
            
    if not data:
        return None
        
    return np.array(data)
