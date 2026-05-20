#!/bin/bash
#SBATCH --job-name=ldt_run
#SBATCH --output=slurm_ldt_%j.out
#SBATCH --error=slurm_ldt_%j.err
#SBATCH --nodes=1
#SBATCH --time=02:00:00
#SBATCH --mem=32G
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
echo "Starting LDT Parameter Generation Job"
echo "=================================================="

echo "Waiting for data downloads to complete (if any are still running)..."
while pgrep -u $USER -f "download_parameters.py" > /dev/null || pgrep -u $USER -f "download_merra2.py" > /dev/null; do
    echo "Downloads still running... sleeping for 60s"
    sleep 60
done

echo "----------------------------------------"
echo "Running LDT..."
echo "----------------------------------------"
./lisf/ldt/make/LDT ldt.config > ldt_run.log 2>&1

if [ $? -ne 0 ]; then
    echo "Error running LDT! Check ldt_run.log"
    exit 1
fi
echo "LDT completed successfully. Generated lis_input.d01.nc."
