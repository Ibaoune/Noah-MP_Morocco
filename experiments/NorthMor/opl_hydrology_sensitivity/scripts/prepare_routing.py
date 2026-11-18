#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import os

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"
routing_dir = f"{base_proj}/routing"

# Read base routing config template from experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_linres0.config
with open(f"{repo_root}/experiments/NorthMor/routing/configs/lis_hymap2_opl_2016_2020_linres0.config", "r") as f:
    base_cfg = f.read()

experiments = [
    ("OL_R1_SIMGM", "simgm"),
    ("OL_R2_SIMTOP", "simtop"),
    ("OL_R3_SCHAAKE96", "schaake96"),
    ("OL_R4_BATS", "bats")
]

for exp_id, short_name in experiments:
    os.makedirs(f"{routing_dir}/outputs/{exp_id}", exist_ok=True)
    os.makedirs(f"{routing_dir}/runs/remap_180x120/{exp_id}/SURFACEMODEL", exist_ok=True)
    os.makedirs(f"{routing_dir}/runs/logs", exist_ok=True)

    # 1. HyMAP2 Config (2017-2018, linres=0, coldstart / spinup)
    lines = base_cfg.splitlines()
    new_lines = []
    for line in lines:
        if line.startswith("Starting year:"):
            new_lines.append("Starting year:                          2017")
        elif line.startswith("Ending year:"):
            new_lines.append("Ending year:                            2019")
        elif line.startswith("Output directory:"):
            new_lines.append(f"Output directory:                       \"{routing_dir}/outputs/{exp_id}\"")
        elif line.startswith("Diagnostic output file:"):
            new_lines.append(f"Diagnostic output file:                 \"{routing_dir}/runs/logs/lislog_hymap2_{short_name}\"")
        elif line.startswith("LIS runoff output directory:"):
            new_lines.append(f"LIS runoff output directory:            \"{routing_dir}/runs/remap_180x120/{exp_id}/SURFACEMODEL\"")
        elif line.startswith("HYMAP2 routing model start mode:"):
            new_lines.append("HYMAP2 routing model start mode:         coldstart")
        elif line.startswith("HYMAP2 routing model restart file:"):
            new_lines.append("HYMAP2 routing model restart file:       none")
        elif line.startswith("HYMAP2 routing model linear reservoir flag:"):
            new_lines.append("HYMAP2 routing model linear reservoir flag: 0")
        else:
            new_lines.append(line)

    cfg_content = "\n".join(new_lines) + "\n"
    cfg_file = f"{routing_dir}/configs/lis_hymap2_{short_name}_2017_2018.config"
    with open(cfg_file, "w") as f:
        f.write(cfg_content)
    print(f"Generated routing config: {cfg_file}")

