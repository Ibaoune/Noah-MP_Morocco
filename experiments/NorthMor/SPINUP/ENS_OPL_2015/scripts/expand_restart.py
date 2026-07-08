#!/usr/bin/env python3
# Author: M. El Aabaribaoune (@um6p)
import sys
import os
import shutil
import netCDF4 as nc
import numpy as np

def expand_restart(input_file, output_file, num_ensembles=20):
    print(f"Expanding {input_file} to {output_file} with {num_ensembles} ensembles...")
    shutil.copy2(input_file, output_file)
    
    with nc.Dataset(output_file, 'r+') as ds:
        # Check current ntiles
        current_ntiles = ds.dimensions['ntiles'].size
        new_ntiles = current_ntiles * num_ensembles
        print(f"Current ntiles: {current_ntiles}, New ntiles: {new_ntiles}")
        
        # We need to recreate the file to change dimension size easily in netCDF3/4
        # But wait, netCDF4 might not allow resizing a dimension unless it's UNLIMITED.
        pass

# Actually, to change dimension size safely in netCDF4:
def create_expanded_restart(input_file, output_file, num_ensembles=20):
    print(f"Creating {output_file} from {input_file} with {num_ensembles} ensembles...")
    with nc.Dataset(input_file, 'r') as src, nc.Dataset(output_file, 'w', format=src.data_model) as dst:
        # Copy global attributes
        dst.setncatts({k: src.getncattr(k) for k in src.ncattrs()})
        
        # Copy dimensions
        for name, dim in src.dimensions.items():
            if name == 'ntiles':
                dst.createDimension(name, len(dim) * num_ensembles)
            else:
                dst.createDimension(name, len(dim) if not dim.isunlimited() else None)
        
        # Copy variables
        for name, var in src.variables.items():
            outVar = dst.createVariable(name, var.datatype, var.dimensions)
            outVar.setncatts({k: var.getncattr(k) for k in var.ncattrs()})
            
            if 'ntiles' in var.dimensions:
                # We need to replicate the data along the ntiles dimension
                axis = var.dimensions.index('ntiles')
                data = var[:]
                # Replicate
                expanded_data = np.repeat(data, num_ensembles, axis=axis)
                outVar[:] = expanded_data
            else:
                outVar[:] = var[:]

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python expand_restart.py <input> <output> <num_ensembles>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    num_ensembles = int(sys.argv[3])
    
    create_expanded_restart(input_file, output_file, num_ensembles)
    print("Done.")
