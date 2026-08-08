#!/bin/bash
# run_manuscript_hydrological_response_figures.sh

# Exit on error
set -e

echo "--- Starting Hydrological Response Figure Generation ---"

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc/

# Create logs directory
mkdir -p matrix_2016_2020/outputs/logs/

# Parse arguments
ARGS=""
for i in "$@"; do
    if [ "$i" == "--overwrite" ]; then
        ARGS="$ARGS --overwrite"
    elif [ "$i" == "--dry-run" ]; then
        ARGS="$ARGS --dry-run"
    fi
done

echo "Running with arguments: $ARGS"

# Run the python script
python src/hydrological_response/hydrological_response_cdf_nocdf.py \
    --input-parquet /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/data/processed/monthly_pixel_dataset_2016_2020_static.parquet \
    --output-root matrix_2016_2020/outputs \
    $ARGS | tee matrix_2016_2020/outputs/logs/run_hydrological_response_cdf_nocdf.log

echo "--- Done ---"
