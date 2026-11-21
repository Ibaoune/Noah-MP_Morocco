#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=ENS_OPL_18
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/logs/slurm_ENS_OPL_18_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/logs/slurm_ENS_OPL_18_%j.err
#SBATCH --time=16:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclude=slurm-compute-h23c8-u6-svn1

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/config/lis_ENS_OPL_2018_restart_jun.config"
BIN="./src/lisf/lis/make/LIS"

echo "=========================================================="
echo " LIS NorthMor - ENS_OPL_2018 RESTART (20 members, perturbed OL)"
echo " Start: 2018-06-01 | End: 2019-01-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN} (Production)"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation ENS_OPL_2018 restart terminée avec succès "
echo "=========================================================="
