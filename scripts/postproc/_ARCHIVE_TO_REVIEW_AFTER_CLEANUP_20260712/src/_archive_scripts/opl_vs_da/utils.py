"""
===============================================================================
Script: utils.py
Author: M. El Aabaribaoune (@um6p)

Objective: Utility functions for NetCDF parsing and geospatial mapping.

Description:
    This module provides auxiliary functions for the plotting framework. 
    It includes functions for temporally averaging NetCDF files (`load_variable`), 
    season-based file filtering, and geospatial axis setup using Cartopy 
    (adding coastlines, borders, and gridlines).

Dependencies:
    os, glob, numpy, netCDF4, matplotlib, cartopy
===============================================================================
"""
import os
import glob
import numpy as np
import netCDF4 as nc
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def get_season(month):
    if month in [12, 1, 2]: return 'DJF'
    elif month in [3, 4, 5]: return 'MAM'
    elif month in [6, 7, 8]: return 'JJA'
    elif month in [9, 10, 11]: return 'SON'
    return 'ALL'

def load_variable(base_dir, var_name, layer_index=None, multiplier=1.0, season='all-period'):
    """
    Reads NetCDF files and averages a variable over time.
    """
    search_pattern = os.path.join(base_dir, "**", "LIS_HIST*.nc")
    files = glob.glob(search_pattern, recursive=True)
    files.sort()
    
    if not files:
        return None, None, None
        
    data_list = []
    lat, lon = None, None
    
    for f in files:
        # Check season if not 'all-period'
        if season != 'all-period':
            try:
                # LIS_HIST_YYYYMMDDHHMM.d01.nc -> month is at index 13-14
                basename = os.path.basename(f)
                month = int(basename[13:15])
                if get_season(month) != season:
                    continue
            except:
                pass # Fallback if parsing fails
                
        try:
            with nc.Dataset(f, 'r') as ds:
                if var_name not in ds.variables:
                    continue
                    
                if lat is None:
                    lat = ds.variables['lat'][:]
                    lon = ds.variables['lon'][:]
                
                var_data = ds.variables[var_name][:]
                
                # Slicing logic: (layer, lat, lon) or (lat, lon)
                if layer_index is not None and len(var_data.shape) == 3:
                    var_data = var_data[layer_index, :, :]
                elif len(var_data.shape) > 2:
                    var_data = var_data[0, :, :] # Fallback to first dimension slice
                    
                data_list.append(var_data * multiplier)
        except Exception as e:
            print(f"Error reading {f}: {e}")
            
    if not data_list:
        return None, None, None
        
    data_stack = np.stack(data_list, axis=0)
    data_avg = np.nanmean(data_stack, axis=0)
    
    return data_avg, lat, lon

def setup_map_axis(ax, lon_min, lon_max, lat_min, lat_max):
    ax.set_extent([lon_min, lon_max, lat_min, lat_max], crs=ccrs.PlateCarree())
    ax.add_feature(cfeature.COASTLINE, linewidth=1.2)
    ax.add_feature(cfeature.BORDERS, linestyle=':')
    gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
