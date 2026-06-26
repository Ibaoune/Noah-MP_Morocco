#!/bin/bash
#SBATCH --job-name=cop_lai
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=24:00:00
#SBATCH --partition=compute
#SBATCH --output=logs/cop_lai_%j.out
#SBATCH --error=logs/cop_lai_%j.err

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Starting cop_lai download..."
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/Copernicus_LAI
python3 download_copernicus_lai.py
echo "Finished."
