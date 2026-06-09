#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=da_3d
#SBATCH --output=experiments/3days/assim_tests/logs/lis_da_%j.log
#SBATCH --error=experiments/3days/assim_tests/logs/lis_da_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=4
set -x

CONFIG_FILE="$1"

if [ -z "$CONFIG_FILE" ]; then
    echo "Usage: sbatch experiments/3days/assim_tests/job_da.sh <config_file>"
    exit 1
fi

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

mkdir -p experiments/3days/assim_tests/output
mkdir -p experiments/3days/assim_tests/logs

echo "============================================="
echo " LIS DA Test (3 days): $CONFIG_FILE"
echo "============================================="

time mpirun -n 4 ./src/lisf/lis/LIS -f "$CONFIG_FILE"

echo "============================================="
echo " DONE "
echo "============================================="
