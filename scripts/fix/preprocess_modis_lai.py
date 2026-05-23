#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p) / Antigravity (Google DeepMind)
#
# preprocess_modis_lai.py
#
# Converts downloaded MODIS MOD15A2H tile HDF files (Sinusoidal projection)
# into compressed global NetCDF4 files expected by the LIS "MCD15A2H LAI" plugin.
#
# LIS reader (read_MCD15A2H_LAI_data) expects:
#   - NC4 file with GLOBAL dims (lon=86400, lat=43200) at res 1/240 deg
#   - Variable names: Lai_500m and FparLai_QC
#   - Lat dimension increases Southward (standard raster order)
#   - Output path: <dir>/<YYYY>/MCD15A2H.006_LAI_YYYYDOY.nc4
#
# Requirements:
#   module load GDAL/3.7.1-foss-2023a
#   module load NCO/5.0.3-foss-2021b   # for ncrename
#
# Usage:
#   python3 scripts/fix/preprocess_modis_lai.py

import os
import sys
import glob
import re
import subprocess

# Full path to ncrename (from: module load NCO/5.0.3-foss-2021b && which ncrename)
NCRENAME = '/srv/software/easybuild/software/NCO/5.0.3-foss-2021b/bin/ncrename'
import shutil
import numpy as np
from osgeo import gdal, osr

gdal.UseExceptions()

# ---- Configuration --------------------------------------------------------
GLOBAL_NC = 86400        # global grid columns (360 deg × 240 pts/deg)
GLOBAL_NR = 43200        # global grid rows    (180 deg × 240 pts/deg)
RES       = 1.0 / 240.0  # ~0.00416667 deg ≈ 500 m at equator

HDF_DIR   = "data/observations/MODIS_LAI"
OUT_DIR   = "data/observations/MODIS_LAI/processed"
FILL_BYTE = 255           # standard MODIS fill value (uint8)

# ---- Core Functions -------------------------------------------------------

def warp_to_epsg4326(hdf_path, subdataset_name):
    """Warp a MODIS sinusoidal subdataset to EPSG:4326 (in memory)."""
    sub = f'HDF4_EOS:EOS_GRID:"{hdf_path}":MOD_Grid_MOD15A2H:{subdataset_name}'
    ds = gdal.Warp(
        '', sub,
        format='MEM',
        dstSRS='EPSG:4326',
        xRes=RES, yRes=RES,
        resampleAlg='near',
        srcNodata=FILL_BYTE, dstNodata=FILL_BYTE,
        outputType=gdal.GDT_Byte,
    )
    if ds is None:
        raise RuntimeError(f"gdal.Warp returned None for {sub}")
    return ds


def build_global_array(tile_ds):
    """
    Read a tile dataset (EPSG:4326, North-down raster convention) and
    stamp it into a FILL_BYTE-initialised global grid.
    The global grid goes: row 0 = top-North, row NR-1 = bottom-South
    (standard raster convention, matching how GDAL writes netCDF).
    """
    gt  = tile_ds.GetGeoTransform()  # (ulx, xres, 0, uly, 0, yres)
    ulx = gt[0]  # western edge longitude
    uly = gt[3]  # northern edge latitude
    nc_tile = tile_ds.RasterXSize
    nr_tile = tile_ds.RasterYSize

    # Column offset: pixels left of the global western edge (-180°)
    col_start = int(round((ulx - (-180.0)) / RES))
    # Row offset from global top edge (+90°): tile top latitude
    row_start = int(round((90.0 - uly) / RES))

    col_end = col_start + nc_tile
    row_end = row_start + nr_tile

    # Clamp to global grid
    cs = max(0, min(GLOBAL_NC, col_start))
    ce = max(0, min(GLOBAL_NC, col_end))
    rs = max(0, min(GLOBAL_NR, row_start))
    re = max(0, min(GLOBAL_NR, row_end))

    if cs >= ce or rs >= re:
        raise ValueError(f"Tile falls outside global grid! col=[{cs}:{ce}] row=[{rs}:{re}]")

    tile_data = tile_ds.GetRasterBand(1).ReadAsArray()  # shape (nr_tile, nc_tile), North→South

    # Corresponding sub-region offsets inside the tile
    tc_start = cs - col_start
    tr_start = rs - row_start
    tc_end   = tc_start + (ce - cs)
    tr_end   = tr_start + (re - rs)

    global_arr = np.full((GLOBAL_NR, GLOBAL_NC), FILL_BYTE, dtype=np.uint8)
    global_arr[rs:re, cs:ce] = tile_data[tr_start:tr_end, tc_start:tc_end]

    print(f"    Tile placed at cols [{cs}:{ce}], rows [{rs}:{re}]")
    return global_arr


