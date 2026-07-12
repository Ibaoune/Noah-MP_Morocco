#!/bin/bash
#SBATCH --job-name=postproc_matrix2016
#SBATCH --output=scripts/postproc/logs/postproc_matrix2016_%j.out
#SBATCH --error=scripts/postproc/logs/postproc_matrix2016_%j.err
#SBATCH --time=02:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G

set -e

# ============================================================
# LIS/Noah-MP post-processing job
# Matrix: NorthMor / matrix_2016
# Experiments:
#   - OPL_noirr_2016
#   - DA_nocdf_noirr_2016
#   - DA_cdf_noirr_2016
# Recipe:
#   - smap_cdf_sensitivity_2016.yaml
# ============================================================

# Dans SLURM, BASH_SOURCE pointe vers /var/spool/..., on utilise SLURM_SUBMIT_DIR
PROJECT_ROOT="${SLURM_SUBMIT_DIR:-$PWD}"
POSTPROC_DIR="${PROJECT_ROOT}/scripts/postproc"
LOG_DIR="${POSTPROC_DIR}/logs"
RECIPE="configs/recipes/smap_cdf_sensitivity_2016.yaml"

mkdir -p "${LOG_DIR}"

# Activer l'environnement Python
source ~/.bashrc
conda activate postproc_env || echo "Warning: could not activate postproc_env, continuing..."

cd "${POSTPROC_DIR}"

export PYTHONPATH="${POSTPROC_DIR}/src:${PYTHONPATH:-}"

echo "============================================================"
echo "Project root: ${PROJECT_ROOT}"
echo "Postproc dir: ${POSTPROC_DIR}"
echo "Recipe: ${RECIPE}"
echo "Start time: $(date)"
echo "============================================================"

echo "[1/4] Checking configuration files..."
python scripts/run_postproc.py --check-configs \
  2>&1 | tee "${LOG_DIR}/matrix_2016_check_configs.log"

echo "[2/4] Dry-run..."
python scripts/run_postproc.py \
  --recipe "${RECIPE}" \
  --dry-run \
  2>&1 | tee "${LOG_DIR}/matrix_2016_dry_run.log"

echo "[3/4] Running post-processing figures..."
python scripts/run_postproc.py \
  --recipe "${RECIPE}" \
  --make-figures \
  2>&1 | tee "${LOG_DIR}/matrix_2016_make_figures.log"

echo "[4/4] Optional PDF generation..."
python scripts/run_postproc.py \
  --recipe "${RECIPE}" \
  --make-pdf \
  2>&1 | tee "${LOG_DIR}/matrix_2016_make_pdf.log"

echo "============================================================"
echo "Finished at: $(date)"
echo "Outputs:"
echo "  figures: outputs/matrix_2016/figures/smap_cdf_sensitivity/"
echo "  metrics: outputs/matrix_2016/metrics/smap_cdf_sensitivity/"
echo "  tables : outputs/matrix_2016/tables/smap_cdf_sensitivity/"
echo "  pdf    : outputs/matrix_2016/pdf/smap_cdf_sensitivity_2016.pdf"
echo "============================================================"
