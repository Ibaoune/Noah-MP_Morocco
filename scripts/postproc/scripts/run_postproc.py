#!/usr/bin/env python3
"""
================================================================================
Author: M. El Aabaribaoune (@um6p)
Module: run_postproc
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
"""
run_postproc.py — Main Controller of the LIS/Noah-MP Post-Processing Framework
================================================================================
Single entry point for all post-processing operations.

USAGE:
  # List available experiments
  python scripts/run_postproc.py --list-experiments

  # List available recipes
  python scripts/run_postproc.py --list-recipes

  # Check all configurations
  python scripts/run_postproc.py --check-configs

  # Simulate recipe execution (no calculations)
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --dry-run

  # Run a complete recipe with figures
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures

  # Run with PDF generation
  python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures --make-pdf
"""
import os
import sys
import argparse
import logging
from pathlib import Path

# ============================================================
# Path Resolution
# ============================================================
# This script is located in scripts/ (under postproc/).
# The lis_postproc package is in src/.
_SCRIPTS_DIR = Path(__file__).parent.resolve()
_POSTPROC_DIR = _SCRIPTS_DIR.parent.resolve()    # scripts/postproc/
_SRC_DIR = _POSTPROC_DIR / "src"                 # scripts/postproc/src/

# Add postproc_dir to sys.path to import src as a package
if str(_POSTPROC_DIR) not in sys.path:
    sys.path.insert(0, str(_POSTPROC_DIR))


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

    # Mutually exclusive modes (except --recipe which can be combined)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        '--list-experiments', action='store_true',
        help='Displays the list of all experiments in experiments.yaml'
    )
    mode_group.add_argument(
        '--list-recipes', action='store_true',
        help='Displays the list of all available recipes'
    )
    mode_group.add_argument(
        '--check-configs', action='store_true',
        help='Checks all YAML configurations and paths'
    )

    # Recipe
    parser.add_argument(
        '--recipe', type=str, metavar='RECIPE_PATH',
        help='Path to the YAML recipe file (e.g., configs/recipes/smap_cdf_sensitivity_2016.yaml)'
    )

    # Execution Options
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Displays the execution plan without running calculations'
    )
    parser.add_argument(
        '--make-figures', action='store_true',
        help='Generates the figures'
    )
    parser.add_argument(
        '--make-hydrology-figures', action='store_true',
        help='Generates the hydrology figures'
    )
    parser.add_argument(
        '--scan-variables', action='store_true',
        help='Scan LIS NetCDF files to report available variables and dimensions'
    )
    parser.add_argument(
        '--make-pdf', action='store_true',
        help='Generates the PDF report (requires --make-figures)'
    )

    # Verbosity options
    parser.add_argument(
        '--verbose', '-v', action='store_true',
        help='Verbose mode (DEBUG logging)'
    )
    parser.add_argument(
        '--quiet', '-q', action='store_true',
        help='Quiet mode (WARNING logging only)'
    )

    return parser.parse_args()


def setup_logging(verbose: bool = False, quiet: bool = False,
                  log_dir: str = None):
    """Configures the logging system."""
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
    Resolves the recipe path by testing several bases:
      1. As provided (absolute or relative to CWD)
      2. Relative to the postproc/ directory
      3. Relative to the directory where scripts/run_postproc.py is located
    """
    candidates = [
        recipe_arg,
        os.path.join(str(_POSTPROC_DIR), recipe_arg),
        os.path.join(str(_SCRIPTS_DIR.parent), recipe_arg),
    ]
    for path in candidates:
        if os.path.isfile(path):
            return os.path.abspath(path)
    return os.path.abspath(recipe_arg)  # Return as is for the error message


def main():
    args = parse_args()

    # Logging
    log_dir = os.path.join(str(_POSTPROC_DIR), 'logs')
    setup_logging(verbose=args.verbose, quiet=args.quiet, log_dir=log_dir)
    logger = logging.getLogger('run_postproc')

    logger.debug(f"postproc_dir = {_POSTPROC_DIR}")
    logger.debug(f"src_dir      = {_SRC_DIR}")

    # Import du package principal
    try:
        from src.cli import (
            cmd_list_experiments,
            cmd_list_recipes,
            cmd_check_configs,
            cmd_dry_run,
            cmd_run_recipe,
        )
    except ImportError as e:
        print(f"\n[ERROR] Cannot import src.cli package: {e}")
        print(f"  Expected location: {_SRC_DIR}/cli.py")
        sys.exit(1)

    postproc_dir = str(_POSTPROC_DIR)

    # ============================================================
    # Dispatch based on the execution mode
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
            # No option provided with --recipe → display dry-run by default
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
