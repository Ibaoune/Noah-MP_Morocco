#!/usr/bin/env python3
"""
================================================================================
Author: M. El Aabaribaoune (@um6)
Module: run_postproc
Description: Script for post-processing and analysis of LIS/Noah-MP outputs.
================================================================================
"""
import os
import sys
import argparse
import yaml
from datetime import datetime

# Add root of postproc to path so we can import internal modules
sys.path.append(os.path.dirname(__file__))

from utils.io_lis import get_lis_files
from utils.io_da import get_da_files

# Import modules
try:
    from domain.main import run_domain

    from opl_vs_da.main import run_opl_vs_da
    from runoff_partitioning.main import run_runoff_partitioning
    from hymap_validation.main import run_hymap_validation
    from opl_multiple_da.main import run_opl_multiple_da
    # from figure_export.export_figures import export_figure_set
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

MODULE_MAP = {
    'domain': run_domain,

    'opl_vs_da': run_opl_vs_da,
    'runoff_partitioning': run_runoff_partitioning,
    'hymap_validation': run_hymap_validation,
    'opl_multiple_da': run_opl_multiple_da
}

def load_yaml(filepath):
    if not os.path.exists(filepath):
        print(f"Error: Required config file not found: {filepath}")
        sys.exit(1)
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)

def build_data_dict(matrix_config, proj_root, experiments):
    # Setup data_dict by parsing matrix experiments
    data_dict = {}
    data_dict['start_date'] = datetime.strptime("2016-01-01", "%Y-%m-%d")
    data_dict['end_date'] = datetime.strptime("2016-12-31", "%Y-%m-%d")
    
    matrix_experiments = matrix_config.get('experiments', {})
    
    # We map common experiment types to keys expected by the modules
    # In a real dynamic setup, we might abstract this, but for now we map explicitly:
    exp_mapping = {
        'OPL_noirr_2016': 'files_ol',
        'DA_nocdf_noirr_2016': 'files_da_nocdf',
        'DA_cdf_noirr_2016': 'files_da_cdf'
    }
    
    for exp in experiments:
        if exp not in matrix_experiments:
            print(f"Error: Experiment {exp} not found in matrix config.")
            sys.exit(1)
        
        path = os.path.join(proj_root, matrix_experiments[exp])
        files = get_lis_files(path, data_dict['start_date'], data_dict['end_date'])
        
        dict_key = exp_mapping.get(exp, f"files_{exp}")
        data_dict[dict_key] = files

        # If it's a DA experiment, also load the EnKF and DAOBS files
        if 'DA' in exp:
            da_files = get_da_files(path, data_dict['start_date'], data_dict['end_date'])
            # e.g., da_files_nocdf_innov, da_files_cdf_incr
            suffix = dict_key.replace('files_da_', '')
            data_dict[f'da_{suffix}'] = da_files
        
    return data_dict

def main():
    parser = argparse.ArgumentParser(description="Modular Post-Processing Workflow Orchestrator")
    parser.add_argument("--matrix", type=str, required=True, help="Name of the experiment matrix (e.g., matrix_2016)")
    parser.add_argument("--experiments", type=str, nargs='+', help="List of experiments to process")
    parser.add_argument("--modules", type=str, nargs='+', help="List of scientific modules to run")
    parser.add_argument("--figure-set", type=str, help="Name of the figure set to process and export (e.g., ahmad_2016)")
    parser.add_argument("--make-figures", action="store_true", help="Generate figures")
    parser.add_argument("--export-only", action="store_true", help="Only export figures, no PDF generation")
    
    args = parser.parse_args()
    
    base_dir = os.path.dirname(__file__)
    
    # 1. Load Configurations
    matrix_conf_path = os.path.join(base_dir, f"configs/{args.matrix}.yaml")
    paths_conf_path = os.path.join(base_dir, "configs/paths.yaml")
    fig_sets_conf_path = os.path.join(base_dir, "configs/figure_sets.yaml")
    
    matrix_config = load_yaml(matrix_conf_path)
    paths_config = load_yaml(paths_conf_path)
    proj_root = paths_config.get('project_root', '')
    
    figures_all_dir = os.path.join(proj_root, paths_config['outputs']['figures_all'], args.matrix)
    export_dir = os.path.join(proj_root, paths_config['outputs']['export'], args.matrix)
    
    print("="*60)
    print(f"Starting Modular Post-Processing Workflow for {args.matrix}")
    print("="*60)
    
    # Determine modules to run and experiments to load
    modules_to_run = set()
    experiments_to_load = set(args.experiments) if args.experiments else set()
    
    if args.modules:
        modules_to_run.update(args.modules)
        
    if args.figure_set:
        fig_sets_config = load_yaml(fig_sets_conf_path)
        if 'figure_sets' in fig_sets_config and args.figure_set in fig_sets_config['figure_sets']:
            fset = fig_sets_config['figure_sets'][args.figure_set]
            if not args.experiments and 'experiments' in fset:
                experiments_to_load.update(fset['experiments'])
            for fig in fset.get('figures', []):
                modules_to_run.add(fig['module'])
        else:
            print(f"Error: Figure set {args.figure_set} not found in configuration.")
            sys.exit(1)
            
    # Load Data
    data_dict = build_data_dict(matrix_config, proj_root, list(experiments_to_load))
    
    # 2. Run Modules
    if args.make_figures and modules_to_run:
        print(f"Running requested modules: {', '.join(modules_to_run)}")
        for mod in modules_to_run:
            if mod in MODULE_MAP:
                out_dir = os.path.join(figures_all_dir, mod)
                print(f"\n--- Running Module: {mod} ---")
                MODULE_MAP[mod](data_dict, out_dir)
            else:
                print(f"Warning: Module '{mod}' is not recognized.")
                
    # 3. Export
    if args.export_only:
        print("\nNote: PDF generation is disabled as requested by --export-only.")
        
    if args.figure_set:
        print(f"\n--- Exporting figure set: {args.figure_set} ---")
        # export_figure_set(fig_sets_conf_path, args.figure_set, figures_all_dir, export_dir)

if __name__ == "__main__":
    main()
