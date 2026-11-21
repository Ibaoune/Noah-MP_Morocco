#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_nowilt_17
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/logs/slurm_DA_nowilt_17_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/logs/slurm_DA_nowilt_17_%j.err
#SBATCH --time=16:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2017/DA_nocdf_nowilt_2017/config/lis_DA_nocdf_nowilt_2017.config"
BIN="./src/lisf_nowilt/lis/LIS"

echo "=========================================================="
echo " LIS NorthMor - DA_nocdf_nowilt_2017"
echo " Start: 2017-01-01 | End: 2018-01-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN}"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation DA_nocdf_nowilt_2017 terminee avec succes "
echo "=========================================================="
