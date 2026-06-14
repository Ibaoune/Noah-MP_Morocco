#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# job_preprocess_modis_lai.sh
#
# Preprocess all MODIS MOD15A2H tile HDF files into global NetCDF4 files
# required by the LIS "MCD15A2H LAI" data assimilation plugin.
#
# Usage:
#   sbatch scripts/jobs/job_preprocess_modis_lai.sh
#
######################
##  TOUBKAL  UM6P   ##
######################
#SBATCH --job-name=preprocess_modis_lai
#SBATCH --output=logs/slurm/slurm_preprocess_modis_lai_%j.log
#SBATCH --error=logs/slurm/slurm_preprocess_modis_lai_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=12:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU

set -euo pipefail
cd $SLURM_SUBMIT_DIR

echo "=================================================="
echo "  MODIS LAI HDF -> NetCDF4 Preprocessing"
echo "=================================================="
echo " Job ID: $SLURM_JOB_ID"
echo " Start:  $(date)"
echo "=================================================="

# Load modules needed for GDAL (Python bindings) and NCO (ncrename)
module load GDAL/3.7.1-foss-2023a

echo ""
echo "Starting preprocessing..."
python3 scripts/fix/preprocess_modis_lai.py

echo ""
echo "=================================================="
echo "  Preprocessing complete:  $(date)"
echo "  Output files:"
find data/observations/MODIS_LAI/processed -name "*.nc4" | sort | head -20 || true
echo "  Total NC4 files: $(find data/observations/MODIS_LAI/processed -name '*.nc4' | wc -l)"
echo "=================================================="
