#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_smap_spl3smp_e.py

Script to download SMAP Enhanced L3 Radiometer Global Daily 9 km Soil Moisture (SPL3SMP_E)
for the Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31
Bounding Box: 33.0N to 35.0N, 7.0W to 4.0W
Uses the `earthaccess` python package for downloading.
"""

import os
import logging
import pandas as pd
import earthaccess

import argparse

parser = argparse.ArgumentParser(description="Download SMAP SPL3SMP_E data")
parser.add_argument('--start_date', type=str, default="2015-01-01", help='Start date YYYY-MM-DD')
parser.add_argument('--end_date', type=str, default="2020-12-31", help='End date YYYY-MM-DD')
args = parser.parse_args()

# --- Configuration ---
START_DATE = args.start_date
END_DATE = args.end_date
SHORT_NAME = "SPL3SMP_E"
VERSION = "006" # Version 6 as requested
BBOX = (-7.5, 32.0, -3.0, 36.0)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/observations/SMAP_SPL3SMP_E/raw')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_smap_spl3smp_e.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_smap.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting SMAP SPL3SMP_E download workflow.")
    
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
        
        # Extract date from SMAP filename (e.g., SMAP_L3_SM_P_E_20150401_R18290_001.h5)
        try:
            date_part = fname.split('_')[5]
            date_str = pd.to_datetime(date_part, format="%Y%m%d").strftime("%Y-%m-%d")
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
    logging.info("SMAP workflow completed.")

if __name__ == "__main__":
    main()
