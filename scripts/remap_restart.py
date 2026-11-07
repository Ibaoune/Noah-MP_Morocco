#!/usr/bin/env python3
"""
Remap Noah-MP 4.0.1 restart file from 181x121 domain (16030 tiles)
to the new 180x120 HyMAP-aligned domain (15888 tiles).
"""
import sys
import numpy as np
import netCDF4 as nc
from scipy.spatial import cKDTree

def remap_restart(src_path, ldt_input_path, dst_path):
    print(f"Reading source restart: {src_path}")
    ds_src = nc.Dataset(src_path, 'r')
    
    print(f"Reading target domain parameters: {ldt_input_path}")
    ds_ldt = nc.Dataset(ldt_input_path, 'r')
    
    lmask = ds_ldt.variables['LANDMASK'][:]
    nr, nc_dim = lmask.shape # 120, 180
    
    # Generate list of new tiles in LIS row-major order
    new_lats = []
    new_lons = []
    for r in range(nr):
        for c in range(nc_dim):
            if lmask[r, c] == 1:
                new_lats.append(30.025 + r * 0.05)
                new_lons.append(-9.975 + c * 0.05)
                
    new_lats = np.array(new_lats, dtype=np.float32)
    new_lons = np.array(new_lons, dtype=np.float32)
    ntiles_new = len(new_lats)
    print(f"New domain tiles count: {ntiles_new}")
    
    # KD-Tree on source coordinates
    src_lats = ds_src.variables['lat'][:]
    src_lons = ds_src.variables['lon'][:]
    src_pts = np.column_stack([src_lons, src_lats])
    new_pts = np.column_stack([new_lons, new_lats])
    
    tree = cKDTree(src_pts)
    dists, indices = tree.query(new_pts)
    print(f"Max distance: {dists.max():.4f} deg, Mean distance: {dists.mean():.4f} deg")
    
    # Create destination file
    print(f"Writing remapped restart to: {dst_path}")
    ds_dst = nc.Dataset(dst_path, 'w', format='NETCDF4_CLASSIC')
    
    # Copy global attributes
    for attr in ds_src.ncattrs():
        if attr == 'SOUTH_WEST_CORNER_LAT':
            ds_dst.setncattr(attr, np.float32(30.025))
        elif attr == 'SOUTH_WEST_CORNER_LON':
            ds_dst.setncattr(attr, np.float32(-9.975))
        elif attr == 'history':
            ds_dst.setncattr(attr, f"Remapped from {src_path} onto 180x120 grid")
        else:
            ds_dst.setncattr(attr, ds_src.getncattr(attr))
            
    # Create dimensions
    for dimname, dim in ds_src.dimensions.items():
        if dimname == 'ntiles':
            ds_dst.createDimension('ntiles', ntiles_new)
        elif dim.isunlimited():
            ds_dst.createDimension(dimname, None)
        else:
            ds_dst.createDimension(dimname, len(dim))
            
    # Create and copy variables
    for vname, var in ds_src.variables.items():
        fill_val = getattr(var, '_FillValue', None)
        dst_var = ds_dst.createVariable(vname, var.dtype, var.dimensions, fill_value=fill_val)
        for attr in var.ncattrs():
            if attr != '_FillValue':
                dst_var.setncattr(attr, var.getncattr(attr))
            
        if vname == 'lat':
            dst_var[:] = new_lats
        elif vname == 'lon':
            dst_var[:] = new_lons
        elif vname == 'time':
            dst_var[:] = var[:]
        elif var.dimensions == ('ntiles',):
            src_val = var[:]
            dst_var[:] = src_val[indices]
        elif len(var.dimensions) == 2 and var.dimensions[1] == 'ntiles':
            src_val = var[:] # shape: (dimX, ntiles_old)
            dst_var[:] = src_val[:, indices]
        else:
            print(f"Warning: unexpected shape for {vname}: {var.shape}")
            dst_var[:] = var[:]
            
    ds_src.close()
    ds_ldt.close()
    ds_dst.close()
    print("Remapping completed successfully!")

if __name__ == '__main__':
    src = "experiments/NorthMor/matrix_2016_2020/OPL_noirr_2016_2020/restarts/LIS_RST_NOAHMP401_201801010000.d01.nc"
    ldt = "experiments/NorthMor/routing/ldt_hymap/lis_input.d01.nc"
    dst = "experiments/NorthMor/routing/restarts/LIS_RST_NOAHMP401_201801010000.d01.nc"
    remap_restart(src, ldt, dst)
