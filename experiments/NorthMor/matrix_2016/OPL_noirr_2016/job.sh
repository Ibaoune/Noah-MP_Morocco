#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=kickoff_opl
#SBATCH --output=logs/kickoff_%j.log
#SBATCH --error=logs/kickoff_%j.err
#SBATCH --time=00:05:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=1

set -e
cd $SLURM_SUBMIT_DIR

source ../../../../arch/arch_toubkal.env

# Kick off the chain for 2016 OPL.
# It reads StartDate from config/experiment.ini
START_DATE=$(grep StartDate config/experiment.ini | awk -F'=' '{print $2}' | tr -d ' ')

python3 scripts/chain_opl.py --current-date $START_DATE --submit
