#!/usr/bin/env python3
# =============================================================================
# Author: M. El Aabaribaoune (@UM6P)
# Date:   2026-06-07
# =============================================================================
import netCDF4 as nc

ds = nc.Dataset('data/lis_input/lis_input.d01_sebou.nc', 'a')
ds.setncattr('CROPCLASS_SCHEME', 'CROPMAP')
ds.setncattr('CROPCLASS_NUMBER', 0)
ds.close()
print("Attributes added successfully!")
