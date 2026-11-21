#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_15m_18N
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/logs/slurm_DA_15m_18N_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/logs/slurm_DA_15m_18N_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov/config/lis_DA_nocdf_diag_15min_2018Nov.config"
BIN="./src/lisf/lis/make/LIS"

echo "=========================================================="
echo " LIS NorthMor - DA_nocdf_diag_15min_2018Nov (15-min inst output)"
echo " Start: 2018-11-01 | End: 2018-11-06 (5 days)"
echo " Config: $CONFIG"
echo " Binary: $BIN"
echo "=========================================================="

time mpirun -n 32 "$BIN" -f "$CONFIG"

echo "=========================================================="
echo " Simulation DA_nocdf_diag_15min_2018Nov terminee avec succes "
echo "=========================================================="
