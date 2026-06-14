#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job: Download IMERG Half-Hourly (4 days for Scalability)
#
######################
#SBATCH --job-name=dl_imerg_4d
#SBATCH --output=logs/slurm/slurm_dl_imerg_4d_%j.log
#SBATCH --error=logs/slurm/slurm_dl_imerg_4d_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

echo "=================================================="
echo "Starting IMERG Scalability Download (4 days)"
echo "=================================================="

# Run the 4-day download script
./data/scripts/download/download_imerg_scalability.sh

echo "Download complete!"
