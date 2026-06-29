#!/bin/bash
#SBATCH --job-name=grace_dl
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=24:00:00
#SBATCH --partition=compute
#SBATCH --output=logs/grace_%j.out
#SBATCH --error=logs/grace_%j.err

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Starting GRACE download..."
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/GRACE
python3 download_grace.py
echo "Finished."
