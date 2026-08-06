#!/usr/bin/env python3
# Author: M. EL Aabaribaoune (@um6p)

# ==============================================================================
# Script: download_gleam.py
# Description: Download script for validation data.
# Author: M. El Aabaribaoune (@um6p)
# ==============================================================================

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import config_validation as config
from credentials_validation import GLEAM_USERNAME, GLEAM_PASSWORD

"""
download_gleam.py

Script to download GLEAM Evapotranspiration data for validation via SFTP.
Target Period: 2015-01-01 to 2020-12-31
Uses curl since python ftplib doesn't support SFTP and paramiko is not installed.
"""

import logging
import pandas as pd
import subprocess

# --- Configuration ---
START_YEAR = 2015
END_YEAR = 2020
VERSION = "v4.3a" 
PRODUCT_TYPE = "daily"

# --- Identifiants ---


SFTP_HOST = "aether.ugent.be"
SFTP_PORT = 2225

BASE_DIR = config.PROJECT_ROOT
RAW_DIR = os.path.join(BASE_DIR, 'data/validation/evapotranspiration/GLEAM/raw')
REPORT_DIR = os.path.join(BASE_DIR, 'reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_gleam.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging locally
log_file = os.path.join(os.path.dirname(__file__), "logs", "download_gleam.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

def download_with_curl(remote_path, local_path):
    url = f"sftp://{SFTP_HOST}:{SFTP_PORT}{remote_path}"
    # Use -k to allow insecure connection, -u for credentials, -o for output file, -s for silent, -f to fail silently on error
    cmd = [
        "curl", "-k", "-s", "-f",
        "-u", f"{GLEAM_USERNAME}:{GLEAM_PASSWORD}",
        "-o", local_path,
        url
    ]
    try:
        result = subprocess.run(cmd, check=True, stderr=subprocess.PIPE)
        return True
    except subprocess.CalledProcessError as e:
        logging.error(f"Curl failed for {url}: {e.stderr.decode('utf-8').strip()}")
        return False

def main():
    logging.info("Starting GLEAM ET download workflow via SFTP using curl.")
    
    inventory_data = []
    
    for year in range(START_YEAR, END_YEAR + 1):
        try:
            # We will download E (Actual Evapotranspiration) and Ep (Potential Evapotranspiration)
            # You can add others like SMrz, SMs, etc. if needed
            for var in ['E', 'Ep']:
                fname = f"{var}_{year}_GLEAM_{VERSION}.nc"
                remote_path = f"/data/{VERSION}/{PRODUCT_TYPE}/{year}/{fname}"
                output_path = os.path.join(RAW_DIR, fname)
                
                if os.path.exists(output_path):
                    logging.info(f"File {fname} already exists. Skipping.")
                    status = "Already Downloaded"
                else:
                    logging.info(f"Downloading {fname} from {remote_path} ...")
                    success = download_with_curl(remote_path, output_path)
                    if success:
                        logging.info(f"Successfully downloaded {fname}.")
                        status = "Downloaded"
                    else:
                        status = "Failed"
                        
                size = os.path.getsize(output_path) / (1024 * 1024) if os.path.exists(output_path) else 0
                
                inventory_data.append({
                    'year': year,
                    'file_name': fname,
                    'product': f'GLEAM_{var}',
                    'file_size_mb': round(size, 2),
                    'status': status
                })
                
        except Exception as e:
            logging.error(f"Failed processing year {year}: {e}")
            
    if inventory_data:
        df_inv = pd.DataFrame(inventory_data)
        df_inv.to_csv(INVENTORY_FILE, index=False)
        logging.info(f"Inventory saved to {INVENTORY_FILE}")
        
    logging.info("GLEAM workflow completed.")

if __name__ == "__main__":
    main()
