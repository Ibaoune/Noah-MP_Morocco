#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=dl_forcing
#SBATCH --output=logs/download/dl_forcing_%j.out
#SBATCH --error=logs/download/dl_forcing_%j.err
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

echo "=== Starting IMERG download ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_imerg.py

echo "=== Starting GDAS download ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_gdas.py

echo "=== Forcing downloads finished ==="
