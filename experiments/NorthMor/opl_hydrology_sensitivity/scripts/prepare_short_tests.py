#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"

experiments = [
    ("OL_R1_SIMGM", 1, "simgm"),
    ("OL_R2_SIMTOP", 2, "simtop"),
    ("OL_R3_SCHAAKE96", 3, "schaake96"),
    ("OL_R4_BATS", 4, "bats")
]

for exp_id, opt_run, short_name in experiments:
    exp_dir = f"{base_proj}/experiments/{exp_id}"
    test_dir = f"{exp_dir}/test_short"
    os.makedirs(f"{test_dir}/output", exist_ok=True)
    os.makedirs(f"{test_dir}/logs", exist_ok=True)

    template_file = f"{exp_dir}/templates/lis_{short_name}.config.template"
    with open(template_file, "r") as f:
        template_text = f.read()

    restart_file_param = f"{exp_dir}/restarts/LIS_RST_NOAHMP401_201701010000.d01.nc"
    output_dir = f"{test_dir}/output"
    diag_file = f"{test_dir}/logs/lislog_test"

    config_text = template_text
    config_text = config_text.replace("__START_MODE__", "restart")
    config_text = config_text.replace("__START_YEAR__", "2017")
    config_text = config_text.replace("__START_MONTH__", "01")
    config_text = config_text.replace("__START_DAY__", "01")
    config_text = config_text.replace("__END_YEAR__", "2017")
    config_text = config_text.replace("__END_MONTH__", "01")
    config_text = config_text.replace("__END_DAY__", "03")
    config_text = config_text.replace("__RESTART_FILE__", restart_file_param)
    config_text = config_text.replace("__OUTPUT_DIR__", output_dir)
    config_text = config_text.replace("__DIAGNOSTIC_OUT__", diag_file)

    config_out = f"{test_dir}/lis_test_{short_name}.config"
    with open(config_out, "w") as f:
        f.write(config_text)

    slurm_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=test_{short_name}
#SBATCH --output={test_dir}/logs/test_{short_name}_%j.log
#SBATCH --error={test_dir}/logs/test_{short_name}_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {repo_root}

source arch/arch_toubkal.env

echo "============================================="
echo " Short Sanity Test (2 days) - {exp_id}"
echo " Start: 2017-01-01 | End: 2017-01-03"
echo " Config: {config_out}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {config_out}

echo "============================================="
echo " Test completed successfully for {exp_id}!"
echo "============================================="
"""
    job_out = f"{test_dir}/run_test_{short_name}.sh"
    with open(job_out, "w") as f:
        f.write(slurm_script)
    os.chmod(job_out, 0o755)

    print(f"Prepared short test for {exp_id}: {job_out}")
