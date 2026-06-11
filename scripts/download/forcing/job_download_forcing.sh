#!/bin/bash
#SBATCH --job-name=dl_forcing
#SBATCH --output=logs/dl_%A_%a.out
#SBATCH --error=logs/dl_%A_%a.err
#SBATCH --time=12:00:00        # Maximum time per task (12 hours should be plenty for 1 year)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2      # 2 CPUs (one for MERRA, one for IMERG)
#SBATCH --mem=8G               # Memory limit
#SBATCH --array=2000-2023      # Job array for each year from 2000 to 2023

#SBATCH --nodes=1
#SBATCH --partition=compute

# ==============================================================================
# Script Name   : job_download_forcing.sh
# Author        : M. El Aabaribaoune (@um6p)
# Description   : SLURM job array script to download MERRA-2 and IMERG in parallel.
#                 Each task downloads 1 year of data, preventing timeouts.
#                 Both MERRA-2 and IMERG scripts run in parallel for that year.
# ==============================================================================

year=$SLURM_ARRAY_TASK_ID
start_date="${year}-01-01"
end_date="${year}-12-31"

# IMERG data starts exactly on June 1st 2000 for version 07
if [ "$year" -eq 2000 ]; then
    imerg_start="2000-06-01"
else
    imerg_start="${year}-01-01"
fi

echo "================================================================================"
echo "Starting Forcing Download for Year: $year"
echo "MERRA-2 Period : $start_date to $end_date"
echo "IMERG Period   : $imerg_start to $end_date"
echo "================================================================================"

# 1. Load the standard Toubkal environment modules (relative to this script's directory)
source ../../../arch/arch_toubkal.env

# 2. Load the python virtual environment
source ../../venv/bin/activate

# 3. Download Constants (Only needed once, so we tie it to the year 2000)
if [ "$year" -eq 2000 ]; then
    echo "Downloading MERRA-2 Constants (Topography)..."
    python3 download_merra2_const.py
fi

# 4. Run downloads in parallel for this specific year
echo "Starting MERRA-2 & IMERG downloads for $year..."

python3 download_merra2.py --start "$start_date" --end "$end_date" &
MERRA_PID=$!

python3 download_imerg.py --start "$imerg_start" --end "$end_date" &
IMERG_PID=$!

# Wait for both background python processes to finish
wait $MERRA_PID
MERRA_STATUS=$?

wait $IMERG_PID
IMERG_STATUS=$?

echo "================================================================================"
if [ $MERRA_STATUS -eq 0 ] && [ $IMERG_STATUS -eq 0 ]; then
    echo "SUCCESS: Forcing download for year $year completed successfully."
else
    echo "ERROR: Download failed for year $year. (MERRA_STATUS=$MERRA_STATUS, IMERG_STATUS=$IMERG_STATUS)"
    exit 1
fi
echo "================================================================================"
