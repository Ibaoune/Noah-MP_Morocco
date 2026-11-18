#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
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
    log_dir = f"{exp_dir}/logs/012017"
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(f"{exp_dir}/output/2017-01", exist_ok=True)

    cfg_file = f"{exp_dir}/generated/configs/lis_{short_name}_2017-01.config"
    job_file = f"{exp_dir}/generated/jobs/job_{short_name}_val_2017-01.sh"

    script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=val_{short_name}_0117
#SBATCH --output={log_dir}/{short_name}_val_2017-01_%j.log
#SBATCH --error={log_dir}/{short_name}_val_2017-01_%j.err
#SBATCH --time=01:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {repo_root}
source arch/arch_toubkal.env

echo "============================================="
echo " Monthly Validation: {exp_id} - 2017-01"
echo " Start: 2017-01-01 | End: 2017-02-01"
echo " Config: {cfg_file}"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f {cfg_file}

echo "============================================="
echo " Verifying and Staging Restart for 2017-02-01 "
echo "============================================="

EXPECTED_RST="LIS_RST_NOAHMP401_201702010000.d01.nc"
RST_SRC=$(find {exp_dir}/output/2017-01/SURFACEMODEL -name "$EXPECTED_RST" | head -n 1)

if [ -n "$RST_SRC" ] && [ -f "$RST_SRC" ]; then
    echo "SUCCESS: Found restart file $RST_SRC"
    cp "$RST_SRC" {exp_dir}/restarts/
    echo "Copied to {exp_dir}/restarts/$EXPECTED_RST"
else
    echo "ERROR: Restart file $EXPECTED_RST not found in {exp_dir}/output/2017-01/SURFACEMODEL!"
    exit 1
fi

echo "Validation run for 2017-01 complete. STOPPING without submitting next month."
"""
    with open(job_file, "w") as f:
        f.write(script)
    os.chmod(job_file, 0o755)
    print(f"Created validation job: {job_file}")

