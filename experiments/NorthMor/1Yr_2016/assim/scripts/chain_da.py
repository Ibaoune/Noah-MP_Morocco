#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Daisy-Chaining Script for 1Yr_2016 DA (Assimilation) Experiments
"""

import argparse
import os
import sys
import subprocess
import configparser
from datetime import datetime
from dateutil.relativedelta import relativedelta

def read_config(config_path: str) -> configparser.SectionProxy:
    config = configparser.ConfigParser()
    if not os.path.exists(config_path):
        print(f"Error: Config file {config_path} not found.")
        sys.exit(1)
    config.read(config_path)
    return config['Experiment']

def get_next_date(current_date: datetime, period_length: str) -> datetime:
    if period_length == '1Y':
        return current_date + relativedelta(years=1)
    elif period_length == '1M':
        return current_date + relativedelta(months=1)
    elif period_length == '1D':
        return current_date + relativedelta(days=1)
    else:
        raise ValueError(f"Unsupported PeriodLength: {period_length}")

def get_label(current_date: datetime, period_len: str) -> str:
    if period_len == "1Y":
        return current_date.strftime("%Y")
    elif period_len == "1M":
        return current_date.strftime("%Y-%m")
    elif period_len == "1D":
        return current_date.strftime("%Y-%m-%d")
    return current_date.strftime("%Y")

def get_log_dir_name(current_date, period_len):
    if period_len == "1Y":
        return current_date.strftime("%Y")
    elif period_len == "1M":
        return current_date.strftime("%m%Y")
    elif period_len == "1D":
        return current_date.strftime("%Y%m%d")
    return current_date.strftime("%Y")

def main():
    parser = argparse.ArgumentParser(description="Daisy-chaining script for DA experiments.")
    parser.add_argument("--current-date", required=True, help="Current date to run (YYYY-MM-DD)")
    parser.add_argument("--submit", action="store_true", help="Submit the job to SLURM immediately")
    
    args = parser.parse_args()
    
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/assim"
    os.chdir(base_dir)

    config_path = "config/experiment.ini"
    cfg = read_config(config_path)

    global_start_date = datetime.strptime(cfg['StartDate'], "%Y-%m-%d")
    global_end_date = datetime.strptime(cfg['EndDate'], "%Y-%m-%d")
    period_length = cfg['PeriodLength']
    exp_name = cfg['ExperimentName']
    template_path = cfg['TemplateFile']
    
    current_date = datetime.strptime(args.current_date, "%Y-%m-%d")
    
    if current_date >= global_end_date:
        print(f"End date {global_end_date.strftime('%Y-%m-%d')} reached. Chain is complete!")
        sys.exit(0)

    next_date = get_next_date(current_date, period_length)
    if next_date > global_end_date:
        next_date = global_end_date

    label = get_label(current_date, period_length)
    start_mode = "restart"

    os.makedirs("generated/configs", exist_ok=True)
    os.makedirs("generated/jobs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(f"output/{label}", exist_ok=True)

    restarts_dir_surf = "restarts/surf"
    restarts_dir_pert = "restarts/pert"
    
    expected_start_surf_restart = f"LIS_RST_NOAHMP401_{current_date.strftime('%Y%m%d')}0000.d01.nc"
    expected_start_pert_restart = f"LIS_DAPERT_{current_date.strftime('%Y%m%d')}0000.d01.bin"
    
    surf_restart_path = os.path.join(restarts_dir_surf, expected_start_surf_restart)
    pert_restart_path = os.path.join(restarts_dir_pert, expected_start_pert_restart)
    
    if not os.path.exists(surf_restart_path):
        print(f"Error: Required surface restart file {surf_restart_path} not found!")
        sys.exit(1)
        
    if not os.path.exists(pert_restart_path):
        print(f"Error: Required perturbation restart file {pert_restart_path} not found!")
        sys.exit(1)

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
    config_text = config_text.replace("__SURF_RESTART_FILE__", f"{base_dir}/{surf_restart_path}")
    config_text = config_text.replace("__PERT_RESTART_FILE__", f"{base_dir}/{pert_restart_path}")
    config_text = config_text.replace("__OUTPUT_DIR__", f"{base_dir}/output/{label}")
    
    log_dir_name = get_log_dir_name(current_date, period_length)
    log_dir_path = os.path.join(base_dir, "logs", log_dir_name)
    os.makedirs(log_dir_path, exist_ok=True)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", f"{log_dir_path}/lislog_{label}")

    with open(config_out, "w") as f:
        f.write(config_text)

    expected_end_surf_restart = f"LIS_RST_NOAHMP401_{next_date.strftime('%Y%m%d')}0000.d01.nc"
    expected_end_pert_restart = f"LIS_DAPERT_{next_date.strftime('%Y%m%d')}0000.d01.bin"
        
    if next_date < global_end_date:
        next_cmd = f"python3 scripts/chain_da.py --current-date {next_date.strftime('%Y-%m-%d')} --submit"
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
cd {base_dir}/../../../../

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - DA - Period {label}"
echo " Start: {current_date.strftime('%Y-%m-%d')} | End: {next_date.strftime('%Y-%m-%d')}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {base_dir}/generated/configs/lis_{exp_name}_{label}.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

SURF_RST=$(find {base_dir}/output/{label}/SURFACEMODEL -name "{expected_end_surf_restart}" | head -n 1)
PERT_RST=$(find {base_dir}/output/{label}/DAPERT -name "{expected_end_pert_restart}" | head -n 1)

if [ -n "$SURF_RST" ] && [ -f "$SURF_RST" ] && [ -n "$PERT_RST" ] && [ -f "$PERT_RST" ]; then
    echo "Found restart files."
    cp "$SURF_RST" {base_dir}/{restarts_dir_surf}/
    cp "$PERT_RST" {base_dir}/{restarts_dir_pert}/
    echo "Successfully copied restarts to {base_dir}/restarts/"
else
    echo "ERROR: Restart files not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
cd {base_dir}
{next_cmd}
"""

    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)

    print(f"Generated {config_out} and {job_out}")

    if args.submit:
        print(f"Submitting {job_out} to SLURM...")
        subprocess.run(["sbatch", job_out], check=True)

if __name__ == "__main__":
    main()
