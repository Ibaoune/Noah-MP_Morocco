#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"

# Read base template from matrix_2016_2020 OPL
with open(f"{repo_root}/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/templates/lis_opl.config.template", "r") as f:
    orig_template = f.read()

experiments = [
    ("OL_R1_SIMGM", 1, "simgm"),
    ("OL_R2_SIMTOP", 2, "simtop"),
    ("OL_R3_SCHAAKE96", 3, "schaake96"),
    ("OL_R4_BATS", 4, "bats")
]

for exp_id, opt_run, short_name in experiments:
    exp_dir = f"{base_proj}/experiments/{exp_id}"
    os.makedirs(f"{exp_dir}/config", exist_ok=True)
    os.makedirs(f"{exp_dir}/templates", exist_ok=True)
    os.makedirs(f"{exp_dir}/scripts", exist_ok=True)
    os.makedirs(f"{exp_dir}/restarts", exist_ok=True)
    os.makedirs(f"{exp_dir}/logs", exist_ok=True)
    os.makedirs(f"{exp_dir}/output", exist_ok=True)
    os.makedirs(f"{exp_dir}/generated/configs", exist_ok=True)
    os.makedirs(f"{exp_dir}/generated/jobs", exist_ok=True)

    # 1. Template
    lines = orig_template.splitlines()
    new_lines = []
    for line in lines:
        if "Noah-MP.4.0.1 runoff and groundwater option:" in line:
            new_lines.append(f"Noah-MP.4.0.1 runoff and groundwater option:                  {opt_run}  # {opt_run}={short_name.upper()}")
        else:
            new_lines.append(line)
    template_content = "\n".join(new_lines) + "\n"

    template_file = f"{exp_dir}/templates/lis_{short_name}.config.template"
    with open(template_file, "w") as f:
        f.write(template_content)

    # 2. Config experiment.ini
    ini_content = f"""# Author: M. El Aabaribaoune (@um6p)
# OPL Hydrology Sensitivity Pilot (2017-2018)
[Experiment]
# Simulation start date (Format: YYYY-MM-DD)
StartDate = 2017-01-01

# Simulation end date (Format: YYYY-MM-DD). 2017 = equilibrium adjustment, 2018 = evaluation.
EndDate   = 2019-01-02

# Length of a single simulation chunk
PeriodLength = 1M

# Initialization mode for the VERY FIRST period defined by StartDate.
InitMode = restart

# Experiment name
ExperimentName = {short_name}

# Experiment Identifier
ExperimentId = {exp_id}

# Runoff option (1=SIMGM, 2=SIMTOP, 3=SCHAAKE96, 4=BATS)
RunoffOption = {opt_run}

# Path to the base LIS configuration template
TemplateFile = templates/lis_{short_name}.config.template
"""
    with open(f"{exp_dir}/config/experiment.ini", "w") as f:
        f.write(ini_content)

    # 3. chain_opl.py with resume capability without overwriting
    chain_script = f"""#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
\"\"\"
Daisy-Chaining Script for OPL Hydrology Sensitivity Experiment: {exp_id}
Period: 2017-01-01 to 2019-01-01 (Monthly chunks)
Includes resume capability: detects already completed months and advances automatically.
\"\"\"

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
        print(f"Error: Config file {{config_path}} not found.")
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
        raise ValueError(f"Unsupported PeriodLength: {{period_length}}")

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
    parser = argparse.ArgumentParser(description="Daisy-chaining script for {exp_id}.")
    parser.add_argument("--current-date", required=True, help="Current date to run (YYYY-MM-DD)")
    parser.add_argument("--submit", action="store_true", help="Submit the job to SLURM immediately")
    parser.add_argument("--force", action="store_true", help="Force rerun even if already completed")
    
    args = parser.parse_args()
    
    base_dir = "{exp_dir}"
    repo_root = "{repo_root}"
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
        print(f"End date {{global_end_date.strftime('%Y-%m-%d')}} reached. Chain is complete for {exp_id}!")
        sys.exit(0)

    next_date = get_next_date(current_date, period_length)
    if next_date > global_end_date:
        next_date = global_end_date

    label = get_label(current_date, period_length)
    restarts_dir = "restarts"
    expected_start_restart = f"LIS_RST_NOAHMP401_{{current_date.strftime('%Y%m%d')}}0000.d01.nc"
    expected_end_restart = f"LIS_RST_NOAHMP401_{{next_date.strftime('%Y%m%d')}}0000.d01.nc"

    # RESUME LOGIC: Check if this period was ALREADY completed successfully
    staged_end_restart = os.path.join(restarts_dir, expected_end_restart)
    output_dir = f"{{base_dir}}/output/{{label}}"
    
    if not args.force and os.path.exists(staged_end_restart) and os.path.exists(output_dir):
        hist_files = glob.glob(f"{{output_dir}}/SURFACEMODEL/**/LIS_HIST_*.nc", recursive=True)
        # For a full month, we expect >= 28 history files
        if len(hist_files) >= 28:
            print(f"[{exp_id}] Period {{label}} is ALREADY completed ({{len(hist_files)}} history files and {{expected_end_restart}} present).")
            print("Skipping to avoid overwriting validated data and advancing to next period...")
            if next_date < global_end_date:
                sub_args = ["python3", "scripts/chain_opl.py", "--current-date", next_date.strftime("%Y-%m-%d")]
                if args.submit:
                    sub_args.append("--submit")
                subprocess.run(sub_args, check=True)
            sys.exit(0)

    restart_path = os.path.join(restarts_dir, expected_start_restart)
    if not os.path.exists(restart_path):
        print(f"Error: Required starting restart file {{restart_path}} not found in {{base_dir}}!")
        sys.exit(1)
    restart_file_param = f"{{base_dir}}/{{restart_path}}"

    start_mode = "restart"
    os.makedirs("generated/configs", exist_ok=True)
    os.makedirs("generated/jobs", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    os.makedirs(f"output/{{label}}", exist_ok=True)

    with open(template_path, "r") as f:
        template_text = f.read()

    config_out = f"generated/configs/lis_{{exp_name}}_{{label}}.config"
    
    config_text = template_text
    config_text = config_text.replace("__START_MODE__", start_mode)
    config_text = config_text.replace("__START_YEAR__", current_date.strftime("%Y"))
    config_text = config_text.replace("__START_MONTH__", current_date.strftime("%m"))
    config_text = config_text.replace("__START_DAY__", current_date.strftime("%d"))
    config_text = config_text.replace("__END_YEAR__", next_date.strftime("%Y"))
    config_text = config_text.replace("__END_MONTH__", next_date.strftime("%m"))
    config_text = config_text.replace("__END_DAY__", next_date.strftime("%d"))
    config_text = config_text.replace("__RESTART_FILE__", restart_file_param)
    config_text = config_text.replace("__OUTPUT_DIR__", f"{{base_dir}}/output/{{label}}")
    
    log_dir_name = get_log_dir_name(current_date, period_length)
    log_dir_path = os.path.join(base_dir, "logs", log_dir_name)
    os.makedirs(log_dir_path, exist_ok=True)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", f"{{log_dir_path}}/lislog_{{label}}")

    with open(config_out, "w") as f:
        f.write(config_text)
        
    if next_date < global_end_date:
        next_cmd = f"python3 scripts/chain_opl.py --current-date {{next_date.strftime('%Y-%m-%d')}} --submit"
    else:
        next_cmd = "echo \\"Chain complete for {exp_id}!\\""

    job_out = f"generated/jobs/job_{{exp_name}}_{{label}}.sh"

    slurm_script = f\"\"\"#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name={exp_id}_{{label}}
#SBATCH --output={{log_dir_path}}/{exp_id}_{{label}}_%j.log
#SBATCH --error={{log_dir_path}}/{exp_id}_{{label}}_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {{repo_root}}
source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - {exp_id} - Period {{label}}"
echo " Start: {{current_date.strftime('%Y-%m-%d')}} | End: {{next_date.strftime('%Y-%m-%d')}}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {{base_dir}}/generated/configs/lis_{{exp_name}}_{{label}}.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

RESTART_SRC=$(find {{base_dir}}/output/{{label}}/SURFACEMODEL -name "{{expected_end_restart}}" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    echo "Found restart file: $RESTART_SRC"
    cp "$RESTART_SRC" {{base_dir}}/{{restarts_dir}}/
    echo "Successfully copied restart file to {{base_dir}}/{{restarts_dir}}/"
else
    echo "ERROR: Restart file {{expected_end_restart}} not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
cd {{base_dir}}
{{next_cmd}}
\"\"\"

    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)

    print(f"[{exp_id}] Generated {{config_out}} and {{job_out}}")

    if args.submit:
        print(f"Submitting {{job_out}} to SLURM...")
        subprocess.run(["sbatch", job_out], check=True)

if __name__ == "__main__":
    main()
"""
    chain_file = f"{exp_dir}/scripts/chain_opl.py"
    with open(chain_file, "w") as f:
        f.write(chain_script)
    os.chmod(chain_file, 0o755)
    print(f"Configured {exp_id} with resume logic")

