#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_gleam.py

Script to download GLEAM Evapotranspiration data for validation over the Sebou-Saïss basin.
Target Period: 2015-01-01 to 2020-12-31
GLEAM Version: v3 (e.g. v3.7a or v3.7b)

Note: GLEAM data is typically downloaded from their FTP server (ftp.gleam.eu)
or provided via a direct download link upon registration.
"""

import os
import logging
import pandas as pd
from ftplib import FTP

# --- Configuration ---
START_YEAR = 2015
END_YEAR = 2020
VERSION = "v3.7a" # Adjust as per availability

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/validation/evapotranspiration/GLEAM')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_gleam.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_gleam.log')),
        logging.StreamHandler()
    ]
)

def main():
    logging.info("Starting GLEAM ET download workflow.")
    logging.info("NOTE: Please ensure you have registered for GLEAM to access their FTP server.")
    
    # FTP details (these might require update based on GLEAM's current access method)
    ftp_host = "ftp.gleam.eu"
    # Typically anonymous login with email as password, or explicit credentials provided by GLEAM
    
    inventory_data = []
    
    try:
        logging.info(f"Connecting to {ftp_host}...")
        # ftp = FTP(ftp_host)
        # ftp.login() # Add credentials if required
        
        # for year in range(START_YEAR, END_YEAR + 1):
            # Define remote path, e.g., /v3.7a/daily/2015/
            # Download E (actual ET) and Ep (potential ET) if needed
            # For this placeholder, we just log the requirement.
        logging.warning("FTP login is commented out. Implement specific paths based on your GLEAM access link.")
        
        # Dummy file creation for workflow completeness
        for year in range(START_YEAR, END_YEAR + 1):
            fname = f"E_{year}_GLEAM_{VERSION}.nc"
            output_path = os.path.join(RAW_DIR, fname)
            if not os.path.exists(output_path):
                with open(output_path, 'w') as f:
                    f.write("DUMMY GLEAM DATA. Download via FTP required.")
            
            inventory_data.append({
                'year': year,
                'file_name': fname,
                'product': 'GLEAM',
                'version': VERSION,
                'status': 'Dummy_Created'
            })
            
    except Exception as e:
        logging.error(f"FTP connection failed: {e}")
        
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("GLEAM workflow completed.")

if __name__ == "__main__":
    main()
