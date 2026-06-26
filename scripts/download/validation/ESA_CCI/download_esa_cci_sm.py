#!/usr/bin/env python3
# ==============================================================================
# Script: download_esa_cci_sm.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config_validation as config
from credentials_validation import CEDA_USERNAME, CEDA_PASSWORD


"""
download_esa_cci_sm.py

Script to download ESA CCI Soil Moisture data for validation via CEDA HTTP Archive.
Target Period: 2015-01-01 to 2020-12-31
Product: COMBINED v08.1
"""

import logging
import pandas as pd
import requests
from datetime import date, timedelta
from requests.auth import HTTPBasicAuth

# --- Configuration ---
START_DATE = date(2015, 1, 1)
END_DATE = date(2020, 12, 31)
VERSION = "v08.1"

# --- Identifiants ---



BASE_DIR = config.PROJECT_ROOT
RAW_DIR = os.path.join(BASE_DIR, 'data/validation/soil_moisture/ESA_CCI/raw')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_esa_cci.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging locally
log_file = os.path.join(os.path.dirname(__file__), "logs", "download_esa_cci.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

def main():
    logging.info("Starting ESA CCI SM download workflow via CEDA HTTP.")
    
    inventory_data = []
    auth = HTTPBasicAuth(CEDA_USERNAME, CEDA_PASSWORD)
    session = requests.Session()
    session.auth = auth
    
    for single_date in daterange(START_DATE, END_DATE):
        year_str = single_date.strftime("%Y")
        date_str = single_date.strftime("%Y%m%d")
        
        fname = f"ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{date_str}000000-f{VERSION}.nc"
        # Download URL example: https://dap.ceda.ac.uk/neodc/esacci/soil_moisture/data/daily_files/COMBINED/v08.1/2015/ESACCI...
        url = f"https://dap.ceda.ac.uk/neodc/esacci/soil_moisture/data/daily_files/COMBINED/{VERSION}/{year_str}/{fname}"
        
        output_path = os.path.join(RAW_DIR, fname)
        
        if os.path.exists(output_path):
            # logging.info(f"File {fname} already exists. Skipping.")
            status = "Already Downloaded"
        else:
            logging.info(f"Downloading {fname}...")
            try:
                response = session.get(url, stream=True)
                if response.status_code == 200:
                    with open(output_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    status = "Downloaded"
                else:
                    logging.error(f"Failed to download {fname}: HTTP {response.status_code}")
                    status = f"Failed HTTP {response.status_code}"
            except Exception as e:
                logging.error(f"Failed to download {fname}: {e}")
                status = "Failed Exception"
                
        size = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0
        
        inventory_data.append({
            'date': date_str,
            'file_name': fname,
            'product': 'ESA_CCI_COMBINED',
            'file_size_mb': round(size, 2),
            'status': status
        })
        
    if inventory_data:
        df_inv = pd.DataFrame(inventory_data)
        df_inv.to_csv(INVENTORY_FILE, index=False)
        logging.info(f"Inventory saved to {INVENTORY_FILE}")
        
    logging.info("ESA CCI SM workflow completed.")

if __name__ == "__main__":
    main()
