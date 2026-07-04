import os
import sys
import argparse
from datetime import datetime

# Local imports
from utils import load_config, deep_merge_dicts
from diagnostics.diag_coverage import run_coverage
from diagnostics.diag_innovations import run_innovations
from diagnostics.diag_seasonal_increments import run_seasonal_increments
from diagnostics.diag_spread import run_spread

def main():
    parser = argparse.ArgumentParser(description="Assimilation Diagnostics Module")
    parser.add_argument("--global_config", type=str, default="configs/global.yaml",
                        help="Path to the global YAML configuration file")
    parser.add_argument("--experiment", type=str, required=True,
                        help="Path to the experiment YAML configuration file")
    parser.add_argument("--diagnostic", type=str, default=None,
                        help="Specific diagnostic to run (coverage, innovations, seasonal_increments, spread)")
    parser.add_argument("--all", action="store_true",
                        help="Run all available diagnostics in configs/diagnostics/")
    args = parser.parse_args()

    if not args.diagnostic and not args.all:
        print("ERROR: You must specify either --diagnostic <name> or --all")
        sys.exit(1)

    # Load configuration
    try:
        config = load_config(args.global_config)
        exp_config = load_config(args.experiment)
        deep_merge_dicts(config, exp_config)
    except Exception as e:
        print(f"Error loading base configurations: {e}")
        sys.exit(1)
        
    # Convert dates to datetime objects
    try:
        if 'start_date' not in config or 'end_date' not in config:
            raise KeyError("start_date and end_date are required")
        config['start_date'] = datetime.strptime(config['start_date'], '%Y-%m-%d')
        config['end_date'] = datetime.strptime(config['end_date'], '%Y-%m-%d')
    except Exception as e:
        print(f"Error parsing dates (use YYYY-MM-DD): {e}")
        sys.exit(1)

    # Build absolute paths
    project_root = config.get('project_root', '')
    if 'da_dir' not in config:
        print("ERROR: da_dir is missing in the configuration")
        sys.exit(1)
    
    # We might not strictly need opl_dir for all, but let's just make sure paths are absolute
    da_dir = os.path.join(project_root, config['da_dir']) if not os.path.isabs(config['da_dir']) else config['da_dir']
    out_dir = os.path.join(project_root, config.get('output_dir', '')) if not os.path.isabs(config.get('output_dir', '')) else config.get('output_dir', '')

    if not os.path.exists(da_dir):
        print(f"ERROR: DA directory not found: {da_dir}")
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    print(f"Output directory ready: {out_dir}")

    # Determine diagnostics to run
    available_diags = {
        'coverage': run_coverage,
        'innovations': run_innovations,
        'seasonal_increments': run_seasonal_increments,
        'spread': run_spread
    }
    
    diags_to_run = []
    if args.all:
        diags_to_run = list(available_diags.keys())
    else:
        if args.diagnostic not in available_diags:
            print(f"ERROR: Unknown diagnostic '{args.diagnostic}'. Available: {list(available_diags.keys())}")
            sys.exit(1)
        diags_to_run = [args.diagnostic]

    for diag in diags_to_run:
        diag_config_path = f"configs/diagnostics/{diag}.yaml"
        if not os.path.exists(diag_config_path):
            print(f"WARNING: Diagnostic config {diag_config_path} not found. Skipping {diag}.")
            continue
            
        print(f"\n--- Running diagnostic: {diag} ---")
        try:
            diag_cfg = load_config(diag_config_path)
            # Create a fresh copy of the base config for this diagnostic
            import copy
            run_config = copy.deepcopy(config)
            deep_merge_dicts(run_config, diag_cfg)
            
            # Execute
            available_diags[diag](run_config, da_dir, out_dir)
        except Exception as e:
            print(f"Error running diagnostic {diag}: {e}")

    print("\nAssimilation Diagnostics module completed successfully!")

if __name__ == "__main__":
    main()
