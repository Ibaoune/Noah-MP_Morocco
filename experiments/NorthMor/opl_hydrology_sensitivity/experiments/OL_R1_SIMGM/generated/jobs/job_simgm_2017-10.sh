#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=OL_R1_SIMGM_2017-10
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/logs/102017/OL_R1_SIMGM_2017-10_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/logs/102017/OL_R1_SIMGM_2017-10_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - OL_R1_SIMGM - Period 2017-10"
echo " Start: 2017-10-01 | End: 2017-11-01"
echo " Expected days: 31"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/generated/configs/lis_simgm_2017-10.config

echo "============================================="
echo " Post-processing & Strict Operational Audit "
echo "============================================="

# 1. Audit restart
RESTART_SRC=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/output/2017-10/SURFACEMODEL -name "LIS_RST_NOAHMP401_201711010000.d01.nc" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    RST_SZ=$(stat -c%s "$RESTART_SRC" 2>/dev/null || stat -f%z "$RESTART_SRC" 2>/dev/null || echo 0)
    if [ "$RST_SZ" -lt 1000000 ]; then
        echo "ERROR: Restart file $RESTART_SRC is corrupted or too small ($RST_SZ bytes)!"
        exit 1
    fi
    echo "Found valid terminal restart: $RESTART_SRC ($RST_SZ bytes)"
    cp "$RESTART_SRC" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/restarts/
    echo "Successfully copied restart file to /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/restarts/"
else
    echo "ERROR: Terminal restart file LIS_RST_NOAHMP401_201711010000.d01.nc not found in output directory!"
    exit 1
fi

# 2. Audit exact count of history files
HIST_COUNT=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM/output/2017-10/SURFACEMODEL -name "LIS_HIST_*.nc" | wc -l)
if [ "$HIST_COUNT" -ne 31 ]; then
    echo "ERROR: Expected exactly 31 history files for period 2017-10, found $HIST_COUNT!"
    exit 1
fi
echo "Verified exact count: $HIST_COUNT/31 daily history files present."

echo "============================================="
echo " Period 2017-10 successfully completed and validated."
echo " Submitting next period "
echo "============================================="
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R1_SIMGM
python3 scripts/chain_opl.py --current-date 2017-11-01 --submit
