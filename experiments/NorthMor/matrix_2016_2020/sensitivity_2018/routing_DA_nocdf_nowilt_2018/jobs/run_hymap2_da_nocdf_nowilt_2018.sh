#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=hm2_nowilt_18
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/routing_DA_nocdf_nowilt_2018/logs/slurm_hymap2_nowilt_18_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/routing_DA_nocdf_nowilt_2018/logs/slurm_hymap2_nowilt_18_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

echo "=== 1. Remapping du ruissellement DA_nocdf_nowilt_2018 vers 180x120 ==="
python3 experiments/NorthMor/matrix_2016_2020/sensitivity_2018/routing_DA_nocdf_nowilt_2018/scripts/remap_runoff_nowilt_2018.py

echo "=== 2. Routage HyMAP2 pour l'année 2018 ==="
CONFIG="experiments/NorthMor/matrix_2016_2020/sensitivity_2018/routing_DA_nocdf_nowilt_2018/config/lis_hymap2_da_nocdf_nowilt_2018.config"
/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "=== Fin du run HYMAP2 DA NoWilt 2018 ==="
