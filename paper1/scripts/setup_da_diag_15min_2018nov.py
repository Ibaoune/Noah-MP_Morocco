import os

base_dir = '/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco'
run_dir = os.path.join(base_dir, 'experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_15min_2018Nov')
src_cfg = os.path.join(base_dir, 'experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/config/lis_DA_nocdf_diag_2018ND.config')
dst_cfg = os.path.join(run_dir, 'config/lis_DA_nocdf_diag_15min_2018Nov.config')

with open(src_cfg, 'r') as f:
    cfg = f.read()

cfg = cfg.replace('Surface model output interval:          1da',
                  'Surface model output interval:          15mn')
cfg = cfg.replace('Ending day:                             01',
                  'Ending day:                             06')
cfg = cfg.replace('Ending month:                           01',
                  'Ending month:                           11')
cfg = cfg.replace('Ending year:                            2019',
                  'Ending year:                            2018')
cfg = cfg.replace('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/output',
                  f'{run_dir}/output')
cfg = cfg.replace('/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_diag/DA_nocdf_diag_2018ND/logs/lislog_DA_nocdf_diag_2018ND',
                  f'{run_dir}/logs/lislog_DA_nocdf_diag_15min_2018Nov')
cfg = cfg.replace("Model output attributes file:           './shared/MODEL_OUTPUT_LIST.TBL'",
                  f"Model output attributes file:           '{run_dir}/config/MODEL_OUTPUT_LIST.TBL'")

with open(dst_cfg, 'w') as f:
    f.write(cfg)

print(f'[OK] Wrote {dst_cfg}')

dst_job = os.path.join(run_dir, 'jobs/run_DA_nocdf_diag_15min_2018Nov.sh')
job_content = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=DA_15m_18N
#SBATCH --output={run_dir}/logs/slurm_DA_15m_18N_%j.log
#SBATCH --error={run_dir}/logs/slurm_DA_15m_18N_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=32

set -e
cd {base_dir}

source arch/arch_toubkal.env

CONFIG="{dst_cfg}"
BIN="./src/lisf/lis/make/LIS"

echo "=========================================================="
echo " LIS NorthMor - DA_nocdf_diag_15min_2018Nov (15-min inst output)"
echo " Start: 2018-11-01 | End: 2018-11-06 (5 days)"
echo " Config: $CONFIG"
echo " Binary: $BIN"
echo "=========================================================="

time mpirun -n 32 "$BIN" -f "$CONFIG"

echo "=========================================================="
echo " Simulation DA_nocdf_diag_15min_2018Nov terminee avec succes "
echo "=========================================================="
"""

with open(dst_job, 'w') as f:
    f.write(job_content)
os.chmod(dst_job, 0o775)
print(f'[OK] Wrote and chmoded {dst_job}')
