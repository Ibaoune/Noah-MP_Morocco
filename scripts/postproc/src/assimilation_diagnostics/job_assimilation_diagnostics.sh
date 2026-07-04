#!/bin/bash
#SBATCH --mem=32G
#SBATCH --time=01:00:00
set -eo pipefail

# Initialize conda for the script
source ~/.bashrc || true
conda activate postproc_env || true

# ======================================================
# Job: Assimilation diagnostics for SMAP DA
# Matrix: matrix_2016
# Experiment: DA_nocdf_noirr_2016
# Year: 2016
# ======================================================

# SLURM runs the job in the submission directory by default
# No need to cd if we submit from the correct directory

python main.py --config config_assimilation_diagnostics.yaml
