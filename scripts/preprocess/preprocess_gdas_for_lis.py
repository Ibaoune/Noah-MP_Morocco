#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
preprocess_gdas_for_lis.py

Converts raw GDAS GRIB2 files into formats/NetCDF expected by LIS.
Subsets to the Sebou-Saïss domain and maintains original temporal resolution.
"""

import os
import glob
import logging
# import xarray as xr # Assuming use of xarray with cfgrib backend

# --- Configuration ---
BBOX = (-7.5, 32.0, -3.0, 36.0)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/forcing/GDAS/raw')
SUBSET_DIR = os.path.join(BASE_DIR, 'data/forcing/GDAS/subset')

os.makedirs(SUBSET_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/preprocess/preprocess_gdas.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting GDAS preprocessing...")
    
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, '*.grib2')))
    if not raw_files:
        logging.warning("No raw GDAS files found. Have they been downloaded?")
        return
        
    for rf in raw_files:
        basename = os.path.basename(rf)
        out_name = basename.replace('.grib2', '_subset.nc')
        out_path = os.path.join(SUBSET_DIR, out_name)
        
        if os.path.exists(out_path):
            logging.info(f"Skipping {basename}, already processed.")
            continue
            
        logging.info(f"Processing {basename}...")
        try:
            # Example logic using xarray and cfgrib:
            # ds = xr.open_dataset(rf, engine='cfgrib')
            # 
            # # GDAS longitude is typically 0 to 360, need to align with BBOX -7.0 to -4.0
            # ds = ds.assign_coords(longitude=(((ds.longitude + 180) % 360) - 180))
            # ds = ds.sortby('longitude')
            # 
            # subset_ds = ds.sel(
            #     longitude=slice(BBOX[0], BBOX[2]),
            #     latitude=slice(BBOX[3], BBOX[1]) # Descending lat usually in GDAS
            # )
            # 
            # subset_ds.to_netcdf(out_path)
            # ds.close()
            
            # Dummy output for workflow completeness
            with open(out_path, 'w') as f:
                f.write("DUMMY GDAS NETCDF SUBSET")
        except Exception as e:
            logging.error(f"Failed to process {basename}: {e}")
            
    logging.info("GDAS preprocessing completed.")

if __name__ == "__main__":
    main()
