#!/bin/bash
#SBATCH --job-name=assim_diag
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --output=logs/assim_diag_%j.out
#SBATCH --error=logs/assim_diag_%j.err

echo "Job started on $(date)"

# Load the required module/environment
module load conda || true
source ~/.bashrc || true
conda activate postproc_env

# Navigate to the correct directory
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/src/assim_diagnostics

echo "Running Assimilation Diagnostics module..."
python3 main.py --config config_diagAssim.yaml

echo "Job completed on $(date)"
