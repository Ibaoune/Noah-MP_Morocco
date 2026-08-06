#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=val_2016_2020
#SBATCH --output=logs/val_2016_2020_%j.out
#SBATCH --error=logs/val_2016_2020_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --partition=compute

# ============================================================
# Script SLURM — Validation Indépendante LIS/Noah-MP (2016-2020)
# ============================================================

set -e  # Arrêt si erreur

if [ -n "$SLURM_SUBMIT_DIR" ]; then
    POSTPROC_DIR="$SLURM_SUBMIT_DIR"
else
    POSTPROC_DIR="$(cd "$(dirname "$0")/.." && pwd)"
fi

cd "$POSTPROC_DIR"

echo "============================================================"
echo "  Démarrage de la validation indépendante (2016-2020)"
echo "  Date       : $(date)"
echo "  Répertoire : $(pwd)"
echo "  Node       : $HOSTNAME"
echo "============================================================"
echo ""

# Activer l'environnement conda
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Step 1: Checking configurations..."
python scripts/run_postproc.py --check-configs

echo ""
echo "Step 2: Generating independent validation figures..."
python scripts/run_postproc.py --recipe configs/recipes/smap_cdf_independent_validation_2016_2020.yaml --make-figures

echo ""
echo "============================================================"
echo "  Validation completed — $(date)"
echo "============================================================"
