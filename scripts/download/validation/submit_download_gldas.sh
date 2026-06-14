#!/bin/bash
# =============================================================================
# submit_download_gldas.sh
#
# SLURM job array to download GLDAS products for postproc_01 intercomparison.
# One array task per GLDAS product (4 tasks total).
#
# Usage:
#   sbatch submit_download_gldas.sh
#
# Outputs:
#   data/validation/intercomparison/GLDAS/<product>/
#   scripts/download/validation/logs/gldas_<product>.out
# =============================================================================

#SBATCH --job-name=gldas_download
#SBATCH --array=0-3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=08:00:00
#SBATCH --partition=compute
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/logs/gldas_%a_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/logs/gldas_%a_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=mohammad.elaabaribao@um6p.ma

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
BASE=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
SCRIPT=${BASE}/scripts/download/validation/download_gldas.py

# Export NASA credentials for earthaccess
export EARTHDATA_USERNAME="el.aabaribaoune@gmail.com"
export EARTHDATA_PASSWORD="mohkaj111@ZO"

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

# ---------------------------------------------------------------------------
# Product selection (array index → product name)
# ---------------------------------------------------------------------------
PRODUCTS=("GLDAS_NOAH025_3H" "GLDAS_VIC10_3H" "GLDAS_CLSM10_3H" "GLDAS_CLSM025_DA1_D")
PRODUCT=${PRODUCTS[$SLURM_ARRAY_TASK_ID]}

echo "======================================================="
echo " GLDAS Download — Task ${SLURM_ARRAY_TASK_ID}: ${PRODUCT}"
echo " Start: $(date)"
echo "======================================================="

python3 ${SCRIPT} \
    --product    "${PRODUCT}" \
    --start_date "2015-01-01" \
    --end_date   "2020-12-31"

EXIT_CODE=$?
echo "Finished at: $(date)  (exit code: ${EXIT_CODE})"
exit ${EXIT_CODE}
