"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: utils.masking
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import numpy as np
import netCDF4 as nc

def get_lat_lon(files):
    if not files: return None, None
    try:
        ds = nc.Dataset(files[0], 'r')
        lat = ds.variables['lat'][:]
        lon = ds.variables['lon'][:]
        ds.close()
        return lat, lon
    except:
        return None, None

def get_landmask(files):
    if not files: return None
    try:
        ds = nc.Dataset(files[0], 'r')
        if 'SoilMoist_tavg' in ds.variables:
            var_data = ds.variables['SoilMoist_tavg']
            if len(var_data.shape) == 4:
                sm = var_data[0, 0, :, :]
            else:
                sm = var_data[0, :, :]
            mask = np.where(sm > -9000, 1, 0)
        else:
            mask = np.ones(ds.variables['lat'].shape)
        ds.close()
        return mask
    except Exception as e:
        print(f"Error getting landmask: {e}")
        return None
