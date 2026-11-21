#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_nost_18MAM
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/logs/slurm_DA_nost_18MAM_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/logs/slurm_DA_nost_18MAM_%j.err
#SBATCH --time=06:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_nostate_2018MAM/config/lis_DA_nocdf_nostate_2018MAM.config"
BIN="./src/lisf/lis/make/LIS"

echo "=========================================================="
echo " LIS NorthMor - DA_nocdf_nostate_2018MAM"
echo " Start: 2018-03-01 | End: 2018-06-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN}"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation DA_nocdf_nostate_2018MAM terminee avec succes "
echo "=========================================================="
