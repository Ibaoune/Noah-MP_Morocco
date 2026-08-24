#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#SBATCH --job-name=IA_SM_RF_V01_Static
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --output=jobs/logs/rf_v01_cpu_%j.out
#SBATCH --error=jobs/logs/rf_v01_cpu_%j.err

# Load environment
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate base

# Go to project root
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim

# Threading parameters for CPU optimizations (RF)
export OMP_NUM_THREADS=16
export MKL_NUM_THREADS=16
export OPENBLAS_NUM_THREADS=16
export NUMEXPR_NUM_THREADS=16

# Log environment info
echo "========================================"
echo "Host: $(hostname)"
echo "Date: $(date)"
echo "Job ID: $SLURM_JOB_ID"
echo "--- SLURM JOB INFO ---"
scontrol show job $SLURM_JOB_ID || sacct -j $SLURM_JOB_ID
echo "----------------------"
echo "PWD: $(pwd)"
echo "Python path: $(which python)"
python --version
echo "========================================"
echo "Starting RF Training V0.1 Static (CPU Cluster)"

python -m py_compile src/*.py

echo "0. Building V0.1 static dataset (if not exists)..."
if [ ! -f "data/processed/monthly_pixel_dataset_2016_2020_static.parquet" ]; then
    python -u src/06_add_static_predictors_to_dataset.py
else
    echo "Static dataset already exists, skipping build."
fi

echo "1. Training Random Forest (Full V0.1 Static)..."
python -u src/02_train_rf.py --mode real_data --dataset static

echo "2. Plotting results..."
python -u src/03_plot_results.py --mode real_data --dataset static

echo "3. Exporting summary..."
python -u src/04_export_summary.py --mode real_data --dataset static

echo "Pipeline completed at: $(date)"
