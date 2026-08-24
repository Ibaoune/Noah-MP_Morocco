#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#SBATCH --job-name=IA_SM_RF_GPU
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --gres=gpu:1
#SBATCH --partition=gpu
#SBATCH --account=empowermed-ahl6xm8o7mg
#SBATCH --output=jobs/logs/full_v0_gpu_%j.out
#SBATCH --error=jobs/logs/full_v0_gpu_%j.err

# NOTE: This script is an optional template. 
# The current pipeline uses scikit-learn's RandomForestRegressor which is strictly CPU-bound.
# Do NOT run this unless the Python code is refactored to use RAPIDS cuML or XGBoost GPU.

# Load environment
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate base

# Go to project root
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim

echo "========================================"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "PWD: $(pwd)"
echo "CUDA Devices: $CUDA_VISIBLE_DEVICES"
echo "========================================"

echo "[WARNING] Running Python pipeline on GPU node."
echo "If scikit-learn is used, this will not utilize the GPU."

python -u src/00_check_config.py
python -u src/01_build_dataset.py --mode real_data --resume
python -u src/02_train_rf.py --mode real_data
python -u src/03_plot_results.py --mode real_data
python -u src/04_export_summary.py

echo "Pipeline completed at: $(date)"
