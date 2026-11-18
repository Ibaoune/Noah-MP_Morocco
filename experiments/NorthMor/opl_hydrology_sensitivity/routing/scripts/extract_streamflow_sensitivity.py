#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Extract streamflow from local HyMAP-2 outputs for sensitivity experiments.
Uses the exact date reconstruction (sim_dt = file_dt - 1 day) and 0-based indices from
experiments/NorthMor/routing/stations/hymap_stations_pairing.csv (Read-Only).
"""
import os, sys, glob, re, argparse, datetime
import netCDF4 as nc
import pandas as pd
import numpy as np

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"
routing_dir = f"{base_proj}/routing"
pairing_file = f"{repo_root}/experiments/NorthMor/routing/stations/hymap_stations_pairing.csv"

if not os.path.exists(pairing_file):
    print(f"Error: Pairing file {pairing_file} not found!")
    sys.exit(1)

df_stations = pd.read_csv(pairing_file)

def extract_for_experiment(exp_id, input_dir=None, output_csv=None):
    if input_dir is None:
        cand_dirs = [
            f"{routing_dir}/outputs/{exp_id}/ROUTING",
            f"{routing_dir}/outputs/test_jan2017/{exp_id}/ROUTING"
        ]
        out_dir = next((d for d in cand_dirs if os.path.exists(d)), cand_dirs[0])
    else:
        out_dir = input_dir

    if output_csv is None:
        csv_out = f"{routing_dir}/outputs/{exp_id}/streamflow_daily_stations.csv"
    else:
        csv_out = output_csv
    os.makedirs(os.path.dirname(csv_out), exist_ok=True)

    hist_files = sorted(glob.glob(f"{out_dir}/**/LIS_HIST_*.nc", recursive=True))
    if not hist_files:
        hist_files = sorted(glob.glob(f"{out_dir}/**/LIS_HIST_*.d01.nc", recursive=True))

    if not hist_files:
        print(f"[{exp_id}] No routing history NetCDF files found in {out_dir}")
        return

    print(f"[{exp_id}] Extracting streamflow from {len(hist_files)} files in {out_dir}...")
    records = []

    for f in hist_files:
        try:
            with nc.Dataset(f, "r") as ds:
                t_units = ds["time"].units
                t_val = ds["time"][0]
                base_str = t_units.replace("minutes since ", "")
                base_dt = datetime.datetime.strptime(base_str, "%Y-%m-%d %H:%M:%S")
                file_dt = base_dt + datetime.timedelta(minutes=float(t_val))
                sim_dt = file_dt - datetime.timedelta(days=1)
                dt_str = sim_dt.strftime("%Y-%m-%d")

                flow = np.nan_to_num(ds["Streamflow_tavg"][:].filled(0.0))
                if flow.ndim == 3:
                    flow = flow[0]

                row_dict = {"date": dt_str}
                for _, row in df_stations.iterrows():
                    sid = row["station_id"]
                    r, c = int(row["row_hymap"]), int(row["col_hymap"])
                    row_dict[sid] = float(flow[r, c])
                records.append(row_dict)
        except Exception as e:
            print(f"Error reading {f}: {e}")

    df_out = pd.DataFrame(records).sort_values("date").reset_index(drop=True)
    df_out.to_csv(csv_out, index=False)
    print(f"[{exp_id}] Successfully saved {len(df_out)} days of streamflow to {csv_out}")
    print(df_out[["date", "b_l_chafia", "b_s_jabeur"]].head())

def main():
    parser = argparse.ArgumentParser(description="Extract station streamflow from HyMAP-2 NetCDFs.")
    parser.add_argument("--experiment", choices=["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS", "all"], default="all")
    parser.add_argument("--input-dir", default=None, help="Custom input directory")
    parser.add_argument("--output-csv", default=None, help="Custom output CSV")
    args = parser.parse_args()

    exps = ["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS"] if args.experiment == "all" else [args.experiment]
    for exp in exps:
        extract_for_experiment(exp, input_dir=args.input_dir, output_csv=args.output_csv)

if __name__ == "__main__":
    main()
