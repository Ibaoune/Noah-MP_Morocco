#!/bin/bash
# =============================================================================
# submit_download_wapor.sh
#
# SLURM job to download FAO WaPOR v3 data for postproc_02 validation.
# Downloads: AETI, T, E, NPP at L2 (100m, dekadal) for 2015–2020.
#
# Prerequisites:
#   export WAPOR_API_TOKEN=<your_token>
#   pip install wapordl
#   Register at: https://wapor.apps.fao.org/
#
# Usage:
#   sbatch submit_download_wapor.sh
#
# Output:
#   data/validation/evapotranspiration/WaPOR/<component>/
#   scripts/download/validation/WaPOR/logs/wapor_<jobid>.out
# =============================================================================

#SBATCH --job-name=wapor_download
#SBATCH --array=0-3
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=8G
#SBATCH --time=04:00:00
#SBATCH --partition=compute
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/WaPOR/logs/wapor_%a_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/WaPOR/logs/wapor_%a_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=mohammad.elaabaribao@um6p.ma

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
BASE=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
SCRIPT=${BASE}/scripts/download/validation/WaPOR/download_wapor.py

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

# ---------------------------------------------------------------------------
# WaPOR token must be set in environment or ~/.wapor_token
# Uncomment and set if not already in your environment:
# export WAPOR_API_TOKEN="your_token_here"
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Component selection (array index → component name)
# ---------------------------------------------------------------------------
COMPONENTS=("AETI" "T" "E" "NPP")
COMPONENT=${COMPONENTS[$SLURM_ARRAY_TASK_ID]}

echo "======================================================="
echo " WaPOR v3 Download — Task ${SLURM_ARRAY_TASK_ID}: ${COMPONENT}"
echo " Start: $(date)"
echo "======================================================="

python3 ${SCRIPT} \
    --start_date "2015-01-01" \
    --end_date   "2020-12-31" \
    --components "${COMPONENT}" \
    --level      L2

EXIT_CODE=$?
echo "Finished at: $(date)  (exit code: ${EXIT_CODE})"
exit ${EXIT_CODE}
