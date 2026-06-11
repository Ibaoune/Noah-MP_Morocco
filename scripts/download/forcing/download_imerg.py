#!/usr/bin/env python3

"""
===============================================================================
Script Name   : download_imerg.py
Description   : 
  Part 1: Authenticates with NASA Earthdata using local credentials (.netrc).
  Part 2: Searches for GPM IMERG granules intersecting the target bounding box.
  Part 3: Downloads the raw global HDF5 granules to local storage (no subsetting during download).
  Part 4: Restructures the downloaded files into YYYYMM subdirectories as required by LIS.
  Part 5: Generates and saves an inventory CSV report of all downloaded files.
  Part 6: Contains a configurable flag (PERFORM_SUBSET) to activate optional post-download 
          local spatial subsetting to reduce storage footprint.
Data Downloaded: GPM_3IMERGHH (Precipitation Final Run)
Data Version  : V07B
Frequency     : Half-hourly (30 minutes)
Resolution    : 0.1° x 0.1°
Source / Site : NASA GES DISC (via the `earthaccess` Python library)
Target Period : 2000-06-01 to 2023-12-31
Bounding Box  : 33.0N to 35.0N, 7.0W to 4.0W
Author        : M. El Aabaribaoune (@um6p)
Date Updated  : 2026-06-11
===============================================================================
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

import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description="Download IMERG data")
parser.add_argument('--start', type=str, default="2000-06-01", help="Start date (YYYY-MM-DD)")
parser.add_argument('--end', type=str, default="2023-12-31", help="End date (YYYY-MM-DD)")
args = parser.parse_args()

# --- Configuration ---
START_DATE = args.start
END_DATE = args.end
SHORT_NAME = "GPM_3IMERGHH" # Half-Hourly Final Run
VERSION = "07"
# Bounding box coordinates: (min_lon, min_lat, max_lon, max_lat)
BBOX = (-7.5, 32.0, -3.0, 36.0) 
PERFORM_SUBSET = False  # Set to True to perform local subsetting (post-download)

# Define root paths based on script location
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/forcing/IMERG/raw')
SUBSET_DIR = os.path.join(BASE_DIR, 'data/forcing/IMERG/subset')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_imerg.csv')

# Ensure necessary directories exist
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(SUBSET_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging to file and console
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
        # Try to login using ~/.netrc file credentials
        earthaccess.login(strategy="netrc")
    except Exception as e:
        logging.error(f"Failed to authenticate: {e}")
        logging.info("Attempting interactive login or environment variables...")
        earthaccess.login() # Will prompt for username/password if no credentials are found

    
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
    # The earthaccess library automatically skips existing files
    downloaded_files = earthaccess.download(
        results,
        local_path=RAW_DIR
    )
    
    # 4. Restructure files into YYYYMM directories (required by LIS IMERG reader)
    logging.info("Restructuring HDF5 files into YYYYMM subdirectories...")
    raw_files = sorted(glob.glob(os.path.join(RAW_DIR, '*.HDF5')))
    
    inventory_data = []
    
    for rf in raw_files:
        basename = os.path.basename(rf)
        
        # Extract date from filename (e.g., 3B-HHR.MS.MRG.3IMERG.20150101-S000000-E002959.0000.V07B.HDF5)
        date_str = "Unknown"
        yyyymm = "Unknown"
        try:
            date_part = basename.split('.')[4].split('-')[0]
            date_str = pd.to_datetime(date_part, format="%Y%m%d").strftime("%Y-%m-%d")
            yyyymm = date_part[:6]
        except Exception as e:
            logging.error(f"Failed to parse date for {basename}: {e}")
            continue
        
        # Create YYYYMM dir and move
        dest_dir = os.path.join(RAW_DIR, yyyymm)
        os.makedirs(dest_dir, exist_ok=True)
        dest_file = os.path.join(dest_dir, basename)
        
        # Move file if it is in the root RAW_DIR
        if rf != dest_file:
            os.rename(rf, dest_file)
            
        file_size = os.path.getsize(dest_file) / (1024 * 1024) # MB
        
        inventory_data.append({
            'date': date_str,
            'file_name': basename,
            'product': SHORT_NAME,
            'version': VERSION,
            'file_size_mb': round(file_size, 2),
            'status': "Downloaded_and_Structured"
        })
    
    # 5. Save inventory
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    
    # 6. Post-download subsetting (Optional)
    if PERFORM_SUBSET:
        logging.info("Local subsetting is activated (PERFORM_SUBSET=True).")
        logging.info("This is a post-download process. (Subsetting logic using xarray/h5py goes here...)")
        # TODO: Implement local subsetting reading from RAW_DIR and writing to SUBSET_DIR
    else:
        logging.info("Local subsetting is deactivated (PERFORM_SUBSET=False).")

    logging.info("IMERG workflow completed.")

if __name__ == "__main__":
    main()
