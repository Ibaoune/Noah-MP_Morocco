#!/bin/bash

# Author: M. El Aabaribaoune (@um6p)

#SBATCH --job-name=lis_spinup
#SBATCH --output=slurm-%j.out
#SBATCH --error=slurm-%j.err
#SBATCH --nodes=4
#SBATCH --ntasks=128
#SBATCH --time=24:00:00
#SBATCH --partition=compute

source arch/arch_toubkal.env

echo "Starting Noah-MP Open-Loop Spin-up (2015-2020)..."
time mpirun -n $SLURM_NTASKS ./src/lisf/lis/LIS -f configs/lis.config.spinup_sebou
echo "Spin-up finished."
