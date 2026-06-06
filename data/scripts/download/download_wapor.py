#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_wapor.py

Script to download FAO WaPOR AETI (Actual Evapotranspiration and Interception)
for the Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31
"""

import os
import logging
import pandas as pd
import requests

# --- Configuration ---
START_DATE = "2015-01-01"
END_DATE = "2020-12-31"

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/validation/evapotranspiration/WaPOR')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_wapor.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_wapor.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting WaPOR AETI download workflow.")
    logging.info("NOTE: Downloading WaPOR programmatically requires an API token from FAO WaPOR portal.")
    
    # Normally use 'wapor-api' python package or requests with API token
    # This is a skeleton.
    
    inventory_data = []
    
    years = range(2015, 2021)
    for year in years:
        fname = f"WaPOR_AETI_{year}.tif"
        output_path = os.path.join(RAW_DIR, fname)
        
        if not os.path.exists(output_path):
            with open(output_path, 'w') as f:
                f.write("DUMMY WAPOR DATA. API download implementation required.")
        
        inventory_data.append({
            'year': year,
            'file_name': fname,
            'product': 'WaPOR_AETI',
            'status': 'Dummy_Created'
        })
        
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("WaPOR workflow completed.")

if __name__ == "__main__":
    main()
