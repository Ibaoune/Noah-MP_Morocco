#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=val_schaake96_0117
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/logs/012017/schaake96_val_2017-01_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/logs/012017/schaake96_val_2017-01_%j.err
#SBATCH --time=01:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env

echo "============================================="
echo " Monthly Validation: OL_R3_SCHAAKE96 - 2017-01"
echo " Start: 2017-01-01 | End: 2017-02-01"
echo " Config: /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/generated/configs/lis_schaake96_2017-01.config"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/generated/configs/lis_schaake96_2017-01.config

echo "============================================="
echo " Verifying and Staging Restart for 2017-02-01 "
echo "============================================="

EXPECTED_RST="LIS_RST_NOAHMP401_201702010000.d01.nc"
RST_SRC=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/output/2017-01/SURFACEMODEL -name "$EXPECTED_RST" | head -n 1)

if [ -n "$RST_SRC" ] && [ -f "$RST_SRC" ]; then
    echo "SUCCESS: Found restart file $RST_SRC"
    cp "$RST_SRC" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/restarts/
    echo "Copied to /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/restarts/$EXPECTED_RST"
else
    echo "ERROR: Restart file $EXPECTED_RST not found in /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R3_SCHAAKE96/output/2017-01/SURFACEMODEL!"
    exit 1
fi

echo "Validation run for 2017-01 complete. STOPPING without submitting next month."
