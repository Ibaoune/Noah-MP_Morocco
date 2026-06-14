#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=dl_orog
#SBATCH --output=logs/download/dl_orog_%j.out
#SBATCH --error=logs/download/dl_orog_%j.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=2G
#SBATCH --partition=compute

echo "=== Starting GDAS Orography download ==="
cd data/scripts/download
bash download_gdas_orography.sh

echo "=== Orography download finished ==="
