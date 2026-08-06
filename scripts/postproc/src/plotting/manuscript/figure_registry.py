# Author: M. EL Aabaribaoune (@um6p)

"""
Registry for mapping figure IDs to their builders.
"""
import logging
from typing import Callable, Dict

from src.plotting.panels.assimilation import build_assim_01
from src.plotting.panels.hydrology import build_sm_01, build_flux_01
from src.plotting.panels.drought import build_drought_01
from src.plotting.panels.runoff import build_runoff_01, build_gldas_01
from src.plotting.panels.water_balance import build_wb_01
from src.plotting.panels.propagation import build_prop_01

logger = logging.getLogger(__name__)

FIGURE_REGISTRY: Dict[str, Callable] = {
    'ASSIM-01': build_assim_01,
    'SM-01': build_sm_01,
    'FLUX-01': build_flux_01,
    'DROUGHT-01': build_drought_01,
    'RUNOFF-01': build_runoff_01,
    'GLDAS-01': build_gldas_01,
    'WB-01': build_wb_01,
    'PROP-01': build_prop_01,
}

def get_builder(figure_id: str) -> Callable:
    """Returns the builder function for a given figure ID."""
    if figure_id not in FIGURE_REGISTRY:
        raise ValueError(f"Figure ID {figure_id} not found in registry.")
    return FIGURE_REGISTRY[figure_id]
