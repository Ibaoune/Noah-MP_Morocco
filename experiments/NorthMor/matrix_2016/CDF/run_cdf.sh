#!/bin/bash
#SBATCH --job-name=cdf_gen
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --time=12:00:00
#SBATCH --partition=compute

source ../../../arch/arch_toubkal.env

BASE_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016"

# Create consolidated directories for LDT to read from
echo "Consolidating OPL outputs into symlinks for LDT..."
mkdir -p ${BASE_DIR}/CDF/combined_OPL_irr/SURFACEMODEL
mkdir -p ${BASE_DIR}/CDF/combined_OPL_noirr/SURFACEMODEL

for month in $(seq -w 01 12); do
    if [ -d "${BASE_DIR}/OPL_irr/output/2016-${month}/SURFACEMODEL/2016${month}" ]; then
        ln -s ${BASE_DIR}/OPL_irr/output/2016-${month}/SURFACEMODEL/2016${month} ${BASE_DIR}/CDF/combined_OPL_irr/SURFACEMODEL/2016${month}
    fi
    if [ -d "${BASE_DIR}/OPL_noirr/output/2016-${month}/SURFACEMODEL/2016${month}" ]; then
        ln -s ${BASE_DIR}/OPL_noirr/output/2016-${month}/SURFACEMODEL/2016${month} ${BASE_DIR}/CDF/combined_OPL_noirr/SURFACEMODEL/2016${month}
    fi
done

echo "Starting LDT CDF Generation for IRR..."
time ./../../../src/lisf/ldt/LDT -f ldt.config.cdf.irr

echo "Starting LDT CDF Generation for NO-IRR..."
time ./../../../src/lisf/ldt/LDT -f ldt.config.cdf.noirr

echo "Done."
