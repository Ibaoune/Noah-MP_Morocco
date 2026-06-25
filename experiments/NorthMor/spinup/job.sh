#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=kickoff_spinup
#SBATCH --output=logs/kickoff_%j.log
#SBATCH --error=logs/kickoff_%j.err
#SBATCH --time=00:10:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=1

# ==============================================================================
# Spin-up Daisy Chain Kickoff Script
# ==============================================================================
# This script is intended to run in a batch-processing environment to kick off 
# the automated daisy-chain workflow. It prevents the need to run the Python 
# submission script interactively on the login node.
# ==============================================================================

# Stop on first error
set -e

# Change directory to the spinup workflow root
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup

# Load required computing environment (Modules, Conda, Compilers, etc.)
source ../../../arch/arch_toubkal.env

echo "============================================="
echo " Starting Spin-up Daisy Chain "
echo "============================================="
echo "Date: $(date)"

# Execute the python script to generate and submit the first job in the chain.
# The script will submit the batch job for the period starting at 2008-01-01, 
# and that job will subsequently submit the next period upon successful completion.
python3 scripts/chain_spinup.py --current-date 2008-01-01 --submit

echo "============================================="
echo " Kickoff complete! Check SLURM queue using 'squeue' "
echo "============================================="
