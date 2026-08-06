#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=postproc_2016_2020
#SBATCH --output=logs/postproc_2016_2020_%j.out
#SBATCH --error=logs/postproc_2016_2020_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --partition=compute

# ============================================================
# Script SLURM — Post-processing LIS/Noah-MP (2016-2020)
# ============================================================

set -e  # Arrêt si erreur

if [ -n "$SLURM_SUBMIT_DIR" ]; then
    POSTPROC_DIR="$SLURM_SUBMIT_DIR"
else
    POSTPROC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
fi
LOG_DIR="${POSTPROC_DIR}/logs"

echo "============================================================"
echo "  LIS/Noah-MP Post-Processing — $(date)"
echo "  Postproc dir : ${POSTPROC_DIR}"
echo "============================================================"

# Créer le dossier logs si nécessaire
mkdir -p "${LOG_DIR}"

# Activer l'environnement conda
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

# Aller dans le répertoire postproc
cd "${POSTPROC_DIR}"

# ------------------------------------------------------------
# 1. Vérification des configs
# ------------------------------------------------------------
echo ""
echo "Step 1: Checking configurations..."
python scripts/run_postproc.py --check-configs

# ------------------------------------------------------------
# 2. Exécution des figures intermédiaires et finaux
# ------------------------------------------------------------
echo ""
echo "Step 2: Generating all intermediate fields and metric figures..."
python scripts/run_postproc.py \
    --recipe configs/recipes/smap_cdf_sensitivity_2016_2020.yaml \
    --make-figures \
    --make-hydrology-figures

echo ""
echo "Step 3: Generating manuscript figures..."
python scripts/run_postproc.py \
    --recipe configs/recipes/paper_manuscript_figures.yaml \
    --make-figures

echo ""
echo "============================================================"
echo "  Post-processing completed — $(date)"
echo "============================================================"
