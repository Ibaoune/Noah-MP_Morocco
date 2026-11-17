#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=OL_rsf2_2018
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_rsf2_hourly_2018/logs/slurm_OL_rsf2_2018_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_rsf2_hourly_2018/logs/slurm_OL_rsf2_2018_%j.err
#SBATCH --time=03:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_rsf2_hourly_2018/config/lis_OL_rsf2_hourly_2018.config"

echo "============================================="
echo " LIS NorthMor - OL_rsf2_hourly_2018 (1 year)"
echo " Start: 2018-01-01 | End: 2019-01-01"
echo " Config: ${CONFIG}"
echo " Surface resistance: 2 (Sellers 1992)"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/make/LIS -f "${CONFIG}"

echo "============================================="
echo " Simulation terminée avec succès "
echo "============================================="
