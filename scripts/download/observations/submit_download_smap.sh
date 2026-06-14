#!/bin/bash
# =============================================================================
# submit_download_smap.sh
#
# Description:
#   SLURM job script to download NASA SMAP L3 Soil Moisture (SPL3SMP_E) data
#   for the Sebou-Saïss basin. To ensure stability, this script uses a job 
#   array (1-12) where each task independently downloads data for a single month.
#
# Author: M. El Aabaribaoune (@um6p)
# Last Updated: 2026-06-14
#
# Usage:
#   sbatch --export=ALL,YEAR=2020 submit_download_smap.sh
#
# =============================================================================

#SBATCH --job-name=smap_dl
#SBATCH --array=1-12
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=12:00:00
#SBATCH --partition=compute
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/observations/logs/smap_%A_%a.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/observations/logs/smap_%A_%a.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=mohammad.elaabaribao@um6p.ma

if [ -z "$YEAR" ]; then
    echo "Error: YEAR is not set. Use: sbatch --export=ALL,YEAR=2020 submit_download_smap.sh"
    exit 1
fi

BASE=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
SCRIPT=${BASE}/scripts/download/observations/download_smap_spl3smp_e.py

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

MONTH=$(printf "%02d" $SLURM_ARRAY_TASK_ID)
START_DATE="${YEAR}-${MONTH}-01"
END_DATE=$(date -d "${START_DATE} +1 month -1 day" +%Y-%m-%d)

echo "======================================================="
echo " SMAP SPL3SMP_E Download — ${YEAR}-${MONTH}"
echo " Start: $(date)"
echo " Range: ${START_DATE} to ${END_DATE}"
echo "======================================================="

python3 ${SCRIPT} \
    --start_date "${START_DATE}" \
    --end_date   "${END_DATE}"

EXIT_CODE=$?
echo "Finished at: $(date)  (exit code: ${EXIT_CODE})"
exit ${EXIT_CODE}
