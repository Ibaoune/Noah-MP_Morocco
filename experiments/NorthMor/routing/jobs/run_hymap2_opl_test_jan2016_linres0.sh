#!/bin/bash
#SBATCH --job-name=hm2_test_jan16
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:15:00
#SBATCH --chdir=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
#SBATCH --output=experiments/NorthMor/routing/logs/slurm_hymap2_test_jan16_linres0_%j.out
#SBATCH --error=experiments/NorthMor/routing/logs/slurm_hymap2_test_jan16_linres0_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="experiments/NorthMor/routing/configs/lis_hymap2_opl_test_jan2016_linres0.config"
LOG_DIR="experiments/NorthMor/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/OPL_test_jan2016_linres0"
mkdir -p "${LOG_DIR}" "${OUT_DIR}"

echo "=== Lancement HYMAP2 OPL Test Janvier 2016 (linres=0, coldstart) ==="
echo "Date debut : $(date)"
echo "Config     : ${CONFIG}"
echo "Nodes      : ${SLURM_NNODES}, Tasks : ${SLURM_NTASKS}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin   : $(date)"
echo "Code retour: $?"
echo "=== Fin du run HYMAP2 OPL Test Janvier 2016 ==="
