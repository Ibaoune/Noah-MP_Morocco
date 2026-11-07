#!/bin/bash
#SBATCH --job-name=hm2_da_cdf_5y
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=01:15:00
#SBATCH --output=experiments/NorthMor/routing/logs/slurm_hymap2_da_cdf_5y_%j.out
#SBATCH --error=experiments/NorthMor/routing/logs/slurm_hymap2_da_cdf_5y_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="experiments/NorthMor/routing/configs/lis_hymap2_da_cdf_2016_2020.config"
LOG_DIR="experiments/NorthMor/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/DA_cdf_2016_2020"
mkdir -p "${LOG_DIR}" "${OUT_DIR}"

echo "=== Lancement HYMAP2 DA_cdf 2016-2020 (5 ans continu) ==="
echo "Date debut : $(date)"
echo "Config : ${CONFIG}"
echo "Nodes : ${SLURM_NNODES}, Tasks : ${SLURM_NTASKS}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin : $(date)"
echo "Code retour : $?"
echo "=== Fin du run HYMAP2 DA_cdf 2016-2020 ==="
