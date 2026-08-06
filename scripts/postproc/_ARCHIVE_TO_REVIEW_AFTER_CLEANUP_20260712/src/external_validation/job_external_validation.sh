#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

#SBATCH --job-name=external_validation
#SBATCH --output=logs/ext_val_%j.out
#SBATCH --error=logs/ext_val_%j.err
#SBATCH --time=01:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=8G

# ==============================================================================
# Job Script: External Validation Module
# ==============================================================================


PROJECT_ROOT="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
MODULE_DIR="$PROJECT_ROOT/scripts/postproc/src/external_validation"

cd "$MODULE_DIR"

# Load environment
source ~/.bashrc
conda activate postproc_env

echo "Running External Validation Module..."
python main.py \
  --matrix matrix_2016 \
  --config config_external_validation.yaml \
  --output-root "$PROJECT_ROOT/scripts/postproc/figures" \
  --table-root "$PROJECT_ROOT/scripts/postproc/tables" \
  --log-root "$PROJECT_ROOT/scripts/postproc/logs"

echo "External Validation Module completed successfully."
