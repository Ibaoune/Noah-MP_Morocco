#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_nocdf_TEST_nowilt_2018-07
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/logs/072018/DA_nocdf_TEST_nowilt_2018-07_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/logs/072018/DA_nocdf_TEST_nowilt_2018-07_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/../../../../

source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - DA - Period 2018-07"
echo " Start: 2018-07-01 | End: 2018-08-01"
echo "============================================="

time mpirun -n 32 ./src/lisf_nowilt/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/generated/configs/lis_DA_nocdf_TEST_nowilt_2018-07.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

SURF_RST=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/output/2018-07/SURFACEMODEL -name "LIS_RST_NOAHMP401_201808010000.d01.nc" | head -n 1)
PERT_RST=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/output/2018-07/DAPERT -name "LIS_DAPERT_201808010000.d01.bin" | head -n 1)

if [ -n "$SURF_RST" ] && [ -f "$SURF_RST" ] && [ -n "$PERT_RST" ] && [ -f "$PERT_RST" ]; then
    echo "Found restart files."
    cp "$SURF_RST" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/restarts/surf/
    cp "$PERT_RST" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/restarts/pert/
    echo "Successfully copied restarts to /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt/restarts/"
else
    echo "ERROR: Restart files not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/DA_nocdf_TEST_nowilt
/home/mohammad.elaabaribao/.conda/envs/smap-xai-audit/bin/python scripts/chain_da.py --current-date 2018-08-01 --submit
