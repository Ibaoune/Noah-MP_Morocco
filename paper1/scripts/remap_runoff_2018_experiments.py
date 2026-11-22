#!/usr/bin/env python3
"""
remap_runoff_2018_experiments.py
Remapping standardise et rigoureusement identique a la production (181x121 -> 180x120)
pour les 3 experiences de sensibilite 2018:
  - OL_DAIC_2018
  - ENS_OPL_2018
  - DA_nocdf_nowilt_2018

Formule identique a remap_runoff_opl.py et checks/03_remapping_ruissellement.md:
  qs_dst = 0.25 * (qs[:-1,:-1] + qs[:-1,1:] + qs[1:,:-1] + qs[1:,1:])
  qsb_dst = 0.25 * (qsb[:-1,:-1] + qsb[:-1,1:] + qsb[1:,:-1] + qsb[1:,1:])
"""

import os
import glob
import re
import time
import shutil
import multiprocessing as mp
import netCDF4 as nc
import numpy as np

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
LDT_PATH = os.path.join(BASE_DIR, "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc")

ds_ldt = nc.Dataset(LDT_PATH)
TGT_LAT = ds_ldt["lat"][:].astype(np.float32)
TGT_LON = ds_ldt["lon"][:].astype(np.float32)
ds_ldt.close()

def process_single_file(args):
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
        time_units = getattr(ds_src["time"], "units", "minutes since 2018-01-01 00:00:00")
        ds_src.close()

        qs_clean = np.where((qs_src < 0) | np.isnan(qs_src), 0.0, qs_src).astype(np.float64)
        qsb_clean = np.where((qsb_src < 0) | np.isnan(qsb_src), 0.0, qsb_src).astype(np.float64)

        qs_tgt = 0.25 * (qs_clean[:-1, :-1] + qs_clean[:-1, 1:] + qs_clean[1:, :-1] + qs_clean[1:, 1:])
        qsb_tgt = 0.25 * (qsb_clean[:-1, :-1] + qsb_clean[:-1, 1:] + qsb_clean[1:, :-1] + qsb_clean[1:, 1:])

        tmp_path = dst_path + ".tmp"
        ds_dst = nc.Dataset(tmp_path, "w", format="NETCDF4")
        ds_dst.createDimension("time", 1)
        ds_dst.createDimension("north_south", 120)
        ds_dst.createDimension("east_west", 180)

        v_time = ds_dst.createVariable("time", "f8", ("time",))
        v_time.units = time_units
        v_time[:] = time_val

        v_lat = ds_dst.createVariable("lat", "f4", ("north_south", "east_west"))
        v_lat.units = "degrees_north"
        v_lat[:] = TGT_LAT

        v_lon = ds_dst.createVariable("lon", "f4", ("north_south", "east_west"))
        v_lon.units = "degrees_east"
        v_lon[:] = TGT_LON

        v_qs = ds_dst.createVariable("Qs_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qs.units = "kg m-2 s-1"
        v_qs.standard_name = "surface_runoff_flux"
        v_qs.long_name = "surface runoff amount"
        v_qs.missing_value = np.float32(-9999.0)
        v_qs[0, :, :] = qs_tgt.astype(np.float32)

        v_qsb = ds_dst.createVariable("Qsb_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qsb.units = "kg m-2 s-1"
        v_qsb.standard_name = "subsurface_runoff_flux"
        v_qsb.long_name = "subsurface runoff amount"
        v_qsb.missing_value = np.float32(-9999.0)
        v_qsb[0, :, :] = qsb_tgt.astype(np.float32)

        ds_dst.title = "LIS land surface model output (conservative remap 180x120 for offline HYMAP2)"
        ds_dst.MAP_PROJECTION = "EQUIDISTANT CYLINDRICAL"
        ds_dst.SOUTH_WEST_CORNER_LAT = np.float32(30.025)
        ds_dst.SOUTH_WEST_CORNER_LON = np.float32(-9.975)
        ds_dst.DX = np.float32(0.05)
        ds_dst.DY = np.float32(0.05)

        ds_dst.close()
        os.replace(tmp_path, dst_path)
    except Exception as e:
        print(f"Error processing {src_path}: {e}")

def remap_experiment(exp_name, src_dir, dst_base):
    print(f"\n=======================================================")
    print(f"Remapping ruissellement 181x121 -> 180x120: {exp_name}")
    print(f"Source: {src_dir}")
    print(f"Destination: {dst_base}")
    print(f"=======================================================")
    os.makedirs(dst_base, exist_ok=True)
    src_files = sorted(glob.glob(os.path.join(src_dir, "**", "LIS_HIST_*.d01.nc"), recursive=True))
    print(f"Fichiers trouves: {len(src_files)}")
    if not src_files:
        print(f"ATTENTION: Aucun fichier source trouve pour {exp_name}!")
        return

    t0 = time.time()
    task_args = [(f, dst_base) for f in src_files]
    with mp.Pool(processes=16) as pool:
        pool.map(process_single_file, task_args)
    
    # Boundary padding file for the end of 2018: clone 201901010000 to 201901020000
    src_bnd = os.path.join(dst_base, "201901", "LIS_HIST_201901010000.d01.nc")
    dst_bnd = os.path.join(dst_base, "201901", "LIS_HIST_201901020000.d01.nc")
    if os.path.exists(src_bnd) and not os.path.exists(dst_bnd):
        shutil.copyfile(src_bnd, dst_bnd)
        print(f"Created terminal boundary file: {dst_bnd}")
    
    # Count remapped files
    dst_files = glob.glob(os.path.join(dst_base, "**", "LIS_HIST_*.d01.nc"), recursive=True)
    print(f"Remapping termine pour {exp_name}: {len(dst_files)} fichiers crees en {time.time()-t0:.1f} s.")

if __name__ == "__main__":
    experiments = [
        (
            "OL_DAIC_2018",
            os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/OL_DAIC_2018/output/SURFACEMODEL"),
            os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/OL_DAIC_2018/SURFACEMODEL")
        ),
        (
            "ENS_OPL_2018",
            os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/ENS_OPL_2018/output/SURFACEMODEL"),
            os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/ENS_OPL_2018/SURFACEMODEL")
        ),
        (
            "DA_nocdf_nowilt_2018",
            os.path.join(BASE_DIR, "experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL"),
            os.path.join(BASE_DIR, "experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_nowilt_2018/SURFACEMODEL")
        ),
    ]

    for name, src, dst in experiments:
        remap_experiment(name, src, dst)
