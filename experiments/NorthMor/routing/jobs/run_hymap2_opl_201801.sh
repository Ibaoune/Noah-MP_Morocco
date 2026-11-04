#!/bin/bash
#SBATCH --job-name=hymap2_opl_201801
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/logs/slurm_run_opl_201801_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/logs/slurm_run_opl_201801_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/

source arch/arch_toubkal.env
export GFORTRAN_CONVERT_UNIT='big_endian'

mkdir -p experiments/NorthMor/routing/output/OPL_201801
mkdir -p experiments/NorthMor/routing/logs

echo "=== HYMAP2 OFFLINE ROUTING - JANVIER 2018 OPL ==="
echo "Date debut : $(date)"
echo "Nombre de taches MPI : $SLURM_NTASKS"
echo "Hote d'execution : $(hostname)"

START_TIME=$(date +%s)

/usr/bin/time -v mpirun -n 16 ./src/lisf/lis/LIS -f experiments/NorthMor/routing/configs/lis_hymap2_opl_201801.config

END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))

echo "Date fin : $(date)"
echo "Temps ecoule : ${ELAPSED} secondes"
