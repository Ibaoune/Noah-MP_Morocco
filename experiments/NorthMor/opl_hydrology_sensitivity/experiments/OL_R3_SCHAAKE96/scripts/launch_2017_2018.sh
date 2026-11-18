#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
# Production Launch Script (2017-2018 Daisy-Chained Noah-MP 4.0.1 Open-Loop)
# Experiment: OL_R3_SCHAAKE96
# Resume support: Skips already completed months without overwriting validated data.

set -e
BASE_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96"
cd "$BASE_DIR"

echo "=== Launching 2017-2018 Production Run for OL_R3_SCHAAKE96 ==="
echo "Working directory: $BASE_DIR"
python3 scripts/chain_opl.py --current-date 2017-01-01 --submit
