#!/bin/bash
#SBATCH --job-name=hm2_ENS_OPL_20
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --time=00:30:00
#SBATCH --chdir=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
#SBATCH --output=paper1/runs/routing/logs/slurm_hymap2_ens_opl_2017_linres0_%j.out
#SBATCH --error=paper1/runs/routing/logs/slurm_hymap2_ens_opl_2017_linres0_%j.err

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco

source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

CONFIG="paper1/runs/routing/configs/lis_hymap2_ens_opl_2017_linres0.config"
LOG_DIR="paper1/runs/routing/logs"
OUT_DIR="experiments/NorthMor/routing/output/ENS_OPL_2017_linres0"
mkdir -p "${LOG_DIR}" "${OUT_DIR}"

echo "=== Lancement HYMAP2 ENS_OPL_2017 (2017, linres=0, restart DA_nocdf 2017-01-01) ==="
echo "Date debut : $(date)"
echo "Config     : ${CONFIG}"

/usr/bin/time -v mpirun -np 16 ./src/lisf/lis/LIS -f "${CONFIG}"

echo "Date fin   : $(date)"
echo "Code retour: $?"
echo "=== Fin du run HYMAP2 ENS_OPL_2017 (linres=0) ==="
