# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: lis_postproc.utils.helpers
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
"""
utils/helpers.py — Fonctions utilitaires partagées
=====================================================
Wrappeurs et helpers qui réexportent ou complètent
les fonctions du module utils/ existant (masking, metrics, spatial_stats).
"""
import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Optional, List, Tuple

logger = logging.getLogger(__name__)

# Ajouter src/ au path pour accéder à utils/ existant
_SRC_DIR = Path(__file__).parent.parent.parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

try:
    from utils.masking import get_land_mask   # noqa
except ImportError:
    def get_land_mask(lat, lon):
        return np.ones((len(lat), len(lon)), dtype=bool)

try:
    from utils.metrics import compute_bias, compute_rmse  # noqa
except ImportError:
    def compute_bias(sim, obs):
        return float(np.nanmean(sim - obs))
    def compute_rmse(sim, obs):
        return float(np.sqrt(np.nanmean((sim - obs)**2)))

try:
    from utils.spatial_stats import compute_domain_mean  # noqa
except ImportError:
    def compute_domain_mean(data, mask=None):
        if mask is not None:
            return float(np.nanmean(data[mask]))
        return float(np.nanmean(data))


def robust_vmin_vmax(
    data: np.ndarray,
    percentiles: List[float] = [2, 98]
) -> Tuple[float, float]:
    """Calcule des limites robustes pour les colorbars."""
    valid = data[np.isfinite(data)]
    if len(valid) == 0:
        return 0.0, 1.0
    return float(np.percentile(valid, percentiles[0])), \
           float(np.percentile(valid, percentiles[1]))


def setup_logging(log_dir: Optional[str] = None, level: str = 'INFO'):
    """Configure le logging pour le framework."""
    import logging
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    handlers = [logging.StreamHandler()]

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        from datetime import datetime
        log_file = os.path.join(
            log_dir, f"postproc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )
    return logging.getLogger('lis_postproc')
