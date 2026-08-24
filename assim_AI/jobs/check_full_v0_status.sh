#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

JOB_ID=$1

echo "======================================"
echo "    Full Run V0 Status Monitor"
echo "======================================"

if [ -n "$JOB_ID" ]; then
    echo "SLURM Job Status for ID: $JOB_ID"
    squeue -j $JOB_ID
    echo ""
    
    OUT_LOG="jobs/logs/full_v0_cpu_${JOB_ID}.out"
    ERR_LOG="jobs/logs/full_v0_cpu_${JOB_ID}.err"
    
    if [ -f "$OUT_LOG" ]; then
        echo "--- Last 20 lines of Stdout ($OUT_LOG) ---"
        tail -n 20 $OUT_LOG
        echo ""
    fi
    
    if [ -f "$ERR_LOG" ]; then
        echo "--- Last 20 lines of Stderr ($ERR_LOG) ---"
        tail -n 20 $ERR_LOG
        echo ""
    fi
else
    echo "No JOB_ID provided. To see specific job logs, run: bash jobs/check_full_v0_status.sh <JOB_ID>"
fi

echo "--- Dataset Progress (reports/full_run_v0_log.md) ---"
if [ -f "reports/full_run_v0_log.md" ]; then
    tail -n 20 reports/full_run_v0_log.md
else
    echo "Log file not created yet."
fi

echo ""
echo "--- Processed Monthly Files (data/processed/monthly_parts) ---"
if [ -d "data/processed/monthly_parts" ]; then
    COUNT=$(ls -1 data/processed/monthly_parts/ | grep parquet | wc -l)
    echo "Monthly parquet files created: $COUNT / 60"
else
    echo "Directory not created yet."
fi
echo "======================================"
