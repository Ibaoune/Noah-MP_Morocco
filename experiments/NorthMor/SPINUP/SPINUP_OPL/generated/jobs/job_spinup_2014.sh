#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=spinup_2014
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/logs/2014/spinup_2014_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/logs/2014/spinup_2014_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
# Navigate to the ROOT of the NoahMP_Morocco project for LIS execution
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/../../../

# Load computing environment (Modules, Conda, Compilers, etc.)
source arch/arch_toubkal.env

echo "============================================="
echo " LIS NorthMor - SPINUP - Period 2014"
echo " Start: 2014-01-01 | End: 2015-01-01 | Mode: restart"
echo "============================================="

# Execute LIS simulation from the root directory
time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/generated/configs/lis_spinup_2014.config

echo "============================================="
echo " Post-processing & Validation "
echo "============================================="

# Find the generated restart file required for the next period
RESTART_SRC=$(find /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/output/2014/SURFACEMODEL -name "LIS_RST_NOAHMP401_201501010000.d01.nc" | head -n 1)

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    echo "Found restart file: $RESTART_SRC"
    cp "$RESTART_SRC" /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/restarts/
    echo "Successfully copied restart file to /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup/restarts/"
else
    echo "ERROR: Restart file LIS_RST_NOAHMP401_201501010000.d01.nc not found in output directory!"
    exit 1
fi

echo "============================================="
echo " Submitting next period "
echo "============================================="
# Change back to spinup directory to submit the next job
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/spinup
# Trigger the python script for the next chronological step
python3 scripts/chain_spinup.py --current-date 2015-01-01 --submit
