#!/usr/bin/env python3
# ==============================================================================
# Script: download_grace.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

"""
download_grace.py

Script to download GRACE / GRACE-FO Mascon Terrestrial Water Storage
for the Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31
Uses the `earthaccess` python package for downloading.
"""

import os
import sys
import logging
import pandas as pd
import earthaccess

# Import centralized configuration
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config_validation as config

CONCEPT_ID = "C3195527175-POCLOUD" # JPL GRACE and GRACE-FO Mascon CRI Filtered Release 06.3 Version 04

RAW_DIR = os.path.join(config.PROJECT_ROOT, 'data/validation/water_storage/GRACE_GRACEFO/raw')
os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(config.REPORT_DIR, exist_ok=True)
INVENTORY_FILE = os.path.join(config.REPORT_DIR, 'inventory_grace.csv')

# Set up logging locally
log_file = os.path.join(os.path.dirname(__file__), "logs", "download_grace.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting GRACE/GRACE-FO Mascon download workflow.")
    
    # Authenticate
    logging.info("Authenticating with NASA Earthdata...")
    try:
        earthaccess.login(strategy="netrc")
    except Exception as e:
        logging.error(f"Failed to authenticate: {e}")
        earthaccess.login()
        
    # Search
    logging.info(f"Searching for Concept ID {CONCEPT_ID} from {config.START_DATE} to {config.END_DATE}...")
    results = earthaccess.search_data(
        concept_id=CONCEPT_ID,
        bounding_box=config.BBOX,
        temporal=(config.START_DATE, config.END_DATE)
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
        
        inventory_data.append({
            'file_name': fname,
            'product': "GRACE_Mascon",
            'file_size_mb': round(size, 2),
            'status': status
        })
        
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("GRACE workflow completed.")

if __name__ == "__main__":
    main()
