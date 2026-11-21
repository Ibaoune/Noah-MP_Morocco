#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=ENS_STAT_1803
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803/logs/slurm_ENS_STAT_1803_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803/logs/slurm_ENS_STAT_1803_%j.err
#SBATCH --time=04:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclude=slurm-compute-h23c8-u6-svn1

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_STATE_201803/config/lis_ENS_STATE_201803.config"
BIN="./src/lisf/lis/make/LIS"

echo "=========================================================="
echo " LIS NorthMor - ENS_STATE_201803 (20 members, state-only pert, March 2018)"
echo " Start: 2018-03-01 | End: 2018-04-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN} (Production)"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation ENS_STATE_201803 terminée avec succès "
echo "=========================================================="
