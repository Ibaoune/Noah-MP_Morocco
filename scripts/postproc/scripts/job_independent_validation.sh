#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=independent_validation
#SBATCH --output=logs/validation_%j.out
#SBATCH --error=logs/validation_%j.err
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

# Move to the postproc root directory
cd "$(dirname "$0")/.."

echo "Démarrage de la validation : $(date)"
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016.yaml --make-figures
echo "Fin de la validation : $(date)"
