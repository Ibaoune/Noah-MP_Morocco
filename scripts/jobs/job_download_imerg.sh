#!/usr/bin/env bash
# =============================================================================
# Author: M. El Aabaribaoune (@UM6P)
# Date:   2026-06-07
# =============================================================================
#SBATCH --job-name=dl_imerg
#SBATCH --output=data/logs/download/dl_imerg_%j.out
#SBATCH --error=data/logs/download/dl_imerg_%j.err
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=8G
#SBATCH --partition=compute

source ~/.bashrc
/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python data/scripts/download/download_imerg.py
