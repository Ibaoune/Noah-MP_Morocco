#!/bin/bash
#SBATCH --job-name=dl_scalability_val
#SBATCH --output=data/logs/download/dl_scalability_%j.out
#SBATCH --error=data/logs/download/dl_scalability_%j.err
#SBATCH --time=02:00:00
#SBATCH --partition=compute
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=4

# -----------------------------------------------------------------------------
# Script to download Validation and Observation data for the Scalability Test
# Dates: 2020-02-01 to 2020-02-04
# -----------------------------------------------------------------------------

echo "=========================================================="
echo "Starting targeted download for Scalability Test (3 days)"
echo "Dates: 2020-02-01 to 2020-02-04"
echo "=========================================================="

START_DATE="2020-02-01"
END_DATE="2020-02-04"

# 1. ASCAT Soil Moisture (Validation)
echo "----------------------------------------------------------"
echo "Downloading ASCAT Soil Moisture..."
python scripts/download/download_ascat.py --start_date $START_DATE --end_date $END_DATE
echo "ASCAT download complete."

# 2. Copernicus LAI (Validation)
echo "----------------------------------------------------------"
echo "Downloading Copernicus LAI..."
python scripts/download/download_copernicus_lai.py --start_date $START_DATE --end_date $END_DATE
echo "Copernicus LAI download complete."

# 3. SMAP SPL3SMP.009 (Observation)
echo "----------------------------------------------------------"
echo "Downloading SMAP SPL3SMP..."
python scripts/download/download_smap.py --start_date $START_DATE --end_date $END_DATE
echo "SMAP download complete."

# 4. MODIS LAI / MCD15A2H (Observation)
echo "----------------------------------------------------------"
echo "Downloading MODIS MCD15A2H..."
python scripts/download/download_modis_mcd15a2h.py --start_date $START_DATE --end_date $END_DATE
echo "MODIS LAI download complete."

echo "=========================================================="
echo "All targeted downloads finished successfully."
echo "=========================================================="
