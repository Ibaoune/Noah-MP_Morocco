#!/bin/bash
# ============================================================
# Author  : M. El Aabaribaoune (@um6p)
# Job     : Download MERRA-2 geopotential constants file
#           (MERRA2_101.const_2d_asm_Nx.00000000.nc4)
# Purpose : Required by LDT to compute ELEV_MERRA2 for
#           lapse-rate topographic correction in LIS.
# Output  : data/forcing/MERRA2/M2C0NXASM/
# ============================================================
#SBATCH --job-name=dl_merra2_const
#SBATCH --output=logs/download/dl_merra2_const_%j.out
#SBATCH --error=logs/download/dl_merra2_const_%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --partition=compute
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU

set -euo pipefail
cd "$SLURM_SUBMIT_DIR"

PYTHON=/home/mohammad.elaabaribao/.conda/envs/env_py3.10.13/bin/python

echo "=================================================="
echo "  MERRA-2 Constants File Download"
echo "  Job ID : ${SLURM_JOB_ID}"
echo "  Node   : $(hostname)"
echo "  Start  : $(date)"
echo "=================================================="

mkdir -p logs/download
mkdir -p data/forcing/MERRA2/M2C0NXASM

${PYTHON} data/scripts/download/download_merra2_const.py

echo ""
echo "=================================================="
echo "  Download finished : $(date)"
echo "=================================================="

# Verify the file exists and print its size
FILE="data/forcing/MERRA2/M2C0NXASM/MERRA2_101.const_2d_asm_Nx.00000000.nc4"
if [ -f "${FILE}" ]; then
    SIZE=$(du -sh "${FILE}" | cut -f1)
    echo "  File : ${FILE}"
    echo "  Size : ${SIZE}"
    echo ""
    echo "  Next step: add this line to your LDT config:"
    echo "    MERRA2 geopotential terrain height file: ./${FILE}"
else
    echo "[ERROR] File not found after download: ${FILE}"
    exit 1
fi
