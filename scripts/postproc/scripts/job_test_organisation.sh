#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=test_organisation
#SBATCH --output=logs/test_org_%j.out
#SBATCH --error=logs/test_org_%j.err
#SBATCH --time=12:00:00
#SBATCH --mem=32G
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc

echo "Démarrage de la validation : $(date)"
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_sensitivity_2016_test.yaml --make-figures --make-hydrology-figures
echo "Fin de la validation : $(date)"
