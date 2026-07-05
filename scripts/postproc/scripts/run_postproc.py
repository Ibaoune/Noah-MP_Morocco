#!/usr/bin/env python3
"""
run_postproc.py — Contrôleur principal du framework LIS/Noah-MP Post-Processing
================================================================================
Point d'entrée unique pour toutes les opérations de post-processing.

UTILISATION :
  # Lister les expériences disponibles
  python scripts/run_postproc.py --list-experiments

  # Lister les recettes disponibles
  python scripts/run_postproc.py --list-recipes

  # Vérifier toutes les configurations
  python scripts/run_postproc.py --check-configs

  # Simuler l'exécution d'une recette (sans calculs)
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run

  # Lancer une recette complète avec figures
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures

  # Lancer avec génération PDF
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures --make-pdf
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# ============================================================
# Résolution des chemins
# ============================================================
# Ce script est dans scripts/ (sous postproc/).
# Le package lis_postproc est dans src/.
_SCRIPTS_DIR = Path(__file__).parent.resolve()
_POSTPROC_DIR = _SCRIPTS_DIR.parent.resolve()    # scripts/postproc/
_SRC_DIR = _POSTPROC_DIR / "src"                 # scripts/postproc/src/

# Ajouter src/ au sys.path pour importer lis_postproc
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))


def parse_args():
    parser = argparse.ArgumentParser(
        description="LIS/Noah-MP Post-Processing Framework — YAML-driven modular pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/run_postproc.py --list-experiments
  python scripts/run_postproc.py --list-recipes
  python scripts/run_postproc.py --check-configs
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures --make-pdf
        """
    )

    # Modes mutuellement exclusifs (sauf --recipe qui peut se combiner)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--list-experiments', action='store_true',
        help='Affiche la liste de toutes les expériences dans experiments.yaml'
    )
    mode_group.add_argument(
        '--list-recipes', action='store_true',
        help='Affiche la liste de toutes les recettes disponibles'
    )
    mode_group.add_argument(
        '--check-configs', action='store_true',
        help='Vérifie toutes les configurations YAML et les chemins'
    )

    # Recette
    parser.add_argument(
        '--recipe', type=str, metavar='RECIPE_PATH',
        help='Chemin vers le fichier YAML de recette (ex: configs/recipes/smap_cdf_sensitivity_2016.yaml)'
    )

    # Options d'exécution
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Affiche le plan d\'exécution sans lancer les calculs'
    )
    parser.add_argument(
        '--make-figures', action='store_true',
        help='Génère les figures'
    )
    parser.add_argument(
        '--make-hydrology-figures', action='store_true',
        help='Génère les figures hydrologiques'
    )
    parser.add_argument(
        '--scan-variables', action='store_true',
        help='Scan LIS NetCDF files to report available variables and dimensions'
    )
    parser.add_argument(
        '--make-pdf', action='store_true',
        help='Génère le rapport PDF (nécessite --make-figures)'
    )

    # Options de verbosité
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Mode verbeux (logging DEBUG)'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Mode silencieux (logging WARNING uniquement)'
    )

    return parser.parse_args()


def setup_logging(verbose: bool = False, quiet: bool = False,
                  log_dir: str = None):
    """Configure le logging."""
    if verbose:
        level = logging.DEBUG
    elif quiet:
        level = logging.WARNING
    else:
        level = logging.INFO

    handlers = [logging.StreamHandler(sys.stdout)]

    if log_dir:
        os.makedirs(log_dir, exist_ok=True)
        from datetime import datetime
        log_file = os.path.join(
            log_dir, f"run_postproc_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        )
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=handlers
    )


def resolve_recipe_path(recipe_arg: str) -> str:
    """
    Résout le chemin de la recette, en testant plusieurs bases :
      1. Tel quel (chemin absolu ou relatif au CWD)
      2. Relatif au dossier postproc/
      3. Relatif au dossier où est scripts/run_postproc.py
    """
    candidates = [
        recipe_arg,
        os.path.join(str(_POSTPROC_DIR), recipe_arg),
        os.path.join(str(_SCRIPTS_DIR.parent), recipe_arg),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)
    return os.path.abspath(recipe_arg)  # Retourner tel quel pour le message d'erreur


def main():
    args = parse_args()

    # Logging
    log_dir = os.path.join(str(_POSTPROC_DIR), 'logs')
    setup_logging(verbose=args.verbose, quiet=args.quiet, log_dir=log_dir)
    logger = logging.getLogger('run_postproc')

    logger.debug(f"postproc_dir = {_POSTPROC_DIR}")
    logger.debug(f"src_dir      = {_SRC_DIR}")

    # Import du package lis_postproc
    try:
        from lis_postproc.cli import (
            cmd_list_experiments,
            cmd_list_recipes,
            cmd_check_configs,
            cmd_dry_run,
            cmd_run_recipe,
        )
    except ImportError as e:
        print(f"\n[ERROR] Cannot import lis_postproc package: {e}")
        print(f"  Expected location: {_SRC_DIR}/lis_postproc/")
        sys.exit(1)

    postproc_dir = str(_POSTPROC_DIR)

    # ============================================================
    # Dispatch selon le mode
    # ============================================================

    if args.list_experiments:
        cmd_list_experiments(postproc_dir)

    elif args.list_recipes:
        cmd_list_recipes(postproc_dir)

    elif args.check_configs:
        cmd_check_configs(postproc_dir)

    elif args.recipe:
        recipe_path = resolve_recipe_path(args.recipe)

        if not os.path.isfile(recipe_path):
            print(f"\n[ERROR] Recipe file not found: {recipe_path}")
            print(f"  Tried: {args.recipe}")
            print(f"  Use --list-recipes to see available recipes")
            sys.exit(1)

        logger.info(f"Recipe: {recipe_path}")

        if args.dry_run:
            cmd_dry_run(recipe_path, postproc_dir)
        elif args.make_figures or args.make_pdf or args.make_hydrology_figures or args.scan_variables:
            cmd_run_recipe(
                recipe_path=recipe_path,
                postproc_dir=postproc_dir,
                make_figures=args.make_figures,
                make_hydrology_figures=args.make_hydrology_figures,
                scan_variables=args.scan_variables,
                make_pdf=args.make_pdf,
            )
        else:
            # Pas d'option fournie avec --recipe → afficher le dry-run par défaut
            print(
                "\n[INFO] No action specified. Use --dry-run, --make-figures, or --make-pdf."
                "\n       Showing dry-run output:\n"
            )
            cmd_dry_run(recipe_path, postproc_dir)

    else:
        print("\n[ERROR] No command specified.")
        print("  Use --help to see available options.")
        print("\n  Quick examples:")
        print("    python scripts/run_postproc.py --list-experiments")
        print("    python scripts/run_postproc.py --list-recipes")
        print("    python scripts/run_postproc.py --check-configs")
        print("    python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run")
        sys.exit(1)


if __name__ == '__main__':
    main()
