# Author: M. EL Aabaribaoune (@um6p)

"""
Module for computing and caching differences between experiments.
"""
import os
import logging
import numpy as np
from datetime import datetime
from typing import Dict, Any, Optional

from .experiment_fields import ExperimentFields, get_temporal_aggregation

logger = logging.getLogger(__name__)

class ExperimentDifferences:
    """
    Manager for computing and caching experiment differences.
    """
    def __init__(self, cache_dir: str, fields_manager: ExperimentFields):
        self.cache_dir = cache_dir
        self.fields_manager = fields_manager
        os.makedirs(self.cache_dir, exist_ok=True)

    def _generate_cache_key(self, exp1_id: str, exp2_id: str, var_id: str, start_date: datetime, end_date: datetime, agg_method: str = "daily") -> str:
        date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
        key = f"diff_{exp1_id}_minus_{exp2_id}_{var_id}_{date_str}_{agg_method}"
        return key

    def get_difference(self, exp_target: Dict[str, Any], exp_reference: Dict[str, Any], variable: Dict[str, Any], 
                       start_date: datetime, end_date: datetime, agg_method: str = "daily", force_recompute: bool = False) -> Optional[np.ndarray]:
        """
        Computes (exp_target - exp_reference) for the given variable and period.
        
        Example: DA-CDF minus OPL -> exp_target=DA-CDF, exp_reference=OPL
        """
        exp1_id = exp_target.get('id', exp_target.get('label', 'unknown'))
        exp2_id = exp_reference.get('id', exp_reference.get('label', 'unknown'))
        var_id = variable.get('variable_id', variable.get('short_name', 'unknown'))
        
        cache_key = self._generate_cache_key(exp1_id, exp2_id, var_id, start_date, end_date, agg_method)
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.npy")

        if not force_recompute and os.path.exists(cache_path):
            logger.info(f"Loading cached difference for {cache_key}")
            try:
                return np.load(cache_path)
            except Exception as e:
                logger.warning(f"Failed to load cache {cache_path}: {e}. Recomputing.")

        logger.info(f"Computing difference: {exp1_id} minus {exp2_id} for {var_id}")
        
        data_target = self.fields_manager.get_field(exp_target, variable, start_date, end_date, force_recompute)
        data_reference = self.fields_manager.get_field(exp_reference, variable, start_date, end_date, force_recompute)
        
        if data_target is None or data_reference is None:
            logger.warning(f"Cannot compute difference for {var_id}: Missing data for one or both experiments.")
            return None
            
        # Optional: apply temporal aggregation before difference (or after, it's linear for means, but better to do it explicitely)
        if agg_method != "daily":
            data_target = get_temporal_aggregation(data_target, agg_method)
            data_reference = get_temporal_aggregation(data_reference, agg_method)
            
        # Target minus Reference
        diff_data = data_target - data_reference
        
        try:
            np.save(cache_path, diff_data)
            logger.debug(f"Saved difference to cache: {cache_path}")
        except Exception as e:
            logger.warning(f"Failed to save cache to {cache_path}: {e}")
            
        return diff_data
