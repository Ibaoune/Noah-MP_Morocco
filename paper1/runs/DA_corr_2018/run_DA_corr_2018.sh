#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_corr_18
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/slurm_DA_corr_18_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/logs/slurm_DA_corr_18_%j.err
#SBATCH --time=24:00:00
#SBATCH --partition=compute
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_corr_2018/config/lis_DA_corr_2018.config"
BIN="./src/lisf_corr/lis/LIS"

echo "========================================================"
echo " LIS NorthMor - DA_corr_2018"
echo " Start: 2018-01-01 | End: 2019-01-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN}"
echo "========================================================"

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "========================================================"
echo " Simulation DA_corr_2018 terminee avec succes "
echo "========================================================"
