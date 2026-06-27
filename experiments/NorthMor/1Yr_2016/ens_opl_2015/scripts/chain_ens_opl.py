#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Script to run the Ensemble Open Loop for 2015 to generate perturbation restarts.
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

def main():
    parser = argparse.ArgumentParser(description="Run Ensemble OPL for 2015.")
    parser.add_argument("--submit", action="store_true", help="Submit the job to SLURM immediately")
    args = parser.parse_args()
    
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015"
    os.chdir(base_dir)

    config_path = "config/experiment.ini"
    cfg = read_config(config_path)

    start_date = datetime.strptime(cfg['StartDate'], "%Y-%m-%d")
    end_date = datetime.strptime(cfg['EndDate'], "%Y-%m-%d")
    exp_name = cfg['ExperimentName']
    template_path = cfg['TemplateFile']
    start_mode = cfg.get('InitMode', 'restart')
    
    label = start_date.strftime("%Y")

    os.makedirs("generated/configs", exist_ok=True)
    os.makedirs("generated/jobs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(f"output/{label}", exist_ok=True)
    
    # We need the spinup restart file from end of 2014 / start of 2015
    # The spinup directory contains LIS_RST_NOAHMP401_201501010000.d01.nc
    spinup_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/restarts"
    expected_start_restart = f"LIS_RST_NOAHMP401_{start_date.strftime('%Y%m%d')}0000_ens20.d01.nc"
    restart_path = os.path.join(spinup_dir, expected_start_restart)
    
    if not os.path.exists(restart_path):
        print(f"Error: Required spinup restart file {restart_path} not found!")
        sys.exit(1)

    with open(template_path, "r") as f:
        template_text = f.read()

    config_out = f"generated/configs/lis_{exp_name}_{label}.config"
    
    config_text = template_text
    config_text = config_text.replace("__START_MODE__", start_mode)
    config_text = config_text.replace("__START_YEAR__", start_date.strftime("%Y"))
    config_text = config_text.replace("__START_MONTH__", start_date.strftime("%m"))
    config_text = config_text.replace("__START_DAY__", start_date.strftime("%d"))
    config_text = config_text.replace("__END_YEAR__", end_date.strftime("%Y"))
    config_text = config_text.replace("__END_MONTH__", end_date.strftime("%m"))
    config_text = config_text.replace("__END_DAY__", end_date.strftime("%d"))
    config_text = config_text.replace("__SURF_RESTART_FILE__", restart_path)
    config_text = config_text.replace("__OUTPUT_DIR__", f"{base_dir}/output/{label}")
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", f"{base_dir}/logs/lislog_{label}")

    with open(config_out, "w") as f:
        f.write(config_text)

    # Expected Outputs at the end of 2015
    expected_end_surf_restart = f"LIS_RST_NOAHMP401_{end_date.strftime('%Y%m%d')}0000.d01.nc"
    expected_end_pert_restart = f"LIS_DAPERT_{end_date.strftime('%Y%m%d')}0000.d01.bin"

    job_out = f"generated/jobs/job_{exp_name}_{label}.sh"

    slurm_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name={exp_name}_{label}
#SBATCH --output={base_dir}/logs/{exp_name}_{label}_%j.log
#SBATCH --error={base_dir}/logs/{exp_name}_{label}_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {base_dir}/../../../../

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - {exp_name.upper()} - Year {label}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {base_dir}/generated/configs/lis_{exp_name}_{label}.config

echo "============================================="
echo " Post-processing: Copying Restarts to 2016 DA setup "
echo "============================================="

SURF_RST=$(find {base_dir}/output/{label}/SURFACEMODEL -name "{expected_end_surf_restart}" | head -n 1)
PERT_RST=$(find {base_dir}/output/{label}/DAPERT -name "{expected_end_pert_restart}" | head -n 1)

DA_DIR="{base_dir}/../assim/restarts"

if [ -n "$SURF_RST" ] && [ -f "$SURF_RST" ] && [ -n "$PERT_RST" ] && [ -f "$PERT_RST" ]; then
    echo "Found restart files."
    cp "$SURF_RST" $DA_DIR/surf/
    cp "$PERT_RST" $DA_DIR/pert/
    echo "Successfully copied restarts to $DA_DIR"
else
    echo "ERROR: Restart files not found in output directory!"
    exit 1
fi

echo "Done."
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
