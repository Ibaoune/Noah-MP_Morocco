"""
===============================================================================
Script: main.py
Author: M. El Aabaribaoune (@um6p)

Objective: Orchestrator for the modular OPL vs DA plotting framework.

Description:
    This script serves as the main entry point for generating spatial 
    comparisons between the Open Loop (OL) and Data Assimilation (DA) 
    experiments. It reads the configuration from 'config_opl_da.yaml', 
    determines the requested variables and temporal aggregation periods 
    (e.g., 'all-period' or seasonal), and dispatches the plotting 
    tasks to the core processing engine.

Execution:
    $ conda activate postproc_env
    $ python main.py

Dependencies:
    os, yaml, core.plot_variable
===============================================================================
"""
import sys
import os
import yaml
from core import plot_variable

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config_opl_da.yaml"
    if not os.path.exists(config_path):
        print(f"Error: Configuration file '{config_path}' not found.")
        return
        
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
        
    print("="*60)
    print("Starting Modular OPL vs DA Plotting Framework")
    print("="*60)
    
    # Process variables
    period = config['analysis'].get('period', 'all-period')
    
    for var_key, var_conf in config['variables'].items():
        if not var_conf.get('active', True):
            print(f"Skipping {var_key}: Marked as inactive in config.")
            continue
            
        if period == 'seasonal':
            for season in ['DJF', 'MAM', 'JJA', 'SON']:
                plot_variable(config, var_key, season)
        else:
            plot_variable(config, var_key, 'all-period')
            
    print("All configured variables processed successfully.")

if __name__ == "__main__":
    main()
