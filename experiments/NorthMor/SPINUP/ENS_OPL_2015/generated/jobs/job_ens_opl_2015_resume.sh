#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=ens_opl_2015_2015
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/logs/ens_opl_2015_2015_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/logs/ens_opl_2015_2015_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/../../../../

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - ENS_OPL_2015 - Year 2015"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/generated/configs/lis_ens_opl_2015_resume.config

echo "============================================="
echo " Post-processing: Copying Restarts to 2016 DA setup "
echo "============================================="

SURF_RST=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/output/2015/SURFACEMODEL -name "LIS_RST_NOAHMP401_201601010000.d01.nc" | head -n 1)
PERT_RST=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/output/2015/DAPERT -name "LIS_DAPERT_201601010000.d01.bin" | head -n 1)

DA_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/1Yr_2016/ens_opl_2015/../assim/restarts"

if [ -n "$SURF_RST" ] && [ -f "$SURF_RST" ] && [ -n "$PERT_RST" ] && [ -f "$PERT_RST" ]; then
    echo "Found restart files."
    cp "$SURF_RST" $DA_DIR/surf/
    cp "$PERT_RST" $DA_DIR/pert/
    echo "Successfully copied restarts to $DA_DIR"
else
    echo "ERROR: Restart files not found in output directory!"
    exit 1
fi

echo "Done."
