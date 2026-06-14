#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Submit high scalability tests (T6, T7, T8) for LIS NoahMP Morocco
# 3-day simulation (Jun 1-4 2020) with 256, 512, and 896 MPI tasks.
# Max 32 procs/node.

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASEDIR"

mkdir -p logs/slurm

echo "============================================="
echo " Submitting High Scalability Tests (T6-T8)"
echo "============================================="
echo " Working dir: $BASEDIR"
echo ""

# ---- OPL Tests ----
echo ">>> OPL Tests <<<"
echo ""

echo "[OPL T6] 256 tasks (16x16) on 8 nodes"
sbatch --nodes=8 --ntasks=256 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.256tasks_8nodes OPL_256tasks_8nodes 256

echo "[OPL T7] 512 tasks (16x32) on 16 nodes"
sbatch --nodes=16 --ntasks=512 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.512tasks_16nodes OPL_512tasks_16nodes 512

echo "[OPL T8] 896 tasks (32x28) on 28 nodes"
sbatch --nodes=28 --ntasks=896 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.896tasks_28nodes OPL_896tasks_28nodes 896

echo ""
echo ">>> DA Tests <<<"
echo ""

echo "[DA T6] 256 tasks (16x16) on 8 nodes"
sbatch --nodes=8 --ntasks=256 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.256tasks_8nodes DA_256tasks_8nodes 256

echo "[DA T7] 512 tasks (16x32) on 16 nodes"
sbatch --nodes=16 --ntasks=512 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.512tasks_16nodes DA_512tasks_16nodes 512

echo "[DA T8] 896 tasks (32x28) on 28 nodes"
sbatch --nodes=28 --ntasks=896 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.896tasks_28nodes DA_896tasks_28nodes 896

echo ""
echo "============================================="
echo " High scalability tests (T6-T8) submitted!"
echo " Monitor with: squeue -u \$USER"
echo " Results will append to: experiments/scalability/timing_results.csv"
echo "============================================="
