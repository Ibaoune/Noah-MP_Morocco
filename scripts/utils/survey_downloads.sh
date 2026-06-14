#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

# scripts/survey_downloads.sh
# This script checks the status of the download jobs and prints a summary of the downloaded data.

echo "========================================="
echo "   SURVEYING DATA DOWNLOAD STATUS"
echo "========================================="

echo ""
echo "[1/2] Checking SLURM job queue for active download jobs..."
# Check jobs submitted by current user with names starting with dl_
squeue -u $USER -n dl_forcing,dl_obs,dl_valid

echo ""
echo "[2/2] Running data inventory check..."
cd $(dirname "$0")
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python check_data_inventory.py

echo ""
echo "Summary of completeness report:"
cat ../reports/data_completeness_2015_2020.md
echo "========================================="
