# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Author : M. EL AAbaribaoune
# Purpose: Shared utility functions for the LIS/Noah-MP post-processing framework.
#          Provides functions to load NetCDF history files, extract specific layers,
#          calculate basin-wide spatial averages, and compute evaluation metrics.
# ==============================================================================

import os
import numpy as np
import netCDF4 as nc
from datetime import timedelta

def get_lis_files(output_dir, start_date, end_date):
    """
    Retrieve a chronologically sorted list of LIS NetCDF history files 
    within a specified date range.
    
    Args:
        output_dir (str): Base directory for LIS output (e.g., 'output_smap').
        start_date (datetime): Start date of the evaluation period.
        end_date (datetime): End date of the evaluation period.
        
    Returns:
        list: Absolute or relative paths to the existing LIS history files.
    """
    files = []
    current_date = start_date
    
    while current_date <= end_date:
        yyyymm = current_date.strftime("%Y%m")
        yyyy_mm = current_date.strftime("%Y-%m")
        yyyymmddhh = current_date.strftime("%Y%m%d%H00")
        
        # Standard format
        filepath = os.path.join(output_dir, yyyymm, f"LIS_HIST_{yyyymmddhh}.d01.nc")
        
        # matrix_2016 format (e.g., output/2016-01/SURFACEMODEL/201601/LIS_HIST_...)
        filepath_matrix = os.path.join(output_dir, yyyy_mm, "SURFACEMODEL", yyyymm, f"LIS_HIST_{yyyymmddhh}.d01.nc")
        
        if os.path.exists(filepath):
            files.append(filepath)
        elif os.path.exists(filepath_matrix):
            files.append(filepath_matrix)
            
        # Increment by 1 day (assumes daily outputs; adjust if sub-daily)
        current_date += timedelta(days=1)
        
    return files


def load_lis_variable(files, var_name, extract_layer=None):
    """
    Load a specific variable across multiple LIS NetCDF files and stack them along the time axis.
    
    Args:
        files (list): List of paths to LIS NetCDF files.
        var_name (str): Name of the variable to extract (e.g., 'SoilMoist_tavg').
        extract_layer (int, optional): If the variable has a vertical layer dimension 
                                       (like Soil Moisture), extract this specific layer (0-indexed).
        
    Returns:
        numpy.ndarray: Stacked array of the variable data over time. Returns None if not found.
    """
    data_list = []
    
    for f in files:
        try:
            ds = nc.Dataset(f, 'r')
            if var_name in ds.variables:
                var_data = ds.variables[var_name][:]
                
                # Handle layer extraction if requested
                if extract_layer is not None:
                    # Case 1: Data has time dimension (time, layer, lat, lon)
                    if len(var_data.shape) == 4:
                        if var_data.shape[0] == 1: 
                            data_list.append(var_data[0, extract_layer, :, :])
                        else:
                            data_list.append(var_data[extract_layer, :, :])
                    # Case 2: Data dropped time dimension (layer, lat, lon)
                    elif len(var_data.shape) == 3 and var_data.shape[0] > 1:
                        data_list.append(var_data[extract_layer, :, :])
                else:
                    # Standard 2D extraction (lat, lon)
                    if len(var_data.shape) == 3 and var_data.shape[0] == 1:
                        data_list.append(var_data[0, :, :])
                    else:
                        data_list.append(var_data)
            ds.close()
        except Exception as e:
            print(f"Warning: Error reading {f} variable {var_name} - {e}")
            
    if data_list:
        # Stack all time slices together on a new axis 0
        return np.stack(data_list, axis=0)
    return None


def calculate_basin_average(data_array, landmask):
    """
    Calculate the spatial average over the basin, strictly where landmask == 1.
    
    Args:
        data_array (numpy.ndarray): 3D array (time, lat, lon).
        landmask (numpy.ndarray): 2D array (lat, lon) defining the valid basin.
        
    Returns:
        numpy.ndarray: 1D array of the basin average over time.
    """
    if data_array is None:
        return None
    
    # Broadcast landmask to match the time dimension of data_array
    mask_3d = np.broadcast_to(landmask == 1, data_array.shape)
    
    # Mask invalid values (LIS default missing is usually <= -9000)
    valid_data = np.ma.masked_where(~mask_3d | (data_array <= -9000) | np.isnan(data_array), data_array)
    
    # Return the mean across latitude (axis=1) and longitude (axis=2)
    return valid_data.mean(axis=(1, 2))


def calculate_metrics(obs, sim):
    """
    Calculate standard evaluation metrics (Bias, RMSE, ubRMSE, Correlation) between 
    observation arrays and simulation arrays.
    
    Args:
        obs (numpy.ndarray): Flattened observation array.
        sim (numpy.ndarray): Flattened simulation array.
        
    Returns:
        dict: Dictionary containing 'bias', 'rmse', 'ubrmse', and 'corr'.
    """
    # Remove NaN values from both arrays simultaneously to ensure exact alignment
    valid_idx = ~np.isnan(obs) & ~np.isnan(sim)
    o = obs[valid_idx]
    s = sim[valid_idx]
    
    # Return NaNs if there is no overlapping valid data
    if len(o) == 0:
        return {"bias": np.nan, "rmse": np.nan, "ubrmse": np.nan, "corr": np.nan}
    
    # Core calculations
    bias = np.mean(s - o)
    rmse = np.sqrt(np.mean((s - o)**2))
    
    # Unbiased RMSE formula
    if rmse**2 >= bias**2:
        ubrmse = np.sqrt(rmse**2 - bias**2)
    else:
        ubrmse = np.nan
        
    # Pearson Correlation Coefficient
    corr = np.corrcoef(o, s)[0, 1] if len(o) > 1 else np.nan
    
    return {"bias": bias, "rmse": rmse, "ubrmse": ubrmse, "corr": corr}
