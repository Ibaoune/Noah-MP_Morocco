#!/bin/bash
#SBATCH --job-name=hm2_sp_lr0
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=experiments/NorthMor/routing/logs/slurm_hymap2_sp_lr0_da_nocdf_%j.out
#SBATCH --error=experiments/NorthMor/routing/logs/slurm_hymap2_sp_lr0_da_nocdf_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="experiments/NorthMor/routing/configs/lis_hymap2_da_nocdf_spinup_linres0.config"
LOG_DIR="experiments/NorthMor/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/DA_nocdf_linres0_spinup_2016"
mkdir -p "${LOG_DIR}" "${OUT_DIR}"

echo "=== Lancement HYMAP2 DA_nocdf Spin-up 2016 (linres=0) ==="
echo "Date debut : $(date)"
echo "Config : ${CONFIG}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin : $(date)"
echo "Code retour : $?"
echo "=== Fin du run HYMAP2 DA_nocdf Spin-up 2016 (linres=0) ==="
