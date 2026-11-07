#!/usr/bin/env python3
# Conservative regridding of LIS runoff (Qs_tavg, Qsb_tavg) from 181x121 to 180x120
# For offline HYMAP2 routing.
import os, sys, glob, re
import netCDF4 as nc
import numpy as np

src_base = "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/output/2018-01/SURFACEMODEL"
dst_base = "experiments/NorthMor/routing/runoff_remap_180x120/OPL_noirr_2016_2020/SURFACEMODEL"

# Target coords from ldt_hymap/lis_input.d01.nc
ldt_path = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
ds_ldt = nc.Dataset(ldt_path)
tgt_lat = ds_ldt["lat"][:].astype(np.float32) # (120, 180)
tgt_lon = ds_ldt["lon"][:].astype(np.float32) # (120, 180)
ds_ldt.close()

files = sorted(glob.glob(src_base + "/**/LIS_HIST_*.d01.nc", recursive=True))
print(f"Found {len(files)} files to remap.")

for idx, src_file in enumerate(files):
    rel = os.path.relpath(src_file, src_base)
    dst_file = os.path.join(dst_base, rel)
    os.makedirs(os.path.dirname(dst_file), exist_ok=True)
    
    ds_src = nc.Dataset(src_file, "r")
    qs_src = ds_src["Qs_tavg"][:]
    qsb_src = ds_src["Qsb_tavg"][:]
    if qs_src.ndim == 3:
        qs_src = qs_src[0]
    if qsb_src.ndim == 3:
        qsb_src = qsb_src[0]
        
    time_val = ds_src["time"][:] if "time" in ds_src.variables else [0.0]
    time_units = getattr(ds_src["time"], "units", "minutes since 2018-01-01 00:00:00") if "time" in ds_src.variables else ""
    
    # Replace -9999 / missing / negative with 0.0 before conservative remap
    qs_clean = np.where((qs_src < 0) | np.isnan(qs_src), 0.0, qs_src).astype(np.float64)
    qsb_clean = np.where((qsb_src < 0) | np.isnan(qsb_src), 0.0, qsb_src).astype(np.float64)
    
    # 4-point conservative convolution: weight 0.25 on each of the 4 overlapping cells
    qs_tgt = 0.25 * (qs_clean[:-1, :-1] + qs_clean[:-1, 1:] + qs_clean[1:, :-1] + qs_clean[1:, 1:])
    qsb_tgt = 0.25 * (qsb_clean[:-1, :-1] + qsb_clean[:-1, 1:] + qsb_clean[1:, :-1] + qsb_clean[1:, 1:])
    
    # Create output NetCDF
    if os.path.exists(dst_file):
        os.remove(dst_file)
        
    ds_dst = nc.Dataset(dst_file, "w", format="NETCDF4_CLASSIC")
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
    
    # Global attributes
    ds_dst.title = "LIS land surface model output (conservative remap 180x120 for offline HYMAP2)"
    ds_dst.MAP_PROJECTION = "EQUIDISTANT CYLINDRICAL"
    ds_dst.SOUTH_WEST_CORNER_LAT = np.float32(30.025)
    ds_dst.SOUTH_WEST_CORNER_LON = np.float32(-9.975)
    ds_dst.DX = np.float32(0.05)
    ds_dst.DY = np.float32(0.05)
    ds_dst.missing_value = np.float32(-9999.0)
    
    ds_src.close()
    ds_dst.close()
    
print("Successfully remapped 31 files into", dst_base)
