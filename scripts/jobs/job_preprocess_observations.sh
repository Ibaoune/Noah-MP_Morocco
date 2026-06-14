#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=prep_obs
#SBATCH --output=logs/preprocess/prep_obs_%j.out
#SBATCH --error=logs/preprocess/prep_obs_%j.err
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --partition=compute

# Load environment
source ~/.bashrc
source ../venv/bin/activate

cd scripts/preprocess

echo "=== Starting SMAP Preprocessing ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python preprocess_smap_qc_regrid.py

echo "=== Starting MODIS Preprocessing ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python preprocess_modis_lai.py

echo "=== Starting ABHS Streamflow Preprocessing ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python preprocess_abhs_streamflow.py

echo "=== Observation preprocessing finished ==="
