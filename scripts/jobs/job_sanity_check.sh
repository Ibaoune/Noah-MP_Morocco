#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job: LDT + LIS Sanity Check (5km)
#
######################
#SBATCH --job-name=sanity_5km
#SBATCH --output=logs/slurm/slurm_sanity_5km_%j.log
#SBATCH --error=logs/slurm/slurm_sanity_5km_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting Sanity Check (5km) Job"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

echo "----------------------------------------"
echo "1. Running LDT Parameter Generation..."
echo "----------------------------------------"
{
    time ./src/lisf/ldt/make/LDT configs/ldt.config.sanity
} > logs/ldt_sanity_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running LDT! Check logs/ldt_sanity_run.log"
    exit 1
fi
echo "LDT completed successfully."

echo "----------------------------------------"
echo "2. Running LIS Sanity Check Simulation..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.sanity
} > logs/lis_sanity_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running LIS! Check logs/lis_sanity_run.log"
    exit 1
fi
echo "LIS Sanity Check simulation completed successfully."
