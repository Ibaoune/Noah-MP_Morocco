#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
# Master launcher for all 4 Noah-MP Hydrology Sensitivity Experiments (2017-2018).
# NOTE: DO NOT EXECUTE until explicitly validated by the user.

set -e
ROOT_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity"

echo "=========================================================================="
echo " Launching 2017-2018 Noah-MP Hydrology Sensitivity Experiments (OPL)"
echo " Period: 2017-01-01 to 2018-12-31 (24 months)"
echo " Configurations: OL_R1_SIMGM, OL_R2_SIMTOP, OL_R3_SCHAAKE96, OL_R4_BATS"
echo " Note: January 2017 is already validated and will be resumed seamlessly."
echo "=========================================================================="

for exp in OL_R1_SIMGM OL_R2_SIMTOP OL_R3_SCHAAKE96 OL_R4_BATS; do
    echo "--> Submitting production chain for $exp..."
    /bin/bash "$ROOT_DIR/experiments/$exp/scripts/launch_2017_2018.sh"
done

echo "=========================================================================="
echo " All 4 production daisy chains submitted successfully."
echo " Check queue with: squeue -u \$USER"
echo "=========================================================================="
