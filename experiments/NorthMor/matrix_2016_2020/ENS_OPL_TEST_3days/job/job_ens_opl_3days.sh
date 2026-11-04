#!/bin/bash
#SBATCH --job-name=ENS_OPL_3d
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/ENS_OPL_TEST_3days/logs/ens_opl_3d_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/ENS_OPL_TEST_3days/logs/ens_opl_3d_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - Ensemble Open Loop Test (3 days)"
echo " Start: 2018-01-01 | End: 2018-01-04"
echo " Binary: ./src/lisf/lis/LIS"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/ENS_OPL_TEST_3days/config/lis_ens_opl_3days.config

echo "============================================="
echo " Ensemble Open Loop Test Complete"
echo "============================================="
