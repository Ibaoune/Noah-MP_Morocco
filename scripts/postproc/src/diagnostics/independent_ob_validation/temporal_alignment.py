# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
import xarray as xr
import pandas as pd
import numpy as np

class TemporalAlignment:
    """Handles temporal harmonization between LIS and observations."""
    
    @staticmethod
    def align(lis_ds, obs_ds, freq, method):
        """
        Align both datasets to a common temporal frequency and exactly matching dates.
        """
        # Ensure time is datetime64
        if not np.issubdtype(lis_ds.time.dtype, np.datetime64):
            lis_ds['time'] = pd.to_datetime(lis_ds.time.values)
        if not np.issubdtype(obs_ds.time.dtype, np.datetime64):
            obs_ds['time'] = pd.to_datetime(obs_ds.time.values)
            
        # Normalize time to remove hours/minutes if daily
        if freq == "daily":
            lis_ds['time'] = lis_ds.time.dt.floor("D")
            obs_ds['time'] = obs_ds.time.dt.floor("D")
            
        # Resample LIS if needed
        # We assume LIS is daily or finer
        if freq == "monthly":
            lis_res = lis_ds.resample(time="MS").mean()
            obs_res = obs_ds.resample(time="MS").mean()
        else:
            lis_res = lis_ds
            obs_res = obs_ds
            
        # Find common dates by converting to YYYY-MM-DD strings
        lis_dates = pd.to_datetime(lis_res.time.values).strftime('%Y-%m-%d')
        obs_dates = pd.to_datetime(obs_res.time.values).strftime('%Y-%m-%d')
        
        common_str = np.intersect1d(lis_dates, obs_dates)
        
        if len(common_str) == 0:
            raise ValueError(f"No common time steps found. LIS: {lis_dates[0]} to {lis_dates[-1]}. OBS: {obs_dates[0]} to {obs_dates[-1]}")
            
        # Select using the common strings (xarray sel can handle string dates)
        lis_aligned = lis_res.sel(time=common_str)
        obs_aligned = obs_res.sel(time=common_str)
        
        return lis_aligned, obs_aligned
