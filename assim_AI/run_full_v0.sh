#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
echo "Starting Full Run V0 (2016-2020)..."
mkdir -p logs results models data/processed/monthly_parts
# Ensure we run in real_data mode
python -m py_compile src/*/*.py
echo "1. Checking config..."
python src/main/00_check_config.py
echo "2. Building dataset..."
python src/preproc/01_build_dataset.py --mode real_data --resume

echo "2.5 Validating strict completeness of the dataset..."
python src/preproc/05_validate_full_dataset.py --require-complete
if [ $? -ne 0 ]; then
    echo "ERROR: Validation failed. The dataset is not strictly complete."
    echo "Aborting the pipeline to prevent partial RF training."
    exit 1
fi

echo "3. Training Random Forest..."
python src/main/02_train_rf.py --mode real_data
echo "4. Plotting results..."
python src/postproc/03_plot_results.py --mode real_data
echo "5. Exporting summary..."
python src/postproc/04_export_summary.py
echo "Full Run V0 completed."
