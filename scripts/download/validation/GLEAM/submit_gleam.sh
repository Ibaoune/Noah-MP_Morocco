#!/bin/bash
#SBATCH --job-name=gleam
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=12:00:00
#SBATCH --partition=compute
#SBATCH --output=logs/gleam_%j.out
#SBATCH --error=logs/gleam_%j.err

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Starting gleam download..."
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/GLEAM
python3 download_gleam.py
echo "Finished."
