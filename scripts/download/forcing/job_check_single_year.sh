#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script Name   : job_check_single_year.sh
# Author        : M. El Aabaribaoune (@um6p)
# Description   : SLURM job script to launch the Python-based data integrity 
#                 verification. It is automatically called by the orchestrator 
#                 after a year finishes downloading. It checks if the Python 
#                 script returned 0 (success) or 1 (failure) and manages the 
#                 status file (`status/status_${YEAR}.success`) accordingly.
# Usage         : sbatch job_check_single_year.sh <YYYY>
#                 (Typically triggered by job_orchestrator.sh)
# ==============================================================================
#SBATCH --job-name=chk_yr
#SBATCH --output=logs/chk_yr_%A_%a.out
#SBATCH --error=logs/chk_yr_%A_%a.err
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32

YEAR=$1

if [ -z "$YEAR" ]; then
    echo "ERROR: YEAR argument not provided."
    exit 1
fi

echo "Starting verification for year $YEAR..."
module load Anaconda3/2020.11
export PYTHONNOUSERSITE=1

python3 check_single_year.py $YEAR
STATUS=$?

if [ $STATUS -eq 0 ]; then
    echo "Verification for $YEAR passed!"
    touch status/status_${YEAR}.success
    echo "=========================================================================="
else
    echo "Verification for $YEAR failed."
    rm -f status/status_${YEAR}.success
    exit 1
fi
