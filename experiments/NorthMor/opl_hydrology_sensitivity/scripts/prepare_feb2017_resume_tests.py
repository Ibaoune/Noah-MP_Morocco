#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Prepares the restart resumption test for each scheme:
Takes the staged 2017-02-01 restart (produced by January 2017)
and runs a 2-day simulation (2017-02-01 to 2017-02-03) to prove restart continuity.
"""
import os

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"

experiments = [
    ("OL_R1_SIMGM", "simgm"),
    ("OL_R2_SIMTOP", "simtop"),
    ("OL_R3_SCHAAKE96", "schaake96"),
    ("OL_R4_BATS", "bats")
]

for exp_id, short_name in experiments:
    exp_dir = f"{base_proj}/experiments/{exp_id}"
    resume_dir = f"{exp_dir}/test_resume_feb"
    os.makedirs(f"{resume_dir}/output", exist_ok=True)
    os.makedirs(f"{resume_dir}/logs", exist_ok=True)

    template_file = f"{exp_dir}/templates/lis_{short_name}.config.template"
    with open(template_file, "r") as f:
        template_text = f.read()

    restart_file_param = f"{exp_dir}/restarts/LIS_RST_NOAHMP401_201702010000.d01.nc"
    output_dir = f"{resume_dir}/output"
    diag_file = f"{resume_dir}/logs/lislog_resume"

    config_text = template_text
    config_text = config_text.replace("__START_MODE__", "restart")
    config_text = config_text.replace("__START_YEAR__", "2017")
    config_text = config_text.replace("__START_MONTH__", "02")
    config_text = config_text.replace("__START_DAY__", "01")
    config_text = config_text.replace("__END_YEAR__", "2017")
    config_text = config_text.replace("__END_MONTH__", "02")
    config_text = config_text.replace("__END_DAY__", "03")
    config_text = config_text.replace("__RESTART_FILE__", restart_file_param)
    config_text = config_text.replace("__OUTPUT_DIR__", output_dir)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", diag_file)

    config_out = f"{resume_dir}/lis_resume_{short_name}.config"
    with open(config_out, "w") as f:
        f.write(config_text)

    slurm_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=res_{short_name}
#SBATCH --output={resume_dir}/logs/resume_{short_name}_%j.log
#SBATCH --error={resume_dir}/logs/resume_{short_name}_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {repo_root}
source arch/arch_toubkal.env

echo "============================================="
echo " Resumption Test from 2017-02-01 Restart"
echo " Experiment: {exp_id}"
echo " Start: 2017-02-01 | End: 2017-02-03"
echo " Restart File: {restart_file_param}"
echo " Config: {config_out}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {config_out}

echo "============================================="
echo " Resumption test succeeded for {exp_id}!"
echo "============================================="
"""
    job_out = f"{resume_dir}/run_resume_{short_name}.sh"
    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)
    print(f"Prepared resume test script for {exp_id}: {job_out}")

