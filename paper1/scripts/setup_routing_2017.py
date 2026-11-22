#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
SRC_CFG = os.path.join(BASE_DIR, "paper1/runs/routing/configs/lis_hymap2_ol_daic_2018_linres0.config")

with open(SRC_CFG, "r") as f:
    template = f.read()

experiments_2017 = [
    "OL_DAIC_2017",
    "ENS_OPL_2017",
    "DA_nocdf_nowilt_2017"
]

for exp in experiments_2017:
    cfg = template
    # Replace dates: 2018 -> 2017, 2019 -> 2018
    cfg = cfg.replace("Starting year:                          2018", "Starting year:                          2017")
    cfg = cfg.replace("Ending year:                            2019", "Ending year:                            2018")
    
    # Replace restart: 201712312345 -> 201612312345
    cfg = cfg.replace("ROUTING/201712/LIS_RST_HYMAP2_router_201712312345.d01.nc", "ROUTING/201612/LIS_RST_HYMAP2_router_201612312345.d01.nc")
    
    # Replace exp names
    cfg = cfg.replace("OL_DAIC_2018_linres0", f"{exp}_linres0")
    cfg = cfg.replace("OL_DAIC_2018", exp)
    
    cfg_out = os.path.join(BASE_DIR, f"paper1/runs/routing/configs/lis_hymap2_{exp.lower()}_linres0.config")
    with open(cfg_out, "w") as f:
        f.write(cfg)
    print(f"Generated {cfg_out}")
    
    job_text = f"""#!/bin/bash
#SBATCH --job-name=hm2_{exp[:10]}
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --chdir=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
#SBATCH --output=paper1/runs/routing/logs/slurm_hymap2_{exp.lower()}_linres0_%j.out
#SBATCH --error=paper1/runs/routing/logs/slurm_hymap2_{exp.lower()}_linres0_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="paper1/runs/routing/configs/lis_hymap2_{exp.lower()}_linres0.config"
LOG_DIR="paper1/runs/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/{exp}_linres0"
mkdir -p "${{LOG_DIR}}" "${{OUT_DIR}}"

echo "=== Lancement HYMAP2 {exp} (2017, linres=0, restart DA_nocdf 2017-01-01) ==="
echo "Date debut : $(date)"
echo "Config     : ${{CONFIG}}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${{CONFIG}}"

echo "Date fin   : $(date)"
echo "Code retour: $?"
echo "=== Fin du run HYMAP2 {exp} (linres=0) ==="
"""
    job_out = os.path.join(BASE_DIR, f"paper1/runs/routing/jobs/run_hymap2_{exp.lower()}_linres0.sh")
    with open(job_out, "w") as f:
        f.write(job_text)
    os.chmod(job_out, 0o775)
    print(f"Generated {job_out}")
