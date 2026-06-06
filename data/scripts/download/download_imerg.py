#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_imerg.py

Script to download and subset IMERG Final Run precipitation data for the 
Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31
Bounding Box: 33.0N to 35.0N, 7.0W to 4.0W
Uses the `earthaccess` python package for downloading.
"""

import os
import glob
import logging
import pandas as pd
import earthaccess
import xarray as xr
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

# --- Configuration ---
START_DATE = "2015-01-01"
END_DATE = "2020-12-31"
SHORT_NAME = "GPM_3IMERGDF" # Daily Final Run
VERSION = "07"
# Bounding box: (lower_left_lon, lower_left_lat, upper_right_lon, upper_right_lat)
BBOX = (-7.5, 32.0, -3.0, 36.0) 

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/forcing/IMERG/raw')
SUBSET_DIR = os.path.join(BASE_DIR, 'data/forcing/IMERG/subset')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_imerg.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SUBSET_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_imerg.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting IMERG download workflow.")
    
    # 1. Authenticate with Earthdata
    logging.info("Authenticating with NASA Earthdata...")
    try:
        earthaccess.login(strategy="netrc")
    except Exception as e:
        logging.error(f"Failed to authenticate: {e}")
        logging.info("Attempting interactive login or environment variables...")
        earthaccess.login() # Will prompt if no credentials found
    
    # 2. Search for granules
    logging.info(f"Searching for {SHORT_NAME} v{VERSION} from {START_DATE} to {END_DATE}...")
    results = earthaccess.search_data(
        short_name=SHORT_NAME,
        version=VERSION,
        bounding_box=BBOX,
        temporal=(START_DATE, END_DATE)
    )
    logging.info(f"Found {len(results)} granules.")
    
    # 3. Download granules
    logging.info(f"Downloading to {RAW_DIR}...")
    # earthaccess handles skipping existing files automatically if we use download
    downloaded_files = earthaccess.download(
        results,
        local_path=RAW_DIR
    )
    
    # 4. Subset and inventory
    logging.info("Subsetting files and building inventory...")
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, '*.nc4')))
    
    inventory_data = []
    
    for rf in raw_files:
        basename = os.path.basename(rf)
        subset_file = os.path.join(SUBSET_DIR, basename.replace('.nc4', '_subset.nc4'))
        
        # Extract date from filename (e.g., 3B-DAY.MS.MRG.3IMERG.20150101-S000000-E235959.V07B.nc4)
        date_str = ""
        try:
            date_part = basename.split('.')[4].split('-')[0]
            date_str = pd.to_datetime(date_part, format="%Y%m%d").strftime("%Y-%m-%d")
        except:
            date_str = "Unknown"
        
        status = "Downloaded"
        
        # Subset if not already done
        if not os.path.exists(subset_file):
            try:
                ds = xr.open_dataset(rf)
                # Note: IMERG typically uses lon: -180 to 180, lat: -90 to 90.
                # Adjust variable names if needed (usually 'precipitationCal')
                subset_ds = ds.sel(
                    lon=slice(BBOX[0], BBOX[2]),
                    lat=slice(BBOX[1], BBOX[3])
                )
                subset_ds.to_netcdf(subset_file)
                ds.close()
                subset_ds.close()
                status = "Downloaded_and_Subsetted"
            except Exception as e:
                logging.error(f"Failed to subset {basename}: {e}")
                status = "Subset_Failed"
        else:
            status = "Already_Subsetted"
            
        file_size = os.path.getsize(rf) / (1024 * 1024) # MB
        
        inventory_data.append({
            'date': date_str,
            'file_name': basename,
            'product': SHORT_NAME,
            'version': VERSION,
            'file_size_mb': round(file_size, 2),
            'status': status
        })
    
    # 5. Save inventory
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("IMERG workflow completed.")

if __name__ == "__main__":
    main()