# 2. Write remap script: remap_runoff_sensitivity.py
remap_script = f"""#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
\"\"\"
Remap Noah-MP Qs/Qsb (181x121) to HyMAP-2 (180x120) for sensitivity experiments.
\"\"\"
import os, glob, re, argparse
import multiprocessing as mp
import netCDF4 as nc
import numpy as np

repo_root = "{repo_root}"
base_proj = "{base_proj}"
routing_dir = "{routing_dir}"

ldt_path = f"{repo_root}/experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
ds_ldt = nc.Dataset(ldt_path)
tgt_lat = ds_ldt["lat"][:].astype(np.float32)
tgt_lon = ds_ldt["lon"][:].astype(np.float32)
ds_ldt.close()

def process_file_args(args):
    src_path, dst_base = args
    fname = os.path.basename(src_path)
    m = re.search(r"LIS_HIST_(\\d{{4}})(\\d{{2}})\\d{{6}}\\.d01\\.nc", fname)
    if not m:
        return
    ym = m.group(1) + m.group(2)
    dst_dir = os.path.join(dst_base, ym)
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, fname)

    if os.path.exists(dst_path) and os.path.getsize(dst_path) > 10000:
        return

    try:
        ds_src = nc.Dataset(src_path, "r")
        qs_src = ds_src["Qs_tavg"][:]
        qsb_src = ds_src["Qsb_tavg"][:]
        if qs_src.ndim == 3: qs_src = qs_src[0]
        if qsb_src.ndim == 3: qsb_src = qsb_src[0]
        time_val = ds_src["time"][:] if "time" in ds_src.variables else [0.0]
        time_units = getattr(ds_src["time"], "units", "minutes since 2017-01-01 00:00:00")
        ds_src.close()

        qs_clean = np.where((qs_src < 0) | np.isnan(qs_src), 0.0, qs_src).astype(np.float64)
        qsb_clean = np.where((qsb_src < 0) | np.isnan(qsb_src), 0.0, qsb_src).astype(np.float64)

        qs_tgt = 0.25 * (qs_clean[:-1, :-1] + qs_clean[:-1, 1:] + qs_clean[1:, :-1] + qs_clean[1:, 1:])
        qsb_tgt = 0.25 * (qsb_clean[:-1, :-1] + qsb_clean[:-1, 1:] + qsb_clean[1:, :-1] + qsb_clean[1:, 1:])

        tmp_path = dst_path + ".tmp"
        ds_dst = nc.Dataset(tmp_path, "w", format="NETCDF4_CLASSIC")
        ds_dst.createDimension("east_west", 180)
        ds_dst.createDimension("north_south", 120)
        ds_dst.createDimension("time", 1)

        v_lat = ds_dst.createVariable("lat", "f4", ("north_south", "east_west"))
        v_lat.units = "degrees_north"
        v_lat.long_name = "latitude"
        v_lat[:] = tgt_lat

        v_lon = ds_dst.createVariable("lon", "f4", ("north_south", "east_west"))
        v_lon.units = "degrees_east"
        v_lon.long_name = "longitude"
        v_lon[:] = tgt_lon

        v_time = ds_dst.createVariable("time", "f8", ("time",))
        v_time.units = time_units
        v_time[:] = time_val

        v_qs = ds_dst.createVariable("Qs_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qs.units = "kg m-2 s-1"
        v_qs.long_name = "surface runoff"
        v_qs[0, :, :] = qs_tgt.astype(np.float32)

        v_qsb = ds_dst.createVariable("Qsb_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qsb.units = "kg m-2 s-1"
        v_qsb.long_name = "subsurface runoff"
        v_qsb[0, :, :] = qsb_tgt.astype(np.float32)

        ds_dst.close()
        os.replace(tmp_path, dst_path)
    except Exception as e:
        print(f"Error processing {{src_path}}: {{e}}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS", "all"], default="all")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    exps = ["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS"] if args.experiment == "all" else [args.experiment]

    for exp in exps:
        src_pattern = f"{base_proj}/experiments/{{exp}}/output/*/SURFACEMODEL/*/LIS_HIST_*.nc"
        files = sorted(glob.glob(src_pattern))
        dst_base = f"{routing_dir}/runs/remap_180x120/{{exp}}/SURFACEMODEL"
        os.makedirs(dst_base, exist_ok=True)
        print(f"[{{exp}}] Found {{len(files)}} Noah-MP history files to remap to {{dst_base}}")
        if not files:
            continue
        tasks = [(f, dst_base) for f in files]
        with mp.Pool(processes=args.workers) as pool:
            pool.map(process_file_args, tasks)
        print(f"[{{exp}}] Finished remapping.")

if __name__ == "__main__":
    main()
"""
with open(f"{routing_dir}/scripts/remap_runoff_sensitivity.py", "w") as f:
    f.write(remap_script)
os.chmod(f"{routing_dir}/scripts/remap_runoff_sensitivity.py", 0o755)

