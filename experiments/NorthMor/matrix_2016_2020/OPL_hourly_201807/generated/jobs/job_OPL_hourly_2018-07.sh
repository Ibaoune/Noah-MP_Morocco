#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=OPL_hourly_2018-07
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_hourly_201807/logs/OPL_hourly_2018-07_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_hourly_201807/logs/OPL_hourly_2018-07_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - OPL Hourly - Period 2018-07"
echo " Start: 2018-07-01 | End: 2018-08-01"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_hourly_201807/generated/configs/lis_OPL_hourly_2018-07.config

echo "============================================="
echo " Simulation Complete "
echo "============================================="
