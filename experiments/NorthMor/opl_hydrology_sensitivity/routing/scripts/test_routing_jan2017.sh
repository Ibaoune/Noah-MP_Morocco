#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=hm2_val_0117
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --chdir=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/slurm_hm2_val_0117_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/slurm_hm2_val_0117_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/test_jan2017/lis_hymap2_simgm_jan2017.config"
echo "=== Testing HyMAP-2 Local Routing on January 2017 ==="
echo "Date debut : $(date)"
echo "Config     : ${CONFIG}"

time mpirun -n 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin   : $(date)"
echo "=== HyMAP-2 Jan 2017 run finished successfully ==="
