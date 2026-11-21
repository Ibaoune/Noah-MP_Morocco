#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=REGR_RYU_1803
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr/logs/slurm_REGR_RYU_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr/logs/slurm_REGR_RYU_%j.err
#SBATCH --time=00:45:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclude=slurm-compute-h23c8-u6-svn1

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/tests/ENS_STATE_201803_regr/config/lis_ENS_STATE_201803_regr.config"
BIN="./src/lisf_ryu/lis/LIS"

echo "=========================================================="
echo " LIS NorthMor - Non-regression check: ENS_STATE_201803 with Ryu=1 (2 days)"
echo " Start: 2018-03-01 | End: 2018-03-03"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN} (Patched LIS reading pert_bias_corr)"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation regression terminée avec succès "
echo "=========================================================="
