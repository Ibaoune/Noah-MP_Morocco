#!/bin/bash
#SBATCH --job-name=postproc_eval
#SBATCH --output=scripts/postproc/logs/eval_%j.out
#SBATCH --error=scripts/postproc/logs/eval_%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4
#SBATCH --time=01:00:00
#SBATCH --partition=compute
#SBATCH --mem=8G

echo "Starting Post-Processing and Evaluation..."
date

# Create logs directory if it doesn't exist
mkdir -p scripts/postproc/logs
mkdir -p scripts/postproc/figures

# Set PYTHONPATH to the root directory where the scripts reside
export PYTHONPATH=scripts/postproc/scripts

echo "1. Running Water Budget Evaluation..."
python3 scripts/postproc/scripts/eval_water_budget.py

echo "2. Running Direct DA vs OPL Comparison..."
python3 scripts/postproc/scripts/compare_opl_da.py

echo "3. Running DA Increment/Innovation Statistics..."
python3 scripts/postproc/scripts/eval_da_stats.py

echo "4. Running Spatial Validation vs Independent Datasets..."
python3 scripts/postproc/scripts/validate_spatial.py

echo "All post-processing tasks completed!"
date
