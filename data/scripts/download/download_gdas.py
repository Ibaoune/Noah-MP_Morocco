#!/usr/bin/env python3

# Author: M. El Aabaribaoune (@um6p)

"""
download_gdas.py

Script to download GDAS meteorological forcing (excluding precipitation) 
for the Sebou-Saïss basin, Morocco.
Target Period: 2015-01-01 to 2020-12-31

Data Source: NCAR RDA ds083.3 (NCEP GDAS/FNL 0.25 Degree Global Tropospheric Analyses)
This script provides a skeleton for downloading using requests. 
Note: NCAR RDA requires an account and API token.
"""

import os
import sys
import requests
import logging
import pandas as pd
from datetime import datetime, timedelta

# --- Configuration ---
START_DATE = datetime(2015, 1, 1)
END_DATE = datetime(2020, 12, 31)

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../'))
RAW_DIR = os.path.join(BASE_DIR, 'data/forcing/GDAS/raw')
REPORT_DIR = os.path.join(BASE_DIR, 'data/reports')
INVENTORY_FILE = os.path.join(REPORT_DIR, 'inventory_gdas.csv')

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(REPORT_DIR, exist_ok=True)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(BASE_DIR, 'data/logs/download/download_gdas.log')),
        logging.StreamHandler()
    ]
)

def download_gdas_file(date_obj, cycle, output_dir, credentials=None):
    """
    Placeholder function to download GDAS file for a specific date and cycle (00, 06, 12, 18).
    This function should interface with the NCAR RDA API or use a pre-generated wget script.
    """
    # Example filename pattern for ds083.3: gdas1.fnl.0p25.2015010100.f00.grib2
    date_str = date_obj.strftime("%Y%m%d")
    filename = f"gdas1.fnl.0p25.{date_str}{cycle:02d}.f00.grib2"
    url = f"https://data.rda.ucar.edu/ds083.3/{date_obj.strftime('%Y')}/{date_str}/{filename}"
    output_path = os.path.join(output_dir, filename)
    
    if os.path.exists(output_path):
        return filename, "Already_Downloaded", os.path.getsize(output_path)
    
    # NOTE: Actual download requires RDA authentication. 
    # For a real run, you need to pass cookies or tokens to requests.get()
    try:
        # Example of anonymous download (will fail if auth required)
        # response = requests.get(url, stream=True)
        # response.raise_for_status()
        # with open(output_path, 'wb') as f:
        #     for chunk in response.iter_content(chunk_size=8192):
        #         f.write(chunk)
        
        # We will touch a dummy file here to represent the download process for workflow testing
        with open(output_path, 'w') as f:
            f.write("DUMMY GDAS DATA. Implement RDA API auth to download real GRIB files.")
            
        return filename, "Dummy_Created", os.path.getsize(output_path)
    except Exception as e:
        logging.error(f"Failed to download {url}: {e}")
        return filename, "Failed", 0

def main():
    logging.info("Starting GDAS download workflow.")
    logging.warning("This script requires NCAR RDA authentication to download actual data.")
    
    current_date = START_DATE
    cycles = [0, 6, 12, 18]
    inventory_data = []
    
    while current_date <= END_DATE:
        for cycle in cycles:
            fname, status, size = download_gdas_file(current_date, cycle, RAW_DIR)
            
            inventory_data.append({
                'date': current_date.strftime("%Y-%m-%d"),
                'cycle': f"{cycle:02d}Z",
                'file_name': fname,
                'file_size_mb': round(size / (1024 * 1024), 2),
                'status': status
            })
            
        current_date += timedelta(days=1)
        
    # Save inventory
    df_inv = pd.DataFrame(inventory_data)
    df_inv.to_csv(INVENTORY_FILE, index=False)
    logging.info(f"Inventory saved to {INVENTORY_FILE}")
    logging.info("GDAS workflow completed.")

if __name__ == "__main__":
    main()
