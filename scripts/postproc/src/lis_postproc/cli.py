"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.cli
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
"""
cli.py — Interface en ligne de commande
=========================================
Fonctions CLI appelées par scripts/run_postproc.py.
Implémente : --list-experiments, --list-recipes, --check-configs,
             --dry-run, --make-figures, --make-pdf.
"""
import os
import sys
import logging
from typing import Dict, Any

from .core.config import (
    load_global_config, load_experiments_catalog, load_recipe,
    load_all_variables_for_recipe, list_available_recipes,
    list_available_variables, check_all_configs, validate_recipe_against_catalog,
)
from .core.experiments import Experiment, build_experiments_from_catalog
from .core.recipes import Recipe
from .runner import RecipeRunner
from .diagnostics.assimilation.adapter import get_dry_run_summary

logger = logging.getLogger(__name__)


def _find_postproc_dir(script_path: str) -> str:
    """Trouve le dossier racine postproc/ à partir du script run_postproc.py."""
    return os.path.dirname(os.path.dirname(os.path.abspath(script_path)))


def _load_context(postproc_dir: str) -> Dict[str, Any]:
    """Charge le contexte complet : global, experiments, chemins."""
    configs_dir = os.path.join(postproc_dir, 'configs')
    global_cfg = load_global_config(os.path.join(configs_dir, 'global.yaml'))
    experiments_raw = load_experiments_catalog(
        os.path.join(configs_dir, 'experiments.yaml'), global_cfg
    )
    return {
        'global_cfg': global_cfg,
        'experiments_raw': experiments_raw,
        'configs_dir': configs_dir,
        'variables_dir': os.path.join(configs_dir, 'variables'),
        'recipes_dir': os.path.join(configs_dir, 'recipes'),
    }


# ============================================================
# Commandes principales
# ============================================================

def cmd_list_experiments(postproc_dir: str):
    """Affiche la liste de toutes les expériences dans experiments.yaml."""
    ctx = _load_context(postproc_dir)
    experiments = build_experiments_from_catalog(ctx['experiments_raw'])

    print("\n" + "=" * 65)
    print("  AVAILABLE EXPERIMENTS")
    print("=" * 65)
    print(f"  {'ID':<35} {'Label':<18} {'Status'}")
    print("  " + "-" * 63)

    for exp_id, exp in experiments.items():
        status = "✓ available" if exp.is_available() else "✗ path=null (future)"
        print(f"  {exp_id:<35} {exp.label:<18} {status}")

    print("=" * 65)
    print(f"\n  Total: {len(experiments)} experiments\n")


def cmd_list_recipes(postproc_dir: str):
    """Affiche la liste de toutes les recettes disponibles."""
    ctx = _load_context(postproc_dir)
    recipes_dir = ctx['recipes_dir']
    recipe_ids = list_available_recipes(recipes_dir)

    print("\n" + "=" * 65)
    print("  AVAILABLE RECIPES")
    print("=" * 65)

    for rid in recipe_ids:
        recipe_path = os.path.join(recipes_dir, f"{rid}.yaml")
        try:
            recipe_raw = load_recipe(recipe_path, ctx['global_cfg'])
            recipe = Recipe.from_dict(recipe_raw)
            n_exp = len(recipe.experiments)
            n_var = len(recipe.variables)
            print(f"\n  [{rid}]")
            print(f"    Title : {recipe.title}")
            print(f"    Mode  : {recipe.comparison_mode}")
            print(f"    Exps  : {n_exp} | Variables: {n_var}")
            print(f"    File  : configs/recipes/{rid}.yaml")
        except Exception as e:
            print(f"\n  [{rid}] ERROR: {e}")

    print("\n" + "=" * 65)
    print(f"\n  Total: {len(recipe_ids)} recipes\n")


def cmd_check_configs(postproc_dir: str):
    """Vérifie toutes les configurations et affiche le rapport."""
    print("\n" + "=" * 65)
    print("  CONFIGURATION CHECK")
    print("=" * 65)

    report = check_all_configs(postproc_dir)

    # Global
    print("\n  [global.yaml]")
    for msg in report.get('global', []):
        print(f"    {msg}")

    # Experiments
    print("\n  [experiments.yaml]")
    for msg in report.get('experiments', []):
        print(f"    {msg}")

    # Variables
    print("\n  [configs/variables/]")
    for msg in report.get('variables', []):
        print(f"    {msg}")

    # Recipes
    print("\n  [configs/recipes/]")
    for msg in report.get('recipes', []):
        print(f"    {msg}")

    # Summary
    summary = report.get('summary', {})
    print("\n" + "=" * 65)
    print(f"  SUMMARY: "
          f"{summary.get('ok', 0)} OK | "
          f"{summary.get('warnings', 0)} WARNING(S) | "
          f"{summary.get('errors', 0)} ERROR(S)")
    print("=" * 65 + "\n")

    if summary.get('errors', 0) > 0:
        sys.exit(1)


