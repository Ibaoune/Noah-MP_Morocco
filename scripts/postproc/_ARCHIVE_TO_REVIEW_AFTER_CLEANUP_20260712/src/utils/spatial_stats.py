# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: utils.spatial_stats
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import numpy as np

def calculate_basin_average(data_array, landmask):
    """
    Calculate the spatial average over the basin, strictly where landmask == 1.
    """
    if data_array is None:
        return None
    
    mask_3d = np.broadcast_to(landmask == 1, data_array.shape)
    valid_data = np.ma.masked_where(~mask_3d | (data_array <= -9000) | np.isnan(data_array), data_array)
    
    return valid_data.mean(axis=(1, 2))
