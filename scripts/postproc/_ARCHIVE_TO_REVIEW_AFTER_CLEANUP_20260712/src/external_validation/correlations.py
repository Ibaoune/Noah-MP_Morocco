# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Module: external_validation.correlations
Description: Calculs génériques de corrélations et anomalies vs observations
             externes (e.g. WaPOR, FLUXSAT, MODIS).
================================================================================
"""

import numpy as np
import xarray as xr
import logging

logger = logging.getLogger(__name__)

def compute_spatial_correlation(sim_data: xr.DataArray, obs_data: xr.DataArray) -> xr.DataArray:
    """
    Calcule la corrélation de Pearson pixel par pixel entre une simulation et une observation
    sur l'axe du temps.
    
    Args:
        sim_data (xr.DataArray): Données simulées (ex: dimensions [time, lat, lon])
        obs_data (xr.DataArray): Données observées (ex: dimensions [time, lat, lon])
        
    Returns:
        xr.DataArray: Carte de corrélation 2D [lat, lon]
    """
    logger.info(f"Computing spatial correlation for {sim_data.name}")
    
    # S'assurer que le temps est aligné
    sim_aligned, obs_aligned = xr.align(sim_data, obs_data, join="inner")
    
    # Calcul de la corrélation (cov(x,y) / (std(x)*std(y)))
    sim_mean = sim_aligned.mean(dim='time', skipna=True)
    obs_mean = obs_aligned.mean(dim='time', skipna=True)
    
    sim_anom = sim_aligned - sim_mean
    obs_anom = obs_aligned - obs_mean
    
    cov = (sim_anom * obs_anom).mean(dim='time', skipna=True)
    sim_std = sim_aligned.std(dim='time', skipna=True)
    obs_std = obs_aligned.std(dim='time', skipna=True)
    
    corr = cov / (sim_std * obs_std)
    corr.name = f"{sim_data.name}_correlation"
    
    return corr

def compute_anomaly_correlation(sim_data: xr.DataArray, obs_data: xr.DataArray) -> xr.DataArray:
    """
    Calcule la corrélation d'anomalie pixel par pixel.
    L'anomalie est définie ici par rapport à la moyenne climatologique mensuelle.
    """
    logger.info(f"Computing spatial anomaly correlation for {sim_data.name}")
    
    sim_aligned, obs_aligned = xr.align(sim_data, obs_data, join="inner")
    
    # Grouper par mois pour calculer la climatologie
    sim_clim = sim_aligned.groupby('time.month').mean('time')
    obs_clim = obs_aligned.groupby('time.month').mean('time')
    
    # Calcul des anomalies
    sim_anom = sim_aligned.groupby('time.month') - sim_clim
    obs_anom = obs_aligned.groupby('time.month') - obs_clim
    
    # La corrélation d'anomalie est la corrélation simple appliquée sur les anomalies
    return compute_spatial_correlation(sim_anom, obs_anom)

