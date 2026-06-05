#!/usr/bin/env python3
"""
download_grace.py

Script to download GRACE / GRACE-FO Mascon Terrestrial Water Storage
for the Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31
Bounding Box: 33.0N to 35.0N, 7.0W to 4.0W
Uses the `earthaccess` python package for downloading.
"""

import os
import logging
import pandas as pd
import earthaccess

# --- Configuration ---
START_DATE = "2015-01-01"
END_DATE = "2020-12-31"
CONCEPT_ID = "C3195527175-POCLOUD" # JPL GRACE and GRACE-FO Mascon CRI Filtered Release 06.3 Version 04
BBOX = (-7.5, 32.0, -3.0, 36.0)

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
RAW_DIR = os.path.join(DATA_DIR, 'validation/water_storage/GRACE_GRACEFO/raw')
REPORT_DIR = os.path.join(DATA_DIR, 'reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_grace.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(DATA_DIR, 'logs/download/download_grace.log')),
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
    logging.info(f"Searching for Concept ID {CONCEPT_ID} from {START_DATE} to {END_DATE}...")
    results = earthaccess.search_data(
        concept_id=CONCEPT_ID,
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
