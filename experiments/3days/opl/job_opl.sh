#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=opl_3d
#SBATCH --output=experiments/3days/opl/logs/lis_opl_%j.log
#SBATCH --error=experiments/3days/opl/logs/lis_opl_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

mkdir -p experiments/3days/opl/output
mkdir -p experiments/3days/opl/logs

echo "============================================="
echo " LIS Open Loop Test (3 days)"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f experiments/3days/opl/lis.config

echo "============================================="
echo " DONE "
echo "============================================="
