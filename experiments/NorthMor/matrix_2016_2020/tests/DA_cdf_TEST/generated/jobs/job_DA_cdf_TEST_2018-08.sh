#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_cdf_TEST_2018-08
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_TEST/logs/082018/DA_cdf_TEST_2018-08_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_TEST/logs/082018/DA_cdf_TEST_2018-08_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - DA_cdf_TEST - Period 2018-08"
echo " Start: 2018-08-01 | End: 2018-09-01"
echo "============================================="

# Garde-fou d'intégrité spatiale CDF (bloque le job si incohérence de domaine)
/home/mohammad.elaabaribao/.conda/envs/smap-xai-audit/bin/python /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_TEST/scripts/check_cdf_domain.py \
    --config /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_TEST/generated/configs/lis_DA_cdf_TEST_2018-08.config \
    --run-dir $(pwd)

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_cdf_TEST/generated/configs/lis_DA_cdf_TEST_2018-08.config

echo "============================================="
echo " Period 2018-08 Complete! "
echo "============================================="
