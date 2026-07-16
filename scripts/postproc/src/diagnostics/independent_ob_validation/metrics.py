# Author: M. El Aabaribaoune (@um6p)
import xarray as xr
import numpy as np

class Metrics:
    """Calculates scientifically rigorous metrics pixel by pixel."""
    
    @staticmethod
    def bias(model, obs):
        return (model - obs).mean(dim='time')
        
    @staticmethod
    def rmse(model, obs):
        return np.sqrt(((model - obs)**2).mean(dim='time'))
        
    @staticmethod
    def ubrmse(model, obs):
        model_anom = model - model.mean(dim='time')
        obs_anom = obs - obs.mean(dim='time')
        return np.sqrt(((model_anom - obs_anom)**2).mean(dim='time'))
        
    @staticmethod
    def pearson_r(model, obs):
        model_anom = model - model.mean(dim='time')
        obs_anom = obs - obs.mean(dim='time')
        cov = (model_anom * obs_anom).mean(dim='time')
        model_std = model.std(dim='time')
        obs_std = obs.std(dim='time')
        
        # Avoid division by zero
        denom = model_std * obs_std
        r = xr.where(denom != 0, cov / denom, np.nan)
        return r
        
    @staticmethod
    def valid_pairs(model, obs):
        return xr.where(model.notnull() & obs.notnull(), 1, 0).sum(dim='time')

    @staticmethod
    def skill_r(r_da, r_opl):
        return r_da - r_opl
        
    @staticmethod
    def skill_rmse(rmse_da, rmse_opl):
        return rmse_opl - rmse_da
        
    @staticmethod
    def skill_abs_bias(bias_da, bias_opl):
        return np.abs(bias_opl) - np.abs(bias_da)
