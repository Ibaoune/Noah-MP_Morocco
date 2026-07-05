"""
diagnostics/assimilation/adapter.py
=====================================
Adaptateur entre la nouvelle architecture (Recipe/Experiment)
et le module src/assimilation_diagnostics/ préservé.

PRINCIPE :
  Ce module construit un `compat_config` compatible avec l'interface
  attendue par les fonctions run_*(config, da_dir, out_dir) du module
  assimilation_diagnostics/ et les appelle directement.

  Aucune ligne de diag_coverage.py, diag_innovations.py,
  diag_seasonal_increments.py, diag_spread.py n'est modifiée.

UTILISATION :
  L'adaptateur est appelé par runner.py quand la recette active
  le diagnostic "assimilation".
"""
import os
import sys
import copy
import logging
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

# Chemin absolu vers le module assimilation_diagnostics (préservé)
_THIS_DIR = Path(__file__).parent
_POSTPROC_SRC = _THIS_DIR.parent.parent.parent  # scripts/postproc/src/
ASSIMILATION_DIAGS_DIR = _POSTPROC_SRC / "assimilation_diagnostics"


def _add_assimilation_diags_to_path():
    """
    Ajoute temporairement assimilation_diagnostics/ au sys.path
    pour permettre les imports locaux (from utils import ...).
    """
    diags_path = str(ASSIMILATION_DIAGS_DIR)
    if diags_path not in sys.path:
        sys.path.insert(0, diags_path)


def _load_assimilation_global_config() -> Dict:
    """Charge le global.yaml du module assimilation_diagnostics."""
    # Import conditionnel pour éviter les effets de bord au démarrage
    _add_assimilation_diags_to_path()
    from utils import load_config  # noqa: from assimilation_diagnostics/utils.py
    global_cfg_path = ASSIMILATION_DIAGS_DIR / "configs" / "global.yaml"
    if global_cfg_path.exists():
        return load_config(str(global_cfg_path))
    return {}


def _load_diag_config(diag_name: str) -> Dict:
    """Charge le YAML de configuration d'un diagnostic spécifique."""
    _add_assimilation_diags_to_path()
    from utils import load_config  # noqa
    diag_cfg_path = ASSIMILATION_DIAGS_DIR / "configs" / "diagnostics" / f"{diag_name}.yaml"
    if diag_cfg_path.exists():
        return load_config(str(diag_cfg_path))
    logger.warning(f"Diagnostic config not found: {diag_cfg_path}")
    return {}


def _build_compat_config(
    experiment_id: str,
    experiment_label: str,
    da_path_abs: str,
    out_dir: str,
    recipe_diag_cfg: Dict,
    global_cfg_override: Dict
) -> Dict:
    """
    Construit un dictionnaire de configuration compatible avec
    le format attendu par assimilation_diagnostics/main.py.

    Ce config fusionne :
      - le global.yaml du module assimilation_diagnostics
      - les paramètres de la recette (dates, saisons)
      - les overrides nécessaires (chemins, labels)
    """
    # Charger la config globale du module assimilation_diagnostics
    base_cfg = _load_assimilation_global_config()

    # Surcharger project_root et output_dir
    base_cfg['project_root'] = global_cfg_override.get('_project_root', '')
    base_cfg['output_dir'] = out_dir  # Chemin absolu depuis la recette

    # Paramètres d'expérience
    base_cfg['experiment_name'] = experiment_id
    base_cfg['da_dir'] = os.path.relpath(
        da_path_abs, global_cfg_override.get('_project_root', '/')
    )

    # Dates depuis la recette
    year = recipe_diag_cfg.get('year', 2016)
    base_cfg['start_date'] = f"{year}-01-01"
    base_cfg['end_date'] = f"{year}-12-31"

    # Saisons depuis la recette
    seasons = recipe_diag_cfg.get('seasons', {})
    if seasons:
        base_cfg['seasons'] = {
            'wet_season': seasons.get('wet_season', [12, 1, 2]),
            'dry_season': seasons.get('dry_season', [6, 7, 8]),
        }

    return base_cfg


def _deep_merge_into(base: Dict, override: Dict) -> Dict:
    """Fusion récursive."""
    result = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = _deep_merge_into(result[key], value)
        else:
            result[key] = value
    return result


