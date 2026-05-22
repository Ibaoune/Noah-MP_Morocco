#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# LIS Scalability Test Job — 3-day simulation with timing
#
# Usage:
#   sbatch --nodes=N scripts/jobs/job_scalability.sh <config_file> <label> <ntasks>
#
# Examples:
#   sbatch --nodes=1 scripts/jobs/job_scalability.sh configs/scalability/lis.config.opl.32tasks_1node OPL_32tasks_1node 32
#   sbatch --nodes=2 scripts/jobs/job_scalability.sh configs/scalability/lis.config.da.64tasks_2nodes DA_64tasks_2nodes 64
#
######################
## TOUBKAL    UM6P ##
######################
#SBATCH --job-name=lis_scale
#SBATCH --output=logs/slurm/lis_scale_%j.log
#SBATCH --error=logs/slurm/lis_scale_%j.log
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

CONFIG_FILE="$1"
LABEL="$2"
NTASKS="$3"

if [ -z "$CONFIG_FILE" ] || [ -z "$LABEL" ] || [ -z "$NTASKS" ]; then
    echo "Usage: sbatch --nodes=N job_scalability.sh <config_file> <label> <ntasks>"
    exit 1
fi

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "============================================="
echo " LIS Scalability Test: $LABEL"
echo "============================================="
echo " Config:    $CONFIG_FILE"
echo " Nodes:     $SLURM_NNODES"
echo " MPI Tasks: $NTASKS"
echo " Job ID:    $SLURM_JOB_ID"
echo " Started:   $(date)"
echo "============================================="

# Create output directory
mkdir -p "experiments/scalability/${LABEL}"

# Execute the MPI program and log the time
{
    time mpirun -n $NTASKS ./src/lisf/lis/LIS -f "$CONFIG_FILE"
} >> "logs/slurm/lis_scale_${SLURM_JOB_ID}.log" 2>&1

EXIT_CODE=$?

echo "============================================="
echo " RESULTS: $LABEL"
echo "============================================="
echo " Exit code:  $EXIT_CODE"
echo " Nodes:      $SLURM_NNODES"
echo " MPI Tasks:  $NTASKS"
echo " Finished:   $(date)"
echo "============================================="

# Save timing results to a common CSV file
RESULTS_FILE="experiments/scalability/timing_results.csv"
if [ ! -f "$RESULTS_FILE" ]; then
    echo "label,nodes,ntasks,exit_code,job_id" > "$RESULTS_FILE"
fi
echo "${LABEL},${SLURM_NNODES},${NTASKS},${EXIT_CODE},${SLURM_JOB_ID}" >> "$RESULTS_FILE"
