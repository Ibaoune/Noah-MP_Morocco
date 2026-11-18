#!/bin/bash
#SBATCH --job-name=hm3_sp_opl
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --output=experiments/NorthMor/routing/logs/slurm_hymap3_sp_opl_%j.out
#SBATCH --error=experiments/NorthMor/routing/logs/slurm_hymap3_sp_opl_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="experiments/NorthMor/routing/configs/lis_hymap3_opl_spinup_2016.config"
LOG_DIR="experiments/NorthMor/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/HYMAP3_OPL_spinup_2016"
mkdir -p "${LOG_DIR}" "${OUT_DIR}"

echo "=== Lancement HYMAP3 OPL Spin-up 2016 (linres=0) ==="
echo "Date debut : $(date)"
echo "Config : ${CONFIG}"
echo "Nodes : ${SLURM_NNODES}, Tasks : ${SLURM_NTASKS}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin : $(date)"
echo "Code retour : $?"
echo "=== Fin du run HYMAP3 OPL Spin-up 2016 ==="
