#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# job_3a_lis_da_sm_sebou.sh
#
# Experiment DA-SM: SMAP Soil Moisture assimilation ONLY (EnKF, 20 members)
# 3-day test run: 2020-06-01 to 2020-06-04
#
# Usage:
#   sbatch scripts/jobs/job_3a_lis_da_sm_sebou.sh
#
######################
##  TOUBKAL  UM6P   ##
######################
#SBATCH --job-name=lis_da_sm_sebou
#SBATCH --output=logs/slurm/slurm_da_sm_sebou_%j.log
#SBATCH --error=logs/slurm/slurm_da_sm_sebou_%j.log
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --time=06:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -euo pipefail

cd $SLURM_SUBMIT_DIR
source arch/arch_toubkal.env

echo "=================================================="
echo "  DA-SM: SMAP Soil Moisture Assimilation (Sebou)"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES  |  Tasks: $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo " Start:  $(date)"
echo "=================================================="

if [ ! -f "data/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input.d01_sebou.nc not found!"
    echo "Please run job_1_ldt_sebou.sh first."
    exit 1
fi

echo "Running SMAP-SM Data Assimilation..."
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.da_sm_sebou
} > logs/lis_da_sm_sebou_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "ERROR: DA-SM run failed. Check logs/lis_da_sm_sebou_run.log"
    exit 1
fi
echo "DA-SM simulation completed successfully. End: $(date)"
