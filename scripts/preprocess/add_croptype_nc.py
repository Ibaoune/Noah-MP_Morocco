#!/usr/bin/env python3
# =============================================================================
# Author: M. El Aabaribaoune (@UM6P)
# Date:   2026-06-07
# =============================================================================
import netCDF4 as nc
import numpy as np

ds = nc.Dataset('data/lis_input/lis_input.d01_sebou.nc', 'a')

if 'CROPTYPE' not in ds.variables:
    # create the variable
    crop_var = ds.createVariable('CROPTYPE', 'f4', ('north_south', 'east_west'))
    crop_var.long_name = "Crop type classification"
    crop_var.missing_value = -9999.0
    crop_var.fill_value = -9999.0
    
    # We fill it with '1' everywhere, so the first index of maxrootdepth32.txt is always used.
    # We can also just read the landcover type and if it's cropland (12 or 14 in IGBP), set to 1.
    # But actually, the irrigation scale compute_irrigScale does the cropland check based on LANDCOVER!
    # So we can safely just set CROPTYPE = 1 everywhere.
    shape = ds.variables['LANDCOVER'].shape
    # Wait, LANDCOVER might be 3D. Let's just use the shape of IRRIGFRAC or lat
    shape = ds.variables['lat'].shape
    
    data = np.ones(shape, dtype=np.float32)
    crop_var[:] = data
    
ds.close()
print("CROPTYPE added successfully!")
