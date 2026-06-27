#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=kickoff_ens_opl
#SBATCH --output=logs/kickoff_%j.log
#SBATCH --error=logs/kickoff_%j.err
#SBATCH --time=00:05:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=1

# This is a lightweight kickoff script.
# It sets up the environment and calls the Python daisy-chaining script.

set -e
cd $SLURM_SUBMIT_DIR

# Load necessary modules
source ../../../../arch/arch_toubkal.env

# Kick off the chain for 2015 initial perturbations
python3 scripts/chain_ens_opl.py --submit
