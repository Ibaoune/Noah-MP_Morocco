#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job 1: Run LDT to generate domain and parameter file (lis_input.d01.nc)
#
######################
## TOUBKAL    UM6P ##
######################
#SBATCH --job-name=ldt_run
#SBATCH --output=logs/slurm/slurm_ldt_%j.log
#SBATCH --error=logs/slurm/slurm_ldt_%j.log
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --mem=32G
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting LDT Parameter Generation Job"
echo "=================================================="

echo "Waiting for data downloads to complete (if any are still running)..."
while pgrep -u $USER -f "download_parameters.py" > /dev/null || pgrep -u $USER -f "download_merra2.py" > /dev/null; do
    echo "Downloads still running... sleeping for 60s"
    sleep 60
done

echo "----------------------------------------"
echo "Running LDT..."
echo "----------------------------------------"
{
    time ./src/lisf/ldt/make/LDT configs/ldt.config
} > logs/ldt_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running LDT! Check logs/ldt_run.log"
    exit 1
fi
echo "LDT completed successfully. Generated data/lis_input/lis_input.d01.nc."
