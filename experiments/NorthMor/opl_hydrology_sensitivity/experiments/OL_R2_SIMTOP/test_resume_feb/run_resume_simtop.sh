#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=res_simtop
#SBATCH --output=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_resume_feb/logs/resume_simtop_%j.log
#SBATCH --error=/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_resume_feb/logs/resume_simtop_%j.err
#SBATCH --time=00:30:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco
source arch/arch_toubkal.env

echo "============================================="
echo " Resumption Test from 2017-02-01 Restart"
echo " Experiment: OL_R2_SIMTOP"
echo " Start: 2017-02-01 | End: 2017-02-03"
echo " Restart File: /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/restarts/LIS_RST_NOAHMP401_201702010000.d01.nc"
echo " Config: /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_resume_feb/lis_resume_simtop.config"
echo "============================================="

time mpirun -n 32 ./src/lisf/lis/LIS -f /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/opl_hydrology_sensitivity/experiments/OL_R2_SIMTOP/test_resume_feb/lis_resume_simtop.config

echo "============================================="
echo " Resumption test succeeded for OL_R2_SIMTOP!"
echo "============================================="
