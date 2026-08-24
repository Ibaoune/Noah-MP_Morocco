# Author: M. EL Aabaribaoune (@um6p)
import numpy as np
import xarray as xr

def flatten_dataset(ds, time_var='time', lat_var='lat', lon_var='lon'):
    """
    Flattens a 3D (time, lat, lon) xarray Dataset into a 2D pandas DataFrame.
    Filters out pixels where all variables are NaN (e.g., ocean or outside domain).
    """
    df = ds.to_dataframe().reset_index()
    
    # Drop rows where coordinates are null if any
    df = df.dropna(subset=[lat_var, lon_var])
    
    # Optional: add a 'pixel_id' column based on lat/lon
    df['pixel_id'] = df.groupby([lat_var, lon_var]).ngroup()
    
    return df

def regrid_to_target(source_ds, target_ds, method='nearest'):
    """
    Regrid source_ds to the grid of target_ds using xarray's interp or rioxarray.
    For simplicity, assuming xarray's interp works if grids are rectilinear.
    """
    return source_ds.interp(lat=target_ds.lat, lon=target_ds.lon, method=method)
