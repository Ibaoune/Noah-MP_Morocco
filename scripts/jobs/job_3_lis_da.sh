#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job 3: LIS Data Assimilation (DA) — EnKF with SMAP soil moisture
#
# Usage:
#   sbatch --nodes=2 --ntasks=64 scripts/jobs/job_3_lis_da.sh
#
######################
## TOUBKAL    UM6P ##
######################
#SBATCH --job-name=lis_da
#SBATCH --output=logs/slurm/slurm_da_%j.log
#SBATCH --error=logs/slurm/slurm_da_%j.log
#SBATCH --time=24:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting LIS Data Assimilation Simulation Job"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

if [ ! -f "data/lis_input.d01.nc" ]; then
    echo "ERROR: data/lis_input.d01.nc not found!"
    echo "Please ensure that job_1_ldt.sh has successfully completed."
    exit 1
fi

echo "----------------------------------------"
echo "Running Data Assimilation Simulation..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.da
} > logs/lis_da_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running Data Assimilation! Check logs/lis_da_run.log"
    exit 1
fi
echo "Data Assimilation simulation completed successfully."
