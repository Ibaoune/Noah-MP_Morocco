#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script: download_modis_mcd15a2h.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# =============================================================================
# download_modis_mcd15a2h.py
#
# Moved to: scripts/download/validation/  (2026-06-11)
#
# Download MODIS Terra+Aqua LAI/FPAR 8-Day 500m (MCD15A2H Collection 6.1)
# for the Sebou-Saïss basin, Morocco.
#
# Validation period: 2015-01-01 to 2020-12-31  ← DATA ALREADY COMPLETE
# Bounding box:      W=-7.5°, S=32.0°, E=-3.0°, N=36.0° (MODIS tile h17v05)
# Storage:           data/observations_archive/MODIS_LAI/raw/   (276 HDF files)
#
# NOTE: The 2015-2020 dataset is already fully downloaded (276 HDF files).
#       Run this script only if re-downloading is required (e.g., corruption).
#       Uses the `earthaccess` Python library (NASA Earthdata login required).
# =============================================================================


import os
import logging
import pandas as pd
import earthaccess

import argparse

parser = argparse.ArgumentParser(description="Download MODIS MCD15A2H data")
parser.add_argument('--start_date', type=str, default="2015-01-01", help='Start date YYYY-MM-DD')
parser.add_argument('--end_date', type=str, default="2020-12-31", help='End date YYYY-MM-DD')
args = parser.parse_args()

START_DATE = args.start_date
END_DATE = args.end_date
SHORT_NAME = "MCD15A2H"
VERSION = "061" # Collection 6.1
BBOX = (-7.5, 32.0, -3.0, 36.0) # Relevant tile is typically h17v05

BASE_DIR = "/home/mohammad.elaabaribao/lustre/empowermed-ahl6xm8o7mg/users/mohammad.elaabaribao/NoahMP_Morocco"
RAW_DIR = os.path.join(BASE_DIR, 'data/observations/MODIS_MCD15A2H/raw')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_modis_mcd15a2h.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_modis.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting MODIS MCD15A2H download workflow.")
    
    # Authenticate
    logging.info("Authenticating with NASA Earthdata...")
    try:
        earthaccess.login(strategy="netrc")
    except Exception as e:
        logging.error(f"Failed to authenticate: {e}")
        earthaccess.login()
        
    # Search
    logging.info(f"Searching for {SHORT_NAME} v{VERSION} from {START_DATE} to {END_DATE}...")
    results = earthaccess.search_data(
        short_name=SHORT_NAME,
        version=VERSION,
        bounding_box=BBOX,
        temporal=(START_DATE, END_DATE)
    )
    logging.info(f"Found {len(results)} granules.")
    
    # Download
    logging.info(f"Downloading to {RAW_DIR}...")
    downloaded_files = earthaccess.download(
        results,
        local_path=RAW_DIR
    )
    
    # Inventory
    logging.info("Building inventory...")
    inventory_data = []
    
    for r in results:
        fname = r.data_links(access="external")[0].split("/")[-1]
        output_path = os.path.join(RAW_DIR, fname)
        
        status = "Downloaded" if os.path.exists(output_path) else "Failed"
        size = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0
        
        # Extract date from MODIS filename (e.g., MCD15A2H.A2015001.h17v05.061.2020211155959.hdf)
        try:
            date_part = fname.split('.')[1][1:] # e.g. 2015001 (YYYYDDD)
            date_str = pd.to_datetime(date_part, format="%Y%j").strftime("%Y-%m-%d")
        except:
            date_str = "Unknown"
            
        inventory_data.append({
            'date': date_str,
            'file_name': fname,
            'product': SHORT_NAME,
            'version': VERSION,
            'file_size_mb': round(size, 2),
            'status': status
        })
        
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("MODIS workflow completed.")

if __name__ == "__main__":
    main()