def write_nc4_via_gdal(out_path, lai_arr, qc_arr):
    """
    Write two global uint8 arrays to a compressed NetCDF4 file using GDAL.
    Variables will be Band1 and Band2 — renamed afterwards by ncrename.
    """
    tmp_path = out_path + ".tmp.nc4"
    drv = gdal.GetDriverByName('netCDF')
    srs = osr.SpatialReference(); srs.ImportFromEPSG(4326)

    ds = drv.Create(
        tmp_path, GLOBAL_NC, GLOBAL_NR, 2, gdal.GDT_Byte,
        options=['FORMAT=NC4', 'COMPRESS=DEFLATE', 'ZLEVEL=4',
                 'WRITE_GDAL_TAGS=NO', 'WRITE_GDAL_VERSION=NO',
                 'WRITE_LONLAT=NO']
    )
    # GeoTransform: top-left = (-180, 90), pixelsize = RES, -RES
    ds.SetGeoTransform((-180.0, RES, 0.0, 90.0, 0.0, -RES))
    ds.SetProjection(srs.ExportToWkt())

    b1 = ds.GetRasterBand(1)
    b1.SetNoDataValue(FILL_BYTE)
    b1.WriteArray(lai_arr)

    b2 = ds.GetRasterBand(2)
    b2.SetNoDataValue(FILL_BYTE)
    b2.WriteArray(qc_arr)

    ds.FlushCache()
    ds = None
    return tmp_path


def rename_variables(tmp_path, out_path):
    """Use ncrename to rename Band1→Lai_500m and Band2→FparLai_QC."""
    ret = subprocess.run(
        [NCRENAME, '-v', 'Band1,Lai_500m', '-v', 'Band2,FparLai_QC',
         tmp_path, out_path],
        capture_output=True, text=True
    )
    if ret.returncode != 0:
        raise RuntimeError(f"ncrename failed:\n{ret.stderr}")
    os.remove(tmp_path)


# ---- Main per-file function -----------------------------------------------

def process_file(hdf_path):
    filename = os.path.basename(hdf_path)
    m = re.match(r"MOD15A2H\.A(\d{4})(\d{3})\.", filename)
    if not m:
        print(f"[WARN] Skipping unrecognised filename: {filename}")
        return

    year, doy = m.group(1), m.group(2)
    year_dir  = os.path.join(OUT_DIR, year)
    os.makedirs(year_dir, exist_ok=True)

    out_name  = f"MCD15A2H.006_LAI_{year}{doy}.nc4"
    out_path  = os.path.join(year_dir, out_name)

    if os.path.exists(out_path):
        print(f"[SKIP] {out_name} already exists.")
        return

    print(f"\n[PROCESSING] {filename}")

    print("  Warping Lai_500m ...")
    ds_lai = warp_to_epsg4326(hdf_path, 'Lai_500m')
    print("  Building global LAI array ...")
    global_lai = build_global_array(ds_lai)
    ds_lai = None

    print("  Warping FparLai_QC ...")
    ds_qc  = warp_to_epsg4326(hdf_path, 'FparLai_QC')
    print("  Building global QC array ...")
    global_qc  = build_global_array(ds_qc)
    ds_qc = None

    print("  Writing temporary NC4 ...")
    tmp_path = write_nc4_via_gdal(out_path, global_lai, global_qc)
    del global_lai, global_qc

    print("  Renaming variables (ncrename) ...")
    rename_variables(tmp_path, out_path)

    size_mb = os.path.getsize(out_path) / (1024 * 1024)
    print(f"  [OK] {out_name}  ({size_mb:.1f} MB)")


# ---- Entry Point ----------------------------------------------------------

if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)

    hdf_files = sorted(glob.glob(os.path.join(HDF_DIR, "*.hdf")))
    if not hdf_files:
        print(f"ERROR: No .hdf files found in {HDF_DIR}")
        sys.exit(1)

    print(f"Found {len(hdf_files)} HDF file(s) to process.")
    errors = []
    for hdf_path in hdf_files:
        try:
            process_file(hdf_path)
        except Exception as e:
            print(f"  [ERROR] {os.path.basename(hdf_path)}: {e}")
            errors.append(hdf_path)

    print(f"\nDone. {len(hdf_files)-len(errors)} processed, {len(errors)} errors.")
    if errors:
        print("Failed files:")
        for f in errors:
            print(" ", f)
        sys.exit(1)
