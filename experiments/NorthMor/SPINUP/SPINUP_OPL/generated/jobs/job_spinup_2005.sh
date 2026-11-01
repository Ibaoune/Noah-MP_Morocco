#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=spinup_2005
#SBATCH --output=experiments/NorthMor/spinup/logs/spinup_2005_%j.log
#SBATCH --error=experiments/NorthMor/spinup/logs/spinup_2005_%j.err
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -x
cd $SLURM_SUBMIT_DIR

# Load environment
source arch/arch_toubkal.env

# Ensure output directory exists
mkdir -p experiments/NorthMor/spinup/output/2005

echo "============================================="
echo " LIS NorthMor Spin-up - Year 2005"
echo "============================================="

# Run LIS
time mpirun -n 32 ./src/lisf/lis/LIS -f experiments/NorthMor/spinup/lis_spinup_2005.config

echo "============================================="
echo " Post-processing "
echo "============================================="

# Extract and copy the restart file for the next year
RESTART_SRC=$(find experiments/NorthMor/spinup/output/2005/SURFACEMODEL -name "LIS_RST_NOAHMP401_200601010000.d01.nc")

if [ -n "$RESTART_SRC" ] && [ -f "$RESTART_SRC" ]; then
    echo "Found restart file: $RESTART_SRC"
    cp $RESTART_SRC experiments/NorthMor/spinup/restarts/
    echo "Successfully copied restart file to experiments/NorthMor/spinup/restarts/"
else
    echo "ERROR: Restart file LIS_RST_NOAHMP401_200601010000.d01.nc not found in output directory!"
    exit 1
fi

echo " DONE "
