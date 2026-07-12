#!/bin/bash
#SBATCH --job-name=postproc_2016
#SBATCH --output=logs/postproc_2016_%j.out
#SBATCH --error=logs/postproc_2016_%j.err
#SBATCH --time=04:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

echo "Job started on $(date)"

# Load environment
source ~/.bashrc
conda activate postproc_env

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc

echo "Cleaning up old figures directory..."
rm -rf figures/matrix_2016

echo "Running postprocessing..."
python src/run_postproc.py \
  --matrix matrix_2016 \
  --experiments OPL_noirr_2016 DA_nocdf_noirr_2016 \
  --modules domain assimilation_diagnostics opl_vs_da runoff_partitioning hymap_validation \
  --make-figures

echo "Job completed on $(date)"
