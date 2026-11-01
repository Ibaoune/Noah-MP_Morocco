#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Daisy-Chaining Script for LIS Experiments

This script automates the continuous execution of sequential simulation periods 
(e.g., years, months, or days) by implementing a daisy-chaining mechanism. 
Instead of relying on an external polling orchestrator, this script generates the 
configuration for a specific target period, submits a SLURM batch job for that period, 
and embeds a command at the end of that SLURM job to re-invoke this script for the 
subsequent period upon successful completion.

Workflow Logic:
1. Parse arguments to determine the current execution date.
2. Read the global experiment parameters from `config/experiment.ini`.
3. Check if the global end date has been reached.
4. Verify the existence of the required initial conditions (restart files).
5. Generate a target-specific LIS configuration file from a template.
6. Generate a SLURM batch script that runs LIS, copies outputs, and calls this script again.
7. (Optional) Submit the generated SLURM script if the `--submit` flag is provided.

This approach guarantees zero CPU idle-wait time and improves job resilience on HPC clusters.
"""

import argparse
import os
import sys
import subprocess
import configparser
from datetime import datetime
from dateutil.relativedelta import relativedelta

def read_config(config_path: str) -> configparser.SectionProxy:
    """
    Reads the global experiment configuration from the INI file.

    Args:
        config_path (str): The relative or absolute path to the INI file.

    Returns:
        configparser.SectionProxy: A dictionary-like object containing the [Experiment] section parameters.
    """
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        print(f"Error: Config file {config_path} not found.")
        sys.exit(1)
    config.read(config_path)
    return config['Experiment']

def get_next_date(current_date: datetime, period_length: str) -> datetime:
    """
    Calculates the start date for the next consecutive simulation period.

    Args:
        current_date (datetime): The start date of the current period.
        period_length (str): The length of the period ('1Y' for 1 year, '1M' for 1 month, '1D' for 1 day).

    Returns:
        datetime: The start date for the next period.
    """
    if period_length == '1Y':
        return current_date + relativedelta(years=1)
    elif period_length == '1M':
        return current_date + relativedelta(months=1)
    elif period_length == '1D':
        return current_date + relativedelta(days=1)
    else:
        raise ValueError(f"Unsupported PeriodLength: {period_length}")

def get_label(current_date: datetime, period_len: str) -> str:
    """
    Generates a label for the current period (e.g. 2008, 2008-01).
    """
    if period_len == "1Y":
        return current_date.strftime("%Y")
    elif period_len == "1M":
        return current_date.strftime("%Y-%m")
    elif period_len == "1D":
        return current_date.strftime("%Y-%m-%d")
    return current_date.strftime("%Y")

def get_log_dir_name(current_date, period_len):
    """
    Generates the log directory name based on period length.
    """
    if period_len == "1Y":
        return current_date.strftime("%Y")
    elif period_len == "1M":
        return current_date.strftime("%m%Y")
    elif period_len == "1D":
        return current_date.strftime("%Y%m%d")
    return current_date.strftime("%Y")

def main():
    """
    Main execution function.
    """
    parser = argparse.ArgumentParser(description="Daisy-chaining script for LIS experiments.")
    parser.add_argument("--current-date", required=True, help="Current date to run (YYYY-MM-DD)")
    parser.add_argument("--submit", action="store_true", help="Submit the job to SLURM immediately")
    
    args = parser.parse_args()
    
    # Establish base directory to ensure relative paths work regardless of execution context
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup"
    os.chdir(base_dir)

    # 1. Read Global Configuration
    config_path = "config/experiment.ini"
    cfg = read_config(config_path)

    global_start_date = datetime.strptime(cfg['StartDate'], "%Y-%m-%d")
    global_end_date = datetime.strptime(cfg['EndDate'], "%Y-%m-%d")
    period_length = cfg['PeriodLength']
    exp_name = cfg['ExperimentName']
    template_path = cfg['TemplateFile']
    
    current_date = datetime.strptime(args.current_date, "%Y-%m-%d")
    
    # 2. Check Chain Completion
    if current_date >= global_end_date:
        print(f"End date {global_end_date.strftime('%Y-%m-%d')} reached. Chain is complete!")
        sys.exit(0)

    # 3. Calculate Boundaries for the Current Run
    next_date = get_next_date(current_date, period_length)
    if next_date > global_end_date:
        next_date = global_end_date

    label = get_label(current_date, period_length)

    # Determine Initialization Mode
    # The very first run can be 'coldstart' or 'restart' based on the config. 
    # All subsequent runs in the chain MUST be 'restart'.
    if current_date == global_start_date:
        start_mode = cfg.get('InitMode', 'coldstart')
    else:
        start_mode = "restart"

    # 4. Prepare Workspace Directories
    os.makedirs("generated/configs", exist_ok=True)
    os.makedirs("generated/jobs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(f"output/{label}", exist_ok=True)

    restarts_dir = "restarts"
    
    # 5. Verify Restart Files (If applicable)
    expected_start_restart = f"LIS_RST_NOAHMP401_{current_date.strftime('%Y%m%d')}0000.d01.nc"
    restart_path = os.path.join(restarts_dir, expected_start_restart)
    
    if start_mode == "restart":
        if not os.path.exists(restart_path):
            print(f"Error: Required restart file {restart_path} not found!")
            sys.exit(1)
        restart_file_param = f"{base_dir}/{restart_path}"
    else:
        restart_file_param = "none"

    # 6. Generate LIS Configuration
    with open(template_path, "r") as f:
        template_text = f.read()

    config_out = f"generated/configs/lis_{exp_name}_{label}.config"
    
    config_text = template_text
    config_text = config_text.replace("__START_MODE__", start_mode)
    config_text = config_text.replace("__START_YEAR__", current_date.strftime("%Y"))
    config_text = config_text.replace("__START_MONTH__", current_date.strftime("%m"))
    config_text = config_text.replace("__START_DAY__", current_date.strftime("%d"))
    config_text = config_text.replace("__END_YEAR__", next_date.strftime("%Y"))
    config_text = config_text.replace("__END_MONTH__", next_date.strftime("%m"))
    config_text = config_text.replace("__END_DAY__", next_date.strftime("%d"))
    config_text = config_text.replace("__RESTART_FILE__", restart_file_param)
    config_text = config_text.replace("__OUTPUT_DIR__", f"{base_dir}/output/{label}")
    
    # 5b. Generate dynamic log directory
    log_dir_name = get_log_dir_name(current_date, period_length)
    log_dir_path = os.path.join(base_dir, "logs", log_dir_name)
    os.makedirs(log_dir_path, exist_ok=True)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", f"{log_dir_path}/lislog_{label}")

    with open(config_out, "w") as f:
        f.write(config_text)

    # 6. Expected Output Restart
    expected_end_restart = f"LIS_RST_NOAHMP401_{next_date.strftime('%Y%m%d')}0000.d01.nc"
        
    # 7. Generate SLURM Script
    # Determine what to submit next
    if next_date < global_end_date:
        next_cmd = f"python3 scripts/chain_spinup.py --current-date {next_date.strftime('%Y-%m-%d')} --submit"
    else:
        next_cmd = 'echo "Chain complete!"'

    job_out = f"generated/jobs/job_{exp_name}_{label}.sh"

    slurm_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name={exp_name}_{label}
#SBATCH --output={log_dir_path}/{exp_name}_{label}_%j.log
#SBATCH --error={log_dir_path}/{exp_name}_{label}_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
# Navigate to the ROOT of the NoahMP_Morocco project for LIS execution
cd {base_dir}/../../../

# Load computing environment (Modules, Conda, Compilers, etc.)
source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - {exp_name.upper()} - Period {label}"
echo " Start: {current_date.strftime('%Y-%m-%d')} | End: {next_date.strftime('%Y-%m-%d')} | Mode: {start_mode}"
echo "============================================="

# Execute LIS simulation from the root directory
time mpirun -n 32 ./src/lisf/lis/LIS -f {base_dir}/generated/configs/lis_{exp_name}_{label}.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

# Find the generated restart file required for the next period
RESTART_SRC=$(find {base_dir}/output/{label}/SURFACEMODEL -name "{expected_end_restart}" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    echo "Found restart file: $RESTART_SRC"
    cp "$RESTART_SRC" {base_dir}/{restarts_dir}/
    echo "Successfully copied restart file to {base_dir}/{restarts_dir}/"
else
    echo "ERROR: Restart file {expected_end_restart} not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
# Change back to spinup directory to submit the next job
cd {base_dir}
# Trigger the python script for the next chronological step
{next_cmd}
"""

    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)

    print(f"Generated {config_out} and {job_out}")

    # 8. Submit to Scheduler
    if args.submit:
        print(f"Submitting {job_out} to SLURM...")
        subprocess.run(["sbatch", job_out], check=True)

if __name__ == "__main__":
    main()
