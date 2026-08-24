#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#SBATCH --job-name=IA_SM_RF_V0
#SBATCH --time=12:00:00
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --output=jobs/logs/full_v0_cpu_%j.out
#SBATCH --error=jobs/logs/full_v0_cpu_%j.err

# Load environment
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
# We use the base environment which was active in interactive mode
conda activate base

# Go to project root
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim

# Threading parameters for CPU optimizations (Dask/RF)
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
python -c "import numpy; print('numpy:', numpy.__version__)"
python -c "import pandas; print('pandas:', pandas.__version__)"
python -c "import xarray; print('xarray:', xarray.__version__)"
python -c "import dask; print('dask:', dask.__version__)"
python -c "import sklearn; print('sklearn:', sklearn.__version__)"
python -c "import pyarrow; print('pyarrow:', pyarrow.__version__)"
python -c "try: import shap; print('shap:', shap.__version__)
except: print('shap: Not installed')"
echo "========================================"

echo "Starting Full Run V0 Pipeline on CPU Cluster"

echo "1. Checking config..."
python -u src/00_check_config.py

echo "2. Building dataset..."
python -u src/01_build_dataset.py --mode real_data --resume

echo "2.5 Validating strict completeness of the dataset..."
python -u src/05_validate_full_dataset.py --require-complete
if [ $? -ne 0 ]; then
    echo "ERROR: Validation failed. The dataset is not strictly complete."
    echo "Aborting the pipeline to prevent partial RF training."
    exit 1
fi

echo "3. Training Random Forest..."
python -u src/02_train_rf.py --mode real_data

echo "4. Plotting results..."
python -u src/03_plot_results.py --mode real_data

echo "5. Exporting summary..."
python -u src/04_export_summary.py

echo "Pipeline completed at: $(date)"
