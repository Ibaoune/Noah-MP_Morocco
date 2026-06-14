#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=prep_forc
#SBATCH --output=logs/preprocess/prep_forc_%j.out
#SBATCH --error=logs/preprocess/prep_forc_%j.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=16G
#SBATCH --partition=compute

# Load environment
source ~/.bashrc
source ../venv/bin/activate

cd scripts/preprocess

echo "=== Starting GDAS Preprocessing ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python preprocess_gdas_for_lis.py

# IMERG preprocessing is handled in the download script during subsetting
echo "=== Forcing preprocessing finished ==="
