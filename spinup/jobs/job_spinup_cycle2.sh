#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
# Job: LIS Cycled Spin-Up (Cycle 2) for Sebou Basin
#
# Usage:
#   sbatch spinup/jobs/job_spinup_cycle2.sh
#
# SBATCH configuration based on fastest OPL scalability tests
#SBATCH --job-name=spinup_c2
#SBATCH --output=spinup/SPINUP_sebou/logs/slurm_spinup_c2_%j.log
#SBATCH --error=spinup/SPINUP_sebou/logs/slurm_spinup_c2_%j.log
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
echo "Starting LIS Sebou Basin Spin-Up - CYCLE 2"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

# Ensure directories exist
mkdir -p spinup/SPINUP_sebou/cycle2
mkdir -p spinup/SPINUP_sebou/logs

if [ ! -f "data/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input.d01_sebou.nc not found!"
    exit 1
fi

# Find the final restart from Cycle 1
RESTART_FILE=$(ls -1t spinup/SPINUP_sebou/cycle1/LIS_RST_NOAH36_*.nc | head -n 1)

if [ -z "$RESTART_FILE" ] || [ ! -f "$RESTART_FILE" ]; then
    echo "ERROR: Could not find Cycle 1 restart file in spinup/SPINUP_sebou/cycle1/"
    exit 1
fi

echo "Using Cycle 1 final restart: $RESTART_FILE"

# Create a temporary config for Cycle 2
TMP_CONFIG="spinup/configs/lis.config.spinup_cycle2.tmp"
cp spinup/configs/lis.config.spinup_sebou $TMP_CONFIG

# Cycle 2 specific replacements: restart, correct output dir
sed -i 's|^Start mode:.*|Start mode:                             restart|g' $TMP_CONFIG
sed -i "s|^Noah-MP.3.6 restart file:.*|Noah-MP.3.6 restart file:                 ./${RESTART_FILE}|g" $TMP_CONFIG
sed -i 's|^Output directory:.*|Output directory:                       "spinup/SPINUP_sebou/cycle2"|g' $TMP_CONFIG
sed -i 's|^Diagnostic output file:.*|Diagnostic output file:                 "spinup/SPINUP_sebou/cycle2/lislog"|g' $TMP_CONFIG

echo "----------------------------------------"
echo "Running Spin-up Cycle 2..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f $TMP_CONFIG
} > spinup/SPINUP_sebou/logs/lis_spinup_c2_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running Cycle 2! Check spinup/SPINUP_sebou/logs/lis_spinup_c2_run.log"
    exit 1
fi

echo "Spin-Up Cycle 2 completed successfully."
