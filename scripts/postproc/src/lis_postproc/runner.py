"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: lis_postproc.runner
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
"""
runner.py — Recipe Orchestrator
=======================================
RecipeRunner executes the complete pipeline of a recipe:
  1. Resolution of experiments and variables
  2. Creation of output directories
  3. Dispatching to enabled diagnostic modules
  4. Optional PDF report generation
"""
import os
import logging
from typing import Dict, Any, Optional

from .core.recipes import Recipe
from .core.config import load_all_variables_for_recipe
from .diagnostics.assimilation.adapter import run_assimilation_diagnostics

logger = logging.getLogger(__name__)


class RecipeRunner:
    """
    Orchestrates the execution of a post-processing recipe.

    Parameters
    ----------
    recipe            : Recipe object loaded from YAML
    experiments_catalog: Raw dictionary of experiments (from load_experiments_catalog)
    global_cfg        : Global configuration (from load_global_config)
    variables_dir     : Path to configs/variables/
    dry_run           : If True, prints the execution plan without running
    """

    def __init__(
        self,
        recipe: Recipe,
        experiments_catalog: Dict[str, Any],
        global_cfg: Dict[str, Any],
        variables_dir: str,
        dry_run: bool = False,
    ):
        self.recipe = recipe
        self.experiments_catalog = experiments_catalog
        self.global_cfg = global_cfg
        self.variables_dir = variables_dir
        self.dry_run = dry_run
        self._generated_files = []

    def run(self, make_figures: bool = True, make_hydrology_figures: bool = False, make_pdf: bool = False) -> Dict:
        """
        Launches the complete recipe pipeline.

        Returns an execution report.
        """
        logger.info(f"Starting recipe: {self.recipe.recipe_id}")
        report = {
            'recipe_id': self.recipe.recipe_id,
            'experiments': self.recipe.experiments,
            'variables': self.recipe.variables,
            'diagnostics_run': [],
            'generated_files': [],
            'errors': [],
        }

        # 1. Create output directories
        if not self.dry_run:
            self.recipe.outputs.create_dirs()
            logger.info("Output directories created")

        # 2. Load variables
        try:
            variables_data = load_all_variables_for_recipe(
                self.recipe.__dict__, self.variables_dir
            )
        except Exception as e:
            logger.error(f"Error loading variables: {e}")
            report['errors'].append(str(e))
            variables_data = {}

        # 3. Dispatch to enabled diagnostics
        if make_figures or make_hydrology_figures:
            self._run_diagnostics(report, variables_data, make_figures, make_hydrology_figures)

        # 4. PDF
        if make_pdf and not self.dry_run:
            self._generate_pdf(report)

        report['generated_files'] = self._generated_files
        return report

    def _run_diagnostics(self, report: Dict, variables_data: Dict, make_figures: bool, make_hydrology_figures: bool):
        """Dispatches execution to each diagnostic module enabled in the recipe."""

        # --- Assimilation ---
        if self.recipe.is_diagnostic_enabled('assimilation') and make_figures:
            logger.info("Dispatching: assimilation diagnostics")
            out_dir = os.path.join(
                self.recipe.outputs.figure_dir, 'assimilation'
            )
            if not self.dry_run:
                os.makedirs(out_dir, exist_ok=True)
            try:
                files = run_assimilation_diagnostics(
                    recipe=self.recipe,
                    experiments_catalog=self.experiments_catalog,
                    global_cfg=self.global_cfg,
                    out_dir=out_dir,
                    dry_run=self.dry_run,
                )
                self._generated_files.extend(files)
                report['diagnostics_run'].append('assimilation')
            except Exception as e:
                logger.error(f"Error in assimilation diagnostics: {e}")
                report['errors'].append(f"assimilation: {e}")

        # --- Domain ---
        if self.recipe.is_diagnostic_enabled('domain') and make_figures:
            logger.info("Dispatching: domain diagnostics")
            out_dir = os.path.join(
                self.recipe.outputs.figure_dir, 'domain'
            )
            if not self.dry_run:
                os.makedirs(out_dir, exist_ok=True)
            try:
                from .diagnostics.domain.adapter import run_domain_diagnostics
                files = run_domain_diagnostics(
                    recipe=self.recipe,
                    global_cfg=self.global_cfg,
                    out_dir=out_dir,
                    dry_run=self.dry_run,
                )
                self._generated_files.extend(files)
                report['diagnostics_run'].append('domain')
            except Exception as e:
                logger.error(f"Error in domain diagnostics: {e}")
                report['errors'].append(f"domain: {e}")

        # --- Unified Hydrology ---
        hydrology_enabled = self.recipe.is_diagnostic_enabled('hydrology')
        
        if hydrology_enabled and make_hydrology_figures:
            logger.info("Dispatching: unified hydrology diagnostics")
            out_dir = self.recipe.outputs.figure_dir
            if not self.dry_run:
                os.makedirs(out_dir, exist_ok=True)
                from .diagnostics.hydrology.generator import run_hydrology_diagnostics
                try:
                    files = run_hydrology_diagnostics(
                        self.recipe, 
                        self.experiments_catalog, 
                        self.global_cfg, 
                        variables_data, 
                        out_dir
                    )
                    self._generated_files.extend(files)
                except Exception as e:
                    logger.error(f"Error in unified hydrology diagnostics: {e}")
            report['diagnostics_run'].append('hydrology')

        # --- Streamflow ---
        if self.recipe.is_diagnostic_enabled('streamflow') and make_hydrology_figures:
            logger.info("Dispatching: streamflow (Not yet implemented with HyMAP)")
            report['diagnostics_run'].append('streamflow')

        # --- External Validation ---
        if self.recipe.is_diagnostic_enabled('external_validation') and make_hydrology_figures:
            logger.info("Dispatching: external_validation (Not yet implemented)")
            report['diagnostics_run'].append('external_validation')

    def _generate_pdf(self, report: Dict):
        """Generates a PDF report consolidating all figures."""
        pdf_path = self.recipe.outputs.pdf_report
        if not pdf_path:
            logger.warning("No pdf_report path defined in recipe outputs")
            return

        logger.info(f"Generating PDF report: {pdf_path}")
        try:
            from .plotting.pdf_generator import generate_diagnostic_report

            figure_files = [
                f for f in self._generated_files
                if f.endswith('.png') or f.endswith('.pdf') or f.endswith('.json')
            ]

            if not figure_files:
                logger.warning("No figures to include in PDF")
                return

            # Call the new structured generator
            final_pdf = generate_diagnostic_report(self.recipe, figure_files, pdf_path)
            
            self._generated_files.append(final_pdf)
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            report['errors'].append(f"pdf: {e}")
