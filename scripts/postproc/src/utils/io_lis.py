import os
from datetime import timedelta
import netCDF4 as nc
import numpy as np

def get_lis_files(output_dir, start_date, end_date):
    """
    Retrieve a chronologically sorted list of LIS NetCDF history files 
    within a specified date range.
    """
    files = []
    current_date = start_date
    
    while current_date <= end_date:
        yyyymm = current_date.strftime("%Y%m")
        yyyy_mm = current_date.strftime("%Y-%m")
        yyyymmddhh = current_date.strftime("%Y%m%d%H00")
        
        # Standard format
        filepath = os.path.join(output_dir, yyyymm, f"LIS_HIST_{yyyymmddhh}.d01.nc")
        
        # matrix_2016 format
        filepath_matrix = os.path.join(output_dir, yyyy_mm, "SURFACEMODEL", yyyymm, f"LIS_HIST_{yyyymmddhh}.d01.nc")
        
        if os.path.exists(filepath):
            files.append(filepath)
        elif os.path.exists(filepath_matrix):
            files.append(filepath_matrix)
            
        current_date += timedelta(days=1)
        
    return files

def load_lis_variable(files, var_name, extract_layer=None):
    """
    Load a specific variable across multiple LIS NetCDF files and stack them along the time axis.
    """
    data_list = []
    
    for f in files:
        try:
            ds = nc.Dataset(f, 'r')
            if var_name in ds.variables:
                var_data = ds.variables[var_name][:]
                
                if extract_layer is not None:
                    if len(var_data.shape) == 4:
                        if var_data.shape[0] == 1: 
                            data_list.append(var_data[0, extract_layer, :, :])
                        else:
                            data_list.append(var_data[extract_layer, :, :])
                    elif len(var_data.shape) == 3 and var_data.shape[0] > 1:
                        data_list.append(var_data[extract_layer, :, :])
                else:
                    if len(var_data.shape) == 3 and var_data.shape[0] == 1:
                        data_list.append(var_data[0, :, :])
                    else:
                        data_list.append(var_data)
            ds.close()
        except Exception as e:
            print(f"Warning: Error reading {f} variable {var_name} - {e}")
            
    if data_list:
        return np.stack(data_list, axis=0)
    return None
