#!/bin/bash
#SBATCH --job-name=ascat
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --partition=compute
#SBATCH --output=logs/ascat_%j.out
#SBATCH --error=logs/ascat_%j.err

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Starting ascat download..."
python3 download_ascat.py
echo "Finished."