def cmd_dry_run(recipe_path: str, postproc_dir: str):
    """Affiche le plan d'exécution d'une recette sans lancer les calculs."""
    ctx = _load_context(postproc_dir)

    recipe_raw = load_recipe(recipe_path, ctx['global_cfg'])
    recipe = Recipe.from_dict(recipe_raw)
    experiments = ctx['experiments_raw']

    print("\n" + "=" * 65)
    print(f"  DRY-RUN: {recipe.recipe_id}")
    print("=" * 65)

    print(f"\n  Title       : {recipe.title}")
    print(f"  Year        : {recipe.year}")
    print(f"  Domain      : {recipe.domain}")
    print(f"  Mode        : {recipe.comparison_mode}")
    print(f"  Baseline    : {recipe.baseline or '(none)'}")

    # Expériences
    print(f"\n  Experiments ({len(recipe.experiments)}):")
    for exp_id in recipe.experiments:
        exp_data = experiments.get(exp_id, {})
        path = exp_data.get('path_abs', 'null')
        label = exp_data.get('label', exp_id)
        status = "✓" if path and os.path.isdir(path) else "✗"
        print(f"    {status} {exp_id} ({label})")
        if path and not os.path.isdir(path):
            print(f"      Path not found: {path}")

    # Variables
    print(f"\n  Variables ({len(recipe.variables)}):")
    available_vars = list_available_variables(ctx['variables_dir'])
    for var_id in recipe.variables:
        status = "✓" if var_id in available_vars else "✗ MISSING"
        print(f"    {status} {var_id}")

    # Diagnostics
    print(f"\n  Diagnostics:")
    for diag_name, diag_cfg in recipe.diagnostics.items():
        enabled = diag_cfg.get('enabled', False)
        status = "ENABLED " if enabled else "disabled"
        print(f"    [{status}] {diag_name}")

    # Figures prévues
    print(f"\n  Planned outputs:")
    print(f"    Figures   : {recipe.outputs.figure_dir}")
    print(f"    Metrics   : {recipe.outputs.metrics_dir}")
    print(f"    Tables    : {recipe.outputs.table_dir}")
    print(f"    PDF       : {recipe.outputs.pdf_report}")

    # Détails assimilation
    if recipe.is_diagnostic_enabled('assimilation'):
        print(f"\n  Assimilation details:")
        lines = get_dry_run_summary(recipe, experiments)
        for line in lines:
            print(f"  {line}")

    print("\n" + "=" * 65)
    print("  [DRY-RUN] No calculations performed.\n")


def cmd_run_recipe(
    recipe_path: str,
    postproc_dir: str,
    make_figures: bool = True,
    make_hydrology_figures: bool = False,
    scan_variables: bool = False,
    make_pdf: bool = False,
):
    """Lance l'exécution complète d'une recette."""
    ctx = _load_context(postproc_dir)

    recipe_raw = load_recipe(recipe_path, ctx['global_cfg'])
    recipe = Recipe.from_dict(recipe_raw)

    # Validation rapide avant de lancer
    errors = validate_recipe_against_catalog(
        recipe_raw, ctx['experiments_raw'], ctx['variables_dir']
    )
    critical = [e for e in errors if e.startswith('[ERROR]')]
    if critical:
        print("\n[ERROR] Cannot run recipe — validation failed:")
        for e in critical:
            print(f"  {e}")
        sys.exit(1)

    warnings = [e for e in errors if e.startswith('[WARNING]')]
    if warnings:
        print("\n[WARNING] Recipe has warnings (will proceed):")
        for w in warnings:
            print(f"  {w}")

    print(f"\n{'='*65}")
    print(f"  Running recipe: {recipe.recipe_id}")
    print(f"  Title: {recipe.title}")
    print(f"  Experiments: {recipe.experiments}")
    print(f"  Variables: {len(recipe.variables)}")
    print(f"{'='*65}\n")

    runner = RecipeRunner(
        recipe=recipe,
        experiments_catalog=ctx['experiments_raw'],
        global_cfg=ctx['global_cfg'],
        variables_dir=ctx['variables_dir'],
        dry_run=False,
    )

    if scan_variables:
        from lis_postproc.core.scanner import scan_variables as sv
        sv(recipe, ctx['experiments_raw'], ctx['global_cfg'])
        from lis_postproc.core.quality import run_hydrology_qc
        run_hydrology_qc(recipe, ctx['experiments_raw'], ctx['global_cfg'])

    report = runner.run(
        make_figures=make_figures,
        make_hydrology_figures=make_hydrology_figures,
        make_pdf=make_pdf
    )

    print(f"\n{'='*65}")
    print(f"  Recipe completed: {recipe.recipe_id}")
    print(f"  Diagnostics run : {report['diagnostics_run']}")
    print(f"  Files generated : {len(report['generated_files'])}")
    if report['errors']:
        print(f"  Errors          : {len(report['errors'])}")
        for e in report['errors']:
            print(f"    - {e}")
    print(f"{'='*65}\n")
