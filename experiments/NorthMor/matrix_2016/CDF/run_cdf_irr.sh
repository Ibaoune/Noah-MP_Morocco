#!/bin/bash
#SBATCH --job-name=cdf_irr
#SBATCH --output=slurm_cdf_irr_%j.out
#SBATCH --error=slurm_cdf_irr_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --mem=32G

source ../../../../arch/arch_toubkal.env
cd /home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016/CDF
./../../../../src/lisf/ldt/LDT ldt.config.cdf.irr
