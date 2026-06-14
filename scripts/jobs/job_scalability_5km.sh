#!/bin/bash
# Author: M. EL Aabaribaoune (@um6p)
#
# Job: 5km Scalability Test
#
######################
#SBATCH --job-name=scalability_5km
#SBATCH --output=logs/slurm/slurm_scalability_5km_%j.log
#SBATCH --error=logs/slurm/slurm_scalability_5km_%j.log
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --time=04:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
set -x

cd $SLURM_SUBMIT_DIR

# Load required modules
source arch/arch_toubkal.env

echo "=================================================="
echo "Starting 5km Scalability Tests"
echo "=================================================="

# Ensure LDT is run to generate the 5km parameter file
if [ ! -f "data/lis_input/lis_input.d01_5km.nc" ]; then
    echo "Running LDT first to generate parameter file..."
    ./src/lisf/ldt/make/LDT configs/ldt.config.sanity > logs/ldt_scalability_run.log 2>&1
fi

cores=(1 2 4 8 16 32)
px=(1 1 2 2 4 4)
py=(1 2 2 4 4 8)

for i in "${!cores[@]}"; do
    n=${cores[$i]}
    x=${px[$i]}
    y=${py[$i]}
    
    echo "----------------------------------------"
    echo "Running with $n cores (x=$x, y=$y)..."
    echo "----------------------------------------"
    
    # Modify the config file in place
    sed -i "s/^Number of processors along x:.*/Number of processors along x:           $x/g" configs/lis.config.scalability_5km
    sed -i "s/^Number of processors along y:.*/Number of processors along y:           $y/g" configs/lis.config.scalability_5km
    
    # Run and time it
    start_time=$(date +%s)
    mpirun -n $n ./src/lisf/lis/LIS -f configs/lis.config.scalability_5km > logs/lis_scalability_5km_${n}cores.log 2>&1
    end_time=$(date +%s)
    
    elapsed=$(( end_time - start_time ))
    echo "Time taken for $n cores: $elapsed seconds."
    echo "$n,$elapsed" >> logs/scalability_5km_results.csv
done

echo "Scalability tests completed. Results saved to logs/scalability_5km_results.csv."
