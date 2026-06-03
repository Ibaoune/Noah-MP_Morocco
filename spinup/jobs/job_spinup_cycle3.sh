#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
# Job: LIS Cycled Spin-Up (Cycle 3) for Sebou Basin
#
# Usage:
#   sbatch spinup/jobs/job_spinup_cycle3.sh
#
# SBATCH configuration based on fastest OPL scalability tests
#SBATCH --job-name=spinup_c3
#SBATCH --output=spinup/SPINUP_sebou/logs/slurm_spinup_c3_%j.log
#SBATCH --error=spinup/SPINUP_sebou/logs/slurm_spinup_c3_%j.log
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
echo "Starting LIS Sebou Basin Spin-Up - CYCLE 3"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES"
echo " Tasks:  $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo "=================================================="

# Ensure directories exist
mkdir -p spinup/SPINUP_sebou/cycle3
mkdir -p spinup/SPINUP_sebou/final_restart
mkdir -p spinup/SPINUP_sebou/logs

if [ ! -f "data/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input.d01_sebou.nc not found!"
    exit 1
fi

# Find the final restart from Cycle 2
RESTART_FILE=$(ls -1t spinup/SPINUP_sebou/cycle2/LIS_RST_NOAH36_*.nc | head -n 1)

if [ -z "$RESTART_FILE" ] || [ ! -f "$RESTART_FILE" ]; then
    echo "ERROR: Could not find Cycle 2 restart file in spinup/SPINUP_sebou/cycle2/"
    exit 1
fi

echo "Using Cycle 2 final restart: $RESTART_FILE"

# Create a temporary config for Cycle 3
TMP_CONFIG="spinup/configs/lis.config.spinup_cycle3.tmp"
cp spinup/configs/lis.config.spinup_sebou $TMP_CONFIG

# Cycle 3 specific replacements: restart, correct output dir
sed -i 's|^Start mode:.*|Start mode:                             restart|g' $TMP_CONFIG
sed -i "s|^Noah-MP.3.6 restart file:.*|Noah-MP.3.6 restart file:                 ./${RESTART_FILE}|g" $TMP_CONFIG
sed -i 's|^Output directory:.*|Output directory:                       "spinup/SPINUP_sebou/cycle3"|g' $TMP_CONFIG
sed -i 's|^Diagnostic output file:.*|Diagnostic output file:                 "spinup/SPINUP_sebou/cycle3/lislog"|g' $TMP_CONFIG

echo "----------------------------------------"
echo "Running Spin-up Cycle 3..."
echo "----------------------------------------"
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f $TMP_CONFIG
} > spinup/SPINUP_sebou/logs/lis_spinup_c3_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running Cycle 3! Check spinup/SPINUP_sebou/logs/lis_spinup_c3_run.log"
    exit 1
fi

echo "Spin-Up Cycle 3 completed successfully."

echo "----------------------------------------"
echo "Creating final common initial condition..."
echo "----------------------------------------"
FINAL_RESTART=$(ls -1t spinup/SPINUP_sebou/cycle3/LIS_RST_NOAH36_*.nc | head -n 1)
COMMON_RESTART="spinup/SPINUP_sebou/final_restart/restart_spinup_cycle3_2020_common_initial_state.nc"

if [ -f "$FINAL_RESTART" ]; then
    cp $FINAL_RESTART $COMMON_RESTART
    echo "Successfully copied final restart to $COMMON_RESTART"
    echo "This file should be used as the common initial condition for 2015-2020 production experiments."
else
    echo "ERROR: Could not find final restart file from Cycle 3!"
    exit 1
fi
