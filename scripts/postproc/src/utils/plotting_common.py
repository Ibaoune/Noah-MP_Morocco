"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: utils.plotting_common
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import numpy as np
import cartopy.crs as ccrs

def plot_map_diff(ax, diff_data, lat, lon, title, vmin, vmax, cmap):
    if diff_data is None: return None
    valid_data = np.ma.masked_where(diff_data < -9000, diff_data)
    pcm = ax.pcolormesh(lon, lat, valid_data, cmap=cmap, vmin=vmin, vmax=vmax, transform=ccrs.PlateCarree())
    ax.coastlines()
    ax.set_title(title, fontsize=10)
    return pcm
