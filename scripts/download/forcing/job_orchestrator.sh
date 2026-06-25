#!/bin/bash
# ==============================================================================
# Script Name   : job_orchestrator.sh
# Author        : M. El Aabaribaoune (@um6p)
# Description   : Master orchestration script for the forcing data download workflow.
#                 It manages the sequential download and verification of MERRA-2 
#                 and IMERG forcing data year by year. For a given YEAR, it submits 
#                 the download array jobs, waits for their completion, and then 
#                 submits a verification job. If verification passes, it moves to 
#                 the next year. If it fails, it resubmits the current year in an 
#                 infinite loop until data integrity is guaranteed.
# Usage         : sbatch --export=ALL,YEAR=2008,END_YEAR=2020 job_orchestrator.sh
#                 (YEAR defaults to 2000, END_YEAR defaults to 2020)
# ==============================================================================
#SBATCH --job-name=orch_yr
#SBATCH --output=logs/orch_yr_%j.out
#SBATCH --error=logs/orch_yr_%j.err
#SBATCH --time=12:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1

YEAR=${YEAR:-2000}
END_YEAR=${END_YEAR:-2020}

if [ $YEAR -gt $END_YEAR ]; then
    echo "All years processed! Exiting."
    exit 0
fi

echo "=========================================================================="
echo " Processing Year: $YEAR"
echo "=========================================================================="

while true; do
    mkdir -p status
    rm -f status/status_${YEAR}.success
    
    echo "[$YEAR] Submitting MERRA-2 and IMERG downloads (Waiting for completion)..."
    
    sbatch --wait --export=ALL,YEAR=$YEAR job_download_merra2.sh &
    MERRA_PID=$!
    
    sbatch --wait --export=ALL,YEAR=$YEAR job_download_imerg.sh &
    IMERG_PID=$!
    
    wait $MERRA_PID
    wait $IMERG_PID
    
    echo "[$YEAR] Downloads finished. Running verification job..."
    
    sbatch --wait --job-name=chk_${YEAR} job_check_single_year.sh $YEAR
    
    if [ -f "status/status_${YEAR}.success" ]; then
        echo "[$YEAR] SUCCESS: Year $YEAR is 100% complete and verified!"
        break 
    else
        echo "[$YEAR] INCOMPLETE: Missing or corrupted files found."
        echo "[$YEAR] The check script has already deleted the corrupted files."
        echo "[$YEAR] Resubmitting downloads for $YEAR in 10 seconds..."
        sleep 10
    fi
done

NEXT_YEAR=$((YEAR + 1))
echo "Year $YEAR is finished. Submitting job for $NEXT_YEAR..."
sbatch --export=ALL,YEAR=$NEXT_YEAR,END_YEAR=$END_YEAR job_orchestrator.sh
