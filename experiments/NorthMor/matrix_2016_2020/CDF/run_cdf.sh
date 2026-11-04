#!/bin/bash
#SBATCH --job-name=cdf_gen
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=32G
#SBATCH --time=12:00:00
#SBATCH --partition=compute

source ../../../../arch/arch_toubkal.env

BASE_DIR="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020"

# Create consolidated directories for LDT to read from
echo "Consolidating OPL outputs into symlinks for LDT..."
mkdir -p ${BASE_DIR}/CDF/combined_OPL_irr/SURFACEMODEL
mkdir -p ${BASE_DIR}/CDF/combined_OPL_noirr/SURFACEMODEL

for year in {2016..2020}; do
    for month in $(seq -w 01 12); do
        if [ -d "${BASE_DIR}/OPL_irr_2016_2020/output/${year}-${month}/SURFACEMODEL/${year}${month}" ]; then
            ln -s ${BASE_DIR}/OPL_irr_2016_2020/output/${year}-${month}/SURFACEMODEL/${year}${month} ${BASE_DIR}/CDF/combined_OPL_irr/SURFACEMODEL/${year}${month}
        fi
        if [ -d "${BASE_DIR}/OPL_noirr_2016_2020/output/${year}-${month}/SURFACEMODEL/${year}${month}" ]; then
            ln -s ${BASE_DIR}/OPL_noirr_2016_2020/output/${year}-${month}/SURFACEMODEL/${year}${month} ${BASE_DIR}/CDF/combined_OPL_noirr/SURFACEMODEL/${year}${month}
        fi
    done
done

echo "Starting LDT CDF Generation for IRR..."
time ./../../../../src/lisf/ldt/LDT  ldt.config.cdf.irr

echo "Starting LDT CDF Generation for NO-IRR..."
time ./../../../../src/lisf/ldt/LDT  ldt.config.cdf.noirr

echo "Done."
