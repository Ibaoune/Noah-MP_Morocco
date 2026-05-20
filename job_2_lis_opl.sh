#!/bin/bash
#SBATCH --job-name=lis_opl
#SBATCH --output=slurm_opl_%j.out
#SBATCH --error=slurm_opl_%j.err
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --mem=64G
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU

cd $SLURM_SUBMIT_DIR

# Load required modules
module purge
module load foss/2024a \
            netCDF-Fortran/4.6.1-gompi-2024a \
            netCDF/4.9.2-gompi-2024a \
            ESMF/8.7.0-foss-2024a \
            JasPer/4.2.4-GCCcore-13.3.0 \
            ecCodes/2.38.3-gompi-2024a \
            HDF5/1.14.5-gompi-2024a \
            CMake/3.29.3-GCCcore-13.3.0

echo "=================================================="
echo "Starting LIS Open-Loop Simulation Job"
echo "=================================================="

if [ ! -f "lis_input.d01.nc" ]; then
    echo "ERROR: lis_input.d01.nc not found!"
    echo "Please ensure that job_1_ldt.sh has successfully completed before running this job."
    exit 1
fi

echo "----------------------------------------"
echo "Running Open-Loop Simulation..."
echo "----------------------------------------"
./lisf/lis/LIS -f lis.config.opl > lis_opl_run.log 2>&1
if [ $? -ne 0 ]; then
    echo "Error running Open-Loop! Check lis_opl_run.log"
    exit 1
fi
echo "Open-Loop simulation completed successfully."
