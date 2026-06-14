#!/bin/bash

# ==============================================================================
# Script: postproc_00.sh
# Purpose: Unified entry point for the entire Noah-MP 3-day post-processing suite.
# Loads the required conda environment and executes the main python orchestrator.
# ==============================================================================

echo "Starting Post-Processing and Evaluation..."
date

# Create necessary directories
SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/figures"

# Initialize conda and activate the required environment
source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh || source ~/miniconda3/etc/profile.d/conda.sh || source ~/.conda/etc/profile.d/conda.sh
conda activate postproc_env

# Navigate to the script directory to ensure relative paths work correctly
cd "$SCRIPT_DIR"

echo "Executing run_all_postproc.py..."
python3 run_all_postproc.py

echo "Post-processing pipeline completed!"
date
