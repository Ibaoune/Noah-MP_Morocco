#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=dl_modis
#SBATCH --output=data/logs/download/slurm_modis_%j.log
#SBATCH --error=data/logs/download/slurm_modis_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=1
set -x

cd $SLURM_SUBMIT_DIR

# Load python environment if needed (conda base)
source arch/arch_toubkal.env

echo "============================================="
echo " MODIS LAI Download Job (3-day window)"
echo "============================================="

# Define NASA credentials via environment variables to bypass interactive prompts
export EARTHDATA_USERNAME="el.aabaribaoune@gmail.com"
export EARTHDATA_PASSWORD="mohkaj111@ZO"

# Run the python download script
python scripts/download/download_modis_mcd15a2h.py --start_date 2020-02-01 --end_date 2020-02-04

echo "============================================="
echo " DONE "
echo "============================================="
