#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=opl_noirr_2016-08
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/logs/082016/opl_noirr_2016-08_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/logs/082016/opl_noirr_2016-08_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/../../../../

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - OPL - Period 2016-08"
echo " Start: 2016-08-01 | End: 2016-09-01"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/generated/configs/lis_opl_noirr_2016-08.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

RESTART_SRC=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2016-08/SURFACEMODEL -name "LIS_RST_NOAHMP401_201609010000.d01.nc" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    echo "Found restart file: $RESTART_SRC"
    cp "$RESTART_SRC" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/
    echo "Successfully copied restart file to /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/"
else
    echo "ERROR: Restart file LIS_RST_NOAHMP401_201609010000.d01.nc not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020
python3 scripts/chain_opl.py --current-date 2016-09-01 --submit
