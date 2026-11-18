#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"
routing_dir = f"{base_proj}/routing"

with open(f"{repo_root}/experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_linres0.config", "r") as f:
    base_cfg = f.read()

experiments = [
    ("OL_R1_SIMGM", "simgm"),
    ("OL_R2_SIMTOP", "simtop"),
    ("OL_R3_SCHAAKE96", "schaake96"),
    ("OL_R4_BATS", "bats")
]

os.makedirs(f"{routing_dir}/configs/test_jan2017", exist_ok=True)
os.makedirs(f"{routing_dir}/runs/logs", exist_ok=True)

for exp_id, short_name in experiments:
    os.makedirs(f"{routing_dir}/outputs/test_jan2017/{exp_id}", exist_ok=True)

    lines = base_cfg.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("Starting year:"):
            new_lines.append("Starting year:                          2017")
        elif line.startswith("Starting month:"):
            new_lines.append("Starting month:                         01")
        elif line.startswith("Starting day:"):
            new_lines.append("Starting day:                           01")
        elif line.startswith("Ending year:"):
            new_lines.append("Ending year:                            2017")
        elif line.startswith("Ending month:"):
            new_lines.append("Ending month:                           02")
        elif line.startswith("Ending day:"):
            new_lines.append("Ending day:                             01")
        elif line.startswith("Output directory:"):
            new_lines.append(f"Output directory:                       \"{routing_dir}/outputs/test_jan2017/{exp_id}\"")
        elif line.startswith("Diagnostic output file:"):
            new_lines.append(f"Diagnostic output file:                 \"{routing_dir}/runs/logs/lislog_test_jan2017_{short_name}\"")
        elif line.startswith("LIS runoff output directory:"):
            new_lines.append(f"LIS runoff output directory:            \"{routing_dir}/runs/remap_180x120/{exp_id}\"")
        elif line.startswith("HYMAP2 routing model start mode:"):
            new_lines.append("HYMAP2 routing model start mode:         coldstart")
        elif line.startswith("HYMAP2 routing model restart file:"):
            new_lines.append("HYMAP2 routing model restart file:       none")
        elif line.startswith("HYMAP2 routing model linear reservoir flag:"):
            new_lines.append("HYMAP2 routing model linear reservoir flag: 0")
        else:
            new_lines.append(line)

    cfg_file = f"{routing_dir}/configs/test_jan2017/lis_hymap2_{short_name}_jan2017.config"
    with open(cfg_file, "w") as f:
        f.write("\n".join(new_lines) + "\n")
    print(f"Created Jan 2017 test routing config: {cfg_file}")

