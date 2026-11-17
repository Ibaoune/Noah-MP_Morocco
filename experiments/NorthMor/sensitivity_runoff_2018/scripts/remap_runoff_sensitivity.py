#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
"""
Remap Noah-MP Qs/Qsb (181x121) to HyMAP-2 (180x120) for sensitivity experiments.
Matches the exact conservative 4-point stencil and 2D netCDF output format of remap_runoff_opl.py.
"""
import os, glob, re, time, argparse
import multiprocessing as mp
import netCDF4 as nc
import numpy as np

repo_root = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
base_proj = f"{repo_root}/experiments/NorthMor/opl_hydrology_sensitivity"
routing_dir = f"{base_proj}/routing"
ldt_path = f"{repo_root}/experiments/NorthMor/routing/ldt_hymap/lis_input_corrigee.d01.nc"

ds_ldt = nc.Dataset(ldt_path)
tgt_lat = ds_ldt["lat"][:].astype(np.float32)
tgt_lon = ds_ldt["lon"][:].astype(np.float32)
ds_ldt.close()

def process_file_args(args):
    src_path, dst_base = args
    fname = os.path.basename(src_path)
    m = re.search(r"LIS_HIST_(\d{4})(\d{2})\d{6}\.d01\.nc", fname)
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

        # Clean invalid and negative values
        qs_clean = np.where((qs_src < 0) | np.isnan(qs_src), 0.0, qs_src).astype(np.float64)
        qsb_clean = np.where((qsb_src < 0) | np.isnan(qsb_src), 0.0, qsb_src).astype(np.float64)

        # Conservative 4-point stencil
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

        v_time = ds_dst.createVariable("time", "f4", ("time",))
        v_time.units = time_units
        v_time[:] = time_val

        # 2D variables (north_south, east_west) strictly matching remap_runoff_opl.py
        v_qs = ds_dst.createVariable("Qs_tavg", "f4", ("north_south", "east_west"), fill_value=-9999.0)
        v_qs.units = "kg m-2 s-1"
        v_qs.long_name = "surface runoff"
        v_qs.missing_value = np.float32(-9999.0)
        v_qs[:] = qs_tgt.astype(np.float32)

        v_qsb = ds_dst.createVariable("Qsb_tavg", "f4", ("north_south", "east_west"), fill_value=-9999.0)
        v_qsb.units = "kg m-2 s-1"
        v_qsb.long_name = "subsurface runoff amount"
        v_qsb.missing_value = np.float32(-9999.0)
        v_qsb[:] = qsb_tgt.astype(np.float32)

        # Global attributes
        ds_dst.title = "LIS land surface model output (conservative remap 180x120 for offline HYMAP2)"
        ds_dst.MAP_PROJECTION = "EQUIDISTANT CYLINDRICAL"
        ds_dst.SOUTH_WEST_CORNER_LAT = np.float32(30.025)
        ds_dst.SOUTH_WEST_CORNER_LON = np.float32(-9.975)
        ds_dst.DX = np.float32(0.05)
        ds_dst.DY = np.float32(0.05)
        ds_dst.missing_value = np.float32(-9999.0)
        ds_dst.close()
        os.replace(tmp_path, dst_path)
    except Exception as e:
        print(f"Error processing {src_path}: {e}")

def main():
    parser = argparse.ArgumentParser(description="Remap Noah-MP runoff to HyMAP-2 180x120 grid.")
    parser.add_argument("--experiment", choices=["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS", "all"], default="all")
    parser.add_argument("--include-test", action="store_true", help="Include test_short outputs for quick sanity routing tests")
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()

    exps = ["OL_R1_SIMGM", "OL_R2_SIMTOP", "OL_R3_SCHAAKE96", "OL_R4_BATS"] if args.experiment == "all" else [args.experiment]

    for exp in exps:
        patterns = [f"{base_proj}/experiments/{exp}/output/*/SURFACEMODEL/*/LIS_HIST_*.nc"]
        if args.include_test:
            patterns.append(f"{base_proj}/experiments/{exp}/test_short/output/SURFACEMODEL/*/LIS_HIST_*.nc")
        
        files = []
        for p in patterns:
            files.extend(glob.glob(p))
        files = sorted(list(set(files)))

        dst_base = f"{routing_dir}/runs/remap_180x120/{exp}/SURFACEMODEL"
        os.makedirs(dst_base, exist_ok=True)
        print(f"[{exp}] Found {len(files)} Noah-MP history files to remap to {dst_base}")
        if not files:
            continue
        tasks = [(f, dst_base) for f in files]
        with mp.Pool(processes=args.workers) as pool:
            pool.map(process_file_args, tasks)
        print(f"[{exp}] Finished remapping {len(files)} files.")

if __name__ == "__main__":
    main()
