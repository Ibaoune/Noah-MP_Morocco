#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_esa_cci_sm.py

Script to download ESA CCI Soil Moisture data for validation.
Target Period: 2015-01-01 to 2020-12-31
Product: COMBINED
"""

import os
import logging
import pandas as pd

# --- Configuration ---
START_YEAR = 2015
END_YEAR = 2020

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/validation/soil_moisture/ESA_CCI')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_esa_cci.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_esa_cci.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting ESA CCI SM download workflow.")
    logging.info("NOTE: Download typically requires access via CEDA Archive or CDS API.")
    
    inventory_data = []
    
    # Placeholder for actual CDS API or FTP download loop
    for year in range(START_YEAR, END_YEAR + 1):
        fname = f"ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{year}.nc"
        output_path = os.path.join(RAW_DIR, fname)
        
        if not os.path.exists(output_path):
            with open(output_path, 'w') as f:
                f.write("DUMMY ESA CCI DATA. Download implementation required.")
        
        inventory_data.append({
            'year': year,
            'file_name': fname,
            'product': 'ESA_CCI_COMBINED',
            'status': 'Dummy_Created'
        })
        
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("ESA CCI SM workflow completed.")

if __name__ == "__main__":
    main()
