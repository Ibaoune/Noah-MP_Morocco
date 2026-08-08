#!/bin/bash

# run_manuscript_drought_diagnostics.sh
DRY_RUN=""
OVERWRITE=""
INPUT_PARQUET="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/data/processed/monthly_pixel_dataset_2016_2020_static.parquet"

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --dry-run) DRY_RUN="--dry-run"; shift ;;
        --overwrite) OVERWRITE="--overwrite"; shift ;;
        --input-parquet) INPUT_PARQUET="$2"; shift 2 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

ROOT="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc"
MATRIX="${ROOT}/matrix_2016_2020"
SRC_DIR="${ROOT}/src/drought_diagnostics"

echo "==========================================="
echo "Starting Drought Diagnostics V0"
echo "==========================================="

for VAR in SSM RZSM; do
    echo "Processing $VAR..."
    python ${SRC_DIR}/compute_drought_percentiles.py --input-parquet ${INPUT_PARQUET} --output-root ${MATRIX} --variable ${VAR} --reference-mode opl_pooled_2016_2020 ${DRY_RUN} ${OVERWRITE}
    python ${SRC_DIR}/drought_frequency_maps.py --input-parquet ${INPUT_PARQUET} --output-root ${MATRIX} --variable ${VAR} --reference-mode opl_pooled_2016_2020 ${DRY_RUN} ${OVERWRITE}
    python ${SRC_DIR}/drought_area_timeseries.py --input-parquet ${INPUT_PARQUET} --output-root ${MATRIX} --variable ${VAR} --reference-mode opl_pooled_2016_2020 ${DRY_RUN} ${OVERWRITE}
    python ${SRC_DIR}/drought_transition_analysis.py --input-parquet ${INPUT_PARQUET} --output-root ${MATRIX} --variable ${VAR} --reference-mode opl_pooled_2016_2020 ${DRY_RUN} ${OVERWRITE}
    python ${SRC_DIR}/drought_by_landcover.py --input-parquet ${INPUT_PARQUET} --output-root ${MATRIX} --variable ${VAR} --reference-mode opl_pooled_2016_2020 ${DRY_RUN} ${OVERWRITE}
done

echo "Done."
