# Author: M. EL Aabaribaoune (@um6p)

"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: diagnostics.assimilation.adapter
Description: Adapter for the assimilation diagnostics suite.
================================================================================
"""
import os
import copy
import logging
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any




logger = logging.getLogger(__name__)

# Base path for diagnostics configs if they were preserved.
# Since we archived configs/ in the bash script, let's assume global_cfg overrides are sufficient,
# or we can just return empty dicts for legacy configs.
def _load_assimilation_global_config() -> Dict:
    """Returns a dummy global config, overridden by the actual global_cfg."""
    return {}

def _load_diag_config(diag_name: str) -> Dict:
    """Returns a dummy diag config, overridden dynamically."""
    return {}

def _build_compat_config(
    experiment_id: str,
    experiment_label: str,
    da_path_abs: str,
    out_dir: str,
    recipe_diag_cfg: Dict,
    global_cfg_override: Dict
) -> Dict:
    base_cfg = _load_assimilation_global_config()

    base_cfg['project_root'] = global_cfg_override.get('_project_root', '')
    base_cfg['output_dir'] = out_dir

    base_cfg['experiment_name'] = experiment_id
    base_cfg['da_dir'] = os.path.relpath(
        da_path_abs, global_cfg_override.get('_project_root', '/')
    )

    year = recipe_diag_cfg.get('year', 2016)
    period = recipe_diag_cfg.get('period', str(year))
    
    if "-" in str(period):
        start_year, end_year = str(period).split('-')
        base_cfg['start_date'] = f"{start_year}-01-01"
        base_cfg['end_date'] = f"{end_year}-12-31"
    else:
        base_cfg['start_date'] = f"{period}-01-01"
        base_cfg['end_date'] = f"{period}-12-31"
        
    base_cfg['period'] = str(period)

    seasons = recipe_diag_cfg.get('seasons', {})
    if seasons:
        base_cfg['seasons'] = {
            'wet_season': seasons.get('wet_season', [12, 1, 2]),
            'dry_season': seasons.get('dry_season', [6, 7, 8]),
        }

    return base_cfg


def _deep_merge_into(base: Dict, override: Dict) -> Dict:
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge_into(result[key], value)
        else:
            result[key] = value
    return result


def _stylize_diagnostic_config(run_cfg: Dict, diag_name: str, exp_id: str, exp_label: str, out_dir: str, domain_label: str):
    incr_bounds = [-1.5, -1.2, -0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.5]
    period = run_cfg.get('period', '2016')
    
    metadata_map = {
        "mean_innovation_map": {
            "title": f"Mean SMAP innovation, observation minus forecast — {exp_label}, {domain_label}, {period}",
            "caption": "Mean innovation computed as observation minus forecast.",
            "file_suffix": "innovation_map"
        },
        "mean_increment_map": {
            "title": f"Mean SMAP analysis increment — {exp_label}, {domain_label}, {period}",
            "caption": "Mean analysis increment computed as analysis minus forecast.",
            "bounds": incr_bounds,
            "cmap": "RdBu_r",
            "file_suffix": "increment_map"
        },
        "increment_histogram": {
            "title": f"Distribution of SMAP analysis increments — {exp_label}, {domain_label}, {period}",
            "caption": "Distribution of all SMAP analysis increments.",
            "file_suffix": "increment_histogram"
        },
        "seasonal_increment_wet_dry": {
            "title": f"Wet- and dry-season SMAP analysis increments — {exp_label}, {domain_label}, {period}",
            "caption": "Seasonal mean increments during wet and dry seasons.",
            "bounds": incr_bounds,
            "cmap": "RdBu_r",
            "file_suffix": "seasonal_increments"
        },
        "assimilation_observations_map": {
            "title": f"Spatial distribution of assimilated SMAP observations — {exp_label}, {domain_label}, {period}",
            "caption": "Number of assimilated SMAP observations per grid cell.",
            "file_suffix": "obs_count"
        },
        "assimilation_frequency_map": {
            "title": f"Monthly SMAP assimilation frequency — {exp_label}, {domain_label}, {period}",
            "caption": "Spatial assimilation frequency.",
            "file_suffix": "assim_frequency"
        },
        "spread_diagnostics_consistency_check": {
            "title": f"Spread diagnostic consistency check — {exp_label}, {domain_label}, {period}",
            "caption": "Technical quality-control diagnostic.",
            "file_suffix": "spread_consistency"
        },
        "prior_posterior_spread_comparison": {
            "title": f"Forecast uncertainty and model-state spread — {exp_label}, {domain_label}, {period}",
            "caption": "Technical quality-control diagnostic.",
            "file_suffix": "spread_comparison"
        }
    }
    
    for cfg_key, meta in metadata_map.items():
        if cfg_key not in run_cfg:
            run_cfg[cfg_key] = {}
        
        filename = f"{exp_id}_{meta['file_suffix']}.png"
        if 'output' not in run_cfg[cfg_key]: run_cfg[cfg_key]['output'] = {}
        run_cfg[cfg_key]['output']['filename'] = filename
        
        if 'title' not in run_cfg[cfg_key]: run_cfg[cfg_key]['title'] = {}
        run_cfg[cfg_key]['title']['main'] = ""
        run_cfg[cfg_key]['title']['subtitle'] = ""
        run_cfg[cfg_key]['title']['main_fontsize'] = 9 
        
        if 'bounds' in meta:
            if 'colorbar' not in run_cfg[cfg_key]: run_cfg[cfg_key]['colorbar'] = {}
            run_cfg[cfg_key]['colorbar']['bounds'] = meta['bounds']
            
        if 'cmap' in meta:
            if 'colormap' not in run_cfg[cfg_key]: run_cfg[cfg_key]['colormap'] = {}
            run_cfg[cfg_key]['colormap']['name'] = meta['cmap']
            run_cfg[cfg_key]['colormap']['reverse'] = False
            
        json_path = os.path.join(out_dir, f"{exp_id}_{meta['file_suffix']}.json")
        with open(json_path, 'w') as f:
            json.dump({
                "experiment": exp_id,
                "experiment_label": exp_label,
                "title": meta['title'],
                "caption": meta['caption'],
                "filename": filename,
                "diagnostic_type": diag_name
            }, f, indent=2)


def run_assimilation_diagnostics(
    recipe,
    experiments_catalog: Dict,
    global_cfg: Dict,
    out_dir: str,
    dry_run: bool = False
) -> List[str]:
    generated_files = []

    assimil_cfg = recipe.get_assimilation_config() if hasattr(recipe, 'get_assimilation_config') \
        else recipe.diagnostics.get('assimilation', {})

    if not assimil_cfg.get('enabled', False):
        logger.info("Assimilation diagnostics: disabled in recipe")
        return generated_files

    active_diagnostics = assimil_cfg.get('active_diagnostics',
                                          ['coverage', 'innovations',
                                           'seasonal_increments', 'spread'])

    da_experiments = assimil_cfg.get('da_experiments', recipe.get_da_experiments()
                                      if hasattr(recipe, 'get_da_experiments')
                                      else [])

    logger.info(f"Assimilation diagnostics: {active_diagnostics} "
                f"for experiments: {da_experiments}")

    if dry_run:
        print(f"\n  [DRY-RUN] Assimilation diagnostics:")
        print(f"    Diagnostics: {active_diagnostics}")
        print(f"    DA experiments: {da_experiments}")
        print(f"    Output dir: {out_dir}")
        return generated_files

    from .diag_coverage import run_coverage
    from .diag_innovations import run_innovations
    from .diag_seasonal_increments import run_seasonal_increments
    from .diag_spread import run_spread

    available_diags = {
        'coverage': run_coverage,
        'innovations': run_innovations,
        'seasonal_increments': run_seasonal_increments,
        'spread': run_spread,
    }

    year = getattr(recipe, 'year', 2016)
    period = getattr(recipe, 'period', str(year))
    recipe_params = {
        'year': year,
        'period': period,
        'seasons': assimil_cfg.get('seasons', {}),
    }

    for exp_id in da_experiments:
        if exp_id not in experiments_catalog:
            logger.warning(f"Experiment {exp_id} not in catalog, skipping")
            continue

        exp_data = experiments_catalog[exp_id]
        da_path = exp_data.get('path_abs')

        if da_path is None or not os.path.isdir(da_path):
            logger.warning(
                f"Experiment {exp_id}: path not available ({da_path}). Skipping."
            )
            continue

        exp_label = exp_data.get('label', exp_id)
        exp_out_dir = os.path.join(out_dir, exp_id)
        os.makedirs(exp_out_dir, exist_ok=True)

        logger.info(f"Running assimilation diagnostics for: {exp_id} → {exp_out_dir}")

        compat_config = _build_compat_config(
            experiment_id=exp_id,
            experiment_label=exp_label,
            da_path_abs=da_path,
            out_dir=exp_out_dir,
            recipe_diag_cfg=recipe_params,
            global_cfg_override=global_cfg,
        )

        compat_config['start_date'] = datetime.strptime(
            compat_config['start_date'], '%Y-%m-%d'
        )
        compat_config['end_date'] = datetime.strptime(
            compat_config['end_date'], '%Y-%m-%d'
        )

        for diag_name in active_diagnostics:
            if diag_name not in available_diags:
                logger.warning(f"Unknown diagnostic: {diag_name}")
                continue

            diag_extra_cfg = _load_diag_config(diag_name)
            run_cfg = _deep_merge_into(compat_config, diag_extra_cfg)
            
            domain_label = global_cfg.get('default_domain', 'Domain')
            _stylize_diagnostic_config(run_cfg, diag_name, exp_id, exp_label, exp_out_dir, domain_label)

            logger.info(f"  → Running: {diag_name} for {exp_id}")
            try:
                available_diags[diag_name](run_cfg, da_path, exp_out_dir)
            except Exception as e:
                logger.error(f"  ERROR in {diag_name} for {exp_id}: {e}")
                
        import glob
        for ext in ('*.json', '*.png'):
            generated_files.extend(glob.glob(os.path.join(exp_out_dir, ext)))

    return list(set(generated_files))


def get_dry_run_summary(recipe, experiments_catalog: Dict) -> List[str]:
    lines = []
    assimil_cfg = recipe.diagnostics.get('assimilation', {})

    if not assimil_cfg.get('enabled', False):
        lines.append("  Assimilation diagnostics: DISABLED")
        return lines

    active = assimil_cfg.get('active_diagnostics',
                              ['coverage', 'innovations', 'seasonal_increments', 'spread'])
    da_exps = assimil_cfg.get('da_experiments', recipe.get_da_experiments()
                              if hasattr(recipe, 'get_da_experiments') else [])

    lines.append(f"  Assimilation diagnostics: ENABLED")
    lines.append(f"    Module: src/diagnostics/assimilation/")
    lines.append(f"    Active diagnostics: {active}")
    lines.append(f"    DA experiments ({len(da_exps)}):")
    for exp_id in da_exps:
        exp_data = experiments_catalog.get(exp_id, {})
        path = exp_data.get('path_abs', 'null')
        status = " available" if path and os.path.isdir(path) else " not available"
        lines.append(f"      - {exp_id} ({status})")

    return lines
