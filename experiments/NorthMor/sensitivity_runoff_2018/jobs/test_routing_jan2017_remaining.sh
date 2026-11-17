#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=hm2_val_rem
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:20:00
#SBATCH --chdir=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/slurm_hm2_val_rem_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/slurm_hm2_val_rem_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

for exp in simtop schaake96 bats; do
    CONFIG="experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/test_jan2017/lis_hymap2_${exp}_jan2017.config"
    echo "=== Running HyMAP-2 Jan 2017 for ${exp} ==="
    time mpirun -n 16 ./src/lisf/lis/LIS -f "${CONFIG}"
    echo "=== Done ${exp} ==="
done
