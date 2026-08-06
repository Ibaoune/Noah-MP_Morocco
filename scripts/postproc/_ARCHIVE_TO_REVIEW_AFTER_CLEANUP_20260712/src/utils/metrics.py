# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: utils.metrics
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import numpy as np

def calculate_metrics(obs, sim):
    """
    Calculate standard evaluation metrics (Bias, RMSE, ubRMSE, Correlation) between 
    observation arrays and simulation arrays.
    """
    valid_idx = ~np.isnan(obs) & ~np.isnan(sim)
    o = obs[valid_idx]
    s = sim[valid_idx]
    
    if len(o) == 0:
        return {"bias": np.nan, "rmse": np.nan, "ubrmse": np.nan, "corr": np.nan}
    
    bias = np.mean(s - o)
    rmse = np.sqrt(np.mean((s - o)**2))
    
    if rmse**2 >= bias**2:
        ubrmse = np.sqrt(rmse**2 - bias**2)
    else:
        ubrmse = np.nan
        
    corr = np.corrcoef(o, s)[0, 1] if len(o) > 1 else np.nan
    
    return {"bias": bias, "rmse": rmse, "ubrmse": ubrmse, "corr": corr}
