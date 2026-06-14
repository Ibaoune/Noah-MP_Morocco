import os
import sys
import subprocess

# Add scripts directory to python path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts"))

import config_postproc as cfg

# Scripts from the original postproc_00 framework
base_eval_scripts = [
    "compare_opl_da.py",
    "eval_water_budget.py"
]

# Scripts merged from postproc_01 and postproc_02
fig_scripts = [
    # General context & setup (mostly overlapping, running both to be safe)
    "domain/fig0_domain_plots.py",
    "domain/fig01_study_domain.py",
    "domain/fig01_spatial_context.py",
    "fig02_methodology_flowchart.py",
    
    # Specific impact & evaluation
    "fig02_spatial_impact_fluxes.py",
    "fig03_sm_assim_impact.py",
    "fig03_stats_by_ecosystem.py",
    
    # Dynamics and decomposition
    "fig04_lai_dynamics.py",
    "fig04_runoff_irrigation.py",
    "fig05_runoff_decomposition.py",
    "fig05_drought_categorization.py",
    
    # Validations & extremes
    "fig06_09_gldas_intercomparison.py",
    "fig06_extreme_event_response.py",
    "fig10_12_streamflow_validation.py",
    "fig13_14_spatial_impact_drivers.py",
    
    # Supplementary
    "supp_statistical_analysis.py"
]

def run_script(script_name):
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "scripts", script_name)
    if not os.path.exists(script_path):
        print(f"Warning: Script {script_name} not found at {script_path}. Skipping.")
        return
        
    print(f"\n{'='*50}\nRunning {script_name}...\n{'='*50}")
    
    env = os.environ.copy()
    env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__)) + "/scripts:" + env.get("PYTHONPATH", "")
    
    result = subprocess.run([sys.executable, script_path], env=env, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error executing {script_name}:")
        print(result.stderr)
        print("Continuing with next script...\n")
    else:
        print(f"Successfully executed {script_name}.")
        # Print tail of output for context
        out_lines = result.stdout.strip().split('\n')
        if len(out_lines) > 5:
            print("... (output truncated)")
            print('\n'.join(out_lines[-5:]))
        else:
            print(result.stdout)

if __name__ == "__main__":
    print(f"Starting unified post-processing framework...")
    print(f"Output Figures Directory: {cfg.DIR_FIGURES}\n")
    
    print("\n--- Phase 1: Base Evaluations ---")
    for script in base_eval_scripts:
        run_script(script)
        
    print("\n--- Phase 2: Publication Figures ---")
    for script in fig_scripts:
        run_script(script)
        
    print(f"\nAll post-processing tasks completed. Check {cfg.DIR_FIGURES} for outputs.")
