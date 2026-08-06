#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)

#SBATCH --job-name=hydro_manuscript
#SBATCH --output=logs/hydro_manuscript_%j.out
#SBATCH --error=logs/hydro_manuscript_%j.err
#SBATCH --time=03:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G

mkdir -p logs
source ~/.bashrc
conda activate postproc_env
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc

echo "=== Step 1: Compute DA_CDF climatologies (2016-2020) ==="
echo "Started at $(date)"

PYTHONPATH=. python -c "
import os, sys, yaml, tempfile
from pathlib import Path

# Set working directory so all relative paths inside the script resolve correctly
os.chdir('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/scripts/postproc')
sys.path.insert(0, '.')

from src.diagnostics.hydrology.seasonal_impact_maps import compute_seasonal_climatologies

cfg_path = 'configs/manuscripts/hydrology_seasonal_impact.yaml'
with open(cfg_path) as f:
    cfg = yaml.safe_load(f)

# Override to DA_CDF
cfg['experiments']['assimilation'] = 'DA_CDF'

with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, dir='configs/manuscripts') as tmp:
    yaml.dump(cfg, tmp)
    tmp_path = tmp.name

try:
    compute_seasonal_climatologies(tmp_path)
finally:
    os.unlink(tmp_path)
print('DA_CDF climatologies done.')
"

echo "=== Step 2: Generate all manuscript figures ==="
PYTHONPATH=. python -m src.diagnostics.hydrology.manuscript_plots

echo "=== Done at $(date) ==="
