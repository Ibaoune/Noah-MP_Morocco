#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
# run_rf_xai_figures.sh

# Exit on error
set -e

echo "--- Starting RF XAI Figure Generation ---"

cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/IA_SM_assim/

# Create logs directory
mkdir -p outputs/logs/

# Note: this script currently acts as a placeholder to call the future RF plotting script
# python src/plot_rf_xai/generate_all_rf_figures.py | tee outputs/logs/run_rf_xai_figures.log

DRY_RUN=0
for i in "$@"; do
    if [ "$i" == "--dry-run" ]; then
        DRY_RUN=1
    fi
done

echo "Copying previously selected manuscript figures to manuscript_selected directory..."
if [ $DRY_RUN -eq 1 ]; then
    echo "[DRY RUN] Would copy rf_temporal_vs_spatial_cv_v02.png"
    echo "[DRY RUN] Would copy rf_grouped_feature_importance_v02.png"
else
    cp outputs/figures/rf_skill/manuscript_rf_temporal_vs_spatial_cv.png outputs/figures/manuscript_selected/ 2>/dev/null || true
    cp outputs/figures/rf_grouped_importance/manuscript_rf_grouped_feature_importance.png outputs/figures/manuscript_selected/ 2>/dev/null || true
fi

echo "--- Done ---"
