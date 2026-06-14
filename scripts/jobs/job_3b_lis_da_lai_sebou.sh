#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# job_3b_lis_da_lai_sebou.sh
#
# Experiment DA-LAI: MODIS MCD15A2H LAI assimilation ONLY (EnKF, 20 members)
# 3-day test run: 2020-06-01 to 2020-06-04
#
# Prerequisites:
#   - job_1_ldt_sebou.sh must have completed (data/lis_input/lis_input.d01_sebou.nc)
#   - job_preprocess_modis_lai.sh must have completed
#     (data/observations/MODIS_LAI/processed/ must be populated)
#
# Usage:
#   sbatch scripts/jobs/job_3b_lis_da_lai_sebou.sh
#
######################
##  TOUBKAL  UM6P   ##
######################
#SBATCH --job-name=lis_da_lai_sebou
#SBATCH --output=logs/slurm/slurm_da_lai_sebou_%j.log
#SBATCH --error=logs/slurm/slurm_da_lai_sebou_%j.log
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --time=06:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -euo pipefail

cd $SLURM_SUBMIT_DIR
source arch/arch_toubkal.env

echo "=================================================="
echo " DA-LAI: MODIS LAI Assimilation (Sebou)"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES  |  Tasks: $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo " Start:  $(date)"
echo "=================================================="

if [ ! -f "data/lis_input/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input/lis_input.d01_sebou.nc not found!"
    exit 1
fi

LAI_PROC="data/observations/MODIS_LAI/processed"
if [ ! -d "$LAI_PROC" ] || [ -z "$(ls $LAI_PROC 2>/dev/null)" ]; then
    echo "ERROR: Processed MODIS LAI directory not found or empty: $LAI_PROC"
    echo "Please run job_preprocess_modis_lai.sh first."
    exit 1
fi

echo "Running MODIS LAI Data Assimilation..."
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.da_lai_sebou
} > logs/lis_da_lai_sebou_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "ERROR: DA-LAI run failed. Check logs/lis_da_lai_sebou_run.log"
    exit 1
fi
echo "DA-LAI simulation completed successfully. End: $(date)"
