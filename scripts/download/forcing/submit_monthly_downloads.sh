#!/bin/bash
# ==============================================================================
# Script Name   : submit_monthly_downloads.sh
# Description   : Orchestrator to launch monthly forcing downloads year by year.
#                 It submits year 2020, then chains 2019 using SLURM dependencies,
#                 down to 2000.
# ==============================================================================

# Start year
CURRENT_YEAR=2020
# End year
END_YEAR=2000

echo "Submitting monthly array job for year $CURRENT_YEAR..."
# Submit the first year without dependencies
JOB_ID=$(sbatch --export=ALL,YEAR=$CURRENT_YEAR --parsable job_download_forcing.sh)
echo "Submitted $CURRENT_YEAR with JOB_ID: $JOB_ID"

# Loop down to END_YEAR
for (( year=CURRENT_YEAR-1; year>=END_YEAR; year-- )); do
    echo "Submitting monthly array job for year $year (depends on $JOB_ID)..."
    # Submit with dependency 'afterok' so it only runs if the previous year succeeded completely
    JOB_ID=$(sbatch --dependency=afterok:$JOB_ID --export=ALL,YEAR=$year --parsable job_download_forcing.sh)
    echo "Submitted $year with JOB_ID: $JOB_ID"
done

echo "========================================================================"
echo "All years successfully queued! Run 'squeue -u \$USER' to monitor."
echo "========================================================================"
