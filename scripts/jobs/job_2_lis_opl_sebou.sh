#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job 2: LIS Open-Loop (OPL) simulation for Sebou Basin
#
# Usage:
#   sbatch scripts/jobs/job_2_lis_opl_sebou.sh
#
######################
## TOUBKAL    UM6P ##
######################
#SBATCH --job-name=lis_opl_sebou
#SBATCH --output=logs/slurm/slurm_opl_sebou_%j.log
#SBATCH --error=logs/slurm/slurm_opl_sebou_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting LIS Sebou Basin Open-Loop Job"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

if [ ! -f "data/lis_input/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input/lis_input.d01_sebou.nc not found!"
    echo "Please ensure that job_1_ldt_sebou.sh has successfully completed."
    exit 1
fi

echo "----------------------------------------"
echo "Running Open-Loop Simulation..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.opl_sebou
} > logs/lis_opl_sebou_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running Open-Loop! Check logs/lis_opl_sebou_run.log"
    exit 1
fi
echo "Open-Loop simulation completed successfully."
