#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job 1: Run LDT to generate domain and parameter file for Sebou Basin (lis_input.d01_sebou.nc)
#
######################
# SBATCH --job-name=ldt_sebou
# SBATCH --output=logs/slurm/slurm_ldt_sebou_%j.log
# SBATCH --error=logs/slurm/slurm_ldt_sebou_%j.log
# SBATCH --nodes=1
# SBATCH --time=02:00:00
# SBATCH --mem=32G
# SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting LDT Parameter Generation Job for Sebou Basin"
echo "=================================================="

echo "----------------------------------------"
echo "Running LDT..."
echo "----------------------------------------"
{
    time ./src/lisf/ldt/make/LDT configs/ldt.config.sebou
} > logs/ldt_run_sebou.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running LDT! Check logs/ldt_run_sebou.log"
    exit 1
fi
echo "LDT completed successfully. Generated data/lis_input.d01_sebou.nc."