# 3. Write HyMAP-2 runner SLURM script: run_routing_all.sh
run_script = f"""#!/bin/bash
# Author: M. El Aabaribaoune (@um6p)
#SBATCH --job-name=hymap2_sens
#SBATCH --output={routing_dir}/runs/logs/hymap2_sens_%j.log
#SBATCH --error={routing_dir}/runs/logs/hymap2_sens_%j.err
#SBATCH --time=02:00:00
#SBATCH --account=empowermed-ahl6xm8o7mg-DEFAULT-CPU
#SBATCH --nodes=1
#SBATCH --ntasks=16

set -e
cd {repo_root}
source arch/arch_toubkal.env
export OMP_NUM_THREADS=1

EXP_ID=${{1:-"OL_R1_SIMGM"}}

case "$EXP_ID" in
    OL_R1_SIMGM) CFG="{routing_dir}/configs/lis_hymap2_simgm_2017_2018.config" ;;
    OL_R2_SIMTOP) CFG="{routing_dir}/configs/lis_hymap2_simtop_2017_2018.config" ;;
    OL_R3_SCHAAKE96) CFG="{routing_dir}/configs/lis_hymap2_schaake96_2017_2018.config" ;;
    OL_R4_BATS) CFG="{routing_dir}/configs/lis_hymap2_bats_2017_2018.config" ;;
    *) echo "Unknown experiment: $EXP_ID"; exit 1 ;;
esac

echo "============================================="
echo " HyMAP-2 Routing: $EXP_ID (2017-2018, linres=0)"
echo " Config: $CFG"
echo "============================================="

time mpirun -np 16 ./src/lisf/lis/LIS -f "$CFG"

echo "Routing completed successfully for $EXP_ID"
"""
with open(f"{routing_dir}/scripts/run_routing_single.sh", "w") as f:
    f.write(run_script)
os.chmod(f"{routing_dir}/scripts/run_routing_single.sh", 0o755)

# 4. Streamflow extraction script: extract_streamflow_sensitivity.py
extract_script = f"""#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
\"\"\"
Extract streamflow from local HyMAP-2 outputs for sensitivity experiments.
Stations pairing table read from: experiments/NorthMor/routing/stations/hymap_stations_pairing.csv (Read-Only)
\"\"\"
import os, sys, glob, re, argparse
import netCDF4 as nc
import pandas as pd
import numpy as np

repo_root = "{repo_root}"
base_proj = "{base_proj}"
routing_dir = "{routing_dir}"

pairing_file = f"{repo_root}/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv"
if not os.path.exists(pairing_file):
    print(f"Error: Pairing file {{pairing_file}} not found!")
    sys.exit(1)

df_pairs = pd.read_csv(pairing_file)

def extract_for_experiment(exp_id):
    out_dir = f"{routing_dir}/outputs/{{exp_id}}/ROUTING"
    csv_out = f"{routing_dir}/outputs/{{exp_id}}/streamflow_daily_stations.csv"
    
    files = sorted(glob.glob(f"{{out_dir}}/*/LIS_HIST_*.nc"))
    if not files:
        print(f"[{{exp_id}}] No routing history files found in {{out_dir}}")
        return
        
    print(f"[{{exp_id}}] Extracting streamflow from {{len(files)}} files...")
    records = []
    
    for f in files:
        fname = os.path.basename(f)
        m = re.search(r"LIS_HIST_(\\d{{4}})(\\d{{2}})(\\d{{2}})\\d{{4}}\\.d01\\.nc", fname)
        if not m:
            continue
        date_str = f"{{m.group(1)}}-{{m.group(2)}}-{{m.group(3)}}"
        
        try:
            ds = nc.Dataset(f, "r")
            q = ds["Streamflow_tavg"][:]
            if q.ndim == 3: q = q[0]
            ds.close()
            
            row = {{"date": date_str}}
            for _, st in df_pairs.iterrows():
                sid = st["station_id"]
                # col and row in pairing table are 0-based or 1-based?
                # In hymap_stations_pairing.csv, let us check col_0based vs row_0based
                c = int(st["col_0based"]) if "col_0based" in st else int(st["col"])
                r = int(st["row_0based"]) if "row_0based" in st else int(st["row"])
                row[sid] = float(q[r, c])
            records.append(row)
        except Exception as e:
            print(f"Error reading {{f}}: {{e}}")
            
    df_res = pd.DataFrame(records)
    df_res.sort_values("date", inplace=True)
    df_res.to_csv(csv_out, index=False)
    print(f"[{{exp_id}}] Saved {{len(df_res)}} days of streamflow to {{csv_out}}")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", choices=["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS", "all"], default="all")
    args = parser.parse_args()
    
    exps = ["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS"] if args.experiment == "all" else [args.experiment]
    for exp in exps:
        extract_for_experiment(exp)

if __name__ == "__main__":
    main()
"""
with open(f"{routing_dir}/scripts/extract_streamflow_sensitivity.py", "w") as f:
    f.write(extract_script)
os.chmod(f"{routing_dir}/scripts/extract_streamflow_sensitivity.py", 0o755)

print("Routing setup completed successfully!")
