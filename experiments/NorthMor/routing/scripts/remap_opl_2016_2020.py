#!/usr/bin/env python3
import os, glob, re, time
import multiprocessing as mp
import netCDF4 as nc
import numpy as np

ldt_path = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
ds_ldt = nc.Dataset(ldt_path)
tgt_lat = ds_ldt["lat"][:].astype(np.float32)
tgt_lon = ds_ldt["lon"][:].astype(np.float32)
ds_ldt.close()

dst_base = "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"
os.makedirs(dst_base, exist_ok=True)

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
        time_units = getattr(ds_src["time"], "units", "minutes since 2016-01-01 00:00:00")
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

        v_time = ds_dst.createVariable("time", "f4", ("time",))
        v_time.units = time_units
        v_time[:] = time_val

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

if __name__ == "__main__":
    src_pattern = "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/**/LIS_HIST_*.d01.nc"
    files = sorted(glob.glob(src_pattern, recursive=True))
    print(f"Found {len(files)} files to process...")
    t0 = time.time()
    with mp.Pool(processes=16) as pool:
        pool.map(process_file, files)
    
    # Boundary file for the end of 2020: copy 202101010000 to 202101020000
    src_bnd = os.path.join(dst_base, "202101", "LIS_HIST_202101010000.d01.nc")
    dst_bnd = os.path.join(dst_base, "202101", "LIS_HIST_202101020000.d01.nc")
    if os.path.exists(src_bnd) and not os.path.exists(dst_bnd):
        import shutil
        shutil.copyfile(src_bnd, dst_bnd)
        print(f"Created terminal boundary file: {dst_bnd}")
        
    print(f"Remapping completed in {time.time()-t0:.2f} s.")
