#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=hymap2_sens
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/hymap2_sens_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/runs/logs/hymap2_sens_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

EXP_ID=${1:-"OL_R1_SIMGM"}

case "$EXP_ID" in
    OL_R1_SIMGM) CFG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_simgm_2017_2018.config" ;;
    OL_R2_SIMTOP) CFG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_simtop_2017_2018.config" ;;
    OL_R3_SCHAAKE96) CFG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_schaake96_2017_2018.config" ;;
    OL_R4_BATS) CFG="/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/routing/configs/lis_hymap2_bats_2017_2018.config" ;;
    *) echo "Unknown experiment: $EXP_ID"; exit 1 ;;
esac

echo "============================================="
echo " HyMAP-2 Routing: $EXP_ID (2017-2018, linres=0)"
echo " Config: $CFG"
echo "============================================="

time mpirun -np 16 ./src/lisf/lis/LIS -f "$CFG"

echo "Routing completed successfully for $EXP_ID"
