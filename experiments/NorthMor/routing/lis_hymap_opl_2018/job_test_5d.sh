#!/bin/bash
#SBATCH --job-name=hymap_test_5d
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/lis_hymap_opl_2018/logs/test_5d_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/lis_hymap_opl_2018/logs/test_5d_%j.err
#SBATCH --time=01:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=3

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/

source arch/arch_toubkal.env
export GFORTRAN_CONVERT_UNIT='big_endian'

echo "============================================="
echo " Running coupled LIS/Noah-MP + HyMAP test (5 days)"
echo "============================================="

time mpirun -n 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/lis_hymap_opl_2018/configs/lis_test_5d.config
