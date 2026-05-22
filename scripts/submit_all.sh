#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Submit all scalability tests for LIS NoahMP Morocco
# 3-day simulation (Jun 1-4 2020) with different MPI configs
# Max 32 procs/node, using mpirun (tested on Toubkal)

BASEDIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASEDIR"

mkdir -p logs/slurm

echo "============================================="
echo " Submitting Scalability Tests"
echo "============================================="
echo " Working dir: $BASEDIR"
echo ""

# Remove old results
rm -f experiments/scalability/timing_results.csv

# ---- OPL Tests ----
echo ">>> OPL Tests <<<"
echo ""

echo "[OPL T1] 4 tasks (2x2) on 1 node"
sbatch --nodes=1 --ntasks=4 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.4tasks_1node OPL_4tasks_1node 4

echo "[OPL T2] 16 tasks (4x4) on 1 node"
sbatch --nodes=1 --ntasks=16 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.16tasks_1node OPL_16tasks_1node 16

echo "[OPL T3] 32 tasks (4x8) on 1 node"
sbatch --nodes=1 --ntasks=32 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.32tasks_1node OPL_32tasks_1node 32

echo "[OPL T4] 64 tasks (8x8) on 2 nodes"
sbatch --nodes=2 --ntasks=64 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.64tasks_2nodes OPL_64tasks_2nodes 64

echo "[OPL T5] 128 tasks (8x16) on 4 nodes"
sbatch --nodes=4 --ntasks=128 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.opl.128tasks_4nodes OPL_128tasks_4nodes 128

echo ""
echo ">>> DA Tests <<<"
echo ""

echo "[DA T1] 4 tasks (2x2) on 1 node"
sbatch --nodes=1 --ntasks=4 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.4tasks_1node DA_4tasks_1node 4

echo "[DA T2] 16 tasks (4x4) on 1 node"
sbatch --nodes=1 --ntasks=16 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.16tasks_1node DA_16tasks_1node 16

echo "[DA T3] 32 tasks (4x8) on 1 node"
sbatch --nodes=1 --ntasks=32 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.32tasks_1node DA_32tasks_1node 32

echo "[DA T4] 64 tasks (8x8) on 2 nodes"
sbatch --nodes=2 --ntasks=64 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.64tasks_2nodes DA_64tasks_2nodes 64

echo "[DA T5] 128 tasks (8x16) on 4 nodes"
sbatch --nodes=4 --ntasks=128 scripts/jobs/job_scalability.sh \
    configs/scalability/lis.config.da.128tasks_4nodes DA_128tasks_4nodes 128

echo ""
echo "============================================="
echo " All 10 tests submitted!"
echo " Monitor with: squeue -u \$USER"
echo " Results in:   experiments/scalability/timing_results.csv"
echo " Logs in:      logs/slurm/"
echo "============================================="
