#!/bin/bash
# =============================================================================
# submit_download_fluxsat.sh
#
# SLURM job to download FLUXSAT v2 monthly GPP NetCDF files from Zenodo
# for validation of Noah-MP GPP outputs (postproc_02 Figures 2, 3, Supp).
#
# Dataset:  FLUXSAT v2 monthly GPP (0.05°, global)
# Period:   2015–2020 (validation period)
# Source:   https://doi.org/10.5281/zenodo.7761881
# Storage:  data/validation/vegetation/FLUXSAT_GPP/
#
# Usage:
#   sbatch submit_download_fluxsat.sh
#
# Output:
#   scripts/download/validation/FLUXSAT/logs/fluxsat_<jobid>.out
# =============================================================================

#SBATCH --job-name=fluxsat_download
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=4G
#SBATCH --time=02:00:00
#SBATCH --partition=compute
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/FLUXSAT/logs/fluxsat_%j.out
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/download/validation/FLUXSAT/logs/fluxsat_%j.err
#SBATCH --mail-type=END,FAIL
#SBATCH --mail-user=mohammad.elaabaribao@um6p.ma

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
BASE=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
SCRIPT=${BASE}/scripts/download/validation/FLUXSAT/download_fluxsat_gpp.py

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "======================================================="
echo " FLUXSAT v2 GPP Download — postproc_02 validation"
echo " Start: $(date)"
echo "======================================================="

python3 ${SCRIPT} \
    --start_year 2015 \
    --end_year   2020

EXIT_CODE=$?
echo "Finished at: $(date)  (exit code: ${EXIT_CODE})"
exit ${EXIT_CODE}
