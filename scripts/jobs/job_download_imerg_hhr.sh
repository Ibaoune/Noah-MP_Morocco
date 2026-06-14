#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job: Download IMERG Half-Hourly (Full 3 Months)
#
######################
#SBATCH --job-name=dl_imerg_3m
#SBATCH --output=logs/slurm/slurm_dl_imerg_3m_%j.log
#SBATCH --error=logs/slurm/slurm_dl_imerg_3m_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

echo "=================================================="
echo "Starting Full IMERG Download (3 Months)"
echo "=================================================="

# Run the full 3-month download script
./data/scripts/download/download_imerg_hhr.sh

echo "Download complete!"
