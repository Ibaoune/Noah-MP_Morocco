# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: diagnostics.domain.adapter
Description: Geospatial mapping and domain characterization.
================================================================================
"""
import os
import sys
import logging
from pathlib import Path



logger = logging.getLogger(__name__)

def run_domain_diagnostics(recipe, global_cfg, out_dir, dry_run=False):
    """
    Executes the domain mapping script.
    """
    generated_files = []
    
    if dry_run:
        print(f"\n  [DRY-RUN] Domain diagnostics:")
        print(f"    Output dir: {out_dir}")
        return generated_files

    project_root = global_cfg.get('_project_root', str(Path(__file__).resolve().parent.parent.parent.parent.parent))
    
    from .plot_domain_map import plot_all_domain_maps

    logger.info(f"Running domain diagnostics → {out_dir}")
    try:
        files = plot_all_domain_maps(out_dir, project_root)
        if files:
            generated_files.extend(files)
    except Exception as e:
        logger.error(f"Error in plot_all_domain_maps: {e}")

    return list(set(generated_files))
