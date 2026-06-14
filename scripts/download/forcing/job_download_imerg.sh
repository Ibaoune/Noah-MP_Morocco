#!/bin/bash
#SBATCH --job-name=dl_imerg
#SBATCH --output=logs/dl_imerg_%A_%a.out
#SBATCH --error=logs/dl_imerg_%A_%a.err
#SBATCH --time=12:00:00        # Maximum time per task (12 hours should be plenty for 1 month)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1      # 1 CPU
#SBATCH --mem=4G               # Memory limit
#SBATCH --array=1-12           # Job array for each month (1 to 12)
#SBATCH --nodes=1
#SBATCH --partition=compute

# ==============================================================================
# Script Name   : job_download_imerg.sh
# Author        : M. El Aabaribaoune (@um6p)
# Description   : SLURM job array script to download NASA GPM IMERG forcing data.
#                 This script is designed to be submitted one year at a time.
#                 It uses a job array (1-12) where each task handles exactly 1 month.
#                 This granular approach prevents memory issues, speeds up downloads 
#                 via parallelization, and allows easy retries of failed months.
#
# Usage         : sbatch --export=ALL,YEAR=YYYY --array=1-12 job_download_imerg.sh
# Example       : sbatch --export=ALL,YEAR=2010 --array=1-12 job_download_imerg.sh
#
# Dependencies  : Requires python script `download_imerg.py` and Earthdata credentials.
#                 Logs are saved to the `logs/` subdirectory.
# ==============================================================================

year=${YEAR:-2020}
month=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

start_date="${year}-${month}-01"
# Calculate the last day of the current month
end_date=$(date -d "${start_date} + 1 month - 1 day" +%Y-%m-%d)

# IMERG data starts exactly on June 1st 2000 for version 07
if [ "$year" -eq 2000 ] && [ "$SLURM_ARRAY_TASK_ID" -lt 6 ]; then
    echo "================================================================================"
    echo "Skipping IMERG Download for $year-$month (No data before June 2000)"
    echo "================================================================================"
    exit 0
fi

echo "================================================================================"
echo "Starting IMERG Download for: $year-$month"
echo "Period : $start_date to $end_date"
echo "================================================================================"

# 1. Load the standard Toubkal environment modules (relative to this script's directory)
source ../../../arch/arch_toubkal.env

# 2. Load the python virtual environment
source ../../venv/bin/activate

# 3. Run download
python3 download_imerg.py --start "$start_date" --end "$end_date"
IMERG_STATUS=$?

echo "================================================================================"
if [ $IMERG_STATUS -eq 0 ]; then
    echo "SUCCESS: IMERG download for $year-$month completed successfully."
else
    echo "ERROR: IMERG Download failed for $year-$month. (STATUS=$IMERG_STATUS)"
    exit 1
fi
echo "================================================================================"
