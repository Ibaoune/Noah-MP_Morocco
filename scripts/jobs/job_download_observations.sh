#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=dl_obs
#SBATCH --output=logs/download/dl_obs_%j.out
#SBATCH --error=logs/download/dl_obs_%j.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --partition=compute

# Load environment
source ~/.bashrc
source ../venv/bin/activate

cd scripts/download

echo "=== Starting SMAP SPL3SMP_E download ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_smap_spl3smp_e.py

echo "=== Starting MODIS MCD15A2H download ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_modis_mcd15a2h.py

echo "=== Observation downloads finished ==="
