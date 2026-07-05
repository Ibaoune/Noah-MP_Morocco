"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.core.config
Description: Core framework logic: configuration, variables, and experiment parsing.
================================================================================
"""
"""
core/config.py — YAML Loading and Validation
============================================
Functions to load, validate, and resolve paths for:
  - global.yaml
  - experiments.yaml
  - configs/variables/*.yaml
  - configs/recipes/*.yaml
"""
import os
import glob
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


# ============================================================
# Low-level loading functions
# ============================================================

def load_yaml(filepath: str) -> Dict[str, Any]:
    """Loads a YAML file and returns a dictionary."""
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"YAML file not found: {filepath}")
    with open(filepath, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    if data is None:
        return {}
    return data


def deep_merge(base: Dict, override: Dict) -> Dict:
    """Recursively merges override into base (override takes precedence)."""
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and key in result and isinstance(result[key], dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result


# ============================================================
# Main configurations loading
# ============================================================

def load_global_config(global_yaml_path: str) -> Dict[str, Any]:
    """
    Loads configs/global.yaml.
    Resolves relative paths to absolute paths based on project_root.
    """
    cfg = load_yaml(global_yaml_path)
    project_root = cfg.get('paths', {}).get('project_root', '')
    cfg['_project_root'] = project_root
    # Root of the postproc directory (parent of the configs/ directory)
    postproc_dir = str(Path(global_yaml_path).parent.parent)
    cfg['_postproc_dir'] = postproc_dir
    logger.info(f"Global config loaded: project_root={project_root}")
    return cfg


def load_experiments_catalog(experiments_yaml_path: str,
                              global_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads configs/experiments.yaml.
    Resolves experiment paths relative to project_root.
    """
    catalog_raw = load_yaml(experiments_yaml_path)
    project_root = global_cfg.get('_project_root', '')
    experiments = catalog_raw.get('experiments', {})

    resolved = {}
    for exp_id, exp_data in experiments.items():
        exp = dict(exp_data)
        exp['id'] = exp_id
        # Resolve to absolute path if not null
        if exp.get('path') is not None:
            raw_path = exp['path']
            if not os.path.isabs(raw_path):
                exp['path_abs'] = os.path.join(project_root, raw_path)
            else:
                exp['path_abs'] = raw_path
        else:
            exp['path_abs'] = None
        resolved[exp_id] = exp

    logger.info(f"Experiments catalog loaded: {len(resolved)} experiments")
    return resolved


def load_recipe(recipe_yaml_path: str,
                global_cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Loads a recipe from configs/recipes/*.yaml.
    Resolves output paths relative to the postproc/ directory.
    """
    recipe = load_yaml(recipe_yaml_path)
    postproc_dir = global_cfg.get('_postproc_dir', '.')

    # Resolve output paths
    outputs = recipe.get('outputs', {})
    for key in ['figure_dir', 'metrics_dir', 'table_dir', 'pdf_report']:
        if key in outputs and outputs[key] is not None:
            rel = outputs[key]
            if not os.path.isabs(rel):
                outputs[key] = os.path.join(postproc_dir, rel)
    recipe['outputs'] = outputs

    logger.info(f"Recipe loaded: {recipe.get('recipe_id', 'unknown')}")
    return recipe


def load_variable(variable_id: str,
                  variables_dir: str) -> Dict[str, Any]:
    """
    Loads the YAML configuration for a variable from configs/variables/{variable_id}.yaml.
    """
    yaml_path = os.path.join(variables_dir, f"{variable_id}.yaml")
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(
            f"Variable config not found: {yaml_path}\n"
            f"Available: {list_available_variables(variables_dir)}"
        )
    var_cfg = load_yaml(yaml_path)
    logger.debug(f"Variable loaded: {variable_id}")
    return var_cfg


def load_all_variables_for_recipe(recipe: Dict[str, Any],
                                   variables_dir: str) -> Dict[str, Dict]:
    """Loads all variable YAMLs referenced in a recipe."""
    variables = {}
    for var_id in recipe.get('variables', []):
        variables[var_id] = load_variable(var_id, variables_dir)
    return variables


# ============================================================
# Discovery functions
# ============================================================

def list_available_experiments(experiments_catalog: Dict[str, Any]) -> list:
    """Lists available experiment IDs (where path is not null)."""
    available = []
    for exp_id, exp in experiments_catalog.items():
        if exp.get('path_abs') is not None:
            available.append(exp_id)
    return available


def list_available_variables(variables_dir: str) -> list:
    """Lists all available variables in configs/variables/."""
    yamls = glob.glob(os.path.join(variables_dir, '*.yaml'))
    return [os.path.splitext(os.path.basename(f))[0] for f in sorted(yamls)]


def list_available_recipes(recipes_dir: str) -> list:
    """Lists all available recipes in configs/recipes/."""
    yamls = glob.glob(os.path.join(recipes_dir, '*.yaml'))
    return [os.path.splitext(os.path.basename(f))[0] for f in sorted(yamls)]


# ============================================================
# Validation
# ============================================================

def validate_recipe_against_catalog(recipe: Dict[str, Any],
                                     experiments_catalog: Dict[str, Any],
                                     variables_dir: str) -> list:
    """
    Validates a recipe and returns a list of error/warning messages.
    Checks:
      - That all referenced experiments exist in the catalog
      - That all experiments have a non-null path
      - That all paths exist on the disk
      - That all variables have a corresponding YAML
    """
    errors = []
    warnings = []

    recipe_exps = recipe.get('experiments', [])
    for exp_id in recipe_exps:
        if exp_id not in experiments_catalog:
            errors.append(f"[ERROR] Experiment '{exp_id}' not found in experiments.yaml")
            continue
        exp = experiments_catalog[exp_id]
        if exp.get('path_abs') is None:
            warnings.append(
                f"[WARNING] Experiment '{exp_id}' has path=null "
                "(future experiment — not yet available)"
            )
        elif not os.path.isdir(exp['path_abs']):
            errors.append(
                f"[ERROR] Experiment '{exp_id}' path does not exist: {exp['path_abs']}"
            )

    for var_id in recipe.get('variables', []):
        yaml_path = os.path.join(variables_dir, f"{var_id}.yaml")
        if not os.path.exists(yaml_path):
            errors.append(f"[ERROR] Variable config not found: {yaml_path}")

    return errors + warnings


def check_all_configs(postproc_dir: str) -> Dict[str, Any]:
    """
    Performs a comprehensive check of all configurations.
    Returns a structured report.
    """
    report = {
        'global': [],
        'experiments': [],
        'variables': [],
        'recipes': [],
        'summary': {'errors': 0, 'warnings': 0, 'ok': 0}
    }

    configs_dir = os.path.join(postproc_dir, 'configs')
    global_path = os.path.join(configs_dir, 'global.yaml')
    experiments_path = os.path.join(configs_dir, 'experiments.yaml')
    variables_dir = os.path.join(configs_dir, 'variables')
    recipes_dir = os.path.join(configs_dir, 'recipes')

    # 1. Global config
    try:
        global_cfg = load_global_config(global_path)
        report['global'].append(f"[OK] global.yaml loaded")
        report['summary']['ok'] += 1
    except Exception as e:
        report['global'].append(f"[ERROR] global.yaml: {e}")
        report['summary']['errors'] += 1
        return report  # Impossible to continue without global config

    # 2. Experiments catalog
    try:
        catalog = load_experiments_catalog(experiments_path, global_cfg)
        report['experiments'].append(f"[OK] experiments.yaml: {len(catalog)} experiments")
        for exp_id, exp in catalog.items():
            if exp.get('path_abs') is None:
                report['experiments'].append(
                    f"[WARNING] {exp_id}: path=null (future experiment)"
                )
                report['summary']['warnings'] += 1
            elif not os.path.isdir(exp['path_abs']):
                report['experiments'].append(
                    f"[ERROR] {exp_id}: path not found: {exp['path_abs']}"
                )
                report['summary']['errors'] += 1
            else:
                report['experiments'].append(f"[OK] {exp_id}: path exists")
                report['summary']['ok'] += 1
    except Exception as e:
        report['experiments'].append(f"[ERROR] experiments.yaml: {e}")
        report['summary']['errors'] += 1

    # 3. Variables
    var_list = list_available_variables(variables_dir)
    if var_list:
        report['variables'].append(f"[OK] {len(var_list)} variable configs found")
        report['summary']['ok'] += len(var_list)
    else:
        report['variables'].append("[WARNING] No variable configs found in configs/variables/")
        report['summary']['warnings'] += 1

    # 4. Recipes
    recipe_list = list_available_recipes(recipes_dir)
    if not recipe_list:
        report['recipes'].append("[WARNING] No recipe configs found in configs/recipes/")
        report['summary']['warnings'] += 1

    for recipe_id in recipe_list:
        recipe_path = os.path.join(recipes_dir, f"{recipe_id}.yaml")
        try:
            recipe = load_recipe(recipe_path, global_cfg)
            msgs = validate_recipe_against_catalog(recipe, catalog, variables_dir)
            errors = [m for m in msgs if m.startswith('[ERROR]')]
            warnings = [m for m in msgs if m.startswith('[WARNING]')]
            if errors:
                report['recipes'].append(f"[ERROR] {recipe_id}.yaml: {len(errors)} error(s)")
                for e in errors:
                    report['recipes'].append(f"  {e}")
                report['summary']['errors'] += len(errors)
            elif warnings:
                report['recipes'].append(
                    f"[WARNING] {recipe_id}.yaml: {len(warnings)} warning(s)"
                )
                for w in warnings:
                    report['recipes'].append(f"  {w}")
                report['summary']['warnings'] += len(warnings)
                report['summary']['ok'] += 1
            else:
                report['recipes'].append(f"[OK] {recipe_id}.yaml: all checks passed")
                report['summary']['ok'] += 1
        except Exception as e:
            report['recipes'].append(f"[ERROR] {recipe_id}.yaml: {e}")
            report['summary']['errors'] += 1

    return report
