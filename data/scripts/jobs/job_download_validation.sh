#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=dl_valid
#SBATCH --output=../../logs/download/dl_valid_%j.out
#SBATCH --error=../../logs/download/dl_valid_%j.err
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --partition=compute

# Load environment
source ~/.bashrc

cd ../download

echo "=== Starting validation dataset downloads ==="
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_gleam.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_wapor.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_esa_cci_sm.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_mod16.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_gpp.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_grace.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_ascat.py
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python download_copernicus_lai.py


echo "=== Validation downloads finished ==="
