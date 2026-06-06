#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=ldt_cdf
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=12:00:00
#SBATCH --partition=compute

source arch/arch_toubkal.env

# Note to user: 
# Generating CDF files requires the model history (the output from your Spin-up)
# AND the observation history (SMAP). 
# You will need to create an `ldt.config.cdf` configured for "CDF generation"
# mode, pointing to your Spinup_sebou outputs. 
# 
# Only run this job AFTER job_4c_lis_spinup.sh has successfully finished!

echo "Starting LDT CDF Generation..."
time ./src/lisf/ldt/LDT -f configs/ldt.config.cdf
echo "CDF Generation finished."
