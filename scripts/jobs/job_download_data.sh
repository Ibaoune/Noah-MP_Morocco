#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# SLURM script to run all 3 download processes (MERRA-2, SMAP, and MODIS LAI) in parallel/sequence.
#
######################
#SBATCH --job-name=download_data
#SBATCH --output=logs/slurm/slurm_download_%j.log
#SBATCH --error=logs/slurm/slurm_download_%j.log
#SBATCH --nodes=1
#SBATCH --time=24:00:00
#SBATCH --mem=16G
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

# Detect repository root directory relative to the submission path
if [ -f "arch/arch_toubkal.env" ]; then
    echo "Already in repository root: $(pwd)"
elif [ -f "../../arch/arch_toubkal.env" ]; then
    echo "Navigating to repository root: $(pwd)/../.."
    cd ../..
elif [ -f "../arch/arch_toubkal.env" ]; then
    echo "Navigating to repository root: $(pwd)/.."
    cd ..
else
    echo "ERROR: Could not locate repository root containing arch/arch_toubkal.env"
    exit 1
fi

# Load required modules (loads Python and netrc settings)
source arch/arch_toubkal.env


echo "=================================================="
echo "Starting data download processes for the Sebou experiment"
echo "=================================================="

# Ensure directories are ready
mkdir -p data/met_forcing/MERRA2
mkdir -p data/observations/SMAP/SPL3SMP.009
mkdir -p data/observations/MODIS_LAI
mkdir -p logs


# Run download scripts in parallel, redirecting output to log files
echo "Launching MERRA-2 download script..."
python3 scripts/download/download_merra2.py > logs/download_merra2.log 2>&1 &
PID_MERRA=$!

echo "Launching SMAP Soil Moisture download script..."
python3 scripts/download/download_smap.py > logs/download_smap.log 2>&1 &
PID_SMAP=$!

echo "Launching MODIS LAI download script..."
python3 scripts/download/download_modis_lai.py > logs/download_modis_lai.log 2>&1 &
PID_LAI=$!

echo "All download processes started in the background."
echo "MERRA-2 download PID: $PID_MERRA (logs: logs/download_merra2.log)"
echo "SMAP SM download PID: $PID_SMAP (logs: logs/download_smap.log)"
echo "MODIS LAI download PID: $PID_LAI (logs: logs/download_modis_lai.log)"

# Wait for all background downloads to complete
wait $PID_MERRA
STATUS_MERRA=$?
wait $PID_SMAP
STATUS_SMAP=$?
wait $PID_LAI
STATUS_LAI=$?

echo "=================================================="
echo "Download Job Complete Summary:"
echo "MERRA-2 Download Exit Code: $STATUS_MERRA"
echo "SMAP SM Download Exit Code: $STATUS_SMAP"
echo "MODIS LAI Download Exit Code: $STATUS_LAI"
echo "=================================================="
