#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=dl_gdas
#SBATCH --output=data/logs/download/dl_gdas_%j.out
#SBATCH --error=data/logs/download/dl_gdas_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=compute

echo "=== Starting GDAS Forcing Data Download ==="

# Ensure we are in the root directory
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

# Make sure logs directory exists
mkdir -p data/logs/download

# Run the python download script
python data/scripts/download/download_gdas.py

echo "=== GDAS Forcing Data Download Finished ==="
