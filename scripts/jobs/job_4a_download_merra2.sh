#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=download_merra2
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=24:00:00
#SBATCH --partition=compute

source arch/arch_toubkal.env

echo "Starting MERRA-2 download for 2015-2020..."
python3 scripts/download/download_merra2.py
echo "Download finished."
