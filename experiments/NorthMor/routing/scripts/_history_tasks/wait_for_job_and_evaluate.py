#!/usr/bin/env python3
import time
import subprocess
import sys
import os

job_id = "8174226"
print(f"Monitoring SLURM job {job_id}...")

while True:
    res = subprocess.run(["squeue", "-j", job_id], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if job_id not in res.stdout:
        print(f"Job {job_id} is no longer in squeue.")
        break
    # Print progress by checking count of files in output
    files = subprocess.run("find experiments/NorthMor/routing/output/OPL_2016_2020_corrigee -name 'LIS_HIST*.nc' | wc -l",
                           shell=True, stdout=subprocess.PIPE, text=True).stdout.strip()
    print(f"[{time.strftime('%H:%M:%S')}] Job {job_id} still running... Output files: {files}/1827", flush=True)
    time.sleep(30)

print(f"Job {job_id} finished! Verifying SLURM log...")
log_file = f"experiments/NorthMor/routing/logs/slurm_hymap2_5y_corr_{job_id}.out"
if os.path.exists(log_file):
    with open(log_file) as f:
        content = f.read()
    print(f"SLURM log tail:\n{content[-300:]}")

print("\nExecuting evaluation of corrected run...")
sys.stdout.flush()
ret = subprocess.run(["python3", "experiments/NorthMor/routing/scripts/_history_tasks/evaluate_t7_corrected_run.py"])
print(f"\nEvaluation finished with exit code {ret.returncode}")
