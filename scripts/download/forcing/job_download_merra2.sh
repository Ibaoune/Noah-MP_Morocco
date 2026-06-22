#!/bin/bash
#SBATCH --job-name=dl_merra2
#SBATCH --output=logs/dl_merra2_%A_%a.out
#SBATCH --error=logs/dl_merra2_%A_%a.err
#SBATCH --time=12:00:00        # Maximum time per task (12 hours should be plenty for 1 month)
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1      # 1 CPU
#SBATCH --mem=4G               # Memory limit
#SBATCH --array=1-12           # Job array for each month (1 to 12)
#SBATCH --nodes=1
#SBATCH --partition=compute

# ==============================================================================
# Script Name   : job_download_merra2.sh
# Author        : M. El Aabaribaoune (@um6p)
# Description   : SLURM job array script to download NASA MERRA-2 forcing data.
#                 This script is designed to be submitted one year at a time.
#                 It uses a job array (1-12) where each task handles exactly 1 month.
#                 If YEAR=2000 and month=1, it will also download MERRA-2 Constants.
#                 This granular approach prevents API timeouts and allows easy retries.
#
# Usage         : sbatch --export=ALL,YEAR=YYYY --array=1-12 job_download_merra2.sh
# Example       : sbatch --export=ALL,YEAR=2010 --array=1-12 job_download_merra2.sh
#
# Dependencies  : Requires python scripts `download_merra2.py`, `download_merra2_const.py`.
#                 Logs are saved to the `logs/` subdirectory.
# ==============================================================================

year=${YEAR:-2020}
month=$(printf "%02d" $SLURM_ARRAY_TASK_ID)

start_date="${year}-${month}-01"
# Calculate the last day of the current month
end_date=$(date -d "${start_date} + 1 month - 1 day" +%Y-%m-%d)

echo "================================================================================"
echo "Starting MERRA-2 Download for: $year-$month"
echo "Period : $start_date to $end_date"
echo "================================================================================"

# 1. Load the python environment
module load Anaconda3/2020.11

# 3. Download Constants (Only needed once, so we tie it to the year 2000, month 1)
if [ "$year" -eq 2000 ] && [ "$SLURM_ARRAY_TASK_ID" -eq 1 ]; then
    echo "Downloading MERRA-2 Constants (Topography)..."
    python3 download_merra2_const.py
fi

# 4. Run download
python3 download_merra2.py --start "$start_date" --end "$end_date"
MERRA_STATUS=$?

echo "================================================================================"
if [ $MERRA_STATUS -eq 0 ]; then
    echo "SUCCESS: MERRA-2 download for $year-$month completed successfully."
else
    echo "ERROR: MERRA-2 Download failed for $year-$month. (STATUS=$MERRA_STATUS)"
    exit 1
fi
echo "================================================================================"
