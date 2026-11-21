#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=FORC_noRyu
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/logs/slurm_FORC_noRyu_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/logs/slurm_FORC_noRyu_%j.err
#SBATCH --time=04:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --exclude=slurm-compute-h23c8-u6-svn1

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env

CONFIG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_FORC_201803_noRyu/config/lis_ENS_FORC_201803_noRyu.config"
BIN="./src/lisf_ryu/lis/LIS"

echo "=========================================================="
echo " LIS NorthMor - ENS_FORC_201803_noRyu (20 members, forc-only pert, no Ryu recentering, March 2018)"
echo " Start: 2018-03-01 | End: 2018-04-01"
echo " Config: ${CONFIG}"
echo " Binary: ${BIN} (Patched LIS reading pert_bias_corr=0)"
echo "=========================================================="

time mpirun -n 32 "${BIN}" -f "${CONFIG}"

echo "=========================================================="
echo " Simulation ENS_FORC_201803_noRyu terminée avec succès "
echo "=========================================================="
