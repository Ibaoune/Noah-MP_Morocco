#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# job_3c_lis_da_joint_sebou.sh
#
# Experiment DA-Joint: Joint assimilation of SMAP SM + MODIS LAI (EnKF, 20 members)
# 3-day test run: 2020-06-01 to 2020-06-04
#
# Prerequisites:
#   - job_1_ldt_sebou.sh must have completed (data/lis_input.d01_sebou.nc)
#   - job_preprocess_modis_lai.sh must have completed
#     (data/observations/MODIS_LAI/processed/ must be populated)
#   - SMAP data must be downloaded
#     (data/observations/SMAP/SPL3SMP.009/ must be populated)
#
# Usage:
#   sbatch scripts/jobs/job_3c_lis_da_joint_sebou.sh
#
######################
##  TOUBKAL  UM6P   ##
######################
#SBATCH --job-name=lis_da_joint_sebou
#SBATCH --output=logs/slurm/slurm_da_joint_sebou_%j.log
#SBATCH --error=logs/slurm/slurm_da_joint_sebou_%j.log
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -euo pipefail

cd $SLURM_SUBMIT_DIR
source arch/arch_toubkal.env

echo "=================================================="
echo " DA-Joint: SMAP SM + MODIS LAI Assimilation (Sebou)"
echo "=================================================="
echo " Nodes:  $SLURM_NNODES  |  Tasks: $SLURM_NTASKS"
echo " Job ID: $SLURM_JOB_ID"
echo " Start:  $(date)"
echo "=================================================="

# Pre-flight checks
if [ ! -f "data/lis_input.d01_sebou.nc" ]; then
    echo "ERROR: data/lis_input.d01_sebou.nc not found!"
    exit 1
fi

LAI_PROC="data/observations/MODIS_LAI/processed"
if [ ! -d "$LAI_PROC" ] || [ -z "$(ls $LAI_PROC 2>/dev/null)" ]; then
    echo "ERROR: Processed MODIS LAI directory not found or empty: $LAI_PROC"
    echo "Please run job_preprocess_modis_lai.sh first."
    exit 1
fi

SMAP_DIR="data/observations/SMAP/SPL3SMP.009"
if [ ! -d "$SMAP_DIR" ] || [ -z "$(ls $SMAP_DIR 2>/dev/null)" ]; then
    echo "ERROR: SMAP data directory not found or empty: $SMAP_DIR"
    exit 1
fi

echo "Running Joint DA (SMAP SM + MODIS LAI)..."
{
    time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.da_joint
} > logs/lis_da_joint_sebou_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "ERROR: DA-Joint run failed. Check logs/lis_da_joint_sebou_run.log"
    exit 1
fi
echo "DA-Joint simulation completed successfully. End: $(date)"
