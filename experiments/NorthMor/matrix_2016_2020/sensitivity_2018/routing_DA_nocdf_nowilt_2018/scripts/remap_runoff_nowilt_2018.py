#!/usr/bin/env python3
"""
Remapping du ruissellement (Qs, Qsb) de DA_nocdf_nowilt_2018 vers la grille HyMAP2 (180x120).
Auteur: mohammad.elaabaribao
"""
import os, glob, re, time
import multiprocessing as mp
import netCDF4 as nc
import numpy as np

src_base = "/srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/matrix_2016_2020/sensitivity_2018/DA_nocdf_nowilt_2018/output/SURFACEMODEL"
dst_base = "/srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/runoff_remap_180x120/DA_nocdf_nowilt_2018/SURFACEMODEL"
ldt_path = "/srv/lustre01/project/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco/experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"

os.makedirs(dst_base, exist_ok=True)

ds_ldt = nc.Dataset(ldt_path)
tgt_lat = ds_ldt["lat"][:].astype(np.float32)
tgt_lon = ds_ldt["lon"][:].astype(np.float32)
ds_ldt.close()

def process_file(src_path):
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
        v_lat[:] = tgt_lat

        v_lon = ds_dst.createVariable("lon", "f4", ("north_south", "east_west"))
        v_lon.units = "degrees_east"
        v_lon[:] = tgt_lon

        v_qs = ds_dst.createVariable("Qs_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qs.units = "kg m-2 s-1"
        v_qs[0, :, :] = qs_tgt.astype(np.float32)

        v_qsb = ds_dst.createVariable("Qsb_tavg", "f4", ("time", "north_south", "east_west"), fill_value=-9999.0)
        v_qsb.units = "kg m-2 s-1"
        v_qsb[0, :, :] = qsb_tgt.astype(np.float32)

        ds_dst.close()
        os.rename(tmp_path, dst_path)
    except Exception as e:
        print(f"Error {src_path}: {e}")

if __name__ == "__main__":
    src_files = sorted(glob.glob(os.path.join(src_base, "*", "LIS_HIST_*.d01.nc")))
    print(f"Total fichiers a remapper : {len(src_files)}")
    if src_files:
        with mp.Pool(16) as pool:
            pool.map(process_file, src_files)
        print("Remapping terminé !")
