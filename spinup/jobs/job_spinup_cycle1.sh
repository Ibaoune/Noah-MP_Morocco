#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
# Job: LIS Cycled Spin-Up (Cycle 1) for Sebou Basin
#
# Usage:
#   sbatch spinup/jobs/job_spinup_cycle1.sh
#
# SBATCH configuration based on fastest OPL scalability tests
#SBATCH --job-name=spinup_c1
#SBATCH --output=spinup/SPINUP_sebou/logs/slurm_spinup_c1_%j.log
#SBATCH --error=spinup/SPINUP_sebou/logs/slurm_spinup_c1_%j.log
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --ntasks-per-node=32
#SBATCH --time=24:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting LIS Sebou Basin Spin-Up - CYCLE 1"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

# Ensure directories exist
mkdir -p spinup/SPINUP_sebou/cycle1
mkdir -p spinup/SPINUP_sebou/logs

if [ ! -f "data/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input.d01_sebou.nc not found!"
    exit 1
fi

# Create a temporary config for Cycle 1
TMP_CONFIG="spinup/configs/lis.config.spinup_cycle1.tmp"
cp spinup/configs/lis.config.spinup_sebou $TMP_CONFIG

# Cycle 1 specific replacements: coldstart, no restart file, correct output dir
sed -i 's|^Start mode:.*|Start mode:                             coldstart|g' $TMP_CONFIG
sed -i 's|^Noah-MP.3.6 restart file:.*|Noah-MP.3.6 restart file:                 none|g' $TMP_CONFIG
sed -i 's|^Output directory:.*|Output directory:                       "spinup/SPINUP_sebou/cycle1"|g' $TMP_CONFIG
sed -i 's|^Diagnostic output file:.*|Diagnostic output file:                 "spinup/SPINUP_sebou/cycle1/lislog"|g' $TMP_CONFIG

echo "----------------------------------------"
echo "Running Spin-up Cycle 1..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f $TMP_CONFIG
} > spinup/SPINUP_sebou/logs/lis_spinup_c1_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running Cycle 1! Check spinup/SPINUP_sebou/logs/lis_spinup_c1_run.log"
    exit 1
fi

echo "Spin-Up Cycle 1 completed successfully."
