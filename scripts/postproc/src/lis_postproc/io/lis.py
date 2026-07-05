"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.io.lis
Description: Input/Output operations for LIS and HyMAP NetCDF datasets.
================================================================================
"""
"""
io/lis.py — Wrapper autour de src/utils/io_lis.py
====================================================
Réexporte les fonctions de lecture des fichiers LIS NetCDF
depuis le module utils/ existant, en ajoutant des helpers
compatibles avec les nouvelles classes Variable et Experiment.
"""
import os
import sys
import logging
import numpy as np
from pathlib import Path
from typing import Optional, List

logger = logging.getLogger(__name__)

# Ajouter src/ au path pour accéder à utils/io_lis.py existant
_SRC_DIR = Path(__file__).parent.parent.parent  # scripts/postproc/src/
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

try:
    from utils.io_lis import get_lis_files, load_lis_variable  # noqa
    logger.debug("io_lis: imported from utils/io_lis.py")
except ImportError:
    logger.warning("Could not import utils/io_lis.py — defining stubs")

    def get_lis_files(output_dir, start_date, end_date):
        """Stub — retourne une liste vide si io_lis.py non disponible."""
        return []

    def load_lis_variable(files, var_name, extract_layer=None):
        """Stub — retourne None si io_lis.py non disponible."""
        return None


def get_lis_variable_unit(files, var_name):
    if not files:
        return None
    try:
        import netCDF4 as nc
        ds = nc.Dataset(files[0], 'r')
        if var_name in ds.variables:
            var = ds.variables[var_name]
            unit = var.units if hasattr(var, 'units') else None
        else:
            unit = None
        ds.close()
        return unit
    except Exception:
        return None

def load_variable_for_experiment(experiment, variable, start_date, end_date):
    """
    Charge une variable LIS pour une expérience donnée.

    Parameters
    ----------
    experiment  : dict brut ou objet Experiment (avec path_abs)
    variable    : objet Variable (avec lis_variable_names, operation, etc.)
    start_date  : datetime
    end_date    : datetime

    Retourne
    --------
    np.ndarray de forme (T, nlat, nlon) ou None si erreur
    """
    from datetime import datetime as dt

    path_abs = (
        experiment.get('path_abs') if isinstance(experiment, dict)
        else getattr(experiment, 'path_abs', None)
    )

    if path_abs is None or not os.path.isdir(path_abs):
        logger.warning(f"Experiment path not available: {path_abs}")
        return None

    files = get_lis_files(path_abs, start_date, end_date)
    if not files:
        logger.warning(f"No LIS files found in {path_abs}")
        return None

    var_names = (
        variable.lis_variable_names if hasattr(variable, 'lis_variable_names')
        else variable.get('lis_variable_names', [])
    )
    operation = (
        variable.operation if hasattr(variable, 'operation')
        else variable.get('operation', 'direct')
    )
    scale_factor = (
        variable.scale_factor if hasattr(variable, 'scale_factor')
        else variable.get('scale_factor', 1.0)
    )

    # Unit auto-conversion for fluxes to mm/day
    unit = variable.unit if hasattr(variable, 'unit') else variable.get('unit', '')
    nc_unit = get_lis_variable_unit(files, var_names[0]) if var_names else None
    
    if scale_factor == 1.0 and unit in ['mm/day', 'mm day-1'] and nc_unit:
        if nc_unit.strip() in ['kg m-2 s-1', 'kg/m2/s']:
            scale_factor = 86400.0
            logger.info(f"[{getattr(variable, 'variable_id', 'unknown')}] Auto-conversion: NetCDF '{nc_unit}' -> target '{unit}' (x 86400).")
        elif nc_unit.strip() in ['W m-2', 'W/m2']:
            scale_factor = 86400.0 / 2.45e6
            logger.info(f"[{getattr(variable, 'variable_id', 'unknown')}] Auto-conversion: NetCDF '{nc_unit}' -> target '{unit}' (x 86400/2.45e6).")
        elif nc_unit.strip() in ['mm/day', 'mm day-1']:
            logger.info(f"[{getattr(variable, 'variable_id', 'unknown')}] Unit matches '{unit}'. No conversion needed.")
        else:
            logger.warning(f"[{getattr(variable, 'variable_id', 'unknown')}] Unknown unit '{nc_unit}' for target '{unit}'. No conversion applied.")

    layer_yaml = (
        variable.layer if hasattr(variable, 'layer')
        else variable.get('layer')
    )
    # Convert from 1-based (YAML) to 0-based (Python index)
    layer_idx = layer_yaml - 1 if layer_yaml is not None else None

    if operation == 'direct' or operation is None:
        data = load_lis_variable(files, var_names[0], extract_layer=layer_idx)
    elif operation == 'extract_layer':
        data = load_lis_variable(files, var_names[0], extract_layer=layer_idx)
    elif operation == 'sum':
        arrays = [load_lis_variable(files, vn) for vn in var_names]
        arrays = [a for a in arrays if a is not None]
        data = np.sum(arrays, axis=0) if arrays else None
    elif operation == 'layer_mean':
        layers_yaml = (
            variable.layers if hasattr(variable, 'layers')
            else variable.get('layers', [1])
        )
        layers_idx = [L - 1 for L in layers_yaml]
        arrays = [load_lis_variable(files, var_names[0], extract_layer=i)
                  for i in layers_idx]
        arrays = [a for a in arrays if a is not None]
        data = np.mean(arrays, axis=0) if arrays else None
    elif operation == 'weighted_mean':
        # Used for Root-zone soil moisture
        layers_config = (
            variable.layers if hasattr(variable, 'layers')
            else variable.get('layers', [])
        )
        arrays = []
        weights = []
        logger.info(f"[{getattr(variable, 'variable_id', 'unknown')}] Processing 'weighted_mean':")
        for l_cfg in layers_config:
            l_idx = l_cfg['layer'] - 1
            l_depth = l_cfg['depth']
            logger.info(f"  -> YAML layer {l_cfg['layer']} mapped to Python index {l_idx} (depth: {l_depth})")
            arr = load_lis_variable(files, var_names[0], extract_layer=l_idx)
            if arr is not None:
                arrays.append(arr)
                weights.append(l_depth)
                
        if arrays and weights:
            # Normalize weights
            weights = np.array(weights)
            norm_weights = weights / weights.sum()
            logger.info(f"  -> Normalized weights: {norm_weights}")
            
            # Weighted sum
            data = np.zeros_like(arrays[0])
            for arr, w in zip(arrays, norm_weights):
                data += arr * w
        else:
            data = None
    else:
        logger.warning(f"Unknown operation: {operation}, falling back to direct")
        data = load_lis_variable(files, var_names[0], extract_layer=layer_idx)

    if data is not None:
        data = np.where(data <= -9000, np.nan, data)
        if scale_factor != 1.0:
            data = data * scale_factor

    return data
