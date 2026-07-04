import os
import sys
import argparse
from datetime import datetime

# Local imports
from utils import load_config
from diagnostics.diag_coverage import run_coverage
from diagnostics.diag_innovations import run_innovations
from diagnostics.diag_seasonal_increments import run_seasonal_increments
from diagnostics.diag_spread import run_spread

def main():
    parser = argparse.ArgumentParser(description="Assimilation Diagnostics Module")
    parser.add_argument("--config", type=str, default="config_diagAssim.yaml",
                        help="Path to the YAML configuration file")
    args = parser.parse_args()

    # Load configuration
    print(f"Loading configuration from: {args.config}")
    try:
        config = load_config(args.config)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
        
    # Convert dates to datetime objects
    try:
        config['start_date'] = datetime.strptime(config['start_date'], '%Y-%m-%d')
        config['end_date'] = datetime.strptime(config['end_date'], '%Y-%m-%d')
    except Exception as e:
        print(f"Error parsing dates (use YYYY-MM-DD): {e}")
        sys.exit(1)

    # Build absolute paths
    project_root = config.get('project_root', '')
    opl_dir = os.path.join(project_root, config['opl_dir'])
    da_dir = os.path.join(project_root, config['da_dir'])
    out_dir = os.path.join(project_root, config['output_dir'])

    if not os.path.exists(da_dir):
        print(f"ERROR: DA directory not found: {da_dir}")
        sys.exit(1)

    # Create output directory
    os.makedirs(out_dir, exist_ok=True)
    print(f"Output directory ready: {out_dir}")

    # Dispatch to the active diagnostics
    active_diags = config.get('active_diagnostics', [])
    print(f"Active diagnostics to run: {active_diags}")

    if 'coverage' in active_diags:
        run_coverage(config, da_dir, out_dir)
        
    if 'innovations' in active_diags:
        run_innovations(config, da_dir, out_dir)
        
    if 'seasonal_increments' in active_diags:
        run_seasonal_increments(config, da_dir, out_dir)
        
    if 'spread' in active_diags:
        run_spread(config, da_dir, out_dir)

    print("Assimilation Diagnostics module completed successfully!")

if __name__ == "__main__":
    main()
