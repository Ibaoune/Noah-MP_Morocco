#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=test_simtop
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_short/logs/test_simtop_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_short/logs/test_simtop_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

echo "============================================="
echo " Short Sanity Test (2 days) - OL_R2_SIMTOP"
echo " Start: 2017-01-01 | End: 2017-01-03"
echo " Config: /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_short/lis_test_simtop.config"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_short/lis_test_simtop.config

echo "============================================="
echo " Test completed successfully for OL_R2_SIMTOP!"
echo "============================================="
