#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Submit the SLURM job
JOB_ID=$(sbatch jobs/job_full_v0_cpu.sh | awk '{print $4}')

if [ -n "$JOB_ID" ]; then
    echo "Successfully submitted job: $JOB_ID"
    echo "Stdout log: jobs/logs/full_v0_cpu_${JOB_ID}.out"
    echo "Stderr log: jobs/logs/full_v0_cpu_${JOB_ID}.err"
    echo ""
    echo "To monitor the job, you can use the following commands:"
    echo "  squeue -j $JOB_ID"
    echo "  tail -f jobs/logs/full_v0_cpu_${JOB_ID}.out"
    echo "  bash jobs/check_full_v0_status.sh $JOB_ID"
else
    echo "Failed to submit job."
fi
