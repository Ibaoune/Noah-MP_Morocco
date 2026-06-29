#!/bin/bash

# GLDAS
cd scripts/download/validation/GLDAS
sbatch submit_download_gldas.sh
cd ../../../../

# FLUXSAT
cd scripts/download/validation/FLUXSAT
sbatch submit_download_fluxsat.sh
cd ../../../../

# WaPOR
cd scripts/download/validation/WaPOR
sbatch submit_download_wapor.sh
cd ../../../../

# Helper to create and submit slurm jobs for raw python scripts
function submit_py_script() {
    local DIR=$1
    local SCRIPT=$2
    local JOBNAME=$3
    
    cd scripts/download/validation/${DIR}
    
    cat << SLURM > submit_${JOBNAME}.sh
#!/bin/bash
#SBATCH --job-name=${JOBNAME}
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --mem=4G
#SBATCH --time=04:00:00
#SBATCH --partition=compute
#SBATCH --output=logs/${JOBNAME}_%j.out
#SBATCH --error=logs/${JOBNAME}_%j.err

source /srv/software/easybuild/software/Anaconda3/2020.11/etc/profile.d/conda.sh
conda activate postproc_env

echo "Starting ${JOBNAME} download..."
python3 ${SCRIPT}
echo "Finished."
SLURM

    sbatch submit_${JOBNAME}.sh
    cd ../../../../
}

submit_py_script "GLEAM" "download_gleam.py" "gleam"
submit_py_script "ESA_CCI" "download_esa_cci_sm.py" "esacci"
submit_py_script "Copernicus_LAI" "download_copernicus_lai.py" "cop_lai"
submit_py_script "ASCAT" "download_ascat.py" "ascat"

echo "All jobs submitted!"
