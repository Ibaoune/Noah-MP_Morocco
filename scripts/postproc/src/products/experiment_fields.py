# Author: M. EL Aabaribaoune (@um6p)

"""
Module for retrieving and caching harmonized fields for experiments.
"""
import os
import logging
import hashlib
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

from src.io.lis import load_variable_for_experiment

logger = logging.getLogger(__name__)

class ExperimentFields:
    """
    Manager for computing and caching harmonized variable fields.
    """
    def __init__(self, cache_dir: str):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, exp_id: str, var_id: str, start_date: datetime, end_date: datetime) -> str:
        """Generates a unique cache key for the requested field."""
        date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        key = f"{exp_id}_{var_id}_{date_str}"
        return key

    def get_field(self, experiment: Dict[str, Any], variable: Dict[str, Any], start_date: datetime, end_date: datetime, force_recompute: bool = False) -> Optional[np.ndarray]:
        """
        Retrieves the harmonized field, using cache if available.
        """
        exp_id = experiment.get('id', experiment.get('label', 'unknown'))
        var_id = variable.get('variable_id', variable.get('short_name', 'unknown'))
        
        cache_key = self._generate_cache_key(exp_id, var_id, start_date, end_date)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.npy")

        if not force_recompute and os.path.exists(cache_path):
            logger.info(f"Loading cached field for {cache_key}")
            try:
                return np.load(cache_path)
            except Exception as e:
                logger.warning(f"Failed to load cache {cache_path}: {e}. Recomputing.")

        logger.info(f"Computing field for {cache_key}")
        # Note: experiment and variable can be dictionaries or objects.
        # The lis module handles dictionary access if needed, but we should make sure we pass what it expects.
        data = load_variable_for_experiment(experiment, variable, start_date, end_date)
        
        if data is not None:
            try:
                np.save(cache_path, data)
                logger.debug(f"Saved field to cache: {cache_path}")
            except Exception as e:
                logger.warning(f"Failed to save cache to {cache_path}: {e}")
        
        return data

def get_temporal_aggregation(data: np.ndarray, method: str) -> np.ndarray:
    """
    Applies temporal aggregation on the (T, lat, lon) array.
    Supports: daily, monthly, annual_mean, cumulative.
    Note: currently assumes input is daily.
    """
    if data is None:
        return None
        
    if method == 'daily':
        return data
    elif method == 'annual_mean' or method == 'mean':
        return np.nanmean(data, axis=0)
    elif method == 'cumulative' or method == 'sum':
        return np.nansum(data, axis=0)
    else:
        logger.warning(f"Temporal aggregation '{method}' not fully implemented, returning raw data.")
        return data
