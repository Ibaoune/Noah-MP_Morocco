#!/bin/bash
#SBATCH --job-name=opl_mult_da
#SBATCH --output=logs/opl_multiple_da_%j.out
#SBATCH --error=logs/opl_multiple_da_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

echo "Job started on $(date)"

# Load environment
source ~/.bashrc
conda activate postproc_env

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc

echo "Cleaning up old opl_multiple_da figures..."
rm -rf figures/matrix_2016/opl_multiple_da

echo "Running postprocessing for opl_multiple_da..."
python src/run_postproc.py \
  --matrix matrix_2016 \
  --experiments OPL_noirr_2016 DA_nocdf_noirr_2016 DA_cdf_noirr_2016 \
  --modules opl_multiple_da \
  --make-figures

echo "Job completed on $(date)"
