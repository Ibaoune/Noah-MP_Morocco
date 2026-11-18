#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Daisy-chaining script for OL_R3_SCHAAKE96 (Noah-MP 4.0.1 Open-Loop).
Manages sequential monthly runs, restart chaining, and strict operational validation:
- Validates exact expected days for the month.
- Validates presence and non-zero size of every single expected LIS_HIST file.
- Validates terminal restart file existence and integrity (> 1.0 MB).
- Prevents re-running or overwriting already completed and validated months.
"""

import argparse
import os
import sys
import glob
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
    if period_len == '1Y':
        return current_date.strftime("%Y")
    elif period_len == '1M':
        return current_date.strftime("%Y-%m")
    elif period_len == '1D':
        return current_date.strftime("%Y-%m-%d")
    return current_date.strftime("%Y")

def get_log_dir_name(current_date, period_len):
    if period_len == '1Y':
        return current_date.strftime("%Y")
    elif period_len == '1M':
        return current_date.strftime("%m%Y")
    elif period_len == '1D':
        return current_date.strftime("%Y%m%d")
    return current_date.strftime("%Y")

def main():
    parser = argparse.ArgumentParser(description="Daisy-chaining script for OL_R3_SCHAAKE96.")
    parser.add_argument("--current-date", required=True, help="Current date to run (YYYY-MM-DD)")
    parser.add_argument("--submit", action="store_true", help="Submit the job to SLURM immediately")
    parser.add_argument("--force", action="store_true", help="Force rerun even if already completed")
    
    args = parser.parse_args()
    
    base_dir = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96"
    repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
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
        print(f"End date {global_end_date.strftime('%Y-%m-%d')} reached. Chain is complete for OL_R3_SCHAAKE96!")
        sys.exit(0)

    next_date = get_next_date(current_date, period_length)
    if next_date > global_end_date:
        next_date = global_end_date

    label = get_label(current_date, period_length)
    restarts_dir = "restarts"
    expected_start_restart = f"LIS_RST_NOAHMP401_{current_date.strftime('%Y%m%d')}0000.d01.nc"
    expected_end_restart = f"LIS_RST_NOAHMP401_{next_date.strftime('%Y%m%d')}0000.d01.nc"

    # STRICT MONTHLY VALIDATION & RESUME LOGIC
    num_days = (next_date - current_date).days
    expected_hist_files = [
        f"LIS_HIST_{(current_date + relativedelta(days=d)).strftime('%Y%m%d')}0000.d01.nc"
        for d in range(1, num_days + 1)
    ]

    staged_end_restart = os.path.join(restarts_dir, expected_end_restart)
    output_dir = f"{base_dir}/output/{label}"
    
    month_fully_valid = True
    missing_items = []

    if not os.path.exists(output_dir):
        month_fully_valid = False
        missing_items.append("output_dir_missing")
    if not os.path.exists(staged_end_restart):
        month_fully_valid = False
        missing_items.append(f"restart_missing:{expected_end_restart}")
    elif os.path.getsize(staged_end_restart) < 1000000:
        month_fully_valid = False
        missing_items.append(f"restart_too_small:{os.path.getsize(staged_end_restart)}_bytes")
    
    if month_fully_valid:
        for hf in expected_hist_files:
            matches = glob.glob(f"{output_dir}/SURFACEMODEL/**/{hf}", recursive=True)
            if not matches or os.path.getsize(matches[0]) < 100000:
                month_fully_valid = False
                missing_items.append(f"hist_missing_or_corrupt:{hf}")

    if not args.force and month_fully_valid:
        print(f"[OL_R3_SCHAAKE96] Period {label} is ALREADY COMPLETED and RIGOROUSLY VALIDATED (all {num_days}/{num_days} daily history files and restart {expected_end_restart} present).")
        print("Skipping to avoid overwriting validated data and advancing to next period...")
        if next_date < global_end_date:
            sub_args = ["python3", "scripts/chain_opl.py", "--current-date", next_date.strftime("%Y-%m-%d")]
            if args.submit:
                sub_args.append("--submit")
            subprocess.run(sub_args, check=True)
        sys.exit(0)

    restart_path = os.path.join(restarts_dir, expected_start_restart)
    if not os.path.exists(restart_path):
        print(f"Error: Required starting restart file {restart_path} not found in {base_dir}!")
        sys.exit(1)
    restart_file_param = f"{base_dir}/{restart_path}"

    start_mode = "restart"
    os.makedirs("generated/configs", exist_ok=True)
    os.makedirs("generated/jobs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(f"output/{label}", exist_ok=True)

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
    
    log_dir_name = get_log_dir_name(current_date, period_length)
    log_dir_path = os.path.join(base_dir, "logs", log_dir_name)
    os.makedirs(log_dir_path, exist_ok=True)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", f"{log_dir_path}/lislog_{label}")

    with open(config_out, "w") as f:
        f.write(config_text)
        
    if next_date < global_end_date:
        next_cmd = f"python3 scripts/chain_opl.py --current-date {next_date.strftime('%Y-%m-%d')} --submit"
    else:
        next_cmd = "echo \"Chain complete for OL_R3_SCHAAKE96!\""

    job_out = f"generated/jobs/job_{exp_name}_{label}.sh"

    slurm_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=OL_R3_SCHAAKE96_{label}
#SBATCH --output={log_dir_path}/OL_R3_SCHAAKE96_{label}_%j.log
#SBATCH --error={log_dir_path}/OL_R3_SCHAAKE96_{label}_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {repo_root}
source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - OL_R3_SCHAAKE96 - Period {label}"
echo " Start: {current_date.strftime('%Y-%m-%d')} | End: {next_date.strftime('%Y-%m-%d')}"
echo " Expected days: {num_days}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {base_dir}/generated/configs/lis_{exp_name}_{label}.config

echo "============================================="
echo " Post-processing & Strict Operational Audit "
echo "============================================="

# 1. Audit restart
RESTART_SRC=$(find {base_dir}/output/{label}/SURFACEMODEL -name "{expected_end_restart}" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    RST_SZ=$(stat -c%s "$RESTART_SRC" 2>/dev/null || stat -f%z "$RESTART_SRC" 2>/dev/null || echo 0)
    if [ "$RST_SZ" -lt 1000000 ]; then
        echo "ERROR: Restart file $RESTART_SRC is corrupted or too small ($RST_SZ bytes)!"
        exit 1
    fi
    echo "Found valid terminal restart: $RESTART_SRC ($RST_SZ bytes)"
    cp "$RESTART_SRC" {base_dir}/{restarts_dir}/
    echo "Successfully copied restart file to {base_dir}/{restarts_dir}/"
else
    echo "ERROR: Terminal restart file {expected_end_restart} not found in output directory!"
    exit 1
fi

# 2. Audit exact count of history files
HIST_COUNT=$(find {base_dir}/output/{label}/SURFACEMODEL -name "LIS_HIST_*.nc" | wc -l)
if [ "$HIST_COUNT" -ne {num_days} ]; then
    echo "ERROR: Expected exactly {num_days} history files for period {label}, found $HIST_COUNT!"
    exit 1
fi
echo "Verified exact count: $HIST_COUNT/{num_days} daily history files present."

echo "============================================="
echo " Period {label} successfully completed and validated."
echo " Submitting next period "
echo "============================================="
cd {base_dir}
{next_cmd}
"""

    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)

    print(f"[OL_R3_SCHAAKE96] Generated {config_out} and {job_out}")

    if args.submit:
        print(f"Submitting {job_out} to SLURM...")
        subprocess.run(["sbatch", job_out], check=True)

if __name__ == "__main__":
    main()