def _stylize_diagnostic_config(run_cfg: Dict, diag_name: str, exp_id: str, exp_label: str, out_dir: str):
    """
    Overwrites the legacy config dictionary to enforce unified colorbars, limits, and dynamic titles.
    Also creates a metadata mapping for the PDF generator.
    """
    incr_bounds = [-1.5, -1.2, -0.9, -0.6, -0.3, 0.0, 0.3, 0.6, 0.9, 1.2, 1.5]
    
    metadata_map = {
        "mean_innovation_map": {
            "title": f"Mean SMAP innovation, observation minus forecast — {exp_label}, NorthMor, 2016",
            "caption": "Mean innovation computed as observation minus forecast. Positive values indicate that SMAP is wetter than the model forecast; negative values indicate that SMAP is drier.",
            "file_suffix": "innovation_map"
        },
        "mean_increment_map": {
            "title": f"Mean SMAP analysis increment, analysis minus forecast — {exp_label}, NorthMor, 2016",
            "caption": "Mean analysis increment computed as analysis minus forecast. Positive values indicate wetting corrections; negative values indicate drying corrections applied by the EnKF.\nColorbar limits: robust symmetric bounds [-1.5e-3, 1.5e-3].",
            "bounds": incr_bounds,
            "cmap": "RdBu_r",
            "file_suffix": "increment_map"
        },
        "increment_histogram": {
            "title": f"Distribution of SMAP analysis increments — {exp_label}, NorthMor, 2016",
            "caption": "Distribution of all SMAP analysis increments over the domain and year. The mean and median indicate whether the assimilation applies a systematic wetting or drying correction.",
            "file_suffix": "increment_histogram"
        },
        "seasonal_increment_wet_dry": {
            "title": f"Wet- and dry-season SMAP analysis increments — {exp_label}, NorthMor, 2016",
            "caption": "Seasonal mean increments during wet and dry seasons. This diagnostic shows whether the assimilation correction depends on seasonal hydroclimatic conditions.\nWet season = Nov, Dec, Jan, Feb, Mar, Apr\nDry season = May, Jun, Jul, Aug, Sep, Oct\nColorbar limits: robust symmetric bounds [-1.5e-3, 1.5e-3].",
            "bounds": incr_bounds,
            "cmap": "RdBu_r",
            "file_suffix": "seasonal_increments"
        },
        "assimilation_observations_map": {
            "title": f"Spatial distribution of assimilated SMAP observations — {exp_label}, NorthMor, 2016",
            "caption": "Number of assimilated SMAP observations per grid cell during January–December 2016. Higher values indicate more frequent valid SMAP updates.",
            "file_suffix": "obs_count"
        },
        "assimilation_frequency_map": {
            "title": f"Monthly SMAP assimilation frequency — {exp_label}, NorthMor, 2016",
            "caption": "Spatial assimilation frequency and monthly total number of assimilated observations. This diagnostic identifies spatial and temporal gaps in SMAP availability.",
            "file_suffix": "assim_frequency"
        },
        "spread_diagnostics_consistency_check": {
            "title": f"Spread diagnostic consistency check — {exp_label}, NorthMor, 2016",
            "caption": "Technical quality-control diagnostic used to verify the consistency of masks, observation-space uncertainty fields, and model-state spread fields. This figure should not be interpreted as hydrological validation.",
            "file_suffix": "spread_consistency"
        },
        "prior_posterior_spread_comparison": {
            "title": f"Forecast uncertainty and model-state spread — {exp_label}, NorthMor, 2016",
            "caption": "Technical quality-control diagnostic used to verify the consistency of masks, observation-space uncertainty fields, and model-state spread fields. This figure should not be interpreted as hydrological validation.",
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
        run_cfg[cfg_key]['title']['main'] = meta['title']
        run_cfg[cfg_key]['title']['subtitle'] = ""
        run_cfg[cfg_key]['title']['main_fontsize'] = 9 # Reduce size to fit
        
        if 'bounds' in meta:
            if 'colorbar' not in run_cfg[cfg_key]: run_cfg[cfg_key]['colorbar'] = {}
            run_cfg[cfg_key]['colorbar']['bounds'] = meta['bounds']
            
        if 'cmap' in meta:
            if 'colormap' not in run_cfg[cfg_key]: run_cfg[cfg_key]['colormap'] = {}
            run_cfg[cfg_key]['colormap']['name'] = meta['cmap']
            run_cfg[cfg_key]['colormap']['reverse'] = False
            
        # Write JSON metadata alongside
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
    """
    Point d'entrée principal de l'adaptateur.

    Paramètres
    ----------
    recipe            : Objet Recipe (lis_postproc.core.recipes.Recipe)
    experiments_catalog: dict brut des expériences (depuis config.py)
    global_cfg        : Config globale chargée (depuis config.py)
    out_dir           : Dossier de sortie résolu depuis la recette
    dry_run           : Si True, affiche le plan sans exécuter

    Retourne
    --------
    Liste des fichiers PNG générés.
    """
    generated_files = []

    assimil_cfg = recipe.get_assimilation_config() if hasattr(recipe, 'get_assimilation_config') \
        else recipe.diagnostics.get('assimilation', {})

    if not assimil_cfg.get('enabled', False):
        logger.info("Assimilation diagnostics: disabled in recipe")
        return generated_files

    # Diagnostics à lancer
    active_diagnostics = assimil_cfg.get('active_diagnostics',
                                          ['coverage', 'innovations',
                                           'seasonal_increments', 'spread'])

    # Expériences DA à traiter
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

    # Ajouter assimilation_diagnostics/ au path pour les imports
    _add_assimilation_diags_to_path()

    # Import des fonctions de diagnostics (depuis le module préservé)
    try:
        from diagnostics.diag_coverage import run_coverage
        from diagnostics.diag_innovations import run_innovations
        from diagnostics.diag_seasonal_increments import run_seasonal_increments
        from diagnostics.diag_spread import run_spread
    except ImportError as e:
        logger.error(f"Cannot import assimilation diagnostics modules: {e}")
        logger.error(f"Expected location: {ASSIMILATION_DIAGS_DIR}/diagnostics/")
        return generated_files

    available_diags = {
        'coverage': run_coverage,
        'innovations': run_innovations,
        'seasonal_increments': run_seasonal_increments,
        'spread': run_spread,
    }

    # Paramètres de dates depuis la recette
    year = getattr(recipe, 'year', 2016)
    recipe_params = {
        'year': year,
        'seasons': assimil_cfg.get('seasons', {}),
    }

    # Lancer les diagnostics pour chaque expérience DA
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

        # Construire le compat_config
        compat_config = _build_compat_config(
            experiment_id=exp_id,
            experiment_label=exp_label,
            da_path_abs=da_path,
            out_dir=exp_out_dir,
            recipe_diag_cfg=recipe_params,
            global_cfg_override=global_cfg,
        )

        # Convertir les dates en objets datetime (attendus par les diag_*.py)
        compat_config['start_date'] = datetime.strptime(
            compat_config['start_date'], '%Y-%m-%d'
        )
        compat_config['end_date'] = datetime.strptime(
            compat_config['end_date'], '%Y-%m-%d'
        )

        # Lancer chaque diagnostic demandé
        for diag_name in active_diagnostics:
            if diag_name not in available_diags:
                logger.warning(f"Unknown diagnostic: {diag_name}")
                continue

            # Charger le YAML de config du diagnostic et fusionner
            diag_extra_cfg = _load_diag_config(diag_name)
            run_cfg = _deep_merge_into(compat_config, diag_extra_cfg)
            
            # Injecter nos styles V2 (colorbars robustes, titres, metadonnées JSON)
            _stylize_diagnostic_config(run_cfg, diag_name, exp_id, exp_label, exp_out_dir)

            logger.info(f"  → Running: {diag_name} for {exp_id}")
            try:
                available_diags[diag_name](run_cfg, da_path, exp_out_dir)
            except Exception as e:
                logger.error(f"  ERROR in {diag_name} for {exp_id}: {e}")
                import traceback
                logger.debug(traceback.format_exc())
                
        # Collect generated files for the PDF generator
        import glob
        for ext in ('*.json', '*.png'):
            generated_files.extend(glob.glob(os.path.join(exp_out_dir, ext)))

    return list(set(generated_files))


def get_dry_run_summary(recipe, experiments_catalog: Dict) -> List[str]:
    """
    Retourne un résumé textuel du plan d'assimilation sans exécuter.
    Utilisé par le mode --dry-run du CLI.
    """
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
    lines.append(f"    Module: src/assimilation_diagnostics/ (preserved, unchanged)")
    lines.append(f"    Active diagnostics: {active}")
    lines.append(f"    DA experiments ({len(da_exps)}):")
    for exp_id in da_exps:
        exp_data = experiments_catalog.get(exp_id, {})
        path = exp_data.get('path_abs', 'null')
        status = "✓ available" if path and os.path.isdir(path) else "✗ not available"
        lines.append(f"      - {exp_id} ({status})")

    return lines
