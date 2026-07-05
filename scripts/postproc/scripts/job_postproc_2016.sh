#!/bin/bash
#SBATCH --job-name=postproc_2016
#SBATCH --output=logs/postproc_%j.out
#SBATCH --error=logs/postproc_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --partition=compute

# ============================================================
# Script SLURM — Post-processing LIS/Noah-MP (2016)
# ============================================================
# Utilisation :
#   sbatch scripts/job_postproc_2016.sh
#   sbatch scripts/job_postproc_2016.sh smap_cdf_sensitivity_2016
#
# Le premier argument optionnel est l'ID de la recette.
# Par défaut : smap_cdf_sensitivity_2016
# ============================================================

set -e  # Arrêt si erreur

# ------------------------------------------------------------
# Paramètres
# ------------------------------------------------------------
RECIPE_ID="${1:-smap_cdf_sensitivity_2016}"
POSTPROC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RECIPE_PATH="configs/recipes/${RECIPE_ID}.yaml"
LOG_DIR="${POSTPROC_DIR}/logs"

echo "============================================================"
echo "  LIS/Noah-MP Post-Processing — $(date)"
echo "  Postproc dir : ${POSTPROC_DIR}"
echo "  Recipe       : ${RECIPE_ID}"
echo "  Recipe path  : ${RECIPE_PATH}"
echo "============================================================"

# Créer le dossier logs si nécessaire
mkdir -p "${LOG_DIR}"

# Activer l'environnement conda si nécessaire
# (décommenter et adapter selon votre configuration)
# module load anaconda3/2023.09
# conda activate lis_postproc

# Aller dans le répertoire postproc
cd "${POSTPROC_DIR}"

# ------------------------------------------------------------
# 1. Vérification des configs
# ------------------------------------------------------------
echo ""
echo "Step 1: Checking configurations..."
python scripts/run_postproc.py --check-configs

# ------------------------------------------------------------
# 2. Dry-run
# ------------------------------------------------------------
echo ""
echo "Step 2: Dry-run..."
python scripts/run_postproc.py \
    --recipe "${RECIPE_PATH}" \
    --dry-run

# ------------------------------------------------------------
# 3. Exécution complète avec figures et PDF
# ------------------------------------------------------------
echo ""
echo "Step 3: Running post-processing..."
python scripts/run_postproc.py \
    --recipe "${RECIPE_PATH}" \
    --make-figures \
    --make-pdf

echo ""
echo "============================================================"
echo "  Post-processing completed — $(date)"
echo "  Outputs: ${POSTPROC_DIR}/outputs/matrix_2016/"
echo "============================================================"
